import json
from pathlib import Path
from PySide6.QtWidgets import QToolTip
from PySide6.QtGui import QCursor
from loguru import logger

_TERMS_DICT = {}

def load_terms():
    global _TERMS_DICT
    if not _TERMS_DICT:
        try:
            terms_path = Path("c:/mediassist/config/medical_terms.json")
            if terms_path.exists():
                with open(terms_path, "r", encoding="utf-8") as f:
                    _TERMS_DICT = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load medical terms: {e}")

def show_nurse_tooltip(term: str) -> None:
    """
    Looks up the medical term in the config dictionary and displays it as a tooltip.
    """
    load_terms()
    term_lower = term.lower().strip()
    meaning = _TERMS_DICT.get(term_lower, "Term not found in dictionary.")
    
    QToolTip.showText(QCursor.pos(), f"<b>{term.capitalize()}</b><br>{meaning}")
