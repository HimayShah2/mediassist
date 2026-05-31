from typing import List, Dict
from models.questionnaire import SessionAnswers

class RedFlagDetector:
    """Scans answers in real-time for emergency clinical markers."""
    
    # Common emergency markers (Simplified for now)
    EMERGENCY_KEYWORDS = [
        "chest pain", "shortness of breath", "loss of consciousness", 
        "facial droop", "severe bleeding", "meningitis", "fetal distress"
    ]

    def check_answers(self, answers: Dict, round_number: int) -> List[str]:
        """
        Checks a dictionary of answers for red flags.
        Returns a list of flags found.
        """
        flags = []
        
        # Check for explicitly marked red flags in MCQ options
        # (This logic depends on how the UI passes the selected option objects)
        
        # Simple keyword fallback for now
        for q_id, answer in answers.items():
            if isinstance(answer, str):
                for keyword in self.EMERGENCY_KEYWORDS:
                    if keyword in answer.lower():
                        flags.append(f"Emergency keyword detected in {q_id}: {keyword}")
        
        return flags
