from typing import List, Dict
from pydantic import BaseModel
from loguru import logger

from llm.server_client import ServerLLMClient


class ICDMapping(BaseModel):
    icd_10: str
    icd_11: str
    confidence: float


class ICDCodeItem(BaseModel):
    condition_name: str
    icd_10: str
    icd_11: str


class ICDBatch(BaseModel):
    codes: List[ICDCodeItem]


class ICDMapper:
    def __init__(self, llm_client: ServerLLMClient):
        self.llm_client = llm_client

    async def map(self, diagnosis_name: str) -> ICDMapping:
        prompt = (
            "Return the most appropriate ICD-10 and ICD-11 codes for this diagnosis.\n"
            f"Diagnosis: {diagnosis_name}"
        )
        try:
            return await self.llm_client.generate_structured(
                response_model=ICDMapping,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
            )
        except Exception as e:
            logger.warning(f"ICD mapping failed for '{diagnosis_name}': {e}")
            return ICDMapping(icd_10="", icd_11="", confidence=0.0)

    async def map_many(self, diagnosis_names: List[str]) -> Dict[str, ICDMapping]:
        """One LLM call for all differentials (much faster on CPU than one call each)."""
        if not diagnosis_names:
            return {}
        listed = "\n".join(f"- {d}" for d in diagnosis_names)
        prompt = (
            "For EACH diagnosis below, give its ICD-10 and ICD-11 codes. "
            "Return every diagnosis exactly once, using the same wording.\n\n" + listed
        )
        try:
            batch = await self.llm_client.generate_structured(
                response_model=ICDBatch,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
            )
            out: Dict[str, ICDMapping] = {}
            for item in batch.codes:
                out[item.condition_name.strip().lower()] = ICDMapping(
                    icd_10=item.icd_10, icd_11=item.icd_11, confidence=0.6
                )
            return out
        except Exception as e:
            logger.warning(f"Batch ICD mapping failed: {e}")
            return {}
