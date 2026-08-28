"""
ReportViewer — renders a generated PhysicianBrief (dict) for physician review.
"""
import json

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QTextEdit, QPushButton, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal


class ReportViewer(QWidget):
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        self.title = QLabel("Physician Brief")
        self.title.setStyleSheet("font-size: 26px; font-weight: bold; color: #0F2D52;")
        header.addWidget(self.title)
        header.addStretch()
        self.btn_back = QPushButton("Back to Dashboard")
        self.btn_back.clicked.connect(self.back_requested.emit)
        header.addWidget(self.btn_back)
        self.layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        scroll.setWidget(self.body)
        self.layout.addWidget(scroll)

    def _section(self, heading: str) -> QVBoxLayout:
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        v = QVBoxLayout(frame)
        lbl = QLabel(heading)
        lbl.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 6px;")
        v.addWidget(lbl)
        self.body_layout.addWidget(frame)
        return v

    def load_brief(self, brief: dict):
        # Clear
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.title.setText(f"Physician Brief — {brief.get('case_number', 'Unknown case')}")

        if brief.get("is_emergency"):
            banner = QLabel("⚠  EMERGENCY — RED FLAGS PRESENT")
            banner.setStyleSheet("background:#b91c1c;color:white;font-weight:bold;padding:8px;border-radius:4px;")
            self.body_layout.addWidget(banner)

        conf = brief.get("confidence_score", 0.0)
        v = self._section(f"Overall confidence: {conf:.0%}")

        flags = brief.get("flags", [])
        if flags:
            v = self._section("Clinical Flags")
            for f in flags:
                if isinstance(f, dict):
                    v.addWidget(QLabel(f"• [{f.get('level','?')}] {f.get('reason','')} ({f.get('category','')})"))
                else:
                    v.addWidget(QLabel(f"• {f}"))

        diffs = brief.get("differentials", [])
        if diffs:
            v = self._section("Differential Diagnoses")
            for d in diffs:
                if isinstance(d, dict):
                    line = f"• {d.get('condition_name','?')}"
                    codes = " / ".join(c for c in [d.get("icd_10_code"), d.get("icd_11_code")] if c)
                    if codes:
                        line += f"  [{codes}]"
                    if d.get("confidence_score") is not None:
                        line += f"  — {float(d['confidence_score']):.0%}"
                    v.addWidget(QLabel(line))
                    if d.get("reasoning_summary"):
                        r = QLabel(d["reasoning_summary"])
                        r.setWordWrap(True)
                        r.setStyleSheet("color:#475569;margin-left:16px;")
                        v.addWidget(r)
                else:
                    v.addWidget(QLabel(f"• {d}"))

        for key, heading in [("examination_plan", "Examination Plan"),
                             ("recommended_investigations", "Recommended Investigations"),
                             ("rag_sources", "Sources")]:
            items = brief.get(key, [])
            if items:
                v = self._section(heading)
                for it in items:
                    w = QLabel(f"• {it}")
                    w.setWordWrap(True)
                    v.addWidget(w)

        raw = QTextEdit()
        raw.setReadOnly(True)
        raw.setPlainText(json.dumps(brief, indent=2, default=str))
        raw.setMaximumHeight(240)
        v = self._section("Raw brief (JSON)")
        v.addWidget(raw)

        self.body_layout.addStretch()
