import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import List, Optional
from nim.nim_key_manager import NIMKeyManager, ModelRole
from models.report_output import PhysicianBrief

class ConsensusResult(BaseModel):
    agrees_with_top_differential: bool
    alternative_differentials: Optional[List[str]] = None
    consensus_score: float

class ConsensusValidator:
    def __init__(self, key_manager: NIMKeyManager):
        self.key_manager = key_manager

    async def validate(self, brief: PhysicianBrief, patient_ctx: dict, rag_text: str) -> ConsensusResult:
        key = self.key_manager.get_key_for_role(ModelRole.STANDARD)
        client = instructor.from_openai(AsyncOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=key.key_value
        ))
        
        prompt = f"""
Review the following physician brief and patient context. 
Do you agree with the top differential? 
Brief Differentials: {[d.condition_name for d in brief.differentials]}
Patient Context: {patient_ctx}
"""
        return await client.chat.completions.create(
            model=self.key_manager.get_model_for_role(ModelRole.STANDARD),
            response_model=ConsensusResult,
            messages=[{"role": "user", "content": prompt}]
        )

    def merge_consensus(self, brief: PhysicianBrief, consensus: ConsensusResult) -> PhysicianBrief:
        # Update brief based on consensus if needed
        return brief
