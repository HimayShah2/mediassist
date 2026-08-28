from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, 
    QMessageBox, QHBoxLayout
)
from PySide6.QtCore import Signal
import json
import os

class SetupWizard(QWidget):
    setup_complete = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_path = "c:\\mediassist\\config\\settings.json"
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("First-Time Setup")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(title)
        
        desc = QLabel("Please configure your local environment settings.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        form_layout = QFormLayout()
        
        self.db_url = QLineEdit()
        self.db_url.setText("sqlite:///mediassist.db")
        form_layout.addRow("Database URL:", self.db_url)
        
        self.llm_model = QLineEdit()
        self.llm_model.setText("gemma-2b-it")
        form_layout.addRow("Local LLM Model:", self.llm_model)
        
        self.api_key = QLineEdit()
        self.api_key.setPlaceholderText("Optional API Key for cloud fallback")
        form_layout.addRow("API Key:", self.api_key)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save & Continue")
        self.btn_save.clicked.connect(self.save_config)
        self.btn_save.setStyleSheet("background-color: #2563eb; color: white; padding: 10px; font-weight: bold;")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        
        layout.addLayout(btn_layout)
        layout.addStretch()

    def save_config(self):
        config = {
            "DATABASE_URL": self.db_url.text(),
            "LLM_MODEL": self.llm_model.text(),
            "API_KEY": self.api_key.text()
        }
        
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=4)
            self.setup_complete.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save config: {e}")
