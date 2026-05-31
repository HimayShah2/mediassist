from enum import Enum

class VisitType(Enum):
    VACCINATION = "Vaccination/Immunization"
    GENERAL = "General/Routine Checkup"
    SPECIFIC = "Specific Complaint"
    FOLLOWUP = "Follow-up"
    MATERNAL = "Maternal/Antenatal Care"
    PEDIATRIC = "Pediatric Well-Visit"
    MENTAL = "Mental Health Screen"

VISIT_TYPE_MAPPING = {
    VisitType.VACCINATION: "Vaccination/Immunization Visit",
    VisitType.GENERAL: "General/Routine Checkup",
    VisitType.SPECIFIC: "Specific Complaint / Acute Visit",
    VisitType.FOLLOWUP: "Follow-up for Previous Condition",
    VisitType.MATERNAL: "Maternal/Antenatal Care",
    VisitType.PEDIATRIC: "Pediatric Well-Visit",
    VisitType.MENTAL: "Mental Health Screening"
}

def get_visit_type_name(visit_type: VisitType) -> str:
    """Returns the human-readable name for a given visit type."""
    return VISIT_TYPE_MAPPING.get(visit_type, visit_type.value if isinstance(visit_type, VisitType) else "Unknown Visit Type")
