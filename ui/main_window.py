from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget,
    QApplication, QMessageBox
)
from PySide6.QtCore import Qt
import os
from loguru import logger

from ui.sidebar import Sidebar
from ui.dashboard import DashboardView
from ui.patients import PatientView
from ui.questionnaire_ui import QuestionnaireUI
from ui.vital_signs_form import VitalSignsManager
from ui.physician_dashboard_ui import PhysicianDashboardView
from ui.document_manager_ui import DocumentManagerUI
from ui.settings_ui import SettingsUI
from ui.audit_log_ui import AuditLogUI
from ui.login_ui import LoginUI

class MainWindow(QMainWindow):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("MediAssist Pro")
        self.resize(1200, 800)

        # Central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Login View (Shown first)
        self.login_view = LoginUI(self.controller)
        self.login_view.login_successful.connect(self._on_login_success)

        # 2. Sidebar navigation (Hidden until login)
        self.sidebar = Sidebar()
        self.sidebar.hide()
        self.main_layout.addWidget(self.sidebar)

        # 3. Stacked widget for views
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget, 1)

        # Add login view to stack
        self.stacked_widget.addWidget(self.login_view)
        self.stacked_widget.setCurrentWidget(self.login_view)

        # Initialize other views
        self._init_app_views()

        # Connect signals
        self.sidebar.navigation_requested.connect(self.navigate_to)
        self.sidebar.logout_requested.connect(self._on_logout)
        
    def _init_app_views(self):
        self.dashboard_view = DashboardView()
        self.patient_view = PatientView(self.controller)
        self.questionnaire_view = QuestionnaireUI(self.controller)
        self.vital_signs_view = VitalSignsManager()
        self.physician_view = PhysicianDashboardView()
        self.docs_view = DocumentManagerUI(self.controller)
        self.settings_view = SettingsUI(self.controller)
        self.audit_view = AuditLogUI(self.controller)

        # Add to stack
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.patient_view)
        self.stacked_widget.addWidget(self.questionnaire_view)
        self.stacked_widget.addWidget(self.vital_signs_view)
        self.stacked_widget.addWidget(self.physician_view)
        self.stacked_widget.addWidget(self.docs_view)
        self.stacked_widget.addWidget(self.settings_view)
        self.stacked_widget.addWidget(self.audit_view)

        # Specialized connections
        self.patient_view.start_intake_requested.connect(self._start_questionnaire)
        self.questionnaire_view.session_complete.connect(lambda: self.navigate_to("vitals"))

    def _on_login_success(self, username, role):
        self.controller.current_user = username
        self.controller.current_role = role
        
        # Apply Role-Based Access Control (RBAC) to Sidebar
        self._apply_rbac(role)
        
        # Refresh views that have role-dependent features
        self.patient_view._apply_rbac()
        
        self.sidebar.show()
        self.navigate_to("dashboard")
        
        QMessageBox.information(self, "Welcome", f"Logged in as {username} ({role})")

    def _on_logout(self):
        """Clean up session and return to login screen."""
        if self.controller.current_user:
            self.controller.log_activity(
                user_id=self.controller.current_user,
                action="USER_LOGOUT"
            )
            
        self.controller.current_user = None
        self.controller.current_role = None
        
        # Hide role-dependent features
        self.patient_view.btn_delete.hide()
        
        self.sidebar.hide()
        self.stacked_widget.setCurrentWidget(self.login_view)
        QMessageBox.information(self, "Logged Out", "You have been securely logged out.")

    def _apply_rbac(self, role):
        """Restrict sidebar buttons based on user role."""
        # Reset visibility
        self.sidebar.btn_dashboard.show()
        self.sidebar.btn_patients.show()
        self.sidebar.btn_physician.show()
        self.sidebar.btn_docs.show()
        self.sidebar.btn_audit.show()
        self.sidebar.btn_settings.show()

        if role == "NURSE":
            self.sidebar.btn_physician.hide()
            self.sidebar.btn_docs.hide()
            self.sidebar.btn_audit.hide()
            self.sidebar.btn_settings.hide()
        elif role == "DOCTOR":
            self.sidebar.btn_docs.hide()
            self.sidebar.btn_audit.hide()
            self.sidebar.btn_settings.hide()
        # ADMIN has access to all

    def _start_questionnaire(self, visit_type, patient_ctx, specialty):
        self.questionnaire_view.start_session(visit_type, patient_ctx, specialty)
        self.navigate_to("questionnaire")

    def navigate_to(self, view_name: str):
        # Activity Logging
        if self.controller.current_user:
            self.controller.log_activity(
                user_id=self.controller.current_user,
                action="NAVIGATE_TO",
                details={"view": view_name}
            )

        if view_name == "dashboard":
            self.stacked_widget.setCurrentWidget(self.dashboard_view)
        elif view_name == "patients":
            self.stacked_widget.setCurrentWidget(self.patient_view)
        elif view_name == "questionnaire":
            self.stacked_widget.setCurrentWidget(self.questionnaire_view)
        elif view_name == "vitals":
            self.stacked_widget.setCurrentWidget(self.vital_signs_view)
        elif view_name == "physician":
            self.stacked_widget.setCurrentWidget(self.physician_view)
        elif view_name == "documents":
            self.stacked_widget.setCurrentWidget(self.docs_view)
        elif view_name == "settings":
            self.stacked_widget.setCurrentWidget(self.settings_view)
        elif view_name == "audit":
            self.stacked_widget.setCurrentWidget(self.audit_view)
