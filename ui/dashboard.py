from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                               QFrame, QGridLayout, QPushButton, QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Qt

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self.header_layout = QHBoxLayout()
        self.title = QLabel("Nurse Dashboard")
        self.title.setStyleSheet("font-size: 28px; font-weight: bold; color: #0F2D52;")
        self.header_layout.addWidget(self.title)
        self.header_layout.addStretch()
        self.layout.addLayout(self.header_layout)

        # Stats Cards
        self.stats_layout = QHBoxLayout()
        
        self.card_active = self._create_stat_card("Active Sessions", "3", "#00A896")
        self.card_completed = self._create_stat_card("Completed Today", "12", "#0F2D52")
        self.card_alerts = self._create_stat_card("Emergency Alerts", "0", "#D62839")
        
        self.stats_layout.addWidget(self.card_active)
        self.stats_layout.addWidget(self.card_completed)
        self.stats_layout.addWidget(self.card_alerts)
        self.layout.addLayout(self.stats_layout)

        # Recent Patients Table
        self.table_label = QLabel("Recent Patient Intakes")
        self.table_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        self.layout.addWidget(self.table_label)

        self.table = QTableWidget(5, 4)
        self.table.setHorizontalHeaderLabels(["Case Number", "Name", "Visit Type", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # Mock data
        self._add_table_row(0, "MC-2025-0042", "John Doe", "Specific Complaint", "Awaiting Doctor")
        self._add_table_row(1, "MC-2025-0043", "Jane Smith", "General Checkup", "In Progress")
        self._add_table_row(2, "MC-2025-0044", "Baby Alan", "Pediatric Well-Visit", "Completed")
        
        self.layout.addWidget(self.table)

    def _create_stat_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"border-top: 4px solid {color}; border-radius: 8px; padding: 15px;")
        card_layout = QVBoxLayout(card)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 14px; color: #7f8fa6;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_value)
        return card

    def _add_table_row(self, row, case, name, vtype, status):
        self.table.setItem(row, 0, QTableWidgetItem(case))
        self.table.setItem(row, 1, QTableWidgetItem(name))
        self.table.setItem(row, 2, QTableWidgetItem(vtype))
        self.table.setItem(row, 3, QTableWidgetItem(status))