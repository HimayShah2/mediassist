"""
MediAssist Pro — Case Number Generator.

Generates sequential, facility-scoped case numbers in the format::

    {FACILITY}-{YYYY}-{NNNN}

Example: ``DEV-2026-0001``
"""

from __future__ import annotations

import datetime

from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.db_models import Patient


def generate_case_number(session: Session, facility_code: str = "DEV") -> str:
    """
    Generate the next sequential case number for a facility and year.

    Format: ``{FACILITY}-{YYYY}-{NNNN}``

    The sequence counter is derived from the count of existing patients
    whose case number starts with the same facility-year prefix.

    Args:
        session: Active SQLAlchemy session.
        facility_code: Short facility identifier (e.g. ``"DEV"``).

    Returns:
        A unique case number string.
    """
    year = datetime.datetime.now().year
    prefix = f"{facility_code}-{year}-"

    # Count existing case numbers with this prefix
    count: int = (
        session.query(func.count(Patient.id))
        .filter(Patient.case_number.like(f"{prefix}%"))
        .scalar()
    ) or 0

    # Next sequence number (1-based)
    next_seq = count + 1
    case_number = f"{prefix}{next_seq:04d}"

    # Safety: ensure uniqueness (collision guard)
    while (
        session.query(Patient.id)
        .filter(Patient.case_number == case_number)
        .first()
        is not None
    ):
        next_seq += 1
        case_number = f"{prefix}{next_seq:04d}"

    logger.debug("Generated case number: {}", case_number)
    return case_number
