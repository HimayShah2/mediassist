def calculate_phq9(scores: list[int]) -> dict:
    """
    Calculate PHQ-9 (Patient Health Questionnaire-9) score for depression severity.
    :param scores: List of 9 integers, each between 0 and 3.
    :return: Dictionary with 'score' and 'interpretation'.
    """
    if len(scores) != 9:
        raise ValueError("PHQ-9 requires exactly 9 responses.")
    if any(s < 0 or s > 3 for s in scores):
        raise ValueError("Each PHQ-9 response must be between 0 and 3.")
        
    total_score = sum(scores)
    
    if total_score <= 4:
        interpretation = "Minimal depression"
    elif total_score <= 9:
        interpretation = "Mild depression"
    elif total_score <= 14:
        interpretation = "Moderate depression"
    elif total_score <= 19:
        interpretation = "Moderately severe depression"
    else:
        interpretation = "Severe depression"
        
    return {"score": total_score, "interpretation": interpretation}


def calculate_gcs(eye: int, verbal: int, motor: int) -> dict:
    """
    Calculate GCS (Glasgow Coma Scale) for level of consciousness.
    :param eye: Eye opening response (1-4).
    :param verbal: Verbal response (1-5).
    :param motor: Motor response (1-6).
    :return: Dictionary with 'score' and 'interpretation'.
    """
    if not (1 <= eye <= 4):
        raise ValueError("Eye response must be between 1 and 4.")
    if not (1 <= verbal <= 5):
        raise ValueError("Verbal response must be between 1 and 5.")
    if not (1 <= motor <= 6):
        raise ValueError("Motor response must be between 1 and 6.")
        
    total_score = eye + verbal + motor
    
    if total_score >= 13:
        interpretation = "Mild brain injury"
    elif total_score >= 9:
        interpretation = "Moderate brain injury"
    else:
        interpretation = "Severe brain injury"
        
    return {"score": total_score, "interpretation": interpretation}


def calculate_apgar(appearance: int, pulse: int, grimace: int, activity: int, respiration: int) -> dict:
    """
    Calculate APGAR score for newborn health assessment.
    :param appearance: Skin color (0-2).
    :param pulse: Heart rate (0-2).
    :param grimace: Reflex irritability (0-2).
    :param activity: Muscle tone (0-2).
    :param respiration: Respiratory effort (0-2).
    :return: Dictionary with 'score' and 'interpretation'.
    """
    scores = [appearance, pulse, grimace, activity, respiration]
    if any(s < 0 or s > 2 for s in scores):
        raise ValueError("Each APGAR parameter must be between 0 and 2.")
        
    total_score = sum(scores)
    
    if total_score >= 7:
        interpretation = "Normal"
    elif total_score >= 4:
        interpretation = "Low"
    else:
        interpretation = "Critically low"
        
    return {"score": total_score, "interpretation": interpretation}


def calculate_sofa(respiration: int, coagulation: int, liver: int, cardiovascular: int, cns: int, renal: int) -> dict:
    """
    Calculate SOFA (Sequential Organ Failure Assessment) score.
    :param respiration: Respiratory system score (0-4).
    :param coagulation: Coagulation system score (0-4).
    :param liver: Liver system score (0-4).
    :param cardiovascular: Cardiovascular system score (0-4).
    :param cns: Central nervous system score (0-4).
    :param renal: Renal system score (0-4).
    :return: Dictionary with 'score' and 'interpretation'.
    """
    scores = [respiration, coagulation, liver, cardiovascular, cns, renal]
    if any(s < 0 or s > 4 for s in scores):
        raise ValueError("Each SOFA parameter must be between 0 and 4.")
        
    total_score = sum(scores)
    
    if total_score <= 6:
        interpretation = "Low risk"
    elif total_score <= 9:
        interpretation = "Moderate risk"
    elif total_score <= 12:
        interpretation = "High risk"
    elif total_score <= 14:
        interpretation = "Very high risk"
    else:
        interpretation = "Extremely high risk"
        
    return {"score": total_score, "interpretation": interpretation}
