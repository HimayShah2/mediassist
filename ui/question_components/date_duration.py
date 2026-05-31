from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QDateEdit, QComboBox, QHBoxLayout
from PySide6.QtCore import Qt, Signal, QDate
from models.questionnaire import Question

class DATEDURATION(QFrame):
    """
    Blueprint-compliant Date + Duration Picker Widget.
    Section 13 (Folder structure)
    """
    answer_changed = Signal(str)

    def __init__(self, question: Question, parent=None):
        super().__init__(parent)
        self.setProperty("role", "option-container")
        self.layout = QVBoxLayout(self)

        self.lbl_question = QLabel(question.text)
        self.lbl_question.setProperty("role", "question")
        self.layout.addWidget(self.lbl_question)

        self.input_layout = QHBoxLayout()
        
        if "date" in question.question_id.lower() or question.type == "date":
            self.date_edit = QDateEdit()
            self.date_edit.setCalendarPopup(True)
            self.date_edit.setDate(QDate.currentDate())
            self.date_edit.setMinimumHeight(44)
            self.input_layout.addWidget(self.date_edit)
            self.date_edit.dateChanged.connect(lambda d: self.answer_changed.emit(d.toString(Qt.ISODate)))
        else:
            # Duration selector
            self.val_combo = QComboBox()
            self.val_combo.addItems([str(i) for i in range(1, 31)])
            self.val_combo.setMinimumHeight(44)
            
            self.unit_combo = QComboBox()
            self.unit_combo.addItems(["Hours", "Days", "Weeks", "Months", "Years"])
            self.unit_combo.setMinimumHeight(44)
            
            self.input_layout.addWidget(self.val_combo)
            self.input_layout.addWidget(self.unit_combo)
            
            self.val_combo.currentTextChanged.connect(self._emit_duration)
            self.unit_combo.currentTextChanged.connect(self._emit_duration)

        self.layout.addLayout(self.input_layout)

    def _emit_duration(self):
        duration = f"{self.val_combo.currentText()} {self.unit_combo.currentText()}"
        self.answer_changed.emit(duration)

    def get_answer(self) -> str:
        if hasattr(self, 'date_edit'):
            return self.date_edit.date().toString(Qt.ISODate)
        return f"{self.val_combo.currentText()} {self.unit_combo.currentText()}"
