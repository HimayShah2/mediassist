from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class ScaleSlider(QWidget):
    def __init__(self, question_text: str, min_val: int = 1, max_val: int = 10, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(question_text))
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(min_val)
        self.slider.setMaximum(max_val)
        self.slider.setValue((min_val + max_val) // 2)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        
        self.val_label = QLabel(str(self.slider.value()))
        self.slider.valueChanged.connect(lambda v: self.val_label.setText(str(v)))
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel(str(min_val)))
        h_layout.addWidget(self.slider)
        h_layout.addWidget(QLabel(str(max_val)))
        h_layout.addWidget(self.val_label)
        
        layout.addLayout(h_layout)
        
    def get_value(self) -> int:
        return self.slider.value()
