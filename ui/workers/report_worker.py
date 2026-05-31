import asyncio
from PySide6.QtCore import QThread, Signal
from loguru import logger
from models.report_output import PhysicianBrief
from models.questionnaire import SessionAnswers

class ReportWorker(QThread):
    """
    Asynchronous worker for Report generation.
    Following Blueprint Section 14.3 and 13.
    """
    report_generated = Signal(PhysicianBrief)
    error_occurred = Signal(str)

    def __init__(self, controller, case_number: str, session_answers: SessionAnswers,
                 patient_ctx: dict, vital_signs: dict, specialty: str):
        super().__init__()
        self.controller = controller
        self.case_number = case_number
        self.session_answers = session_answers
        self.patient_ctx = patient_ctx
        self.vital_signs = vital_signs
        self.specialty = specialty

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Extract rag_chunks_used from raw_rag_log in questionnaire_engine if needed
            # For now passing empty list as per simple implementation
            report = loop.run_until_complete(
                self.controller.report_generator.generate(
                    case_number=self.case_number,
                    session_answers=self.session_answers,
                    patient_ctx=self.patient_ctx,
                    vital_signs=self.vital_signs,
                    rag_chunks_used=[],
                    specialty=self.specialty
                )
            )
            self.report_generated.emit(report)
        except Exception as e:
            logger.exception(f"Error in ReportWorker: {e}")
            self.error_occurred.emit(str(e))
        finally:
            loop.close()
