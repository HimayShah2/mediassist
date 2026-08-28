from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt

class OPENTEXT(QWidget):
    def __init__(self, question):
        super().__init__()
        self.question = question
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(getattr(self.question, "text", None) or getattr(self.question, "question_text", ""))
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 5px;")
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Type your answer here...")
        self.text_input.setStyleSheet("padding: 10px; font-size: 14px; border: 1px solid #cbd5e1; border-radius: 4px;")
        self.text_input.setMinimumHeight(100)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.text_input)
        
    def get_answer(self):
        text = self.text_input.toPlainText().strip()
        return text if text else ""
