from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
                               QPushButton, QFileDialog, QComboBox, QListWidget, QMessageBox, QLineEdit)
from PySide6.QtCore import Qt
from loguru import logger

class DocumentManagerUI(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self.title = QLabel("Document Library (RAG)")
        self.title.setStyleSheet("font-size: 28px; font-weight: bold; color: #0F2D52;")
        self.layout.addWidget(self.title)

        self.subtitle = QLabel("Upload medical books, guidelines, and protocols or add web links to the local AI knowledge base.")
        self.layout.addWidget(self.subtitle)

        # File Section
        self.upload_layout = QHBoxLayout()
        self.btn_browse = QPushButton("Select Document (PDF/DOCX)...")
        self.btn_browse.clicked.connect(self._browse_file)
        
        self.selected_file_label = QLabel("No source selected")
        self.selected_file_label.setStyleSheet("color: #7f8fa6; font-style: italic;")
        self.selected_file_path = None
        
        self.upload_layout.addWidget(self.btn_browse)
        self.upload_layout.addWidget(self.selected_file_label)
        self.upload_layout.addStretch()
        self.layout.addLayout(self.upload_layout)

        # URL Section
        self.url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("...or enter a web link (URL) to a medical guideline")
        self.btn_add_url = QPushButton("Add URL")
        self.btn_add_url.clicked.connect(self._on_url_added)
        
        self.url_layout.addWidget(self.url_input)
        self.url_layout.addWidget(self.btn_add_url)
        self.layout.addLayout(self.url_layout)

        # Collection Selection
        self.collection_layout = QHBoxLayout()
        self.collection_label = QLabel("Assign to Specialty Collection:")
        self.collection_combo = QComboBox()
        # All 21 domains as specified in settings + common
        self.collection_combo.addItems([
            "general_medicine", "pediatrics", "obstetrics", "gynecology",
            "cardiology", "dermatology", "endocrinology", "gastroenterology",
            "hematology", "infectious_disease", "nephrology", "neurology",
            "oncology", "ophthalmology", "orthopedics", "ent",
            "psychiatry", "pulmonology", "rheumatology", "urology", "emergency",
            "common_medicine", "cdc_guidelines", "who_guidelines"
        ])
        
        self.collection_layout.addWidget(self.collection_label)
        self.collection_layout.addWidget(self.collection_combo)
        self.collection_layout.addStretch()
        self.layout.addLayout(self.collection_layout)

        # Ingest Button
        self.btn_ingest = QPushButton("Vectorize Selected Source")
        self.btn_ingest.setStyleSheet("background-color: #00A896; color: white; padding: 12px; font-size: 16px; font-weight: bold;")
        self.btn_ingest.clicked.connect(self._ingest_source)
        self.btn_ingest.setEnabled(False)
        self.layout.addWidget(self.btn_ingest)

        # Existing Collections View
        self.list_label = QLabel("Active RAG Collections")
        self.list_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        self.layout.addWidget(self.list_label)

        self.collection_list = QListWidget()
        self.layout.addWidget(self.collection_list)
        
        self._refresh_stats()

    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Medical Document", "", "Documents (*.pdf *.docx *.txt)"
        )
        if file_path:
            self.selected_file_path = file_path
            self.url_input.clear()
            self.selected_file_label.setText(file_path.split("/")[-1])
            self.btn_ingest.setEnabled(True)

    def _on_url_added(self):
        url = self.url_input.text().strip()
        if url.startswith("http"):
            self.selected_file_path = None
            self.selected_file_label.setText("URL: " + url[:30] + "...")
            self.btn_ingest.setEnabled(True)
        else:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid URL starting with http:// or https://")

    def _ingest_source(self):
        if not self.controller or not getattr(self.controller, 'doc_manager', None):
            return
            
        collection = self.collection_combo.currentText()
        self.btn_ingest.setText("Processing... (This may take a minute)")
        self.btn_ingest.setEnabled(False)
        
        try:
            # Force UI update
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()
            
            if self.selected_file_path:
                result = self.controller.doc_manager.ingest_document(
                    self.selected_file_path, collection
                )
            else:
                url = self.url_input.text().strip()
                result = self.controller.doc_manager.ingest_url(url, collection)
                
            QMessageBox.information(self, "Success", f"Ingested {result['chunks_added']} chunks into '{collection}'.")
        except Exception as e:
            logger.exception("Failed to ingest source")
            QMessageBox.critical(self, "Error", f"Failed to process source:\n{e}")
        finally:
            self.btn_ingest.setText("Vectorize Selected Source")
            self.selected_file_path = None
            self.selected_file_label.setText("No source selected")
            self.url_input.clear()
            self.btn_ingest.setEnabled(False)
            self._refresh_stats()

    def _refresh_stats(self):
        self.collection_list.clear()
        if not self.controller or not getattr(self.controller, 'doc_manager', None):
            self.collection_list.addItem("Document manager not initialized.")
            return
            
        try:
            stats = self.controller.doc_manager.get_stats()
            if not stats:
                self.collection_list.addItem("No documents uploaded yet.")
            for col, count in stats.items():
                self.collection_list.addItem(f"📁 {col}  —  {count} chunks embedded")
        except Exception as e:
            self.collection_list.addItem("Could not load collection stats.")
