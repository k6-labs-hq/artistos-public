# XR7 Engine — Developer Onboarding Guide

> **Audience:** Engineers joining the XR7 project, senior contributors, and external reviewers.
> This document is the single authoritative reference for how the codebase is structured, how to run it, and how to contribute without breaking architecture.

---

## Table of Contents

1. [What is XR7?](#1-what-is-xr7)
2. [Prerequisite Setup](#2-prerequisite-setup)
3. [Running the Project Locally](#3-running-the-project-locally)
4. [Running Tests](#4-running-tests)
5. [Architecture Overview](#5-architecture-overview)
6. [Domain Reference](#6-domain-reference)
7. [How Files Are Organized](#7-how-files-are-organized)
8. [Adding a New Module Without Breaking Architecture](#8-adding-a-new-module-without-breaking-architecture)
9. [Domain Boundary Rules — Do Not Violate](#9-domain-boundary-rules--do-not-violate)
10. [Glossary of Domain Terms](#10-glossary-of-domain-terms)
11. [How to Contribute Safely](#11-how-to-contribute-safely)

---

## 1. What is XR7?

XR7 is a royalty recovery and music rights intelligence engine. It ingests payment statements from DSPs, PROs, and distributors; normalizes and reconciles them against an artist's registered catalog; identifies discrepancies; and drives automated recovery of unpaid or underpaid royalties.

The system is built on **FastAPI**, **SQLAlchemy 2**, **Celery**, and **LangGraph** and deployed as a containerized service on Kubernetes.

---

## 2. Prerequisite Setup

```bash
# Python version
python --version   # must be 3.12.x

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env   # then fill in secrets

# Apply database migrations
alembic upgrade head
```

### Required environment variables

| Variable | Purpose | Default (dev) |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `sqlite:///./dev.db` |
| `REDIS_URL` | Celery broker | `redis://localhost:6379/0` |
| `XR7_EVIDENCE_HMAC_SECRET` | Evidence packet signing key | `xr7-dev-evidence-secret` |
| `XR7_EVIDENCE_SIGNING_MODE` | `hmac` or `rsa` | `hmac` |
| `OPENAI_API_KEY` | LLM gap explainer | optional |

---

## 3. Running the Project Locally

```bash
# Start the API server (hot-reload enabled)
uvicorn XR7.api.app:app --reload --port 8000

# Start a Celery worker (in a separate terminal)
celery -A XR7.tasks worker --loglevel=info

# Run with Docker Compose (API + Postgres + Redis + Celery)
docker-compose up --build

# Interactive API docs
open http://localhost:8000/docs
```

---

## 4. Running Tests

```bash
# Full test suite (1300+ tests)
pytest tests/ -q

# One domain at a time
pytest tests/test_core_*.py -v                   # pure core logic
pytest tests/test_shared_*.py -v                 # shared utilities
pytest tests/ -k "ingestion" -v                  # ingestion domain
pytest tests/ -k "recovery" -v                   # recovery domain

# Stop on first failure
pytest tests/ -x --tb=short

# Coverage report
pytest tests/ --cov=XR7 --cov-report=term-missing

# Branding contract guard
pytest -q tests/test_branding.py tests/test_branding_contract_guard.py tests/test_branding_service.py
```

### Test naming convention

| File pattern | Layer |
|---|---|
| `test_core_*.py` | Pure logic, no DB — runs in milliseconds |
| `test_shared_*.py` | Shared utility functions |
| `test_*_integration.py` | DB-dependent, uses in-memory SQLite |
| All others | Mixed; check the fixture list in the file header |

---

## 5. Architecture Overview

XR7 follows a strict **layered, domain-oriented architecture**. Each layer has exactly one purpose. Dependencies only flow inward.

```
┌──────────────────────────────────────────────────────────────────┐
│  API layer      (XR7/api/routers/)  — HTTP in/out only           │
│  Task layer     (XR7/tasks/)        — Celery entry points only   │
├──────────────────────────────────────────────────────────────────┤
│  Service layer  (XR7/services/, XR7/<domain>/)                   │
│  — business logic, DB calls, orchestration                       │
├──────────────────────────────────────────────────────────────────┤
│  Core layer     (XR7/core/)         — pure functions, no I/O     │
│  Shared utils   (shared/utils/)     — zero-dependency utilities  │
├──────────────────────────────────────────────────────────────────┤
│  Models         (XR7/models/)       — SQLAlchemy ORM definitions │
└──────────────────────────────────────────────────────────────────┘
```

**Golden rule:** Lower layers must never import from higher layers.
`core/` and `shared/utils/` must never import from `services/`, `api/`, or `tasks/`.

### Data flow

```
DSP Statement File
      │
      ▼
[ingestion/]      — parse, normalize raw rows into Statement records
      │
      ▼
[fingerprinting/] — match statement rows to catalog Works and Artists
      │
      ▼
[normalization/]  — repair metadata gaps, crosswalk PRO data
      │
      ▼
[recovery/]       — identify anomalies, package evidence, file claims
      │
      ▼
[reporting/]      — dashboards, forecasts, valuations
```

---

## 6. Domain Reference

Each domain owns its own subdirectory under `XR7/`. No other domain should reach into it except through its public API.

### `ingestion/`
**Purpose:** Accept raw statement files from DSPs, PROs, distributors, and MLC platforms; parse them into normalized `Statement` rows.

Key files: `statement_parser.py`, `statement_signal_extractor.py`, `pipeline.py`, `fetchers.py`

**Inputs:** Raw files (CSV, Excel, JSON); API webhooks
**Outputs:** `Statement` ORM rows; identity signal dicts for `fingerprinting/`

---

### `fingerprinting/`
**Purpose:** Match statement rows to catalog entities (Artists, Works) using a weighted multi-signal algorithm.

Key files: `matching/identity_matching.py`

**Band thresholds:**

| Score | Band | Action |
|---|---|---|
| ≥ 0.90 | `AUTO_ACCEPT` | Auto-accepted |
| 0.70–0.89 | `SOFT_CONFIRM` | Analyst soft-confirm queue |
| < 0.70 | `REQUIRE_CONFIRMATION` | Explicit confirmation required |

---

### `normalization/`
**Purpose:** Repair metadata gaps in the catalog — missing ISRCs, ISWC mismatches, PRO crosswalk errors, distributor drift.

Key files: `metadata_repair_engine.py`

---

### `recovery/`
**Purpose:** The core revenue-recovery pipeline — identify anomalies, score them, package evidence, and file or escalate claims.

Key files: `gap_explainer.py`, `orchestrator.py`, `auto_filing_engine.py`, `immutable_ledger/`, `tvfilm/`

**Claims lifecycle:**
```
IDENTIFIED → PREPARED → SUBMITTED → FILED → IN_REVIEW → ACCEPTED → PAID → CLOSED
```

---

### `reporting/`
**Purpose:** Aggregated dashboards, forecasts, and historical analysis surfaces.

Key files: `org_dashboard_service.py`, `post_repair_forecast_pipeline.py`, `xr7_valuation_service.py`

---

### `shared/utils/`
**Purpose:** Zero-dependency utility functions. Must never import from `XR7/`.

| Module | Functions |
|---|---|
| `dates.py` | `ensure_utc()`, `period_key()` |
| `numbers.py` | `safe_float()` |
| `currency.py` | `convert_currency()` |
| `text.py` | `normalize_name()`, `slugify()` |

---

### `XR7/core/`
**Purpose:** Pure-logic modules — no DB, no I/O, no service imports.

| Module | Key exports |
|---|---|
| `core/claims/state_machine.py` | `next_status()`, `contract_type_for_category()` |
| `core/integrity/evidence_crypto.py` | `seal_packet()`, `verify_packet_integrity()` |
| `core/scoring/confidence_band.py` | `classify_band()` |
| `core/scoring/metadata_match.py` | `metadata_triangulation_score()`, `confidence_score()` |
| `core/workflow/variance_rows.py` | `event_to_variance_row()`, `event_to_universal_row()` |

---

## 7. How Files Are Organized

```
/
├── XR7/                    Main application package
│   ├── api/                HTTP layer (FastAPI routers, no business logic)
│   │   └── routers/        One router per domain
│   ├── core/               Pure functions — no I/O, no DB
│   ├── models/             SQLAlchemy ORM models
│   ├── tasks/              Celery task entry points
│   ├── agents/             LangGraph / AI agent definitions
│   ├── ingestion/          DSP statement ingestion
│   ├── fingerprinting/     Catalog matching algorithms
│   ├── normalization/      Metadata repair
│   ├── recovery/           Anomaly detection → claim filing
│   ├── reporting/          Dashboards and forecasts
│   ├── billing/            Advance offers and payment management
│   ├── ml/                 ML models (anomaly detection, calibration)
│   ├── llm/                LLM integrations (OpenAI, xAI)
│   ├── blockchain/         Immutable evidence anchoring
│   └── services/           Cross-cutting infrastructure services
├── shared/                 Zero-XR7-dependency utilities
│   └── utils/
├── xr7_common/             Shared logging, config helpers
├── tests/                  All tests (pytest)
├── alembic/                Database migrations
└── docs/                   Extended documentation
```

**One file, one concern.** If a file grows beyond ~400 lines, it is doing too much. Split it.

---

## 8. Adding a New Module Without Breaking Architecture

### Step 1 — Identify the domain

Use the [Domain Reference](#6-domain-reference). If it's genuinely cross-cutting infrastructure (caching, storage, signing), it goes in `services/`.

### Step 2 — Create the file in the right package

```
XR7/<domain>/my_new_service.py
```

### Step 3 — Extract pure logic to core/ first

```python
# XR7/core/<domain>/my_logic.py — NO db/service imports
def compute_something(value: float, factor: float) -> float:
    ...
```

### Step 4 — Write tests alongside the implementation

Every new file must have: a happy-path test per public function, at least one edge case, and a domain-boundary assertion if in `core/`.

### Step 5 — Register the API router (if HTTP-exposed)

Router in `XR7/api/routers/`, registered in `XR7/api/app.py`. Routers call service functions only — no logic in the router.

---

## 9. Domain Boundary Rules — Do Not Violate

### Rule 1: `core/` and `shared/utils/` are dependency-free

```python
# FORBIDDEN in XR7/core/ or shared/utils/
from sqlalchemy.orm import Session          # ❌
from XR7.services.branding import ...      # ❌
```

### Rule 2: API routers contain zero business logic

```python
# FORBIDDEN in XR7/api/routers/
db.query(Claim).filter(...).all()          # ❌  move to a service
if claim.amount > 1000: ...               # ❌  move to a service
```

### Rule 3: ML must not import recovery or blockchain directly

Return scores; let the recovery pipeline consume them.

### Rule 4: Domain modules do not import from sibling domains

```python
# In XR7/ingestion/
from XR7.recovery.orchestrator import ...   # ❌
```

### Rule 5: Branding injection is required on identity payloads

Any non-admin endpoint returning a top-level dict with `artist_id` or `org_id` must include top-level `branding` metadata via `inject_branding_metadata(db, payload)`.

---

## 10. Glossary of Domain Terms

| Term | Definition |
|---|---|
| **Work** | A musical composition — the underlying song (lyrics + melody). Identified by ISWC or `work_id`. |
| **Recording** | A specific recorded performance of a Work. Identified by ISRC. One Work may have many Recordings. |
| **Party** | Any legal entity with an ownership stake: songwriter, publisher, performing artist, label. |
| **Statement** | A payment statement received from a DSP, PRO, or distributor. |
| **Anomaly** | A detected discrepancy between expected and reported royalties. |
| **Claim** | A formal recovery action initiated against a payer for an identified Anomaly. |
| **Evidence Packet** | A cryptographically sealed bundle of proof supporting a Claim. |
| **Gap** | The monetary difference between what an artist should have earned and what was reported/paid. |
| **DSP** | Digital Service Provider — Spotify, Apple Music, Amazon Music, YouTube, etc. |
| **PRO** | Performing Rights Organisation — ASCAP, BMI, SESAC, PRS, SOCAN, etc. |
| **MLC** | The Mechanical Licensing Collective — administers mechanical royalties in the US. |
| **ISRC** | International Standard Recording Code — uniquely identifies a Recording. |
| **ISWC** | International Standard Musical Work Code — uniquely identifies a Work (composition). |
| **IPI** | Interested Parties Information number — uniquely identifies a Party at a PRO. |
| **UPC** | Universal Product Code — identifies an album/release. |
| **Crosswalk** | Mapping an artist's works across identifier systems (e.g., ISRC → ISWC). |
| **Confidence Band** | Routing classification for matches: `AUTO_ACCEPT`, `SOFT_CONFIRM`, `REQUIRE_CONFIRMATION`. |
| **Black Box** | Royalties collected by a PRO but undistributed because the rights holder is unidentified. |
| **Advance** | A pre-disbursement payment to an artist against projected recovery proceeds. |
| **Ledger** | The immutable, append-only audit trail of all recovery actions (sealed with HMAC or RSA). |
| **Variance Row** | A normalized data row fed into the variance-detection algorithm to flag payout anomalies. |
| **Universal Event** | A normalized representation of any royalty event used as the common internal format. |

---

## 11. How to Contribute Safely

### Before you start

1. Read [Domain Boundary Rules](#9-domain-boundary-rules--do-not-violate).
2. Run `pytest tests/ -q` and confirm it passes.
3. Branch: `git checkout -b feat/<domain>/<short-description>`.

### During development

- **One concern per file.** If unsure, split.
- **Write the test first** (or alongside). Every new public function needs a test.
- **No `SessionLocal()` calls inside domain logic.** Inject `Session` from the caller (task or router).
- **Use `shared/utils/`** for date, number, currency, and text helpers. Never reimplement `ensure_utc` or `safe_float`.
- **No circular imports.**

### Naming conventions

| Entity | Use | Avoid |
|---|---|---|
| Compositions | `work_id`, `work_title`, `work_count` | `song_id`, `track_title`, `track_count` |
| Recordings | `recording_id`, `entity: "recording"` | `track_id`, `entity: "track"` |
| Rights holders | `party_id`, `party_name` | `writer_id` in new code |

### Before you merge

```bash
pytest tests/ -q                                # all tests pass
pytest tests/ --collect-only -q 2>&1 | grep ERROR  # no new collection errors
python -c "import XR7.api.app"                 # no circular imports
```

---

*Last updated: 2026-04-08 | XR7 Engine architecture — Platform team*
