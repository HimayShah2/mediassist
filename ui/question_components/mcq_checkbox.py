from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QCheckBox
from PySide6.QtCore import Signal

from models.questionnaire import Question


class MCQCheckbox(QFrame):
    """Multi-select MCQ widget (Question-model based, consistent with MCQRADIO)."""

    answer_changed = Signal(list)

    def __init__(self, question: Question, parent=None):
        super().__init__(parent)
        self.question = question
        self.setProperty("role", "option-container")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        self.lbl_question = QLabel(question.text)
        self.lbl_question.setWordWrap(True)
        self.lbl_question.setProperty("role", "question")
        self.layout.addWidget(self.lbl_question)

        self.checkboxes = {}  # option_id -> QCheckBox
        for opt in (question.options or []):
            cb = QCheckBox(opt.label)
            cb.setMinimumHeight(44)  # fat-finger safe
            cb.stateChanged.connect(lambda _s: self.answer_changed.emit(self.get_answer()))
            self.checkboxes[opt.id] = cb
            self.layout.addWidget(cb)

    def get_answer(self) -> list:
        return [oid for oid, cb in self.checkboxes.items() if cb.isChecked()]
