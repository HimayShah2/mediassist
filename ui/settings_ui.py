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
        self.import_path.setPlaceholderText("Path to old patient histories (CSV/Excel/PDF/HL7/FHIR)...")
        self.btn_import = QPushButton("Browse & Import")
        self.btn_import.clicked.connect(self._browse_and_import)

        self.import_layout.addWidget(self.import_path)
        self.import_layout.addWidget(self.btn_import)
        self.import_group.setLayout(self.import_layout)
        self.layout.addWidget(self.import_group)

        self.layout.addStretch()

    def _browse_and_import(self):
        from PySide6.QtWidgets import QFileDialog
        path = self.import_path.text().strip()
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self, "Select a records file", "",
                "Records (*.csv *.xlsx *.xls *.pdf *.hl7 *.json *.fhir);;All files (*)")
            if not path:
                return
            self.import_path.setText(path)
        try:
            from data_port.importer import DataImporter
            records = DataImporter().import_file(path)
        except Exception as e:
            logger.error(f"Import failed: {e}")
            QMessageBox.critical(self, "Import failed", str(e))
            return
        if not records:
            QMessageBox.warning(self, "Nothing imported",
                                "No records were parsed (unsupported format or missing optional "
                                "dependency for this file type).")
            return
        created = self._persist_imported(records)
        QMessageBox.information(self, "Import complete",
                                f"Parsed {len(records)} record(s); {created} new patient(s) added.")

    def _persist_imported(self, records):
        if not self.controller:
            return 0
        import datetime
        from models.db_models import Patient
        from patient.case_number import generate_case_number
        created = 0
        session = self.controller.get_db_session()
        try:
            for rec in records:
                fn = rec.get("first_name") or rec.get("First") or rec.get("firstName") or "Imported"
                ln = rec.get("last_name") or rec.get("Last") or rec.get("lastName") or "Patient"
                cn = rec.get("case_number") or rec.get("mrn") or generate_case_number(session, "IMP")
                if session.query(Patient).filter(Patient.case_number == cn).first():
                    continue
                session.add(Patient(case_number=cn, first_name=str(fn), last_name=str(ln),
                                    date_of_birth=str(rec.get("dob") or "1970-01-01"),
                                    gender=str(rec.get("gender") or "unknown"),
                                    notes="Imported from legacy records"))
                created += 1
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Persist imported failed: {e}")
        finally:
            session.close()
        return created

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
