import sys
from pathlib import Path

# Add project root to path
sys.path.append('c:/mediassist')

from config.settings import settings
from database.connection import init_db, get_session
from patient.patient_manager import PatientManager

def main():
    print("Initializing database...")
    init_db()
    print("Database initialized.")
    
    manager = PatientManager()
    with get_session() as session:
        print("Creating patient...")
        patient = manager.create_patient(
            session=session,
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            gender="Male",
            facility_code="TEST",
            national_id="123456789",
        )
        print(f"Created patient with case number: {patient.case_number}")
        print(f"Encrypted national ID: {patient.national_id}")
        
        print("Decrypting PII...")
        pii = manager.decrypt_pii(patient)
        print(f"Decrypted National ID: {pii['national_id']}")

if __name__ == "__main__":
    main()
