from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Signal, Qt

class Sidebar(QWidget):
    # Signal emitted when a navigation button is clicked
    navigation_requested = Signal(str)
    logout_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self.setObjectName("sidebar")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 20, 10, 20)

        # Title
        self.title = QLabel("MediAssist Pro")
        self.title.setObjectName("header_title")
        self.title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title)

        # Navigation Buttons
        self.btn_dashboard = QPushButton("Nurse Dashboard")
        self.btn_dashboard.setProperty("class", "sidebar_btn")
        self.btn_dashboard.clicked.connect(lambda: self.navigation_requested.emit("dashboard"))
        self.main_layout.addWidget(self.btn_dashboard)

        self.btn_patients = QPushButton("Patient Management")
        self.btn_patients.setProperty("class", "sidebar_btn")
        self.btn_patients.clicked.connect(lambda: self.navigation_requested.emit("patients"))
        self.main_layout.addWidget(self.btn_patients)
        
        self.btn_physician = QPushButton("Physician Dashboard")
        self.btn_physician.setProperty("class", "sidebar_btn")
        self.btn_physician.clicked.connect(lambda: self.navigation_requested.emit("physician"))
        self.main_layout.addWidget(self.btn_physician)
        
        self.btn_docs = QPushButton("Document Library (RAG)")
        self.btn_docs.setProperty("class", "sidebar_btn")
        self.btn_docs.clicked.connect(lambda: self.navigation_requested.emit("documents"))
        self.main_layout.addWidget(self.btn_docs)

        self.btn_audit = QPushButton("System Audit Logs")
        self.btn_audit.setProperty("class", "sidebar_btn")
        self.btn_audit.clicked.connect(lambda: self.navigation_requested.emit("audit"))
        self.main_layout.addWidget(self.btn_audit)

        # Spacer at the bottom
        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addItem(self.spacer)
        
        self.btn_settings = QPushButton("Settings")
        self.btn_settings.setProperty("class", "sidebar_btn")
        self.btn_settings.clicked.connect(lambda: self.navigation_requested.emit("settings"))
        self.main_layout.addWidget(self.btn_settings)

        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setProperty("class", "sidebar_btn")
        self.btn_logout.setStyleSheet("color: #e11d48; font-weight: bold;") # Red text for logout
        self.btn_logout.clicked.connect(lambda: self.logout_requested.emit())
        self.main_layout.addWidget(self.btn_logout)
