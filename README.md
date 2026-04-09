# XR7 Engine 2 — Artist Earnings Accuracy Platform

> **Version 2.0.0** | Python 3.12 · FastAPI · SQLAlchemy 2.0 · Pydantic v2 · Celery · PostgreSQL · Redis  
> Last updated: 2026-04-09

<!-- COMPLETION_START -->
## Project Completion: 97%

`████████████████████` **97%** — 2026-04-09

| Signal | Detail | Weight |
|--------|--------|--------|
| Market Readiness | 18 ✅  4 🔑  0 ⚠️  (91% of 22 components) | 45% |
| Test Coverage | 106 test files / 1,348+ test functions | 25% |
| Documentation | 72 docs complete | 20% |
| Infrastructure | 27/27 checks passing | 10% |

<!-- COMPLETION_END -->

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Domain Descriptions](#2-domain-descriptions)
3. [Folder Structure](#3-folder-structure)
4. [Naming Conventions](#4-naming-conventions)
5. [Dev Workflow](#5-dev-workflow)
6. [Testing](#6-testing)
7. [n8n Orchestration](#7-n8n-orchestration)
8. [API Reference](#8-api-reference)
9. [How to Extend XR7 Safely](#9-how-to-extend-xr7-safely)
10. [Production-Readiness Checklist](#10-production-readiness-checklist)
11. [Market Readiness](#11-market-readiness)
12. [Glossary](#12-glossary)

---

## 1. Architecture Overview

XR7 Engine 2 detects, recovers, and prevents earning discrepancies for artists across music royalties, TV/Film residuals, touring settlements, sync licensing, brand partnerships, and platform payments.

```
[Ingest]  Statement upload (CSV/TSV/XLSX, 15+ named formats)
    ↓
[Normalise]  ingestion/parser → UniversalRoyaltyEvent
    ↓
[Analyse]   anomaly/variance_detection_engine  (5-category rule engine)
    ↓
[Score]     core/scoring/confidence_band  (HIGH / MEDIUM / LOW / UNCERTAIN)
    ↓
[Enrich]    graph/catalog_graph_builder + ml/auto_inference_engine
    ↓
[Recover]   recovery/recovery_automation_engine → claims state machine
    ↓
[Evidence]  core/integrity/evidence_crypto → JSON + PDF + ZIP packets
    ↓
[Distribute] services/claim_submission → PRO / DSP endpoints
    ↓
[Audit]     recovery/immutable_ledger  (SHA-256 hash-chained log)
    ↓
[Dashboard] dashboard/ → artist-facing recovery metrics
```

**Key characteristics:**
- Multi-tenant: tenant namespace isolated via JWT `tenant_id` claim
- Multi-vertical: Music and TV/Film workflows share infrastructure; role-specific rules diverge at the anomaly and claim layers
- ML-augmented: confidence scoring, isolation-forest anomaly detection, earnings forecasting built into the core pipeline
- Agent-orchestrated: LangGraph stateful multi-agent graphs for onboarding, recovery, VIP concierge, and TV/Film workflows
- Immutable audit: every workflow run appends a cryptographically-linked ledger entry

---

## 2. Domain Descriptions

| Domain | Package | Responsibility |
|--------|---------|----------------|
| **API Gateway** | `XR7/api/` | FastAPI app, 75 routers (436 paths), middleware, auth deps |
| **Core Logic** | `XR7/core/` | Pure business rules: claims FSM, evidence crypto, confidence scoring, variance row modelling. No ORM. No service imports. |
| **Models** | `XR7/models/` | 69 SQLAlchemy 2.0 `Mapped` ORM models — canonical data definitions |
| **Services** | `XR7/services/` | 44 service classes — the bridge between API/agents and domain+ORM logic |
| **Ingestion** | `XR7/ingestion/` | CSV/TSV/XLSX parsing for 15+ named formats; normalises into `UniversalRoyaltyEvent` |
| **Recovery** | `XR7/recovery/` | Recovery automation, immutable ledger, SOL tracking, claim packaging, bulk-export |
| **Anomaly Detection** | `XR7/anomaly/` | 5-category rule engine (rate deviation, missing periods, territory gaps, split discrepancies, publisher conflicts), genre rules |
| **Agents** | `XR7/agents/` | LangGraph graphs: onboarding, recovery, TV/Film, VIP concierge, two-agent delegation |
| **ML** | `XR7/ml/` | Isolation Forest anomaly detector, earnings forecaster, catalog scorer, rate benchmarker, auto-inference engine |
| **Fingerprinting** | `XR7/fingerprinting/` | Audio fingerprint adapters + multi-signal matching (ISRC, title, artist, acoustid) |
| **Graph** | `XR7/graph/` | Catalog graph builder, rights graph, node definitions (NetworkX) |
| **Intelligence** | `XR7/intelligence/` | Opportunity ranking, proactive insight engine |
| **LLM** | `XR7/llm/` | Claim narrative generation, copilot Q&A, cue-sheet PDF extraction |
| **Auth** | `XR7/auth/` | JWT issuance, validation, token rotation (RS256) |
| **Billing** | `XR7/billing/` | 12% contingency fee calculation, invoice generation, Trolley MoR bridge |
| **Blockchain** | `XR7/blockchain/` | Hash-based immutability layer for evidence packets |
| **Dashboard** | `XR7/dashboard/` | Aggregation queries for the artist recovery dashboard |
| **Earnings** | `XR7/earnings/` | Live earnings calculation, historical reconstruction |
| **Legal** | `XR7/legal/` | SOL matrix, jurisdiction reference |
| **Tasks** | `XR7/tasks/` | 10 Celery task files — queue-based async processing |
| **Transparency** | `XR7/transparency/` | Trust-layer explainability, audit trail rendering |
| **Trolley** | `XR7/trolley/` | Trolley.io payout adapter |
| **UGC** | `XR7/ugc/` | Global social UGC claim scanning, auto-claim workflows |
| **Shared Utils** | `shared/utils/` | Pure-Python utilities (numbers, text, currency, dates) — no XR7 imports |
| **Common** | `xr7_common/` | Settings (Pydantic), structured logger, universal schema |

---

## 3. Folder Structure

```
ArtistOS/
├── XR7/                        # Main source — 428 Python files
│   ├── api/
│   │   ├── app.py              # FastAPI application factory
│   │   ├── authz.py            # RBAC enforcement
│   │   ├── deps.py             # Dependency providers (db session, current user)
│   │   └── routers/            # 75 router files → 436 API paths
│   ├── core/                   # Pure business logic (no ORM, no service imports)
│   │   ├── claims/state_machine.py
│   │   ├── integrity/evidence_crypto.py
│   │   ├── scoring/confidence_band.py
│   │   └── workflow/variance_rows.py
│   ├── models/                 # 69 SQLAlchemy 2.0 ORM models
│   ├── services/               # 44 service classes
│   ├── agents/                 # LangGraph multi-agent graphs
│   ├── ingestion/              # Statement parsers + universal schema
│   ├── recovery/               # Recovery automation + immutable ledger
│   ├── anomaly/                # Variance detection engine + rule catalog
│   ├── ml/                     # scikit-learn ML modules
│   ├── fingerprinting/         # Audio ident adapters + matching engine
│   ├── graph/                  # Catalog graph (NetworkX)
│   ├── intelligence/           # Opportunity ranking + insight engine
│   ├── llm/                    # LLM wrappers + prompt templates
│   ├── auth/                   # JWT issuance + validation
│   ├── billing/                # Contingency billing engine
│   ├── blockchain/             # Hash immutability layer
│   ├── dashboard/              # Dashboard aggregation
│   ├── earnings/               # Earnings calculator
│   ├── legal/                  # SOL matrix
│   ├── notifications/          # Email + webhook triggers
│   ├── prevention/             # Proactive leakage prevention
│   ├── registration/           # Work registration workflows
│   ├── tasks/                  # Celery task definitions
│   ├── transparency/           # Trust-layer explainability
│   ├── trolley/                # Trolley.io adapter
│   ├── ugc/                    # UGC scanning
│   ├── network/                # Partner/DSP connector abstractions
│   └── modules/                # 8 feature-flagged module plug-ins
├── xr7_common/                 # Settings · logger · universal schema
├── shared/utils/               # numbers · text · currency · dates
├── tests/                      # 106 test files (1,348+ test functions)
├── alembic/versions/           # 30 migration scripts
├── scripts/                    # check_naming_conventions.py · check_domain_boundaries.py
├── openapi/openapi.json        # 436 paths · 288 schemas
├── docs/                       # 72 documentation files
├── infrastructure/             # Terraform + Kustomize (AWS EKS)
├── frontend/                   # React/TypeScript SPA
├── sdk/                        # Python + TypeScript SDKs (auto-generated from OpenAPI)
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── alembic.ini
└── pyproject.toml
```

---

## 4. Naming Conventions

These conventions are enforced by `scripts/check_naming_conventions.py` (runs in CI):

| Term | Correct | Forbidden |
|------|---------|-----------|
| Work name field | `work_title` | ~~`track_title`~~ |
| Work count field | `work_count` | ~~`track_count`~~ |
| Entity type value | `'recording'` | ~~`'track'`~~ |
| JSON entity key | `"entity": "recording"` | ~~`"entity": "track"`~~ |

**Python code standards:**
- Models use SQLAlchemy 2.0 `Mapped[T]` annotations (no legacy `Column()`)
- Schemas use Pydantic v2 `model_config = ConfigDict(from_attributes=True, ...)`
- IDs are UUID strings (`str` type, not `uuid.UUID`)
- All monetary amounts stored as `Decimal` or `float`, displayed in the currency specified by the `currency` field
- Timezone-aware datetimes required everywhere (`datetime.now(timezone.utc)`)

**Domain boundary rules** (enforced by `scripts/check_domain_boundaries.py`):
- `XR7/core/` — may NOT import from `services`, `api`, `recovery`, `fingerprinting`, `ml`, or `sqlalchemy`
- `shared/utils/` — may NOT import from `XR7.*`
- `XR7/api/routers/` — **target state**: all DB access via service layer (active refactor: v2.1)

---

## 5. Dev Workflow

### Prerequisites
- Python 3.12+
- PostgreSQL 16
- Redis 7
- Docker + Docker Compose (optional, recommended)

### Local Setup

```bash
# 1 – Clone and create virtual environment
git clone https://github.com/your-org/ArtistOS.git
cd ArtistOS
python -m venv .venv && source .venv/bin/activate

# 2 – Install dependencies
pip install -e ".[dev]"

# 3 – Configure environment
cp .env.example .env          # fill in DATABASE_URL, REDIS_URL, SECRET_KEY

# 4 – Run migrations
alembic upgrade head

# 5 – Start the API server
uvicorn XR7.api.app:app --reload --port 8000

# 6 – Start the Celery worker (separate terminal)
celery -A XR7.celery_app worker --loglevel=info
```

### Docker Compose (Recommended for Full Stack)

```bash
docker compose up --build
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Flower: http://localhost:5555
```

### Makefile Shortcuts

```bash
make test          # Run pytest
make lint          # Run ruff check
make format        # Run ruff format
make migrate       # Run alembic upgrade head
make check         # Run naming + boundary checkers
make coverage      # Run tests with HTML coverage report
```

---

## 6. Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=XR7 --cov-report=html

# Run a specific domain
pytest tests/test_core_claims_state_machine.py -v
pytest tests/fingerprinting/ -v

# Run only fast unit tests (exclude integration)
pytest -m "not integration"
```

**Test layout:**

| Area | Test Files | Coverage Notes |
|------|-----------|----------------|
| `XR7/core/` | 4 files | Full (state machine, evidence crypto, scoring, variance) |
| API routers | 15+ files | Major CRUD paths; TV/Film and VIP routers included |
| `XR7/fingerprinting/` | 15 files | Unit + integration for all adapters |
| `XR7/agents/` | 3 files | Onboarding + orchestrator graphs |
| `XR7/ml/` | 2 files | Anomaly detector + feedback loop |
| `shared/utils/` | 4 files | One per util module |

**Pre-existing known failures**: 49 tests are marked as expected failures related to external API stubs (PRO connectors, Trolley sandbox). These are not regressions.

---

## 7. n8n Orchestration

Six production-ready n8n workflow JSON templates live in `docs/n8n/workflows/`:

| File | Purpose |
|------|---------|
| `artist_onboarding.json` | Automated artist signup → connector link → first statement ingest |
| `statement_ingestion.json` | Scheduled statement fetch + normalisation trigger |
| `anomaly_alert.json` | Anomaly webhook → analyst Slack alert → ticket creation |
| `claim_lifecycle.json` | Claim state transitions → email notifications → ledger events |
| `partner_onboarding.json` | Partner certification flow (bronze → silver → gold) |
| `gtm_launch.json` | GTM launch-day automation: health check → feature flag enable → announcement |

**Import:** In n8n, go to **Workflows → Import from file** and select any JSON from `docs/n8n/workflows/`.

**Webhook base URL** (configure in n8n credentials): `https://your-xr7-host/api/v1/webhooks/`

---

## 8. API Reference

- **Base URL**: `https://your-host/api/v1/`
- **Auth**: `Authorization: Bearer <JWT>` on all non-public endpoints
- **Interactive docs**: `GET /docs` (Swagger UI) · `GET /redoc` (ReDoc)
- **OpenAPI spec**: `openapi/openapi.json` — 436 paths, 288 schemas

### Core Endpoint Groups

| Group | Prefix | Description |
|-------|--------|-------------|
| Artists | `/artists/` | CRUD, onboarding, recovery dashboard |
| Statements | `/statements/` | Upload, parse, normalise |
| Anomalies | `/anomalies/` | Scan, list, review |
| Claims | `/claims/` | Create, progress, evidence, bulk export |
| Recovery | `/recovery/` | Automation, SOL, priority queue |
| Workflow | `/workflow/` | End-to-end pipeline trigger + preview |
| ML | `/ml/` | Forecast, catalog score, rate benchmark |
| Agents | `/agents/` | LangGraph run, status, interrupt |
| TV/Film | `/tvfilm/` | TV/Film-specific onboarding, audit, claims |
| Admin | `/admin/` | VIP grants, tenant management, feature flags |
| Billing | `/billing/` | Invoice generation, ledger |
| Webhooks | `/webhooks/` | Inbound partner/DSP event hooks |

### n+1 Safety Note
Endpoints that return collections (e.g. `GET /artists/{id}/works`) use `joinedload` to avoid n+1 queries. When adding new collection endpoints, always profile with `SQLALCHEMY_ECHO=1`.

---

## 9. How to Extend XR7 Safely

Follow these steps to add a new feature without violating domain boundaries:

### Adding a new API endpoint

1. Create a router file in `XR7/api/routers/new_feature.py`
2. Define route functions that accept `db: Session = Depends(get_db)` and `current_user = Depends(get_current_user)` from `XR7/api/deps.py`
3. Call a **service class** (in `XR7/services/`) for all business logic — do not put `db.query()` directly in routers (this is the v2.1 refactor target)
4. Register the router in `XR7/api/app.py`
5. Add/update the OpenAPI spec by running `make openapi`

### Adding a new ORM model

1. Create `XR7/models/new_model.py` using `DeclarativeBase` and `Mapped[T]` annotations
2. Import and include in `alembic/env.py` if not already auto-discovered
3. Run `alembic revision --autogenerate -m "add new_model"` and review the generated migration
4. Apply: `alembic upgrade head`

### Adding a new service

1. Create `XR7/services/new_service.py`
2. Service `__init__` should accept `db: Session` if it needs ORM access
3. Never import from `XR7/api/` within a service
4. Add unit tests in `tests/test_new_service.py`

### Adding a new anomaly rule

1. Add rule definition to `XR7/anomaly/rules/`
2. Register it in the rule catalog (`XR7/anomaly/variance_detection_engine.py`)
3. Document the rule in `docs/anomaly_rule_catalog.md`
4. Add a test case in `tests/test_anomaly_*.py`

### Adding a new ingestion format

1. Create a parser in `XR7/ingestion/parsers/new_format.py` implementing the `BaseParser` interface
2. Register it in `XR7/ingestion/parser_registry.py`
3. Document it in `docs/ingestion_format_catalog.md`
4. Add test fixtures and tests

### Adding a new Celery task

1. Define the task in `XR7/tasks/new_task.py` using `@celery_app.task`
2. Tasks should call service-layer methods — not perform ORM queries directly
3. Wire to the appropriate queue in `XR7/celery_app.py`

### Naming rules checklist (run before committing)

```bash
make check       # runs check_naming_conventions.py + check_domain_boundaries.py
```

---

## 10. Production-Readiness Checklist

| Category | Item | Status |
|----------|------|--------|
| **Infrastructure** | EKS manifests + Kustomize overlays | ✅ |
| | Terraform AWS module (VPC, RDS, ElastiCache, S3, KMS) | ✅ |
| | Autoscaling (HPA + cluster autoscaler) | ✅ |
| | Ingress + TLS (cert-manager) | ✅ |
| **Database** | Alembic migrations (30 scripts) | ✅ |
| | Nightly backup cron + restore drill | ✅ |
| | Connection pooling (PgBouncer) | ✅ |
| **Security** | JWT RS256 auth + RBAC | ✅ |
| | Network policies (pod-level isolation) | ✅ |
| | Pod security standards | ✅ |
| | Dependency CVE scan (Trivy + pip-audit in CI) | ✅ |
| | Secret management via AWS Secrets Manager | ✅ |
| **Observability** | OTel collector → Prometheus → Grafana | ✅ |
| | SLO rules + alert manager | ✅ |
| | Structured JSON logging (`xr7_common/logging.py`) | ✅ |
| | Distributed tracing (trace_id propagation) | ✅ |
| **CI/CD** | 12 GitHub Actions workflows | ✅ |
| | Naming convention check in CI | ✅ |
| | Domain boundary check in CI | ✅ |
| | SLO-gated progressive deploy | ✅ |
| **APIs** | OpenAPI 3.1 spec (436 paths, 288 schemas) | ✅ |
| | SDK auto-generation (Python + TypeScript) | ✅ |
| | API versioning strategy | ✅ |
| | Webhook idempotency + retry policy | ✅ |
| **Compliance** | Data retention policy | ✅ |
| | GDPR right-to-erasure endpoint | ✅ |
| | Multi-currency + internationalisation | ✅ |
| **External Integrations** | Trolley MoR | 🔑 key needed |
| | ASCAP / BMI / SESAC API connectors | 🔑 key needed |
| | YouTube / TikTok / Meta OAuth | 🔑 key needed |
| | Ticketmaster / AXS connectors | 🔑 key needed |

---

## 11. Market Readiness

| Component | Status | Notes |
|-----------|--------|-------|
| Artist Recovery Dashboard | ✅ Ready | Leakage, in-pursuit totals, deposits received, calibration health |
| Royalty Estimator Widget | ✅ Ready | MFA-gated, lead capture, results email, CTA |
| Earnings Engine | ✅ Ready | Full historical reconstruction + real-time calculation |
| Anomaly Detection | ✅ Ready | 5-category rule engine; auto-runs after statement upload |
| Claims Orchestration | ✅ Ready | IDENTIFIED → PAID lifecycle with evidence packets |
| Billing Engine | ✅ Ready | 12% contingency fee, invoice generation, Trolley bridge |
| Recovery Tools | ✅ Ready | SOL tracker, audit eligibility, rate benchmark, recoupment, priority queue |
| ML Suite | ✅ Ready | Isolation Forest, earnings forecaster, catalog scorer, rate benchmarker |
| Statement Upload | ✅ Ready | CSV/TSV/XLSX for 15 named formats + generic fallback |
| TV/Film Vertical | ✅ Ready | SAG-AFTRA/WGA/DGA/IATSE rules, cue sheets, role-specific workflows |
| VIP / Founders Circle | ✅ Ready | Invite codes, weekly brief, copilot, concierge, referrals |
| Global Social / UGC | ✅ Ready | UGC scanning + auto-claim workflows |
| White-Label Mode | ✅ Ready | Tenant-level branding flag in settings + readiness endpoint |
| Kubernetes Runtime | ✅ Ready | Base manifests + overlays for dev/staging/prod |
| Infrastructure as Code | ✅ Ready | Full Terraform AWS module |
| Observability Pipeline | ✅ Ready | OTel → Prometheus → Grafana |
| Disaster Recovery | ✅ Ready | Nightly backup, weekly restore drill, DR runbook |
| Platform Security | ✅ Ready | Network policies, pod security, dependency CVE scan |
| Collaborator Viral Loop | ✅ Ready | Co-writer invite panel + HubSpot CRM lead capture |
| Trolley (MoR) | 🔑 Key needed | Integration built; needs `TROLLEY_API_KEY` |
| PRO API Connectors | 🔑 Key needed | Adapter layer built; needs ASCAP/BMI/SESAC credentials |
| Platform API Connectors | 🔑 Key needed | OAuth scaffolding built; needs YouTube/TikTok/Meta credentials |
| Ticketing API Connectors | 🔑 Key needed | Adapter built; needs Ticketmaster/AXS keys |

---

## 12. Glossary

| Term | Definition |
|------|-----------|
| **Work** | A musical composition or TV/Film production work. Field: `work_title` (not `track_title`). |
| **Recording** | A specific recorded version of a Work. `entity_type = 'recording'` (not `'track'`). |
| **UniversalRoyaltyEvent** | The canonical normalised row after ingestion — every statement row maps to one or more `UniversalRoyaltyEvent` records. |
| **Anomaly** | A detected discrepancy in a royalty statement (rate deviation, missing period, territory gap, split discrepancy, or publisher conflict). |
| **Claim** | A formal recovery action initiated against a DSP or PRO for an identified anomaly. Lifecycle: `IDENTIFIED → EVIDENCE_GATHERED → SUBMITTED → ACKNOWLEDGED → IN_DISPUTE → RESOLVED → PAID`. |
| **Variance Row** | A normalised representation of a royalty event used by the variance detection engine. |
| **Confidence Tier** | ML-scored certainty of an anomaly or match: HIGH (≥0.95 auto-approve), MEDIUM (0.80–0.94 analyst queue), LOW (0.60–0.79 mandatory review), UNCERTAIN (<0.60 flag). |
| **Immutable Ledger** | SHA-256 hash-chained audit log. Every workflow run, claim state change, and ledger interaction is appended; entries cannot be modified or deleted. |
| **SOL** | Statute of Limitations — the legal time window within which a royalty recovery claim can be filed. Varies by jurisdiction and contract type. |
| **PRO** | Performing Rights Organisation (e.g., ASCAP, BMI, SESAC, PRS, SOCAN). |
| **DSP** | Digital Service Platform / streaming platform (e.g., Spotify, Apple Music, YouTube). |
| **MLC** | Mechanical Licensing Collective — US body for mechanical royalties from on-demand streaming. |
| **ISRC** | International Standard Recording Code — unique identifier for a recording. |
| **ISWC** | International Standard Musical Work Code — unique identifier for a musical composition. |
| **Tenant** | An organisational namespace within XR7 (e.g., a management company or label). Artists belong to a tenant. |
| **Trolley** | Third-party Merchant of Record used for artist payouts. |
| **LangGraph** | Framework for building stateful, resumable multi-step AI agent workflows. Used for onboarding, recovery, and VIP concierge orchestration. |
| **White-Label** | Mode where XR7 is deployed under a partner's brand. Controlled by `branding_profile` in tenant settings. |
| **VIP / Founders Circle** | Invite-only premium tier for high-value artists with concierge service, weekly AI brief, and exclusive features. |
| **TV/Film Vertical** | Production-grade workflows for SAG-AFTRA, WGA, DGA, IATSE, and studio residual recovery in parity with the music stack. |

---

## Setup Quick Reference

```bash
# Full local stack
docker compose up --build

# API:   http://localhost:8000
# Docs:  http://localhost:8000/docs
# Admin: http://localhost:8000/admin

# Run tests
pytest -x -q

# Apply migrations
alembic upgrade head

# Check naming + boundaries
make check
```

---

## Key Documentation

| Document | Location |
|----------|---------|
| Final Architecture Summary | [docs/final_architecture_summary.md](docs/final_architecture_summary.md) |
| Handoff Packet | [docs/HANDOFF.md](docs/HANDOFF.md) |
| API Maintenance Guide | [docs/openapi_maintenance_guide.md](docs/openapi_maintenance_guide.md) |
| Database Schema & Migrations | [docs/database_schema_and_migrations.md](docs/database_schema_and_migrations.md) |
| Anomaly Rule Catalog | [docs/anomaly_rule_catalog.md](docs/anomaly_rule_catalog.md) |
| Claims State Machine | [docs/claims_state_machine.md](docs/claims_state_machine.md) |
| LangGraph Agent DevOps | [docs/langgraph_agent_devops.md](docs/langgraph_agent_devops.md) |
| Ingestion Format Catalog | [docs/ingestion_format_catalog.md](docs/ingestion_format_catalog.md) |
| Partner Integration Architecture | [docs/partner_integration_architecture.md](docs/partner_integration_architecture.md) |
| AI Augmentation Roadmap | [docs/ai_augmentation_roadmap.md](docs/ai_augmentation_roadmap.md) |
| GTM Technical Plan | [docs/gtm_technical_plan.md](docs/gtm_technical_plan.md) |
| Security Threat Model | [docs/security_threat_model.md](docs/security_threat_model.md) |
| Observability Stack | [docs/observability_monitoring_stack.md](docs/observability_monitoring_stack.md) |
| Disaster Recovery | [docs/disaster_recovery_backup_strategy.md](docs/disaster_recovery_backup_strategy.md) |
| Production Deployment Guide | [docs/production_deployment_guide.md](docs/production_deployment_guide.md) |

---

## License

Proprietary. All rights reserved. © 2026 XR7 Engine 2.
