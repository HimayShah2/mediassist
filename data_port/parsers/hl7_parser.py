import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:
    import hl7
    HL7_AVAILABLE = True
except ImportError:
    HL7_AVAILABLE = False
    logger.warning("hl7 package not available. HL7 parsing will be disabled.")

class HL7Parser:
    def __init__(self):
        self.is_available = HL7_AVAILABLE

    def parse(self, filepath: str) -> List[Dict[str, Any]]:
        if not self.is_available:
            logger.error("HL7 parser is not available because hl7 package is missing.")
            return []
        
        results = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                hl7_message = f.read()
            h = hl7.parse(hl7_message)
            results.append({"raw_hl7": str(h)})
        except Exception as e:
            logger.error(f"Failed to parse HL7 {filepath}: {e}")
            
        return results
