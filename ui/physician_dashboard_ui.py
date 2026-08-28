from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                               QTableWidget, QTableWidgetItem, QPushButton, QHeaderView)
from PySide6.QtCore import Qt, Signal
from ui.components.modern_button import ModernButton

class PhysicianDashboardView(QWidget):
    review_requested = Signal(str) # case_number

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self.header_layout = QHBoxLayout()
        self.title = QLabel("Physician Dashboard")
        self.title.setStyleSheet("font-size: 28px; font-weight: bold; color: #0F2D52;")
        self.header_layout.addWidget(self.title)
        
        self.btn_refresh = ModernButton("Refresh Cases")
        self.btn_refresh.setStyleSheet("background-color: #00A896; color: white; padding: 8px 16px; border-radius: 4px;")
        self.btn_refresh.clicked.connect(self.refresh_data)
        self.header_layout.addWidget(self.btn_refresh)
        
        self.layout.addLayout(self.header_layout)

        # Review Queue Table
        self.table_label = QLabel("Awaiting Physician Review")
        self.table_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        self.layout.addWidget(self.table_label)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Case Number", "Top Differential", "Emergency", "Date", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.layout.addWidget(self.table)
        
        self.raw_data_label = QLabel("Note: Select 'Review' to access the full Physician Brief, Raw LLM Data, and RAG Sources.")
        self.raw_data_label.setStyleSheet("color: #7f8fa6; font-style: italic;")
        self.layout.addWidget(self.raw_data_label)
        
        # Load cases on init
        self.refresh_data()

    def refresh_data(self):
        self.table.setRowCount(0)
        import os, json, glob
        cases_dir = os.path.join(os.getcwd(), "data", "cases")
        if not os.path.exists(cases_dir):
            return
            
        case_folders = [f for f in os.listdir(cases_dir) if os.path.isdir(os.path.join(cases_dir, f))]
        
        row = 0
        for cf in case_folders:
            pb_path = os.path.join(cases_dir, cf, "physician_brief.json")
            if os.path.exists(pb_path):
                with open(pb_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        continue
                    
                    self.table.insertRow(row)
                    self.table.setItem(row, 0, QTableWidgetItem(data.get("case_number", cf)))
                    
                    differentials = data.get("differentials") or data.get("differential_diagnoses", [])
                    top_diff = "Unknown"
                    if differentials:
                        first = differentials[0]
                        top_diff = first.get("condition_name", "Unknown") if isinstance(first, dict) else str(first)
                    self.table.setItem(row, 1, QTableWidgetItem(top_diff))
                    
                    # Emergency
                    flags = data.get("flags", [])
                    has_red = False
                    for flag in flags:
                        if isinstance(flag, dict):
                            val = str(flag.get('level', '')).upper() + " " + str(flag.get('reason', '')).upper()
                            if "RED" in val or "EMERGENCY" in val:
                                has_red = True
                                break
                        elif isinstance(flag, str):
                            if "RED" in flag.upper() or "EMERGENCY" in flag.upper():
                                has_red = True
                                break
                                
                    item_emerg = QTableWidgetItem("YES" if has_red else "No")
                    if has_red:
                        item_emerg.setForeground(Qt.red)
                    self.table.setItem(row, 2, item_emerg)
                    
                    self.table.setItem(row, 3, QTableWidgetItem(data.get("date", "Today")))
                    
                    btn_review = ModernButton("Review Report")
                    btn_review.clicked.connect(lambda checked, c=cf: self.review_requested.emit(c))
                    self.table.setCellWidget(row, 4, btn_review)
                    row += 1