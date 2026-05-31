import json
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                               QPushButton, QLineEdit, QFormLayout, QGroupBox, QCheckBox, QComboBox,
                               QDoubleSpinBox, QSpinBox, QMessageBox)
from PySide6.QtCore import Qt
from loguru import logger

class SettingsUI(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self.title = QLabel("Application Settings")
        self.title.setObjectName("header_title")
        self.layout.addWidget(self.title)

        # Keys Group
        self.keys_group = QGroupBox("NVIDIA NIM API Keys")
        self.keys_layout = QFormLayout()
        
        self.key_inputs = []
        for i in range(1, 8):
            inp = QLineEdit()
            inp.setPlaceholderText(f"nvapi-...")
            inp.setEchoMode(QLineEdit.Password)
            self.keys_layout.addRow(f"Key {i}:", inp)
            self.key_inputs.append(inp)
        
        self.btn_save_keys = QPushButton("Save API Keys")
        self.btn_save_keys.setObjectName("action_primary")
        self.keys_layout.addRow("", self.btn_save_keys)
        self.keys_group.setLayout(self.keys_layout)
        self.layout.addWidget(self.keys_group)

        # Doctor Field Group
        self.field_group = QGroupBox("Active Doctor Field (Specialty Configuration)")
        self.field_layout = QHBoxLayout()
        self.field_combo = QComboBox()
        self._load_doctor_fields()
        self.field_layout.addWidget(self.field_combo)
        
        self.btn_save_field = QPushButton("Apply Field")
        self.btn_save_field.setObjectName("action_primary")
        self.field_layout.addWidget(self.btn_save_field)
        self.field_group.setLayout(self.field_layout)
        self.layout.addWidget(self.field_group)

        # Web Search Configuration
        self.web_group = QGroupBox("Web Search Configuration")
        self.web_layout = QVBoxLayout()
        self.trusted_sites_input = QLineEdit()
        self.trusted_sites_input.setPlaceholderText("e.g. who.int, cdc.gov, nih.gov (comma separated)")
        from config.settings import settings
        self.trusted_sites_input.setText(settings.trusted_sites)
        self.web_layout.addWidget(QLabel("Trusted Domains (Restricted Search):"))
        self.web_layout.addWidget(self.trusted_sites_input)
        self.web_group.setLayout(self.web_layout)
        self.layout.addWidget(self.web_group)

        # AI Model Parameters
        self.ai_group = QGroupBox("AI Model Parameters")
        self.ai_layout = QFormLayout()
        
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 1.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setValue(settings.ai_temperature)
        
        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(128, 16384)
        self.tokens_spin.setSingleStep(256)
        self.tokens_spin.setValue(settings.ai_max_tokens)

        self.ai_layout.addRow("Temperature (0=Deterministic, 1=Creative):", self.temp_spin)
        self.ai_layout.addRow("Max Output Tokens:", self.tokens_spin)
        
        self.btn_save_ai = QPushButton("Apply AI Parameters")
        self.btn_save_ai.setObjectName("action_primary")
        self.btn_save_ai.clicked.connect(self._save_ai_settings)
        self.ai_layout.addRow("", self.btn_save_ai)
        
        self.ai_group.setLayout(self.ai_layout)
        self.layout.addWidget(self.ai_group)

        # Visit Types Group
        self.visit_group = QGroupBox("Active Visit Types")
        self.visit_layout = QVBoxLayout()
        
        visit_types = [
            "Vaccination/Immunization Visit",
            "General/Routine Checkup",
            "Specific Complaint / Acute Visit",
            "Follow-up for Previous Condition",
            "Maternal/Antenatal Care",
            "Pediatric Well-Visit",
            "Mental Health Screening"
        ]
        
        for vt in visit_types:
            cb = QCheckBox(vt)
            cb.setChecked(True)
            self.visit_layout.addWidget(cb)
            
        self.visit_group.setLayout(self.visit_layout)
        self.layout.addWidget(self.visit_group)

        # Legacy Import Group
        self.import_group = QGroupBox("Legacy Data Import")
        self.import_layout = QHBoxLayout()
        
        self.import_path = QLineEdit()
        self.import_path.setPlaceholderText("Path to old patient histories (CSV/Excel)...")
        self.btn_import = QPushButton("Browse & Import")
        
        self.import_layout.addWidget(self.import_path)
        self.import_layout.addWidget(self.btn_import)
        self.import_group.setLayout(self.import_layout)
        self.layout.addWidget(self.import_group)

        self.layout.addStretch()

    def _save_ai_settings(self):
        from config.settings import settings
        settings.trusted_sites = self.trusted_sites_input.text()
        settings.ai_temperature = self.temp_spin.value()
        settings.ai_max_tokens = self.tokens_spin.value()
        QMessageBox.information(self, "Success", "AI and Web Search settings applied for this session.")

    def _load_doctor_fields(self):
        try:
            fields_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "doctor_fields.json")
            with open(fields_path, "r", encoding="utf-8") as f:
                fields = json.load(f)
                for key, data in fields.items():
                    self.field_combo.addItem(data["name"], userData=key)
        except Exception as e:
            logger.warning(f"Could not load doctor fields: {e}")
            self.field_combo.addItem("Default (All Enabled)", userData="default")
