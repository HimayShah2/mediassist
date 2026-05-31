from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QHBoxLayout, QMessageBox, QFrame)
from PySide6.QtCore import Qt, Signal
from loguru import logger
import datetime

class LoginUI(QWidget):
    """
    Role-based Login Interface (Blueprint §9.2).
    Supports Doctor, Nurse, and Admin roles.
    """
    login_successful = Signal(str, str)  # username, role

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
        # Main layout centered
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setAlignment(Qt.AlignCenter)
        
        # Login Card
        self.card = QFrame()
        self.card.setObjectName("stat_card")
        self.card.setFixedWidth(400)
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(30, 40, 30, 40)
        self.card_layout.setSpacing(20)
        
        # Logo/Title
        self.title = QLabel("MediAssist Pro")
        self.title.setObjectName("header_title")
        self.title.setAlignment(Qt.AlignCenter)
        
        self.subtitle = QLabel("Please sign in to continue")
        self.subtitle.setObjectName("muted_text")
        self.subtitle.setAlignment(Qt.AlignCenter)
        
        self.card_layout.addWidget(self.title)
        self.card_layout.addWidget(self.subtitle)
        
        # Credentials
        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Username / ID")
        self.input_user.setMinimumHeight(44)
        
        self.input_pass = QLineEdit()
        self.input_pass.setPlaceholderText("PIN / Password")
        self.input_pass.setEchoMode(QLineEdit.Password)
        self.input_pass.setMinimumHeight(44)
        
        self.card_layout.addWidget(self.input_user)
        self.card_layout.addWidget(self.input_pass)
        
        # Role Buttons for Demo/Quick Selection
        self.btn_nurse = QPushButton("Login as Nurse")
        self.btn_nurse.clicked.connect(lambda: self._attempt_login("NURSE"))
        
        self.btn_doctor = QPushButton("Login as Doctor")
        self.btn_doctor.clicked.connect(lambda: self._attempt_login("DOCTOR"))
        
        self.btn_admin = QPushButton("Login as Admin")
        self.btn_admin.setObjectName("action_primary")
        self.btn_admin.clicked.connect(lambda: self._attempt_login("ADMIN"))
        
        self.card_layout.addWidget(self.btn_nurse)
        self.card_layout.addWidget(self.btn_doctor)
        self.card_layout.addWidget(self.btn_admin)
        
        self.root_layout.addWidget(self.card)

    def _attempt_login(self, role):
        username = self.input_user.text().strip()
        if not username:
            QMessageBox.warning(self, "Input Required", "Please enter a Username.")
            return

        # In a real app, verify password_hash in 'users' table
        logger.info(f"User {username} logged in as {role}")
        
        # Log to Audit Table (Blueprint §12.3)
        self.controller.log_activity(
            user_id=username,
            action="USER_LOGIN",
            details={"role": role, "timestamp": datetime.datetime.now().isoformat()}
        )
        
        self.login_successful.emit(username, role)
