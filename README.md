# ARCOS7 Engine 2 — Artist Earnings Accuracy Platform

ARCOS7 Engine 2 is a comprehensive platform designed to detect, recover, and prevent earning discrepancies for artists across all revenue streams — streaming royalties, touring settlements, merchandise royalties, sync licensing, brand partnerships, and platform payments.

## Market Readiness

| Component | Status | Notes |
|-----------|--------|-------|
| **Royalty Estimator Widget** | ✅ Ready | MFA-gated, lead capture, results email, CTA — no API keys needed |
| **Earnings Engine** | ✅ Ready | Full historical reconstruction and real-time calculation |
| **Anomaly Detection** | ✅ Ready | 5-category rule engine; runs automatically after statement upload |
| **Claims Orchestration** | ✅ Ready | Full IDENTIFIED → PAID lifecycle with evidence packets |
| **Billing Engine** | ✅ Ready | 10% contingency fee, invoice generation |
| **Recovery Tools** | ✅ Ready | SOL tracker, audit eligibility, rate benchmark, recoupment, priority queue |
| **ML Suite** | ✅ Ready | Isolation Forest anomaly detector, earnings forecaster, catalog scorer, rate benchmarker |
| **Statement Upload** | ✅ Ready | CSV ingestion for DistroKid, TuneCore, CD Baby, ASCAP, BMI, Spotify, generic |
| **PRO API Connectors** | ⚠️ Pending | ASCAP, BMI, SESAC, etc. require formal data-partnership agreements |
| **DSP API Connectors** | ⚠️ Pending | DSPs don't expose royalty data via API — use distributor CSV exports |
| **Platform API Connectors** | ⚠️ Pending | YouTube CMS requires Google partnership; TikTok/IG require approved developer access |
| **Ticketing API Connectors** | ⚠️ Pending | Ticketmaster/AXS require formal partnership agreements |

### Data Ingestion — No API Keys Required

The platform is **fully operational today** using the statement file upload workflow.  Artists download their royalty statements from distributors and PRO portals and upload them as CSV files:

```
POST /artists/{id}/statements/upload   # Upload a CSV statement
GET  /artists/{id}/statements          # See all uploaded statements
```

Supported formats are auto-detected from the column headers:
- **DistroKid** — monthly earnings reports
- **TuneCore** — sale month reports
- **CD Baby** — sales/earnings exports
- **ASCAP** — performance royalty statements
- **BMI** — royalty statement downloads
- **Spotify for Artists** — stream revenue CSV
- **Generic** — any CSV with date, amount, and quantity columns

After upload, anomaly detection runs automatically.

### Checking What's Configured

```
GET /health/readiness
```

Returns the status of every connector and notification service.  Use this endpoint to see exactly which credentials are missing.

---

## Features

- **Statement Upload & Auto-Ingestion**: Upload royalty statement CSVs; events and payments are parsed, persisted, and analysed automatically
- **Multi-Source Connector Architecture**: Pluggable connectors for PROs, DSPs, ticketing platforms, and content platforms (credentials validated via env vars; `connect()` returns `False` rather than silently failing)
- **Rights Graph**: NetworkX-powered directed graph mapping artists, works, and contracts
- **Earnings Engine**: Reconstructs historical earnings and computes real-time expected payments against contract terms
- **Anomaly Detection**: Rule-based detection for royalty underpayments, touring settlement gaps, merch royalty omissions, sync licensing violations, and low platform rates
- **Claims Orchestration**: Full lifecycle management from identification through payment recovery
- **Billing Engine**: 10% contingency fee model with invoice generation and billing summaries
- **ML Suite**: Isolation Forest anomaly detector, linear-regression earnings forecaster, catalog health scorer, comparable-rate benchmarker
- **Royalty Estimator Widget**: MFA-gated public widget (SMS + email OTP) for artist lead capture and indicative royalty estimates
- **REST API**: FastAPI-powered endpoints for all platform operations

## Architecture

```
arcos7/
├── models/         # SQLAlchemy ORM models + Pydantic schemas
├── ingestion/      # CSV statement parser + connector architecture (PRO, DSP, Ticketing, Platform)
├── graph/          # Rights graph (NetworkX DiGraph)
├── earnings/       # Earnings calculation and historical reconstruction
├── anomaly/        # Anomaly detection engine + rule modules
├── recovery/       # Claims lifecycle orchestration
├── billing/        # Contingency billing and invoice management
├── ml/             # ML modules (anomaly detector, forecaster, catalog scorer, rate benchmarker)
├── auth/           # OTP service, notification service (Twilio SMS + SMTP email)
├── widget/         # Royalty estimator widget HTML
└── api/            # FastAPI application and routers
```

## Setup

### Requirements

- Python 3.11+

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env with your credentials
source .env
```

Key variables:
- `ARCOS7_ENV` — set to `production` to enable real Twilio/SMTP and enforce CORS allowlist
- `WIDGET_ADMIN_KEY` — secret key for `GET /widget/leads` admin endpoint
- `WIDGET_ALLOWED_ORIGINS` — comma-separated CORS origins (required in production)
- `TWILIO_*` — SMS delivery for OTP
- `SMTP_*` — email delivery for OTP and results emails
- `DATABASE_URL` — PostgreSQL URL for production (defaults to SQLite)

See `.env.example` for the full list including connector API key variable names.

### Running the API

```bash
uvicorn arcos7.api.app:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Running Tests

```bash
pytest tests/ -v
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/health/readiness` | Connector and credential readiness status |
| POST | `/artists/` | Create artist |
| GET | `/artists/{id}` | Get artist |
| GET | `/artists/{id}/summary` | Earnings + anomaly summary |
| POST | `/artists/{id}/connect` | Check connector credential status |
| GET | `/artists/{id}/earnings` | Earnings summary |
| GET | `/artists/{id}/earnings/history` | Earnings history |
| POST | `/artists/{id}/earnings/reconstruct` | Reconstruct earnings for date range |
| POST | `/artists/{id}/ml/forecast` | ML earnings forecast |
| GET | `/artists/{id}/ml/catalog-health` | ML catalog health score |
| POST | `/artists/{id}/statements/upload` | **Upload royalty statement CSV** |
| GET | `/artists/{id}/statements` | List uploaded statements |
| GET | `/artists/{id}/statements/{statement_id}` | Get statement detail |
| GET | `/artists/{id}/anomalies` | List anomalies |
| POST | `/artists/{id}/anomalies/detect` | Run anomaly detection |
| GET | `/anomalies/{id}` | Get anomaly detail |
| GET | `/artists/{id}/claims` | List claims |
| GET | `/claims/{id}` | Get claim detail |
| POST | `/claims/{id}/advance` | Advance claim status |
| POST | `/claims/{id}/evidence` | Generate evidence packet |
| POST | `/claims/{id}/reconcile` | Reconcile recovered amount |
| GET | `/artists/{id}/billing` | Billing summary |
| GET | `/artists/{id}/invoices` | List invoices |
| GET | `/artists/{id}/recovery/sol-status` | Statute of limitations status |
| GET | `/artists/{id}/recovery/rate-benchmark` | Rate vs. industry benchmark |
| GET | `/artists/{id}/recovery/audit-eligibility` | Audit rights eligibility |
| GET | `/artists/{id}/recovery/recoupment` | Recoupment position |
| GET | `/artists/{id}/recovery/priority-queue` | Prioritised recovery action queue |
| POST | `/widget/register` | Widget Step 1: register + send OTPs |
| POST | `/widget/verify` | Widget Step 2: verify OTPs → estimate token |
| POST | `/widget/estimate` | Widget Step 3: generate + persist estimate |
| POST | `/widget/claim` | Widget: submit recovery claim |
| GET | `/widget/leads` | Admin: list all widget leads (requires X-Admin-Key) |

## License

Proprietary — ARCOS7 Engine 2
