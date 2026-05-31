from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ClinicalFlag(BaseModel):
    level: str  # RED, AMBER, GREEN
    reason: str
    category: str  # e.g., Triage, Vital Signs, History

class DifferentialDiagnosis(BaseModel):
    condition_name: str
    icd_10_code: Optional[str] = None
    icd_11_code: Optional[str] = None
    confidence_score: float
    reasoning_summary: str

class PhysicianBrief(BaseModel):
    case_number: str
    flags: List[ClinicalFlag]
    differentials: List[DifferentialDiagnosis]
    examination_plan: List[str]
    recommended_investigations: List[str]
    rag_sources: List[str]
    confidence_score: float
    is_emergency: bool = False
    generated_at: datetime = datetime.now()
