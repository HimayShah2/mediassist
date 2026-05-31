from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VisitBase(BaseModel):
    patient_id: str
    visit_date: datetime
    reason_for_visit: str
    notes: Optional[str] = None
    status: str = Field(default="scheduled", description="Status of the visit (e.g., scheduled, completed, cancelled)")

class VisitCreate(VisitBase):
    pass

class Visit(VisitBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
