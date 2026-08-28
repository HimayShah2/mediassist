from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
