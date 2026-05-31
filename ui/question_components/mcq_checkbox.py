from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QCheckBox
from PySide6.QtCore import Qt, Signal
from models.questionnaire import Question

class MCQCHECKBOX(QFrame):
    """
    Blueprint-compliant Checkbox MCQ Widget.
    Section 9.1 & 9.2
    """
    answer_changed = Signal(list)

    def __init__(self, question: Question, parent=None):
        super().__init__(parent)
        self.setProperty("role", "option-container")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        # Question text
        self.lbl_question = QLabel(question.text)
        self.lbl_question.setWordWrap(True)
        self.lbl_question.setProperty("role", "question")
        self.layout.addWidget(self.lbl_question)

        self.checkboxes = {}

        if question.options:
            for opt in question.options:
                card = QFrame()
                card.setProperty("role", "option-card")
                card_layout = QVBoxLayout(card)
                
                cb = QCheckBox(opt.label)
                cb.setMinimumHeight(44)
                card_layout.addWidget(cb)
                
                self.checkboxes[opt.id] = cb
                self.layout.addWidget(card)
                
                cb.toggled.connect(self._on_toggled)

    def _on_toggled(self):
        selected_ids = [o_id for o_id, cb in self.checkboxes.items() if cb.isChecked()]
        self.answer_changed.emit(selected_ids)

    def get_answer(self) -> list:
        return [o_id for o_id, cb in self.checkboxes.items() if cb.isChecked()]
