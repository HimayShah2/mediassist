import os
from loguru import logger
from typing import Callable, Optional

from config.settings import Settings
from llm.server_client import ServerLLMClient
from rag.document_manager import DocumentManager
from questionnaire.engine import QuestionnaireEngine
from report.report_generator import ReportGenerator
from database.connection import SessionLocal, init_db

class AppController:
    """
    Central orchestrator — wires all modules together.
    Following Blueprint Section 13 and 14.
    """

    def __init__(self, splash_callback: Optional[Callable[[str], None]] = None):
        self.splash_callback = splash_callback
        self.settings = None
        self.llm_client = None
        self.doc_manager = None
        self.questionnaire_engine = None
        self.report_generator = None
        self.current_user = None
        self.current_role = None

    def initialize(self):
        """Initializes all services, loads DB, keys, RAG."""
        self._log("Initializing Settings...")
        
        self._log("Initializing Database schema...")
        init_db()
        
        self._log("Connecting to Standalone Local Server...")
        self.llm_client = ServerLLMClient()
        
        self._log("Initializing Document Manager (RAG)...")
        # Ensure chroma_db directory exists
        db_path = os.path.join(os.getcwd(), "knowledge_base", "chroma_db")
        os.makedirs(db_path, exist_ok=True)
        self.doc_manager = DocumentManager(self.llm_client, db_path)
        
        self._log("Initializing Questionnaire Engine...")
        self.questionnaire_engine = QuestionnaireEngine(self.llm_client, self.doc_manager)
        
        self._log("Initializing Report Generator...")
        self.report_generator = ReportGenerator(self.llm_client, self.doc_manager)
        
        self._log("System Ready.")

    def _log(self, message: str):
        logger.info(message)
        if self.splash_callback:
            self.splash_callback(message)

    def get_db_session(self):
        """Returns a new database session."""
        return SessionLocal()

    def log_activity(self, user_id, action, case_number=None, details=None):
        """Immutable security audit logging (Blueprint §12.3)."""
        import json
        from models.db_models import AuditLog
        session = self.get_db_session()
        try:
            # Note: details must be a valid JSON string or dict
            details_json = json.dumps(details) if isinstance(details, dict) else "{}"
            audit_entry = AuditLog(
                user=user_id,
                action=action,
                entity_type="case" if case_number else None,
                entity_id=case_number,
                details=details_json
            )
            session.add(audit_entry)
            session.commit()
        except Exception as e:
            logger.error(f"Audit log failed: {e}")
        finally:
            session.close()
