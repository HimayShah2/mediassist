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
from ui.report_viewer_ui import ReportViewer
from ui.workers.report_worker import ReportWorker

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
        self.report_viewer = ReportViewer()

        # Add to stack
        self.stacked_widget.addWidget(self.dashboard_view)
        self.stacked_widget.addWidget(self.patient_view)
        self.stacked_widget.addWidget(self.questionnaire_view)
        self.stacked_widget.addWidget(self.vital_signs_view)
        self.stacked_widget.addWidget(self.physician_view)
        self.stacked_widget.addWidget(self.docs_view)
        self.stacked_widget.addWidget(self.settings_view)
        self.stacked_widget.addWidget(self.audit_view)
        self.stacked_widget.addWidget(self.report_viewer)

        # Tracks the case currently moving through intake -> vitals -> report
        self.active_case = None
        self._report_worker = None

        # Specialized connections
        self.patient_view.start_intake_requested.connect(self._start_questionnaire)
        self.questionnaire_view.session_complete.connect(lambda: self.navigate_to("vitals"))
        self.vital_signs_view.vitals_submitted.connect(self._generate_report)
        self.physician_view.review_requested.connect(self._open_saved_report)
        self.report_viewer.back_requested.connect(lambda: self.navigate_to("physician"))

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
        self.active_case = {
            "case_number": patient_ctx.get("case_number", "UNKNOWN"),
            "patient_ctx": patient_ctx,
            "visit_type": visit_type,
            "specialty": specialty,
        }
        # Fresh engine state for a new patient
        try:
            from models.questionnaire import SessionAnswers
            self.controller.questionnaire_engine.session_answers = SessionAnswers()
            self.controller.questionnaire_engine.raw_llm_log = []
            self.controller.questionnaire_engine.raw_rag_log = []
        except Exception as e:
            logger.warning(f"Could not reset questionnaire engine state: {e}")
        self.questionnaire_view.start_session(visit_type, patient_ctx, specialty)
        self.navigate_to("questionnaire")

    def _generate_report(self, vitals: dict):
        if not self.active_case:
            QMessageBox.warning(self, "No active case",
                                "Start a patient intake before generating a brief.")
            self.vital_signs_view.reset_generate_button()
            return

        engine = self.controller.questionnaire_engine
        try:
            engine.session_answers.vital_signs = vitals
        except Exception:
            pass

        case = self.active_case
        self._report_worker = ReportWorker(
            controller=self.controller,
            case_number=case["case_number"],
            session_answers=engine.session_answers,
            patient_ctx=case["patient_ctx"],
            vital_signs=vitals,
            specialty=case["specialty"],
        )
        self._report_worker.report_generated.connect(self._on_report_ready)
        self._report_worker.error_occurred.connect(self._on_report_error)
        self._report_worker.start()

    def _on_report_error(self, msg: str):
        self.vital_signs_view.reset_generate_button()
        QMessageBox.critical(self, "Report generation failed", msg)

    def _on_report_ready(self, brief):
        self.vital_signs_view.reset_generate_button()
        try:
            brief_dict = brief.model_dump(mode="json")
        except Exception:
            brief_dict = dict(getattr(brief, "__dict__", {}))

        engine = self.controller.questionnaire_engine
        flags_raised = list(getattr(engine.session_answers, "flags_raised", []) or [])
        brief_flag_levels = [str(f.get("level", "")) if isinstance(f, dict) else str(f)
                             for f in (brief_dict.get("flags", []) or [])]
        is_emergency = bool(brief_dict.get("is_emergency")) or any(
            ("RED" in str(x).upper() or "EMERGENCY" in str(x).upper())
            for x in (flags_raised + brief_flag_levels)
        )
        merged_flags = list(brief_dict.get("flags", []) or [])
        for f in flags_raised:
            merged_flags.append({"level": "RED" if "RED" in str(f).upper() else "AMBER",
                                 "reason": str(f), "category": "Intake red-flag detector"})
        payload = {
            **brief_dict,
            "flags": merged_flags,
            "is_emergency": is_emergency,
            "date": __import__("datetime").date.today().isoformat(),
            "raw_llm_log": getattr(engine, "raw_llm_log", []),
            "raw_rag_log": getattr(engine, "raw_rag_log", []),
        }

        case_number = self.active_case["case_number"] if self.active_case else brief_dict.get("case_number", "case")
        import os, json
        case_dir = os.path.join(os.getcwd(), "data", "cases", case_number)
        os.makedirs(case_dir, exist_ok=True)
        with open(os.path.join(case_dir, "physician_brief.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)

        if self.controller.current_user:
            self.controller.log_activity(
                user_id=self.controller.current_user,
                action="REPORT_GENERATED",
                case_number=case_number,
            )

        self._save_encounter(case_number, payload, vitals=self.vital_signs_view.get_vitals())

        self.report_viewer.load_brief(payload)
        self.physician_view.refresh_data()
        self.stacked_widget.setCurrentWidget(self.report_viewer)

    def _save_encounter(self, case_number, payload, vitals):
        """Write an Encounter row so the dashboard / patient history reflect the visit."""
        try:
            import json as _json
            from models.db_models import Patient, Encounter
            engine = self.controller.questionnaire_engine
            case = self.active_case or {}
            diffs = payload.get("differentials", [])
            top = ", ".join(
                (d.get("condition_name") if isinstance(d, dict) else str(d)) for d in diffs[:3]
            )
            summary = f"Top differentials: {top}. Confidence {payload.get('confidence_score', 0):.0%}."
            session = self.controller.get_db_session()
            try:
                pat = session.query(Patient).filter(Patient.case_number == case_number).first()
                if pat is None:
                    pat = Patient(case_number=case_number, first_name="Unknown", last_name="Patient",
                                  date_of_birth="1970-01-01", gender="unknown")
                    session.add(pat); session.flush()
                enc = Encounter(
                    patient_id=pat.id,
                    case_number=case_number,
                    encounter_type=case.get("visit_type", "intake"),
                    chief_complaint=case.get("patient_ctx", {}).get("chief_complaint_summary"),
                    triage_category="EMERGENCY" if payload.get("is_emergency") else "ROUTINE",
                    vitals_json=_json.dumps(vitals or {}),
                    questionnaire_json=_json.dumps(getattr(engine.session_answers, "model_dump", dict)()
                                                  if hasattr(engine.session_answers, "model_dump") else {}, default=str),
                    ai_summary=summary,
                )
                session.add(enc)
                session.commit()
            finally:
                session.close()
        except Exception as e:
            logger.warning(f"Could not persist encounter for {case_number}: {e}")

    def _open_saved_report(self, case_number: str):
        import os, json
        pb = os.path.join(os.getcwd(), "data", "cases", case_number, "physician_brief.json")
        if not os.path.exists(pb):
            QMessageBox.warning(self, "Not found", f"No brief saved for {case_number}.")
            return
        with open(pb, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.report_viewer.load_brief(data)
        self.stacked_widget.setCurrentWidget(self.report_viewer)

    def navigate_to(self, view_name: str):
        # Activity Logging
        if self.controller.current_user:
            self.controller.log_activity(
                user_id=self.controller.current_user,
                action="NAVIGATE_TO",
                details={"view": view_name}
            )

        if view_name == "dashboard":
            if hasattr(self.dashboard_view, "refresh_data"):
                self.dashboard_view.refresh_data()
            self.stacked_widget.setCurrentWidget(self.dashboard_view)
        elif view_name == "patients":
            self.stacked_widget.setCurrentWidget(self.patient_view)
        elif view_name == "questionnaire":
            self.stacked_widget.setCurrentWidget(self.questionnaire_view)
        elif view_name == "vitals":
            self.stacked_widget.setCurrentWidget(self.vital_signs_view)
        elif view_name == "physician":
            self.physician_view.refresh_data()
            self.stacked_widget.setCurrentWidget(self.physician_view)
        elif view_name == "documents":
            self.stacked_widget.setCurrentWidget(self.docs_view)
        elif view_name == "settings":
            self.stacked_widget.setCurrentWidget(self.settings_view)
        elif view_name == "audit":
            self.stacked_widget.setCurrentWidget(self.audit_view)
