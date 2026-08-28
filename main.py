import sys
import os
from loguru import logger


from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app_controller import AppController
from ui.main_window import MainWindow

def main():
    """
    MediAssist Pro - Main Entry Point.
    Following Blueprint Section 14.1
    """
    # High DPI support for modern Windows displays
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setApplicationName("MediAssist Pro")
    app.setApplicationVersion("2.0.0")
    app.setStyle("Fusion")

    # Apply Global Dark Theme
    theme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mediassist_theme.qss")
    if os.path.exists(theme_path):
        with open(theme_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        logger.info("Global dark theme applied successfully.")
    else:
        logger.warning(f"Theme file not found at {theme_path}")

    # In a real scenario, we'd have a Splash Screen here
    logger.info("Initializing AppController...")
    controller = AppController()
    controller.initialize()

    logger.info("Launching MainWindow...")
    window = MainWindow(controller=controller)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
