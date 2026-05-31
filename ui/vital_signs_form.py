from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QRadioButton, QTabWidget, 
                               QStackedWidget, QFormLayout, QGroupBox)

class VitalSignsForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.form_widget = QWidget()
        form_layout = QFormLayout(self.form_widget)
        
        self.hr_input = QLineEdit()
        self.bp_input = QLineEdit()
        self.temp_input = QLineEdit()
        self.rr_input = QLineEdit()
        
        form_layout.addRow("Heart Rate (bpm):", self.hr_input)
        form_layout.addRow("Blood Pressure (mmHg):", self.bp_input)
        form_layout.addRow("Temperature (°C):", self.temp_input)
        form_layout.addRow("Respiratory Rate:", self.rr_input)

        self.layout.addWidget(self.form_widget)
        self.layout.addStretch()
        
    def get_vitals(self):
        return {
            "heart_rate": self.hr_input.text(),
            "blood_pressure": self.bp_input.text(),
            "temperature": self.temp_input.text(),
            "respiratory_rate": self.rr_input.text()
        }

class VitalSignsManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Toggle Layout
        toggle_layout = QHBoxLayout()
        self.lbl_toggle = QLabel("Vitals Display Mode:")
        self.rb_inline = QRadioButton("Inline")
        self.rb_tab = QRadioButton("Separate Tab")
        self.rb_inline.setChecked(True)
        
        toggle_layout.addWidget(self.lbl_toggle)
        toggle_layout.addWidget(self.rb_inline)
        toggle_layout.addWidget(self.rb_tab)
        toggle_layout.addStretch()
        
        self.layout.addLayout(toggle_layout)
        
        # Container stack
        self.stacked = QStackedWidget()
        
        # Mode 1: Inline
        self.inline_container = QGroupBox("Vital Signs")
        self.inline_layout = QVBoxLayout(self.inline_container)
        
        # Mode 2: Tabbed
        self.tab_container = QTabWidget()
        
        self.stacked.addWidget(self.inline_container)
        self.stacked.addWidget(self.tab_container)
        
        self.layout.addWidget(self.stacked)
        
        # The form itself
        self.vitals_form = VitalSignsForm()
        self.inline_layout.addWidget(self.vitals_form)
        
        self.rb_inline.toggled.connect(self.switch_mode)
        
    def switch_mode(self):
        self.vitals_form.setParent(None)
        
        if self.rb_inline.isChecked():
            self.inline_layout.addWidget(self.vitals_form)
            self.stacked.setCurrentWidget(self.inline_container)
        else:
            self.tab_container.clear()
            self.tab_container.addTab(self.vitals_form, "Vital Signs")
            self.stacked.setCurrentWidget(self.tab_container)
            
    def get_vitals(self):
        return self.vitals_form.get_vitals()
