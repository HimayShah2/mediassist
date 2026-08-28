import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QStackedWidget, QCheckBox, QComboBox, QLineEdit, QTextEdit, 
    QGroupBox, QFormLayout, QScrollArea, QSpinBox, QRadioButton, QButtonGroup,
    QMessageBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from loguru import logger

class GuidedWizardUI(QWidget):
    session_complete = Signal(dict)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.patient_ctx = {}
        self.payload = {}
        self.setup_ui()

    def start_session(self, patient_ctx):
        self.patient_ctx = patient_ctx
        self.payload = {}
        self.stacked_widget.setCurrentIndex(0)
        self.update_nav_buttons()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Header
        self.header_lbl = QLabel("Guided OPD Flow")
        self.header_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e3a8a;")
        main_layout.addWidget(self.header_lbl)

        # Stacked Widget for Pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)

        # Build Pages
        self.pages = [
            ChiefComplaintPage(self),
            SymptomDetailsPage(self),
            FollowUpPage(self),
            PastHistoryPage(self),
            FamilyHistoryPage(self),
            ImmunisationPage(self),
            DevelopmentalPage(self),
            VitalsPage(self),
            ExaminationPage(self),
            ManagementPlanPage(self)
        ]

        for page in self.pages:
            self.stacked_widget.addWidget(page)

        # Navigation Bar
        nav_layout = QHBoxLayout()
        self.btn_back = QPushButton("<< Back")
        self.btn_back.clicked.connect(self.go_back)
        
        self.btn_next = QPushButton("Next >>")
        self.btn_next.clicked.connect(self.go_next)
        
        self.btn_finish = QPushButton("Finish Intake")
        self.btn_finish.setStyleSheet("background-color: #22c55e; color: white;")
        self.btn_finish.clicked.connect(self.finish_wizard)
        self.btn_finish.hide()
        
        nav_layout.addWidget(self.btn_back)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_next)
        nav_layout.addWidget(self.btn_finish)
        
        main_layout.addLayout(nav_layout)
        self.update_nav_buttons()

    def go_back(self):
        idx = self.stacked_widget.currentIndex()
        if idx > 0:
            self.stacked_widget.setCurrentIndex(idx - 1)
        self.update_nav_buttons()

    def go_next(self):
        current_page = self.stacked_widget.currentWidget()
        if hasattr(current_page, 'save_data'):
            self.payload.update(current_page.save_data())
            
        idx = self.stacked_widget.currentIndex()
        if idx < self.stacked_widget.count() - 1:
            self.stacked_widget.setCurrentIndex(idx + 1)
        self.update_nav_buttons()

    def update_nav_buttons(self):
        idx = self.stacked_widget.currentIndex()
        self.btn_back.setEnabled(idx > 0)
        
        if idx == self.stacked_widget.count() - 1:
            self.btn_next.hide()
            self.btn_finish.show()
        else:
            self.btn_next.show()
            self.btn_finish.hide()

    def finish_wizard(self):
        current_page = self.stacked_widget.currentWidget()
        if hasattr(current_page, 'save_data'):
            self.payload.update(current_page.save_data())
            
        logger.info(f"Wizard complete. Payload: {self.payload}")
        self.session_complete.emit(self.payload)

# --- Pages ---

class ChiefComplaintPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>1. Chief Complaint</h2>"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter primary reason for visit...")
        layout.addWidget(self.text_edit)
        
    def save_data(self):
        return {"chief_complaint": self.text_edit.toPlainText().strip()}

class SymptomDetailsPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>2. Symptom Details (HPI)</h2>"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Duration, severity, relieving factors...")
        layout.addWidget(self.text_edit)
        
    def save_data(self):
        return {"hpi": self.text_edit.toPlainText().strip()}

class FollowUpPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>3. Follow Up Details</h2>"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("If this is a follow-up, list changes since last visit...")
        layout.addWidget(self.text_edit)
        
    def save_data(self):
        return {"follow_up": self.text_edit.toPlainText().strip()}

class PastHistoryPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>4. Past Medical & Surgical History</h2>"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Previous illnesses, surgeries, chronic conditions...")
        layout.addWidget(self.text_edit)
        
    def save_data(self):
        return {"past_history": self.text_edit.toPlainText().strip()}

class FamilyHistoryPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>5. Family History</h2>"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Hereditary conditions, family illnesses...")
        layout.addWidget(self.text_edit)
        
    def save_data(self):
        return {"family_history": self.text_edit.toPlainText().strip()}

class ImmunisationPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>6. Immunisation History</h2>"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Vaccination records, up to date?")
        layout.addWidget(self.text_edit)
        
    def save_data(self):
        return {"immunisation": self.text_edit.toPlainText().strip()}

class DevelopmentalPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>7. Developmental History (Pediatrics)</h2>"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Milestones, growth, concerns...")
        layout.addWidget(self.text_edit)
        
    def save_data(self):
        return {"developmental_history": self.text_edit.toPlainText().strip()}

class VitalsPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        layout = QFormLayout(self)
        layout.addRow(QLabel("<h2>8. Preliminary Vitals</h2>"))
        self.bp = QLineEdit()
        self.hr = QLineEdit()
        self.temp = QLineEdit()
        self.spo2 = QLineEdit()
        layout.addRow("Blood Pressure:", self.bp)
        layout.addRow("Heart Rate:", self.hr)
        layout.addRow("Temperature:", self.temp)
        layout.addRow("SpO2:", self.spo2)
        
    def save_data(self):
        return {
            "vitals": {
                "blood_pressure": self.bp.text().strip(),
                "heart_rate": self.hr.text().strip(),
                "temperature": self.temp.text().strip(),
                "spo2": self.spo2.text().strip()
            }
        }

class ExaminationPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>9. Nurse Examination Notes</h2>"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("General appearance, visible distress...")
        layout.addWidget(self.text_edit)
        
    def save_data(self):
        return {"examination": self.text_edit.toPlainText().strip()}

class ManagementPlanPage(QWidget):
    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<h2>10. Medications & Allergies</h2>"))
        self.meds = QTextEdit()
        self.meds.setPlaceholderText("Current medications...")
        self.allergies = QTextEdit()
        self.allergies.setPlaceholderText("Known allergies...")
        layout.addWidget(QLabel("Current Medications:"))
        layout.addWidget(self.meds)
        layout.addWidget(QLabel("Allergies:"))
        layout.addWidget(self.allergies)
        
    def save_data(self):
        return {
            "medications": self.meds.toPlainText().strip(),
            "allergies": self.allergies.toPlainText().strip()
        }