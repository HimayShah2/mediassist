from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                               QTableWidget, QTableWidgetItem, QPushButton, QHeaderView)
from PySide6.QtCore import Qt

class PhysicianDashboardView(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self.header_layout = QHBoxLayout()
        self.title = QLabel("Physician Dashboard")
        self.title.setStyleSheet("font-size: 28px; font-weight: bold; color: #0F2D52;")
        self.header_layout.addWidget(self.title)
        
        self.btn_sql = QPushButton("SQL Explorer")
        self.btn_sql.setStyleSheet("background-color: #00A896; color: white; padding: 8px 16px; border-radius: 4px;")
        self.header_layout.addWidget(self.btn_sql)
        
        self.layout.addLayout(self.header_layout)

        # Review Queue Table
        self.table_label = QLabel("Awaiting Physician Review")
        self.table_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        self.layout.addWidget(self.table_label)

        self.table = QTableWidget(3, 5)
        self.table.setHorizontalHeaderLabels(["Case Number", "Top Differential", "Confidence", "Emergency", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Mock data
        self._add_table_row(0, "MC-2025-0042", "Tension Headache", "High (0.92)", "No")
        self._add_table_row(1, "MC-2025-0038", "Malaria, Uncomplicated", "Moderate (0.81)", "No")
        self._add_table_row(2, "MC-2025-0045", "Suspected Meningitis", "High (0.95)", "YES")
        
        self.layout.addWidget(self.table)
        
        self.raw_data_label = QLabel("Note: Select 'Review' to access the full Physician Brief, Raw LLM Data, and RAG Sources.")
        self.raw_data_label.setStyleSheet("color: #7f8fa6; font-style: italic;")
        self.layout.addWidget(self.raw_data_label)

    def _add_table_row(self, row, case, diff, conf, emergency):
        self.table.setItem(row, 0, QTableWidgetItem(case))
        self.table.setItem(row, 1, QTableWidgetItem(diff))
        self.table.setItem(row, 2, QTableWidgetItem(conf))
        
        item_emerg = QTableWidgetItem(emergency)
        if emergency == "YES":
            item_emerg.setForeground(Qt.red)
        self.table.setItem(row, 3, item_emerg)
        
        btn_review = QPushButton("Review Report")
        self.table.setCellWidget(row, 4, btn_review)