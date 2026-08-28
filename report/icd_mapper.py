from pydantic import BaseModel
from llm.server_client import ServerLLMClient

class ICDMapping(BaseModel):
    icd_10: str
    icd_11: str
    confidence: float

class ICDMapper:
    def __init__(self, llm_client: ServerLLMClient):
        self.llm_client = llm_client

    async def map(self, diagnosis_name: str) -> ICDMapping:
        prompt = f"""
Given the following diagnosis name, return the most appropriate ICD-10 and ICD-11 codes.
Diagnosis: {diagnosis_name}
"""
        try:
            return await self.llm_client.generate_structured(
                response_model=ICDMapping,
                messages=[{"role": "user", "content": prompt}]
            )
        except Exception as e:
            from loguru import logger
            logger.warning(f"ICD mapping failed for '{diagnosis_name}': {e}")
            return ICDMapping(icd_10="", icd_11="", confidence=0.0)
