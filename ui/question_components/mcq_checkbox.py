from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel

class MCQCheckbox(QWidget):
    def __init__(self, question_text: str, options: list[str], parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(question_text))
        
        self.checkboxes = []
        for opt in options:
            cb = QCheckBox(opt)
            self.checkboxes.append(cb)
            layout.addWidget(cb)
            
    def get_selected(self) -> list[str]:
        return [cb.text() for cb in self.checkboxes if cb.isChecked()]
