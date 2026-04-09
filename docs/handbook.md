# XR7 Developer Handbook

**Version:** 2.0  
**Project:** XR7 Engine — Artist Earnings Accuracy Platform  
**Stack:** Python 3.12 · FastAPI · SQLAlchemy 2.0 · Pydantic v2 · Celery · PostgreSQL · Redis

> **This handbook** is the engineering reference for contributors building, reviewing, or operating XR7. It is deeper and more comprehensive than [developer_onboarding.md](developer_onboarding.md) (which covers setup steps). Start with onboarding, then return here.

---

## Table of Contents

- [A. Architecture Overview](#a-architecture-overview)
- [B. Coding Standards](#b-coding-standards)
- [C. Development Workflow](#c-development-workflow)
- [D. Contribution Guide](#d-contribution-guide)
- [E. n8n Integration Guide](#e-n8n-integration-guide)
- [F. Glossary](#f-glossary)

---

## A. Architecture Overview

### A.1 What XR7 Does

XR7 is an earnings accuracy and rights recovery platform. It:

1. **Ingests** streaming statements from DSPs (Spotify, Apple Music, SoundCloud, etc.)
2. **Reconciles** reported royalties against what artists are mathematically owed
3. **Detects anomalies** using ML models trained on historical underpayment patterns
4. **Generates evidence** packages that artists or their attorneys submit to DSPs
5. **Tracks claims** through a formal state machine until resolved or escalated
6. **Advances capital** to artists via a recoverable advance against expected recoveries

### A.2 Package Map

```
XR7/                        ← core application package
  api/                      ← FastAPI routers and request/response handling
    routers/                ← 72 router files, grouped by domain
    dependencies.py         ← Dependency injection (DB, auth, current user)
    app.py                  ← FastAPI app wiring (72 routers registered)
  core/                     ← Pure logic (no I/O, no ORM, no HTTP)
    claims_state_machine.py ← Allowed state transitions
    integrity/              ← HMAC evidence signing
    scoring/                ← Earnings discrepancy scoring
    workflow/               ← Variance row computation
  services/                 ← Business logic + ORM (the service layer)
  ml/                       ← ML models (anomaly detection, forecasting)
    anomaly_detector.py     ← Isolation Forest underpayment detector
  fingerprinting/           ← ISRC/ISWC identity matching and deduplication
  recovery/                 ← Capital advance and recovery tracking
  ingestion/                ← DSP statement parser orchestration
  blockchain/               ← Provenance ledger (immutable audit trail)
  agents/                   ← LangGraph agentic workflows
  llm/                      ← LLM integration (OpenAI, Anthropic)
  schemas/                  ← Pydantic v2 request/response models
  models/                   ← SQLAlchemy 2.0 ORM models
  db.py                     ← Async session factory

shared/
  utils/                    ← Pure utility functions (zero XR7 imports)
    math_ops.py             ← Safe float arithmetic
    date_ops.py             ← UTC normalization
    isrc_ops.py             ← ISRC validation/parsing
    currency.py             ← Multi-currency conversion
    text_normalization.py   ← Work title normalization

xr7_common/                 ← Shared types and constants used by both
                              XR7 and external integrations (SDK, scripts)
```

### A.3 Layer Boundaries (CRITICAL)

This is the most important architectural rule:

```
┌─────────────────────────────────────────────────┐
│  XR7/api/        (HTTP layer)                   │
│  ↓ may import from                              │
│  XR7/services/   (business logic + ORM)         │
│  ↓ may import from                              │
│  XR7/core/       (pure logic — NO I/O allowed)  │
│  ↓ may import from                              │
│  shared/utils/   (zero-dependency utilities)    │
└─────────────────────────────────────────────────┘
```

**What is FORBIDDEN:**
- `XR7/core/` importing from `XR7/services/`, `XR7/api/`, or `sqlalchemy`
- `shared/utils/` importing from `XR7.*` (any package)
- `XR7/api/routers/` directly calling `db.query()` or `db.execute()` (ORM in services only)
- `XR7/ml/` importing from `XR7/recovery/` or `XR7/blockchain/`

These rules are machine-enforced by `scripts/check_domain_boundaries.py`, which runs in CI on every PR.

### A.4 DSP Ingestion Flow

```
DSP raw file (CSV/ZIP)
    ↓
IngestionConnector (XR7/ingestion/)
    ↓ normalize field names
    ↓ emit StatementRow objects
Services layer (XR7/services/)
    ↓ persist to DB (PostgreSQL)
    ↓ trigger reconciliation
ML layer (XR7/ml/anomaly_detector.py)
    ↓ flag anomalies
Evidence generation (XR7/core/integrity/)
    ↓ sign evidence with HMAC
Claims (XR7/core/claims_state_machine.py)
    ↓ state: EVIDENCE_READY → SUBMITTED
```

### A.5 Multi-Tenancy

Every database query is scoped by `tenant_id`. This is enforced at the service layer, not the router layer. The `tenant_id` is extracted from the JWT claims on every authenticated request and passed explicitly to service functions. It is NEVER read from the request body (injection prevention).

---

## B. Coding Standards

### B.1 Naming Conventions

XR7 uses music industry standard terminology, not informal slang:

| ❌ Forbidden | ✅ Use instead | Source standard |
|-------------|---------------|----------------|
| `track_title` | `work_title` | PPRD / DDEX |
| `track_count` | `work_count` | PPRD |
| `song_id` | `isrc` (for recordings) | ISO 3901 |
| `song_title` | `work_title` | PPRD |
| `"entity": "track"` | `"entity": "recording"` | DDEX ERN |
| `"entity": "song"` | `"entity": "composition"` | DDEX |
| `royalty_type: "sync"` | `"master_sync"` or `"pub_sync"` | DDEX |

**Parser/adapter exemption:** Files under `parsers/`, `adapters/`, and `ingestion/` may use DSP-native field names in their mapping tables (since they read raw DSP files that use these names). They must normalize to XR7 terms before passing data upward.

These rules are enforced by `scripts/check_naming_conventions.py` in CI.

### B.2 Type Annotations

All new code must be fully type-annotated.

```python
# CORRECT
def compute_delta(expected: float, actual: float) -> float:
    return expected - actual

# WRONG  
def compute_delta(expected, actual):
    return expected - actual
```

- `XR7/core/` and `shared/utils/` are mypy-checked in `--strict` mode.
- `XR7/services/` and `XR7/api/` are checked in standard mypy mode.
- Run `mypy XR7/core/ shared/utils/ --strict` before submitting a PR touching these modules.

### B.3 Pydantic Models

Use Pydantic v2's `model_config` (not the v1 `class Config`):

```python
from pydantic import BaseModel, Field, ConfigDict

class ClaimResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    claim_id: str
    work_title: str                          # not track_title
    isrc: str = Field(..., pattern=r"^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$")
    state: str
    amount_usd: float = Field(..., ge=0)
```

### B.4 SQLAlchemy Models

Use SQLAlchemy 2.0's `Mapped[T]` with `mapped_column`:

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Numeric
from XR7.db import Base

class Claim(Base):
    __tablename__ = "claims"

    claim_id:   Mapped[str]   = mapped_column(String, primary_key=True)
    work_title: Mapped[str]   = mapped_column(String, nullable=False)  # not track_title
    isrc:       Mapped[str]   = mapped_column(String(12), nullable=False)
    amount_usd: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
```

**Never** use `db.query()` — use `select()` + `db.execute()`:

```python
# CORRECT (SQLAlchemy 2.0 style)
result = await db.execute(select(Claim).where(Claim.claim_id == claim_id))
claim = result.scalar_one_or_none()

# WRONG (SQLAlchemy 1.x style — banned)
claim = db.query(Claim).filter(Claim.claim_id == claim_id).first()
```

### B.5 Async/Await

All I/O operations must be async. No blocking calls in async functions:

```python
# CORRECT
async def fetch_artist(db: AsyncSession, artist_id: str) -> Artist | None:
    result = await db.execute(select(Artist).where(Artist.id == artist_id))
    return result.scalar_one_or_none()

# WRONG — blocks the event loop
def fetch_artist(db: Session, artist_id: str) -> Artist | None:
    return db.query(Artist).filter(Artist.id == artist_id).first()
```

Use `asyncio.to_thread()` for any unavoidable blocking I/O (file reading, legacy sync libs).

### B.6 Error Handling

Return meaningful HTTP errors — never swallow exceptions silently:

```python
from fastapi import HTTPException, status

# CORRECT
if not claim:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "not_found", "message": f"Claim {claim_id} not found"},
    )

# WRONG — generic 500 gives consumers no actionable info
if not claim:
    raise Exception("not found")
```

Do NOT add `try/except` around every function call. Handle exceptions at system boundaries (router entry points, Celery task entry points). Let them propagate cleanly through the service and core layers.

### B.7 Logging

Use `structlog` (or the stdlib `logging` module with structured extras):

```python
import logging

logger = logging.getLogger(__name__)

logger.info(
    "claim.advanced",
    extra={
        "claim_id": claim.claim_id,
        "from_state": old_state,
        "to_state": new_state,
        "tenant_id": tenant_id,
    },
)
```

**Never log PII** (names, emails, bank details). Log IDs instead. This is enforced in security reviews.

### B.8 Test Requirements

Every PR must include tests. Minimum coverage per layer:

| Layer | Minimum coverage |
|-------|-----------------|
| `XR7/core/` | 95% |
| `shared/utils/` | 95% |
| `XR7/services/` | 75% |
| `XR7/api/routers/` | 70% |
| Overall | 60% |

For each new endpoint, tests must cover:
1. Happy path
2. Unauthorized (401)
3. Invalid input (422)
4. Relevant error cases (404, 409)

---

## C. Development Workflow

### C.1 Local Setup

```bash
# Clone + enter container
git clone https://github.com/your-org/XR7.git
cd XR7

# Install all dev dependencies
pip install -e ".[dev]"

# Start backing services
docker compose up -d postgres redis

# Run migrations
alembic upgrade head

# Verify everything works
pytest tests/ -q
```

### C.2 Running the API Locally

```bash
uvicorn XR7.api.app:app --reload --port 8000
```

Swagger UI is at `http://localhost:8000/docs`.  
ReDoc is at `http://localhost:8000/redoc`.

### C.3 Running Tests

```bash
# Full test suite
pytest tests/ -q

# Specific test file
pytest tests/test_core_claims_state_machine.py -v

# Tests matching a keyword
pytest -k "claim" -v

# With coverage
pytest tests/ --cov=XR7 --cov=shared --cov-report=term-missing

# Parallel (faster)
pytest tests/ -n auto
```

### C.4 Running CI Checks Locally

Before pushing, run the same checks that CI will run:

```bash
# Lint
ruff check XR7/ shared/ tests/ --select E,W,F,I

# Format check
black --check XR7/ shared/ tests/

# Type check (core modules)
mypy XR7/core/ shared/utils/ --strict

# Domain boundary check
python scripts/check_domain_boundaries.py

# Naming convention check
python scripts/check_naming_conventions.py
```

Run all in one command:

```bash
make lint  # if Makefile target exists
```

### C.5 Database Migrations

When you add or modify SQLAlchemy models:

```bash
# Generate a new migration
alembic revision --autogenerate -m "add_my_new_column"

# Review the generated file in alembic/versions/
# Verify it looks correct — autogenerate is helpful but not infallible

# Apply locally
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

**Migration rules:**
- Never modify an existing migration file after it runs in staging
- Every migration must have a working `downgrade()` function
- Migrations that rename columns must use multi-step patterns (add → backfill → remove) to avoid downtime
- See [xr7_database_migration_rollout_plan.md](xr7_database_migration_rollout_plan.md) for zero-downtime patterns

### C.6 Regenerating the OpenAPI Spec

After adding or modifying endpoints, regenerate the spec:

```bash
python -c "
import json
from XR7.api.app import app
with open('openapi/openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)
print('openapi/openapi.json updated')
"
```

Commit the updated file. The `api-contract-guard.yml` CI workflow validates that the committed spec matches the running app.

---

## D. Contribution Guide

### D.1 Branch Strategy

```
main            ← production-ready; protected
staging         ← integration branch; auto-deploys to staging
feature/<name>  ← feature branches; branch from main
fix/<name>      ← bug fixes; branch from main
hotfix/<name>   ← urgent prod fixes; branch from main; merge to both main + staging
```

Branch names must be lowercase with hyphens: `feature/ml-anomaly-threshold-tuning`.

### D.2 Commit Messages

Follow Conventional Commits:

```
feat(claims): add attorney evidence file export endpoint
fix(ml): correct isolation forest window calculation
refactor(core): extract variance row builder to XR7.core.workflow
test(reconciliation): add coverage for duplicate ISRC edge case
docs(api): document /claims/{id}/timeline response shape
```

Scopes match module names: `claims`, `ml`, `core`, `api`, `ingestion`, `recovery`, `fingerprinting`, `n8n`, `ci`.

### D.3 Pull Request Requirements

Every PR needs:
- [ ] All CI checks green (quality gate workflow)
- [ ] At least one test for every new code path
- [ ] `openapi/openapi.json` updated (if endpoints changed)
- [ ] Relevant `docs/api/` file updated (if endpoints changed)
- [ ] No `track_title`, `song_id`, `"entity": "track"` naming violations
- [ ] No direct ORM in routers
- [ ] No imports that violate domain boundaries
- [ ] CHANGELOG.md entry (if user-facing change)

### D.4 Code Review Priorities

Reviewers should focus on:
1. Domain boundary violations (architecture correctness)
2. Missing auth dependencies on new endpoints
3. PII in log statements
4. Tenant isolation (every query scoped by `tenant_id`)
5. Missing test coverage for error paths
6. Naming convention violations

See [code_review_checklist.md](code_review_checklist.md) for the full senior engineer checklist.

### D.5 Release Process

1. Merge all sprint PRs to `main`
2. Run full test suite + smoke tests
3. Tag the release: `git tag v2.X.Y`
4. Push the tag: `git push origin v2.X.Y`
5. The `production-deploy.yml` workflow triggers automatically
6. Approve the `deploy-prod` environment gate in GitHub Actions
7. Monitor health dashboard for 15 minutes post-deploy
8. Update CHANGELOG.md with release notes

---

## E. n8n Integration Guide

### E.1 What n8n Handles

n8n orchestrates the operational workflows that are too complex for a single HTTP request. The XR7 API is n8n's primary execution target.

| n8n Workflow | Responsibility |
|-------------|---------------|
| DSP Ingestion Pipeline | Schedule ingestion; retry on failure; notify on anomalies |
| PRO Reconciliation Pipeline | Match registrations to statements; flag gaps |
| MLC Metadata Alignment Pipeline | Align metadata with MLC registry |
| Recovery Claim Export Pipeline | Bundle evidence; submit to DSPs |

Full blueprints: [docs/n8n/](n8n/)

### E.2 How n8n Calls XR7

n8n calls the XR7 REST API. Every n8n workflow must:

1. **Authenticate first**: `POST /auth/login/artist` or use a long-lived n8n service token
2. **Pass the Bearer token** in subsequent API calls
3. **Handle 503 errors** with exponential backoff retry (n8n's built-in retry node)
4. **Log the `request_id`** from every response for Celery trace correlation

### E.3 Service Account Tokens

n8n uses a dedicated service account (role: `admin`, scoped permissions). This account:
- Is managed in the n8n credentials store, not in `.env` files
- Has minimal permissions (principle of least privilege)
- Is rotated every 90 days as part of the security rotation schedule
- Must NOT be shared with human users

### E.4 Webhook Endpoints

XR7 exposes `POST /webhooks` for n8n-triggered events. Webhook payloads are signed with HMAC-SHA256. The signature is in the `X-XR7-Signature` header. n8n workflows must validate this before processing.

### E.5 Async Job Status Polling

Long-running jobs (evidence generation, ML forecasting, ingestion) return a `job_id`. n8n polls `GET /jobs/{job_id}/status` with a Wait node until the job status is `completed` or `failed`.

Recommended polling interval: 5 seconds, with a maximum 5-minute timeout.

---

## F. Glossary

| Term | Full form | Definition |
|------|-----------|------------|
| **ISRC** | International Standard Recording Code | 12-character identifier for a specific recording (not the composition). Format: `USRC12345678`. |
| **ISWC** | International Standard Musical Work Code | Identifies the underlying musical composition (song). Format: `T-034524680-1`. |
| **DDEX** | Digital Data Exchange | The XML/JSON schema standard used by DSPs for royalty reporting. XR7 ingests DDEX ERN and CRB formats. |
| **PPRD** | Publishing and Performance Rights Data | The XR7 internal term for composer/publisher rights payloads. |
| **DSP** | Digital Service Provider | Music streaming platforms: Spotify, Apple Music, SoundCloud, Amazon Music, etc. |
| **PRO** | Performing Rights Organization | Organizations that collect and distribute performance royalties: ASCAP, BMI, SOCAN, PRS, etc. |
| **MLC** | Mechanical Licensing Collective | US entity that administers mechanical royalties for digital audio transmissions. |
| **Work** | Musical Work | The composition (music + lyrics); identified by ISWC. A work can have many recordings. |
| **Recording** | Sound Recording | A specific recorded performance of a work; identified by ISRC. |
| **Party** | Rights Party | A person or organization holding rights in a work or recording (artist, songwriter, publisher, label). |
| **Variance Row** | — | A row in a reconciliation comparison showing expected vs. actual royalty for one ISRC/period/payer combination. |
| **Evidence Packet** | — | The HMAC-signed bundle of variance rows, earnings calculations, and audit metadata submitted to a DSP as proof of underpayment. |
| **Claim** | Recovery Claim | A formal XR7 record of an underpayment claim from an artist against a DSP, tracked through a state machine. |
| **Advance** | Analyst-Gated Recovery Advance | Capital fronted to an artist against expected recovery, gated on analyst approval. |
| **Tenant** | — | An isolated customer account in XR7's multi-tenant model. Each tenant has a `tenant_id` that scopes all DB queries. |
| **Isolation Forest** | — | The ML algorithm used by `XR7/ml/anomaly_detector.py` to detect abnormal royalty patterns. |
| **n8n** | — | Open-source workflow automation tool used to orchestrate complex multi-step XR7 operations. |
| **LangGraph** | — | Python framework for stateful LLM-agent graphs, used in `XR7/agents/`. |
| **Celery** | — | Python distributed task queue used for background jobs (ingestion, ML scoring, evidence generation). |
| **Alembic** | — | SQLAlchemy migration tool. All DB schema changes must have an Alembic migration. |
