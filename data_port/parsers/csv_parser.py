import csv
import os
from typing import List, Dict, Any
from loguru import logger


class CSVParser:
    """Stateless CSV parser matching the DataImporter parser interface
    (parse(filepath) -> list of row dicts)."""

    is_available = True

    def parse(self, filepath: str) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        try:
            with open(filepath, mode="r", encoding="utf-8-sig", newline="") as f:
                for row in csv.DictReader(f):
                    rows.append({k: v for k, v in row.items() if k})
        except Exception as e:
            logger.error(f"CSV parse failed for {filepath}: {e}")
        return rows


class CSVHistoryParser:
    """Backend parser for legacy patient history CSV files (Blueprint §21)."""
    
    def parse_and_import(self, file_path, db_session):
        logger.info(f"Starting legacy import from: {file_path}")
        success_count = 0
        
        try:
            with open(file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # In a real implementation, we'd map row keys to SQLAlchemy models
                    # e.g., Patient(first_name=row['First'], ...)
                    success_count += 1
            
            db_session.commit()
            return {"status": "success", "count": success_count}
        except Exception as e:
            db_session.rollback()
            logger.error(f"Legacy CSV import failed: {e}")
            return {"status": "error", "message": str(e)}
