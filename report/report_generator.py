import asyncio
import instructor
from openai import AsyncOpenAI
from loguru import logger

from models.report_output import PhysicianBrief
from models.questionnaire import SessionAnswers
from nim.nim_key_manager import NIMKeyManager, ModelRole
from rag.document_manager import DocumentManager
from questionnaire.prompt_templates import PromptTemplates

from .icd_mapper import ICDMapper
from .consensus_validator import ConsensusValidator
from .confidence_scorer import ConfidenceScorer

class ReportGenerator:
    def __init__(self, key_manager: NIMKeyManager, doc_manager: DocumentManager):
        self.key_manager = key_manager
        self.doc_manager = doc_manager
        self.prompts     = PromptTemplates()
        self.icd_mapper  = ICDMapper(key_manager)
        self.validator   = ConsensusValidator(key_manager)
        self.scorer      = ConfidenceScorer()

    async def generate(self, case_number: str, session_answers: SessionAnswers,
                        patient_ctx: dict, vital_signs: dict,
                        rag_chunks_used: list, specialty: str) -> PhysicianBrief:

        # Retrieve final RAG context for report generation
        complaint_query = patient_ctx.get("chief_complaint_summary", "General clinical summary")
        final_chunks    = self.doc_manager.retrieve(complaint_query,
                           ["core_medicine", "who_guidelines"], n_results=15)
        rag_text        = "\n\n".join([f"[{c['metadata']['source_file']}] {c['text']}" for c in final_chunks[:5]])

        # Primary generation: ROLE_MEDICAL
        key_m = self.key_manager.get_key_for_role(ModelRole.MEDICAL)
        client_m = instructor.from_openai(AsyncOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=key_m.key_value, timeout=60.0, max_retries=0
        ))
        
        medical_prompt = self.prompts.get_brief_prompt(
            case_number=case_number,
            session_answers=session_answers.dict(),
            patient_ctx=patient_ctx,
            vital_signs=vital_signs,
            rag_context=rag_text,
            specialty=specialty
        )

        primary_brief: PhysicianBrief = await client_m.chat.completions.create(
            model=self.key_manager.get_model_for_role(ModelRole.MEDICAL),
            response_model=PhysicianBrief,
            messages=[{"role": "user", "content": medical_prompt}],
            temperature=0.1, max_tokens=8192
        )

        # Consensus validation
        consensus_result = await self.validator.validate(primary_brief, patient_ctx, rag_text)
        primary_brief = self.validator.merge_consensus(primary_brief, consensus_result)

        # Assign ICD codes
        for diff in primary_brief.differentials:
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
