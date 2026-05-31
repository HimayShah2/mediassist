import logging
from datetime import datetime, date
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class VaccinationTracker:
    """
    Tracks patient vaccinations and performs EPI (Expanded Programme on Immunization) 
    schedule gap analysis. Fails gracefully if date processing encounters issues.
    """
    
    EPI_SCHEDULE = {
        "BCG": 0,          
        "OPV_0": 0,        
        "HepB_0": 0,       
        "Pentavalent_1": 1.5, 
        "OPV_1": 1.5,
        "Rotavirus_1": 1.5,
        "Pentavalent_2": 2.5, 
        "OPV_2": 2.5,
        "Rotavirus_2": 2.5,
        "Pentavalent_3": 3.5, 
        "OPV_3": 3.5,
        "Measles_1": 9,    
        "Measles_2": 15    
    }

    def __init__(self):
        pass

    def analyze_gaps(self, dob: date, administered_vaccines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        gaps = []
        try:
            today = date.today()
            age_in_months = (today.year - dob.year) * 12 + today.month - dob.month
            if today.day < dob.day:
                age_in_months -= 1
                
            administered_names = [v.get("name") for v in administered_vaccines if v.get("name")]
            
            for vaccine, recommended_age_months in self.EPI_SCHEDULE.items():
                if vaccine not in administered_names:
                    if age_in_months >= recommended_age_months:
                        gaps.append({
                            "vaccine": vaccine,
                            "recommended_age_months": recommended_age_months,
                            "status": "OVERDUE",
                            "message": f"Vaccine {vaccine} is overdue. Recommended at {recommended_age_months} months."
                        })
                    else:
                        gaps.append({
                            "vaccine": vaccine,
                            "recommended_age_months": recommended_age_months,
                            "status": "UPCOMING",
                            "message": f"Vaccine {vaccine} is due at {recommended_age_months} months."
                        })
        except Exception as e:
            logger.error(f"Failed to analyze vaccination gaps: {e}")
            
        return gaps
