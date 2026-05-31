import os
import logging
from typing import List, Dict, Any

from .parsers.csv_parser import CSVParser
from .parsers.excel_parser import ExcelParser
from .parsers.hl7_parser import HL7Parser
from .parsers.fhir_parser import FHIRParser
from .parsers.pdf_parser import PDFParser

logger = logging.getLogger(__name__)

class DataImporter:
    def __init__(self):
        self.parsers = {
            '.csv': CSVParser(),
            '.xlsx': ExcelParser(),
            '.xls': ExcelParser(),
            '.hl7': HL7Parser(),
            '.json': FHIRParser(),
            '.fhir': FHIRParser(),
            '.pdf': PDFParser()
        }

    def import_file(self, filepath: str) -> List[Dict[str, Any]]:
        if not os.path.exists(filepath):
            logger.error(f"File not found: {filepath}")
            return []
            
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        
        parser = self.parsers.get(ext)
        if not parser:
            logger.warning(f"No parser available for extension: {ext}")
            return []
            
        if not getattr(parser, 'is_available', True):
            logger.warning(f"Parser for {ext} is not available due to missing dependencies.")
            return []
            
        return parser.parse(filepath)

    def import_batch(self, directory_path: str) -> Dict[str, List[Dict[str, Any]]]:
        results = {}
        if not os.path.isdir(directory_path):
            logger.error(f"Directory not found: {directory_path}")
            return results
            
        for filename in os.listdir(directory_path):
            filepath = os.path.join(directory_path, filename)
            if os.path.isfile(filepath):
                results[filepath] = self.import_file(filepath)
                
        return results
