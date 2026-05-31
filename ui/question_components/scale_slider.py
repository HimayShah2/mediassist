from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from models.questionnaire import Question

class SCALESLIDER(QFrame):
    """
    Blueprint-compliant Scale/Slider MCQ Widget.
    Section 9.1 & 9.2
    """
    answer_changed = Signal(int)

    def __init__(self, question: Question, parent=None):
        super().__init__(parent)
        self.setProperty("role", "option-container")
        self.layout = QVBoxLayout(self)

        self.lbl_question = QLabel(question.text)
        self.lbl_question.setProperty("role", "question")
        self.layout.addWidget(self.lbl_question)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(10)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setMinimumHeight(44)

        self.val_label = QLabel("0")
        self.val_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("None (0)"))
        h_layout.addWidget(self.slider)
        h_layout.addWidget(QLabel("Severe (10)"))
        h_layout.addWidget(self.val_label)
        
        self.layout.addLayout(h_layout)
        
        self.slider.valueChanged.connect(self._on_changed)

    def _on_changed(self, value):
        self.val_label.setText(str(value))
        self.answer_changed.emit(value)

    def get_answer(self) -> int:
        return self.slider.value()
