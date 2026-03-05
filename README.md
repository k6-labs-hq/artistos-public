# XR7 Engine 2 — Artist Earnings Accuracy Platform

XR7 Engine 2 is a comprehensive platform designed to detect, recover, and prevent earning discrepancies for artists across all revenue streams — streaming royalties, touring settlements, merchandise royalties, sync licensing, brand partnerships, and platform payments.

## Market Readiness

| Component | Status | Notes |
|-----------|--------|-------|
| **Artist Recovery Dashboard** | ✅ Ready | Single endpoint showing leakage, in-pursuit totals, deposits received, calibration health, balance outstanding, activity feed |
| **Royalty Estimator Widget** | ✅ Ready | MFA-gated, lead capture, results email, CTA — no API keys needed |
| **Earnings Engine** | ✅ Ready | Full historical reconstruction and real-time calculation |
| **Anomaly Detection** | ✅ Ready | 5-category rule engine; runs automatically after statement upload |
| **Claims Orchestration** | ✅ Ready | Full IDENTIFIED → PAID lifecycle with evidence packets |
| **Billing Engine** | ✅ Ready | 10% contingency fee, invoice generation, wired to Celero |
| **Recovery Tools** | ✅ Ready | SOL tracker, audit eligibility, rate benchmark, recoupment, priority queue |
| **ML Suite** | ✅ Ready | Isolation Forest anomaly detector, earnings forecaster, catalog scorer, rate benchmarker |
| **Statement Upload** | ✅ Ready | CSV ingestion for 15 explicit formats (major distributors + PROs + Spotify) plus generic fallback |
| **Celero Commerce (MoR)** | 🔑 Key needed | Integration built; needs `CELERO_SECURITY_KEY` from Celero onboarding |
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
- **Amuse** — royalty report exports
- **United Masters** — earnings export CSV
- **ONErpm** — royalty statement CSV
- **Stem** — earnings report CSV
- **LANDR** — royalty statement CSV
- **Ditto Music** — royalty statement CSV
- **ReverbNation** — earnings report CSV
- **Bandcamp** — sales CSV
- **ASCAP** — performance royalty statements
- **BMI** — royalty statement downloads
- **Spotify for Artists** — stream revenue CSV
- **Generic** — any CSV with date, source/platform, quantity, and amount columns

Get the full machine-readable format catalog (including key columns and descriptions):

```
GET /ingestion/supported-formats
```

After upload, anomaly detection runs automatically.

Before upload, artists must accept the current Artist Recovery Services Agreement:

```
GET  /terms
POST /artists/{id}/terms/accept
```

### Checking What's Configured

```
GET /health/readiness
```

Returns the status of every connector and notification service.  Use this endpoint to see exactly which credentials are missing.

---

## Artist Recovery Dashboard

Every artist has a single endpoint that gives them a complete, real-time
view of their recovery status:

```
GET /artists/{id}/dashboard
```

### What the dashboard shows

**1. Leakage discovered** — every anomaly XR7 has ever found for this artist
```json
"leakage_discovered": {
  "total_anomalies": 14,
  "open_anomalies": 9,
  "total_estimated_recoverable": 48750.00,
  "by_category": {
    "ROYALTY":  {"count": 8, "estimated_recoverable": 32000.00},
    "TOURING":  {"count": 4, "estimated_recoverable": 12000.00},
    "SYNC":     {"count": 2, "estimated_recoverable": 4750.00}
  },
  "by_severity": { ... },
  "recent_discoveries": [ ... ]
}
```

**2. In pursuit** — active claims being worked right now
```json
"in_pursuit": {
  "active_claim_count": 9,
  "total_amount_in_pursuit": 43875.00,
  "total_gross_recovered": 5000.00,
  "total_net_recovered": 4500.00
}
```

**3. Recovered & deposited** — actual money in the artist's account
```json
"recovered_and_deposited": {
  "total_deposited": 4500.00,
  "deposit_count": 2,
  "deposits": [
    {
      "amount": 2700.00,
      "currency": "USD",
      "status": "SETTLED",
      "celero_transaction_id": "TXN-...",
      "deposited_at": "2026-03-01T14:23:00Z"
    }
  ]
}
```

**4. Balance still pursuing** — the headline number
```json
"balance_still_pursuing": {
  "total_in_active_claims": 43875.00,
  "total_deposited_to_date": 4500.00,
  "total_pending_deposit": 1350.00,
  "balance_still_pursuing": 42525.00
}
```

**5. Deadlines** — statute-of-limitations urgency
```json
"deadlines": {
  "expired_count": 1,
  "urgent_count": 2,
  "at_risk_count": 3,
  "ok_count": 7,
  "total_open_anomalies": 13,
  "top_urgent_items": [
    {
      "id": "anomaly-id",
      "category": "ROYALTY",
      "subtype": "RATE_BELOW_MARKET",
      "sol_status": "URGENT",
      "days_remaining": 42,
      "estimated_recoverable": 8500.00
    }
  ]
}
```

**6. Priority actions** — what to work on right now
```json
"priority_actions": {
  "total_open_items": 12,
  "top_10_estimated_recoverable": 38250.00,
  "top_10_actions": [
    {
      "action_type": "FILE_CLAIM",
      "priority_rank": 1,
      "normalised_score": 95.2,
      "estimated_recoverable": 8500.00,
      "sol_status": "URGENT",
      "days_remaining": 42
    }
  ]
}
```

**7. Calibration health** — model confidence reliability from real outcomes
```json
"calibration_health": {
  "overall": {
    "posterior_success_rate": 0.666667,
    "sample_count": 12,
    "sufficient_samples": true
  },
  "by_subtype": {
    "MISSING_MECHANICAL": {
      "posterior_success_rate": 0.75,
      "sample_count": 6,
      "sufficient_samples": true
    }
  },
  "minimum_scope_samples": 3,
  "method": "beta_posterior_blend"
}
```

**8. Catalog health** — ML composite score
```json
"catalog_health": {
  "health_score": 68,
  "grade": "C",
  "signals": {
    "metadata_completeness": 0.45,
    "payment_regularity": 0.82,
    "anomaly_density": 0.61,
    "recovery_rate": 0.70,
    "earnings_accuracy": 0.75
  },
  "recommendations": [
    "Add ISRC codes to 55% of your works to improve metadata completeness"
  ]
}
```

**9. Earnings trend** — 90-day forecast
```json
"earnings_trend": {
  "trend": "GROWING",
  "horizon_days": 90,
  "predicted_total": 12400.00,
  "predicted_low": 10200.00,
  "predicted_high": 14600.00,
  "slope_per_day": 18.50
}
```

**10. Activity feed** — reverse-chronological log of everything that's happened
```json
"activity_feed": [
  {
    "type": "PAYMENT_DEPOSITED",
    "timestamp": "2026-03-01T14:23:00Z",
    "title": "Payment deposited to your account",
    "detail": "$2,700.00 USD deposited via Celero Commerce — status: SETTLED (ref: TXN-abc123)",
    "amount": 2700.00
  },
  {
    "type": "CLAIM_ACCEPTED",
    "timestamp": "2026-02-28T10:00:00Z",
    "title": "Claim accepted — awaiting payment",
    "detail": "ROYALTY claim — $3,000.00 USD"
  },
  {
    "type": "LEAKAGE_DISCOVERED",
    "timestamp": "2026-02-15T09:30:00Z",
    "title": "Leakage detected: MISSING_PAYMENT",
    "detail": "ROYALTY anomaly (HIGH) — estimated recoverable: $3,000.00"
  }
]
```

The dashboard updates automatically every time:
- A new anomaly is detected (statement upload or manual detection)
- A claim status changes
- A Celero disbursement is received (webhook `disbursement.settled`)

### Frontend Integration Quickstart

For priority queue UX, call these two endpoints in order:

1. Fetch calibration health (to show model reliability badges):

```http
GET /artists/{id}/intelligence/calibration
```

Example response (truncated):

```json
{
  "artist_id": "artist-123",
  "overall": {
    "posterior_success_rate": 0.666667,
    "sample_count": 12,
    "sufficient_samples": true
  },
  "by_subtype": {
    "MISSING_MECHANICAL": {
      "posterior_success_rate": 0.75,
      "sample_count": 6,
      "sufficient_samples": true
    }
  },
  "minimum_scope_samples": 3,
  "method": "beta_posterior_blend"
}
```

2. Rank queue items by expected utility:

```http
POST /artists/{id}/intelligence/rank-utility
Content-Type: application/json
```

```json
{
  "analyst_hourly_cost": 100,
  "items": [
    {
      "id": "a1",
      "subtype": "MISSING_MECHANICAL",
      "estimated_recoverable": 3000,
      "success_probability": 0.7,
      "effort_hours": 2
    },
    {
      "id": "a2",
      "subtype": "RATE_DRIFT_LOW",
      "estimated_recoverable": 800,
      "success_probability": 0.8,
      "effort_hours": 1
    }
  ]
}
```

Example response fields used by UI sorting/badges:

```json
{
  "artist_id": "artist-123",
  "count": 2,
  "ranked": [
    {
      "id": "a1",
      "utility_rank": 1,
      "expected_utility": 1900,
      "expected_recovery_value": 2100,
      "calibration": {
        "scope": "subtype:MISSING_MECHANICAL",
        "sufficient_samples": true,
        "sample_count": 6,
        "posterior_success_rate": 0.75
      }
    }
  ]
}
```

---

## Claim Evidence and Legal Packet Workflow

XR7 now supports attorney-ready evidence exports and cryptographic verification for each claim packet.

### Generate or refresh evidence

```bash
curl -X POST "http://localhost:8000/claims/{claim_id}/evidence"
```

### Export evidence for legal review

ZIP package (JSON, CSV citations, PDF summary, integrity manifest, and source attachments when files are present):

```bash
curl -L "http://localhost:8000/claims/{claim_id}/evidence/export?format=zip&refresh=true" \
  -o evidence_{claim_id}.zip
```

PDF summary only:

```bash
curl -L "http://localhost:8000/claims/{claim_id}/evidence/export?format=pdf" \
  -o evidence_{claim_id}.pdf
```

### Verify packet integrity and chain linkage

```bash
curl "http://localhost:8000/claims/{claim_id}/evidence/verify"
```

Optional prior-link check:

```bash
curl "http://localhost:8000/claims/{claim_id}/evidence/verify?expected_prior_packet_hash={prior_hash}"
```

One-command operator helper (archives verification JSON and exits non-zero on any failed check):

```bash
scripts/verify_evidence.sh --claim-id {claim_id}
scripts/verify_evidence.sh --claim-id {claim_id} --expected-prior-hash {prior_hash}
```

Gated verify-then-export helper (recommended for legal handoff):

```bash
scripts/export_evidence.sh --claim-id {claim_id} --format zip --refresh
scripts/export_evidence.sh --claim-id {claim_id} --format pdf
scripts/export_evidence.sh --claim-id {claim_id} --format zip --expected-prior-hash {prior_hash}
```

Verification checks include:
- `packet_hash_matches`
- `chain_hash_matches`
- `line_hashes_match`
- `signature_valid`
- `prior_link_matches` (when expected prior hash is supplied)

### Signing modes (HMAC and RSA)

Default mode is HMAC:

```bash
export XR7_EVIDENCE_SIGNING_MODE="hmac"
export XR7_EVIDENCE_HMAC_SECRET="replace-with-long-random-secret"
```

Asymmetric RSA mode:

```bash
export XR7_EVIDENCE_SIGNING_MODE="rsa"
export XR7_EVIDENCE_PRIVATE_KEY_PEM="-----BEGIN PRIVATE KEY-----..."
export XR7_EVIDENCE_PUBLIC_KEY_PEM="-----BEGIN PUBLIC KEY-----..."
```

Each packet includes metadata:
- `metadata.packet_version` (current: `1.1`)
- `metadata.revision` (increments per regenerated packet)
- `integrity.packet_hash`, `integrity.prior_packet_hash`, `integrity.chain_hash`, `integrity.signature`

### Production Security Checklist

Use this checklist before relying on exported packets in active disputes or litigation:

1. Enforce asymmetric signing in production:
`XR7_EVIDENCE_SIGNING_MODE=rsa`

2. Store private keys outside source control:
Inject `XR7_EVIDENCE_PRIVATE_KEY_PEM` through a secrets manager (not `.env` committed to git).

3. Publish public verification key to counsel:
Share `XR7_EVIDENCE_PUBLIC_KEY_PEM` with external attorneys/auditors so they can independently verify signatures.

4. Rotate signing keys on a fixed cadence:
Recommended every 90 days, and immediately after any key exposure event.

5. Preserve prior public keys for historical verification:
Do not delete old verify keys until all packets signed with those keys are no longer needed.

6. Require verification before attorney handoff:
Call `GET /claims/{claim_id}/evidence/verify` and ensure `valid=true`.

7. Enforce chain-link checks for revised packets:
When reviewing revisions, pass `expected_prior_packet_hash` and require `prior_link_matches=true`.

8. Treat any failed integrity check as a stop condition:
If any check fails (`packet_hash_matches`, `chain_hash_matches`, `line_hashes_match`, or `signature_valid`), regenerate and investigate before external submission.

9. Keep immutable export archives:
Store exported ZIP packets in write-once or append-only storage with retention policy.

10. Log verification outcomes:
Persist verification timestamp, claim id, packet hash, signer mode, and result for compliance audit trails.

Detailed operational procedure:
`docs/evidence_security_runbook.md`

---

## Celero Commerce — Merchant of Record Integration

Celero Commerce acts as the **Merchant of Record** for all XR7 payments:

- Celero legally processes every contingency-fee transaction on behalf of XR7.
- Celero handles **tax compliance** (sales tax, VAT, etc.) automatically.
- Celero issues receipts and manages chargebacks with the card networks.
- Artists' payment credentials are stored in the **Celero Customer Vault** — XR7 never handles raw card data (PCI scope stays entirely with Celero).
- Artist disbursements (the 90% net recovery share) are sent as **ACH credits** via Celero.

### Payment flow

```
1. Claim recovered → status = PAID
       ↓
2. POST /artists/{id}/celero/charge
   (charges 10% contingency fee via artist's vaulted payment method)
       ↓
3. Celero webhook: transaction.approved
   → Claim status → CLOSED
       ↓
4. POST /artists/{id}/celero/disburse
   (ACH credit of 90% net to artist's bank account in vault)
       ↓
5. Celero webhook: disbursement.settled
   → CeleroTransaction status → SETTLED
```

### Setup (3 steps)

**Step 1** — Get sandbox credentials:
Request a sandbox merchant key at https://celerocommerce.com/developers/

**Step 2** — Set environment variables:
```bash
export CELERO_SECURITY_KEY="your-key-from-celero"
export CELERO_WEBHOOK_SECRET="your-webhook-secret"
# Optional — defaults to NMI sandbox:
# export CELERO_API_URL="https://secure.networkmerchants.com/api/transact.php"
```

**Step 3** — Configure webhook URL in Celero merchant dashboard:
```
Settings → Webhooks → Add Endpoint
URL: https://your-domain.com/celero/webhook
Events: transaction.approved, transaction.declined, transaction.void,
        transaction.refund, disbursement.settled, disbursement.failed
```

### Artist onboarding with Celero

1. **Register artist** — `POST /artists/{id}/celero/register` (contact details → vault ID)
2. **Collect payment method** — Direct artist to Celero's hosted Collect.js or Collect Checkout form (no card data touches XR7 servers)
3. **Verify** — `GET /artists/{id}/celero/status` confirms vault registration and transaction history

### Check integration status

```
GET /health/readiness
```

Look for the `merchant_of_record` section:
```json
{
  "merchant_of_record": {
    "provider": "Celero Commerce",
    "gateway": "Celero Connect®",
    "api_configured": true,
    "webhook_secret_configured": true,
    "status": "ready"
  }
}
```

---

## Features

- **End-to-End Recovery Lifecycle**: Ingestion -> anomaly detection -> claim orchestration -> billing -> Celero payout tracking in a single API surface.
- **15-Format Statement Ingestion + Generic Fallback**: Explicit parsers for DistroKid, TuneCore, CD Baby, Amuse, United Masters, ONErpm, Stem, LANDR, Ditto, ReverbNation, Bandcamp, ASCAP, BMI, Spotify, plus generic CSV detection.
- **Terms & Conditions Compliance Gate**: Required agreement acceptance (`GET /terms`, `POST /artists/{id}/terms/accept`) is enforced before statement upload.
- **Artist Recovery Dashboard**: Unified artist dashboard with leakage discovered, claims in pursuit, deposited funds, calibration health, pursuing balance, deadlines, priority actions, catalog health, earnings trend, and activity feed.
- **Connector Readiness & Credential Visibility**: `GET /health/readiness` and `POST /artists/{id}/connect` expose integration readiness without making external network calls.
- **Celero Commerce Merchant-of-Record**: Vault registration, customer updates, contingency charges, ACH disbursements, refund/void handling, transaction history, and signed webhook processing.
- **Recovery Tooling Suite**: Statute-of-limitations classification, rate benchmarking, audit-rights eligibility analysis, recoupment tracking, and ranked priority action queue.
- **ML Capabilities**: Catalog health scoring, earnings forecasting, anomaly support tooling, and royalty estimate modeling.
- **MFA-Gated Widget Funnel**: Register/verify/estimate/claim flow with OTP rate limits, lockout, token expiry, lead persistence, and optional admin retrieval endpoint.
- **Security & Production Controls**: CORS allowlist enforcement in production, admin key protection for widget leads, webhook signature verification, and environment-based readiness diagnostics.
- **Comprehensive Test Coverage**: Test modules across ingestion, Celero, dashboard, recovery tools, terms flow, widget auth, ML, models, anomaly, and billing.

## Functionality Map

- **Core API and health**:
`GET /health`, `GET /health/readiness`
- **Artist management and summaries**:
`POST /artists/`, `GET /artists/{id}`, `POST /artists/{id}/connect`, `GET /artists/{id}/summary`, `GET /artists/{id}/ml/catalog-health`, `GET /artists/{id}/dashboard`
- **Terms and legal acceptance**:
`GET /terms`, `POST /artists/{id}/terms/accept`, `GET /artists/{id}/terms/status`
- **Ingestion and statement operations**:
`GET /ingestion/supported-formats`, `POST /artists/{id}/statements/upload`, `GET /artists/{id}/statements`, `GET /artists/{id}/statements/{statement_id}`
- **Anomaly and claims operations**:
`GET /artists/{id}/anomalies`, `GET /anomalies/{id}`, `POST /artists/{id}/anomalies/detect`, `GET /artists/{id}/claims`, `GET /claims/{id}`, `POST /claims/{id}/advance`, `POST /claims/{id}/evidence`, `GET /claims/{id}/evidence/export`, `GET /claims/{id}/evidence/verify`, `POST /claims/{id}/reconcile`
- **Earnings and billing**:
`GET /artists/{id}/earnings`, `GET /artists/{id}/earnings/history`, `POST /artists/{id}/earnings/reconstruct`, `POST /artists/{id}/ml/forecast`, `GET /artists/{id}/billing`, `GET /artists/{id}/invoices`
- **Recovery analytics**:
`GET /artists/{id}/recovery/sol-status`, `GET /artists/{id}/recovery/rate-benchmark`, `GET /artists/{id}/recovery/audit-eligibility`, `GET /artists/{id}/recovery/recoupment`, `GET /artists/{id}/recovery/priority-queue`
- **Recovery intelligence**:
`POST /artists/{id}/intelligence/ledger/ingest`, `POST /artists/{id}/intelligence/contracts/extract`, `POST /artists/{id}/intelligence/contracts/extract-upload`, `POST /artists/{id}/intelligence/simulate-expected-payout`, `POST /artists/{id}/intelligence/feedback`, `POST /artists/{id}/intelligence/rank-utility`, `GET /artists/{id}/intelligence/calibration`
- **Widget funnel and lead ops**:
`POST /widget/register`, `POST /widget/verify`, `POST /widget/estimate`, `POST /widget/claim`, `GET /widget/leads` (requires `X-Admin-Key`)
- **Celero merchant-of-record**:
`POST /artists/{id}/celero/register`, `GET /artists/{id}/celero/status`, `PUT /artists/{id}/celero/customer`, `POST /artists/{id}/celero/charge`, `POST /artists/{id}/celero/disburse`, `POST /artists/{id}/celero/transactions/{transaction_id}/refund`, `POST /artists/{id}/celero/transactions/{transaction_id}/void`, `GET /artists/{id}/celero/transactions`, `GET /artists/{id}/celero/transactions/{transaction_id}`, `POST /celero/webhook`

## Architecture

```
XR7/
├── models/         # SQLAlchemy ORM models + Pydantic schemas
├── ingestion/      # CSV statement parser + connector architecture (PRO, DSP, Ticketing, Platform)
├── celero/         # Celero Commerce Merchant of Record (client, webhook handler)
├── graph/          # Rights graph (NetworkX DiGraph)
├── earnings/       # Earnings calculation, historical reconstruction, artist dashboard engine
├── anomaly/        # Anomaly detection engine + rule modules
├── recovery/       # Claims lifecycle orchestration
├── billing/        # Contingency billing, invoice management, Celero payment methods
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
- `XR7_ENV` — set to `production` to enable real Twilio/SMTP and enforce CORS allowlist
- `WIDGET_ADMIN_KEY` — secret key for `GET /widget/leads` admin endpoint
- `WIDGET_ALLOWED_ORIGINS` — comma-separated CORS origins (required in production)
- `TWILIO_*` — SMS delivery for OTP
- `SMTP_*` — email delivery for OTP and results emails
- `DATABASE_URL` — PostgreSQL URL for production (defaults to SQLite)
- `CELERO_SECURITY_KEY` — **Celero Commerce merchant key** (issued during Celero onboarding; request at https://celerocommerce.com/developers/)
- `CELERO_WEBHOOK_SECRET` — HMAC-SHA256 secret for validating Celero webhook payloads (set in Celero dashboard → Settings → Webhooks)
- `CELERO_API_URL` — override gateway URL (defaults to NMI sandbox; live URL provided during production onboarding)
- `XR7_EVIDENCE_SIGNING_MODE` — `hmac` (default) or `rsa` for evidence packet signing
- `XR7_EVIDENCE_HMAC_SECRET` — secret used when signing mode is `hmac`
- `XR7_EVIDENCE_PRIVATE_KEY_PEM` — PEM private key used when signing mode is `rsa`
- `XR7_EVIDENCE_PUBLIC_KEY_PEM` — PEM public key used to verify RSA signatures

See `.env.example` for the full list including connector API key variable names.

### Running the API

```bash
uvicorn XR7.api.app:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Running Tests

```bash
pytest tests/ -v
```

## Roadmap (Market-Driven Additions)

The following additions are prioritised based on current market reality: widespread underpayments, artist demand for transparency + automation, slow external partnerships, and litigation-grade evidence requirements.

### High Priority (Quick Wins and Core Experience)

- Mobile/responsive dashboard expansion (`/dashboard/ui`) so artists and managers can operate from phones and tablets.
- Event notifications by SMS/email for key lifecycle moments: anomaly detected, urgent SOL deadline, claim advanced, and deposit received.
- Bulk statement upload and batch processing for multi-year historical recovery work.
- Dashboard visual analytics: earnings trends, leakage by category over time, and forecast confidence bands.
- Exportable reporting (PDF/CSV): leakage totals, recovered vs potential, and catalog health signal breakdown.
- Contract ingestion improvements for `/artists/{id}/intelligence/contracts/extract-upload`: stronger OCR for scanned PDFs and highlighted key clauses (rate, recoupment, audit rights).

### Competitive Differentiation

- Semi-automated ingestion fallbacks where full APIs are unavailable (secure OAuth where feasible; guided browser-assisted workflows where not).
- Collaborative team access with scoped roles (artist, manager, attorney) and permission boundaries.
- Benchmark intelligence with anonymized peer percentiles by catalog profile.
- Trust-marketing metrics and success stories using safe aggregated outcomes (total recovered, average uplift).
- Self-service claim templates (letters/emails) prefilled by anomaly type and evidence context.
- Better international support: non-USD handling, FX normalization, and baseline withholding tax estimation.

### Strategic

- Priority API partnership program (target at least one major PRO/distributor integration once traction milestones are met).
- Optional immutable evidence lineage layer on top of current hashing/signature chain.
- Predictive recovery scoring model to estimate total recoverable value by artist.
- In-product education layer (download guides, dispute playbooks, SOL explainers by jurisdiction).
- White-label B2B deployment mode for labels, managers, and law firms.
- Audit-rights exercise workflow: draft demand letters, timeline tracking, and counterparty response handling.

Detailed phased implementation plan and acceptance criteria:
`docs/product_expansion_backlog.md`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/health/readiness` | Connector and credential readiness status |
| GET | `/dashboard/ui` | Serve the standalone recovery dashboard frontend |
| POST | `/artists/` | Create artist |
| GET | `/artists/{id}` | Get artist |
| GET | `/terms` | Get current terms text/version/hash |
| POST | `/artists/{id}/terms/accept` | Accept current terms version (required before statement upload) |
| GET | `/artists/{id}/terms/status` | Check whether artist accepted current terms |
| **GET** | **`/artists/{id}/dashboard`** | **Artist recovery dashboard — leakage, in pursuit, deposits, calibration health, balance, activity feed** |
| GET | `/artists/{id}/summary` | Earnings + anomaly summary |
| POST | `/artists/{id}/connect` | Check connector credential status |
| GET | `/artists/{id}/earnings` | Earnings summary |
| GET | `/artists/{id}/earnings/history` | Earnings history |
| POST | `/artists/{id}/earnings/reconstruct` | Reconstruct earnings for date range |
| POST | `/artists/{id}/ml/forecast` | ML earnings forecast |
| GET | `/artists/{id}/ml/catalog-health` | ML catalog health score |
| GET | `/ingestion/supported-formats` | List explicit CSV formats + key columns and generic fallback |
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
| GET | `/claims/{id}/evidence/export` | Export attorney-ready evidence package (`format=zip|pdf`, optional `refresh=true`) |
| GET | `/claims/{id}/evidence/verify` | Verify evidence packet integrity, signature, and optional prior hash link |
| POST | `/claims/{id}/reconcile` | Reconcile recovered amount |
| GET | `/artists/{id}/billing` | Billing summary |
| GET | `/artists/{id}/invoices` | List invoices |
| GET | `/artists/{id}/recovery/sol-status` | Statute of limitations status |
| GET | `/artists/{id}/recovery/rate-benchmark` | Rate vs. industry benchmark |
| GET | `/artists/{id}/recovery/audit-eligibility` | Audit rights eligibility |
| GET | `/artists/{id}/recovery/recoupment` | Recoupment position |
| GET | `/artists/{id}/recovery/priority-queue` | Prioritised recovery action queue |
| POST | `/artists/{id}/intelligence/ledger/ingest` | Ingest canonical royalty ledger rows with source lineage |
| POST | `/artists/{id}/intelligence/contracts/extract` | Extract contract terms from raw text and persist term snapshots |
| POST | `/artists/{id}/intelligence/contracts/extract-upload` | Upload `.txt/.md/.pdf/.image` contract and extract terms |
| POST | `/artists/{id}/intelligence/simulate-expected-payout` | Simulate expected payout with rate, withholding, and FX inputs |
| POST | `/artists/{id}/intelligence/feedback` | Record recovery outcomes for calibration and learning |
| POST | `/artists/{id}/intelligence/rank-utility` | Rank actions by expected utility using calibrated success probabilities |
| GET | `/artists/{id}/intelligence/calibration` | Calibration health summary (overall + subtype posterior success rates) |
| POST | `/widget/register` | Widget Step 1: register + send OTPs |
| POST | `/widget/verify` | Widget Step 2: verify OTPs → estimate token |
| POST | `/widget/estimate` | Widget Step 3: generate + persist estimate |
| POST | `/widget/claim` | Widget: submit recovery claim |
| GET | `/widget/leads` | Admin: list all widget leads (requires X-Admin-Key) |
| **Celero Commerce (Merchant of Record)** | | |
| POST | `/artists/{id}/celero/register` | Register artist in Celero Customer Vault |
| GET | `/artists/{id}/celero/status` | Artist Celero registration + transaction summary |
| PUT | `/artists/{id}/celero/customer` | Update artist contact info in Celero vault |
| POST | `/artists/{id}/celero/charge` | Charge contingency fee for a reconciled claim |
| POST | `/artists/{id}/celero/disburse` | Disburse net recovery to artist via ACH |
| POST | `/artists/{id}/celero/transactions/{transaction_id}/refund` | Refund a charge |
| POST | `/artists/{id}/celero/transactions/{transaction_id}/void` | Void an unsettled charge |
| GET | `/artists/{id}/celero/transactions` | List all Celero transactions |
| GET | `/artists/{id}/celero/transactions/{transaction_id}` | Get transaction detail |
| POST | `/celero/webhook` | Receive Celero Commerce webhook events |

## Expansion Endpoints (Now Live)

The roadmap capabilities below are implemented and available in the API:

Team access enforcement note:
- After at least one team member exists for an artist, artist-scoped expansion endpoints require `X-Actor-Email` (and optional `X-Actor-Role`) matching a team member.
- Bootstrap rule: the first `POST /artists/{id}/team/members` entry must use role `artist`.
- Only `artist` role can add/remove team members; `manager` and `attorney` are read/operations roles.

- **Mobile/responsive dashboard frontend + charts + export actions**:
`GET /dashboard/ui`, `GET /artists/{id}/dashboard/charts`
- **Event notifications (preferences + dispatch + urgent SOL checks)**:
`GET /artists/{id}/notifications/preferences`,
`PUT /artists/{id}/notifications/preferences`,
`POST /artists/{id}/notifications/dispatch`,
`POST /artists/{id}/notifications/urgent-sol-check`
- **Bulk statement upload / batch processing**:
`POST /artists/{id}/statements/upload-batch`
- **Exportable summary reports (JSON/CSV/PDF)**:
`GET /artists/{id}/reports/summary?format=json|csv|pdf`
- **Contract ingestion improvements (OCR + clause highlights)**:
`POST /artists/{id}/intelligence/contracts/extract-upload`,
`POST /artists/{id}/intelligence/contracts/extract`
- **Integration fallbacks / semi-automated pulling setup**:
`POST /artists/{id}/connect/oauth-session`,
`GET /artists/{id}/connect/fallbacks`
- **Collaborative team access (artist/manager/attorney)**:
`POST /artists/{id}/team/members`,
`GET /artists/{id}/team/members`,
`DELETE /artists/{id}/team/members/{member_id}`
- **Benchmark percentile comparisons**:
`GET /artists/{id}/recovery/benchmark-percentiles`
- **Public aggregate success metrics**:
`GET /stats/public/recovery`
- **Self-service claim templates**:
`POST /artists/{id}/claims/templates`
- **International withholding + FX estimates**:
`POST /artists/{id}/intelligence/withholding-estimate`
- **Immutable evidence anchoring + verification chain**:
`POST /claims/{claim_id}/evidence/anchor`,
`GET /claims/{claim_id}/evidence/verify`
- **Predictive total recoverable scoring**:
`POST /artists/{id}/ml/predict-recoverable`
- **Education/community layer endpoints**:
`GET /education/guides`, `GET /education/guides/{guide_id}`
- **White-label/B2B portfolio view**:
`GET /b2b/portfolio/{org_id}`
- **Audit-rights exercise workflow bootstrap**:
`GET /artists/{id}/recovery/audit-demand-letter`
- **Partnership pipeline visibility**:
`GET /partnerships/targets`

## License

Proprietary — XR7 Engine 2
