"""
MediAssist Pro — Patient Manager.

CRUD operations for the Patient table with fuzzy search, soft-delete,
age calculation, and PII encryption hooks.
"""

from __future__ import annotations

import datetime
from typing import Optional

from loguru import logger
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from database.encryption import FieldEncryptor
from models.db_models import Patient
from patient.case_number import generate_case_number


class PatientManager:
    """
    High-level patient operations backed by SQLAlchemy sessions.

    All PII fields (``national_id``, ``contact_number``,
    ``emergency_contact_phone``) are encrypted at rest.
    """

    def __init__(self) -> None:
        self._encryptor = FieldEncryptor()

    # ── Create ─────────────────────────────────────────────────────────────

    def create_patient(
        self,
        session: Session,
        *,
        first_name: str,
        last_name: str,
        date_of_birth: str,
        gender: str,
        facility_code: str = "DEV",
        national_id: str | None = None,
        contact_number: str | None = None,
        address: str | None = None,
        nationality: str | None = None,
        language: str | None = None,
        blood_type: str | None = None,
        emergency_contact_name: str | None = None,
        emergency_contact_phone: str | None = None,
        notes: str | None = None,
    ) -> Patient:
        """
        Create a new patient record with an auto-generated case number.

        PII fields are encrypted before persistence.
        """
        case_number = generate_case_number(session, facility_code)

        patient = Patient(
            case_number=case_number,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            facility_code=facility_code,
            national_id=self._encrypt_if_present(national_id),
            contact_number=self._encrypt_if_present(contact_number),
            address=address,
            nationality=nationality,
            language=language,
            blood_type=blood_type,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_phone=self._encrypt_if_present(emergency_contact_phone),
            notes=notes,
        )

        session.add(patient)
        session.flush()  # populate id and case_number
        logger.info("Patient created: {} {}", case_number, first_name)
        return patient

    # ── Search ─────────────────────────────────────────────────────────────

    def search_patients(
        self,
        session: Session,
        query: str,
        search_type: str = "name",
        limit: int = 20,
    ) -> list[Patient]:
        """
        Search patients by name, case number, or national ID.

        Args:
            session: Active SQLAlchemy session.
            query: The search string.
            search_type: One of ``'name'``, ``'case_number'``, ``'id'``.
            limit: Maximum results to return.

        Returns:
            List of matching :class:`Patient` objects.
        """
        q = session.query(Patient).filter(Patient.is_deleted == False)  # noqa: E712

        if search_type == "case_number":
            q = q.filter(Patient.case_number.ilike(f"%{query}%"))
        elif search_type == "id":
            # National IDs are encrypted; search requires exact match after encryption
            # For usability, we also support case_number lookup here
            q = q.filter(
                or_(
                    Patient.case_number.ilike(f"%{query}%"),
                    Patient.national_id == self._encrypt_if_present(query),
                )
            )
        else:
            # Fuzzy name search: LIKE on first_name and last_name
            like_pattern = f"%{query}%"
            q = q.filter(
                or_(
                    Patient.first_name.ilike(like_pattern),
                    Patient.last_name.ilike(like_pattern),
                    func.concat(Patient.first_name, " ", Patient.last_name).ilike(like_pattern),
                )
            )

        results = q.order_by(Patient.last_name, Patient.first_name).limit(limit).all()
        logger.debug("search_patients({!r}, type={}) → {} results", query, search_type, len(results))
        return results

    # ── Get one ────────────────────────────────────────────────────────────

    def get_patient(self, session: Session, case_number: str) -> Optional[Patient]:
        """
        Retrieve a single patient by case number.

        Returns ``None`` if not found or soft-deleted.
        """
        return (
            session.query(Patient)
            .filter(Patient.case_number == case_number, Patient.is_deleted == False)  # noqa: E712
            .first()
        )

    # ── Recent ─────────────────────────────────────────────────────────────

    def get_recent_patients(self, session: Session, limit: int = 5) -> list[Patient]:
        """Return the most recently created (non-deleted) patients."""
        return (
            session.query(Patient)
            .filter(Patient.is_deleted == False)  # noqa: E712
            .order_by(Patient.created_at.desc())
            .limit(limit)
            .all()
        )

    # ── Update ─────────────────────────────────────────────────────────────

    def update_patient(
        self,
        session: Session,
        case_number: str,
        **kwargs: object,
    ) -> Optional[Patient]:
        """
        Update fields on an existing patient.

        PII fields are re-encrypted automatically.

        Args:
            session: Active SQLAlchemy session.
            case_number: Target patient's case number.
            **kwargs: Field-value pairs to update.

        Returns:
            The updated patient, or ``None`` if not found.
        """
        patient = self.get_patient(session, case_number)
        if patient is None:
            logger.warning("update_patient: {} not found", case_number)
            return None

        pii_fields = {"national_id", "contact_number", "emergency_contact_phone"}

        for field, value in kwargs.items():
            if not hasattr(patient, field):
                logger.warning("Ignoring unknown patient field: {}", field)
                continue
            if field in pii_fields and isinstance(value, str):
                value = self._encrypt_if_present(value)
            setattr(patient, field, value)

        patient.updated_at = datetime.datetime.utcnow()
        session.flush()
        logger.info("Patient updated: {}", case_number)
        return patient

    # ── Soft delete ────────────────────────────────────────────────────────

    def soft_delete_patient(self, session: Session, case_number: str) -> bool:
        """
        Mark a patient as deleted without removing the row.

        Returns ``True`` if the patient was found and marked.
        """
        patient = self.get_patient(session, case_number)
        if patient is None:
            logger.warning("soft_delete_patient: {} not found", case_number)
            return False

        patient.is_deleted = True
        patient.updated_at = datetime.datetime.utcnow()
        session.flush()
        logger.info("Patient soft-deleted: {}", case_number)
        return True

    # ── Age calculation ────────────────────────────────────────────────────

    @staticmethod
    def calculate_age(dob: str) -> int:
        """
        Calculate age in whole years from a ``YYYY-MM-DD`` date-of-birth string.

        Returns ``0`` if the date cannot be parsed.
        """
        try:
            birth = datetime.datetime.strptime(dob, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            logger.warning("Invalid DOB format: {!r}", dob)
            return 0

        today = datetime.date.today()
        age = today.year - birth.year
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1
        return max(age, 0)

    # ── Decryption helper (for display) ────────────────────────────────────

    def decrypt_pii(self, patient: Patient) -> dict[str, str]:
        """
        Return a dict of decrypted PII fields for UI display.

        Keys: ``national_id``, ``contact_number``, ``emergency_contact_phone``.
        """
        return {
            "national_id": self._encryptor.decrypt(patient.national_id or ""),
            "contact_number": self._encryptor.decrypt(patient.contact_number or ""),
            "emergency_contact_phone": self._encryptor.decrypt(
                patient.emergency_contact_phone or ""
            ),
        }

    # ── Internal ───────────────────────────────────────────────────────────

    def _encrypt_if_present(self, value: str | None) -> str | None:
        """Encrypt a string only if it is non-None and non-empty."""
        if value:
            return self._encryptor.encrypt(value)
        return value
