from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                               QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QGroupBox, QMessageBox, QTabWidget)
from PySide6.QtCore import Qt
import json

class ReportReviewUI(QWidget):
    """
    Physician Review & Sign-off Interface (Blueprint §10.4).
    Allows doctors to annotate AI briefs and lock them.
    """
    def __init__(self, controller, visit_id, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.visit_id = visit_id
        
        self.layout = QVBoxLayout(self)
        
        # Tabs: Brief | Raw Data | SQL Explorer
        self.tabs = QTabWidget()
        
        # --- TAB 1: Physician Brief & Sign-off ---
        self.brief_tab = QWidget()
        self.brief_layout = QVBoxLayout(self.brief_tab)
        
        self.brief_display = QTextEdit()
        self.brief_display.setReadOnly(True)
        self.brief_display.setPlaceholderText("AI Clinical Brief loading...")
        self.brief_layout.addWidget(QLabel("AI Clinical Assessment:"))
        self.brief_layout.addWidget(self.brief_display)
        
        self.notes_group = QGroupBox("Physician Annotations & Sign-off")
        self.notes_layout = QVBoxLayout()
        self.input_notes = QTextEdit()
        self.input_notes.setPlaceholderText("Enter your clinical notes here...")
        self.btn_sign = QPushButton("Sign & Lock Report")
        self.btn_sign.setObjectName("action_primary")
        self.btn_sign.clicked.connect(self._sign_off)
        
        self.notes_layout.addWidget(self.input_notes)
        self.notes_layout.addWidget(self.btn_sign)
        self.notes_group.setLayout(self.notes_layout)
        self.brief_layout.addWidget(self.notes_group)
        
        # --- TAB 2: Raw Data Explorer (Blueprint §10.2) ---
        self.raw_tab = QWidget()
        self.raw_layout = QVBoxLayout(self.raw_tab)
        
        self.llm_log = QTextEdit()
        self.llm_log.setReadOnly(True)
        self.rag_log = QTableWidget(0, 3)
        self.rag_log.setHorizontalHeaderLabels(["Source", "Similarity", "Chunk Text"])
        self.rag_log.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.raw_layout.addWidget(QLabel("Raw LLM JSON Responses:"))
        self.raw_layout.addWidget(self.llm_log)
        self.raw_layout.addWidget(QLabel("Retrieved RAG Evidence:"))
        self.raw_layout.addWidget(self.rag_log)
        
        self.tabs.addTab(self.brief_tab, "Clinical Brief")
        self.tabs.addTab(self.raw_tab, "Raw AI Data")
        
        self.layout.addWidget(self.tabs)
        self._load_data()

    def _load_data(self):
        # In a real app, this fetches from the visits table in SQLite
        # For this skeleton, we display the logs from the active engine
        engine = self.controller.questionnaire_engine
        
        # Load LLM logs
        self.llm_log.setText(json.dumps(engine.raw_llm_log, indent=2))
        
        # Load RAG logs
        self.rag_log.setRowCount(len(engine.raw_rag_log))
        for i, chunk in enumerate(engine.raw_rag_log):
            self.rag_log.setItem(i, 0, QTableWidgetItem(chunk['metadata'].get('source_file', 'Unknown')))
            self.rag_log.setItem(i, 1, QTableWidgetItem(str(chunk.get('similarity', 0.0))))
            self.rag_log.setItem(i, 2, QTableWidgetItem(chunk.get('text', '')))

    def _sign_off(self):
        # Blueprint §10.4: Lock the report
        notes = self.input_notes.toPlainText().strip()
        if not notes:
            QMessageBox.warning(self, "Required", "Please provide clinical notes before signing.")
            return
        
        QMessageBox.information(self, "Signed", f"Report for Visit {self.visit_id} has been signed and locked.")
        self.btn_sign.setEnabled(False)
        self.input_notes.setReadOnly(True)
