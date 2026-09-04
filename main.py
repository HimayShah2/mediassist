import sys
import os
import traceback
from loguru import logger


from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QPixmap, QColor

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

    # Splash screen — first run downloads + loads the local AI model, which
    # takes a while; the user must see that something is happening.
    pix = QPixmap(560, 320)
    pix.fill(QColor("#0F2D52"))
    splash = QSplashScreen(pix)
    splash.showMessage("Starting MediAssist Pro…", Qt.AlignBottom | Qt.AlignHCenter, QColor("white"))
    splash.show()
    app.processEvents()

    def on_status(msg: str):
        splash.showMessage(str(msg), Qt.AlignBottom | Qt.AlignHCenter, QColor("white"))
        QCoreApplication.processEvents()

    logger.info("Initializing AppController...")
    controller = AppController(splash_callback=on_status)
    try:
        controller.initialize()
    except Exception as e:
        logger.exception("Startup failed")
        splash.close()
        QMessageBox.critical(None, "MediAssist Pro — startup failed",
                             f"{e}\n\n{traceback.format_exc()[-800:]}")
        sys.exit(1)

    logger.info("Launching MainWindow...")
    window = MainWindow(controller=controller)
    window.show()
    splash.finish(window)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
