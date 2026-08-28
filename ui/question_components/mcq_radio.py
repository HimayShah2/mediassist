from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QRadioButton, QButtonGroup
from PySide6.QtCore import Qt, Signal
from models.questionnaire import Question

class MCQRADIO(QFrame):
    """
    Blueprint-compliant Radio MCQ Widget.
    Section 9.1 & 9.2
    """
    answer_changed = Signal(str)

    def __init__(self, question: Question, parent=None):
        super().__init__(parent)
        self.question = question
        self.setProperty("role", "option-container")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        # Question text
        self.lbl_question = QLabel(question.text)
        self.lbl_question.setWordWrap(True)
        self.lbl_question.setProperty("role", "question")
        self.layout.addWidget(self.lbl_question)

        self.btn_group = QButtonGroup(self)
        self.options = []

        if question.options:
            for opt in question.options:
                card = QFrame()
                card.setProperty("role", "option-card")
                card_layout = QVBoxLayout(card)
                
                rb = QRadioButton(opt.label)
                rb.setMinimumHeight(44)  # Fat-finger safe
                card_layout.addWidget(rb)
                
                self.btn_group.addButton(rb)
                self.layout.addWidget(card)
                
                # Signal relay
                rb.toggled.connect(lambda checked, o_id=opt.id: self._on_toggled(checked, o_id))

    def _on_toggled(self, checked, option_id):
        if checked:
            self.answer_changed.emit(option_id)

    def get_answer(self) -> str:
        selected = self.btn_group.checkedButton()
        if selected:
            # Re-map the button text back to option ID
            for opt in self.question.options:
                if opt.label == selected.text():
                    return opt.id
        return ""
