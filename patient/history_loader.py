"""
MediAssist Pro — Patient History Loader.

Builds a comprehensive patient context dictionary from the database,
used by the LLM prompt pipeline to inform clinical decision-making.
"""

from __future__ import annotations

import datetime
from typing import Any, Optional

from loguru import logger
from sqlalchemy.orm import Session

from models.db_models import (
    Allergy,
    Diagnosis,
    Encounter,
    Medication,
    Patient,
    Vaccination,
)
from patient.patient_manager import PatientManager
from patient.vaccination_tracker import VaccinationTracker


def build_patient_context(
    case_number: str,
    session: Session,
) -> dict[str, Any]:
    """
    Assemble a rich patient context dictionary for LLM prompt injection.

    Returned structure::

        {
            "demographics": { ... },
            "chronic_conditions": [ ... ],
            "current_medications": [ ... ],
            "allergies": [ ... ],
            "recent_diagnoses": [ ... ],
            "vaccination_gaps": [ ... ],
        }

    Returns an empty dict with an ``"error"`` key if the patient is not found.
    """
    pm = PatientManager()
    patient = pm.get_patient(session, case_number)

    if patient is None:
        logger.warning("build_patient_context: patient {} not found", case_number)
        return {"error": f"Patient {case_number} not found"}

    age = pm.calculate_age(patient.date_of_birth)

    context: dict[str, Any] = {
        "demographics": _build_demographics(patient, age),
        "chronic_conditions": _get_chronic_conditions(session, case_number),
        "current_medications": _get_current_medications(session, case_number),
        "allergies": _get_allergies(session, case_number),
        "recent_diagnoses": _get_recent_diagnoses(session, case_number),
        "vaccination_gaps": _get_vaccination_gaps(case_number, age, session),
    }

    logger.debug(
        "Patient context built for {} — {} conditions, {} meds, {} allergies",
        case_number,
        len(context["chronic_conditions"]),
        len(context["current_medications"]),
        len(context["allergies"]),
    )
    return context


# ═══════════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════════


def _build_demographics(patient: Patient, age: int) -> dict[str, Any]:
    """Extract non-PII demographic data."""
    return {
        "case_number": patient.case_number,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "age": age,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "nationality": patient.nationality or "Unknown",
        "language": patient.language or "Unknown",
        "blood_type": patient.blood_type or "Unknown",
    }


def _get_chronic_conditions(session: Session, case_number: str) -> list[dict[str, Any]]:
    """Return active/chronic diagnoses."""
    rows = (
        session.query(Diagnosis)
        .filter(
            Diagnosis.case_number == case_number,
            Diagnosis.status.in_(["active", "chronic"]),
        )
        .order_by(Diagnosis.diagnosed_date.desc())
        .all()
    )
    return [
        {
            "icd_code": d.icd_code or "",
            "description": d.description,
            "severity": d.severity or "unspecified",
            "status": d.status,
            "diagnosed_date": d.diagnosed_date or "",
        }
        for d in rows
    ]


def _get_current_medications(session: Session, case_number: str) -> list[dict[str, Any]]:
    """Return medications with status 'active'."""
    rows = (
        session.query(Medication)
        .filter(
            Medication.case_number == case_number,
            Medication.status == "active",
        )
        .order_by(Medication.name)
        .all()
    )
    return [
        {
            "name": m.name,
            "dosage": m.dosage or "",
            "frequency": m.frequency or "",
            "route": m.route or "",
            "start_date": m.start_date or "",
        }
        for m in rows
    ]


def _get_allergies(session: Session, case_number: str) -> list[dict[str, Any]]:
    """Return active allergies."""
    rows = (
        session.query(Allergy)
        .filter(
            Allergy.case_number == case_number,
            Allergy.status == "active",
        )
        .order_by(Allergy.severity.desc())
        .all()
    )
    return [
        {
            "allergen": a.allergen,
            "reaction": a.reaction or "",
            "severity": a.severity or "unknown",
        }
        for a in rows
    ]


def _get_recent_diagnoses(
    session: Session,
    case_number: str,
    months: int = 6,
) -> list[dict[str, Any]]:
    """Return diagnoses from the last *months* months."""
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=months * 30)).strftime(
        "%Y-%m-%d"
    )
    rows = (
        session.query(Diagnosis)
        .filter(
            Diagnosis.case_number == case_number,
            Diagnosis.diagnosed_date >= cutoff,
        )
        .order_by(Diagnosis.diagnosed_date.desc())
        .all()
    )
    return [
        {
            "icd_code": d.icd_code or "",
            "description": d.description,
            "severity": d.severity or "unspecified",
            "status": d.status,
            "diagnosed_date": d.diagnosed_date or "",
        }
        for d in rows
    ]


def _get_vaccination_gaps(
    case_number: str,
    age_years: int,
    session: Session,
) -> list[dict[str, Any]]:
    """Identify overdue vaccines using the VaccinationTracker."""
    try:
        tracker = VaccinationTracker()
        overdue = tracker.get_overdue_vaccines(case_number, age_years, session)
        return overdue
    except Exception as exc:
        logger.warning("Failed to compute vaccination gaps: {}", exc)
        return []
