import asyncio
from PySide6.QtCore import QThread, Signal, Slot
from loguru import logger
from models.questionnaire import QuestionnaireRound

class QuestionnaireWorker(QThread):
    """
    Asynchronous worker for Questionnaire generation.
    Following Blueprint Section 14.2 and 13.
    """
    round_generated = Signal(QuestionnaireRound)
    error_occurred = Signal(str)

    def __init__(self, controller, round_number: int, visit_type: str, 
                 patient_ctx: dict, specialty: str):
        super().__init__()
        self.controller = controller
        self.round_number = round_number
        self.visit_type = visit_type
        self.patient_ctx = patient_ctx
        self.specialty = specialty

    def run(self):
        try:
            # QuestionnaireEngine.generate_round is an async function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            round_data = loop.run_until_complete(
                self.controller.questionnaire_engine.generate_round(
                    round_number=self.round_number,
                    visit_type=self.visit_type,
                    patient_ctx=self.patient_ctx,
                    specialty=self.specialty
                )
            )
            self.round_generated.emit(round_data)
        except Exception as e:
            logger.exception(f"Error in QuestionnaireWorker: {e}")
            self.error_occurred.emit(str(e))
        finally:
            loop.close()
