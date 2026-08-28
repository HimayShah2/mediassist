from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                               QFrame, QGridLayout, QPushButton, QTableWidget, QTableWidgetItem)
from PySide6.QtCore import Qt
import datetime
from sqlalchemy import desc

from database.connection import get_session
from models.db_models import Patient, Encounter

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
        
        self.card_active, self.lbl_active_val = self._create_stat_card("Total Patients", "0", "#00A896")
        self.card_completed, self.lbl_completed_val = self._create_stat_card("Encounters Today", "0", "#0F2D52")
        self.card_alerts, self.lbl_alerts_val = self._create_stat_card("Emergency Alerts", "0", "#D62839")
        
        self.stats_layout.addWidget(self.card_active)
        self.stats_layout.addWidget(self.card_completed)
        self.stats_layout.addWidget(self.card_alerts)
        self.layout.addLayout(self.stats_layout)

        # Recent Patients Table
        self.table_label = QLabel("Recent Patient Intakes")
        self.table_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        self.layout.addWidget(self.table_label)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Case Number", "Name", "Visit Type", "Status"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.table)
        
        self.refresh_data()

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
        return card, lbl_value

    def refresh_data(self):
        try:
            with get_session() as db:
                total_patients = db.query(Patient).count()
                
                today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
                encounters_today = db.query(Encounter).filter(Encounter.created_at >= today_start).count()
                
                self.lbl_active_val.setText(str(total_patients))
                self.lbl_completed_val.setText(str(encounters_today))
                self.lbl_alerts_val.setText("0")

                recent_encounters = db.query(Encounter).order_by(desc(Encounter.created_at)).limit(10).all()
                self.table.setRowCount(len(recent_encounters))
                
                for row, enc in enumerate(recent_encounters):
                    pat = enc.patient
                    name = f"{pat.first_name} {pat.last_name}" if pat else "Unknown"
                    vtype = enc.encounter_type or "General Checkup"
                    status = "Completed" if enc.ai_summary else "In Progress"
                    
                    self.table.setItem(row, 0, QTableWidgetItem(enc.case_number))
                    self.table.setItem(row, 1, QTableWidgetItem(name))
                    self.table.setItem(row, 2, QTableWidgetItem(vtype))
                    self.table.setItem(row, 3, QTableWidgetItem(status))
        except Exception as e:
            print(f"Dashboard refresh error: {e}")