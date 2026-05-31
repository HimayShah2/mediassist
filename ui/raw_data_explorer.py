from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QTextEdit, 
                                 QTableWidget, QTableWidgetItem, QHeaderView, QLabel)

class RawDataExplorer(QWidget):
    """Physician's raw data access layer for inspecting AI inference steps (Section 10.2)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel("Raw Data Explorer")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Sub-panel A: Full Questionnaire Transcript
        self.transcript_tab = QWidget()
        self.transcript_layout = QVBoxLayout(self.transcript_tab)
        self.transcript_text = QTextEdit()
        self.transcript_text.setReadOnly(True)
        self.transcript_layout.addWidget(QLabel("Full Questionnaire Transcript (Verbatim)"))
        self.transcript_layout.addWidget(self.transcript_text)
        self.tabs.addTab(self.transcript_tab, "Transcript")
        
        # Sub-panel B: RAG Chunk Viewer
        self.rag_tab = QWidget()
        self.rag_layout = QVBoxLayout(self.rag_tab)
        self.rag_table = QTableWidget(0, 4)
        self.rag_table.setHorizontalHeaderLabels(["Source", "Similarity", "Collection", "Chunk Text"])
        self.rag_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.rag_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.rag_layout.addWidget(QLabel("RAG Chunk Viewer (Sorted by Similarity)"))
        self.rag_layout.addWidget(self.rag_table)
        self.tabs.addTab(self.rag_tab, "RAG Chunks")
        
        # Sub-panel C: LLM Response Log
        self.llm_tab = QWidget()
        self.llm_layout = QVBoxLayout(self.llm_tab)
        self.llm_table = QTableWidget(0, 6)
        self.llm_table.setHorizontalHeaderLabels(["Model", "Key ID", "Prompt Tokens", "Response Tokens", "Latency (ms)", "Response JSON"])
        self.llm_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.llm_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.llm_layout.addWidget(QLabel("LLM API Call Log"))
        self.llm_layout.addWidget(self.llm_table)
        self.tabs.addTab(self.llm_tab, "LLM Log")
        
        # Sub-panel D: Confidence Breakdown
        self.confidence_tab = QWidget()
        self.confidence_layout = QVBoxLayout(self.confidence_tab)
        self.confidence_text = QTextEdit()
        self.confidence_text.setReadOnly(True)
        self.confidence_text.setStyleSheet("font-family: monospace;")
        self.confidence_layout.addWidget(QLabel("Deterministic Confidence Breakdown"))
        self.confidence_layout.addWidget(self.confidence_text)
        self.tabs.addTab(self.confidence_tab, "Confidence Breakdown")
        
    def load_session_data(self, session_data: dict):
        """Populate the tabs with data from a specific session."""
        # A: Transcript
        self.transcript_text.setPlainText(session_data.get("transcript", "No transcript available."))
        
        # B: RAG Chunks
        chunks = session_data.get("rag_chunks", [])
        self.rag_table.setRowCount(len(chunks))
        for row, chunk in enumerate(chunks):
            self.rag_table.setItem(row, 0, QTableWidgetItem(str(chunk.get("source", ""))))
            self.rag_table.setItem(row, 1, QTableWidgetItem(f"{chunk.get('similarity', 0.0):.2f}"))
            self.rag_table.setItem(row, 2, QTableWidgetItem(str(chunk.get("collection", ""))))
            self.rag_table.setItem(row, 3, QTableWidgetItem(str(chunk.get("text", ""))))
            
        # C: LLM Log
        llm_calls = session_data.get("llm_calls", [])
        self.llm_table.setRowCount(len(llm_calls))
        for row, call in enumerate(llm_calls):
            self.llm_table.setItem(row, 0, QTableWidgetItem(str(call.get("model", ""))))
            self.llm_table.setItem(row, 1, QTableWidgetItem(str(call.get("key_id", ""))))
            self.llm_table.setItem(row, 2, QTableWidgetItem(str(call.get("prompt_tokens", ""))))
            self.llm_table.setItem(row, 3, QTableWidgetItem(str(call.get("response_tokens", ""))))
            self.llm_table.setItem(row, 4, QTableWidgetItem(str(call.get("latency_ms", ""))))
            self.llm_table.setItem(row, 5, QTableWidgetItem(str(call.get("response_json", ""))))
            
        # D: Confidence Breakdown
        breakdown = session_data.get("confidence_breakdown", "No confidence data available.")
        self.confidence_text.setPlainText(breakdown)
