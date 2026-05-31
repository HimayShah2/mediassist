import json
import os
import re
from loguru import logger
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                               QScrollArea, QToolTip, QFrame, QMessageBox)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QCursor

from models.questionnaire import QuestionnaireRound, OptionType, Question
from ui.workers.questionnaire_worker import QuestionnaireWorker
from ui.question_components.mcq_radio import MCQRADIO
from ui.question_components.mcq_checkbox import MCQCHECKBOX
from ui.question_components.scale_slider import SCALESLIDER
from ui.question_components.date_duration import DATEDURATION

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

    def start_session(self, visit_type: str, patient_ctx: dict, specialty: str):
        """Starts the first round of the questionnaire."""
        self.patient_ctx = patient_ctx
        self.visit_type = visit_type
        self.specialty = specialty
        self.current_round = 1
        self.load_round(1)

    def load_round(self, round_number: int):
        """Spawns a worker to generate the next round."""
        self.btn_submit.setEnabled(False)
        self.btn_submit.setText(f"Generating Round {round_number}...")
        
        self.worker = QuestionnaireWorker(
            self.controller, 
            round_number, 
            self.visit_type, 
            self.patient_ctx, 
            self.specialty
        )
        self.worker.round_generated.connect(self.on_round_generated)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.start()

    @Slot(QuestionnaireRound)
    def on_round_generated(self, round_data: QuestionnaireRound):
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
        else:
            logger.warning(f"Unsupported question type: {question.type}")
            return None

    def submit_round(self):
        """Collects answers and submits to engine."""
        round_answers = {}
        for q_id, widget in self.widgets.items():
            ans = widget.get_answer()
            round_answers[q_id] = ans
            
        # Submit to engine
        result = self.controller.questionnaire_engine.submit_round_answers(
            self.current_round_data.round_number, 
            round_answers,
            scoring_tool_id=self.current_round_data.scoring_tool_id
        )
        
        if result.get("emergency"):
            QMessageBox.critical(self, "EMERGENCY", f"Red flags detected: {', '.join(result['flags'])}")
            # Handle emergency transition
            return

        # Advance to next round or vitals
        if self.current_round_data.round_number < 4:
            self.load_round(self.current_round_data.round_number + 1)
        else:
            self.btn_submit.setText("Intake Complete - Processing Vitals")
            self.btn_submit.setEnabled(False)
            # Signal to main window to switch to Vitals form
            # self.session_complete.emit()

    def on_error(self, error_msg: str):
        QMessageBox.critical(self, "Generation Error", f"Failed to generate round: {error_msg}")
        self.btn_submit.setText("Retry Generation")
        self.btn_submit.setEnabled(True)
