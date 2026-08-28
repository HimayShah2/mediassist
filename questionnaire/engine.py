import asyncio
import time
import instructor
from openai import AsyncOpenAI
from loguru import logger

from models.questionnaire import QuestionnaireRound, SessionAnswers
from llm.server_client import ServerLLMClient
from rag.document_manager import DocumentManager
from config.settings import VISIT_TYPE_RAG_MAP, VISIT_TYPE_ROLE_MAP
from .prompt_templates import PromptTemplates
from .red_flag_detector import RedFlagDetector

class QuestionnaireEngine:
    MAX_RETRIES = 3

    def __init__(self, llm_client: ServerLLMClient, doc_manager: DocumentManager):
        self.llm_client       = llm_client
        self.doc_manager      = doc_manager
        self.prompts          = PromptTemplates()
        self.flag_detector    = RedFlagDetector()
        self.session_answers  = SessionAnswers()
        self.raw_llm_log      = []    # Stored for physician raw data access
        self.raw_rag_log      = []    # Stored for physician raw data access

    async def generate_round(self, round_number: int, visit_type: str,
                              patient_ctx: dict, specialty: str) -> QuestionnaireRound:
        
        # Use blueprint mapping for role, default to STANDARD if missing
        role = VISIT_TYPE_ROLE_MAP.get(visit_type, "STANDARD")
        # Always use MEDICAL for the final refinement round
        if round_number == 4:
            role = "MEDICAL"
            
        # DOMAIN RESTRICTION LOGIC
        # Standard domains map directly to collection names
        domain_slug = specialty.lower().replace(" ", "_").replace("(ent)", "ent")
        
        if patient_ctx.get("allow_all_domains"):
            # Use blueprint default map + current specialty
            collections = VISIT_TYPE_RAG_MAP.get(visit_type, ["core_medicine", "who_guidelines"])
            if domain_slug not in collections:
                collections.append(domain_slug)
        else:
            # STRICT MODE: Only [Selected Domain, Common Knowledge]
            collections = [domain_slug, "common_medicine"]
        
        # Retrieve RAG context
        query       = f"Patient presenting for {visit_type} in {specialty} domain. Context: {patient_ctx}"
        
        # Get trusted sites from settings
        from config.settings import settings
        trusted_sites = [s.strip() for s in settings.trusted_sites.split(",") if s.strip()]
        
        # DocumentManager.retrieve should now handle trusted_sites
        rag_chunks  = await self.doc_manager.retrieve(query, collections, n_results=15, trusted_sites=trusted_sites)
        self.raw_rag_log.extend(rag_chunks)
        rag_text    = "\n\n".join([f"SOURCE [{c.get('metadata', {}).get('source_file', 'unknown')}]: {c['text']}" for c in rag_chunks[:5]])

        prompt      = self.prompts.get_round_prompt(
            round_number=round_number,
            visit_type=visit_type,
            specialty=specialty,
            patient_ctx=patient_ctx,
            session_answers=self.session_answers.dict(),
            rag_context=rag_text
        )

        from config.settings import settings
        
        from config.settings import settings
        grounding_prefix = """
CRITICAL GROUNDING RULES:
1. You MUST answer ONLY based on the provided RAG context below.
2. If the context is from a website (labeled SOURCE [WEB: ...]), you MUST explicitly quote the site name in your reasoning (e.g., 'According to WebMD...' or 'As per WHO...').
3. Do NOT use your own internal knowledge if it contradicts the context. 
4. Cite sources verbatim in the 'rag_context_used' array.
"""
        start = time.time()
        for attempt in range(self.MAX_RETRIES):
            try:
                result: QuestionnaireRound = await self.llm_client.generate_structured(
                    response_model=QuestionnaireRound,
                    messages=[{"role": "system", "content": grounding_prefix}, {"role": "user", "content": prompt}],
                    temperature=settings.ai_temperature,
                    max_tokens=settings.ai_max_tokens
                )
                duration = int((time.time() - start) * 1000)
                result.generation_time_ms = duration
                result.model_used         = "local-model"
                result.rag_chunk_ids      = [c.get("metadata", {}).get("chunk_id", "") for c in rag_chunks[:5]]
                self.raw_llm_log.append({"round": round_number, "model": "local-model",
                                          "duration_ms": duration})
                logger.info(f"Round {round_number} generated: {len(result.questions)} questions in {duration}ms")
                return result
            except Exception as e:
                logger.warning(f"Round {round_number} generation attempt {attempt+1} failed: {e}")
                if attempt == self.MAX_RETRIES - 1:
                    raise RuntimeError(f"Failed to generate round {round_number} after {self.MAX_RETRIES} attempts")

    def submit_round_answers(self, round_number: int, answers: dict, scoring_tool_id: str = None):
        """Store answers, calculate clinical scores if applicable, and check for red flags."""
        setattr(self.session_answers, f"round_{round_number}", answers)
        
        # Clinical Scoring Integration
        if scoring_tool_id:
            from scoring import clinical_tools
            try:
                # Convert answers dict to ordered list of values for the specific tool
                # This assumes the LLM correctly mapped the MCQ options to integer values
                score_values = [int(v) for v in answers.values() if str(v).isdigit()]
                
                calculation = None
                if scoring_tool_id == "phq9":
                    calculation = clinical_tools.calculate_phq9(score_values)
                elif scoring_tool_id == "gcs":
                    # GCS requires eye, verbal, motor separately - simplified for skeleton
                    if len(score_values) >= 3:
                        calculation = clinical_tools.calculate_gcs(score_values[0], score_values[1], score_values[2])
                elif scoring_tool_id == "apgar":
                    if len(score_values) >= 5:
                        calculation = clinical_tools.calculate_apgar(*score_values[:5])
                elif scoring_tool_id == "sofa":
                    if len(score_values) >= 6:
                        calculation = clinical_tools.calculate_sofa(*score_values[:6])
                
                if calculation:
                    logger.info(f"Clinical score calculated [{scoring_tool_id}]: {calculation}")
                    self.session_answers.flags_raised.append(f"Score [{scoring_tool_id.upper()}]: {calculation['score']} - {calculation['interpretation']}")
            except Exception as e:
                logger.warning(f"Failed to calculate clinical score {scoring_tool_id}: {e}")

        flags = self.flag_detector.check_answers(answers, round_number)
        if flags:
            self.session_answers.flags_raised.extend(flags)
            return {"emergency": True, "flags": flags}
        return {"emergency": False, "flags": []}

        """Store answers and check every answer for red flags."""
        setattr(self.session_answers, f"round_{round_number}", answers)
        flags = self.flag_detector.check_answers(answers, round_number)
        if flags:
            self.session_answers.flags_raised.extend(flags)
            return {"emergency": True, "flags": flags}
        return {"emergency": False, "flags": []}
