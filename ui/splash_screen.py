import sys
from PySide6.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

class SplashScreen(QSplashScreen):
    """
    MediAssist Pro Splash Screen.
    Shown during initialization.
    """
    def __init__(self):
        super().__init__()
        # In a real app, we'd use a nice image
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        self.label = QLabel("MediAssist Pro - Initializing...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        
        layout.addStretch()
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addSpacing(20)

    def set_status(self, message: str, progress: int = 0):
        self.label.setText(message)
        if progress > 0:
            self.progress.setValue(progress)
        self.showMessage(message, Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        # Force UI update
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
