import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("pandas not available. Excel parsing will be disabled.")

class ExcelParser:
    def __init__(self):
        self.is_available = PANDAS_AVAILABLE

    def parse(self, filepath: str) -> List[Dict[str, Any]]:
        if not self.is_available:
            logger.error("Excel parser is not available because pandas is missing.")
            return []
        
        try:
            df = pd.read_excel(filepath)
            return df.to_dict(orient='records')
        except Exception as e:
            logger.error(f"Failed to parse Excel {filepath}: {e}")
            return []
