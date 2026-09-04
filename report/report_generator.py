import asyncio
from loguru import logger

from models.report_output import PhysicianBrief
from models.questionnaire import SessionAnswers
from llm.server_client import ServerLLMClient
from rag.document_manager import DocumentManager
from questionnaire.prompt_templates import PromptTemplates

from .icd_mapper import ICDMapper
from .consensus_validator import ConsensusValidator
from .confidence_scorer import ConfidenceScorer

class ReportGenerator:
    def __init__(self, llm_client: ServerLLMClient, doc_manager: DocumentManager):
        self.llm_client = llm_client
        self.doc_manager = doc_manager
        self.prompts     = PromptTemplates()
        self.icd_mapper  = ICDMapper(llm_client)
        self.validator   = ConsensusValidator(llm_client)
        self.scorer      = ConfidenceScorer()

    async def generate(self, case_number: str, session_answers: SessionAnswers,
                        patient_ctx: dict, vital_signs: dict,
                        rag_chunks_used: list, specialty: str) -> PhysicianBrief:

        # Retrieve final RAG context for report generation
        complaint_query = patient_ctx.get("chief_complaint_summary", "General clinical summary")
        # Ensure we await the retrieval
        final_chunks    = await self.doc_manager.retrieve(complaint_query,
                           ["core_medicine", "who_guidelines"], n_results=15)
        rag_text        = "\n\n".join([f"[{c.get('metadata', {}).get('source_file', 'unknown')}] {c['text']}" for c in final_chunks[:5]])

        medical_prompt = self.prompts.get_brief_prompt(
            case_number=case_number,
            session_answers=session_answers.dict(),
            patient_ctx=patient_ctx,
            vital_signs=vital_signs,
            rag_context=rag_text,
            specialty=specialty
        )

        from config.settings import settings as _settings
        _rep_tokens = getattr(_settings, "ai_report_max_tokens", 3000)
        primary_brief: PhysicianBrief = await self.llm_client.generate_structured(
            response_model=PhysicianBrief,
            messages=[{"role": "user", "content": medical_prompt}],
            temperature=0.1, max_tokens=_rep_tokens
        )

        # Consensus validation
        consensus_result = await self.validator.validate(primary_brief, patient_ctx, rag_text)
        primary_brief = self.validator.merge_consensus(primary_brief, consensus_result)

        # Assign ICD codes — one batched call for all differentials
        icd_map = await self.icd_mapper.map_many([d.condition_name for d in primary_brief.differentials])
        for diff in primary_brief.differentials:
            icd = icd_map.get(diff.condition_name.strip().lower())
            if icd is None:
                icd = await self.icd_mapper.map(diff.condition_name)
            diff.icd_10_code = icd.icd_10
            diff.icd_11_code = icd.icd_11

        # Calculate confidence score
        primary_brief.confidence_score = self.scorer.calculate(
            rag_chunks=final_chunks[:5],
            consensus=consensus_result,
            session_answers=session_answers,
            patient_ctx=patient_ctx
        )

        logger.info(f"Report generated for {case_number} - confidence: {primary_brief.confidence_score:.2f}")
        return primary_brief
