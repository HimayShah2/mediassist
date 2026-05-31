from enum import Enum, auto
from typing import Optional, Dict, Any

class SessionState(Enum):
    IDLE = auto()
    PATIENT_LOADED = auto()
    VISIT_TYPE_SELECTED = auto()
    
    ROUND_1_GENERATING = auto()
    ROUND_1_ACTIVE = auto()
    ROUND_1_SUBMITTED = auto()
    
    ROUND_2_GENERATING = auto()
    ROUND_2_ACTIVE = auto()
    ROUND_2_SUBMITTED = auto()
    
    ROUND_3_GENERATING = auto()
    ROUND_3_ACTIVE = auto()
    ROUND_3_SUBMITTED = auto()
    
    ROUND_4_GENERATING = auto()
    ROUND_4_ACTIVE = auto()
    ROUND_4_SUBMITTED = auto()
    
    VITALS_CAPTURE = auto()
    REPORT_GENERATING = auto()
    REPORT_READY = auto()
    SAVED = auto()
    
    EMERGENCY = auto()
    PHYSICIAN_VIEW = auto()

class EngineStateMachine:
    def __init__(self):
        self.state = SessionState.IDLE
        
    def transition(self, new_state: SessionState):
        """Transitions to a new state in the state machine."""
        # Any state can transition to EMERGENCY or IDLE
        self.state = new_state
        print(f"State transitioned to {self.state.name}")
        
    def trigger_emergency(self):
        """Emergency override for red flags in any round."""
        self.transition(SessionState.EMERGENCY)
        
    def cancel_session(self):
        """Returns to IDLE from any state on 'Cancel Session' or 'New Patient'."""
        self.transition(SessionState.IDLE)
        
    def physician_login(self):
        """Transitions to PHYSICIAN_VIEW if the report is ready."""
        if self.state == SessionState.REPORT_READY:
            self.transition(SessionState.PHYSICIAN_VIEW)

    def process_round(self, round_number: int):
        """Advance state for a given round number."""
        if round_number == 1:
            self.transition(SessionState.ROUND_1_GENERATING)
            self.transition(SessionState.ROUND_1_ACTIVE)
            self.transition(SessionState.ROUND_1_SUBMITTED)
        elif round_number == 2:
            self.transition(SessionState.ROUND_2_GENERATING)
            self.transition(SessionState.ROUND_2_ACTIVE)
            self.transition(SessionState.ROUND_2_SUBMITTED)
        elif round_number == 3:
            self.transition(SessionState.ROUND_3_GENERATING)
            self.transition(SessionState.ROUND_3_ACTIVE)
            self.transition(SessionState.ROUND_3_SUBMITTED)
        elif round_number == 4:
            self.transition(SessionState.ROUND_4_GENERATING)
            self.transition(SessionState.ROUND_4_ACTIVE)
            self.transition(SessionState.ROUND_4_SUBMITTED)
        else:
            raise ValueError(f"Invalid round number: {round_number}")
            
    def complete_session(self):
        """Handle vitals capture and report generation."""
        self.transition(SessionState.VITALS_CAPTURE)
        self.transition(SessionState.REPORT_GENERATING)
        self.transition(SessionState.REPORT_READY)
        self.transition(SessionState.SAVED)
