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
    

    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    access_token_expire_minutes: int = 60 * 24 * 8 # 8 days
    field_encryption_key: Optional[str] = None
    project_root: str = "c:/mediassist"

    # RAG Web Search
    trusted_sites: str = "who.int,cdc.gov,nih.gov,nice.org.uk"
    
    # AI Parameters
    ai_temperature: float = 0.0
    ai_max_tokens: int = 1536      # enough for a 6-8 question round; keeps CPU latency down
    ai_report_max_tokens: int = 3000
    ai_top_p: float = 1.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")



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
    "Vaccination/Immunization Visit": "FAST",
    "General/Routine Checkup": "STANDARD",
    "Specific Complaint / Acute Visit": "MEDICAL",
    "Follow-up for Previous Condition": "STANDARD",
    "Maternal/Antenatal Care": "MEDICAL",
    "Pediatric Well-Visit": "MEDICAL",
    "Mental Health Screening": "MEDICAL"
}

settings = Settings()
