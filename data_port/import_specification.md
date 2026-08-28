# MediAssist Pro — Legacy Data Import Specification
## HIPAA-Compliant CSV/Excel Format (Version 1.0)

To ensure secure and accurate ingestion of patient history, all import files MUST follow this exact header structure.

### 1. Master Patient Record (CSV/Excel)
| Header | Description | Format | Required |
|--------|-------------|--------|----------|
| `case_number` | Unique ID | `FACILITY-YYYY-XXXX` | **YES** |
| `first_name` | Patient First Name | String | **YES** |
| `last_name` | Patient Last Name | String | **YES** |
| `dob` | Date of Birth | `YYYY-MM-DD` | **YES** |
| `gender` | Biologic Sex | `male`, `female`, `other` | **YES** |
| `phone` | Primary Contact | `+CountryCode-Number` | No |
| `chronic_conditions` | Existing Diseases | Comma-separated strings | No |
| `known_allergies` | Allergies & Severity | `Allergen(Severity); ...` | No |
| `last_visit_date` | Date of last encounter | `YYYY-MM-DD` | No |

---

### 2. HIPAA Compliance Checklist for Data Sharing
1. **Encryption at Rest:** Ensure the source CSV/Excel file is stored on an encrypted volume (BitLocker) before import.
2. **PII Removal:** If sharing data for research, all PII (Name, Phone, DOB) MUST be replaced with a de-identified hash.
3. **Secure Hand-off:** Only authorized ADMIN users should handle these import files.
4. **Validation:** malformed dates or missing IDs will cause the record to be rejected to prevent data corruption.
