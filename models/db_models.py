"""
MediAssist Pro — SQLAlchemy ORM Models.

Canonical database schema for the medical application.
All tables use soft-delete (is_deleted flag) where applicable.
"""

from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    event,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Shared declarative base for all models."""
    pass


# ═══════════════════════════════════════════════════════════════════════════
# Patient
# ═══════════════════════════════════════════════════════════════════════════
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_number = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(String(10), nullable=False)  # YYYY-MM-DD
    gender = Column(String(20), nullable=False)
    national_id = Column(String(255), nullable=True)  # encrypted PII
    contact_number = Column(String(255), nullable=True)  # encrypted PII
    address = Column(Text, nullable=True)
    nationality = Column(String(100), nullable=True)
    language = Column(String(50), nullable=True)
    blood_type = Column(String(5), nullable=True)
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(255), nullable=True)  # encrypted
    notes = Column(Text, nullable=True)
    facility_code = Column(String(10), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )

    # Relationships
    diagnoses = relationship("Diagnosis", back_populates="patient", lazy="select")
    medications = relationship("Medication", back_populates="patient", lazy="select")
    allergies = relationship("Allergy", back_populates="patient", lazy="select")
    vaccinations = relationship("Vaccination", back_populates="patient", lazy="select")
    lab_results = relationship("LabResult", back_populates="patient", lazy="select")
    encounters = relationship("Encounter", back_populates="patient", lazy="select")

    __table_args__ = (
        Index("ix_patients_name", "first_name", "last_name"),
    )


# ═══════════════════════════════════════════════════════════════════════════
# Diagnosis
# ═══════════════════════════════════════════════════════════════════════════
class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    case_number = Column(String(20), nullable=False, index=True)
    icd_code = Column(String(10), nullable=True)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=True)
    status = Column(String(20), default="active")  # active / resolved / chronic
    diagnosed_date = Column(String(10), nullable=True)
    resolved_date = Column(String(10), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="diagnoses")


# ═══════════════════════════════════════════════════════════════════════════
# Medication
# ═══════════════════════════════════════════════════════════════════════════
class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    case_number = Column(String(20), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    dosage = Column(String(100), nullable=True)
    frequency = Column(String(100), nullable=True)
    route = Column(String(50), nullable=True)
    start_date = Column(String(10), nullable=True)
    end_date = Column(String(10), nullable=True)
    status = Column(String(20), default="active")  # active / completed / discontinued
    prescribing_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="medications")


# ═══════════════════════════════════════════════════════════════════════════
# Allergy
# ═══════════════════════════════════════════════════════════════════════════
class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    case_number = Column(String(20), nullable=False, index=True)
    allergen = Column(String(200), nullable=False)
    reaction = Column(Text, nullable=True)
    severity = Column(String(20), nullable=True)  # mild / moderate / severe
    status = Column(String(20), default="active")
    noted_date = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="allergies")


# ═══════════════════════════════════════════════════════════════════════════
# Vaccination
# ═══════════════════════════════════════════════════════════════════════════
class Vaccination(Base):
    __tablename__ = "vaccinations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    case_number = Column(String(20), nullable=False, index=True)
    vaccine_name = Column(String(200), nullable=False)
    dose_number = Column(Integer, nullable=True)
    date_administered = Column(String(10), nullable=True)
    batch_number = Column(String(50), nullable=True)
    site = Column(String(50), nullable=True)
    administered_by = Column(String(100), nullable=True)
    next_due_date = Column(String(10), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="vaccinations")


# ═══════════════════════════════════════════════════════════════════════════
# Lab Result
# ═══════════════════════════════════════════════════════════════════════════
class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    case_number = Column(String(20), nullable=False, index=True)
    test_name = Column(String(200), nullable=False)
    result_value = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=True)
    reference_range = Column(String(100), nullable=True)
    status = Column(String(20), default="normal")  # normal / abnormal / critical
    test_date = Column(String(10), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="lab_results")


# ═══════════════════════════════════════════════════════════════════════════
# Encounter
# ═══════════════════════════════════════════════════════════════════════════
class Encounter(Base):
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    case_number = Column(String(20), nullable=False, index=True)
    encounter_type = Column(String(50), nullable=True)  # intake / follow-up / emergency
    chief_complaint = Column(Text, nullable=True)
    clinical_notes = Column(Text, nullable=True)
    triage_category = Column(String(20), nullable=True)
    vitals_json = Column(Text, nullable=True)  # JSON blob
    questionnaire_json = Column(Text, nullable=True)  # JSON blob
    ai_summary = Column(Text, nullable=True)
    encounter_date = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    patient = relationship("Patient", back_populates="encounters")


# ═══════════════════════════════════════════════════════════════════════════
# Audit Log
# ═══════════════════════════════════════════════════════════════════════════
class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    user = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
