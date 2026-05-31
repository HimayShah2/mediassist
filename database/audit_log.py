import sqlite3
import datetime
import hashlib
from pathlib import Path
from loguru import logger
from config.settings import settings

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

class AuditLogger:
    """
    Append-only audit log tracking user actions for security compliance.
    Implements cryptographic hash chaining to detect tampering.
    """

    def __init__(self, db_path: str | None = None):
        if db_path is None:
            self.db_path = settings.mediassist_db_path
        else:
            self.db_path = db_path
            
        self._init_table()

    def _init_table(self) -> None:
        """Ensure the audit_events table exists with hash columns."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    previous_hash TEXT NOT NULL,
                    current_hash TEXT NOT NULL
                )
                """
            )
            # Prevent updates and deletes on this table using triggers
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS prevent_audit_update
                BEFORE UPDATE ON audit_events
                BEGIN
                    SELECT RAISE(ABORT, 'Audit log is append-only.');
                END;
                """
            )
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS prevent_audit_delete
                BEFORE DELETE ON audit_events
                BEGIN
                    SELECT RAISE(ABORT, 'Audit log is append-only.');
                END;
                """
            )
            conn.commit()

    def _calculate_hash(self, prev_hash: str, user_id: str, role: str, action: str, timestamp: str) -> str:
        data = f"{prev_hash}|{user_id}|{role}|{action}|{timestamp}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def log_event(self, user_id: str, role: str, action: str) -> None:
        """
        Log an event in an append-only format with hash chaining.
        """
        try:
            timestamp = datetime.datetime.utcnow().isoformat()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT current_hash FROM audit_events ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                prev_hash = row[0] if row else GENESIS_HASH
                
                curr_hash = self._calculate_hash(prev_hash, user_id, role, action, timestamp)
                
                cursor.execute(
                    """
                    INSERT INTO audit_events (user_id, role, action, timestamp, previous_hash, current_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, role, action, timestamp, prev_hash, curr_hash)
                )
                conn.commit()
            logger.debug(f"Audit event logged: {action} by user {user_id}")
        except Exception as e:
            logger.error(f"Failed to log audit event: {e}")

audit_logger = AuditLogger()

def log_audit_event(user_id: str, role: str, action: str) -> None:
    audit_logger.log_event(user_id, role, action)
