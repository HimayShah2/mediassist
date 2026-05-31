from pydantic import BaseModel
from typing import Optional

class VitalSigns(BaseModel):
    systolic_bp:   Optional[int]   = None   # mmHg
    diastolic_bp:  Optional[int]   = None   # mmHg
    heart_rate:    Optional[int]   = None   # bpm
    respiratory_rate: Optional[int] = None  # breaths/min
    spo2:          Optional[float] = None   # %
    temperature_c: Optional[float] = None   # Celsius
    weight_kg:     Optional[float] = None   # kg
    height_cm:     Optional[float] = None   # cm - BMI auto-calculated
    avpu:          Optional[str]   = None   # Alert/Voice/Pain/Unresponsive
    pain_scale:    Optional[int]   = None   # 0-10
    blood_glucose: Optional[float] = None   # mmol/L (if glucometer available)
    # Auto-calculated from weight + height:
    bmi:           Optional[float] = None
