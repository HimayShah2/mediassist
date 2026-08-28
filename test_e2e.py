import sys
import asyncio
from PySide6.QtWidgets import QApplication
from app_controller import AppController
from ui.main_window import MainWindow

def test():
    app = QApplication(sys.argv)
    controller = AppController()
    controller.initialize()
    
    window = MainWindow(controller=controller)
    # Simulate Login
    print("Simulating Login...")
    window.login_view.input_user.setText("admin")
    window.login_view.input_pass.setText("admin")
    window.login_view.btn_admin.click()
    
    print("Login successful. Current View:", window.stacked_widget.currentWidget().__class__.__name__)
    
    # Simulate Questionnaire start
    print("Simulating Questionnaire Start...")
    window.patient_view.btn_intake.click()
    print("Intake clicked. Current View:", window.stacked_widget.currentWidget().__class__.__name__)
    
    # Simulate completing questionnaire (which hits the LLM and Report Generator)
    # Actually, the user might just be clicking around and it crashes.
    print("Closing...")
    app.quit()

if __name__ == "__main__":
    test()
