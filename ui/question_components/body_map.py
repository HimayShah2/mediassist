from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox

class BodyMap(QWidget):
    def __init__(self, question_text: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(question_text))
        
        # Placeholder for an interactive SVG body map.
        # For MVP, we use a ComboBox covering major body regions.
        self.region_combo = QComboBox()
        self.region_combo.addItems([
            "Head", "Neck", "Chest", "Abdomen", 
            "Upper Back", "Lower Back", "Left Arm", 
            "Right Arm", "Left Leg", "Right Leg", "Pelvis"
        ])
        
        layout.addWidget(QLabel("Select Region (Visual Body Map Coming Soon):"))
        layout.addWidget(self.region_combo)
        
    def get_selected_region(self) -> str:
        return self.region_combo.currentText()
