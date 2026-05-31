from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton, 
                                 QTableWidget, QTableWidgetItem, QMessageBox, QHBoxLayout, QLabel)
from PySide6.QtCore import Qt

class SQLExplorer(QWidget):
    """Read-only SQL interface for physicians to query patient data directly (Section 10.3)."""
    ALLOWED_STATEMENTS = ("SELECT",)   # Only SELECT allowed — no INSERT/UPDATE/DELETE

    def __init__(self, db_session_factory, parent=None):
        super().__init__(parent)
        self.db_session_factory = db_session_factory
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        header = QLabel("SQL Explorer (Read-Only)")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("Enter SELECT query here...")
        self.query_input.setMaximumHeight(100)
        layout.addWidget(self.query_input)

        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("Execute Query")
        self.run_btn.clicked.connect(self.on_execute)
        btn_layout.addWidget(self.run_btn)
        
        self.quick_queries_btn = QPushButton("Quick Queries")
        self.quick_queries_btn.clicked.connect(self.show_quick_queries)
        btn_layout.addWidget(self.quick_queries_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.results_table = QTableWidget()
        layout.addWidget(self.results_table)

    def on_execute(self):
        sql = self.query_input.toPlainText()
        self.execute_query(sql)

    def show_quick_queries(self):
        # Provide example quick query as specified
        self.query_input.setText("SELECT * FROM patients LIMIT 10;")
        
    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        
    def populate_table(self, cols, rows):
        self.results_table.clear()
        self.results_table.setColumnCount(len(cols))
        self.results_table.setHorizontalHeaderLabels(cols)
        self.results_table.setRowCount(len(rows))
        
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) # Read-only
                self.results_table.setItem(row_idx, col_idx, item)

    def execute_query(self, sql: str):
        sql_stripped = sql.strip().upper()
        if not any(sql_stripped.startswith(stmt) for stmt in self.ALLOWED_STATEMENTS):
            self.show_error("Only SELECT statements are permitted.")
            return
            
        from sqlalchemy import text
        try:
            with self.db_session_factory() as session:
                result = session.execute(text(sql))
                rows = result.fetchall()
                cols = list(result.keys())
                self.populate_table(cols, rows)
                # self.log_audit("SQL_QUERY", details={"query": sql})
        except Exception as e:
            self.show_error(f"Query error: {e}")
