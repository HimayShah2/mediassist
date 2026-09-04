import os
import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


def _local_secret_key() -> str:
    """Never ship a hardcoded secret in source. Read SECRET_KEY from the
    environment/.env if set; otherwise generate one and cache it in a
    gitignored local file so it stays stable across restarts."""
    env_val = os.getenv("SECRET_KEY")
    if env_val:
        return env_val
    path = os.path.join(os.getcwd(), ".secret_key")
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                val = f.read().strip()
                if val:
                    return val
        val = secrets.token_hex(32)
        with open(path, "w", encoding="utf-8") as f:
            f.write(val)
        return val
    except OSError:
        return secrets.token_hex(32)  # ephemeral fallback (e.g. read-only fs)


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
    secret_key: str = Field(default_factory=_local_secret_key)
    access_token_expire_minutes: int = 60 * 24 * 8 # 8 days
    field_encryption_key: Optional[str] = None
    project_root: str = Field(default_factory=os.getcwd)

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
