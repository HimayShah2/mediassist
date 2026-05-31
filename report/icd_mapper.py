import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel
from nim.nim_key_manager import NIMKeyManager, ModelRole

class ICDMapping(BaseModel):
    icd_10: str
    icd_11: str
    confidence: float

class ICDMapper:
    def __init__(self, key_manager: NIMKeyManager):
        self.key_manager = key_manager

    async def map(self, diagnosis_name: str) -> ICDMapping:
        key = self.key_manager.get_key_for_role(ModelRole.FAST)
        client = instructor.from_openai(AsyncOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=key.key_value
        ))
        
        prompt = f"""
Given the following diagnosis name, return the most appropriate ICD-10 and ICD-11 codes.
Diagnosis: {diagnosis_name}
"""
        return await client.chat.completions.create(
            model=self.key_manager.get_model_for_role(ModelRole.FAST),
            response_model=ICDMapping,
            messages=[{"role": "user", "content": prompt}]
        )
