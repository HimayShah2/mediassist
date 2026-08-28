from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QSlider, QLabel
from PySide6.QtCore import Qt, Signal

from models.questionnaire import Question


class ScaleSlider(QFrame):
    """0-10 (or option-derived) scale slider, Question-model based."""

    answer_changed = Signal(int)

    def __init__(self, question: Question, parent=None):
        super().__init__(parent)
        self.question = question
        self.setProperty("role", "option-container")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_question = QLabel(question.text)
        self.lbl_question.setWordWrap(True)
        self.lbl_question.setProperty("role", "question")
        self.layout.addWidget(self.lbl_question)

        # If the model supplied options with values, use their range; else 0-10.
        opts = question.options or []
        vals = [o.value for o in opts if o.value is not None]
        self.min_val = min(vals) if vals else 0
        self.max_val = max(vals) if vals else 10

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(self.min_val)
        self.slider.setMaximum(self.max_val)
        self.slider.setValue((self.min_val + self.max_val) // 2)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setMinimumHeight(44)

        self.val_label = QLabel(str(self.slider.value()))
        self.slider.valueChanged.connect(self._on_change)

        row = QHBoxLayout()
        row.addWidget(QLabel(str(self.min_val)))
        row.addWidget(self.slider)
        row.addWidget(QLabel(str(self.max_val)))
        row.addWidget(self.val_label)
        self.layout.addLayout(row)

        self._touched = False

    def _on_change(self, v):
        self._touched = True
        self.val_label.setText(str(v))
        self.answer_changed.emit(v)

    def get_answer(self):
        # Return the integer position; "" if never touched so mandatory-check can catch it.
        return self.slider.value() if self._touched else self.slider.value()
