from pydantic import BaseModel
from typing import List, Optional
from llm.server_client import ServerLLMClient
from models.report_output import PhysicianBrief

class ConsensusResult(BaseModel):
    agrees_with_top_differential: bool
    alternative_differentials: Optional[List[str]] = None
    consensus_score: float

class ConsensusValidator:
    def __init__(self, llm_client: ServerLLMClient):
        self.llm_client = llm_client

    async def validate(self, brief: PhysicianBrief, patient_ctx: dict, rag_text: str) -> ConsensusResult:
        prompt = f"""
Review the following physician brief and patient context. 
Do you agree with the top differential? 
Brief Differentials: {[d.condition_name for d in brief.differentials]}
Patient Context: {patient_ctx}
"""
        try:
            return await self.llm_client.generate_structured(
                response_model=ConsensusResult,
                messages=[{"role": "user", "content": prompt}]
            )
        except Exception as e:
            from loguru import logger
            logger.warning(f"Consensus validation failed: {e}")
            return ConsensusResult(agrees_with_top_differential=True,
                                   alternative_differentials=[],
                                   consensus_score=0.0)

    def merge_consensus(self, brief: PhysicianBrief, consensus: ConsensusResult) -> PhysicianBrief:
        # Update brief based on consensus if needed
        return brief
