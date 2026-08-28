from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QLineEdit, QHBoxLayout)
from PySide6.QtCore import Qt
from sqlalchemy import text

class AuditLogUI(QWidget):
    """Admin interface for browsing security audit logs (Blueprint §12.3)."""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.title = QLabel("System Audit Logs")
        self.title.setObjectName("header_title")
        self.layout.addWidget(self.title)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Filter by User ID or Action...")
        self.layout.addWidget(self.search_bar)
        
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Timestamp", "User", "Action", "Case Number", "Details"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)
        
        self._load_logs()

    def _load_logs(self):
        # Queries the audit_log table in SQLite
        if not self.controller or not hasattr(self.controller, "get_db_session"):
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem("Audit log unavailable (no database session)."))
            return

        session = self.controller.get_db_session()
        try:
            # Column names match models.db_models.AuditLog
            res = session.execute(text(
                "SELECT timestamp, user, action, entity_id, details "
                "FROM audit_log ORDER BY timestamp DESC LIMIT 100"
            ))
            logs = res.fetchall()

            if not logs:
                self.table.setRowCount(1)
                self.table.setItem(0, 0, QTableWidgetItem("No logs available yet."))
                return

            self.table.setRowCount(len(logs))
            for i, log in enumerate(logs):
                for j in range(5):
                    self.table.setItem(i, j, QTableWidgetItem(str(log[j])))
        except Exception as e:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(f"Could not load logs: {e}"))
        finally:
            session.close()
