from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "MediAssist Pro"
    debug: bool = False
    api_v1_str: str = "/api/v1"
    
    # Database
    database_url: str = "sqlite:///./mediassist.db"
    mediassist_db_path: str = "./mediassist.db"
    
    def get_db_url(self) -> str:
        return self.database_url
    
    # NVIDIA NIM API configuration
    nvidia_nim_api_key: Optional[str] = None
    nim_api_key_1: Optional[str] = None
    nim_api_key_2: Optional[str] = None
    nim_api_key_3: Optional[str] = None
    nim_api_key_4: Optional[str] = None
    nim_api_key_5: Optional[str] = None
    nim_api_key_6: Optional[str] = None
    nim_api_key_7: Optional[str] = None

    def get_nim_keys(self) -> list[str]:
        keys = []
        if self.nim_api_key_1: keys.append(self.nim_api_key_1)
        if self.nim_api_key_2: keys.append(self.nim_api_key_2)
        if self.nim_api_key_3: keys.append(self.nim_api_key_3)
        if self.nim_api_key_4: keys.append(self.nim_api_key_4)
        if self.nim_api_key_5: keys.append(self.nim_api_key_5)
        if self.nim_api_key_6: keys.append(self.nim_api_key_6)
        if self.nim_api_key_7: keys.append(self.nim_api_key_7)
        return keys

    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    access_token_expire_minutes: int = 60 * 24 * 8 # 8 days
    field_encryption_key: Optional[str] = None
    project_root: str = "c:/mediassist"

    # RAG Web Search
    trusted_sites: str = "who.int,cdc.gov,nih.gov,nice.org.uk"
    
    # AI Parameters
    ai_temperature: float = 0.0
    ai_max_tokens: int = 4096
    ai_top_p: float = 1.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

from nim.nim_key_manager import ModelRole

VISIT_TYPE_RAG_MAP = {
    "Vaccination/Immunization Visit": ["vaccination", "cdc_guidelines", "who_guidelines"],
    "General/Routine Checkup": ["core_medicine", "who_guidelines", "pharmacology"],
    "Specific Complaint / Acute Visit": ["core_medicine", "who_guidelines"],
    "Follow-up for Previous Condition": ["core_medicine"],
    "Maternal/Antenatal Care": ["ob_gyn", "who_guidelines"],
    "Pediatric Well-Visit": ["pediatrics", "vaccination", "cdc_guidelines"],
    "Mental Health Screening": ["core_medicine", "nice_guidelines", "who_guidelines"]
}

VISIT_TYPE_ROLE_MAP = {
    "Vaccination/Immunization Visit": ModelRole.FAST,
    "General/Routine Checkup": ModelRole.STANDARD,
    "Specific Complaint / Acute Visit": ModelRole.MEDICAL,
    "Follow-up for Previous Condition": ModelRole.STANDARD,
    "Maternal/Antenatal Care": ModelRole.MEDICAL,
    "Pediatric Well-Visit": ModelRole.MEDICAL,
    "Mental Health Screening": ModelRole.MEDICAL
}

settings = Settings()
