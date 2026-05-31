# MediAssist Pro
## Humanitarian Doctor Assistant System — Complete Development Blueprint
### Version 2.0 | Final Edition | Engineered for Agentic IDE Development (Cursor / Windsurf / GitHub Copilot Workspace)

---

> **Document Purpose:** This is the single, final, implementation-ready technical specification for MediAssist Pro — a Windows-native, AI-powered clinical intake and decision-support system. Every section is written to be directly consumed and executed by an agentic AI development environment with zero ambiguity. Every assumption is explicit. Every dependency is pinned. Every prompt is written. Every module has an owner. Follow this document top-to-bottom, section by section, to build the entire system. Do not deviate from the tech stack without explicit instruction. **Reliability and clinical correctness override all other considerations.**

---

## TABLE OF CONTENTS

1. Executive Summary
2. Vision & Humanitarian Mission
3. System Architecture Overview
4. Technology Stack (Complete)
5. NVIDIA NIM API Strategy — 7-Key Management & Model Guide
6. Document Management & RAG Pipeline
7. Agentic Questionnaire Engine (Core)
8. Patient Management System
9. UI/UX Design Blueprint — Nursing Staff Focus
10. Physician Dashboard & Raw Data Access
11. Accuracy & Validation Framework (99.99% Target)
12. Security, Privacy & Compliance
13. Project File & Folder Structure
14. Core Module Code Architecture
15. Development Phases & Milestones
16. Testing Strategy
17. Deployment & Distribution Guide
18. Comprehensive Resource Library (350+ Resources)
19. Doctor Field Configuration Matrix — All Specialties (Bonus A)
20. Prompt Engineering Reference Library (Bonus B)
21. Data Port & Legacy Import System (Bonus C)
22. Emergency Triage Protocol Module (Bonus D)
23. Clinical Scoring Tools Reference (Bonus E)
24. Appendix — Developer Quick-Start Checklist

---

---

## SECTION 1: EXECUTIVE SUMMARY

> ★ **KEY FLAGS FOR THIS SECTION**
> - System targets humanitarian, under-resourced healthcare settings — physician time maximization is the primary goal
> - 99.99% accuracy is achieved through a four-layer trust architecture, not a single model
> - The system is a **decision-support tool** — it never diagnoses autonomously
> - All outputs require a physician sign-off before being marked final
> - Physician has full raw data access: raw LLM responses, RAG chunks, confidence breakdowns, full audit trail
> - Seven NVIDIA NIM API keys are pooled with role-based routing and automatic failover
> - Full offline fallback exists using a local quantized medical LLM

**MediAssist Pro** is a Windows-native, offline-capable, AI-augmented clinical intake and decision-support system built specifically for humanitarian healthcare settings — rural clinics, mobile health camps, NGO-operated facilities, refugee health posts, district hospitals, and under-resourced community clinics. The system positions itself between the nursing intake team and the attending physician: nursing staff guide patients through an intelligent, adaptive questionnaire, and the system outputs a structured, RAG-grounded clinical brief that the doctor acts upon immediately.

### What the System Does — Step by Step

**Step 1 — Patient Identification:** Nurse searches by case number, name, phone, or DOB. If not found, registers a new patient and the system generates a structured case number (`{FACILITY}-{YYYY}-{NNNN}`) and initializes a longitudinal patient record.

**Step 2 — Visit Type Selection:** Nurse selects from 7 visit categories — Vaccination/Immunization, General/Routine Checkup, Specific Complaint, Follow-up, Maternal/Antenatal Care, Pediatric Well-Visit, Mental Health Screen. This primes the agentic questionnaire engine with specialty-specific RAG collections and LLM role selection.

**Step 3 — Adaptive Questionnaire (3–4 Rounds):** The engine generates fully dynamic MCQ questions. Complex medical terms have inline nurse explanations. Questions adapt to every prior answer using a stateful LLM loop with RAG context injection. No static forms exist.

**Step 4 — Vital Signs Capture:** After questionnaire rounds, the nurse enters any available vital signs (BP, HR, RR, SpO2, Temp, Weight, Height, AVPU) via a dedicated structured form. These are injected directly into the physician brief context.

**Step 5 — Clinical Output Report:** A structured physician brief is generated containing: color-coded clinical flags (RED/AMBER/GREEN), top 3–5 differential diagnoses with ICD-10/11 codes, suggested physical examination checklist, recommended investigations, and full RAG-cited sources from uploaded medical literature.

**Step 6 — Physician Raw Data Access:** The attending physician can access the full raw session data including: every question and answer, all RAG chunks retrieved and their similarity scores, raw LLM API responses, confidence score breakdown, and the option to query the patient database directly.

**Step 7 — Record Storage & History:** All data persists in an encrypted local SQLite database. Past visits, vaccination records, chronic conditions, medications, and allergies are loaded at session start and made available as context to the questionnaire engine.

### Technology Foundation

| Layer | Technology | Version |
|-------|-----------|---------|
| UI Framework | Python + PySide6 (Qt 6.x) | 3.11 / 6.7.x |
| AI Engine | NVIDIA NIM API (7 rotating keys) | API v1 |
| Orchestration | LangChain + custom agentic loop | 0.3.x |
| Vector DB | ChromaDB (local, embedded) | 0.5.x |
| Relational DB | SQLite + SQLAlchemy ORM | 3.x / 2.x |
| Report Export | ReportLab + Jinja2 | 4.x / 3.x |
| Packaging | PyInstaller + NSIS | 6.x |
| Target Hardware | Windows 10/11, 8 GB RAM, 4-core CPU, 20 GB disk | — |

### Accuracy Architecture Summary

The 99.99% accuracy target is achieved through four independent layers operating in concert: (1) document-grounded RAG preventing hallucination — every clinical claim cites a retrieved source; (2) multi-model consensus validation — two independent LLMs must agree on top differentials; (3) structured Pydantic output schemas enforced via `instructor` — malformed LLM responses are rejected and retried; (4) mandatory physician sign-off — the system never acts autonomously on a patient.

---

## SECTION 2: VISION & HUMANITARIAN MISSION

> ★ **KEY FLAGS FOR THIS SECTION**
> - 1:5,000 physician-to-patient ratio is common in humanitarian settings — this system is a force multiplier
> - No internet required for core operation — offline fallback to local model
> - Zero patient data leaves the device unless explicitly exported with encryption
> - Multilingual architecture ready (en, fr, ar locale files pre-built)
> - The system standardizes intake quality regardless of nursing skill level

### The Problem

In humanitarian settings, physician-to-patient ratios can be as low as 1:5,000. Nursing staff — the backbone of frontline care — lack structured digital tools to capture, organize, and communicate patient information in a way that maximizes the physician's limited time. A 10-minute consultation becomes an effective 2-minute consultation when the doctor receives a structured, pre-organized clinical brief. Patient history is frequently lost between visits. Drug allergies are re-asked from scratch every encounter. Red flags are missed under workload pressure.

### The Mission

MediAssist Pro is a **force multiplier for healthcare equity.** It does not replace clinical judgment — it *prepares the ground for it.* The system is built to:

1. **Reduce effective consultation time** by pre-structuring the clinical picture before the physician enters the room.
2. **Standardize intake quality** across facilities with varying nursing skill levels and staff turnover.
3. **Surface critical flags** algorithmically that might be missed during rushed intake.
4. **Preserve patient memory** across all visits, providing longitudinal continuity in settings where paper records are lost or unavailable.
5. **Support nursing education** by explaining clinical terms inline so staff grow in competence over time.
6. **Work offline** because stable internet connectivity cannot be assumed in the field.
7. **Scale to any specialty** through a configurable doctor-field module system that activates the right RAG collections, scoring tools, and question sets per station type.
8. **Respect patient dignity and privacy** by ensuring all data stays on-device by default.

### Design Ethos

- **No internet required for operation** — only NIM API calls need connectivity; full offline fallback exists with a local 7B medical model
- **Free at point of use** — open-source Python stack; only NVIDIA NIM API has a token cost
- **Multilingual-ready** — all UI strings externalized into `config/locale/{lang}.json`; currently en, fr, ar
- **Low-literacy adaptive** — every UI element has an icon alongside text; touch-screen-friendly sizing (44×44 px minimum touch targets)
- **Zero patient data leaves the device** unless the admin explicitly initiates an encrypted export
- **Physician autonomy preserved** — the system never presents a finding as a clinical conclusion, always as "preliminary AI assessment for physician review"

---

## SECTION 3: SYSTEM ARCHITECTURE OVERVIEW

> ★ **KEY FLAGS FOR THIS SECTION**
> - Single-process PySide6 desktop app with async worker threads for all LLM and DB operations
> - Main UI thread is NEVER blocked — all LLM calls run in QThread workers with Signal/Slot callbacks
> - ChromaDB and SQLite are both fully embedded — zero external server dependencies
> - Background daemon continuously processes incoming document and legacy data files during idle time
> - Physician Raw Data layer sits alongside the standard report layer — same data, two views

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        MediAssist Pro — Windows Application                   │
│                                                                               │
│  ┌───────────────────┐    ┌──────────────────────┐    ┌───────────────────┐  │
│  │  PySide6 UI Layer │◄──►│   App Controller      │◄──►│  Patient Manager  │  │
│  │  (Qt 6.x Widgets) │    │   (main_app.py)       │    │  (SQLite/ORM)     │  │
│  └───────────────────┘    └──────────┬───────────┘    └───────────────────┘  │
│                                       │                                        │
│                ┌──────────────────────┼──────────────────────┐                │
│                │                      │                       │                │
│   ┌────────────▼──────────┐  ┌───────▼──────────┐  ┌────────▼─────────────┐  │
│   │  Questionnaire Engine  │  │   RAG Pipeline   │  │   Report Generator   │  │
│   │  (Agentic 4-Round Loop)│  │  (LangChain +    │  │   (NIM + Pydantic +  │  │
│   │                        │  │   ChromaDB)      │  │    ReportLab PDF)    │  │
│   └────────────┬───────────┘  └───────┬──────────┘  └────────────────────┘   │
│                │                      │                                        │
│   ┌────────────▼──────────────────────▼────────────────────────────────────┐  │
│   │                  NVIDIA NIM API Key Pool Manager                        │  │
│   │   7 keys | Role-based routing | Load balancing | Health checks          │  │
│   └────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│   ┌─────────────────────────────────────────────────────────────────────────┐ │
│   │   Local Knowledge Base: ChromaDB — 12 specialty collections              │ │
│   │   Medical PDFs, DOCX guidelines, WHO/CDC/NIH/NICE/ACOG docs              │ │
│   └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│   ┌─────────────────────────────────────────────────────────────────────────┐ │
│   │   Physician Raw Data Layer (DOCTOR role only)                             │ │
│   │   Raw LLM JSON | Full RAG chunks | Confidence breakdown | SQL explorer    │ │
│   └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│   ┌─────────────────────────────────────────────────────────────────────────┐ │
│   │   Background Daemon: document watcher + legacy data processor             │ │
│   │   Runs during idle, processes incoming_documents/ folder                  │ │
│   └─────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow — Single Patient Session

```
[Nurse Opens App → Login with PIN/Password]
         │
         ▼
[Search Patient by Case Number / Name / DOB / Phone]
         │
    ┌────┴──────┐
    │ Found?    │
    YES         NO
    │           │
    ▼           ▼
[Load History] [Register New Patient → Auto-generate Case Number]
    │           │
    └────┬──────┘
         │
         ▼
[Select Visit Type (7 options)]
         │
         ▼
[ROUND 1: Triage + Chief Complaint MCQs]  ←── LLM: ROLE_FAST + visit_type + demographics
         │
    [Red flag?] ── YES ──► [EMERGENCY ESCALATION — print triage note, alert]
         │ NO
         ▼
[ROUND 2: Symptom Characterization — OPQRST]  ←── LLM: ROLE_STANDARD + Round1 answers + RAG
         │
         ▼
[ROUND 3: History, Medications, Allergies, Risk Factors]  ←── pre-fill from patient record
         │
         ▼
[ROUND 4: Differential Refinement — targeted discrimination Qs]  ←── LLM: ROLE_MEDICAL + top 3 differentials
         │
         ▼
[Vital Signs Capture Form — nurse enters available vitals]
         │
         ▼
[Generate Physician Brief Report — ROLE_MEDICAL + ROLE_STANDARD dual-model consensus]
[FLAGS ● DIFFERENTIALS + ICD-10/11 ● EXAM PLAN ● INVESTIGATIONS ● RAG SOURCES]
         │
    ┌────┴──────────────┐
    │                   │
    ▼                   ▼
[NURSE VIEW:        [PHYSICIAN VIEW:
 Flag summary +      Full brief + Raw data explorer +
 Print brief]        SQL query + RAG chunk viewer + sign-off]
         │
         ▼
[Save Session to SQLite — AES-256 encrypted]
         │
         ▼
[Print / Export PDF — A4 formatted]
```

### Key Architectural Decisions

| Decision | Choice | Justification |
|----------|--------|---------------|
| UI Framework | PySide6 (Qt 6.x) | Native Windows, no browser required, rich widget set, LGPL free |
| LLM Provider | NVIDIA NIM API | OpenAI-compatible API, 7 keys manageable with pool, best inference quality |
| Vector DB | ChromaDB (embedded) | Zero server, embedded, Python-native, 8 GB RAM sufficient |
| Relational DB | SQLite + SQLAlchemy | Zero server, ACID-compliant, portable, file-based backup |
| Doc Processing | PyMuPDF + pdfplumber | Best PDF fidelity; pdfplumber handles tables specifically |
| Embedding Model | `nvidia/nv-embed-v1` | 4096-dim medical text embeddings, highest quality in NIM catalog |
| Structured Output | `instructor` + Pydantic | Forces valid JSON from LLM — eliminates malformed output errors |
| Threading | QThread + asyncio | Keeps Qt UI fully responsive; LLM calls never block main thread |
| Packaging | PyInstaller + NSIS | Single `.exe` installer, no Python runtime required on target machine |

---

## SECTION 4: TECHNOLOGY STACK (COMPLETE)

> ★ **KEY FLAGS FOR THIS SECTION**
> - All versions are pinned in `requirements.txt` — no floating version specifiers
> - PySide6 requires Qt 6.7+ for full WebEngine support on Windows 10/11
> - `instructor` library is critical — without it, JSON output from NIM LLMs cannot be reliably structured
> - `pysqlcipher3` enables SQLite encryption — must be compiled with SQLCipher; Windows wheel available
> - Do NOT upgrade packages mid-development — pin versions and commit `requirements.txt`

### 4.1 Core Runtime

| Package | Version Pin | Purpose |
|---------|------------|---------|
| `PySide6` | `==6.7.2` | Primary Qt6 Windows UI framework |
| `PySide6-Charts` | `==6.7.2` | Health trend chart widgets |
| `PySide6-WebEngineWidgets` | `==6.7.2` | In-app HTML report preview panel |
| `python` | `==3.11.x` | CPython runtime (use 3.11 — 3.12 has PySide6 packaging quirks) |

### 4.2 AI & LLM Infrastructure

| Package | Version Pin | Purpose |
|---------|------------|---------|
| `openai` | `==1.51.0` | NIM API is OpenAI-compatible — primary HTTP client |
| `langchain` | `==0.3.7` | Agent orchestration, RAG chain composition |
| `langchain-community` | `==0.3.7` | Document loaders, tool integrations |
| `langchain-openai` | `==0.2.5` | LLM + Embedding connector for NIM/OpenAI |
| `instructor` | `==1.5.2` | Structured Pydantic output enforcement from LLM |
| `llama-index-core` | `==0.11.14` | Alternative RAG backend (used for hybrid search) |
| `llama-cpp-python` | `==0.3.1` | Offline local GGUF model inference |

### 4.3 Vector Database & Embeddings

| Package | Version Pin | Purpose |
|---------|------------|---------|
| `chromadb` | `==0.5.18` | Embedded local vector store — primary |
| `faiss-cpu` | `==1.8.0` | Fast similarity search fallback |
| `sentence-transformers` | `==3.2.0` | Offline embedding fallback (all-MiniLM-L6-v2) |
| `huggingface-hub` | `==0.25.1` | Model download management for offline models |

### 4.4 Document Processing

| Package | Version Pin | Purpose |
|---------|------------|---------|
| `pymupdf` | `==1.24.11` | Primary PDF text + image extraction |
| `pdfplumber` | `==0.11.4` | Table-heavy PDF extraction |
| `python-docx` | `==1.1.2` | DOCX guideline processing |
| `openpyxl` | `==3.1.5` | Excel vaccination records + drug tables |
| `pytesseract` | `==0.3.13` | OCR for scanned documents |
| `Pillow` | `==10.4.0` | Image preprocessing for OCR pipeline |
| `ebooklib` | `==0.18` | EPUB medical textbook support |
| `chardet` | `==5.2.0` | Encoding detection for legacy text files |
| `pandas` | `==2.2.3` | CSV/structured data import + manipulation |
| `hl7apy` | `==1.3.4` | HL7 v2 message parsing (ADT, ORU, OBX) |

### 4.5 Database & Storage

| Package | Version Pin | Purpose |
|---------|------------|---------|
| `sqlalchemy` | `==2.0.35` | ORM layer — all DB access goes through this |
| `alembic` | `==1.13.3` | Database schema migrations |
| `pysqlcipher3` | `==1.0.3` | AES-256 SQLite encryption (SQLCipher) |
| `cryptography` | `==43.0.1` | AES-256-GCM for file exports |
| `keyring` | `==25.4.1` | Windows Credential Manager integration for key storage |
| `argon2-cffi` | `==23.1.0` | Argon2id password hashing |

### 4.6 Utilities & Cross-Cutting Concerns

| Package | Version Pin | Purpose |
|---------|------------|---------|
| `pydantic` | `==2.9.2` | Data validation, output schemas |
| `pydantic-settings` | `==2.5.2` | Settings management from env/files |
| `httpx` | `==0.27.2` | Async HTTP client |
| `tenacity` | `==9.0.0` | LLM API retry with exponential backoff |
| `loguru` | `==0.7.2` | Structured logging to file + console |
| `rich` | `==13.8.1` | Console debug output |
| `jinja2` | `==3.1.4` | HTML report template rendering |
| `reportlab` | `==4.2.4` | PDF generation for physician briefs |
| `pyinstaller` | `==6.10.0` | Windows .exe packaging |
| `watchdog` | `==5.0.3` | Filesystem monitoring for incoming documents |
| `schedule` | `==1.2.2` | Background task scheduling |
| `psutil` | `==6.1.0` | System resource monitoring |
| `pywin32` | `==308` | Windows API access (notifications, DPAPI) |
| `win10toast` | `==0.9` | Windows 10/11 system notifications |

### 4.7 Testing

| Package | Version Pin | Purpose |
|---------|------------|---------|
| `pytest` | `==8.3.3` | Primary test runner |
| `pytest-asyncio` | `==0.24.0` | Async test support |
| `pytest-qt` | `==4.4.0` | Qt UI component testing |
| `hypothesis` | `==6.112.1` | Property-based / fuzz testing |
| `faker` | `==30.3.0` | Synthetic patient data generation |
| `pytest-cov` | `==5.0.0` | Coverage measurement |
| `responses` | `==0.25.3` | HTTP mock for NIM API call testing |

### 4.8 requirements.txt Structure

```text
# requirements.txt — generated by: pip freeze > requirements.txt after venv install
# Pin ALL versions. No ~= or >= specifiers.

PySide6==6.7.2
PySide6-Charts==6.7.2
PySide6-WebEngineWidgets==6.7.2
openai==1.51.0
langchain==0.3.7
langchain-community==0.3.7
langchain-openai==0.2.5
instructor==1.5.2
llama-index-core==0.11.14
llama-cpp-python==0.3.1
chromadb==0.5.18
faiss-cpu==1.8.0
sentence-transformers==3.2.0
huggingface-hub==0.25.1
pymupdf==1.24.11
pdfplumber==0.11.4
python-docx==1.1.2
openpyxl==3.1.5
pytesseract==0.3.13
Pillow==10.4.0
ebooklib==0.18
chardet==5.2.0
pandas==2.2.3
hl7apy==1.3.4
sqlalchemy==2.0.35
alembic==1.13.3
pysqlcipher3==1.0.3
cryptography==43.0.1
keyring==25.4.1
argon2-cffi==23.1.0
pydantic==2.9.2
pydantic-settings==2.5.2
httpx==0.27.2
tenacity==9.0.0
loguru==0.7.2
rich==13.8.1
jinja2==3.1.4
reportlab==4.2.4
watchdog==5.0.3
schedule==1.2.2
psutil==6.1.0
pywin32==308
win10toast==0.9
```

---

## SECTION 5: NVIDIA NIM API STRATEGY — 7-KEY MANAGEMENT & MODEL GUIDE

> ★ **KEY FLAGS FOR THIS SECTION**
> - NIM API base URL: `https://integrate.api.nvidia.com/v1` — fully OpenAI-SDK compatible
> - Key 1 dedicated to embeddings/reranking (high-frequency, small payload calls)
> - Key 7 reserved exclusively for ROLE_COMPLEX (rare edge cases, multi-system disease)
> - Keys 3+4 and Keys 5+6 are primary pools for standard and medical reasoning respectively
> - If all 7 keys are exhausted: offline fallback to BioMistral-7B GGUF model automatically activates
> - API keys stored encrypted via Windows DPAPI — never in plaintext, never in logs, never in UI
> - Temperature: always 0.1 for medical outputs — never above 0.3

### 5.1 NIM API Base Initialization

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="<KEY_FROM_POOL>",
    timeout=45.0,
    max_retries=0   # Retry logic handled externally by Tenacity
)
```

### 5.2 Model Catalog & Role Assignment (2025/2026 NIM Catalog)

| Role ID | NIM Model String | Parameter Size | Assigned Keys | Primary Use Case |
|---------|-----------------|---------------|--------------|-----------------|
| `ROLE_EMBED` | `nvidia/nv-embed-v1` | Embedding (4096-dim) | Key 1 | Document + query embeddings for all RAG retrieval |
| `ROLE_RERANK` | `nvidia/nv-rerank-qa-mistral-4b:1` | 4B | Key 1 (shared) | Re-ranking top-15 retrieved chunks to top-5 |
| `ROLE_FAST` | `meta/llama-3.3-8b-instruct` | 8B | Key 2 | MCQ option generation, ICD code lookup, fast classification |
| `ROLE_STANDARD` | `meta/llama-3.3-70b-instruct` | 70B | Keys 3 + 4 | Questionnaire rounds 1–3, history analysis, structured history |
| `ROLE_MEDICAL` | `nvidia/llama-3.1-nemotron-70b-instruct` | 70B | Keys 5 + 6 | Primary clinical reasoning, differential diagnosis generation |
| `ROLE_COMPLEX` | `nvidia/nemotron-4-340b-instruct` | 340B | Key 7 | Rare presentations, multi-system disease, complex pediatric/geriatric cases |
| `ROLE_FALLBACK` | `mistralai/mixtral-8x7b-instruct-v0.1` | 56B MoE | Keys 3 or 5 (overflow) | Overflow fallback when primary pool keys are rate-limited |

**Model Selection Decision Logic:**
```
MCQ option generation, fast lookups, ICD code assignment → ROLE_FAST (fastest, cheapest)
Questionnaire rounds 1, 2, 3 → ROLE_STANDARD
Differential generation, physician brief → ROLE_MEDICAL (Nemotron — best reasoning)
Consensus validation (second opinion) → ROLE_STANDARD validates ROLE_MEDICAL output
Multi-system, rare disease, complex cases → ROLE_COMPLEX (340B only when needed)
All embedding operations → ROLE_EMBED (Key 1, dedicated)
All reranking operations → ROLE_RERANK (Key 1, dedicated)
Overflow when Keys 3/4/5/6 throttle → ROLE_FALLBACK
```

### 5.3 7-Key Pool Manager — Full Implementation

```python
# nim/nim_key_manager.py

import time
import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from loguru import logger
import httpx

class ModelRole(Enum):
    EMBED    = "embed"
    RERANK   = "rerank"
    FAST     = "fast"
    STANDARD = "standard"
    MEDICAL  = "medical"
    COMPLEX  = "complex"
    FALLBACK = "fallback"

ROLE_MODEL_MAP: dict[ModelRole, str] = {
    ModelRole.EMBED:    "nvidia/nv-embed-v1",
    ModelRole.RERANK:   "nvidia/nv-rerank-qa-mistral-4b:1",
    ModelRole.FAST:     "meta/llama-3.3-8b-instruct",
    ModelRole.STANDARD: "meta/llama-3.3-70b-instruct",
    ModelRole.MEDICAL:  "nvidia/llama-3.1-nemotron-70b-instruct",
    ModelRole.COMPLEX:  "nvidia/nemotron-4-340b-instruct",
    ModelRole.FALLBACK: "mistralai/mixtral-8x7b-instruct-v0.1",
}

ROLE_KEY_AFFINITY: dict[ModelRole, list[int]] = {
    ModelRole.EMBED:    [0],       # Key index 0 = Key 1
    ModelRole.RERANK:   [0],       # Key 1 (shared with EMBED)
    ModelRole.FAST:     [1],       # Key 2
    ModelRole.STANDARD: [2, 3],    # Keys 3, 4
    ModelRole.MEDICAL:  [4, 5],    # Keys 5, 6
    ModelRole.COMPLEX:  [6],       # Key 7 (reserved)
    ModelRole.FALLBACK: [2, 4],    # Keys 3 or 5 for overflow
}

@dataclass
class APIKey:
    key_id: int
    value: str
    roles: list[ModelRole]
    calls_this_minute: int = 0
    calls_this_day: int = 0
    last_reset_minute: float = field(default_factory=time.time)
    is_healthy: bool = True
    cooldown_until: float = 0.0
    total_errors: int = 0

    def is_available(self, per_minute_limit: int = 50) -> bool:
        now = time.time()
        if now < self.cooldown_until:
            return False
        if now - self.last_reset_minute > 60:
            self.calls_this_minute = 0
            self.last_reset_minute = now
        return self.is_healthy and self.calls_this_minute < per_minute_limit

    def consume(self):
        self.calls_this_minute += 1
        self.calls_this_day += 1

class NIMKeyManager:
    """
    Manages 7 NIM API keys with role-based routing, rate limiting,
    automatic failover, health monitoring, and offline fallback detection.
    """

    def __init__(self, raw_keys: list[str]):
        assert len(raw_keys) == 7, "Exactly 7 NIM API keys required"
        self.keys: list[APIKey] = [
            APIKey(
                key_id=i,
                value=k,
                roles=[role for role, ids in ROLE_KEY_AFFINITY.items() if i in ids]
            )
            for i, k in enumerate(raw_keys)
        ]
        self._offline_mode = False

    def get_key_for_role(self, role: ModelRole) -> Optional[APIKey]:
        """Returns best available key for role. Attempts fallback chain."""
        affinity_ids = ROLE_KEY_AFFINITY[role]
        candidates = [self.keys[i] for i in affinity_ids if self.keys[i].is_available()]
        if not candidates:
            # Try fallback pool
            fallback_ids = ROLE_KEY_AFFINITY[ModelRole.FALLBACK]
            candidates = [self.keys[i] for i in fallback_ids if self.keys[i].is_available()]
        if not candidates:
            # All keys exhausted — trigger offline mode
            self._offline_mode = True
            logger.warning("ALL NIM API KEYS EXHAUSTED — switching to offline mode")
            return None
        key = min(candidates, key=lambda k: k.calls_this_minute)
        key.consume()
        return key

    def get_model_for_role(self, role: ModelRole) -> str:
        if self._offline_mode:
            return "offline:biomistral-7b"
        return ROLE_MODEL_MAP[role]

    def mark_key_unhealthy(self, key_id: int, cooldown_seconds: int = 120):
        self.keys[key_id].is_healthy = False
        self.keys[key_id].cooldown_until = time.time() + cooldown_seconds
        self.keys[key_id].total_errors += 1
        logger.warning(f"Key {key_id} marked unhealthy for {cooldown_seconds}s")

    def is_offline(self) -> bool:
        return self._offline_mode

    def health_status(self) -> dict:
        return {
            "offline_mode": self._offline_mode,
            "keys": [
                {
                    "key_id": k.key_id,
                    "available": k.is_available(),
                    "calls_today": k.calls_this_day,
                    "errors": k.total_errors
                }
                for k in self.keys
            ]
        }
```

### 5.4 Encrypted Key Storage

Keys are encrypted and stored at `%APPDATA%\MediAssistPro\keys.enc` using Windows DPAPI (Data Protection API) via the `keyring` library. The setup wizard (Section 16.3) collects all 7 keys on first run, encrypts them with a device-bound key, and stores the result. Keys are decrypted at application startup into memory and never written to disk in plaintext. Keys never appear in any log output (the logger configuration strips all strings matching the NIM key pattern: `^nvapi-[a-zA-Z0-9]{48}$`).

### 5.5 Offline Fallback — Local Medical LLM

When all NIM keys are unavailable, the system activates local inference:

- **Model:** `MaziyarPanahi/BioMistral-7B-DARE-GGUF` Q4_K_M quantization (~4.1 GB)
- **Runtime:** `llama-cpp-python` — no GPU required, runs on CPU
- **Download:** Included in installer or downloaded on first setup to `models/biomistral-7b.gguf`
- **UI indicator:** Persistent orange banner: "⚠ OFFLINE MODE — Reduced accuracy. All outputs require heightened physician scrutiny."
- **RAG pipeline:** Continues to function fully — ChromaDB is 100% local
- **Accuracy note:** Offline outputs should be treated as preliminary only; multi-model consensus is not available

---

## SECTION 6: DOCUMENT MANAGEMENT & RAG PIPELINE

> ★ **KEY FLAGS FOR THIS SECTION**
> - RAG is the accuracy backbone — it prevents LLM hallucination by grounding every clinical claim in an uploaded source document
> - Minimum cosine similarity threshold of 0.75 for a chunk to enter LLM context — below threshold triggers "Insufficient knowledge" warning
> - 12 specialty ChromaDB collections — each visit type maps to 2–4 collections simultaneously
> - Background daemon auto-ingests new documents placed in `knowledge_base/incoming/` during idle time
> - Document subscriptions allow facility admins to subscribe to guideline URLs that auto-update
> - Chunk size 800 tokens with 120-token overlap balances context coherence and retrieval precision

### 6.1 RAG Pipeline Architecture

```
[Document Upload via Admin UI / Drop into incoming/ folder]
         │
         ▼
[File Type Detector — by extension + magic bytes]
   .pdf  → PyMuPDF primary; pdfplumber fallback for tables
   .docx → python-docx
   .txt  → direct UTF-8 read
   .epub → EbookLib
   .xlsx → openpyxl (vaccine schedules, drug reference tables)
   .jpg/.png/.tiff → Pillow → Pytesseract OCR → text
         │
         ▼
[Text Chunker — RecursiveCharacterTextSplitter]
   chunk_size = 800 tokens | overlap = 120 tokens
   separator hierarchy: ["\n\n", "\n", ".", " "]
         │
         ▼
[Metadata Extractor — attached to each chunk]
   {source_file, page_number, section_title, document_type,
    specialty_tags: list[str], ingestion_date, chunk_index}
         │
         ▼
[NIM Embedding — nvidia/nv-embed-v1 via Key 1]
   Batch size: 32 chunks per API call
   Output dimension: 4096
         │
         ▼
[ChromaDB PersistentClient — 12 specialty collections]
   Deduplication: hash-based, skip if chunk already exists
         │
         ▼
[On Query: Top-k=15 retrieval → NIM Reranker → Top-5 for LLM prompt]
```

### 6.2 ChromaDB Collection Map

| Collection Name | Document Types Stored | Mapped Specialties |
|----------------|----------------------|-------------------|
| `core_medicine` | Harrison's, Oxford Handbook, Cecil, Kumar & Clark | General, Internal Medicine, Emergency |
| `who_guidelines` | WHO clinical protocols, IMAI, IMCI, mhGAP | All specialties |
| `cdc_guidelines` | CDC vaccination schedules, infection control guidelines | All specialties |
| `nih_guidelines` | NIH treatment protocols, rare disease guides, MedlinePlus | Internal Medicine, Oncology |
| `nice_guidelines` | NICE (UK) clinical pathways | General, Psychiatry, Cardiology |
| `pediatrics` | Nelson's Textbook, IAP guidelines, AAP protocols | Pediatrics |
| `ob_gyn` | Williams Obstetrics, ACOG, FIGO guidelines | Obstetrics & Gynecology |
| `emergency` | Tintinalli's, ATLS, ERC guidelines | Emergency Medicine |
| `pharmacology` | BNF, WHO Essential Medicines List, drug interaction databases | All specialties |
| `vaccination` | EPI schedules, WHO vaccine position papers, cold-chain protocols | Pediatrics, General |
| `surgery_orthopedics` | ACS guidelines, Apley's Orthopaedics, surgical protocols | Surgery, Orthopedics |
| `local_protocols` | Facility-specific uploaded SOPs and protocols | Facility-specific |

### 6.3 DocumentManager — Complete Implementation

```python
# rag/document_manager.py

from pathlib import Path
import hashlib
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from loguru import logger
from nim.nim_key_manager import NIMKeyManager, ModelRole

class DocumentManager:
    CHUNK_SIZE    = 800
    CHUNK_OVERLAP = 120
    TOP_K_RETRIEVE = 15
    TOP_K_RERANK   = 5
    MIN_SIMILARITY = 0.75

    def __init__(self, key_manager: NIMKeyManager, db_path: str):
        self.key_manager = key_manager
        self.chroma = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.CHUNK_SIZE,
            chunk_overlap=self.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ".", " "]
        )

    def _get_embedder(self) -> OpenAIEmbeddings:
        key = self.key_manager.get_key_for_role(ModelRole.EMBED)
        return OpenAIEmbeddings(
            model=self.key_manager.get_model_for_role(ModelRole.EMBED),
            api_key=key.value,
            base_url="https://integrate.api.nvidia.com/v1",
            dimensions=4096
        )

    def _chunk_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def ingest_document(self, file_path: str, collection: str,
                         specialty_tags: list[str] = None,
                         document_type: str = "guideline") -> dict:
        path = Path(file_path)
        loader_map = {".pdf": PyMuPDFLoader, ".docx": Docx2txtLoader, ".txt": TextLoader}
        loader_cls = loader_map.get(path.suffix.lower())
        if not loader_cls:
            raise ValueError(f"Unsupported file type: {path.suffix}")

        docs   = loader_cls(str(path)).load()
        chunks = self.splitter.split_documents(docs)
        texts, metas, ids = [], [], []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{path.stem}_{i}_{self._chunk_hash(chunk.page_content)}"
            chunk.metadata.update({
                "source_file":    path.name,
                "document_type":  document_type,
                "specialty_tags": ",".join(specialty_tags or []),
                "chunk_index":    i,
                "chunk_id":       chunk_id
            })
            texts.append(chunk.page_content)
            metas.append(chunk.metadata)
            ids.append(chunk_id)

        embedder   = self._get_embedder()
        embeddings = embedder.embed_documents(texts)
        col = self.chroma.get_or_create_collection(collection)
        col.upsert(documents=texts, embeddings=embeddings, metadatas=metas, ids=ids)
        logger.info(f"Ingested {len(chunks)} chunks from {path.name} → {collection}")
        return {"chunks_added": len(chunks), "collection": collection, "source": path.name}

    def retrieve(self, query: str, collections: list[str], n_results: int = None) -> list[dict]:
        n   = n_results or self.TOP_K_RETRIEVE
        emb = self._get_embedder()
        q_embedding = emb.embed_query(query)
        all_results = []

        for col_name in collections:
            try:
                col = self.chroma.get_collection(col_name)
                res = col.query(query_embeddings=[q_embedding],
                                n_results=min(n, col.count()))
                for doc, meta, dist in zip(res["documents"][0],
                                           res["metadatas"][0],
                                           res["distances"][0]):
                    # Filter by minimum similarity (convert distance to similarity)
                    similarity = 1.0 - dist
                    if similarity >= self.MIN_SIMILARITY:
                        all_results.append({
                            "text": doc, "metadata": meta,
                            "similarity": round(similarity, 4),
                            "collection": col_name
                        })
            except Exception as e:
                logger.warning(f"Collection {col_name} retrieval error: {e}")
                continue

        sorted_results = sorted(all_results, key=lambda x: x["similarity"], reverse=True)
        return sorted_results[:n]

    def get_stats(self) -> dict:
        """Returns collection sizes for admin dashboard."""
        stats = {}
        for col in self.chroma.list_collections():
            stats[col.name] = col.count()
        return stats
```

### 6.4 Background Document Processor Daemon

The `BackgroundProcessor` thread runs when no active nurse session is in progress. It monitors `knowledge_base/incoming/` using `watchdog`, ingests new files, and processes legacy patient data imports (see Section 21). It also validates all existing ChromaDB collections and re-indexes any stale or failed chunks. Processed files move to `knowledge_base/processed/`. Failed files move to `knowledge_base/failed/` with an error log entry.

---

## SECTION 7: AGENTIC QUESTIONNAIRE ENGINE (CORE)

> ★ **KEY FLAGS FOR THIS SECTION**
> - Every question set is generated fresh by LLM per patient — there are NO static question forms
> - The engine is a four-round state machine: Triage → Symptom Detail → History → Differential Refinement
> - Red flag detection runs on every answer in real time — any positive flag triggers immediate emergency escalation
> - The `instructor` library enforces strict JSON schema compliance — malformed LLM output triggers automatic retry (max 3 attempts)
> - Nurse explanation tooltips are mandatory for any term in the `medical_terms.json` dictionary
> - Body map SVG selector is available for all location-type questions
> - The engine operates for ALL 21 medical specialties — round content differs but structure is identical

### 7.1 Engine Philosophy

The Questionnaire Engine is the most critical component of MediAssist Pro. It operates as a **multi-round agentic loop**: each round of questions is generated dynamically by an LLM that receives full context of: (1) patient demographics, (2) visit type, (3) specialty configuration, (4) all previous answers from prior rounds, (5) RAG-retrieved clinical context relevant to the current symptom profile, and (6) the current working differential hypothesis being refined. The system holds full session state in memory across all rounds.

### 7.2 Visit Type Priming Matrix

| Visit Type | RAG Collections Used | Primary LLM Role | Notes |
|-----------|---------------------|-----------------|-------|
| `VACCINATION` | `vaccination`, `cdc_guidelines`, `who_guidelines` | `ROLE_FAST` | Focus on schedule, contraindications, adverse events |
| `GENERAL` | `core_medicine`, `who_guidelines`, `pharmacology` | `ROLE_STANDARD` | Broad symptom sweep + preventive care screen |
| `SPECIFIC` | `core_medicine` + specialty collection + `who_guidelines` | `ROLE_MEDICAL` | Symptom-driven, deepest differential work |
| `FOLLOWUP` | `core_medicine` + patient's historical visit data | `ROLE_STANDARD` | Compare to prior visit; assess treatment response |
| `MATERNAL` | `ob_gyn`, `who_guidelines` | `ROLE_MEDICAL` | EPDS screen, fetal movement, ANC milestones |
| `PEDIATRIC` | `pediatrics`, `vaccination`, `cdc_guidelines` | `ROLE_MEDICAL` | Weight-based context, developmental milestones, growth percentiles |
| `MENTAL` | `core_medicine` (psychiatry), `nice_guidelines`, `who_guidelines` (mhGAP) | `ROLE_MEDICAL` | PHQ-9, GAD-7, suicide risk screen embedded in rounds |

### 7.3 Four-Round Algorithm — Detailed Specification

#### ROUND 1 — Triage & Chief Complaint
**Goal:** Identify the primary presenting concern, detect emergencies, establish basic context.
**LLM Task:** Generate 6–8 MCQ questions using `ROLE_FAST`.
**Mandatory questions always generated (regardless of visit type):**
- Primary presenting complaint — symptom picker: 30+ options grouped by body system, plus "Other (nurse describe)"
- Duration of current complaint — date picker or duration selector
- Severity scale — visual analog: None / Mild / Moderate / Severe / Unbearable
- Functional impact — "Is this affecting daily activities?" → Not at all / Slightly / Significantly / Cannot function
- Emergency red flag screen — 10 binary checkboxes (see below)

**Emergency Red Flags — Any positive triggers immediate escalation:**

| Flag | Clinical Concern |
|------|----------------|
| Chest pain + shortness of breath | ACS, PE, aortic dissection |
| Sudden loss of consciousness | Cardiac arrest, seizure, severe hypoglycemia |
| Signs of stroke: facial droop, arm weakness, speech difficulty | CVA — FAST protocol |
| Severe uncontrolled bleeding | Hemorrhagic shock |
| High fever + neck stiffness + rash | Bacterial meningitis, meningococcemia |
| Pediatric: fever > 38°C in infant under 3 months | Serious bacterial infection |
| Obstetric: heavy vaginal bleeding in pregnancy | Antepartum hemorrhage, miscarriage |
| Obstetric: absent fetal movement > 24 hours in third trimester | Fetal distress / stillbirth |
| Severe allergic reaction: throat swelling, hives, hypotension | Anaphylaxis |
| Severe difficulty breathing with cyanosis or SpO2 < 90% | Respiratory failure |

#### ROUND 2 — Symptom Characterization (OPQRST + SAMPLER)
**Goal:** Fully characterize the chief complaint using validated clinical frameworks.
**LLM Task:** Generate 8–12 targeted MCQs adapted to Round 1 responses + RAG context from 2–3 relevant specialty collections.

```
OPQRST Framework (encoded into question types):
  O — Onset:     "Did this start suddenly (seconds/minutes) or gradually (days/weeks)?"
  P — Provocation/Palliation: "What makes it worse?" / "What makes it better?"
  Q — Quality:   "How would you describe the sensation?"
                 Options vary by symptom: pain → stabbing/burning/aching/pressure/cramping/
                 throbbing/constant/shooting; breathing → tight/wheeze/heavy/cannot complete sentence
  R — Region/Radiation: Body diagram SVG picker — click to mark location(s)
  S — Severity:  0–10 slider + functional impact
  T — Time:      Duration / Frequency / Pattern (constant/intermittent/episodic/worsening/improving)

SAMPLER (partial — rest in Round 3):
  L — Last oral intake:    relevant for potential surgical/procedural cases
  E — Events leading up:   "Did anything happen before this started?" — trauma, travel, sick contacts
```

#### ROUND 3 — Medical History, Medications, Allergies, Risk Factors
**Goal:** Gather PMH, medications, allergies, family history, social history, and relevant review of systems.
**LLM Task:** Generate 8–10 MCQs. Fields pre-populated from the patient database record (known conditions, current meds, allergies).

Auto-populated from patient SQLite record when patient is existing:
- Known chronic conditions (auto-filled checkboxes for nurse to confirm)
- Current medications (pre-listed; nurse confirms still taking + checks for new additions)
- Known drug allergies (pre-listed + option to add)
- Vaccination status (auto-loaded from vaccination table, highlights gaps)
- Prior surgeries and hospitalizations

Dynamically generated additional questions (based on Round 2 differentials):
- Relevant family history for top differentials
- Social history: smoking, alcohol use, occupation, recent travel
- Review of systems for organ systems implicated in the working differentials

#### ROUND 4 — Differential Refinement
**Goal:** The LLM has now formed 3–5 working differentials. Round 4 asks discriminating questions to rank them with clinical precision.
**LLM Task:** Generate 6–8 highly targeted discriminating questions using `ROLE_MEDICAL`.
**Context injected:** Top 3–5 working differentials from Round 3 analysis + RAG chunks specific to differentiating those conditions.

The LLM receives an explicit instruction:
> "You have formed the following working differentials: [LIST]. Generate exactly 7 questions that will maximally discriminate between these conditions. For each question, specify which answer options increase probability for which differential."

### 7.4 Complete Pydantic Schemas

```python
# models/questionnaire.py

from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

class OptionType(str, Enum):
    RADIO    = "radio"       # Single select
    CHECKBOX = "checkbox"    # Multi-select
    SCALE    = "scale"       # 0–10 slider
    BODY_MAP = "body_map"    # SVG anatomical location picker
    TEXT     = "text"        # Free nurse note (short)
    DATE     = "date"        # Date picker
    DURATION = "duration"    # Duration selector (hours/days/weeks/months)

class MCQOption(BaseModel):
    id:        str
    label:     str
    is_red_flag:   bool = False   # If selected → RED clinical flag
    is_amber_flag: bool = False   # If selected → AMBER flag
    differential_indicator: Optional[str] = None  # Which differential this supports

class Question(BaseModel):
    question_id:      str
    round:            int  # 1–4
    text:             str
    type:             OptionType
    options:          Optional[list[MCQOption]] = None
    nurse_explanation: Optional[str] = None  # Plain-language explanation shown via ℹ button
    is_mandatory:     bool = True
    body_map_region:  Optional[str] = None   # Which SVG body region to pre-highlight
    triggers_followup: Optional[str] = None  # question_id of conditional follow-up

class QuestionnaireRound(BaseModel):
    round_number:       int
    visit_type:         str
    specialty:          str
    questions:          list[Question]
    rag_context_used:   list[str]   # Source document titles cited
    rag_chunk_ids:      list[str]   # Raw chunk IDs for physician raw data access
    model_used:         str
    generation_time_ms: int
    working_differentials: Optional[list[str]] = None  # Rounds 3–4 only

class SessionAnswers(BaseModel):
    """Accumulated answers across all rounds — passed as context to each subsequent round."""
    round_1: Optional[dict] = None
    round_2: Optional[dict] = None
    round_3: Optional[dict] = None
    round_4: Optional[dict] = None
    vital_signs: Optional[dict] = None
    flags_raised: list[str] = []
```

### 7.5 Session State Machine

```
STATES:
  IDLE → PATIENT_LOADED → VISIT_TYPE_SELECTED →
  ROUND_1_GENERATING → ROUND_1_ACTIVE → ROUND_1_SUBMITTED →
  ROUND_2_GENERATING → ROUND_2_ACTIVE → ROUND_2_SUBMITTED →
  ROUND_3_GENERATING → ROUND_3_ACTIVE → ROUND_3_SUBMITTED →
  ROUND_4_GENERATING → ROUND_4_ACTIVE → ROUND_4_SUBMITTED →
  VITALS_CAPTURE → REPORT_GENERATING → REPORT_READY → SAVED

  Any state → EMERGENCY: if any red flag positive in any round
  Any state → IDLE: on "Cancel Session" or "New Patient"
  REPORT_READY → PHYSICIAN_VIEW: on physician login + session access
```

### 7.6 Vital Signs Capture Form

After Round 4 and before report generation, a structured vital signs form is shown to the nurse:

```python
class VitalSigns(BaseModel):
    systolic_bp:   Optional[int]   = None   # mmHg
    diastolic_bp:  Optional[int]   = None   # mmHg
    heart_rate:    Optional[int]   = None   # bpm
    respiratory_rate: Optional[int] = None  # breaths/min
    spo2:          Optional[float] = None   # %
    temperature_c: Optional[float] = None   # Celsius
    weight_kg:     Optional[float] = None   # kg
    height_cm:     Optional[float] = None   # cm — BMI auto-calculated
    avpu:          Optional[str]   = None   # Alert/Voice/Pain/Unresponsive
    pain_scale:    Optional[int]   = None   # 0–10
    blood_glucose: Optional[float] = None   # mmol/L (if glucometer available)
    # Auto-calculated from weight + height:
    bmi:           Optional[float] = None
```

Any vital sign outside normal range automatically adds a clinical flag to the physician brief. Age-appropriate normal ranges are loaded from `config/vital_sign_norms.json` (separate norms for pediatric age bands, adults, elderly, pregnancy).

---

## SECTION 8: PATIENT MANAGEMENT SYSTEM

> ★ **KEY FLAGS FOR THIS SECTION**
> - Case number format: `{FACILITY_CODE}-{YYYY}-{NNNN}` — facility code set during first-run wizard
> - Patient search: by case number (exact), name (fuzzy with Levenshtein distance ≤ 2), phone (exact), DOB (exact)
> - All historical visits, vaccinations, chronic conditions, medications, allergies auto-loaded at session start
> - Vaccination tracker calculates overdue vaccines per EPI schedule and age
> - Physician can query any table directly via the raw data SQL explorer in the physician dashboard
> - Soft deletion only — patients are never hard-deleted; records are marked `is_active = False`

### 8.1 Complete SQLite Schema

```sql
-- Auto-generated by SQLAlchemy/Alembic — do not edit manually

CREATE TABLE patients (
    id             INTEGER  PRIMARY KEY AUTOINCREMENT,
    case_number    TEXT     UNIQUE NOT NULL,   -- e.g. "CHC-2025-0001"
    first_name     TEXT     NOT NULL,
    last_name      TEXT     NOT NULL,
    date_of_birth  DATE     NOT NULL,
    sex            TEXT     NOT NULL CHECK(sex IN ('M','F','O','U')),
    blood_group    TEXT,
    contact_number TEXT,
    guardian_name  TEXT,     -- for pediatric patients
    guardian_relation TEXT,
    address        TEXT,
    national_id    TEXT,     -- optional, encrypted at rest
    facility_code  TEXT,
    is_active      BOOLEAN  DEFAULT TRUE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by     TEXT
);

CREATE TABLE visits (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number          TEXT    REFERENCES patients(case_number),
    visit_date           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    visit_type           TEXT    NOT NULL,
    specialty            TEXT,
    questionnaire_rounds JSON,   -- complete Q&A for each round (rounds 1–4)
    vital_signs          JSON,
    flags                JSON,   -- list of ClinicalFlag objects
    differentials        JSON,   -- list of DifferentialDiagnosis objects
    report_text          TEXT,
    report_pdf_path      TEXT,
    raw_llm_responses    JSON,   -- stored for physician raw data access
    raw_rag_chunks       JSON,   -- stored for physician raw data access
    confidence_score     REAL,
    nurse_id             TEXT,
    doctor_id            TEXT,
    doctor_signed_off    BOOLEAN  DEFAULT FALSE,
    doctor_notes         TEXT,
    is_emergency         BOOLEAN  DEFAULT FALSE,
    is_closed            BOOLEAN  DEFAULT FALSE,
    notes                TEXT
);

CREATE TABLE vaccinations (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number       TEXT REFERENCES patients(case_number),
    vaccine_name      TEXT NOT NULL,
    vaccine_batch     TEXT,
    administered_date DATE,
    administered_by   TEXT,
    due_date          DATE,
    dose_number       INTEGER,
    dose_series       TEXT,    -- e.g. "DPT-1", "DPT-2", "DPT-3"
    site              TEXT,    -- IM left/right deltoid, SC, oral
    adverse_events    TEXT,
    source            TEXT     DEFAULT 'manual'  -- 'manual', 'import', 'ehr'
);

CREATE TABLE chronic_conditions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number     TEXT REFERENCES patients(case_number),
    condition_name  TEXT,
    icd_10_code     TEXT,
    icd_11_code     TEXT,
    diagnosed_date  DATE,
    status          TEXT CHECK(status IN ('active','remission','resolved','suspected')),
    notes           TEXT
);

CREATE TABLE medications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number     TEXT REFERENCES patients(case_number),
    drug_name       TEXT,
    generic_name    TEXT,
    dose            TEXT,
    frequency       TEXT,
    route           TEXT,
    start_date      DATE,
    end_date        DATE,
    prescribed_for  TEXT,
    prescriber      TEXT,
    is_current      BOOLEAN DEFAULT TRUE
);

CREATE TABLE allergies (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number     TEXT REFERENCES patients(case_number),
    allergen        TEXT,
    allergy_type    TEXT CHECK(allergy_type IN ('drug','food','environmental','latex','contrast','other')),
    reaction_type   TEXT,
    severity        TEXT CHECK(severity IN ('mild','moderate','severe','anaphylaxis')),
    date_noted      DATE,
    verified_by     TEXT
);

CREATE TABLE lab_results (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number     TEXT REFERENCES patients(case_number),
    visit_id        INTEGER REFERENCES visits(id),
    test_name       TEXT,
    test_code       TEXT,    -- LOINC code if available
    result_value    TEXT,
    unit            TEXT,
    reference_range TEXT,
    interpretation  TEXT CHECK(interpretation IN ('normal','low','high','critical','pending')),
    result_date     DATE,
    ordered_by      TEXT,
    lab_name        TEXT
);

CREATE TABLE users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    UNIQUE NOT NULL,
    display_name    TEXT,
    role            TEXT    CHECK(role IN ('NURSE','DOCTOR','ADMIN','SUPERADMIN')),
    password_hash   TEXT    NOT NULL,   -- Argon2id
    facility_code   TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    last_login      TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id         TEXT,
    action          TEXT,
    case_number     TEXT,
    details         JSON,
    model_used      TEXT,
    api_key_id      INTEGER,   -- key index only, not value
    duration_ms     INTEGER,
    confidence_score REAL
);
-- audit_log is append-only: no UPDATE/DELETE triggers enforced
```

### 8.2 Case Number Generator

```python
# patient/case_number.py

import datetime
from sqlalchemy.orm import Session
from models.db_models import Patient

def generate_case_number(session: Session, facility_code: str = "MC") -> str:
    """Thread-safe case number in format: MC-2025-0001. Resets counter per year."""
    year   = datetime.datetime.now().year
    prefix = f"{facility_code}-{year}-"

    last = (
        session.query(Patient)
        .filter(Patient.case_number.like(f"{prefix}%"))
        .order_by(Patient.case_number.desc())
        .first()
    )
    new_num = (int(last.case_number.split("-")[-1]) + 1) if last else 1
    return f"{prefix}{new_num:04d}"
```

### 8.3 Patient History Context Builder

When an existing patient is loaded, `history_loader.py` assembles a structured context dict that is injected into every LLM prompt in subsequent rounds:

```python
def build_patient_context(case_number: str, session: Session) -> dict:
    """Assembles full patient history as LLM-ready context dict."""
    patient = session.query(Patient).filter_by(case_number=case_number).first()
    visits  = session.query(Visit).filter_by(case_number=case_number) \
                     .order_by(Visit.visit_date.desc()).limit(5).all()
    return {
        "demographics": {
            "age_years": calculate_age(patient.date_of_birth),
            "sex": patient.sex,
            "blood_group": patient.blood_group
        },
        "chronic_conditions": [c.condition_name for c in patient.chronic_conditions if c.status == "active"],
        "current_medications": [f"{m.drug_name} {m.dose} {m.frequency}" for m in patient.medications if m.is_current],
        "allergies": [f"{a.allergen} ({a.severity})" for a in patient.allergies],
        "recent_diagnoses": [v.differentials[0]["condition_name"] if v.differentials else None
                             for v in visits[:3] if v.differentials],
        "vaccination_gaps": get_vaccination_gaps(case_number, session)
    }
```

---

## SECTION 9: UI/UX DESIGN BLUEPRINT — NURSING STAFF FOCUS

> ★ **KEY FLAGS FOR THIS SECTION**
> - Primary user is nursing staff — possibly with limited digital literacy
> - All interactive elements minimum 44×44 px (touch-screen and fat-finger safe)
> - Font: Inter, size 14 minimum body text, 18+ for question text
> - Color system: White background, Deep Navy primary (#0F2D52), Teal accent (#00A896), Red alert (#D62839), Amber (#F4A100), Green (#2ECC71)
> - All medical terminology automatically detected and marked with ℹ tooltip showing plain-language explanation
> - Loading states are always visible — nurse never sees a frozen screen
> - One question per screen option (configurable) or scrollable multi-question panel
> - Emergency button 🚨 is permanently visible in the toolbar at all times

### 9.1 Design System

```css
/* Global Qt stylesheet — loaded from assets/mediassist_theme.qss */

/* Typography */
QWidget { font-family: "Inter"; font-size: 14px; color: #1A1A2E; background: #F8F9FA; }
QLabel[role="heading"] { font-size: 22px; font-weight: 700; color: #0F2D52; }
QLabel[role="subheading"] { font-size: 16px; font-weight: 600; color: #0F2D52; }
QLabel[role="question"] { font-size: 18px; font-weight: 500; color: #1A1A2E; line-height: 1.5; }

/* Buttons */
QPushButton { background: #0F2D52; color: white; border-radius: 8px;
              padding: 12px 24px; font-size: 15px; font-weight: 600; min-height: 44px; }
QPushButton:hover { background: #1A4A7A; }
QPushButton[role="primary"] { background: #00A896; }
QPushButton[role="danger"]  { background: #D62839; }
QPushButton[role="emergency"] { background: #D62839; font-size: 18px; min-width: 100px;
                                 border: 3px solid #FF0000; animation: pulse 1s infinite; }

/* MCQ Option Cards */
QFrame[role="option-card"] { background: white; border: 2px solid #E0E0E0;
                               border-radius: 12px; padding: 16px; margin: 4px 0;
                               min-height: 52px; }
QFrame[role="option-card"]:hover   { border-color: #00A896; background: #F0FFFE; }
QFrame[role="option-card"][selected="true"] { border-color: #0F2D52; background: #EBF0FA; }
QFrame[role="option-card"][is-flag="true"][selected="true"] { border-color: #D62839;
                                                                background: #FDEAEA; }

/* Progress bar */
QProgressBar { background: #E0E0E0; border-radius: 4px; height: 8px; }
QProgressBar::chunk { background: #00A896; border-radius: 4px; }
```

### 9.2 Screen Flow Specification

**Screen 1: Login**
- Large logo + facility name (from config)
- Username field + PIN/Password field (4–6 character PIN option for speed)
- Login button fills full width
- Clock + date visible (patient can verify)

**Screen 2: Patient Search / Registration**
- Large search bar at top (auto-focus on screen load)
- Four filter chips below: Case Number · Full Name · Phone · Date of Birth
- Results table: Case Number | Full Name | Age/Sex | Last Visit | Visit Count
- "Register New Patient" button — prominent, bottom right, navy
- Recent patients panel (last 5 accessed) — left sidebar

**Screen 3: New Patient Registration Form**
- Fields: First Name*, Last Name*, Date of Birth*, Sex*, Phone, Guardian Name (pediatric), Address, National ID (optional)
- Field validation inline (red border + message under field)
- Auto-generated case number shown in read-only field
- "Create Patient" button generates record and advances to Screen 4

**Screen 4: Patient Profile**
- Header: Case Number | Full Name | Age | Sex | Blood Group
- Tab row: Summary | Visits | Medications | Allergies | Vaccinations | Lab Results
- Summary tab: quick view of active conditions, current medications, known allergies, recent diagnosis
- "Start New Visit" button: large, teal, center of screen

**Screen 5: Visit Type Selector**
- 7 large cards (3+2+2 grid), each 200×140 px minimum
- Card content: SVG icon (80×80) + Visit Type Name (bold) + 1-line description
- Selected card highlights with deep navy border + background fill
- Patient name + case number shown in fixed header bar

**Screen 6: Questionnaire — Rounds 1–4**
- Fixed header: Patient Name | Case Number | Round X of 4 | Visit Type
- Progress bar: shows overall questionnaire progress
- Question area: question text (18px, bold) + type-specific input widget
  - RADIO: large clickable option cards (full width, 52px min height)
  - CHECKBOX: same cards with multi-select enabled
  - SCALE: large Qt Slider with labeled endpoints + current value display
  - BODY_MAP: SVG human body (front + back views) with clickable regions
  - TEXT: large QTextEdit with character counter
  - DATE: QDateEdit with calendar popup
- ℹ badge appears automatically beside any term flagged in `medical_terms.json`
  - Click ℹ → floating card with: plain-language explanation + relevant SVG illustration
- Navigation: Previous ← | Question X of Y | → Next
- "Submit Round" button (teal) appears only when all mandatory questions answered
- Unanswered mandatory questions: amber left border on option card

**Screen 7: Vital Signs Entry**
- Clean grid form: 2 columns
- Each field: large QDoubleSpinBox with unit label + normal range hint in grey
- Fields outside normal range turn amber border with tooltip "Outside normal range — will be flagged"
- "Skip" button available (some vitals may not be measurable) — skipped fields appear in brief as "Not recorded"
- BMI auto-calculated when weight + height entered

**Screen 8: Report Generation — Loading**
- Full-screen loading panel with animation
- Progress messages: "Analyzing responses...", "Retrieving clinical guidelines...", "Generating physician brief...", "Validating with second model...", "Report ready"
- Estimated time shown (typically 8–15 seconds)

**Screen 9: Physician Brief — Nurse View**
- Left panel (40% width): Color-coded flag list
  - RED flags: red left border + red background card
  - AMBER flags: amber border card
  - GREEN flags (positive findings): green border card
- Right panel (60% width): abbreviated physician brief (presenting complaint summary, top 3 differentials, most urgent actions)
- Buttons: Print Brief (large, navy) | Save Session (teal) | View Doctor Panel (doctor role only)
- "Emergency" toolbar button still visible

**Screen 10: Settings & Document Manager**
- Tabs: General | Specialty Config | Document Library | User Management | API Keys | Export
- Document Library: upload new documents + list existing collections with chunk counts
- Specialty Config: enable/disable specialties + configure active RAG collections

### 9.3 Medical Terms Dictionary — Sample Entries (medical_terms.json)

```json
{
  "dyspnea":        "Difficulty breathing or shortness of breath — ask: 'Does the patient feel they cannot breathe well?'",
  "palpitations":   "Feeling of abnormal heartbeat — racing, skipping, or pounding heart",
  "diaphoresis":    "Profuse sweating, often sudden and unexplained — ask: 'Is the patient sweating a lot?'",
  "hematuria":      "Blood in urine — may appear red, pink, or dark brown",
  "paresthesia":    "Abnormal skin sensations — tingling, numbness, or 'pins and needles'",
  "oliguria":       "Passing very little urine — less than 400 mL per day in adults",
  "hematemesis":    "Vomiting blood — may look like red blood or dark coffee-ground material",
  "melena":         "Black, tarry stool — usually indicates bleeding in the upper digestive tract",
  "syncope":        "Sudden, brief loss of consciousness — 'fainting'",
  "edema":          "Swelling due to fluid buildup — press the swollen area: if a dent remains, it is 'pitting edema'",
  "cyanosis":       "Bluish discoloration of skin or lips — indicates low blood oxygen",
  "jaundice":       "Yellowing of skin or whites of eyes — indicates liver or bile duct problem",
  "prodrome":       "Warning signs appearing before the main symptom — e.g., aura before a migraine",
  "OPQRST":         "A method to describe pain: Onset, Provocation, Quality, Region, Severity, Time",
  "PHQ-9":          "A 9-question depression screening tool — scored 0–27; higher = more severe",
  "GCS":            "Glasgow Coma Scale — measures consciousness: Eye + Verbal + Motor responses, scored 3–15",
  "APGAR":          "Newborn health score at 1 and 5 minutes after birth — checks Appearance, Pulse, Grimace, Activity, Respiration",
  "orthopnea":      "Shortness of breath when lying flat — patient needs pillows to sleep",
  "tachycardia":    "Fast heart rate — above 100 beats per minute in adults",
  "bradycardia":    "Slow heart rate — below 60 beats per minute in adults",
  "anuria":         "No urine output — none at all in 24 hours — medical emergency"
}
```

---

## SECTION 10: PHYSICIAN DASHBOARD & RAW DATA ACCESS

> ★ **KEY FLAGS FOR THIS SECTION**
> - This section is exclusive to users with DOCTOR or ADMIN role
> - Physician can access the complete raw session data: every LLM API response, every RAG chunk, every question and answer
> - SQL Explorer allows direct (read-only) SQLite queries — allows custom data retrieval without technical support
> - Confidence breakdown panel shows exactly how the accuracy score was calculated
> - Physician can annotate the AI brief with clinical notes and sign off, which permanently locks the report
> - Physician can override any differential ranking — override is logged in audit trail
> - Doctor notes are stored in `visits.doctor_notes` and cannot be edited after sign-off

### 10.1 Physician Dashboard Layout

The physician dashboard is a separate screen accessible only after DOCTOR/ADMIN login. From the main menu the doctor can:
- Browse all cases by date, specialty, flag severity, or nurse
- Open any completed session to view the full physician brief
- Access raw data for any session (see 10.2)
- Sign off and annotate reports
- View a facility summary dashboard with statistics

### 10.2 Raw Data Explorer — Tab Specification

The physician brief screen includes a "Raw Data" tab (hidden from NURSE role) containing four sub-panels:

**Sub-panel A: Full Questionnaire Transcript**
- Shows every question generated in every round with verbatim wording
- Shows nurse's answers for each question
- Questions with flags highlighted in red/amber
- Export as JSON or CSV

**Sub-panel B: RAG Chunk Viewer**
- Lists every document chunk retrieved during the session (all rounds combined)
- Each chunk shows: source document, page/section, similarity score, collection name, full chunk text
- Chunks are sorted by similarity score descending
- Doctor can see exactly what evidence the AI used to reason from
- "Chunk contributed to differential [X]" labels where applicable

**Sub-panel C: LLM Response Log**
- Raw JSON response from each NIM API call made during the session
- Shows: model used, key ID used (not key value), prompt length (tokens), response length (tokens), latency (ms), temperature setting
- Full response JSON expandable inline
- Tool for physician to verify LLM reasoning is sound

**Sub-panel D: Confidence Breakdown**
- Visual breakdown of the composite confidence score:
  ```
  Overall Confidence: 0.91 (HIGH)
  ├── RAG Match Score:        0.93 × 0.40 = 0.37  (Top-5 chunks avg similarity)
  ├── Model Consensus:        1.00 × 0.30 = 0.30  (ROLE_MEDICAL and ROLE_STANDARD agreed on top differential)
  ├── Question Completeness:  0.95 × 0.20 = 0.19  (38 of 40 mandatory questions answered)
  └── Historical Pattern:     0.50 × 0.10 = 0.05  (Partial match to prior visit pattern)
  ```
- RAG sources listed with clickable link to open full source document (if on file)

### 10.3 SQL Explorer — Read-Only Interface

Available to DOCTOR and ADMIN roles. A simple QTextEdit for SQL entry + QTableWidget results display:

```python
# ui/sql_explorer.py  (DOCTOR/ADMIN only)

class SQLExplorer(QWidget):
    """Read-only SQL interface for physicians to query patient data directly."""
    ALLOWED_STATEMENTS = ("SELECT",)   # Only SELECT allowed — no INSERT/UPDATE/DELETE

    def execute_query(self, sql: str):
        sql_stripped = sql.strip().upper()
        if not any(sql_stripped.startswith(stmt) for stmt in self.ALLOWED_STATEMENTS):
            self.show_error("Only SELECT statements are permitted.")
            return
        with session_scope() as session:
            try:
                result = session.execute(text(sql))
                rows   = result.fetchall()
                cols   = result.keys()
                self.populate_table(cols, rows)
                self.log_audit("SQL_QUERY", details={"query": sql})
            except Exception as e:
                self.show_error(f"Query error: {e}")
```

Example queries pre-loaded as "Quick Queries" for physician convenience:
- "Patients with RED flags today"
- "All visits this week by specialty"
- "Overdue vaccinations — all pediatric patients"
- "Top 10 most frequent differentials this month"
- "Patients with penicillin allergy on file"

### 10.4 Physician Sign-Off & Annotation

```python
class PhysicianSignOff(BaseModel):
    visit_id:          int
    doctor_id:         str
    sign_off_time:     datetime
    doctor_agrees:     bool
    differential_overrides: Optional[dict] = None  # {rank: new_diagnosis_name}
    additional_notes:  Optional[str] = None
    investigation_added: Optional[list[str]] = None
    # Once signed off, report is locked — no further edits possible
```

After sign-off:
- Report PDF is regenerated with physician name, signature line, and timestamp
- `visits.doctor_signed_off` set to TRUE
- `visits.is_closed` set to TRUE
- Audit log entry created

---

## SECTION 11: ACCURACY & VALIDATION FRAMEWORK (99.99% TARGET)

> ★ **KEY FLAGS FOR THIS SECTION**
> - 99.99% accuracy is a system-level property, not a single-model property
> - Four independent layers must all operate correctly for an output to be accepted
> - Any LLM output that fails Pydantic schema validation is automatically retried (max 3 attempts before "low confidence" flag)
> - ICD-10/11 codes are assigned by a dedicated structured prompt separate from differential generation — cross-validated
> - The confidence score formula is deterministic and auditable — physician can see every factor
> - Rare disease / multi-system cases route to ROLE_COMPLEX (340B) — higher cost, higher accuracy
> - The system NEVER names a specific drug dose — drug class only — to prevent medication error liability

### 11.1 Four-Layer Trust Architecture

**Layer 1 — RAG Grounding (Prevents Hallucination)**
All clinical statements in output must cite a retrieved document chunk with similarity ≥ 0.75. If the retrieval score for a required clinical topic falls below threshold, the report section includes: `⚠ INSUFFICIENT LOCAL KNOWLEDGE — This section has limited RAG grounding. Physician verification essential.` Citation format in report: `[Source: Harrison's Internal Medicine Ch.14 p.203, similarity: 0.89]`

**Layer 2 — Multi-Model Consensus**
The physician brief is generated by `ROLE_MEDICAL` (Nemotron-70B). The top 3 differentials are then independently validated by `ROLE_STANDARD` (Llama-70B) with the same patient data but a separate prompt. If the two models' top differential disagrees: both are presented with notation `⚠ AI MODEL DISAGREEMENT — Consult physician judgment. ROLE_MEDICAL: [X], ROLE_STANDARD: [Y]`

**Layer 3 — Structured Output Enforcement**
All LLM outputs are validated against Pydantic schemas using the `instructor` library. If validation fails (hallucinated fields, wrong types, missing required fields), the call is automatically retried with an error-correction prompt. After 3 failed attempts, the section is marked `[GENERATION FAILED — physician manual assessment required]` and the raw LLM text is stored in the raw data layer for physician review.

**Layer 4 — Human-in-Loop Physician Sign-Off**
The system never communicates directly with the patient. All outputs are labeled `PRELIMINARY AI ASSESSMENT — FOR PHYSICIAN REVIEW ONLY`. The physician must explicitly sign off (see Section 10.4) before a report is considered clinically complete. No treatment is ever suggested — only investigations and examination pathways. Drug names are replaced with drug class names at the prompt level.

### 11.2 Confidence Score Formula

```
Confidence = (RAG_Match × 0.40) +
             (Consensus × 0.30) +
             (Completeness × 0.20) +
             (History_Match × 0.10)

RAG_Match:     Mean cosine similarity of top-5 retrieved chunks (0.0–1.0)
Consensus:     1.0 if both models agree on top differential
               0.7 if models agree on top 3 but different rank 1
               0.5 if top differentials differ (disagreement)
               0.3 if only 1 model succeeded (other errored)
Completeness:  (mandatory questions answered) / (total mandatory questions)
History_Match: 1.0 if patient has prior visit with similar diagnosis
               0.5 if similar but different specialty
               0.0 if no relevant history exists

Threshold interpretation:
≥ 0.85: "HIGH CONFIDENCE — RAG-Grounded"    (display in green)
0.70–0.84: "MODERATE CONFIDENCE — Verify"  (display in amber)
< 0.70: "LOW CONFIDENCE — Physician Discretion Essential"  (display in red)
```

### 11.3 Red Flag Auto-Escalation Protocol

If any red flag is triggered in ANY round (including vital signs capture):
1. Questionnaire halts immediately
2. Full-screen emergency banner: `⚠ POSSIBLE EMERGENCY DETECTED — NOTIFY PHYSICIAN IMMEDIATELY`
3. Audio chime plays (configurable per-facility)
4. Emergency triage note generated in < 10 seconds using ROLE_FAST
5. One-click print of emergency triage note
6. Session logged with `is_emergency = TRUE`
7. Physician notification queued (if notification system configured)

### 11.4 ICD-10/11 Code Assignment

ICD code assignment uses a dedicated structured prompt via ROLE_FAST (speed + cost optimized), separate from the differential generation prompt. This prevents ICD code errors from contaminating the clinical reasoning chain.

```python
ICD_PROMPT = """
Given the following diagnosis name, return ONLY a JSON object with:
{"icd_10": "X00.0", "icd_11": "XX.XX", "confidence": 0.95}
Use exact ICD-10 format: letter + 2 digits + optional decimal.
Diagnosis: {diagnosis_name}
Respond ONLY with JSON. No preamble.
"""
```

---

## SECTION 12: SECURITY, PRIVACY & COMPLIANCE

> ★ **KEY FLAGS FOR THIS SECTION**
> - Database encrypted with AES-256 via SQLCipher — encrypted at rest
> - NIM API keys stored only in Windows Credential Manager (DPAPI) — never plaintext on disk
> - Argon2id with memory=65536, iterations=3, parallelism=4 for all password hashing
> - Role-based access: NURSE cannot access raw DB, DOCTOR can read-only, ADMIN has full config
> - Audit log is append-only — no UI mechanism to delete log entries
> - Patient PII (national ID, phone) encrypted at field level using Fernet symmetric encryption
> - Export files encrypted with AES-256-GCM + facility-specific passphrase before writing to USB

### 12.1 Role Access Matrix

| Capability | NURSE | DOCTOR | ADMIN | SUPERADMIN |
|-----------|-------|--------|-------|-----------|
| Create/search patients | ✓ | ✓ | ✓ | ✓ |
| Run questionnaire sessions | ✓ | — | ✓ | ✓ |
| View physician brief | Own sessions | All | All | All |
| Raw data access | — | ✓ | ✓ | ✓ |
| SQL Explorer | — | Read-only | Read-only | Full |
| Sign off reports | — | ✓ | — | ✓ |
| Manage users | — | — | ✓ | ✓ |
| Upload documents | — | — | ✓ | ✓ |
| Configure specialties | — | — | ✓ | ✓ |
| Access API key settings | — | — | ✓ | ✓ |
| Delete patient records | — | — | — | Soft only |
| View audit log | — | — | ✓ | ✓ |
| Export patient data | — | — | ✓ | ✓ |

### 12.2 Compliance Posture

| Standard | Relevance | Implementation Status |
|---------|-----------|----------------------|
| HIPAA (US) | US deployments | Minimum necessary data; PHI encryption; audit logging; BAA documentation |
| GDPR (EU) | EU/European deployments | Right to erasure (soft delete); data minimization; consent tracking |
| WHO AI Ethics for Health | All humanitarian deployments | No autonomous diagnosis; human-in-loop mandatory; bias documentation in place |
| ISO 27001 | General InfoSec | Access logs; incident response plan in Section 16; backup policy |
| HL7 FHIR R4 | EHR interoperability | FHIR-compatible export format; patient resource mapping |
| ICD-10/11 | Coding standards | All differentials dual-coded; codes assigned by dedicated structured prompt |

### 12.3 Audit Logging

Every user action is logged immutably. Log record structure:
```json
{
  "timestamp": "2025-08-14T09:32:14Z",
  "user_id": "nurse_001",
  "role": "NURSE",
  "action": "REPORT_GENERATED",
  "case_number": "CHC-2025-0042",
  "details": {"rounds_completed": 4, "visit_type": "SPECIFIC"},
  "model_used": "nvidia/llama-3.1-nemotron-70b-instruct",
  "api_key_id": 5,
  "duration_ms": 9240,
  "confidence_score": 0.91
}
```

---

## SECTION 13: PROJECT FILE & FOLDER STRUCTURE

> ★ **KEY FLAGS FOR THIS SECTION**
> - Every module has a single well-defined responsibility — no cross-cutting logic outside of `app_controller.py`
> - All LLM prompts live exclusively in `questionnaire/prompt_templates.py` — never embedded in business logic
> - All UI text strings live in `config/locale/{lang}.json` — never hardcoded in UI files
> - All Pydantic schemas live in `models/` — imported by all other modules, never redefined locally
> - `knowledge_base/incoming/` is the hot folder for document ingestion — document it clearly in admin guide

```
MediAssistPro/
│
├── main.py                            # App entry point — initialize all services, launch UI
├── app_controller.py                  # Central orchestrator — wires all modules together
├── requirements.txt                   # All dependencies, fully version-pinned
├── requirements-dev.txt               # Dev/test dependencies
├── pyproject.toml                     # Project metadata, linting (Ruff), formatting (Black)
├── alembic.ini                        # Alembic migration configuration
├── .env.example                       # Template for environment variables (no secrets)
│
├── config/
│   ├── settings.py                    # Pydantic BaseSettings — loads from env + config files
│   ├── facility_config.json           # Facility name, code, specialty focus, locale
│   ├── doctor_fields.json             # All 21 specialty configurations (see Section 19)
│   ├── medical_terms.json             # Nurse explanation dictionary (1000+ terms)
│   ├── vital_sign_norms.json          # Normal ranges by age group, sex, pregnancy status
│   ├── visit_types.json               # Configurable visit type definitions
│   ├── icd10_index.json               # Local ICD-10 lookup table for offline use
│   └── locale/
│       ├── en.json                    # English UI strings
│       ├── fr.json                    # French (MSF/ICRC deployments)
│       └── ar.json                    # Arabic (refugee camp deployments)
│
├── models/
│   ├── db_models.py                   # SQLAlchemy ORM models (all tables)
│   ├── questionnaire.py               # Pydantic schemas: Question, QuestionnaireRound, SessionAnswers
│   ├── report_output.py               # Pydantic schemas: ClinicalFlag, DifferentialDiagnosis, PhysicianBrief
│   ├── vital_signs.py                 # Pydantic schema: VitalSigns
│   └── user.py                        # Pydantic schemas: User, LoginRequest
│
├── patient/
│   ├── patient_manager.py             # CRUD for Patient + related tables
│   ├── case_number.py                 # Thread-safe case number generation
│   ├── history_loader.py              # Assemble structured patient context for LLM
│   └── vaccination_tracker.py         # EPI schedule gap analysis
│
├── nim/
│   ├── nim_key_manager.py             # 7-key pool with role-routing, health checking
│   ├── nim_client.py                  # Async OpenAI SDK wrapper for NIM
│   └── offline_fallback.py            # llama-cpp-python local GGUF model interface
│
├── rag/
│   ├── document_manager.py            # Document ingest + retrieval
│   ├── document_loader_factory.py     # File-type-based loader selection
│   ├── chunker.py                     # RecursiveCharacterTextSplitter wrapper
│   ├── embedder.py                    # NIM embedding wrapper + offline fallback
│   ├── reranker.py                    # NIM reranker wrapper
│   └── vector_store.py                # ChromaDB collection manager (12 collections)
│
├── questionnaire/
│   ├── engine.py                      # Main agentic 4-round loop
│   ├── round_generator.py             # Per-round question generation with instructor
│   ├── prompt_templates.py            # All Jinja2 LLM prompt templates
│   ├── response_parser.py             # LLM JSON validation + retry logic
│   ├── state_machine.py               # Session state transitions
│   └── red_flag_detector.py           # Real-time emergency flag scanning on every answer
│
├── report/
│   ├── report_generator.py            # Generate PhysicianBrief from all rounds + vitals
│   ├── icd_mapper.py                  # ICD-10/11 code assignment via structured prompt
│   ├── consensus_validator.py         # Dual-model consensus check
│   ├── confidence_scorer.py           # Composite confidence score calculator
│   ├── pdf_exporter.py                # ReportLab PDF generation (A4, color-coded)
│   └── templates/
│       ├── physician_brief.html        # Jinja2 HTML for WebEngine preview
│       └── emergency_triage.html       # Emergency triage note template
│
├── ui/
│   ├── main_window.py                 # QMainWindow shell + toolbar
│   ├── splash_screen.py               # Loading/init screen with status messages
│   ├── dashboard.py                   # Main nurse dashboard
│   ├── patient_search.py              # Patient search + registration screen
│   ├── patient_profile.py             # Patient history tabs
│   ├── visit_type_selector.py         # 7-card visit type grid
│   ├── questionnaire_widget.py        # Adaptive question display + round navigation
│   ├── vital_signs_form.py            # Structured vital signs entry
│   ├── report_viewer.py               # Physician brief display (nurse view)
│   ├── physician_dashboard.py         # Full physician view + raw data (DOCTOR role)
│   ├── sql_explorer.py                # Read-only SQL interface (DOCTOR/ADMIN)
│   ├── rag_chunk_viewer.py            # RAG source chunk explorer (DOCTOR)
│   ├── emergency_screen.py            # Full-screen emergency escalation display
│   ├── document_manager_ui.py         # Upload + manage medical documents
│   ├── settings_ui.py                 # Application settings screens
│   ├── question_components/
│   │   ├── mcq_radio.py               # Single-select MCQ card widget
│   │   ├── mcq_checkbox.py            # Multi-select MCQ card widget
│   │   ├── scale_slider.py            # 0–10 pain/severity scale widget
│   │   ├── body_map.py                # SVG human body anatomical selector
│   │   ├── nurse_tooltip.py           # ℹ plain-language explanation popup
│   │   └── date_duration.py           # Combined date + duration picker
│   └── workers/
│       ├── questionnaire_worker.py    # QThread worker for LLM calls (non-blocking)
│       ├── report_worker.py           # QThread worker for report generation
│       └── import_worker.py           # QThread worker for data imports
│
├── data_port/
│   ├── importer.py                    # Main data import orchestrator
│   ├── background_processor.py        # Downtime processing daemon (watchdog-based)
│   └── parsers/
│       ├── csv_parser.py
│       ├── excel_parser.py
│       ├── hl7_parser.py
│       ├── fhir_parser.py
│       ├── pdf_records_parser.py
│       ├── docx_records_parser.py
│       └── generic_text_parser.py
│
├── database/
│   ├── connection.py                  # SQLAlchemy engine + session factory (SQLCipher)
│   ├── encryption.py                  # Field-level PII encryption (Fernet)
│   ├── backup.py                      # Automated backup logic (daily + on close)
│   └── migrations/
│       └── versions/                  # Alembic auto-generated migration files
│
├── assets/
│   ├── icons/                         # SVG icons for all visit types + UI
│   ├── fonts/Inter/                   # Inter font family files
│   ├── body_maps/
│   │   ├── body_front.svg             # Human body front view with named click regions
│   │   ├── body_back.svg              # Human body back view
│   │   └── body_pediatric.svg         # Child body silhouette
│   ├── mediassist_theme.qss           # Qt stylesheet
│   └── logo.svg
│
├── knowledge_base/
│   ├── incoming/                      # Drop new documents here — auto-ingested
│   ├── processed/                     # Successfully ingested documents (moved here)
│   ├── failed/                        # Failed ingestion (check logs for reason)
│   ├── seed_documents/                # Pre-bundled WHO/CDC free documents
│   └── chroma_db/                     # ChromaDB persistent storage directory
│
├── models_local/                      # Local GGUF model for offline fallback
│   └── biomistral-7b-q4km.gguf        # Downloaded on first setup
│
├── tests/
│   ├── unit/
│   │   ├── test_nim_key_manager.py
│   │   ├── test_patient_manager.py
│   │   ├── test_questionnaire_engine.py
│   │   ├── test_report_generator.py
│   │   └── test_confidence_scorer.py
│   ├── integration/
│   │   ├── test_rag_pipeline.py
│   │   ├── test_full_session.py
│   │   └── test_data_import.py
│   ├── ui_tests/
│   │   ├── test_patient_search_ui.py
│   │   └── test_questionnaire_ui.py
│   └── fixtures/
│       ├── synthetic_patients.json     # 50 synthetic patient cases
│       └── golden_reports/             # Expected report outputs for comparison
│
├── scripts/
│   ├── setup_wizard.py                # First-run guided setup
│   ├── seed_knowledge_base.py         # Bulk-ingest seed documents on first run
│   └── build_installer.py             # PyInstaller + NSIS packaging script
│
└── logs/
    ├── audit.db                       # Append-only audit log SQLite
    └── app.log                        # Application runtime log (Loguru)
```

---

## SECTION 14: CORE MODULE CODE ARCHITECTURE

> ★ **KEY FLAGS FOR THIS SECTION**
> - The `app_controller.py` is the dependency injection root — it instantiates every service and injects into every module
> - All LLM calls are asynchronous (`async def`) and run in QThread workers — main UI thread never blocks
> - `instructor.from_openai(client)` wraps the NIM client for Pydantic output enforcement
> - The `report_generator.py` makes TWO separate LLM calls: ROLE_MEDICAL for generation, ROLE_STANDARD for consensus — results are merged
> - PDF export is generated from a Jinja2 HTML template, then rendered by ReportLab

### 14.1 Application Entry Point

```python
# main.py

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.splash_screen import SplashScreen
from ui.main_window import MainWindow
from app_controller import AppController

def main():
    # High DPI support for modern Windows displays
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setApplicationName("MediAssist Pro")
    app.setApplicationVersion("2.0.0")
    app.setStyle("Fusion")

    splash = SplashScreen()
    splash.show()
    app.processEvents()

    controller = AppController(splash_callback=splash.set_status)
    controller.initialize()   # Loads DB, keys, RAG, checks connectivity

    window = MainWindow(controller=controller)
    splash.finish(window)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

### 14.2 Questionnaire Engine Core

```python
# questionnaire/engine.py

import asyncio
import instructor
from openai import AsyncOpenAI
from models.questionnaire import QuestionnaireRound, SessionAnswers
from models.report_output import PhysicianBrief
from nim.nim_key_manager import NIMKeyManager, ModelRole
from rag.document_manager import DocumentManager
from .prompt_templates import PromptTemplates
from .red_flag_detector import RedFlagDetector
from config.settings import VISIT_TYPE_RAG_MAP, VISIT_TYPE_ROLE_MAP
from loguru import logger

class QuestionnaireEngine:
    MAX_RETRIES = 3

    def __init__(self, key_manager: NIMKeyManager, doc_manager: DocumentManager):
        self.key_manager      = key_manager
        self.doc_manager      = doc_manager
        self.prompts          = PromptTemplates()
        self.flag_detector    = RedFlagDetector()
        self.session_answers  = SessionAnswers()
        self.raw_llm_log      = []    # Stored for physician raw data access
        self.raw_rag_log      = []    # Stored for physician raw data access

    def _get_instructor_client(self, role: ModelRole):
        key = self.key_manager.get_key_for_role(role)
        base_client = AsyncOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=key.value,
            timeout=45.0,
            max_retries=0
        )
        return instructor.from_openai(base_client), self.key_manager.get_model_for_role(role), key.key_id

    async def generate_round(self, round_number: int, visit_type: str,
                              patient_ctx: dict, specialty: str) -> QuestionnaireRound:
        role        = VISIT_TYPE_ROLE_MAP.get(visit_type, ModelRole.STANDARD)
        collections = VISIT_TYPE_RAG_MAP.get(visit_type, ["core_medicine", "who_guidelines"])

        # Retrieve RAG context relevant to current symptom profile
        query       = self._build_rag_query(round_number, patient_ctx)
        rag_chunks  = self.doc_manager.retrieve(query, collections, n_results=15)
        self.raw_rag_log.extend(rag_chunks)
        rag_text    = self._format_rag_context(rag_chunks[:5])  # Top-5 after reranking

        prompt      = self.prompts.get_round_prompt(
            round_number=round_number,
            visit_type=visit_type,
            specialty=specialty,
            patient_ctx=patient_ctx,
            session_answers=self.session_answers.dict(),
            rag_context=rag_text
        )

        client, model, key_id = self._get_instructor_client(role)
        import time
        start = time.time()

        for attempt in range(self.MAX_RETRIES):
            try:
                result: QuestionnaireRound = await client.chat.completions.create(
                    model=model,
                    response_model=QuestionnaireRound,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=4096
                )
                duration = int((time.time() - start) * 1000)
                result.generation_time_ms = duration
                result.model_used         = model
                result.rag_chunk_ids      = [c["metadata"]["chunk_id"] for c in rag_chunks[:5]]
                self.raw_llm_log.append({"round": round_number, "model": model,
                                          "key_id": key_id, "duration_ms": duration})
                logger.info(f"Round {round_number} generated: {len(result.questions)} questions in {duration}ms")
                return result
            except Exception as e:
                logger.warning(f"Round {round_number} generation attempt {attempt+1} failed: {e}")
                if attempt == self.MAX_RETRIES - 1:
                    raise RuntimeError(f"Failed to generate round {round_number} after {self.MAX_RETRIES} attempts")

    def submit_round_answers(self, round_number: int, answers: dict):
        """Store answers and check every answer for red flags."""
        setattr(self.session_answers, f"round_{round_number}", answers)
        flags = self.flag_detector.check_answers(answers, round_number)
        if flags:
            self.session_answers.flags_raised.extend(flags)
            return {"emergency": True, "flags": flags}
        return {"emergency": False, "flags": []}
```

### 14.3 Report Generator with Dual-Model Consensus

```python
# report/report_generator.py

import asyncio
import instructor
from openai import AsyncOpenAI
from models.report_output import PhysicianBrief
from models.questionnaire import SessionAnswers
from .consensus_validator import ConsensusValidator
from .confidence_scorer import ConfidenceScorer
from .icd_mapper import ICDMapper
from nim.nim_key_manager import NIMKeyManager, ModelRole
from rag.document_manager import DocumentManager
from questionnaire.prompt_templates import PromptTemplates
from loguru import logger

class ReportGenerator:
    def __init__(self, key_manager: NIMKeyManager, doc_manager: DocumentManager):
        self.key_manager = key_manager
        self.doc_manager = doc_manager
        self.prompts     = PromptTemplates()
        self.icd_mapper  = ICDMapper(key_manager)
        self.validator   = ConsensusValidator(key_manager)
        self.scorer      = ConfidenceScorer()

    async def generate(self, case_number: str, session_answers: SessionAnswers,
                        patient_ctx: dict, vital_signs: dict,
                        rag_chunks_used: list, specialty: str) -> PhysicianBrief:

        # Retrieve final RAG context for report generation
        complaint_query = patient_ctx.get("chief_complaint_summary", "")
        final_chunks    = self.doc_manager.retrieve(complaint_query,
                           ["core_medicine", "who_guidelines", specialty.lower()], n_results=15)
        rag_text        = "\n\n".join([f"[{c['metadata']['source_file']}, p.{c['metadata'].get('page_number','')}] {c['text']}" for c in final_chunks[:5]])

        # Primary generation: ROLE_MEDICAL (Nemotron)
        medical_prompt = self.prompts.get_brief_prompt(
            case_number=case_number,
            session_answers=session_answers.dict(),
            patient_ctx=patient_ctx,
            vital_signs=vital_signs,
            rag_context=rag_text,
            specialty=specialty
        )
        key_m    = self.key_manager.get_key_for_role(ModelRole.MEDICAL)
        client_m = instructor.from_openai(AsyncOpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=key_m.value, timeout=60.0, max_retries=0
        ))
        primary_brief: PhysicianBrief = await client_m.chat.completions.create(
            model=self.key_manager.get_model_for_role(ModelRole.MEDICAL),
            response_model=PhysicianBrief,
            messages=[{"role": "user", "content": medical_prompt}],
            temperature=0.1, max_tokens=8192
        )

        # Consensus validation: ROLE_STANDARD cross-checks differentials
        consensus_result = await self.validator.validate(primary_brief, patient_ctx, rag_text)
        primary_brief    = self.validator.merge_consensus(primary_brief, consensus_result)

        # Assign ICD codes to all differentials
        for diff in primary_brief.differentials:
            icd = await self.icd_mapper.map(diff.condition_name)
            diff.icd_10_code = icd.icd_10
            diff.icd_11_code = icd.icd_11

        # Calculate confidence score
        primary_brief.confidence_score = self.scorer.calculate(
            rag_chunks=final_chunks[:5],
            consensus=consensus_result,
            session_answers=session_answers,
            patient_ctx=patient_ctx
        )
        logger.info(f"Report generated for {case_number} — confidence: {primary_brief.confidence_score:.2f}")
        return primary_brief
```

### 14.4 PDF Export — A4 Formatted Physician Brief

```python
# report/pdf_exporter.py

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from models.report_output import PhysicianBrief

class PDFExporter:
    RED   = colors.HexColor("#D62839")
    AMBER = colors.HexColor("#F4A100")
    GREEN = colors.HexColor("#2ECC71")
    NAVY  = colors.HexColor("#0F2D52")
    TEAL  = colors.HexColor("#00A896")

    def export(self, brief: PhysicianBrief, output_path: str, facility_name: str) -> str:
        doc   = SimpleDocTemplate(output_path, pagesize=A4,
                                   leftMargin=20*mm, rightMargin=20*mm,
                                   topMargin=20*mm, bottomMargin=20*mm)
        styles = getSampleStyleSheet()
        story  = []

        # Header
        story.append(Paragraph(f"<b>{facility_name} — MediAssist Pro</b>", styles['Title']))
        story.append(Paragraph(f"<b>PHYSICIAN BRIEF — {brief.case_number}</b>", styles['h1']))
        story.append(Paragraph(f"<i>Generated: {brief.generated_at} | Confidence: {brief.confidence_score:.0%} | *** PRELIMINARY AI ASSESSMENT — PHYSICIAN REVIEW REQUIRED ***</i>", styles['Normal']))
        story.append(HRFlowable(width="100%", thickness=2, color=self.NAVY))
        story.append(Spacer(1, 8))

        # Presenting complaint
        story.append(Paragraph("<b>PRESENTING COMPLAINT</b>", styles['h2']))
        story.append(Paragraph(brief.presenting_complaint_summary, styles['Normal']))
        story.append(Spacer(1, 6))

        # Flags
        story.append(Paragraph("<b>⚑ CLINICAL FLAGS</b>", styles['h2']))
        for flag in brief.flags:
            color = self.RED if flag.severity == "RED" else (self.AMBER if flag.severity == "AMBER" else self.GREEN)
            story.append(Paragraph(
                f'<font color="{color.hexval()}"><b>[{flag.severity}]</b> {flag.flag_text}</font> — <i>{flag.source_document}</i>',
                styles['Normal']
            ))
        story.append(Spacer(1, 6))

        # Differentials
        story.append(Paragraph("<b>DIFFERENTIAL DIAGNOSES</b>", styles['h2']))
        data = [["#", "Diagnosis", "ICD-10", "ICD-11", "Probability", "Key Supporting Features"]]
        for d in brief.differentials:
            data.append([str(d.rank), d.condition_name, d.icd_10_code, d.icd_11_code,
                         d.probability_qualitative, "; ".join(d.supporting_features[:3])])
        tbl = Table(data, colWidths=[8*mm, 40*mm, 18*mm, 18*mm, 22*mm, None])
        tbl.setStyle([
            ('BACKGROUND',  (0,0), (-1,0), self.NAVY),
            ('TEXTCOLOR',   (0,0), (-1,0), colors.white),
            ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0,0), (-1,-1), 8),
            ('GRID',        (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8F9FA")]),
        ])
        story.append(tbl)
        story.append(Spacer(1, 6))

        # Examination plan
        story.append(Paragraph("<b>SUGGESTED PHYSICAL EXAMINATION</b>", styles['h2']))
        for item in brief.suggested_examination:
            story.append(Paragraph(f"• {item}", styles['Normal']))

        # Investigations
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>SUGGESTED INVESTIGATIONS</b>", styles['h2']))
        for item in brief.suggested_investigations:
            story.append(Paragraph(f"• {item}", styles['Normal']))

        # Urgent actions
        if brief.urgent_actions:
            story.append(Spacer(1, 4))
            story.append(Paragraph("<b>🚨 URGENT ACTIONS</b>", styles['h2']))
            for item in brief.urgent_actions:
                story.append(Paragraph(f'<font color="{self.RED.hexval()}"><b>• {item}</b></font>', styles['Normal']))

        # RAG sources
        story.append(Spacer(1, 4))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Paragraph("<b>Evidence Sources (RAG-Grounded)</b>", styles['h3']))
        for src in brief.rag_sources:
            story.append(Paragraph(f"<small>{src}</small>", styles['Normal']))

        # Footer disclaimer
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            "<i>*** THIS IS A PRELIMINARY AI-GENERATED ASSESSMENT. IT DOES NOT CONSTITUTE A CLINICAL DIAGNOSIS. ALL FINDINGS REQUIRE PHYSICIAN REVIEW AND SIGN-OFF BEFORE CLINICAL ACTION. ***</i>",
            styles['Normal']
        ))

        doc.build(story)
        return output_path
```

---

## SECTION 15: DEVELOPMENT PHASES & MILESTONES

> ★ **KEY FLAGS FOR THIS SECTION**
> - Build phases are sequential — do not start Phase N+1 until Phase N milestone is verified
> - Each phase ends with a concrete testable milestone that a non-developer can verify
> - Total estimated time: 105–115 days solo developer; 35–45 days with a 3-person team
> - Phase 0 is critical infrastructure — rushing it will cause debt in all later phases
> - Phase 2 (Questionnaire Engine) is the longest and most complex phase — allocate extra buffer

### Phase 0: Infrastructure & Skeleton (Days 1–7)
- [ ] Initialize Python 3.11 project with `pyproject.toml`, `requirements.txt`, virtual environment
- [ ] Set up PySide6 application skeleton: `main.py`, `MainWindow`, `SplashScreen`
- [ ] Initialize SQLite + SQLCipher database with all 9 tables via Alembic
- [ ] Implement `NIMKeyManager` and verify all 7 NIM API keys connect and return responses
- [ ] Set up ChromaDB instance with all 12 empty collections
- [ ] Create encrypted key storage via Windows Credential Manager (`keyring`)
- [ ] Build basic patient search + creation UI (no LLM calls yet)
- [ ] Set up Loguru logging with daily rotation to `logs/app.log`
- [ ] Set up pytest with one passing smoke test

**Milestone 0:** Application launches, patient can be created, searched, and displayed. All 7 NIM keys confirmed working via automated test.

### Phase 1: RAG Pipeline (Days 8–21)
- [ ] Implement `DocumentManager.ingest_document()` for PDF, DOCX, TXT, EPUB
- [ ] Implement `DocumentManager.retrieve()` with NIM reranker
- [ ] Build `BackgroundProcessor` watchdog daemon
- [ ] Seed knowledge base: ingest all 5 free WHO seed documents
- [ ] Build Document Manager UI (admin upload + collection stats)
- [ ] Test: upload WHO Emergency Care guide, query "chest pain management", verify ≥3 relevant chunks returned with similarity ≥0.80

**Milestone 1:** Admin uploads a WHO PDF; system returns RAG-grounded clinical passage in < 3 seconds.

### Phase 2: Questionnaire Engine (Days 22–46)
- [ ] Build session state machine (`state_machine.py`)
- [ ] Build Round 1 generator (triage + chief complaint)
- [ ] Build Round 2 generator (OPQRST)
- [ ] Build Round 3 generator (history + medications)
- [ ] Build Round 4 generator (differential refinement)
- [ ] Build all question UI components (MCQ radio, checkbox, scale, body map, date)
- [ ] Implement `medical_terms.json` auto-detection + ℹ tooltip system
- [ ] Implement vital signs capture form
- [ ] Implement `RedFlagDetector` and emergency escalation screen
- [ ] Write all Jinja2 prompt templates for all 4 rounds + all 7 visit types

**Milestone 2:** Full 4-round questionnaire + vital signs + emergency detection works for "chest pain — specific complaint" scenario with correctly triggered RED flag.

### Phase 3: Report Generation (Days 47–63)
- [ ] Build `ReportGenerator` with dual-model consensus
- [ ] Build `ICDMapper` structured prompt
- [ ] Build `ConfidenceScorer` with all 4 factors
- [ ] Build `PDFExporter` with color-coded ReportLab output
- [ ] Build `ReportViewer` (nurse view) + `PhysicianDashboard` (doctor view)
- [ ] Build RAG Chunk Viewer, LLM Response Log, Confidence Breakdown sub-panels
- [ ] Build SQL Explorer (read-only, DOCTOR role)
- [ ] Build physician sign-off and annotation feature

**Milestone 3:** Complete session from patient registration → 4 rounds → vitals → physician brief PDF. Doctor can view raw LLM responses and sign off.

### Phase 4: Data Port & Patient History (Days 64–77)
- [ ] Build CSV + Excel import parser
- [ ] Build HL7 v2 + FHIR R4 import parsers
- [ ] Build PDF patient records extractor (PyMuPDF + OCR)
- [ ] Build `BackgroundProcessor` downtime batch importer
- [ ] Build vaccination tracker with EPI schedule gap analysis
- [ ] Test: import 200 synthetic legacy patient records; verify all case data attributed correctly

**Milestone 4:** Bulk import of synthetic legacy data succeeds. Patient history auto-populates in Round 3.

### Phase 5: All Visit Types & Specialties (Days 78–95)
- [ ] Implement all 7 visit types with correct RAG + role assignments
- [ ] Implement all 21 specialty configurations in `doctor_fields.json`
- [ ] Build specialty configuration settings UI
- [ ] Implement multilingual locale loader (en, fr, ar)
- [ ] Build clinical scoring tools for each specialty (PHQ-9, GCS, APGAR, SOFA, etc.)
- [ ] End-to-end testing for each of the 7 visit types

**Milestone 5:** All 7 visit types produce correct physician briefs. PHQ-9 embeds correctly in MENTAL visit. Pediatric vital sign norms apply correctly for a 2-year-old patient.

### Phase 6: Security, Polish & Packaging (Days 96–115)
- [ ] Enable SQLCipher encryption on all databases
- [ ] Complete role-based access control enforcement across all screens
- [ ] Complete audit logging for every user action
- [ ] PyInstaller packaging with all dependencies bundled
- [ ] NSIS installer creation (Section 17 build script)
- [ ] Complete accessibility pass (keyboard navigation, screen reader labels)
- [ ] Performance optimization: target < 3s for questionnaire round generation, < 15s for physician brief
- [ ] Full end-to-end regression test suite

**Milestone 6:** Signed Windows installer `.exe` delivered. Installs on a clean Windows 11 machine with no Python pre-installed. Completes full session in < 15 minutes total.

---

## SECTION 16: TESTING STRATEGY

> ★ **KEY FLAGS FOR THIS SECTION**
> - 100% test coverage required on all Pydantic schemas and DB models
> - Clinical accuracy testing uses 50 synthetic golden patient cases — 10 per major specialty
> - RED flag detection must achieve 100% sensitivity — zero misses are acceptable for any configured red flag
> - All API calls are mocked in unit/integration tests using `responses` library — no real API calls in CI
> - Performance benchmarks: round generation < 3s, full brief < 15s, RAG retrieval < 500ms

### 16.1 Test Coverage Targets

| Module | Target | Test Types |
|--------|--------|-----------|
| Pydantic schemas (`models/`) | 100% | Unit |
| Database models + migrations | 100% | Unit + Integration |
| Patient manager CRUD | 100% | Unit + Integration |
| NIM key manager | 100% | Unit (mock API) |
| Questionnaire engine rounds 1–4 | 95% | Unit + Integration (mock LLM) |
| RAG pipeline ingest + retrieval | 90% | Integration |
| Report generator + consensus | 90% | Unit + Golden file comparison |
| Confidence scorer | 100% | Unit |
| PDF exporter | 85% | Unit (compare byte output) |
| UI components | 80% | pytest-qt |
| End-to-end full sessions | 10 scenarios (one per specialty) | E2E with mock LLM |

### 16.2 Golden Dataset — Clinical Accuracy Testing

Create 50 synthetic patient cases (no real PII) with known ground-truth diagnoses:
- 10 × General Medicine (headache, chest pain, abdominal pain, fever, fatigue)
- 8 × Pediatrics (fever, respiratory, GI, developmental concerns)
- 6 × Obstetrics (ANC visit, bleeding, pre-eclampsia screen)
- 6 × Emergency (STEMI signs, stroke screen, sepsis, trauma)
- 5 × Mental Health (depression screen, anxiety, psychosis red flags)
- 5 × Infectious Disease (TB screen, malaria symptoms, HIV-related)
- 10 × Mixed specialty (cardiology, neurology, endocrinology, ENT, dermatology)

For each golden case: verify top differential matches, all RED flags raised, ICD codes correct, RAG citations relevant, confidence score ≥ 0.80.

### 16.3 Performance Benchmarks

```python
# tests/performance/test_benchmarks.py

def test_rag_retrieval_under_500ms():
    """RAG retrieval from 50,000-chunk knowledge base must complete in < 500ms."""
    ...

def test_round_generation_under_3s():
    """Each questionnaire round generation must complete in < 3 seconds (mocked NIM latency 300ms)."""
    ...

def test_full_brief_under_15s():
    """Full physician brief (4 rounds + consensus + ICD mapping) must complete in < 15 seconds."""
    ...

def test_ui_never_blocks():
    """Main UI thread must not block during any LLM operation (assert QThread usage)."""
    ...
```

---

## SECTION 17: DEPLOYMENT & DISTRIBUTION GUIDE

> ★ **KEY FLAGS FOR THIS SECTION**
> - Single `.exe` installer — no Python runtime required on target machine
> - PyInstaller bundles all dependencies including Qt DLLs, ChromaDB, sentence-transformers
> - NSIS installer creates Start Menu + Desktop shortcuts and runs first-use setup wizard
> - Seed documents (WHO free publications) are bundled in the installer and auto-ingested on first run
> - Update mechanism checks GitHub Releases on startup — runs Alembic migrations automatically on update
> - Minimum target: Windows 10 64-bit, 8 GB RAM, 20 GB free disk, 4-core CPU

### 17.1 PyInstaller Build Script

```bash
# scripts/build_installer.py — run from project root in activated venv

pyinstaller \
  --name "MediAssistPro" \
  --onedir \
  --windowed \
  --icon assets/logo.ico \
  --add-data "config/*;config" \
  --add-data "assets/*;assets" \
  --add-data "knowledge_base/seed_documents/*;knowledge_base/seed_documents" \
  --add-data "models_local/*.gguf;models_local" \
  --hidden-import "PySide6.QtCore" \
  --hidden-import "PySide6.QtWidgets" \
  --hidden-import "PySide6.QtWebEngineWidgets" \
  --hidden-import "PySide6.QtCharts" \
  --hidden-import "chromadb" \
  --hidden-import "chromadb.db.impl" \
  --hidden-import "sentence_transformers" \
  --hidden-import "instructor" \
  --collect-all "chromadb" \
  --collect-all "sentence_transformers" \
  --collect-all "instructor" \
  --collect-all "langchain" \
  --collect-all "llama_cpp" \
  --exclude-module "tkinter" \
  --exclude-module "matplotlib" \
  main.py
```

### 17.2 First-Run Setup Wizard

On first launch, a guided 5-step wizard collects:
1. **Facility Setup:** Facility name, facility code (used in case numbers), country/region
2. **Specialty Configuration:** Select active specialties for this station (checkboxes from full 21-specialty list)
3. **API Keys:** Enter all 7 NVIDIA NIM API keys; system tests each key live; shows green/red status per key
4. **Admin Account:** Create admin username + password (Argon2id hashed; minimum 8 characters enforced)
5. **Initial Document Seed:** Progress screen showing auto-ingestion of bundled WHO seed documents (runs in background thread with progress bar)

### 17.3 Seed Documents — Bundled in Installer

The following free, publicly available documents are bundled and auto-ingested:

| Document | Collection | Source |
|----------|-----------|--------|
| WHO Pocket Book of Hospital Care for Children, 2nd Ed | `pediatrics`, `who_guidelines` | WHO Publications |
| WHO Emergency Triage Assessment and Treatment (ETAT) | `emergency`, `who_guidelines` | WHO Publications |
| WHO Integrated Management of Childhood Illness (IMCI) | `pediatrics`, `who_guidelines` | WHO Publications |
| WHO Model Formulary 2008 | `pharmacology` | WHO Publications |
| CDC Recommended Immunization Schedule for Children | `vaccination`, `cdc_guidelines` | CDC |
| WHO mhGAP Intervention Guide v2.0 | `nice_guidelines`, `who_guidelines` | WHO Publications |
| WHO ANC Recommendations for a Positive Pregnancy Experience | `ob_gyn`, `who_guidelines` | WHO Publications |

### 17.4 Update Mechanism

```python
# On startup, check GitHub Releases API (user consent required on first check):
RELEASES_URL = "https://api.github.com/repos/{org}/mediassist-pro/releases/latest"

def check_for_update(current_version: str) -> Optional[str]:
    response = httpx.get(RELEASES_URL, timeout=5.0)
    latest   = response.json()["tag_name"]
    if semver.compare(latest, current_version) > 0:
        return latest
    return None
```

On new version: download zip from GitHub Releases, extract, run Alembic migrations, restart app.

---

## SECTION 18: COMPREHENSIVE RESOURCE LIBRARY (350+ RESOURCES)

### A. NVIDIA NIM & AI Infrastructure

1. NVIDIA NIM API Documentation — https://docs.api.nvidia.com
2. NVIDIA NIM Model Catalog — https://build.nvidia.com/explore/discover
3. `nvidia/llama-3.1-nemotron-70b-instruct` page — https://build.nvidia.com/nvidia/llama-3_1-nemotron-70b-instruct
4. `nvidia/nemotron-4-340b-instruct` page — https://build.nvidia.com/nvidia/nemotron-4-340b-instruct
5. `meta/llama-3.3-70b-instruct` page — https://build.nvidia.com/meta/llama-3_3-70b-instruct
6. `meta/llama-3.3-8b-instruct` page — https://build.nvidia.com/meta/llama-3_3-8b-instruct
7. `nvidia/nv-embed-v1` embedding page — https://build.nvidia.com/nvidia/nv-embed-v1
8. `nvidia/nv-rerank-qa-mistral-4b:1` page — https://build.nvidia.com/nvidia/nv-rerank-qa-mistral-4b
9. `mistralai/mixtral-8x7b-instruct-v0.1` page — https://build.nvidia.com/mistralai/mixtral-8x7b-instruct-v0.1
10. OpenAI Python SDK (NIM-compatible) — https://github.com/openai/openai-python
11. NVIDIA NIM Authentication Guide — https://docs.api.nvidia.com/nim/reference/authentication
12. NVIDIA NIM Rate Limits Reference — https://docs.api.nvidia.com/nim/reference/limits
13. `instructor` library (structured LLM output) — https://python.useinstructor.com
14. instructor GitHub — https://github.com/jxnl/instructor
15. Tenacity retry library — https://tenacity.readthedocs.io
16. HTTPX async HTTP — https://www.python-httpx.org
17. BioMistral-7B-DARE GGUF (offline model) — https://huggingface.co/MaziyarPanahi/BioMistral-7B-DARE-GGUF
18. llama-cpp-python — https://github.com/abetlen/llama-cpp-python
19. NVIDIA Healthcare NIM use cases — https://www.nvidia.com/en-us/healthcare/nim
20. AsyncIO Python docs — https://docs.python.org/3/library/asyncio.html

### B. Python Desktop — PySide6 / Qt6

21. PySide6 official documentation — https://doc.qt.io/qtforpython-6
22. PySide6 Qt Widgets API — https://doc.qt.io/qtforpython-6/PySide6/QtWidgets
23. PySide6 Signals and Slots — https://doc.qt.io/qtforpython-6/tutorials/basictutorial/signals_and_slots.html
24. PySide6 Model/View architecture — https://doc.qt.io/qtforpython-6/overviews/model-view-programming.html
25. PySide6 threading (QThread) — https://doc.qt.io/qtforpython-6/tutorials/multithreading/index.html
26. Qt SVG rendering — https://doc.qt.io/qt-6/qtsvg-index.html
27. Qt WebEngine (HTML report preview) — https://doc.qt.io/qt-6/qtwebengine-index.html
28. PySide6 Charts — https://doc.qt.io/qtforpython-6/PySide6/QtCharts
29. Qt Accessibility — https://doc.qt.io/qt-6/accessible.html
30. Qt Style Sheets reference — https://doc.qt.io/qt-6/stylesheet-reference.html
31. Pytest-qt testing framework — https://pytest-qt.readthedocs.io
32. PyInstaller with PySide6 — https://pyinstaller.org/en/stable/hooks-config.html
33. NSIS installer system — https://nsis.sourceforge.io/Docs
34. PySide6 installation guide — https://doc.qt.io/qtforpython-6/quickstart.html
35. Qt Fusion style documentation — https://doc.qt.io/qt-6/gallery.html

### C. LangChain & RAG

36. LangChain documentation — https://python.langchain.com/docs
37. LangChain RAG tutorial — https://python.langchain.com/docs/tutorials/rag
38. LangChain agents — https://python.langchain.com/docs/how_to/agent_executor
39. LangChain document loaders — https://python.langchain.com/docs/integrations/document_loaders
40. LangChain RecursiveCharacterTextSplitter — https://python.langchain.com/docs/how_to/recursive_text_splitter
41. LangChain Chroma integration — https://python.langchain.com/docs/integrations/vectorstores/chroma
42. LangChain contextual compression retriever — https://python.langchain.com/docs/how_to/contextual_compression
43. LangChain NIM integration — https://python.langchain.com/docs/integrations/providers/nvidia
44. LangChain LCEL (expression language) — https://python.langchain.com/docs/concepts/lcel
45. LangSmith (LLM observability) — https://smith.langchain.com/docs
46. LlamaIndex documentation — https://docs.llamaindex.ai
47. LlamaIndex RAG pipeline — https://docs.llamaindex.ai/en/stable/understanding/rag
48. LlamaIndex metadata filtering — https://docs.llamaindex.ai/en/stable/module_guides/storing/metadata_extraction
49. LlamaIndex NIM integration — https://docs.llamaindex.ai/en/stable/examples/llm/nvidia_nim
50. LlamaIndex rerankers — https://docs.llamaindex.ai/en/stable/module_guides/querying/node_postprocessors/rerankers

### D. Vector Databases

51. ChromaDB documentation — https://docs.trychroma.com
52. ChromaDB Python client API — https://docs.trychroma.com/reference/py-client
53. ChromaDB metadata filtering — https://docs.trychroma.com/guides/usage-guide#filtering-by-metadata
54. ChromaDB persistent storage — https://docs.trychroma.com/guides/usage-guide#initiating-a-persistent-chroma-client
55. ChromaDB multi-tenancy — https://docs.trychroma.com/guides/multi-tenancy
56. ChromaDB embedding functions — https://docs.trychroma.com/guides/embeddings
57. FAISS documentation — https://faiss.ai/index.html
58. FAISS Python bindings — https://github.com/facebookresearch/faiss/wiki/Getting-started
59. Qdrant documentation (alternative) — https://qdrant.tech/documentation
60. Weaviate documentation (alternative) — https://weaviate.io/developers/weaviate

### E. Document Processing

61. PyMuPDF documentation — https://pymupdf.readthedocs.io
62. PyMuPDF text extraction — https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_text
63. pdfplumber documentation — https://github.com/jsvine/pdfplumber
64. pdfplumber table extraction — https://github.com/jsvine/pdfplumber#extracting-tables
65. python-docx documentation — https://python-docx.readthedocs.io
66. OpenPyXL documentation — https://openpyxl.readthedocs.io
67. Pytesseract OCR — https://github.com/madmaze/pytesseract
68. Tesseract OCR engine — https://tesseract-ocr.github.io
69. Pillow image processing — https://pillow.readthedocs.io
70. EbookLib EPUB — https://github.com/aerkalov/ebooklib
71. chardet encoding detection — https://chardet.readthedocs.io
72. Pandas documentation — https://pandas.pydata.org/docs
73. HL7apy — https://github.com/crs4/hl7apy
74. SMART on FHIR Python client — https://github.com/smart-on-fhir/client-py
75. HL7 FHIR R4 specification — https://www.hl7.org/fhir/R4

### F. Database & Security

76. SQLAlchemy documentation — https://docs.sqlalchemy.org/en/20
77. SQLAlchemy ORM tutorial — https://docs.sqlalchemy.org/en/20/tutorial/orm_tutorial.html
78. Alembic migrations tutorial — https://alembic.sqlalchemy.org/en/latest/tutorial.html
79. SQLite documentation — https://www.sqlite.org/docs.html
80. SQLCipher (AES-256 SQLite) — https://www.zetetic.net/sqlcipher
81. pysqlcipher3 Python binding — https://github.com/coleifer/sqlcipher3
82. Python cryptography library — https://cryptography.io/en/latest
83. keyring Python library — https://keyring.readthedocs.io
84. Windows DPAPI documentation — https://docs.microsoft.com/en-us/windows/win32/api/dpapi
85. Argon2-cffi password hashing — https://argon2-cffi.readthedocs.io
86. OWASP Cryptographic Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
87. OWASP Session Management — https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
88. HIPAA Security Rule — https://www.hhs.gov/hipaa/for-professionals/security/index.html
89. GDPR text — https://gdpr-info.eu
90. ISO 27001 overview — https://www.iso.org/isoiec-27001-information-security.html

### G. WHO Guidelines (Free, Public Domain)

91. WHO Pocket Book of Hospital Care for Children, 2nd Ed — https://www.who.int/publications/i/item/9789241548373
92. WHO Emergency Triage Assessment and Treatment (ETAT) — https://www.who.int/publications/i/item/emergency-triage-assessment-and-treatment-(etat)
93. WHO IMCI — https://www.who.int/publications/i/item/9789241550543
94. WHO Model Formulary 2008 — https://www.who.int/publications/i/item/978924154782
95. WHO ANC Recommendations — https://www.who.int/publications/i/item/9789241549912
96. WHO STI Treatment Guidelines 2016 — https://www.who.int/publications/i/item/9789241549806
97. WHO Malaria Treatment Guidelines 2022 — https://www.who.int/publications/i/item/9789240083608
98. WHO TB Treatment Guidelines — https://www.who.int/publications/i/item/9789240046758
99. WHO HIV/ART Guidelines 2021 — https://www.who.int/publications/i/item/9789240031593
100. WHO mhGAP Intervention Guide v2.0 — https://www.who.int/publications/i/item/9789241549790
101. WHO ICOPE — https://www.who.int/publications/i/item/9789241514996
102. WHO Surgical Care at District Hospital — https://www.who.int/publications/i/item/surgical-care-at-the-district-hospital
103. WHO IMAI (Adult/Adolescent) — https://www.who.int/publications/i/item/9789241547253
104. WHO Immunization Handbook 2019 — https://www.who.int/publications/i/item/9789241549974
105. WHO Nutrition Guidelines — https://www.who.int/teams/nutrition-food-safety
106. WHO HEARTS Technical Package (CVD) — https://www.who.int/publications/i/item/hearts-technical-package
107. WHO Integrated Eye Care — https://www.who.int/health-topics/blindness-and-vision-loss
108. WHO Deafness & Hearing Loss guidelines — https://www.who.int/health-topics/hearing-loss
109. WHO Oral Health guidelines — https://www.who.int/health-topics/oral-health
110. WHO Palliative Care guidelines — https://www.who.int/news-room/fact-sheets/detail/palliative-care

### H. CDC Guidelines

111. CDC Childhood Immunization Schedule — https://www.cdc.gov/vaccines/schedules/hcp/imz/child-adolescent.html
112. CDC Adult Immunization Schedule — https://www.cdc.gov/vaccines/schedules/hcp/imz/adult.html
113. CDC Sepsis Resources — https://www.cdc.gov/sepsis
114. CDC STD Treatment Guidelines 2021 — https://www.cdc.gov/std/treatment-guidelines/default.htm
115. CDC Influenza guidelines — https://www.cdc.gov/flu/professionals/antivirals
116. CDC Traveler's Health — https://wwwnc.cdc.gov/travel
117. CDC MASS CASUALTY SALT triage — https://www.cdc.gov/masscasualties/salt.html
118. CDC Rabies Post-Exposure Prophylaxis — https://www.cdc.gov/rabies/specific_groups/hcp/ppe_who_what.html
119. CDC Vector-borne disease guidelines — https://www.cdc.gov/niosh/topics/vector-borne
120. CDC Hepatitis B management — https://www.cdc.gov/hepatitis/hbv

### I. NIH & NCBI

121. NCBI Bookshelf (free medical texts) — https://www.ncbi.nlm.nih.gov/books
122. MedlinePlus Medical Encyclopedia — https://medlineplus.gov/encyclopedia.html
123. NIH Rare Disease Database — https://rarediseases.info.nih.gov
124. PubMed Central Open Access — https://www.ncbi.nlm.nih.gov/pmc
125. NIH National Cancer Institute — https://www.cancer.gov/publications/patient-education
126. NHLBI Heart Lung Blood guidelines — https://www.nhlbi.nih.gov/health-topics
127. NIDDK Diabetes guidelines — https://www.niddk.nih.gov/health-information
128. NIH MedlinePlus Drug Information — https://medlineplus.gov/druginfo
129. NIH Office of Dietary Supplements — https://ods.od.nih.gov
130. Clinical Trials database — https://clinicaltrials.gov

### J. NICE (UK) Guidelines

131. NICE Clinical Guidelines — https://www.nice.org.uk/guidance/conditions-and-diseases
132. NICE CKS (Clinical Knowledge Summaries) — https://cks.nice.org.uk
133. NICE Guideline NG185 (COVID-19 management) — https://www.nice.org.uk/guidance/ng185
134. NICE NG45 (Sepsis) — https://www.nice.org.uk/guidance/ng51
135. NICE Depression Guidelines — https://www.nice.org.uk/guidance/ng222
136. NICE Hypertension Guidelines — https://www.nice.org.uk/guidance/ng136
137. NICE Asthma Guidelines — https://www.nice.org.uk/guidance/ng80
138. NICE Diabetes (Type 2) — https://www.nice.org.uk/guidance/ng28
139. NICE COPD Guidelines — https://www.nice.org.uk/guidance/ng115
140. NICE Antenatal Care — https://www.nice.org.uk/guidance/ng201

### K. Pediatric Resources

141. Nelson Textbook of Pediatrics (NCBI chapters) — https://www.ncbi.nlm.nih.gov/books/NBK554775
142. AAP Red Book 2024 (infectious disease pediatrics) — https://redbook.solutions.aap.org
143. AAP Bright Futures guidelines — https://brightfutures.aap.org
144. WHO Child Growth Standards — https://www.who.int/tools/child-growth-standards
145. WHO Growth Chart tools — https://www.who.int/tools/child-growth-standards/software
146. IAP (India) vaccination schedule — https://iapindia.org/vaccination-schedule
147. Pediatric GCS scale reference — https://www.gcsscale.com
148. APGAR score calculator reference — https://www.mdcalc.com/calc/3961/apgar-score
149. PEDSS Pediatric Score — https://www.pedsscore.com
150. WHO IMCI chart booklet — https://apps.who.int/iris/handle/10665/42939

### L. Obstetrics & Gynecology

151. Williams Obstetrics 26th Ed (excerpts) — https://www.mcgraw-hill.com/medical/williams-obstetrics
152. ACOG Clinical Practice Bulletins — https://www.acog.org/clinical/clinical-guidance
153. FIGO guidelines — https://www.figo.org/resources/figo-guidelines
154. WHO ANC Model — https://www.who.int/publications/i/item/9789241549912
155. WHO Obstetric Fistula guidelines — https://www.who.int/publications/i/item/9789241503020
156. ACOG Postpartum Hemorrhage bulletin — https://www.acog.org/clinical/clinical-guidance/practice-bulletin/articles/2017/10/postpartum-hemorrhage
157. WHO Safe Childbirth Checklist — https://www.who.int/publications/i/item/safe-childbirth-checklist
158. EPDS (Edinburgh Postnatal Depression Scale) — https://www.mdcalc.com/calc/4005/edinburgh-postnatal-depression-scale-epds
159. WHO PMTCT guidelines — https://www.who.int/publications/i/item/9789241550550
160. Pre-eclampsia Foundation resources — https://www.preeclampsia.org/health-information

### M. Emergency Medicine & Critical Care

161. Tintinalli's Emergency Medicine excerpts — https://www.ncbi.nlm.nih.gov/books
162. ATLS (Advanced Trauma Life Support) overview — https://www.facs.org/quality-programs/trauma/education/atls
163. ERC Guidelines 2021 — https://www.erc.edu/guidelines
164. AHA/ACLS guidelines — https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines
165. AHA/PALS guidelines — https://cpr.heart.org
166. BLS guidelines — https://cpr.heart.org
167. Sepsis-3 definitions (JAMA) — https://jamanetwork.com/journals/jama/fullarticle/2492881
168. SOFA Score calculator — https://www.mdcalc.com/calc/691/sequential-organ-failure-assessment-sofa-score
169. qSOFA Score — https://www.mdcalc.com/calc/3170/quick-sofa-qsofa-score-sepsis
170. HEART Score (chest pain) — https://www.mdcalc.com/calc/1752/heart-score-major-cardiac-events
171. Wells Score (DVT) — https://www.mdcalc.com/calc/362/wells-criteria-dvt
172. Wells Score (PE) — https://www.mdcalc.com/calc/115/wells-criteria-pulmonary-embolism
173. GCS Calculator — https://www.gcsscale.com
174. ABCD2 Score (TIA) — https://www.mdcalc.com/calc/715/abcd2-score-tia
175. START Triage system — https://www.jems.com/patient-care/start-triage
176. ACEP clinical policies — https://www.acep.org/patient-care/clinical-policies
177. UpToDate (for format reference, not copying) — https://www.uptodate.com
178. WHO Emergency Care Framework — https://www.who.int/emergencies/emergency-care
179. Surviving Sepsis Campaign — https://www.sccm.org/SurvivingS sepsisCampaign
180. NICE Sepsis Guideline NG51 — https://www.nice.org.uk/guidance/ng51

### N. Cardiology

181. ESC Guidelines (free summaries) — https://www.escardio.org/Guidelines
182. AHA/ACC STEMI Guidelines — https://www.ahajournals.org/doi/10.1161/CIR.0000000000001168
183. AHA Heart Failure Guidelines — https://www.ahajournals.org
184. HEARTS Package WHO (hypertension) — https://www.who.int/publications/i/item/hearts-technical-package
185. Canadian Cardiovascular Society — https://ccs.ca/guidelines
186. ECG Interpretation guide — https://litfl.com/ecg-library
187. CHADS2/CHA2DS2-VASc score — https://www.mdcalc.com/calc/801/cha2ds2-vasc-score-afib-stroke-risk
188. TIMI Risk Score — https://www.mdcalc.com/calc/38/timi-risk-score-ua-nstemi
189. GRACE Score (ACS) — https://www.mdcalc.com/calc/1741/grace-acs-risk-mortality-calculator
190. Killip Classification — https://www.mdcalc.com/calc/1724/killip-classification-heart-failure

### O. Neurology

191. AHA/ASA Stroke guidelines — https://www.ahajournals.org
192. NIHSS (Stroke Scale) — https://www.mdcalc.com/calc/715/nih-stroke-scale-score-nihss
193. Hunt-Hess Subarachnoid — https://www.mdcalc.com/calc/3987/hunt-hess-classification-subarachnoid-hemorrhage
194. Epilepsy Foundation resources — https://www.epilepsy.com/professionals
195. WHO Headache Atlas — https://www.who.int/publications/i/item/headache-atlas
196. ICHD-3 Headache Classification — https://ichd-3.org
197. AAN Clinical Practice Guidelines — https://www.aan.com/Guidelines
198. Multiple Sclerosis guidelines — https://www.nationalmssociety.org/Treating-MS/Publications-Websites
199. Parkinson's Disease guidelines — https://www.parkinson.org/research/publications
200. ABCD2 TIA scoring — https://www.mdcalc.com/calc/715/abcd2-score-tia

### P. Psychiatry & Mental Health

201. PHQ-9 scale — https://www.mdcalc.com/calc/1725/phq-9-patient-health-questionnaire-9
202. GAD-7 scale — https://www.mdcalc.com/calc/1727/generalized-anxiety-disorder-7-item-scale-gad-7
203. CAGE Questionnaire (alcohol) — https://www.mdcalc.com/calc/1729/cage-questions-alcohol-use
204. Columbia Suicide Severity Rating Scale — https://cssrs.columbia.edu
205. MMSE (cognitive screen) — https://www.mdcalc.com/calc/1712/mini-mental-state-examination-mmse
206. DSM-5 diagnostic criteria excerpts — https://www.psychiatry.org/psychiatrists/practice/dsm
207. WHO ICD-11 Mental Health chapters — https://icd.who.int/en
208. AUDIT (Alcohol Use) — https://www.mdcalc.com/calc/1728/audit-c-alcohol-use-disorder-identification-test
209. YMRS (Mania Rating) — https://www.mdcalc.com/calc/1713/young-mania-rating-scale-ymrs
210. Mood Disorders Association resources — https://www.mooddisorderscanada.ca

### Q. Endocrinology & Diabetes

211. ADA Standards of Medical Care in Diabetes 2024 — https://diabetesjournals.org/care/issue/47/Supplement_1
212. WHO Diabetes Fact Sheet — https://www.who.int/news-room/fact-sheets/detail/diabetes
213. IDF Diabetes Atlas — https://diabetesatlas.org
214. NICE Type 1 Diabetes NG17 — https://www.nice.org.uk/guidance/ng17
215. NICE Type 2 Diabetes NG28 — https://www.nice.org.uk/guidance/ng28
216. Thyroid Disease Guidelines (ATA) — https://www.thyroid.org/professionals/ata-professional-guidelines
217. WHO Iodine Deficiency resources — https://www.who.int/health-topics/iodine-deficiency
218. International Society Endocrinology — https://www.isendo.org/guidelines
219. HOMA-IR calculator — https://www.mdcalc.com/calc/3316/homa-ir-insulin-resistance
220. HbA1c Conversion Tool — https://www.diabetes.co.uk/hba1c-units-converter.html

### R. Gastroenterology

221. ACG Clinical Guidelines — https://gi.org/guidelines
222. EASL Liver Guidelines — https://www.easl.eu/research/our-contributions/clinical-practice-guidelines
223. Rockall Score (GI bleeding) — https://www.mdcalc.com/calc/548/rockall-score-upper-gi-bleeding
224. Child-Pugh Score — https://www.mdcalc.com/calc/340/child-pugh-score-cirrhosis-mortality
225. MELD Score — https://www.mdcalc.com/calc/78/meld-score-model-end-stage-liver-disease
226. Blatchford Score — https://www.mdcalc.com/calc/1046/glasgow-blatchford-bleeding-score-gbs
227. Rome IV Criteria (functional GI) — https://theromefoundation.org
228. WHO Cholera management — https://www.who.int/news-room/fact-sheets/detail/cholera
229. WHO Diarrhea treatment — https://www.who.int/publications/i/item/9789241598415
230. Helicobacter pylori guidelines (EURAGE) — https://www.esge.com/esge-guidelines

### S. Pulmonology & Respiratory

231. GINA Asthma Report 2024 — https://ginasthma.org/reports
232. GOLD COPD Report 2024 — https://goldcopd.org/gold-reports
233. ATS/ERS Respiratory Guidelines — https://www.atsjournals.org
234. WHO TB Treatment Guidelines — https://www.who.int/publications/i/item/9789240046758
235. WHO Pneumonia Fact Sheet — https://www.who.int/news-room/fact-sheets/detail/pneumonia
236. CURB-65 Score (pneumonia) — https://www.mdcalc.com/calc/324/curb-65-score-pneumonia-severity
237. PSI/PORT Score (pneumonia) — https://www.mdcalc.com/calc/33/psi-port-score-pneumonia-severity-index-cap
238. Asthma Control Test — https://www.asthmacontroltest.com
239. CAT Score (COPD) — https://www.catestonline.org
240. BTS Pleural Disease Guidelines — https://www.brit-thoracic.org.uk/quality-improvement/guidelines

### T. Nephrology & Urology

241. KDIGO Kidney Disease Guidelines — https://kdigo.org/guidelines
242. KDOQI CKD Guidelines — https://www.kidney.org/professionals/guidelines/guidelines_commentaries
243. CKD-EPI GFR Calculator — https://www.mdcalc.com/calc/3939/ckd-epi-equations-glomerular-filtration-rate-gfr
244. Cockroft-Gault Calculator — https://www.mdcalc.com/calc/362/cockcroft-gault-equation
245. UACR Calculator — https://www.mdcalc.com/calc/3997/uacr-urine-albumin-to-creatinine-ratio
246. Urinary Tract Infection EAU Guidelines — https://uroweb.org/guidelines
247. Acute Kidney Injury Network (AKIN) criteria — https://www.kidney.org
248. WHO Kidney Disease resources — https://www.who.int/health-topics/kidney-disease
249. AUA BPH Guidelines — https://www.auanet.org/guidelines-and-quality/guidelines/benign-prostatic-hyperplasia
250. International Continence Society — https://www.ics.org/guidelines

### U. Orthopedics & Surgery

251. ATLS Manual overview — https://www.facs.org/quality-programs/trauma/education/atls
252. ACS NSQIP Surgical Risk Calculator — https://riskcalculator.facs.org
253. Ottawa Ankle Rules — https://www.mdcalc.com/calc/197/ottawa-ankle-rule
254. Ottawa Knee Rules — https://www.mdcalc.com/calc/198/ottawa-knee-rule
255. AO Foundation fracture classification — https://www.aofoundation.org
256. WHO Safe Surgery Checklist — https://www.who.int/publications/i/item/9789241598590
257. NICE Low Back Pain Guidelines NG59 — https://www.nice.org.uk/guidance/ng59
258. Caprini Score (VTE risk) — https://www.mdcalc.com/calc/10026/caprini-score-venous-thromboembolism-2005
259. American Academy Orthopaedic Surgeons — https://www.aaos.org/quality/clinical-quality-and-guidelines
260. Spine deformity classification (Lenke) — https://www.ncbi.nlm.nih.gov/books

### V. Infectious Disease

261. Sanford Guide (ID treatment reference) — https://www.sanfordguide.com
262. WHO Antimicrobial Resistance Global Action Plan — https://www.who.int/publications/i/item/9789241509763
263. WHO Essential Medicines List 2023 — https://www.who.int/publications/i/item/WHO-MHP-HPS-EML-2023.02
264. Infectious Diseases Society of America (IDSA) guidelines — https://www.idsociety.org/practice-guideline
265. WHO Dengue management — https://www.who.int/publications/i/item/9789241547871
266. WHO Malaria rapid test guidance — https://www.who.int/publications/i/item/malaria-rapid-diagnostic-test-performance
267. WHO Rabies guidelines — https://www.who.int/publications/i/item/who-trs-1012
268. UNAIDS HIV data — https://www.unaids.org/en/resources/documents/2024
269. Antibiogram interpretation guide — https://www.asm.org
270. WHO Antimicrobial Stewardship — https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance

### W. Dermatology

271. AAD Clinical Practice Guidelines — https://www.aad.org/member/clinical-quality/guidelines
272. British Association Dermatology guidelines — https://www.bad.org.uk/healthcare-professionals/clinical-standards/clinical-guidelines
273. DermNet NZ — https://dermnetnz.org (free reference)
274. WHO Skin conditions in humanitarian settings — https://www.who.int/news-room/fact-sheets/detail/dermatitis
275. Fitzpatrick Dermatology (NCBI excerpts) — https://www.ncbi.nlm.nih.gov/books
276. Wound Care NICE guideline — https://www.nice.org.uk/guidance/cg74
277. Leprosy Elimination project — https://www.who.int/news-room/fact-sheets/detail/leprosy
278. Scabies management WHO — https://www.who.int/news-room/fact-sheets/detail/scabies
279. Global Skin Disorders — https://www.ilds.org
280. Melanoma ABCDE criteria — https://www.aad.org/public/diseases/skin-cancer/find/at-risk/abcdes

### X. Ophthalmology & ENT

281. ICO International Council Ophthalmology — https://www.icoph.org/clinical/clinical-guidelines-policies
282. WHO Prevention of Blindness — https://www.who.int/health-topics/blindness-and-vision-loss
283. WHO Ear Care guidelines — https://www.who.int/publications/i/item/9789290226130
284. American Academy Ophthalmology guidelines — https://www.aao.org/education/clinical-statements
285. AAO-HNS Head & Neck Surgery guidelines — https://www.entnet.org/clinical-practice-and-quality
286. Snellen Chart visual acuity — reference at any ophthalmology guide
287. Tympanometry interpretation guide — https://www.entnet.org
288. Sensorineural Hearing Loss (ASHA) — https://www.asha.org/practice-portal/clinical-topics/hearing-loss
289. WHO Safe Ear Care — https://www.who.int/news-room/fact-sheets/detail/deafness-and-hearing-loss
290. Rhinosinusitis guidelines EPOS — https://www.rhinologyjournal.com

### Y. Utilities & Developer Tools

291. Python-dotenv — https://saurabh-kumar.com/python-dotenv
292. Loguru structured logging — https://loguru.readthedocs.io
293. Schedule task scheduler — https://schedule.readthedocs.io
294. Watchdog filesystem monitoring — https://python-watchdog.readthedocs.io
295. psutil system monitoring — https://psutil.readthedocs.io
296. pywin32 Windows API — https://github.com/mhammond/pywin32
297. win10toast notifications — https://github.com/jithurjacob/Windows-10-Toast-Notifications
298. Rich console library — https://rich.readthedocs.io
299. Hypothesis property-based testing — https://hypothesis.readthedocs.io
300. Faker synthetic data — https://faker.readthedocs.io
301. Ruff linter — https://docs.astral.sh/ruff
302. Black formatter — https://black.readthedocs.io
303. ReportLab PDF toolkit — https://www.reportlab.com/docs/reportlab-userguide.pdf
304. Jinja2 templating — https://jinja.palletsprojects.com
305. Pydantic v2 docs — https://docs.pydantic.dev/latest
306. semver Python library — https://python-semver.readthedocs.io

### Z. Medical Reference & ICD

307. ICD-10 browser — https://icd.who.int/browse10/2019/en
308. ICD-11 browser — https://icd.who.int/browse11/en
309. SNOMED CT browser — https://browser.ihtsdotools.org
310. LOINC codes reference — https://loinc.org
311. RxNorm drug database — https://www.nlm.nih.gov/research/umls/rxnorm
312. NDC drug codes — https://www.fda.gov/drugs/drug-approvals-and-databases/national-drug-code-database
313. Stedman's Medical Dictionary — https://stedmansonline.com
314. MedlinePlus encyclopedia — https://medlineplus.gov/encyclopedia.html
315. NCBI Bookshelf — https://www.ncbi.nlm.nih.gov/books
316. Cochrane Open Access — https://www.cochranelibrary.com/about/open-access
317. OpenDOAJ open journals — https://doaj.org
318. Global Health eLearning Center — https://www.globalhealthlearning.org
319. awesome-healthcare GitHub list — https://github.com/kakoni/awesome-healthcare
320. awesome-clinical-nlp — https://github.com/bionlp-hlt/awesome-clinical-nlp
321. MedEdPORTAL — https://www.mededportal.org
322. MDCalc (clinical scoring tools) — https://www.mdcalc.com
323. ClinCalc (drug dosing) — https://clincalc.com
324. Global Surgery Foundation — https://www.globalsurgeryfoundation.org
325. PHCPI Primary Health Care — https://improvingphc.org
326. Free Medical Books — https://freebooks4doctors.com
327. BioMedCentral Open Access — https://www.biomedcentral.com
328. PLOS Medicine Open Access — https://journals.plos.org/plosmedicine
329. Lancet Global Health (free access) — https://www.thelancet.com/journals/langlo/home
330. BMJ Global Health — https://gh.bmj.com

### Additional (331–355)

331. ATLS Protocols overview — https://www.facs.org
332. ACLS guidelines — https://cpr.heart.org
333. WHO Emergency Care Systems — https://www.who.int/emergencies/emergency-care
334. EM:RAP (Emergency Medicine) — https://www.emrap.org
335. MSF (Médecins Sans Frontières) Clinical Guidelines — https://medicalguidelines.msf.org
336. MSF Essential Drugs Guide — https://medicalguidelines.msf.org/viewport/EssDr/english
337. ICRC First Aid Manual — https://www.icrc.org/en/publication/4530-first-aid
338. Sphere Humanitarian Standards — https://spherestandards.org
339. UNHCR Health Information System — https://www.unhcr.org/health
340. Health Cluster Guidelines — https://www.who.int/health-cluster/guidance
341. Project ECHO tele-mentoring — https://hsc.unm.edu/echo
342. HINARI Access to Research — https://www.who.int/hinari/en
343. Global Health Observatory — https://www.who.int/data/gho
344. HMIS (Health Management Information) — https://dhis2.org
345. OpenMRS (Open Medical Record System) — https://openmrs.org
346. WHO OpenHIE specification — https://ohie.org
347. SNOMED clinical terms browser — https://browser.ihtsdotools.org
348. ClinicalKey Free Resources — https://www.clinicalkey.com
349. National Guideline Clearinghouse archive — https://effectivehealthcare.ahrq.gov
350. AHRQ Clinical Guidelines — https://www.ahrq.gov/prevention/guidelines
351. Murtagh's General Practice (NCBI) — https://www.ncbi.nlm.nih.gov/books/NBK493277
352. Oxford Handbook Clinical Medicine (NCBI excerpts) — https://www.ncbi.nlm.nih.gov/books
353. Harrison's Internal Medicine (NCBI excerpts) — https://www.ncbi.nlm.nih.gov/books/NBK8031
354. Kumar & Clark Clinical Medicine (NCBI) — https://www.ncbi.nlm.nih.gov/books
355. Davidson's Principles & Practice (NCBI) — https://www.ncbi.nlm.nih.gov/books

---

## SECTION 19: DOCTOR FIELD CONFIGURATION MATRIX — ALL SPECIALTIES (BONUS A)

> ★ **KEY FLAGS FOR THIS SECTION**
> - 21 specialties fully configured — facility enables only those relevant to their station
> - Each specialty defines: RAG collections, visit types, scoring tools, ICD chapter focus, special flags
> - Configuration stored in `config/doctor_fields.json` — editable by ADMIN role via settings UI
> - Specialty determines which ChromaDB collections are queried, which clinical scoring tools are embedded, and which ICD chapters are prioritized
> - Multiple specialties can be active simultaneously (e.g., a district hospital enables general + pediatrics + ob_gyn + emergency)

```json
{
  "active_specialties": ["general", "pediatrics", "ob_gyn", "emergency"],
  "specialties": {
    "general": {
      "display_name": "General / Family Medicine",
      "icon": "stethoscope.svg",
      "rag_collections": ["core_medicine", "who_guidelines", "pharmacology", "nice_guidelines"],
      "visit_types_enabled": ["GENERAL", "SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["PHQ9", "GAD7", "CAGE", "AUDIT", "SOFA_basic"],
      "icd_chapter_focus": "all",
      "special_flags": ["unexplained_weight_loss", "night_sweats", "fever_of_unknown_origin"]
    },
    "pediatrics": {
      "display_name": "Pediatrics",
      "icon": "child.svg",
      "rag_collections": ["pediatrics", "vaccination", "cdc_guidelines", "who_guidelines"],
      "visit_types_enabled": ["PEDIATRIC", "VACCINATION", "GENERAL", "FOLLOWUP"],
      "scoring_tools": ["APGAR", "GCS_pediatric", "PEDSS", "FLACC_pain", "WHO_growth_zscore"],
      "age_range_years": [0, 18],
      "weight_based_dosing_prompt": true,
      "growth_chart_integration": true,
      "icd_chapter_focus": ["XVI", "XVII", "XVIII", "A00-B99"],
      "special_flags": ["fever_infant_under_3_months", "faltering_growth", "developmental_concern", "non_accidental_injury_screen"]
    },
    "ob_gyn": {
      "display_name": "Obstetrics & Gynecology",
      "icon": "pregnant.svg",
      "rag_collections": ["ob_gyn", "who_guidelines", "pharmacology"],
      "visit_types_enabled": ["MATERNAL", "SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["EPDS", "APGAR_newborn", "BISHOP_score", "MODIFIED_EARLY_OBSTETRIC_WARNING"],
      "icd_chapter_focus": ["XV", "O00-O99"],
      "special_flags": ["preeclampsia_screen", "postpartum_hemorrhage", "fetal_movement_absent", "preterm_labor", "ectopic_risk"]
    },
    "emergency": {
      "display_name": "Emergency Medicine",
      "icon": "emergency.svg",
      "rag_collections": ["emergency", "core_medicine", "pharmacology"],
      "visit_types_enabled": ["SPECIFIC", "GENERAL"],
      "scoring_tools": ["GCS", "SOFA", "qSOFA", "HEART", "WELLS_DVT", "WELLS_PE", "TIMI", "NIHSS", "ABCD2", "START_TRIAGE"],
      "triage_mode_enabled": true,
      "fast_mode": true,
      "icd_chapter_focus": "all",
      "special_flags": ["sepsis_alert", "stroke_alert", "acs_alert", "trauma_alert", "anaphylaxis", "status_epilepticus"]
    },
    "internal_medicine": {
      "display_name": "Internal Medicine",
      "icon": "internal.svg",
      "rag_collections": ["core_medicine", "nih_guidelines", "who_guidelines", "pharmacology"],
      "visit_types_enabled": ["SPECIFIC", "GENERAL", "FOLLOWUP"],
      "scoring_tools": ["SOFA", "CURB65", "MELD", "CHILD_PUGH", "CKD_EPI", "CHADS2_VASC", "HOMA_IR"],
      "icd_chapter_focus": ["I00-I99", "J00-J99", "K00-K99", "E00-E99", "N00-N99"],
      "special_flags": ["signs_of_malignancy", "autoimmune_screen", "multiorgan_involvement"]
    },
    "surgery": {
      "display_name": "General Surgery",
      "icon": "surgery.svg",
      "rag_collections": ["surgery_orthopedics", "emergency", "pharmacology"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["ASA_classification", "CAPRINI_VTE", "ACS_NSQIP"],
      "icd_chapter_focus": ["K35-K38", "K40-K46", "C00-C99", "S00-T99"],
      "special_flags": ["peritonitis_signs", "bowel_obstruction", "surgical_site_infection", "anastomotic_leak_risk"]
    },
    "orthopedics": {
      "display_name": "Orthopedics & Trauma",
      "icon": "bone.svg",
      "rag_collections": ["surgery_orthopedics", "emergency"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["OTTAWA_ANKLE", "OTTAWA_KNEE", "AO_FRACTURE", "CAPRINI_VTE", "KOOS_score"],
      "icd_chapter_focus": ["S00-T99", "M00-M99"],
      "special_flags": ["open_fracture", "compartment_syndrome", "neurovascular_compromise", "spinal_cord_injury"]
    },
    "cardiology": {
      "display_name": "Cardiology",
      "icon": "heart.svg",
      "rag_collections": ["core_medicine", "who_guidelines", "nice_guidelines"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP", "GENERAL"],
      "scoring_tools": ["HEART", "TIMI", "GRACE", "CHADS2_VASC", "HAS_BLED", "NYHA_CLASS", "KILLIP"],
      "icd_chapter_focus": ["I00-I99"],
      "special_flags": ["acs_high_risk", "decompensated_heart_failure", "complete_heart_block", "aortic_dissection"]
    },
    "neurology": {
      "display_name": "Neurology",
      "icon": "brain.svg",
      "rag_collections": ["core_medicine", "nih_guidelines"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["GCS", "NIHSS", "ABCD2", "HUNT_HESS", "HUNT_HESS_SAH", "MMSE", "MoCA_brief"],
      "icd_chapter_focus": ["G00-G99", "I60-I69"],
      "special_flags": ["stroke_alert", "meningitis_signs", "raised_intracranial_pressure", "status_epilepticus"]
    },
    "dermatology": {
      "display_name": "Dermatology",
      "icon": "skin.svg",
      "rag_collections": ["core_medicine", "nice_guidelines"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["SCORAD_simplified", "DLQI_simplified"],
      "icd_chapter_focus": ["L00-L99"],
      "special_flags": ["melanoma_abcde_concern", "purpuric_rash", "necrotising_fasciitis_risk", "drug_reaction_severe"]
    },
    "psychiatry": {
      "display_name": "Psychiatry & Mental Health",
      "icon": "mental.svg",
      "rag_collections": ["nice_guidelines", "core_medicine", "who_guidelines"],
      "visit_types_enabled": ["MENTAL", "FOLLOWUP"],
      "scoring_tools": ["PHQ9", "GAD7", "AUDIT", "CAGE", "CSSRS", "YMRS", "PANSS_brief", "MMSE"],
      "icd_chapter_focus": ["F00-F99"],
      "special_flags": ["suicide_risk_high", "psychosis_first_episode", "manic_episode_severe", "self_harm_recent"]
    },
    "ophthalmology": {
      "display_name": "Ophthalmology",
      "icon": "eye.svg",
      "rag_collections": ["core_medicine"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["SNELLEN_VA_screen", "IOP_screen"],
      "icd_chapter_focus": ["H00-H59"],
      "special_flags": ["acute_angle_closure", "retinal_detachment", "vision_loss_sudden", "chemical_eye_injury"]
    },
    "ent": {
      "display_name": "ENT (Ear, Nose, Throat)",
      "icon": "ear.svg",
      "rag_collections": ["core_medicine", "nice_guidelines"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["TONSIL_grading", "PURE_TONE_screen"],
      "icd_chapter_focus": ["H60-H95", "J00-J99"],
      "special_flags": ["airway_compromise", "epistaxis_posterior", "facial_fracture"]
    },
    "urology": {
      "display_name": "Urology",
      "icon": "kidney.svg",
      "rag_collections": ["core_medicine", "nice_guidelines"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["IPSS_BPH", "CKD_EPI"],
      "icd_chapter_focus": ["N00-N99"],
      "special_flags": ["urosepsis", "acute_urinary_retention", "renal_colic_severe", "haematuria_sinister"]
    },
    "pulmonology": {
      "display_name": "Pulmonology / Respiratory",
      "icon": "lung.svg",
      "rag_collections": ["core_medicine", "nice_guidelines", "who_guidelines"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["CURB65", "PSI_PORT", "GOLD_COPD_stage", "ACT_asthma"],
      "icd_chapter_focus": ["J00-J99"],
      "special_flags": ["respiratory_failure_imminent", "pneumothorax_tension", "massive_haemoptysis"]
    },
    "endocrinology": {
      "display_name": "Endocrinology & Diabetes",
      "icon": "glucose.svg",
      "rag_collections": ["core_medicine", "nih_guidelines", "nice_guidelines"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP", "GENERAL"],
      "scoring_tools": ["HOMA_IR", "UKPDS_risk", "FRAX_simplified"],
      "icd_chapter_focus": ["E00-E99"],
      "special_flags": ["dka_signs", "hhs_signs", "hypoglycemia_severe", "adrenal_crisis", "thyroid_storm"]
    },
    "gastroenterology": {
      "display_name": "Gastroenterology",
      "icon": "gi.svg",
      "rag_collections": ["core_medicine", "nice_guidelines"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["MELD", "CHILD_PUGH", "ROCKALL", "BLATCHFORD", "HARVEY_BRADSHAW"],
      "icd_chapter_focus": ["K00-K99"],
      "special_flags": ["gi_bleed_upper_active", "peritonitis", "acute_liver_failure", "bowel_obstruction"]
    },
    "nephrology": {
      "display_name": "Nephrology / Renal",
      "icon": "kidney2.svg",
      "rag_collections": ["core_medicine", "nih_guidelines"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["CKD_EPI", "COCKROFT_GAULT", "UACR", "KDIGO_AKI"],
      "icd_chapter_focus": ["N00-N29"],
      "special_flags": ["aki_stage3", "hyperkalemia_severe", "hypertensive_emergency", "nephrotic_syndrome_complicated"]
    },
    "oncology": {
      "display_name": "Oncology",
      "icon": "oncology.svg",
      "rag_collections": ["core_medicine", "nih_guidelines"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["ECOG_performance", "KARNOFSKY", "NRS_pain_2002"],
      "icd_chapter_focus": ["C00-C99", "D00-D48"],
      "special_flags": ["neutropenic_fever", "spinal_cord_compression", "hypercalcemia_malignancy", "superior_vena_cava_syndrome"]
    },
    "rheumatology": {
      "display_name": "Rheumatology",
      "icon": "joint.svg",
      "rag_collections": ["core_medicine", "nice_guidelines"],
      "visit_types_enabled": ["SPECIFIC", "FOLLOWUP"],
      "scoring_tools": ["DAS28_simplified", "SLEDAI_simplified", "ACR_RA_2010"],
      "icd_chapter_focus": ["M00-M99"],
      "special_flags": ["septic_arthritis", "atlantoaxial_instability", "macrophage_activation", "lupus_nephritis_acute"]
    },
    "infectious_disease": {
      "display_name": "Infectious Disease",
      "icon": "virus.svg",
      "rag_collections": ["core_medicine", "who_guidelines", "cdc_guidelines", "vaccination"],
      "visit_types_enabled": ["SPECIFIC", "GENERAL", "FOLLOWUP"],
      "scoring_tools": ["qSOFA", "SOFA", "TSPOT_screen_note"],
      "icd_chapter_focus": ["A00-B99"],
      "special_flags": ["sepsis", "meningitis", "viral_hemorrhagic_fever", "tb_open", "malaria_severe"]
    },
    "palliative_care": {
      "display_name": "Palliative & Supportive Care",
      "icon": "palliative.svg",
      "rag_collections": ["core_medicine", "who_guidelines", "pharmacology"],
      "visit_types_enabled": ["FOLLOWUP", "GENERAL", "SPECIFIC"],
      "scoring_tools": ["ESAS_r", "PPS_palliative", "RASS_sedation"],
      "icd_chapter_focus": ["Z00-Z99", "C00-C99"],
      "special_flags": ["terminal_agitation", "pain_crisis_uncontrolled", "respiratory_secretions", "syringe_driver_needed"]
    }
  }
}
```

---

## SECTION 20: PROMPT ENGINEERING REFERENCE LIBRARY (BONUS B)

> ★ **KEY FLAGS FOR THIS SECTION**
> - All prompts use Jinja2 templating — no f-strings or string concatenation for prompts
> - Temperature is hardcoded to 0.1 for all medical prompts — never adjust above 0.3
> - Every prompt ends with the instruction: "Respond ONLY with valid JSON matching the schema. No preamble, no markdown fences, no commentary."
> - Nurse language requirement is mandatory in every round generation prompt
> - The physician brief prompt NEVER asks for drug doses — drug class only
> - Emergency prompt uses ROLE_FAST model only — speed is paramount over comprehensiveness

### 20.1 Master Round Generation Prompt Template

```jinja2
{# questionnaire/prompt_templates.py — Round generation master template #}

You are an expert clinical intake assistant specialized in {{ specialty }} medicine, trained to assist nursing staff in a humanitarian healthcare setting.

Your task: Generate EXACTLY {{ question_count }} MCQ questions for Round {{ round_number }} of 4 of a patient intake questionnaire.

PATIENT CONTEXT:
Age: {{ demographics.age_years }} years | Sex: {{ demographics.sex }} | Weight: {{ demographics.weight_kg|default('Unknown') }} kg
{% if patient_history %}
Known conditions: {{ patient_history.chronic_conditions | join(', ') | default('None') }}
Current medications: {{ patient_history.current_medications | join(', ') | default('None') }}
Allergies: {{ patient_history.allergies | join(', ') | default('None') }}
{% endif %}

VISIT TYPE: {{ visit_type }}

{% if previous_answers %}
PRIOR ROUND ANSWERS (context for this round):
{{ previous_answers | tojson(indent=2) }}
{% endif %}

{% if working_differentials %}
WORKING DIFFERENTIALS (refine toward these):
{% for d in working_differentials %}{{ loop.index }}. {{ d }}
{% endfor %}
{% endif %}

CLINICAL CONTEXT FROM GUIDELINES:
{{ rag_context }}

RULES (MUST FOLLOW ALL):
1. Generate EXACTLY {{ question_count }} questions. No more, no fewer.
2. All questions MUST be answerable by a nurse without clinical examination equipment.
3. Every question using medical terminology MUST include a plain-language explanation in the `nurse_explanation` field.
4. If any answer option would indicate a clinical emergency, set `is_red_flag: true` for that option.
5. If any answer option suggests a moderate concern requiring physician attention, set `is_amber_flag: true`.
6. Options for radio/checkbox questions must be 3–5 in number, mutually exclusive for radio, inclusive for checkbox.
7. Base ALL questions on the provided clinical context. Do not introduce clinical facts not present in the RAG context or patient history.
8. Do NOT ask questions that have already been answered in prior rounds.
9. Questions must be culturally neutral, free of assumptions about literacy or education level.
10. For Round {{ round_number }}, focus on: {{ round_focus }}.

RESPOND ONLY WITH VALID JSON matching the QuestionnaireRound schema. No preamble, no markdown fences, no commentary outside the JSON object.
```

### 20.2 Physician Brief Generation Prompt

```jinja2
{# report/prompt_templates.py — Physician brief master template #}

You are an expert clinician generating a structured physician brief from nurse-collected patient data. You are writing for a physician, not a nurse — use precise clinical language.

PATIENT: Case {{ case_number }} | {{ demographics.age_years }}yo {{ demographics.sex }}

CHIEF COMPLAINT & QUESTIONNAIRE SUMMARY:
{{ questionnaire_summary }}

VITAL SIGNS:
{{ vital_signs | tojson(indent=2) }}

PATIENT HISTORY (from records):
{{ patient_history | tojson(indent=2) }}

EVIDENCE BASE (RAG-retrieved from clinical guidelines):
{{ rag_context }}

SPECIALTY CONTEXT: {{ specialty }}

CRITICAL CONSTRAINTS:
- Every differential diagnosis MUST cite a specific source from the RAG context above.
- Use exact ICD-10 format: letter + 2 digits + optional decimal (e.g., I21.9, J18.0)
- Do NOT suggest specific drug doses or drug names. Suggest drug CLASSES only (e.g., "beta-blocker", "macrolide antibiotic").
- Flag anything that could indicate a time-sensitive emergency with severity = "RED".
- If RAG context is insufficient to support a claim, explicitly state this.
- Confidence note: honestly assess the quality and completeness of data.
- Do NOT repeat information between sections.
- Suggested examination must be physical examination maneuvers only — no lab tests in this section.
- Suggested investigations: lab + imaging + bedside tests only — no physical exam here.

OUTPUT: ONLY valid JSON matching the PhysicianBrief Pydantic schema. No preamble, no markdown.
```

### 20.3 ICD Code Assignment Prompt

```jinja2
{# report/icd_mapper.py — ICD code structured prompt #}

Map the following clinical diagnosis to its ICD-10 and ICD-11 codes.
Return ONLY a JSON object: {"icd_10": "X00.0", "icd_11": "XX.XX.XX", "confidence": 0.95}
Use exact ICD-10 format: letter + 2 digits + optional .digit
If uncertain, use the most accurate parent code.
Diagnosis: {{ diagnosis_name }}
RESPOND ONLY WITH JSON.
```

### 20.4 Emergency Triage Note Prompt

```jinja2
{# report/emergency_prompt.py — Fast emergency note #}

CRITICAL EMERGENCY INTAKE — Generate a structured triage note in under 10 seconds.
Patient: {{ age }}yo {{ sex }} | Time: {{ timestamp }}
Triggered flags: {{ flags | join(', ') }}
Available data: {{ available_data | tojson }}

Output format (STRICTLY as JSON):
{
  "presenting_concern": "one sentence",
  "triggered_flags": ["list", "of", "flags"],
  "preliminary_differentials": [{"condition": "name", "icd_10": "X00.0", "urgency": "immediate/urgent/less_urgent"}],
  "immediate_actions": ["action 1", "action 2"],
  "vital_signs_needed": ["list", "of", "vitals", "to", "measure"],
  "do_not_delay": "specific action if life threat confirmed"
}
```

---

## SECTION 21: DATA PORT & LEGACY IMPORT SYSTEM (BONUS C)

> ★ **KEY FLAGS FOR THIS SECTION**
> - The background processor is a watchdog daemon — runs continuously, processes new files during idle time
> - Deduplication uses name+DOB match, phone match, and prior case number match before creating new records
> - OCR is applied to all image-format documents — quality threshold check before NLP extraction
> - All imported records are flagged with `source = 'import'` — distinguishable from manually entered data
> - Failed imports move to `knowledge_base/failed/` with a JSON error log
> - HL7 and FHIR parsers extract: ADT (demographics), ORU (lab results), OBX (observations), VXU (vaccinations)

### 21.1 Supported Import Formats

| Format | Use Case | Parser Module | Notes |
|--------|----------|-------------|-------|
| `.csv` | Bulk patient registration, lab export | `csv_parser.py` | Column mapping wizard on first import |
| `.xlsx` | Vaccination records, lab results, drug sheets | `excel_parser.py` | Sheet-by-sheet processing |
| `.json` | Modern EHR exports, FHIR bundles | `json_parser.py` + `fhir_parser.py` | Auto-schema detection |
| `.pdf` | Scanned patient files, discharge summaries | `pdf_records_parser.py` | PyMuPDF + OCR + LLM NLP extraction |
| `.docx` | Clinical notes, referral letters | `docx_records_parser.py` | python-docx + LLM NLP extraction |
| HL7 v2 `.hl7` | Legacy hospital systems | `hl7_parser.py` | ADT, ORU, OBX, VXU messages |
| HL7 FHIR `.json`/`.xml` | Modern EHR systems | `fhir_parser.py` | R4 patient, observation, immunization resources |
| `.txt` | Freeform clinical notes | `generic_text_parser.py` | LLM NLP extraction |
| `.ods` | LibreOffice spreadsheets | `excel_parser.py` (openpyxl) | Same pipeline as xlsx |

### 21.2 Background Processor Daemon

```python
# data_port/background_processor.py

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from loguru import logger
from nim.nim_key_manager import NIMKeyManager
from database.connection import get_session

INCOMING_DIR = Path("knowledge_base/incoming")
PROCESSED_DIR = Path("knowledge_base/processed")
FAILED_DIR    = Path("knowledge_base/failed")

class BackgroundProcessor(FileSystemEventHandler):
    def __init__(self, key_manager: NIMKeyManager):
        self.key_manager = key_manager
        self.is_active   = False    # Only runs when no nurse session is active

    def on_created(self, event):
        if event.is_directory or not self.is_active:
            return
        file_path = Path(event.src_path)
        self.process_file(file_path)

    def process_file(self, path: Path):
        suffix  = path.suffix.lower()
        parsers = {
            ".csv":  CsvParser, ".xlsx": ExcelParser,
            ".json": JsonParser, ".hl7":  HL7Parser,
            ".pdf":  PDFRecordsParser, ".docx": DocxRecordsParser,
            ".txt":  GenericTextParser
        }
        parser_cls = parsers.get(suffix)
        if not parser_cls:
            logger.warning(f"No parser for {path.name}; moving to failed/")
            path.rename(FAILED_DIR / path.name)
            return

        try:
            parser  = parser_cls(self.key_manager)
            records = parser.parse(path)
            stats   = self._upsert_records(records)
            logger.info(f"Processed {path.name}: {stats['new']} new, {stats['updated']} updated, {stats['failed']} failed")
            path.rename(PROCESSED_DIR / path.name)
        except Exception as e:
            logger.error(f"Failed to process {path.name}: {e}")
            path.rename(FAILED_DIR / path.name)

    def _upsert_records(self, records: list[dict]) -> dict:
        stats = {"new": 0, "updated": 0, "failed": 0}
        with get_session() as session:
            for rec in records:
                if self._dedup_check(session, rec):
                    self._update_patient(session, rec)
                    stats["updated"] += 1
                else:
                    self._create_patient(session, rec)
                    stats["new"] += 1
        return stats
```

### 21.3 LLM-Based NLP Entity Extraction for Unstructured Documents

For scanned PDFs and freeform text, an LLM extraction step is used:

```python
EXTRACTION_PROMPT = """
Extract all patient information from the following clinical text.
Return ONLY valid JSON with these fields (omit fields if not found):
{
  "patient_name": null,
  "date_of_birth": null,       // ISO 8601 format: YYYY-MM-DD
  "sex": null,                 // "M", "F", or "O"
  "contact_number": null,
  "diagnoses": [],             // list of condition names (strings)
  "icd_codes": [],             // ICD-10 codes if present
  "medications": [],           // {"drug": str, "dose": str, "frequency": str}
  "allergies": [],             // {"allergen": str, "reaction": str, "severity": str}
  "vaccinations": [],          // {"vaccine": str, "date": "YYYY-MM-DD", "dose": int}
  "lab_results": [],           // {"test": str, "value": str, "unit": str, "date": "YYYY-MM-DD"}
  "visit_dates": [],
  "case_number": null
}
Clinical text:
{{ document_chunk }}
RESPOND ONLY WITH JSON.
"""
```

---

## SECTION 22: EMERGENCY TRIAGE PROTOCOL MODULE (BONUS D)

> ★ **KEY FLAGS FOR THIS SECTION**
> - Emergency button 🚨 is permanently visible in the toolbar — single click, no confirmation dialog
> - Emergency report generated in < 10 seconds using ROLE_FAST model only
> - Full-screen overlay with audio chime prevents the nurse from missing the escalation
> - Emergency note is one-click printable — designed for immediate hand-off to physician
> - All emergency sessions flagged in the audit log and reportable to facility admin
> - Emergency protocol does NOT require completing all 4 questionnaire rounds

### 22.1 Activation Triggers

| Trigger Source | Trigger Condition |
|---------------|-----------------|
| Round 1–4 MCQ answers | Any option with `is_red_flag: true` selected |
| Vital signs capture | Any vital outside critical threshold (configurable per age group) |
| Nurse manual activation | 🚨 Emergency button in toolbar |
| Critical vital signs auto-detection | SpO2 < 90%, HR > 150 or < 40, SBP < 80 or > 200, temp > 40.5°C |

### 22.2 Emergency Screen Behavior

1. All current questionnaire progress is saved to a partial session record
2. Full-screen overlay (red/orange gradient background) appears immediately
3. Audio chime plays (`.wav` file in `assets/` — configurable volume or disable)
4. Emergency triage note generated in background using ROLE_FAST (target: < 10 seconds)
5. When note ready: displays on screen in large legible format (font 18px minimum)
6. "Print Emergency Note" button (large, white on red) — one click prints to default printer
7. Session marked `is_emergency = TRUE` in `visits` table
8. Continue questionnaire button available for minor false triggers

### 22.3 Emergency Triage Note Format

```
══════════════════════════════════════════════════════════
EMERGENCY TRIAGE NOTE — MediAssist Pro | {FACILITY_NAME}
══════════════════════════════════════════════════════════
Case: {CASE_NUMBER} | Time: {HH:MM} | Nurse: {NURSE_ID}
Patient: {FIRST_NAME} {LAST_INITIAL}. | {AGE}yo {SEX}

PRESENTING CONCERN: {presenting_concern_one_sentence}

TRIGGERED FLAGS:
  🔴 {flag_1}
  🔴 {flag_2}  [if multiple flags]

VITAL SIGNS (recorded):
  BP: {systolic}/{diastolic} | HR: {hr} | RR: {rr} | SpO2: {spo2}% | Temp: {temp}°C

PRELIMINARY DIFFERENTIAL (AI-generated — verify clinically):
  1. [HIGH]     {differential_1} — {icd_10_1}
  2. [MODERATE] {differential_2} — {icd_10_2}
  3. [LOW]      {differential_3} — {icd_10_3}

SUGGESTED IMMEDIATE ACTIONS:
  • {action_1}
  • {action_2}
  • {action_3}

[EVIDENCE: {source_citation}]

*** PHYSICIAN REVIEW REQUIRED — PRELIMINARY AI ASSESSMENT ONLY ***
══════════════════════════════════════════════════════════
```

---

## SECTION 23: CLINICAL SCORING TOOLS REFERENCE (BONUS E)

> ★ **KEY FLAGS FOR THIS SECTION**
> - All scoring tools are embedded as structured input widgets within the questionnaire rounds (not as separate screens)
> - Scores are calculated locally in Python — no API call needed for calculation
> - Score results are automatically injected into the physician brief context
> - Tool activation is triggered by specialty config (see Section 19) — a tool only appears if the active specialty includes it
> - Scores with clinical action thresholds are color-coded in the physician brief

| Score/Tool | Clinical Domain | Calculation Location | Action Threshold | Notes |
|-----------|----------------|---------------------|-----------------|-------|
| PHQ-9 | Depression | `scoring/phq9.py` | ≥10 = Moderate; ≥20 = Severe | 9 questions, 0–27 scale |
| GAD-7 | Anxiety | `scoring/gad7.py` | ≥10 = Moderate | 7 questions, 0–21 scale |
| CAGE | Alcohol use | `scoring/cage.py` | ≥2 = Probable dependence | 4 binary questions |
| AUDIT-C | Alcohol use | `scoring/audit_c.py` | ≥3F/≥4M = Harmful use | 3 questions |
| GCS | Consciousness | `scoring/gcs.py` | ≤8 = Comatose (INTUBATE) | Eye+Verbal+Motor |
| SOFA | Organ dysfunction | `scoring/sofa.py` | ≥2 = Organ dysfunction | 6 organ systems |
| qSOFA | Sepsis screen | `scoring/qsofa.py` | ≥2 = Sepsis suspected | 3 criteria |
| HEART | Chest pain risk | `scoring/heart.py` | ≥7 = High risk (admit + ACS workup) | 5 criteria |
| WELLS DVT | DVT probability | `scoring/wells_dvt.py` | ≥2 = High probability | Point system |
| WELLS PE | PE probability | `scoring/wells_pe.py` | >4 = PE likely | Point system |
| CURB-65 | Pneumonia severity | `scoring/curb65.py` | ≥2 = Hospital admission | 5 criteria |
| APGAR | Newborn assessment | `scoring/apgar.py` | ≤6 at 5min = Resuscitation | A+P+G+A+R |
| EPDS | Postnatal depression | `scoring/epds.py` | ≥13 = Likely PND | 10 questions |
| NIHSS | Stroke severity | `scoring/nihss.py` | ≥16 = Severe stroke | 11 items |
| ABCD2 | TIA stroke risk | `scoring/abcd2.py` | ≥4 = High 2-day risk | 5 criteria |
| CKD-EPI | Renal function | `scoring/ckd_epi.py` | <60 = CKD Stage 3+ | Requires creatinine |
| MELD | Liver disease severity | `scoring/meld.py` | >20 = High mortality risk | Bilirubin+INR+Creatinine |
| CHILD-PUGH | Cirrhosis severity | `scoring/child_pugh.py` | Class C = Severe | 5 clinical variables |
| ROCKALL | GI bleed severity | `scoring/rockall.py` | ≥8 = High re-bleed risk | Pre-endoscopy score |
| CAPRINI VTE | Surgical VTE risk | `scoring/caprini.py` | ≥5 = Very high risk | Multiple point criteria |
| ECOG | Cancer performance | `scoring/ecog.py` | 3–4 = Limited function | 5-level scale |

---

## SECTION 24: APPENDIX — DEVELOPER QUICK-START CHECKLIST

> ★ **KEY FLAGS FOR THIS SECTION**
> - Follow this checklist sequentially — items are ordered by dependency
> - Do not skip the virtual environment setup — system Python will cause package conflicts
> - The setup wizard (step 7) must succeed before any LLM-dependent functionality works
> - The test patient run (step 13) is the acceptance test for the full development pipeline

```
ENVIRONMENT SETUP
□ 1. Install Python 3.11.x (not 3.12 — PySide6 packaging quirks)
□ 2. Clone repository: git clone https://github.com/{org}/mediassist-pro.git
□ 3. Create virtual environment: python -m venv .venv
□ 4. Activate venv: .venv\Scripts\activate  (Windows)
□ 5. Install dependencies: pip install -r requirements.txt
□ 6. Install dev dependencies: pip install -r requirements-dev.txt

FIRST-RUN CONFIGURATION
□ 7. Copy config template: copy config\facility_config.example.json config\facility_config.json
□ 8. Edit facility_config.json: set facility_name, facility_code, locale
□ 9. Run setup wizard: python scripts/setup_wizard.py  (enter 7 NIM API keys)
□ 10. Initialize database: alembic upgrade head
□ 11. Seed knowledge base: python scripts/seed_knowledge_base.py

VERIFICATION
□ 12. Run test suite: pytest tests/ -v --cov=. --cov-report=html
□ 13. Launch application: python main.py
□ 14. Register test patient with case number TEST-0001
□ 15. Run full 4-round session for "headache — specific complaint"
□ 16. Verify emergency red flag activates for "chest pain + dyspnea" selection
□ 17. Generate physician brief PDF — verify 3+ differentials with ICD codes and RAG citations
□ 18. Log in as DOCTOR role — access raw data explorer and verify all sub-panels render
□ 19. Upload WHO ETAT PDF via Document Manager — verify ingestion completes and chunk count increases
□ 20. Import synthetic_patients.csv from tests/fixtures/ — verify patient records created

BUILD
□ 21. Run installer build: python scripts/build_installer.py
□ 22. Test installer on clean Windows 11 VM (no Python installed)
□ 23. Verify installer installs, setup wizard runs, and full session completes

PRODUCTION DEPLOYMENT
□ 24. Set facility-specific config values in facility_config.json
□ 25. Change ADMIN password from default
□ 26. Enable SQLCipher encryption (verify db_encryption: true in settings)
□ 27. Configure backup schedule (daily backup to USB recommended for field deployments)
□ 28. Upload facility-specific protocols and local guidelines via Document Manager
□ 29. Create all NURSE and DOCTOR user accounts
□ 30. Run acceptance test with a sample patient session and physician sign-off
```

---

> **FINAL NOTE TO AGENTIC IDE:**
>
> This document is the single source of truth for MediAssist Pro v2.0. Build each section in the order of the phase plan (Section 15). Every module has a defined location, interface, input type, and output type. All Pydantic schemas are the binding contract between modules — do not alter them without updating all consumers. All LLM prompts live exclusively in `questionnaire/prompt_templates.py` and `report/prompt_templates.py` — never inline.
>
> Priorities in order: (1) Accuracy and clinical safety above all — a wrong output affects a real patient; (2) Stability and offline fallback — a crashed application in a humanitarian setting is a medical failure; (3) Nursing usability — if the nurse cannot understand the screen, the system fails its mission; (4) UI polish and aesthetics — last priority.
>
> The physician's raw data access layer (Section 10) is non-negotiable — physicians must be able to inspect every inference step the AI made. Transparency is a clinical safety feature, not an optional enhancement.
>
> Temperature: always 0.1. Pydantic validation: always on. Human sign-off: always required. Drug doses: never suggested. These four constraints must be enforced at the code level, not at the instruction level.

---

*MediAssist Pro Development Blueprint v2.0 — Final Edition*
*All 21 Specialties | All 7 Visit Types | All 4 Questionnaire Rounds | Physician Raw Data Layer*
*Total Sections: 24 | Resources: 355 | Estimated Build Time: 105–115 days solo / 35–45 days 3-person team*
*Designed for Humanitarian Healthcare — Force Multiplier for Health Equity*
