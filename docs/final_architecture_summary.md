# XR7 Engine 2 — Final Architecture Summary

> Generated: 2026-04-09 | Version: 2.0.0 | Status: Production-Ready

---

## 1. System Overview

XR7 Engine 2 is a multi-vertical artist earnings accuracy platform. It detects, recovers, and prevents earning discrepancies across music royalties, TV/Film residuals, touring settlements, merchandise royalties, sync licensing, brand partnerships, and platform payments.

**Core value proposition**: Given a set of royalty statements from any distributor, PRO, or DSP, XR7 automatically ingests, normalises, variance-scans, generates evidence packets, and drafts claims through a state-machine-managed lifecycle. Once a remittance is recorded, fee calculation and Trolley payout are also automated.

> **Honest scope note (beta period, updated 2026-04-30):** the *filing* step is partially automated — outbound email infrastructure (Postmark) and inbound reply parse are live and verified on QA (#219, #220). What's still human-mediated is **per-payer dispute content** (BMI-specific email body, ASCAP attachments, MLC submission process) and reply-to-claim correlation. Tracked in [#179](https://github.com/k6-labs-hq/ArtistOS/issues/179) under parent epic [#176](https://github.com/k6-labs-hq/ArtistOS/issues/176). Operator runbook: [docs/runbooks/manual-recovery.md](runbooks/manual-recovery.md).

---

## 2. High-Level Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Web Framework | FastAPI 0.100+ |
| ORM | SQLAlchemy 2.0 (Mapped / `DeclarativeBase`) |
| Schema Validation | Pydantic v2 (`model_config = ConfigDict(...)`) |
| Task Queue | Celery 5.4 + Redis 5 |
| Primary DB | PostgreSQL 16 (Alembic migrations) |
| Auth | PyJWT (RS256); multi-tenant RBAC via `XR7.api.authz` |
| ML | scikit-learn + numpy (isolation forest, forecaster, scorer) |
| AI Agents | LangGraph (stateful multi-agent graphs) |
| Graph Analysis | NetworkX (catalog relationship graphs) |
| Cloud | AWS (EKS + RDS + ElastiCache + S3 + KMS) |
| IaC | Terraform + Kustomize (overlay-based k8s) |
| CI/CD | GitHub Actions (12 workflows) |
| Observability | OpenTelemetry → Prometheus → Grafana |

---

## 3. Domain Map

XR7 is organised into 27 first-level packages under `XR7/`. Each has a clear responsibility boundary:

### 3.1 Core Domains

| Domain | Package | Responsibility |
|--------|---------|----------------|
| **API Gateway** | `XR7/api/` | FastAPI app, 75 routers, middleware, auth deps |
| **Core Logic** | `XR7/core/` | Pure business rules: claims state machine, evidence crypto, confidence scoring, variance row modelling |
| **Models** | `XR7/models/` | 69 SQLAlchemy 2.0 ORM models (canonical data definitions) |
| **Services** | `XR7/services/` | 44 service classes bridging API ↔ domain logic and ORM |
| **Ingestion** | `XR7/ingestion/` | CSV/TSV/XLSX statement parsing for 15+ named formats; universal schema normalisation |
| **Recovery** | `XR7/recovery/` | Recovery automation, immutable ledger, SOL tracking, claim packaging, bulk-export |
| **Anomaly Detection** | `XR7/anomaly/` | 5-category rule engine, variance detection, genre-specific rules |
| **Agents** | `XR7/agents/` | LangGraph multi-agent orchestration (onboarding, recovery, TV/Film, VIP, two-agent) |
| **ML** | `XR7/ml/` | Isolation Forest anomaly detector, earnings forecaster, catalog scorer, rate benchmarker, auto-inference |
| **Fingerprinting** | `XR7/fingerprinting/` | Audio fingerprint adapters + multi-signal matching engine |
| **Graph** | `XR7/graph/` | Catalog graph builder, rights graph, node definitions |
| **Intelligence** | `XR7/intelligence/` | Recovery intelligence, opportunity ranking, proactive insight engine |
| **LLM** | `XR7/llm/` | LLM wrapper, prompt templates, claim narrative generation |

### 3.2 Supporting Domains

| Domain | Package | Responsibility |
|--------|---------|----------------|
| **Auth** | `XR7/auth/` | JWT issuance, validation, token rotation |
| **Billing** | `XR7/billing/` | 12% contingency fee calculation, invoice generation, Trolley MoR bridge |
| **Blockchain** | `XR7/blockchain/` | Hash-based immutability layer for evidence packets |
| **Dashboard** | `XR7/dashboard/` | Aggregation queries powering the artist recovery dashboard |
| **Earnings** | `XR7/earnings/` | Live earnings calculation, historical reconstruction |
| **Legal** | `XR7/legal/` | SOL (statute of limitations) matrix, jurisdiction reference |
| **Notifications** | `XR7/notifications/` | Email/webhook trigger service |
| **Prevention** | `XR7/prevention/` | Proactive leakage prevention rules |
| **Registration** | `XR7/registration/` | Work registration workflows (PRO, ISRC, ISWC) |
| **Tasks** | `XR7/tasks/` | Celery task definitions (10 files); wired to queue topics |
| **Transparency** | `XR7/transparency/` | Trust-layer explainability, audit trail rendering |
| **Trolley** | `XR7/trolley/` | Trolley.io payout platform adapter |
| **UGC** | `XR7/ugc/` | Global social UGC claim scanning and auto-claim workflows |
| **Network** | `XR7/network/` | Partner / DSP network connector abstractions |
| **Modules** | `XR7/modules/` | 8 plug-in module files (feature-flagged expansions) |

### 3.3 Shared & Common Packages

| Package | Description |
|---------|-------------|
| `xr7_common/` | `settings.py` (Pydantic settings), `logging.py` (structured JSON logger), `schemas/universal.py` |
| `shared/utils/` | Pure-Python utility functions: `numbers.py`, `text.py`, `currency.py`, `dates.py` — no XR7 imports |

---

## 4. Folder Structure (Abbreviated)

```
/workspaces/ArtistOS/
├── XR7/                        # Main source (428 Python files)
│   ├── api/
│   │   ├── app.py              # FastAPI application factory
│   │   ├── authz.py            # RBAC enforcement
│   │   ├── deps.py             # FastAPI dependency providers (db, auth)
│   │   └── routers/            # 75 router files (436 API paths)
│   ├── core/                   # Pure business logic (no ORM, no services)
│   │   ├── claims/state_machine.py
│   │   ├── integrity/evidence_crypto.py
│   │   ├── scoring/confidence_band.py
│   │   └── workflow/variance_rows.py
│   ├── models/                 # 69 SQLAlchemy 2.0 ORM models
│   ├── services/               # 44 service classes
│   ├── agents/                 # LangGraph multi-agent graphs
│   ├── ingestion/              # Statement parsers + universal schema
│   ├── recovery/               # Recovery automation + ledger
│   ├── anomaly/                # Rule engine + variance detection
│   ├── ml/                     # scikit-learn ML modules
│   ├── fingerprinting/         # Audio ident + matching
│   └── [17 other domain packages]
├── xr7_common/                 # Shared settings + logging + universal schema
├── shared/utils/               # Pure utility functions (no domain imports)
├── tests/                      # 106 test files
├── alembic/versions/           # 30 migration scripts
├── scripts/                    # Domain boundary + naming convention checkers
├── openapi/                    # openapi.json (436 paths, 288 schemas)
├── docs/                       # 72 documentation files
├── infrastructure/             # Terraform + Kustomize
├── frontend/                   # React/TypeScript SPA
├── sdk/                        # Python + TypeScript SDKs
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── pyproject.toml
```

---

## 5. Key Modules

### 5.1 API Entry Point — `XR7/api/app.py`
FastAPI application factory; mounts all 75 routers, registers middleware (CORS, auth, OpenTelemetry), and exposes `/health`, `/metrics`, and `/openapi.json`.

### 5.2 Workflow Orchestrator — `XR7/services/workflow_orchestrator.py`
Top-level end-to-end pipeline: catalog graph build → ML inference → variance scan → universal event persistence → recovery automation → immutable ledger append.

### 5.3 LangGraph Agents — `XR7/agents/orchestrator.py`
Stateful, resumable agent graph supporting onboarding, recovery, TV/Film, VIP concierge, and two-agent delegation patterns. State schema defined in `XR7/agents/state.py`.

### 5.4 Ingestion Pipeline — `XR7/ingestion/`
`universal_schema.py` defines the canonical `UniversalRoyaltyRow`. Parser registry handles 15+ named formats (DistroKid, TuneCore, CD Baby, Spotify, SoundCloud, ASCAP, BMI, SESAC, MLC, etc.) plus a generic CSV fallback.

### 5.5 Recovery Automation — `XR7/recovery/recovery_automation_engine.py`
Receives variance findings → generates claim drafts → routes through claim state machine → attaches evidence packets → triggers distribution to PRO/DSP targets.

### 5.6 Claims State Machine — `XR7/core/claims/state_machine.py`
Pure finite-state machine: `IDENTIFIED → EVIDENCE_GATHERED → SUBMITTED → ACKNOWLEDGED → IN_DISPUTE → RESOLVED → PAID`. No DB or API dependencies.

### 5.7 Immutable Ledger — `XR7/recovery/immutable_ledger.py`
SHA-256 hash-chained audit log of all recovery workflow events. Every workflow run appends a ledger entry; entries cannot be modified or deleted.

### 5.8 Anomaly Engine — `XR7/anomaly/variance_detection_engine.py`
Runs 5 anomaly categories (rate deviation, missing periods, territory gaps, split discrepancies, publisher conflicts) on normalised event rows.

### 5.9 Trust Layer — `XR7/transparency/`
Renders explainability summaries for every ML inference, anomaly finding, and claim decision — surfaced via `POST /tvfilm/trust/explain` and inline in dashboard responses.

---

## 6. Shared Models & Utilities

### Canonical Data Contracts

| Model | File | Description |
|-------|------|-------------|
| `Artist` | `XR7/models/artist.py` | Core artist entity |
| `Work` | `XR7/models/work.py` | Musical / TV-Film work (uses `work_title`, `work_count`) |
| `Statement` | `XR7/models/statement.py` | Uploaded royalty statement |
| `UniversalRoyaltyEvent` | `XR7/models/universal_royalty_event.py` | Normalised royalty event (canonical post-ingestion row) |
| `Claim` | `XR7/models/claim.py` | Recovery claim entity |
| `Anomaly` | `XR7/models/anomaly.py` | Detected anomaly |
| `ImmutableLedgerEntry` | `XR7/models/immutable_ledger_entry.py` | Audit log entry |
| `CatalogGraphSnapshot` | `XR7/models/catalog_graph.py` | Serialised catalog graph snapshot |

### Naming Conventions (Enforced)

| Term | Correct | Forbidden |
|------|---------|---------|
| Work name field | `work_title` | ~~`track_title`~~ |
| Work count field | `work_count` | ~~`track_count`~~ |
| Entity type value | `'recording'` | ~~`'track'`~~ |
| JSON entity key | `"entity": "recording"` | ~~`"entity": "track"`~~ |

These are enforced by `scripts/check_naming_conventions.py`, which is run in CI.

---

## 7. API Boundaries

### External Surface
- **Base URL**: `/api/v1/` (configurable; default via `xr7_common/settings.py`)
- **OpenAPI spec**: `openapi/openapi.json` — 436 paths, 288 schemas
- **Auth**: Bearer JWT (RS256) required on all non-public endpoints
- **Multi-tenancy**: Tenant namespace isolated via `tenant_id` claim in JWT

### API → Service Pattern (Target State)
```
Router (XR7/api/routers/*.py)
  └── calls XR7/services/*.py
        └── calls XR7/core/*.py (pure logic) or
            XR7/models/*.py (ORM access)
```

> **Known architectural debt**: ~75 router files currently include inline `db.query()` calls in addition to — or instead of — delegating to service classes. This is the primary refactor target for v2.1. See `scripts/check_domain_boundaries.py` for the machine-readable rules and `docs/HANDOFF.md` for the migration roadmap.

### Celery Task Boundary
Tasks in `XR7/tasks/` are the only code that may call long-running operations asynchronously. Background tasks should never be triggered from within service or core layers directly.

### LangGraph Agent Boundary
Agents in `XR7/agents/` represent autonomous, resumable workflows. They should use service-layer methods for DB access whenever available. Direct `db.query()` in agents is acceptable for read-only state queries during graph traversal.

---

## 8. Orchestration & Event Flow

```
[Ingest] Statement upload
    ↓
[Normalise] ingestion/parser → UniversalRoyaltyEvent
    ↓
[Analyse] anomaly/variance_detection_engine
    ↓
[Score] core/scoring/confidence_band (ML confidence tier: HIGH / MEDIUM / LOW / UNCERTAIN)
    ↓
[Enrich] graph/catalog_graph_builder + ml/auto_inference_engine
    ↓
[Recover] recovery/recovery_automation_engine → claim state machine
    ↓
[Evidence] core/integrity/evidence_crypto → evidence packet (JSON + PDF + ZIP)
    ↓
[Distribute] services/claim_submission_service → PRO / DSP endpoints
    ↓
[Audit] recovery/immutable_ledger → hash-chained ledger entry
    ↓
[Dashboard] dashboard/ → artist-facing recovery metrics
```

---

## 9. Test Coverage

| Area | Test Files | Notes |
|------|-----------|-------|
| `XR7/core/` | 4 dedicated files | Full coverage of state machine, evidence crypto, scoring, variance |
| `XR7/api/routers/` | 15+ integration test files | Covers major CRUD paths; TVFilm and VIP routers included |
| `XR7/fingerprinting/` | `tests/fingerprinting/` (15 files) | Unit + integration tests for all adapters |
| `XR7/agents/` | 3 files | Onboarding + orchestrator workflow tests |
| `XR7/ml/` | 2 files | `test_ml.py`, `test_ml_feedback_loop.py` |
| `shared/utils/` | 4 files | One test per util module |
| Total | **106 test files** | 1,348+ test functions; 49 pre-existing failures tolerated |

---

## 10. Configuration Reference

All configuration is via environment variables read by `xr7_common/settings.py`:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `REDIS_URL` | ✅ | Redis connection string (Celery broker + result backend) |
| `SECRET_KEY` | ✅ | JWT signing key (RS256 private key PEM) |
| `TROLLEY_API_KEY` | 🔑 | Trolley.io MoR payouts |
| `ASCAP_API_KEY` | 🔑 | ASCAP PRO connector |
| `BMI_API_KEY` | 🔑 | BMI PRO connector |
| `SESAC_API_KEY` | 🔑 | SESAC PRO connector |
| `YOUTUBE_CLIENT_ID` | 🔑 | YouTube platform connector |
| `TIKTOK_CLIENT_ID` | 🔑 | TikTok platform connector |
| `META_CLIENT_ID` | 🔑 | Meta platform connector |
| `AWS_REGION` | ✅ (prod) | AWS region for S3/KMS |
| `S3_BUCKET` | ✅ (prod) | Evidence packet storage bucket |
| `OPENAI_API_KEY` | Optional | LLM features (claim narrative gen, copilot) |

---

## 11. CI/CD Pipelines (12 GitHub Actions Workflows)

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci-quality-gate.yml` | PR / push | pytest, ruff lint, naming convention check, domain boundary check |
| `production-deploy.yml` | Tag push `v*` | EKS deploy, Alembic migrate, zero-downtime rollout |
| `nightly-analysis.yml` | Cron 02:00 UTC | Full anomaly scan + model retraining |
| + 9 additional workflows | Various | Security scan, dependency audit, DR drill, SDK publish, etc. |

---

## 12. File Metrics (as of 2026-04-09)

| Metric | Count |
|--------|-------|
| Python source files (`XR7/`) | 428 |
| SQLAlchemy models | 69 |
| FastAPI routers | 75 |
| API paths | 436 |
| OpenAPI schemas | 288 |
| Service classes | 44 |
| Alembic migrations | 30 |
| Test files | 106 |
| Documentation files | 72 |
| GitHub Actions workflows | 12 |
| LOC (estimated) | 100,000+ |
