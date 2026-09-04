import json
import os
import re
from loguru import logger
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                               QScrollArea, QToolTip, QFrame, QMessageBox, QTextEdit)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QCursor

from models.questionnaire import QuestionnaireRound, OptionType, Question
from ui.workers.questionnaire_worker import QuestionnaireWorker
from ui.question_components.mcq_radio import MCQRADIO
from ui.question_components.mcq_checkbox import MCQCheckbox as MCQCHECKBOX
from ui.question_components.scale_slider import ScaleSlider as SCALESLIDER
from ui.question_components.date_duration import DATEDURATION
from ui.question_components.open_text import OPENTEXT

class QuestionnaireUI(QWidget):
    """
    Refactored Questionnaire UI.
    Dynamically renders placeholder widgets from LLM output.
    Following Blueprint Section 9.2.
    """

    session_complete = Signal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.current_round_data = None
        self.widgets = {}  # question_id -> widget
        self.answers = {}
        
        self.layout = QVBoxLayout(self)
        
        # Scroll area for dynamic questions
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        
        self.layout.addWidget(self.scroll_area)
        
        # Submit button
        self.btn_submit = QPushButton("Submit Round")
        self.btn_submit.setMinimumHeight(50)
        self.btn_submit.clicked.connect(self.submit_round)
        self.btn_submit.setEnabled(False)
        self.layout.addWidget(self.btn_submit)

        # Other Issue button
        self.btn_other_issue = QPushButton("Report Other Issue")
        self.btn_other_issue.setStyleSheet("background-color: #f59e0b; color: white;")
        self.btn_other_issue.clicked.connect(self._add_other_issue)
        self.layout.addWidget(self.btn_other_issue)

        # Add Enter shortcut to submit round
        from PySide6.QtGui import QShortcut, QKeySequence
        self.submit_shortcut = QShortcut(QKeySequence("Return"), self)
        self.submit_shortcut.activated.connect(self._on_enter_pressed)
        self.submit_shortcut_enter = QShortcut(QKeySequence("Enter"), self)
        self.submit_shortcut_enter.activated.connect(self._on_enter_pressed)

    def _add_other_issue(self):
        """Adds a generic text box for any unlisted symptoms or issues."""
        from models.questionnaire import Question, OptionType
        q = Question(
            question_id=f"other_issue_{len(self.widgets)}",
            round=1,
            text="Please describe the other issue/symptom in detail:",
            type=OptionType.TEXT,
            is_mandatory=False
        )
        widget = self._create_widget(q)
        if widget:
            self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, widget)
            self.widgets[q.question_id] = widget

    def _on_enter_pressed(self):
        """Trigger submit if all fields are answered, else advance focus."""
        if not self.btn_submit.isEnabled():
            return
            
        # Do not override Enter if focused widget is a multi-line text edit
        focus_widget = self.focusWidget()
        if focus_widget and isinstance(focus_widget, QTextEdit):
            return

            
        all_answered = True
        for q_id, widget in self.widgets.items():
            ans = widget.get_answer()
            if ans == "" or ans == []:
                all_answered = False
                break
                
        if all_answered:
            self.btn_submit.click()
        else:
            # Advance focus to the next input field
            self.focusNextChild()
    def start_session(self, visit_type: str, patient_ctx: dict, specialty: str):
        """Starts the first round of the questionnaire."""
        self.patient_ctx = patient_ctx
        self.visit_type = visit_type
        self.specialty = specialty
        self.current_round = 1
        self.load_round(1)

    def load_round(self, round_number: int, focus: dict = None):
        """Spawns a worker to generate the next round."""
        self.btn_submit.setEnabled(False)
        self._gen_round_number = round_number
        self._gen_focus = focus
        self._gen_elapsed = 0
        kind = "Follow-up round" if round_number > 4 else "Round"
        self.btn_submit.setText(f"Generating {kind} {round_number}…  (0s — the local AI can take a few minutes)")

        if not hasattr(self, "_gen_timer"):
            from PySide6.QtCore import QTimer
            self._gen_timer = QTimer(self)
            self._gen_timer.setInterval(1000)
            self._gen_timer.timeout.connect(self._tick_generating)
        self._gen_timer.start()

        self.worker = QuestionnaireWorker(
            self.controller,
            round_number,
            getattr(self, "visit_type", "General/Routine Checkup"),
            getattr(self, "patient_ctx", {}),
            getattr(self, "specialty", "General Medicine"),
            focus=focus,
        )
        self.worker.round_generated.connect(self.on_round_generated)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    def _tick_generating(self):
        self._gen_elapsed += 1
        kind = "Follow-up round" if self._gen_round_number > 4 else "Round"
        self.btn_submit.setText(
            f"Generating {kind} {self._gen_round_number}…  ({self._gen_elapsed}s — the local AI can take a few minutes)"
        )

    @Slot(QuestionnaireRound)
    def on_round_generated(self, round_data: QuestionnaireRound):
        if hasattr(self, "_gen_timer"):
            self._gen_timer.stop()
        self.current_round_data = round_data
        self.render_round(round_data)
        self.btn_submit.setText(f"Submit Round {round_data.round_number}")
        self.btn_submit.setEnabled(True)

    def render_round(self, round_data: QuestionnaireRound):
        """Clears the layout and renders new widgets."""
        # Clear layout
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        self.widgets = {}
        
        for question in round_data.questions:
            widget = self._create_widget(question)
            if widget:
                self.scroll_layout.addWidget(widget)
                self.widgets[question.question_id] = widget
        
        self.scroll_layout.addStretch()

    def _create_widget(self, question: Question):
        """Factory for question widgets."""
        if question.type == OptionType.RADIO:
            return MCQRADIO(question)
        elif question.type == OptionType.CHECKBOX:
            return MCQCHECKBOX(question)
        elif question.type == OptionType.SCALE:
            return SCALESLIDER(question)
        elif question.type == OptionType.DATE or question.type == OptionType.DURATION:
            return DATEDURATION(question)
        elif question.type == OptionType.TEXT:
            return OPENTEXT(question)
        else:
            # BODY_MAP or any future/unknown type -> free-text fallback so it stays answerable
            logger.warning(f"No dedicated widget for {question.type}; using text fallback")
            return OPENTEXT(question)

    def submit_round(self):
        """Collects answers and submits to engine."""
        round_answers = {}
        missing = False
        
        mandatory = {q.question_id: q.is_mandatory for q in self.current_round_data.questions}
        for q_id, widget in self.widgets.items():
            ans = widget.get_answer()
            if (ans == "" or ans == [] or ans is None) and mandatory.get(q_id, True):
                missing = True
            round_answers[q_id] = ans

        if missing:
            QMessageBox.warning(self, "Incomplete", "Please answer all mandatory questions before submitting.")
            return

        # Submit to engine (pass the round's questions so red-flag / scoring resolution works)
        result = self.controller.questionnaire_engine.submit_round_answers(
            self.current_round_data.round_number,
            round_answers,
            scoring_tool_id=self.current_round_data.scoring_tool_id,
            questions=self.current_round_data.questions,
        )
        
        if result.get("emergency"):
            flags = "\n  • ".join(result["flags"])
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Critical)
            box.setWindowTitle("RED FLAG DETECTED")
            box.setText(f"Emergency indicators found:\n\n  • {flags}\n\n"
                        "Escalate to a clinician now, or continue the intake?")
            escalate = box.addButton("Escalate now (skip to brief)", QMessageBox.AcceptRole)
            cont = box.addButton("Continue intake", QMessageBox.RejectRole)
            box.exec()
            if box.clickedButton() is escalate:
                self.btn_submit.setText("Escalating — generating brief…")
                self.btn_submit.setEnabled(False)
                self.session_complete.emit()
                return
            # else fall through and continue

        # Decide the next step: another mandatory round, an adaptive follow-up
        # round, or done. The sufficiency check is an LLM call -> off-thread.
        self.btn_submit.setEnabled(False)
        rn = self.current_round_data.round_number
        if rn < 4:
            self.load_round(rn + 1)
            return

        self.btn_submit.setText("Reviewing answers — deciding if more questions are needed…")
        from ui.workers.questionnaire_worker import NextStepWorker
        self._step_worker = NextStepWorker(
            self.controller, rn,
            getattr(self, "visit_type", "General/Routine Checkup"),
            getattr(self, "patient_ctx", {}),
            getattr(self, "specialty", "General Medicine"),
        )
        self._step_worker.advance.connect(self._on_advance_round)
        self._step_worker.complete.connect(self._on_intake_sufficient)
        self._step_worker.error_occurred.connect(lambda _m: self._on_intake_sufficient({}))
        self._step_worker.start()

    def _on_advance_round(self, round_number: int, focus: object):
        self.load_round(round_number, focus=focus if isinstance(focus, dict) else None)

    def _on_intake_sufficient(self, assessment: object):
        self.btn_submit.setText("Intake Complete - Processing Vitals")
        self.btn_submit.setEnabled(False)
        self.session_complete.emit()

    def on_error(self, error_msg: str):
        if hasattr(self, "_gen_timer"):
            self._gen_timer.stop()
        QMessageBox.critical(self, "Generation Error", f"Failed to generate round: {error_msg}")
        self.btn_submit.setText("Retry Generation")
        self.btn_submit.setEnabled(True)
        try:
            self.btn_submit.clicked.disconnect()
        except Exception:
            pass
        self.btn_submit.clicked.connect(self._retry_generation)

    def _retry_generation(self):
        self.btn_submit.clicked.disconnect()
        self.btn_submit.clicked.connect(self.submit_round)
        self.load_round(getattr(self, "_gen_round_number", 1))
