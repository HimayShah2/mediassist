from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                               QComboBox, QFormLayout, QLineEdit, QSpinBox, QDoubleSpinBox, 
                               QHBoxLayout, QCheckBox, QMessageBox)
from PySide6.QtCore import Qt, Signal
from loguru import logger

from patient.case_number import generate_case_number
from models.db_models import Patient

class PatientView(QWidget):
    start_intake_requested = Signal(str, dict, str)  # visit_type, patient_ctx, specialty

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        self.title = QLabel("Patient Management & Intake")
        self.title.setObjectName("header_title")
        self.title.setAlignment(Qt.AlignCenter)
        
        self.subtitle = QLabel("Enter patient details and initiate an AI-driven intake session.")
        self.subtitle.setObjectName("muted_text")
        self.subtitle.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.subtitle)

        # Form for basic patient details
        self.form_layout = QFormLayout()
        
        # Case Number with Fetch button
        self.case_num_layout = QHBoxLayout()
        self.input_case_num = QLineEdit()
        self.input_case_num.setPlaceholderText("e.g. DEV-2026-0001 (Leave blank to generate)")
        self.btn_fetch = QPushButton("Fetch Details")
        self.btn_fetch.clicked.connect(self._fetch_patient)
        self.case_num_layout.addWidget(self.input_case_num)
        self.case_num_layout.addWidget(self.btn_fetch)
        
        self.input_first_name = QLineEdit()
        self.input_last_name = QLineEdit()
        
        self.input_age = QSpinBox()
        self.input_age.setRange(0, 120)
        self.input_age.setValue(30)
        
        self.input_sex = QComboBox()
        self.input_sex.addItems(["Male", "Female", "Other"])
        
        self.input_weight = QDoubleSpinBox()
        self.input_weight.setRange(0.0, 300.0)
        self.input_weight.setSuffix(" kg")
        self.input_weight.setValue(70.0)
        
        # Adaptive label for complaint
        self.lbl_complaint = QLabel("Chief Complaint:")
        self.input_complaint = QLineEdit()
        self.input_complaint.setPlaceholderText("Brief description...")
        
        self.visit_type_combo = QComboBox()
        self.visit_type_combo.addItems([
            "Vaccination/Immunization Visit",
            "General/Routine Checkup", 
            "Specific Complaint / Acute Visit", 
            "Follow-up for Previous Condition", 
            "Maternal/Antenatal Care",
            "Pediatric Well-Visit",
            "Mental Health Screening"
        ])
        self.visit_type_combo.currentTextChanged.connect(self._update_complaint_label)
        
        self.specialty_combo = QComboBox()
        self.specialty_combo.addItems([
            "General Medicine", "Pediatrics", "Obstetrics", "Gynecology",
            "Cardiology", "Dermatology", "Endocrinology", "Gastroenterology",
            "Hematology", "Infectious Disease", "Nephrology", "Neurology",
            "Oncology", "Ophthalmology", "Orthopedics", "Otolaryngology (ENT)",
            "Psychiatry", "Pulmonology", "Rheumatology", "Urology", "Emergency Medicine"
        ])

        # History Toggle
        self.toggle_no_history = QCheckBox("No Prior Medical History Available / First Visit")
        self.toggle_no_history.setStyleSheet("margin-top: 10px; font-weight: bold; color: #38bdf8;")

        # Domain Override Toggle
        self.toggle_all_knowledge = QCheckBox("Enable all knowledge bases (Override domain restriction)")
        self.toggle_all_knowledge.setStyleSheet("color: #94a3b8; font-style: italic;")

        # Add rows to the form
        self.form_layout.addRow("Case Number:", self.case_num_layout)
        self.form_layout.addRow("First Name:", self.input_first_name)
        self.form_layout.addRow("Last Name:", self.input_last_name)
        self.form_layout.addRow("Age:", self.input_age)
        self.form_layout.addRow("Sex:", self.input_sex)
        self.form_layout.addRow("Weight:", self.input_weight)
        self.form_layout.addRow(self.lbl_complaint, self.input_complaint)
        self.form_layout.addRow("Visit Type:", self.visit_type_combo)
        self.form_layout.addRow("Clinical Domain:", self.specialty_combo)
        self.form_layout.addRow("", self.toggle_no_history)
        self.form_layout.addRow("", self.toggle_all_knowledge)
        
        self.layout.addLayout(self.form_layout)
        
        self.btn_start = QPushButton("Start AI Clinical Intake")
        self.btn_start.setMinimumHeight(50)
        self.btn_start.setObjectName("action_primary")
        self.btn_start.clicked.connect(self._on_start_clicked)
        
        # Delete Button (Only for Admin)
        self.btn_delete = QPushButton("Delete Patient Record")
        self.btn_delete.setMinimumHeight(50)
        self.btn_delete.setObjectName("action_emergency") # Red style
        self.btn_delete.clicked.connect(self._delete_patient)
        self.btn_delete.hide() # Hidden by default, shown by RBAC
        
        self.layout.addWidget(self.btn_start)
        self.layout.addWidget(self.btn_delete)
        self.layout.addStretch()
        
        # Check RBAC
        self._apply_rbac()

    def _apply_rbac(self):
        if self.controller and self.controller.current_role == "ADMIN":
            self.btn_delete.show()

    def _delete_patient(self):
        """Soft-deletes the currently loaded patient."""
        case_num = self.input_case_num.text().strip()
        if not case_num:
            return
            
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            f"Are you sure you want to delete patient {case_num}? This action is irreversible.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from patient.patient_manager import PatientManager
            manager = PatientManager()
            session = self.controller.get_db_session()
            try:
                success = manager.soft_delete_patient(session, case_num)
                if success:
                    session.commit()
                    QMessageBox.information(self, "Deleted", "Patient record has been soft-deleted.")
                    self.input_case_num.clear()
                    self.input_first_name.clear()
                    self.input_last_name.clear()
                    self.input_first_name.setReadOnly(False)
                    self.input_last_name.setReadOnly(False)
                else:
                    QMessageBox.warning(self, "Error", "Could not find patient record to delete.")
            except Exception as e:
                session.rollback()
                logger.error(f"Delete failed: {e}")
                QMessageBox.critical(self, "Error", f"Deletion failed: {e}")
            finally:
                session.close()
        
        # Initial label update
        self._update_complaint_label(self.visit_type_combo.currentText())

    def _update_complaint_label(self, visit_type):
        """Dynamically updates the complaint label based on visit type."""
        mapping = {
            "Vaccination/Immunization Visit": "Reason for Vaccination:",
            "General/Routine Checkup": "Primary Health Goals:",
            "Specific Complaint / Acute Visit": "Chief Complaint / Symptoms:",
            "Follow-up for Previous Condition": "Update on Condition:",
            "Maternal/Antenatal Care": "Maternal Concerns:",
            "Pediatric Well-Visit": "Developmental/Health Concerns:",
            "Mental Health Screening": "Mental Health Symptoms:"
        }
        label_text = mapping.get(visit_type, "Reason for Visit:")
        self.lbl_complaint.setText(label_text)

    def _fetch_patient(self):
        """Queries the DB for patient details by case number."""
        case_num = self.input_case_num.text().strip()
        if not case_num:
            QMessageBox.warning(self, "Input Required", "Please enter a Case Number to fetch.")
            return

        if not self.controller:
            return

        session = self.controller.get_db_session()
        try:
            patient = session.query(Patient).filter(Patient.case_number == case_num).first()
            if patient:
                self.input_first_name.setText(patient.first_name)
                self.input_last_name.setText(patient.last_name)
                # Current sex/gender setup
                self.input_sex.setCurrentText(patient.gender.capitalize())
                # Lock fields for existing patient
                self.input_first_name.setReadOnly(True)
                self.input_last_name.setReadOnly(True)
                QMessageBox.information(self, "Success", f"Found record for {patient.first_name} {patient.last_name}.")
            else:
                QMessageBox.warning(self, "Not Found", f"No patient found with Case Number: {case_num}")
        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            QMessageBox.critical(self, "Error", f"Database query failed: {e}")
        finally:
            session.close()

    def _on_start_clicked(self):
        # Extract data from the UI dynamically
        case_num = self.input_case_num.text().strip()
        first_name = self.input_first_name.text().strip()
        last_name = self.input_last_name.text().strip()
        age = self.input_age.value()
        sex = self.input_sex.currentText().lower()
        weight = self.input_weight.value()
        complaint = self.input_complaint.text().strip() or "No specific complaint provided."
        
        # Auto-generate case number if blank
        if not case_num:
            if self.controller:
                session = self.controller.get_db_session()
                case_num = generate_case_number(session, "DEV")
                self.input_case_num.setText(case_num)
                session.close()
            else:
                case_num = "NEW-GEN-0000"

        # Build the patient context for the LLM
        patient_ctx = {
            "case_number": case_num,
            "name": f"{first_name} {last_name}".strip() or "Unknown Patient",
            "demographics": f"{age}-year-old {sex}",
            "weight_kg": weight,
            "chronic_conditions": [], 
            "chief_complaint_summary": complaint,
            "no_history_toggle": self.toggle_no_history.isChecked(),
            "allow_all_domains": self.toggle_all_knowledge.isChecked()
        }
        
        visit_type = self.visit_type_combo.currentText()
        specialty = self.specialty_combo.currentText()

        # Persist / update the patient record so it shows up in the dashboard & fetch
        self._save_patient(case_num, first_name, last_name, age, sex)

        self.start_intake_requested.emit(visit_type, patient_ctx, specialty)

    def _save_patient(self, case_num, first_name, last_name, age, sex):
        if not self.controller:
            return
        try:
            import datetime
            from models.db_models import Patient
            dob = (datetime.date.today() - datetime.timedelta(days=int(age) * 365)).isoformat()
            session = self.controller.get_db_session()
            try:
                p = session.query(Patient).filter(Patient.case_number == case_num).first()
                if p is None:
                    p = Patient(case_number=case_num,
                                first_name=first_name or "Unknown",
                                last_name=last_name or "Patient",
                                date_of_birth=dob, gender=sex or "unknown")
                    session.add(p)
                else:
                    if first_name:
                        p.first_name = first_name
                    if last_name:
                        p.last_name = last_name
                    p.gender = sex or p.gender
                session.commit()
            finally:
                session.close()
        except Exception as e:
            logger.warning(f"Could not persist patient {case_num}: {e}")
