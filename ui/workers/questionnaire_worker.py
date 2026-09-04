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
                 patient_ctx: dict, specialty: str, focus: dict = None):
        super().__init__()
        self.controller = controller
        self.round_number = round_number
        self.visit_type = visit_type
        self.patient_ctx = patient_ctx
        self.specialty = specialty
        self.focus = focus

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
                    specialty=self.specialty,
                    focus=self.focus,
                )
            )
            self.round_generated.emit(round_data)
        except Exception as e:
            logger.exception(f"Error in QuestionnaireWorker: {e}")
            self.error_occurred.emit(str(e))
        finally:
            loop.close()


class NextStepWorker(QThread):
    """After a round is submitted, decides whether to run another (focused) round
    or move on to vitals/brief. Runs the sufficiency assessment off the UI thread."""
    advance = Signal(int, object)   # next round_number, focus dict (or None)
    complete = Signal(object)       # assessment dict
    error_occurred = Signal(str)

    def __init__(self, controller, round_number, visit_type, patient_ctx, specialty):
        super().__init__()
        self.controller = controller
        self.round_number = round_number
        self.visit_type = visit_type
        self.patient_ctx = patient_ctx
        self.specialty = specialty

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            step = loop.run_until_complete(
                self.controller.questionnaire_engine.next_step(
                    self.round_number, self.visit_type, self.patient_ctx, self.specialty)
            )
            if step.get("action") == "round":
                self.advance.emit(step["round"], step.get("focus"))
            else:
                self.complete.emit(step.get("assessment", {}))
        except Exception as e:
            logger.exception(f"Error in NextStepWorker: {e}")
            self.error_occurred.emit(str(e))
        finally:
            loop.close()
