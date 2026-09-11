import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                               QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt, Signal, QThread
from loguru import logger
from ui.components.modern_button import ModernButton


class _CaseScanWorker(QThread):
    """Reads every case's physician_brief.json off the UI thread. Only re-parses
    a file whose mtime changed since the last scan (cheap incremental refresh)."""
    done = Signal(list)  # list of row dicts, newest-first

    def __init__(self, cases_dir: str, cache: dict):
        super().__init__()
        self.cases_dir = cases_dir
        self.cache = cache  # cf -> (mtime, row_dict); mutated in place, shared with the view

    def run(self):
        import json
        rows = []
        if not os.path.isdir(self.cases_dir):
            self.done.emit(rows)
            return

        try:
            entries = os.listdir(self.cases_dir)
        except OSError as e:
            logger.warning(f"Could not list cases dir: {e}")
            self.done.emit(rows)
            return

        seen = set()
        for cf in entries:
            pb_path = os.path.join(self.cases_dir, cf, "physician_brief.json")
            try:
                mtime = os.path.getmtime(pb_path)
            except OSError:
                continue
            seen.add(cf)

            cached = self.cache.get(cf)
            if cached and cached[0] == mtime:
                rows.append(cached[1])
                continue

            try:
                with open(pb_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                logger.warning(f"Skipping unreadable brief {pb_path}: {e}")
                continue

            row = self._to_row(cf, data)
            self.cache[cf] = (mtime, row)
            rows.append(row)

        # drop cache entries for cases that no longer exist
        for stale in set(self.cache) - seen:
            del self.cache[stale]

        # Emergency cases first, then newest date first.
        rows.sort(key=lambda r: (r["emergency"], r["date"]), reverse=True)
        self.done.emit(rows)

    @staticmethod
    def _to_row(cf: str, data: dict) -> dict:
        differentials = data.get("differentials") or data.get("differential_diagnoses", [])
        top_diff = "Unknown"
        if differentials:
            first = differentials[0]
            top_diff = first.get("condition_name", "Unknown") if isinstance(first, dict) else str(first)

        has_red = False
        for flag in data.get("flags", []):
            if isinstance(flag, dict):
                val = f"{flag.get('level', '')} {flag.get('reason', '')}".upper()
            else:
                val = str(flag).upper()
            if "RED" in val or "EMERGENCY" in val:
                has_red = True
                break

        return {
            "folder": cf,
            "case_number": data.get("case_number", cf),
            "top_diff": top_diff,
            "emergency": has_red,
            "date": data.get("date", "Today"),
        }


class PhysicianDashboardView(QWidget):
    review_requested = Signal(str) # case_number

    def __init__(self):
        super().__init__()
        self._cache: dict = {}
        self._worker = None

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
        """Scan data/cases/ off the UI thread; cheap on repeat calls since only
        changed briefs are re-parsed. Safe to call while a scan is in flight —
        a new scan is not started until the previous one finishes."""
        if self._worker is not None and self._worker.isRunning():
            return
        cases_dir = os.path.join(os.getcwd(), "data", "cases")
        self.btn_refresh.setEnabled(False)
        self._worker = _CaseScanWorker(cases_dir, self._cache)
        self._worker.done.connect(self._on_scan_done)
        self._worker.start()

    def _on_scan_done(self, rows: list):
        self.btn_refresh.setEnabled(True)
        self.table.setRowCount(len(rows))
        for row, r in enumerate(rows):
            self.table.setItem(row, 0, QTableWidgetItem(r["case_number"]))
            self.table.setItem(row, 1, QTableWidgetItem(r["top_diff"]))

            item_emerg = QTableWidgetItem("YES" if r["emergency"] else "No")
            if r["emergency"]:
                item_emerg.setForeground(Qt.red)
            self.table.setItem(row, 2, item_emerg)

            self.table.setItem(row, 3, QTableWidgetItem(r["date"]))

            btn_review = ModernButton("Review Report")
            btn_review.clicked.connect(lambda checked, c=r["folder"]: self.review_requested.emit(c))
            self.table.setCellWidget(row, 4, btn_review)
