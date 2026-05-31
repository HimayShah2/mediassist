import os
from loguru import logger
from typing import Callable, Optional

from config.settings import Settings
from nim.nim_key_manager import NIMKeyManager
from rag.document_manager import DocumentManager
from questionnaire.engine import QuestionnaireEngine
from report.report_generator import ReportGenerator
from database.connection import SessionLocal

class AppController:
    """
    Central orchestrator — wires all modules together.
    Following Blueprint Section 13 and 14.
    """

    def __init__(self, splash_callback: Optional[Callable[[str], None]] = None):
        self.splash_callback = splash_callback
        self.settings = None
        self.key_manager = None
        self.doc_manager = None
        self.questionnaire_engine = None
        self.report_generator = None
        self.current_user = None
        self.current_role = None

    def initialize(self):
        """Initializes all services, loads DB, keys, RAG."""
        self._log("Initializing Settings...")
        
        self._log("Initializing NIM Key Manager...")
        # Injecting real API keys as requested
        real_keys = [
            "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",
            "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",
            "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",
            "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",
            "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",
            "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",
            "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",
        ]
        self.key_manager = NIMKeyManager(real_keys)
        
        self._log("Initializing Document Manager (RAG)...")
        # Ensure chroma_db directory exists
        db_path = os.path.join(os.getcwd(), "knowledge_base", "chroma_db")
        os.makedirs(db_path, exist_ok=True)
        self.doc_manager = DocumentManager(self.key_manager, db_path)
        
        self._log("Initializing Questionnaire Engine...")
        self.questionnaire_engine = QuestionnaireEngine(self.key_manager, self.doc_manager)
        
        self._log("Initializing Report Generator...")
        self.report_generator = ReportGenerator(self.key_manager, self.doc_manager)
        
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
        from sqlalchemy import text
        import json
        session = self.get_db_session()
        try:
            # Note: details must be a valid JSON string or dict
            details_json = json.dumps(details) if isinstance(details, dict) else "{}"
            query = text("""
                INSERT INTO audit_log (user_id, action, case_number, details) 
                VALUES (:u, :a, :c, :d)
            """)
            session.execute(query, {"u": user_id, "a": action, "c": case_number, "d": details_json})
            session.commit()
        except Exception as e:
            logger.error(f"Audit log failed: {e}")
        finally:
            session.close()
