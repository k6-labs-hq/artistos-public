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
| **Statement Upload** | ✅ Ready | CSV/TSV/XLSX ingestion for 15 explicit formats (major distributors + PROs + Spotify + SoundCloud) plus generic fallback |
| **Global Social Scanning** | ✅ Ready | Endpoint + mobile dashboard UI for global UGC signal scanning and auto-claim workflows |
| **White-Label Mode** | ✅ Ready | Tenant-level branding flag exposed via settings and readiness endpoint |
| **Celero Commerce (MoR)** | 🔑 Key needed | Integration built; needs `CELERO_SECURITY_KEY` from Celero onboarding |
| **PRO API Connectors** | ⚠️ Pending | ASCAP, BMI, SESAC, etc. require formal data-partnership agreements |
| **DSP API Connectors** | ⚠️ Pending | DSPs don't expose royalty data via API — use distributor CSV exports |
| **Platform API Connectors** | ⚠️ Pending | YouTube CMS requires Google partnership; TikTok/IG require approved developer access |
| **Ticketing API Connectors** | ⚠️ Pending | Ticketmaster/AXS require formal partnership agreements |

### Data Ingestion — No API Keys Required

The platform is **fully operational today** using the statement file upload workflow.  Artists download their royalty statements from distributors and PRO portals and upload them as CSV files:

```
POST /artists/{id}/statements/upload   # Upload a CSV/TSV/XLSX statement
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
- **SoundCloud** — monetization exports (CSV/TSV/XLSX)
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

The readiness payload now also includes:
- `global_social` (simulation toggle + API key presence)
- `white_label` (enabled/disabled + deployment status)

### Global Social + Mobile UI

Use the new fetcher for global social opportunity detection:

```
POST /artists/{id}/fetchers/global-social
```

Serve the mobile-first dashboard shell:

```
GET /dashboard/ui
```

### Onboarding Lifecycle Status

Track artist onboarding progression through the state machine:

```
GET /artists/{id}/onboarding/status
```

Status flow:
- `NEW` -> artist record created
- `ONBOARDED` -> terms accepted
- `ACTIVE` -> first statement successfully ingested

### Analyst Review Queue and Admin Console

Analyst queue (requires `ANALYST_API_KEY` and `X-Analyst-Email`):

```
GET  /review-queue/items
POST /review-queue/items
POST /review-queue/items/{id}/assign
POST /review-queue/items/{id}/decision
GET  /review-queue/metrics
POST /review-queue/threshold-check
```

Admin operator console (requires `ADMIN_API_KEY` via `X-Admin-Key`):

```
GET /admin/overview
GET /admin/artists
GET /admin/claims
GET /admin/anomalies
GET /admin/transactions
GET /admin/review-queue
GET /admin/audit-logs
```

### SDK Generation

Generate OpenAPI clients for Python and TypeScript:

```
make sdks
```

Or generate per-language:

```
make sdk-python
make sdk-typescript
```

### ML Feedback and Calibration

Structured ML feedback ingestion endpoint:

```
POST /artists/{id}/intelligence/feedback
GET  /artists/{id}/intelligence/feedback/events
GET  /artists/{id}/intelligence/calibration
```

Calibration now includes posterior parameters, credible intervals, and scope-level metadata for subtype/category/segment.

### HubSpot CRM Sync

Set environment variables:

```
HUBSPOT_ENABLED=true
HUBSPOT_BASE_URL=https://api.hubapi.com
HUBSPOT_PRIVATE_APP_TOKEN=...
# or HUBSPOT_API_KEY=...
```

HubSpot sync is triggered asynchronously from artist creation, widget funnel events, first statement ingestion, anomaly detection, claim milestones, and settled recovery disbursements.

### HubSpot Auto-Enrichment From Statement Uploads

When artists upload `CSV/TSV/XLSX` statements, XR7 extracts and syncs available metadata into HubSpot:

- artist identity signals (name/email fallbacks)
- distributor account metadata
- PRO writer identifiers (for example IPI/CAE fields)
- catalog metadata (titles, ISRC/ISWC/UPC samples)
- earnings and recovery signals

Mapped CRM objects:

| HubSpot Object | XR7 Mapping |
|---|---|
| Contact | `xr7_artist_id`, identity fields, distributor/pro identifiers, summary metrics |
| Company | artist brand, label/publisher entities, distributor entities |
| Deal | `XR7 Recovery - {artist_name}`, amount=`estimated_recoverable`, stage=`Discovery`, pipeline=`Artist Recovery` |

Custom properties populated:

- `xr7_estimated_recoverable`
- `xr7_total_recovered`
- `xr7_catalog_health_score`
- `xr7_anomaly_count`
- `xr7_claim_count`
- `xr7_distributor_list`
- `xr7_pro_affiliations`

Fallback behavior:

- Missing email -> placeholder contact email (`{artist_id}@placeholder.xr7.local`) is used and later updated when verified email is available.
- Missing artist name -> inferred from statement metadata/distributor account context.

### Optional OAuth Intake Prefill Sources

Supported optional intake prefill providers:

- Google OAuth (`openid email profile`)
- Apple Sign-In (`name email`)
- Spotify for Artists OAuth
- YouTube OAuth

OAuth prefill stores only non-sensitive profile metadata and helps seed CRM contact/company context. Royalty ingestion still works without OAuth.

### Recovery Intelligence Feature Matrix

| Capability | Primary Module(s) | API Surface |
|---|---|---|
| 1. Cash recovery forecast (per claim) | `XR7/recovery/cash_recovery_forecast.py` | `GET /claims/{claim_id}/forecast`, `GET /artists/{id}/claims` (includes `forecast`) |
| 2. Automated payer-specific playbooks | `XR7/recovery/payer_playbooks/` | `GET /claims/{claim_id}/playbook`, `GET /artists/{id}/recovery/playbook-summary` |
| 3. Deadline risk engine | `XR7/recovery/deadline_risk_engine.py` | `GET /artists/{id}/recovery/deadline-risk`, dashboard `deadlines.deadline_risk`; Celery: `xr7.pipeline.auto_escalate_claims`, `xr7.pipeline.notify_deadline_risk` |
| 4. Evidence strength scoring | `XR7/recovery/evidence_strength.py` | `GET /claims/{claim_id}/evidence/strength`; integrated into claim advancement and review queue evidence checks |
| 5. Negotiation intelligence | `XR7/recovery/negotiation_intelligence.py` | `GET /claims/{claim_id}/negotiation-intel`; integrated into claim advancement review signals |
| 6. Weekly artist digest | `XR7/recovery/weekly_digest.py` | `GET /artists/{id}/digest/weekly`; Celery: `xr7.pipeline.weekly_artist_digest` |
| 7. Smart contract QA before signature | `XR7/ml/contract_term_extractor.py` | `POST /artists/{id}/intelligence/contracts/pre-signature-review` |
| 8. Contributor split verification | `XR7/recovery/split_verification.py` | `GET /artists/{id}/splits/verification`, `GET /artists/{id}/splits/conflicts` |
| 9. Bank-grade trust controls | `XR7/recovery/orchestrator.py`, `XR7/models/evidence_anchor.py` | `POST /claims/{claim_id}/evidence/export?mode=expert`, `GET /claims/{claim_id}/evidence/verify` |
| 10. Partner ecosystem connectors | `XR7/ingestion/connectors/partner_ecosystem.py` | `POST /artists/{id}/connect/{provider}`, `GET /artists/{id}/connect/{provider}/status` |
| 11. HubSpot CRM auto-populate | `XR7/services/hubspot_client.py`, `XR7/tasks/hubspot.py` | Async triggers from artist/widget/ingestion/anomaly/claim/recovery lifecycle events |
| 12. Output quality requirements | Existing architecture (`FastAPI`, `SQLAlchemy`, `Celery`, `Redis`) + tests | OpenAPI + SDK flow (`make sdks`), regression suite (`pytest`) |

Partner connector environment variables are documented in `.env.example` (for example `STRIPE_CONNECT_TOKEN`, `CHARTMETRIC_TOKEN`, `SONGTRUST_TOKEN`, `ASCAP_TOKEN`, `BMI_TOKEN`, `SESAC_TOKEN`).

---

## Autonomous AI Onboarding & Recovery Agents

XR7 Engine 2 now includes a fully autonomous, LangGraph-powered agent orchestra that handles
artist onboarding, catalog preparation, and royalty recovery with minimal friction and
maximum transparency.

Key capabilities:
- Zero-friction onboarding: drag-and-drop statements, automatic portal guidance, file repair, and catalog building.
- Smart expectations: baseline earnings estimates and readiness scoring.
- Early wins: automatic identification and drafting of the first quick-win claim.
- Deep intelligence: UGC discovery, rights conflict detection, contract extraction, and metadata registration.
- Human-in-the-loop only when necessary: high-value claims and legal escalations are paused for review with traceability.

Agents include:
- ArtistIntentInterpreterAgent
- PortalAutoNavigatorAgent
- SmartUploadFixerAgent
- CatalogAutoBuilderAgent
- DistributorSyncAgent
- ArtistExplainerAgent
- EarningsExpectationAgent
- AutoSplitResolverAgent
- ArtistComfortAgent
- FirstClaimFastTrackAgent
- ArtistProfileEnricherAgent
- WelcomeSummaryAgent
- AutoMetadataRegistrarAgent
- RightsConflictDetectorAgent
- SocialUGCCollectorAgent
- AutoContractExtractorAgent
- ReleaseTimelineAgent
- ArtistReadinessScoreAgent
- AutoFollowUpAgent
- ArtistPersonaAdapterAgent

LangGraph orchestration details:
- Stateful execution model with typed graph state and per-node confidence scores.
- Reflection/self-critique loop when confidence drops below threshold.
- Checkpointer support via `LANGGRAPH_CHECKPOINTER_URL` and thread-scoped run IDs.
- Interrupt safety before escalation/disbursement for high-stakes transitions.

Dashboard exposure:
- `agent_orchestra_status` with current step, confidence, and trace URL.
- `onboarding_progress`, `comfort_messages`, `portal_guidance`, `fast_track_claim`.
- `expected_earnings`, `public_profile`, `readiness_score`, `ugc_opportunities`.
- `catalog_profile`, `split_conflicts`, `registration_actions`, `follow_up_actions`.

Scheduler behavior:
- Every 6 hours: run onboarding completion + new-data recovery workflows.
- Every 24 hours: run follow-up/readiness workflows.
- Event-triggered: statement uploads and UGC fetches enqueue autonomous runs.

Every critical decision is logged with evidence hashes and trace events for auditability.

## Ultra-Simple Artist Onboarding Flow

XR7 is now the **Merchant of Record** path for recovery operations, which removes traditional payment underwriting friction during onboarding. Artists can start immediately with a lightweight intake and statement upload flow.

### 3-Step Onboarding (Under 5 Minutes)

1. **Accept terms**
2. **Upload statements** (`CSV`, `TSV`, `XLSX`)
3. **Get first anomaly + first claim auto-drafted**

```text
+-------------------+      +------------------------+      +-----------------------------+
| 1) Accept Terms   | ---> | 2) Upload Statements   | ---> | 3) Auto Insight + Draft     |
| /terms + /accept  |      | /statements/upload     |      | anomaly + fast-track claim  |
+-------------------+      +------------------------+      +-----------------------------+
```

### API Walkthrough

```bash
# 1) Terms
curl -X GET  http://localhost:8000/terms
curl -X POST http://localhost:8000/artists/{artist_id}/terms/accept

# 2) Statement upload
curl -X POST "http://localhost:8000/artists/{artist_id}/statements/upload" \
  -F "file=@statement.csv"

# 3) Dashboard value appears as ingestion/anomaly pipeline runs
curl -X GET "http://localhost:8000/artists/{artist_id}/dashboard"
```

### What XR7 Does Automatically

- **Format detection** across explicit and generic statement schemas
- **Metadata repair** for missing/ambiguous title, ISRC, and source fields
- **Catalog graph building** and inferred work-linking
- **Split verification** and conflict surfacing
- **UGC opportunity scanning** and related monetization candidates
- **SOL classification** with urgency ranking
- **Anomaly detection** and recoverable estimate scoring
- **FirstClaimFastTrackAgent draft** generation for the highest-value quick win

### What Artists Do NOT Need To Do

- **No underwriting workflow**
- **No bank setup during onboarding**
- **No tax-form upload before first insight**
- **No API keys**
- **No direct portal integrations to get started**
- **No manual anomaly triage for first draft**

## Pre-Populated Intake Form Integrations

XR7 supports optional OAuth-assisted intake prefill. This speeds onboarding while keeping credential use scoped and transparent.

### Providers and Scopes

| Provider | Purpose | Suggested Scopes | Prefilled Fields |
|---|---|---|---|
| **Google OAuth** | Basic profile prefill | `openid`, `email`, `profile` | Name, email, avatar |
| **Apple Sign-In** | Privacy-forward identity prefill | `name`, `email` | Name, Apple relay email |
| **Spotify for Artists OAuth** | Public artist profile and catalog hints | `user-read-email`, `user-read-private` (and partner-approved artist scopes when available) | Display name, artist URI, public catalog metadata |
| **YouTube OAuth** | Channel metadata for UGC matching seed | `openid`, `email`, `https://www.googleapis.com/auth/youtube.readonly` | Channel title/id, public branding metadata |

### Data Handling Rules

- XR7 stores only **non-sensitive profile metadata** for intake prefill.
- OAuth tokens are used for **prefill only**, not for direct royalty settlement ingestion.
- Token retention is minimized; refresh is only used when user explicitly reconnects.
- Artists can revoke or disconnect at any time.

### Manual Entry Fallback

If OAuth is skipped or unavailable, artists can use manual entry with the same onboarding outcome.

```text
Manual mode fields: legal name, stage name(s), email, optional IPI/PRO hints, country
```

## Artist Identity Auto-Matching

XR7 auto-matches artist identity footprints across ingestion and public metadata sources to reduce setup friction and improve anomaly precision.

### Matching Dimensions

- Artist/stage name variants (normalized and phonetic)
- PRO writer identifiers (IPI/CAE where present)
- Distributor account aliases
- ISRC / ISWC / UPC crosswalk links

### Confidence and User Confirmation

| Confidence Band | Behavior |
|---|---|
| `>= 0.90` | Auto-accept with audit log entry |
| `0.70 - 0.89` | Soft-confirm prompt in onboarding/dashboard |
| `< 0.70` | Requires artist confirmation before linkage |

```json
{
  "candidate": "UMG Distribution - Artist Alias",
  "match_type": "distributor_account",
  "confidence": 0.82,
  "status": "needs_confirmation"
}
```

## Zero-Friction Mobile Onboarding

XR7 onboarding is mobile-first for artist and manager workflows.

### Mobile Capabilities

- **One-thumb upload flow** for statements and exports
- **Camera-based scan path** for PDF/image uploads with OCR fallback
- **Auto-cropping and orientation correction** before extraction
- **Mobile UGC alerts** for newly discovered opportunities
- **Offline-safe upload retries** with resumable background retry when connection returns

### Mobile Retry Behavior

```text
Upload queued -> connection drops -> local retry ticket created -> auto retry on reconnect -> final server receipt
```

## Instant Value Delivery

Artists should see value before full ingestion is complete.

### First 5 Minutes Experience

1. XR7 computes a **baseline earnings estimate** from available profile + benchmark priors.
2. Dashboard shows **predicted leakage bands** while ingestion finishes.
3. FirstClaimFastTrackAgent prepares a **first-claim draft candidate**.
4. Artist receives clear next-step guidance with confidence labels.

### Example Early Dashboard Signals

```json
{
  "estimated_leakage_pre_ingestion": 3200.0,
  "confidence_band": "medium",
  "fast_track_claim": {
    "status": "drafted",
    "reason": "high recoverable + low friction + urgent SOL"
  }
}
```

## Artist Trust & Transparency Layer

XR7 is designed so artists always understand what happened, why it happened, and what action is next.

### Transparency Guarantees

- **Plain-language anomaly explanations** in dashboard and support surfaces
- **Human-readable evidence summaries** alongside technical packet artifacts
- **ArtistComfortAgent messaging** for each onboarding/recovery stage
- **Decision override controls** for artist/manager where policy allows
- **No irreversible or financial action without explicit approval**

### Approval Model

| Action Type | Autonomous | Explicit Approval Required |
|---|---|---|
| Read-only recommendations | Yes | No |
| Draft generation | Yes | No |
| Claim submission | Conditional | Yes |
| Payment charge/disbursement initiation | No | Yes |


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
- **15-Format Statement Ingestion + Generic Fallback**: Explicit parsers for DistroKid, TuneCore, CD Baby, Amuse, United Masters, ONErpm, Stem, LANDR, Ditto, ReverbNation, Bandcamp, ASCAP, BMI, Spotify, SoundCloud, plus generic statement detection.
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

Additional architecture assets:

```
xr7_common/                 # shared settings/logging/schemas package
alembic/                    # migration environment and versions
openapi/openapi.json        # generated OpenAPI output
scripts/export_openapi.py   # OpenAPI export utility
scripts/seed_data.py        # local/dev seed data utility
docker-compose.yml          # app + postgres + redis + celery + minio
Makefile                    # standard build/run/test/migrate targets
```

Universal schema implementation:
- Pydantic schemas: `xr7_common/schemas/universal.py`
- SQLAlchemy tables: `XR7/models/universal_royalty_event.py`, `XR7/models/catalog_graph.py`
- Alembic baseline migration: `alembic/versions/20260314_0001_onboarding_architecture.py`
- Alembic enum/signature follow-up migration: `alembic/versions/20260314_0002_enum_consistency_and_plugin_signature.py`
- JSON examples: `docs/examples/universal_royalty_event.json`, `docs/examples/catalog_graph.json`

Background jobs and storage integration:
- Celery app: `XR7/celery_app.py`
- Sync job tasks: `XR7/tasks/sync_jobs.py`
- Retry orchestration helpers: `XR7/ingestion/sync_jobs.py`
- MinIO/S3 storage service: `XR7/services/storage_service.py`

Celery beat schedule:
- `xr7.sync_jobs.requeue_due` is scheduled every `XR7_SYNC_REQUEUE_SECONDS` seconds (minimum 15 seconds) to requeue due retry jobs.

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
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` — enable live Spotify OAuth exchange/refresh in connector layer
- `YOUTUBE_OAUTH_CLIENT_ID`, `YOUTUBE_OAUTH_CLIENT_SECRET` — enable live YouTube OAuth exchange/refresh
- `TIKTOK_CLIENT_KEY`, `TIKTOK_CLIENT_SECRET` — enable live TikTok OAuth exchange/refresh
- `REDIS_URL` — Redis URL for queue/cache infrastructure
- `CELERY_BROKER_URL` — Celery broker URL
- `CELERY_RESULT_BACKEND` — Celery result backend URL
- `XR7_SYNC_QUEUE_MODE` — preferred retry queue backend (`celery`, `background`, `inline`)
- `XR7_SYNC_REQUEUE_SECONDS` — cadence for scheduled retry requeue scanning
- `S3_ENDPOINT_URL`, `S3_REGION`, `S3_BUCKET`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_USE_SSL` — MinIO/S3 object storage configuration
- `XR7_PLUGIN_ALLOWED_PREFIXES` — allowed module prefixes for plugin entrypoints
- `XR7_PLUGIN_BLOCKED_PREFIXES` — blocked module prefixes for plugin entrypoints
- `XR7_PLUGIN_SIGNATURE_SECRET` — optional HMAC secret to require/verify parser plugin signatures

See `.env.example` for the full list including connector API key variable names.

Production scaffold included in this repository:
- `docker-compose.yml` (FastAPI + PostgreSQL + Redis + Celery worker/beat + MinIO)
- `Makefile` (`make run`, `make test`, `make migrate-up`, `make openapi`, `make seed`)
- `alembic/` + `alembic.ini` for migrations
- `xr7_common/` shared library for settings, logging, and universal schemas
- `openapi/openapi.json` generated OpenAPI artifact

### Running the API

```bash
uvicorn XR7.api.app:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Running Tests

```bash
pytest tests/ -v
```

## Local Development Quickstart (End-to-End)

Goal: go from zero to seeded local environment in under 15 minutes.

### Bring Up Stack

```bash
docker compose up -d --build
docker compose ps
```

Expected healthy shape:

| Service | Expected State |
|---|---|
| `api` | healthy / running |
| `postgres` | healthy / accepting connections |
| `redis` | healthy / ready |
| `celery-worker` | running |
| `celery-beat` | running |
| `minio` | healthy / ready |

### Seed Data

```bash
make seed
```

Seed creates representative demo data: artist, statements, anomalies, claims, invoice/billing rows, activity feed entries.

### First Meaningful Endpoint

```bash
curl "http://localhost:8000/artists/{seeded_artist_id}/dashboard"
```

### Common Local Failures and Fixes

| Symptom | Likely Cause | Fix |
|---|---|---|
| Port bind failure | Local service already on `5432/6379/9000/8000` | Stop conflicting process or remap ports in compose |
| API boots but jobs stall | Redis not ready when worker starts | Restart worker after Redis healthy |
| Celery tasks not picked up | Wrong broker URL/env mismatch | Verify `REDIS_URL`, `CELERY_BROKER_URL`, restart worker/beat |

### Full Test Suite + Coverage

```bash
pytest tests/ -v --maxfail=1 --disable-warnings
pytest --cov=XR7 --cov-report=term-missing
```

Coverage interpretation:
- prioritize low-coverage business-critical modules (`recovery`, `billing`, `celero`, `anomaly`, `ingestion`)
- enforce thresholds in CI (see Integration Test Harness section)

### Debugging FastAPI + Celery Together

- VS Code: two launch configs, one for `uvicorn`, one for `celery worker`.
- PyCharm: compound run configuration (`API + Worker`) with shared `.env`.

## Database Schema & Migration Guide

Detailed reference: `docs/database_schema_and_migrations.md`

### Generate, Apply, Roll Back

```bash
make migrate-new MSG="add payer breakdown indexes"
make migrate-up
make migrate-down
alembic history --verbose
```

### Canonical Relationship Chain

```text
Artist -> Statement -> AnomalyEvent -> Claim -> EvidencePacket -> CeleroTransaction -> Invoice
```

### Immutability Rules

| Table/Entity | Mutability | Why |
|---|---|---|
| Evidence anchors / chain hashes | Append-only | Legal integrity + provenance |
| Admin/audit logs | Append-only | Compliance and forensic replay |
| Lineage events | Append-only | End-to-end traceability |

### High-Volume Indexing Notes

- `anomalies(artist_id, status, created_at)`
- `claims(artist_id, status, updated_at)`
- `activity_feed(artist_id, timestamp)`
- `universal_royalty_events(artist_id, source_name, ingested_at)`

### Universal vs Distributor-Specific Rows

`universal_royalty_event` is the normalized canonical layer. Distributor-specific rows map into universal rows via parser metadata + source references.

## Statement Upload — Deep Dive

Catalog reference: `docs/ingestion_format_catalog.md`

### Explicit Formats

XR7 supports 15 explicit formats plus generic fallback. Use machine-readable catalog:

```http
GET /ingestion/supported-formats
```

### Generic Fallback Behavior

If no explicit parser matches, XR7 applies generic schema detection using date/source/amount/quantity signals and still runs anomaly detection with reduced confidence.

### Duplicate Detection

Duplicate heuristic uses statement identity hash over source, period, row signature, and normalized totals.

| Duplicate Outcome | Behavior |
|---|---|
| Exact duplicate | Reject ingest, return duplicate reference |
| Partial overlap | Ingest delta rows only |
| Conflict | Queue analyst review |

### Upload Constraints

- File size limits: environment-configurable
- Row count limits: environment-configurable guardrails
- Encodings: UTF-8 preferred; fallback detection enabled

### Response Shape (Before/After Detection)

```json
{
  "statement_id": "st_123",
  "ingestion_status": "accepted",
  "anomaly_status": "processing",
  "next_poll": "/artists/{id}/statements/st_123"
}
```

```json
{
  "statement_id": "st_123",
  "ingestion_status": "complete",
  "anomaly_status": "complete",
  "anomalies_detected": 12
}
```

### SmartUploadFixerAgent Behavior

- Repairs malformed delimiters/headers/date formats
- Logs repair plan and confidence
- Emits explicit failure report when unable to repair deterministically

## Anomaly Detection Rule Engine — Full Catalog

Full catalog: `docs/anomaly_rule_catalog.md`

### Rule Catalog Contract

| Field | Description |
|---|---|
| `rule_id` | Stable identifier |
| `category` | Royalty/touring/sync/etc. |
| `subtype` | Specific anomaly class |
| `severity_default` | LOW/MEDIUM/HIGH/CRITICAL |
| `recoverable_formula_default` | Baseline estimation expression |

### Rule Combination and Weighting

When multiple rules fire on same row:
- weighted aggregation computes final anomaly score
- highest severity contributes to escalation threshold
- duplicate semantic rules are deduplicated before claim drafting

### False-Positive Suppression

Artist-scoped suppression allows disabling one rule for one artist without global disable.

### Custom Rule Onboarding

1. Implement rule contract
2. Register in rule registry
3. Add unit + integration fixture
4. Validate expected recoverable and severity outputs

### Isolation Forest Interaction

Isolation Forest **supplements** rules and adds model score; it does not silently override deterministic rule findings.

## Claims Lifecycle — State Machine Reference

Reference flow and triggers: `docs/claims_state_machine.md`

```text
IDENTIFIED -> VALIDATED -> IN_DISPUTE -> NEGOTIATING -> ACCEPTED -> PAID -> CLOSED
                     \-> REJECTED
                     \-> WITHDRAWN
                     \-> ESCALATED
```

### Transition Authorities

| Transition Type | Trigger |
|---|---|
| Manual advance | Analyst/authorized role |
| Webhook-driven | Celero event handlers |
| Agent-driven | Orchestrator node action |
| Queue-approved | Review queue decision |

### Approval Boundaries

- High-risk transitions require analyst queue approval.
- Administrative closures require explicit role checks.

### Required Fields by State

| State | Required Fields |
|---|---|
| IDENTIFIED | anomaly link, estimated recoverable |
| NEGOTIATING | evidence packet, counterparty context |
| ACCEPTED | settlement metadata |
| PAID | recovered amount, transaction references |
| CLOSED | reconciliation + ledger linkage |

Evidence packet version increments at major lifecycle checkpoints. ESCALATED claims are routed with attorney role visibility.

## ML Model Cards

Model cards index: `docs/ml_model_cards.md`

Covered models:
- Isolation Forest anomaly detector
- Earnings forecaster
- Catalog scorer
- Rate benchmarker

Each model card includes:
- training data windows and labels
- features + preprocessing
- benchmark metrics and baselines
- failure modes / OOD warnings
- retraining and fine-tuning path via feedback endpoints
- calibration impact via beta posterior blend

## Celero Integration — Failure Handling Playbook

Playbook: `docs/celero_failure_playbook.md`

### Failure Scenarios

| Scenario | Default Behavior |
|---|---|
| Charge declined | Keep claim payable state, queue retry/analyst path |
| Disbursement failed | Mark txn failed, queue retry and notify artist |
| Stuck non-terminal transaction | Reconciliation task + operator intervention path |

### Refund vs Void

- **Void**: pre-settlement reversal window
- **Refund**: post-settlement reversal

### Sandbox vs Production

Sandbox can produce deterministic simulated events not always matching live processor timing.

## Statute of Limitations — Jurisdiction Reference

Reference: `docs/sol_jurisdiction_reference.md`

Modeled jurisdictions include US federal + state baselines, UK, EU baseline, Canada baseline, Australia baseline.

If jurisdiction is ambiguous, XR7 applies conservative default SOL window by anomaly category and marks confidence.

Attorneys can override classification for a specific anomaly with audit logging.

**Disclaimer:** SOL outputs are operational guidance, not legal advice.

## Authentication & Authorization

### Auth Model Overview

XR7 uses header-based role access for operator and scoped routes plus endpoint-specific flows.

| Header | Purpose | Typical Route Groups |
|---|---|---|
| `X-Admin-Key` | Admin console authentication | `/admin/*`, widget lead admin views |
| `X-Analyst-Email` (+ analyst key) | Analyst attribution and review ownership | `/review-queue/*` |
| `X-Actor-Email` | Artist/team member scoping | expansion + support + artist-scoped protected routes |
| `X-Actor-Role` | Optional role assertion | validated against team membership |

### Header Issuance and Rotation

- Admin and analyst secrets are issued by operator secrets manager.
- Rotation cadence: at least every 90 days or immediately on exposure.
- Audit all header-based admin/analyst actions in immutable logs.

### Widget OTP Token Expiry and Refresh

- OTP verification emits short-lived estimate session token.
- Expired token requires re-verify path; no silent extension.
- Lockout policy applies after repeated failed attempts.

## Error Codes & Error Handling Reference

### Standard Error Contract

```json
{
  "status_code": 400,
  "error_code": "TERMS_NOT_ACCEPTED",
  "message": "Artist must accept current terms before statement upload.",
  "trace_id": "req_abc123"
}
```

### Domain Error Codes

| Error Code | Meaning | Retryable |
|---|---|---|
| `TERMS_NOT_ACCEPTED` | Terms gate not satisfied | No |
| `SOL_EXPIRED` | Claim window expired | No |
| `CELERO_VAULT_NOT_FOUND` | Missing Celero vault profile | No (until registration complete) |
| `ANOMALY_DETECTION_FAILED` | Detection pipeline failed | Yes |
| `WEBHOOK_SIGNATURE_INVALID` | Signature verification failed | No |

### Retry Guidance

- Retryable: transient upstream, queue, timeout, or background processing errors
- Non-retryable: validation, permission, legal-state failures

### Background Task Error Surfacing

Long-running Celery flows expose status via job/activity endpoints and reflected dashboard signals.

## Pagination, Filtering & Sorting

### Standard Query Contract

- `page`, `page_size`
- `cursor`
- `sort_by`, `sort_dir`
- `filter_*`

### Response Envelope

```json
{
  "total": 230,
  "page": 2,
  "page_size": 25,
  "next_cursor": "2026-03-16T11:00:00Z",
  "items": []
}
```

### Pagination Mode Guidance

| Endpoint Class | Mode |
|---|---|
| Activity/history feeds | Cursor preferred |
| Bounded admin lists | Offset/page |
| Large event logs | Cursor required |

## Rate Limiting & Throttling

### Rate Tier Defaults

| Tier | Intended Surface |
|---|---|
| Widget funnel | strict anti-abuse limits |
| Artist-scoped | moderate |
| Analyst/admin | higher trusted quotas |

### OTP Lockout Rules

- failed-attempt thresholds trigger temporary lockout
- escalating lock windows on repeated abuse

### Rate Headers

On throttled or tracked responses:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `Retry-After`

## API Versioning Strategy

Current versioning: URL namespace and OpenAPI contract version (`v1` route strategy for external consumers where enabled).

### Change Classification

| Change Type | Classification |
|---|---|
| Add optional field | Non-breaking |
| Add endpoint | Non-breaking |
| Remove/rename required field | Breaking |
| Semantic behavior contract change | Breaking |

Deprecation notices are announced with migration guidance and sunset timeline.

## Webhook Reliability & Idempotency

### Idempotency for Transactional POST Operations

Use idempotency keys for claim-impacting financial actions to avoid duplicate side effects.

### Duplicate Delivery Handling

- Celero webhook retries are expected
- XR7 deduplicates by event signature + event key + transaction identity

### Ordering Guarantees

Webhooks are treated as potentially out-of-order. XR7 applies state machine guards before transitions.

### HMAC-SHA256 Verification Example

```python
import hmac
import hashlib

def verify(signature_header: str, body: bytes, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature_header, expected)
```

## Observability & Monitoring Stack

Reference: `docs/observability_monitoring_stack.md`

### Structured Logging Fields

- `request_id`
- `artist_id`
- `claim_id`
- `duration_ms`
- `level`

### Recommended Metrics

- claim lifecycle transition counts
- anomaly detection latency
- Celero transaction success/failure rates
- ML inference latency

### Tracing Strategy

OpenTelemetry spans should cover ingestion pipeline stages and agent orchestra steps.

### Alerting Recommendations

- SOL breach risk spikes
- Celery queue depth and retry storms
- failed or stuck disbursements

## Data Retention, Privacy & Compliance

Privacy reference: `docs/data_retention_privacy_compliance.md`

### PII Scope

Stored PII includes artist contact profile and Celero vault references (tokenized references, not raw card data).

### Retention Policy Matrix

| Entity | Retention Baseline |
|---|---|
| Statements | contractual + audit window |
| Anomalies/claims | lifecycle + legal window |
| Evidence packets | immutable legal retention |
| Audit logs | compliance retention policy |

### Erasure Handling

Right-to-erasure applies to erasable PII, while immutable evidence/ledger records remain retained where legally required.

See also: **Regulatory Compliance Matrix**.

## Disaster Recovery & Backup Strategy

Reference: `docs/disaster_recovery_backup_strategy.md`

### Backup Cadence

- PostgreSQL: scheduled backups + PITR-ready WAL strategy
- Object storage: replication and versioned backups for evidence artifacts
- Redis: persistence mode selected for queue durability requirements

### Recovery Targets

- define and monitor `RTO` and `RPO` per environment tier
- run failover simulation drills on schedule

## White-Label Deployment Guide

Reference: `docs/white_label_deployment_guide.md`

### Tenant Branding Controls

| Setting | Purpose |
|---|---|
| Logo URL | Brand display |
| Color scheme | UI theming |
| Tenant domain | Branded entrypoint |

### Readiness Gate

`white_label` readiness flag indicates whether tenant-aware configuration is active and validated.

### B2B Onboarding Surface

- `GET /b2b/portfolio/{org_id}`
- `GET /partnerships/targets`

## Multi-Tenancy & White-Label Isolation Model

Isolation reference: `docs/multi_tenancy_isolation_model.md`

- tenant ID propagates through artist-scoped entities
- strict application-level scoping (and DB-level controls where configured)
- public aggregate stats use privacy-safe rollups only

Contract termination flow includes tenant export, retention policy enforcement, and scoped purge workflow.

## LangGraph Agent Orchestra — Developer Operations

Developer ops reference: `docs/langgraph_agent_devops.md`

### Inspecting Runs

- Use trace URLs from dashboard `agent_orchestra_status`
- query checkpointer namespace by artist/thread identifiers

### Replay from Checkpoint

Recover failed runs by restoring checkpoint state and replaying deterministic nodes.

### Adding a New Node

1. Implement node interface contract
2. Emit confidence + trace events
3. Wire node in orchestra supervisor routing
4. Add tests for success/fallback/reflection paths

### Dry-Run Mode

Use simulation/no-side-effect mode for validating orchestration transitions.

## AI & Agent Governance Framework

Governance reference: `docs/ai_agent_governance_framework.md`

### Decision Authority Matrix

| Action | Autonomous | Human Approval |
|---|---|---|
| Recommendations/explanations | Yes | No |
| Draft generation | Yes | No |
| Financial/destructive actions | No | Yes |

### Governance Controls

- override and rollback pathways
- action audit schema (state hashes, confidence, trace URL)
- fairness monitoring and drift alarms
- explainability outputs for prioritization decisions
- agent graph versioning and rollback support

## SDK Usage Examples

SDK generation:

```bash
make sdks
```

### Python SDK Example

```python
from xr7_sdk import XR7Client

client = XR7Client(base_url="http://localhost:8000")
artist_id = "artist_123"

client.artists.accept_terms(artist_id)
client.statements.upload(artist_id, "statement.csv")
anomalies = client.anomalies.list(artist_id)
claim = client.claims.advance(claim_id="claim_abc")
```

### TypeScript SDK Example

```ts
import { XR7Client } from "@xr7/sdk";

const client = new XR7Client({ baseUrl: "http://localhost:8000" });
const artistId = "artist_123";

await client.terms.accept(artistId);
await client.statements.upload(artistId, file);
const anomalies = await client.anomalies.list(artistId);
await client.claims.advance("claim_abc");
```

Generated SDKs provide base API parity; hand-maintained layers add opinionated helpers.

## OpenAPI Specification — Maintenance & Extension Guide

Reference: `docs/openapi_maintenance_guide.md`

### Regenerate Spec

```bash
make openapi
```

### Route Doc Conventions

Document request/response examples in route decorators so they flow into generated spec.

### Security Scheme Declaration

Define per-route security requirements (admin/analyst/actor headers) in OpenAPI metadata.

### CI Validation

Spec diff + schema validation should fail CI on undocumented breaking contract changes.

### Consumer Onboarding

Third-party labels/managers/attorneys should consume OpenAPI for client generation and contract tests.

Postman collection can be generated from OpenAPI and published with SDK artifacts.

## CHANGELOG

Changelog lives in `CHANGELOG.md`.

Initial structure should include:
- universal schema migrations (`20260314_0001`, `20260314_0002`)
- LangGraph orchestra rollout
- expansion endpoints release
- evidence packet `v1.1` with RSA signing support

## Production Deployment Guide (Beyond Docker Compose)

Deployment reference: `docs/production_deployment_guide.md`

### Kubernetes Component Mapping

| Component | Recommended Workload Type |
|---|---|
| FastAPI API | Deployment |
| Celery workers | Deployment |
| Celery beat | Singleton Deployment |
| Redis | StatefulSet |
| PostgreSQL | Managed DB or StatefulSet |
| MinIO | StatefulSet |
| Migration step | Job |

### Cloud Reference Paths

- AWS: ECS Fargate + RDS + ElastiCache + S3
- GCP: Cloud Run + Cloud SQL + Memorystore + GCS
- Azure: Container Apps + Azure Database + Azure Cache + Blob

### Zero-Downtime Release Sequence

1. Run pre-deploy migration job
2. Deploy backward-compatible app build
3. Shift traffic gradually
4. Validate readiness and smoke checks

### Secrets Management

Use provider secret stores or Vault for `CELERO_SECURITY_KEY` and RSA private keys.

### Horizontal Scaling Rules

- API and worker pools scale horizontally
- Celery beat remains singleton

### CDN/Static Assets

Serve `/dashboard/ui` and `/widget` static assets behind CDN with cache-control strategy.

## CI/CD Pipeline Reference

Pipeline reference: `docs/cicd_pipeline_reference.md`

### Recommended GitHub Actions Stages

`lint -> type-check -> unit -> integration -> openapi -> sdk -> build -> staging -> smoke -> production`

### Migration in Pipeline

Use pre-deploy migration job gate before app rollout.

### Required Merge Checks

- tests passing
- coverage threshold
- contract/spec checks
- security scanning gates

### SDK Publishing

Version and publish generated SDKs to PyPI/npm/internal registry according to release policy.

### Security Gates

- secret age/rotation checks
- image signing + vulnerability scan (Trivy/Snyk)
- agent topology snapshot validation for orchestration integrity

## Feature Flags & Configuration Management

Flags reference: `docs/feature_flags_configuration.md`

### Flag Strategy

- env-based baseline + optional LaunchDarkly/Flagsmith integration
- kill switches for ML inference, agent orchestra, Celero live mode
- tenant-scoped flags for white-label rollouts

### Safe Rollout Pattern

Roll out new anomaly rules to small artist cohort before global enable.

### Flag Audit Trail

Track who changed flag, when, prior/new values, and observed downstream effects.

## Billing & Contingency Fee Model — Complete Reference

Reference: `docs/billing_contingency_fee_model.md`

Contingency fee is **10%** of gross recovered amount.

### Calculation

```text
fee = gross_recovered * 0.10
net_disbursed = gross_recovered - fee
```

### Worked Example

| Gross | Fee (10%) | Net |
|---:|---:|---:|
| 45,000.00 | 4,500.00 | 40,500.00 |

### Partial Recovery Handling

Fee and net are prorated per installment.

### Invoice Lifecycle

- invoice generated on paid settlement events
- disputes route to analyst queue
- due dates and status exposed on invoice endpoints

### Tax and Revenue Recognition

Celero (MoR) handles tax processing; XR7 recognizes fee revenue per configured accounting policy after settlement conditions.

### White-Label Variable Fees

Tenant-level fee configuration may be enabled by contract policy.

## Data Lineage & Provenance Tracking

Lineage reference: `docs/data_lineage_provenance_tracking.md`

### Provenance Guarantees

- Universal rows link to source statement, parser version, and ingestion timestamp
- anomalies reference exact source events/rules
- claims link to anomaly set + evidence packet chain data
- agent actions emit lineage events with trace IDs

### Lineage Query Surface

```http
GET /artists/{id}/lineage/{entity_type}/{entity_id}
GET /admin/lineage/audit?artist_id=...&date_range=...
```

Lineage summaries are embedded in exported evidence manifests.

## Regulatory Compliance Matrix

| Regulation | Applicability to XR7 | Current Status / Implementation | Gaps / Next Steps |
|---|---|---|---|
| PCI DSS | XR7 avoids raw card handling; Celero vault integration | Out of direct card-data scope by architecture | Maintain integration controls and annual assessment |
| GDPR | Artist profile and account metadata may be personal data | Data subject workflows and retention policies implemented at platform level | Expand jurisdiction-specific workflows |
| CCPA / CPRA | California artist data may qualify | Service-provider style processing posture | Improve self-service DSAR tooling |
| SOC 2 (Security/Availability/Confidentiality) | Applicable for enterprise sales | Logging, access controls, backup/recovery controls in place | Formal audit readiness program |
| MMA / MLC obligations | Relevant for rights/royalty processing context | MLC-related ingestion and lineage support in architecture | Formal policy mappings and controls evidence |
| State royalty transparency laws | Relevant for claim evidence and reporting | Evidence packet and reconciliation exports available | Jurisdiction-specific legal review updates |
| Money transmitter / payment facilitator status | Celero is MoR and payment processor | XR7 does not directly custody payments by design | Continue legal review for new geographies |
| DMCA safe harbor for UGC workflows | Relevant for UGC claim automation | UGC workflows include traceability and policy checks | Add policy-tier controls per platform contract |

**This matrix is not legal advice; consult qualified counsel.**

## Security Threat Model

Threat model reference: `docs/security_threat_model.md`

### Sensitive Asset Inventory

- artist PII
- vault reference identifiers
- evidence packets + chain hashes
- ML calibration and outcome data

### Trust Boundaries

- XR7 application/data plane
- Celero payment domain
- artist-controlled account sources and uploads

### Key Threat Scenarios and Mitigations

| Threat | Mitigation |
|---|---|
| Unauthorized claim manipulation | role-scoped auth + immutable audit logs |
| Evidence packet tampering | chain hash + signature verification |
| Analyst impersonation | header key controls + actor audit |
| Plugin injection | allowlist/blocklist + optional signature secret |
| Celery task spoofing | broker isolation + signed/internal task controls |

Accepted risks should be documented with compensating controls and review cadence.

Responsible disclosure contact should be published in security policy docs.

## Performance & Scalability Benchmarks

Benchmarks reference: `docs/performance_scalability_benchmarks.md`

### Target SLO Bands

| Operation | p50 | p95 | p99 |
|---|---:|---:|---:|
| Dashboard load | <= 300ms | <= 900ms | <= 1500ms |
| Statement upload accept | <= 500ms | <= 1500ms | <= 2500ms |
| Evidence export start | <= 700ms | <= 2000ms | <= 3500ms |

### Capacity Guidance

- tune worker concurrency per queue type (ML inference vs sync vs digest)
- size DB connection pools relative to worker concurrency
- load-test against statement/anomaly/claim volume targets before release

Known bottlenecks and mitigations are tracked in roadmap backlog.

## Incident Response Runbook Index

Runbook index reference: `docs/incident_response_runbook_index.md`

Runbook stubs:
- failed disbursement recovery
- compromised signing key rotation
- corrupt evidence packet investigation
- celery backlog emergency drain
- database connection exhaustion recovery
- GDPR/CCPA erasure request handling
- false-positive mass suppression workflow

## Support, SLAs & Escalation Paths

Support reference: `docs/support_slas_escalation_paths.md`

### Support Tiers

| Tier | Coverage |
|---|---|
| Self-serve | docs + guides |
| Standard | email SLA |
| Premium | dedicated analyst |
| Enterprise white-label | dedicated CSM + escalation path |

### Escalation Paths

- in-product escalation for stalled claims
- support ticket escalation
- attorney referral path where policy allows

Support outcomes feed calibration and agent training datasets.

## Integration Test Harness & Contract Testing Guide

Testing reference: `docs/integration_test_harness_guide.md`

### Run Modes

- live local stack integration tests
- mocked external services for deterministic CI

### Full Flow Fixtures

Ingestion -> anomaly -> claim -> evidence -> Celero event handling

### Adding Distributor Format Tests

1. Add sample input file fixture
2. Add expected normalized rows
3. Assert expected anomaly outcomes

### LangGraph Flow Testing

Inject checkpoint state fixtures and validate node transitions and confidence behavior.

### Coverage Enforcement

Coverage thresholds should fail CI when below policy baseline.

## Dependency Management & Supply Chain Security

Supply chain reference: `docs/dependency_supply_chain_security.md`

### Dependency Hygiene

- pinned Python dependencies with review cadence
- automated vulnerability alerts (Dependabot/Snyk/Safety)
- controlled major version upgrade sequences

### Plugin Entrypoint Security

`XR7_PLUGIN_ALLOWED_PREFIXES` and `XR7_PLUGIN_SIGNATURE_SECRET` reduce plugin injection risk.

### Container and SBOM

- base image update cadence + CVE response SLA
- generate and publish SBOM for released images

## Internationalization & Multi-Currency Reference

Reference: `docs/internationalization_multi_currency.md`

### Currency and FX Handling

- store source currency and normalized values
- define exchange-rate source and timestamp policy (ingest-time or display-time)

### Tax/Withholding Estimates

`POST /artists/{id}/intelligence/withholding-estimate` models supported country pairs and assumptions.

### Locale and Encoding

- Unicode-safe parser handling for artist/track metadata
- date normalization across multiple source formats
- locale-aware exports for reports/PDF artifacts

## Partner & Distributor Integration Onboarding Guide

Reference: `docs/partner_distributor_integration_guide.md`

### Partner Tiers

| Tier | Description |
|---|---|
| Data partner | file export agreement |
| API partner | direct connector integration |
| White-label partner | tenant deployment |

### New Distributor Format Checklist

- sample files
- column specification
- parser registration ID
- validation fixtures

### New PRO Connector Checklist

- env var contract
- connector interface implementation
- readiness registration

Partnership visibility endpoint:

```http
GET /partnerships/targets
```

## Artist-Facing UX Flow Documentation

UX reference: `docs/artist_facing_ux_flow.md`

### Complete Artist Journey

```text
Discovery -> Widget Funnel -> Onboarding -> First Upload -> First Anomaly -> First Claim -> First Deposit
```

### Widget Funnel Screens & States

- register
- OTP verify
- estimate results
- claim submission + confirmation

Include error and success states with confidence-building copy.

### Dashboard States

- Empty
- Processing
- Active claims
- Success (deposit received)
- Includes **Payers Owing** priority card

### Agent Comfort Messaging

> WelcomeSummaryAgent: "You are fully onboarded. We found 3 immediate opportunities worth reviewing first."

> ArtistComfortAgent: "No action is required right now; we are monitoring payer responses and deadlines for you."

### Mobile and Accessibility

- prioritize high-signal cards on small screens
- maintain WCAG 2.1 AA targets for widget/dashboard surfaces

Screenshot placeholders:

![Widget Register Screen](docs/screenshots/widget-register.png)
![Widget OTP Verify Screen](docs/screenshots/widget-otp-verify.png)
![Dashboard Active Claims Screen](docs/screenshots/dashboard-active-claims.png)

## Demo Environment & Sales Engineering Guide

Reference: `docs/demo_environment_sales_guide.md`

### Demo Stack

Use seeded demo environment with multi-format statements, active lifecycle claims, and one completed deposit.

### 10-Minute Demo Script

1. Dashboard overview
2. Anomaly detail
3. Claim advance
4. Evidence export
5. Celero transaction status

### Reset Between Demos

Use seed reset workflow to return to known state.

### MFA-Friendly Demo Mode

Widget demo mode supports OTP simulation path for non-production demos.

## Competitive Positioning & Differentiation Summary

Reference: `docs/competitive_positioning_summary.md`

XR7 differentiation:
- automation scale beyond manual royalty audit firms
- end-to-end recovery workflow beyond accounting-only SaaS tooling
- defensible moat: evidence-chain integrity + calibrated ML prioritization
- contingency fee model lowers adoption friction
- white-label B2B distribution amplifies reach and data quality flywheel

## Roadmap Prioritization Rationale

Reference: `docs/roadmap_prioritization_rationale.md`

### Scoring Criteria

- artist impact
- revenue impact
- partnership dependency
- technical risk
- regulatory urgency

### PMF Leading Indicators

- anomalies per artist per month
- claim conversion rate
- average recovery value
- upload-to-first-deposit cycle time

### 12-Month Milestone Framing

Roadmap phases should map to measurable adoption, recovery yield, and partner expansion targets.

## Regulatory and Legal Posture Notes

- XR7 provides operational tooling, analytics, and workflow orchestration.
- Jurisdiction-specific legal interpretations require qualified counsel.
- Payment and tax handling follows Celero Merchant-of-Record boundaries.

## Glossary

| Term | Definition |
|---|---|
| Leakage | Recoverable earnings discrepancy between expected and paid amounts |
| Anomaly | Detected outlier or rule-triggered discrepancy candidate |
| Claim | Structured recovery action tied to one or more anomalies |
| Evidence Packet | Structured legal/financial proof bundle for a claim |
| Chain Hash | Hash linking packet lineage across revisions |
| Calibration | Alignment between predicted success and actual outcomes |
| Posterior Success Rate | Updated success estimate after incorporating outcomes |
| Expected Utility | Priority score balancing recoverable value, confidence, and effort |
| Recoupment | Contractual recovery by counterparty before artist payout |
| SOL | Statute of limitations window for pursuing recovery |
| PRO | Performing Rights Organization |
| DSP | Digital Service Provider |
| MLC | Mechanical Licensing Collective |
| UGC | User-generated content |
| Vault ID | Tokenized payment/customer reference in Celero |
| Contingency Fee | Recovery fee charged as percentage of gross recovered |
| Universal Royalty Event | Canonical normalized royalty row |
| Catalog Graph | Relationship graph across works, rights, and sources |
| Isolation Forest | Unsupervised anomaly detection model |
| Beta Posterior Blend | Bayesian calibration approach for success probability updates |
| Artist Readiness Score | Operational readiness score for accelerated recovery |
| Comfort Score | Confidence-oriented guidance quality indicator for artist messaging |
| Fast Track Claim | High-confidence, high-ROI claim drafted for immediate action |

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
| GET | `/artists/{id}/workflow/preview` | Preview full XR7 end-to-end orchestration inputs and step plan |
| POST | `/artists/{id}/workflow/run` | Run or queue the full XR7 orchestration workflow |
| POST | `/artists/{id}/sync/jobs/requeue-due` | Requeue due retry sync jobs for execution |
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

### OpenAPI Role Matrix (Expansion)

Security headers used by protected artist-scoped expansion routes:
- `X-Actor-Email` — required once team membership exists for the artist.
- `X-Actor-Role` — optional validation header; when present, must match the role assigned to `X-Actor-Email`.

Bootstrap behavior:
- If no team members exist for an artist, protected routes allow access without role headers.
- First team member creation must use role `artist`.

Protected artist-scoped routes and allowed roles:

| Method | Path | Allowed roles (when team exists) |
|--------|------|-----------------------------------|
| GET | `/artists/{id}/notifications/preferences` | `artist`, `manager`, `attorney` |
| PUT | `/artists/{id}/notifications/preferences` | `artist`, `manager` |
| POST | `/artists/{id}/notifications/dispatch` | `artist`, `manager` |
| POST | `/artists/{id}/notifications/urgent-sol-check` | `artist`, `manager` |
| GET | `/artists/{id}/dashboard/charts` | `artist`, `manager`, `attorney` |
| GET | `/artists/{id}/reports/summary` | `artist`, `manager`, `attorney` |
| POST | `/artists/{id}/connect/oauth-session` | `artist`, `manager` |
| GET | `/artists/{id}/connect/fallbacks` | `artist`, `manager`, `attorney` |
| GET | `/artists/{id}/team/members` | `artist`, `manager`, `attorney` |
| POST | `/artists/{id}/team/members` | `artist` (or bootstrap first member) |
| DELETE | `/artists/{id}/team/members/{member_id}` | `artist` |
| GET | `/artists/{id}/recovery/benchmark-percentiles` | `artist`, `manager`, `attorney` |
| POST | `/artists/{id}/claims/templates` | `artist`, `manager`, `attorney` |
| POST | `/artists/{id}/intelligence/withholding-estimate` | `artist`, `manager`, `attorney` |
| POST | `/artists/{id}/ml/predict-recoverable` | `artist`, `manager`, `attorney` |
| GET | `/artists/{id}/recovery/audit-demand-letter` | `artist`, `manager`, `attorney` |

Public/non-artist-scoped expansion routes (no team headers required):
- `GET /stats/public/recovery`
- `POST /claims/{claim_id}/evidence/anchor`
- `GET /education/guides`
- `GET /education/guides/{guide_id}`
- `GET /b2b/portfolio/{org_id}`
- `GET /partnerships/targets`

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
- **OAuth/API connector layer (unified)**:
`POST /artists/{id}/connect/oauth-session` (create OAuth2 stateful login session with requested scopes),
`POST /artists/{id}/connect/oauth-session/{session_id}/exchange` (validate state + link provider account + persist tokens),
`GET /artists/{id}/connect/accounts` (list linked accounts with provider/tenant filters),
`POST /artists/{id}/connect/accounts/{account_id}/refresh` (refresh access token from stored refresh token),
`DELETE /artists/{id}/connect/accounts/{account_id}` (disconnect linked account)

- **Data fetcher modules (historical statements + catalog + registrations + usage + universal schema normalisation)**:
`POST /artists/{id}/fetchers/distributor`,
`POST /artists/{id}/fetchers/pro`,
`POST /artists/{id}/fetchers/mlc`,
`POST /artists/{id}/fetchers/youtube`,
`POST /artists/{id}/fetchers/social`

Provider fetcher execution mode:
- If provider API base URL + key env vars are configured, fetchers attempt live pulls.
- If not configured, fetchers return deterministic simulated payloads so local/dev pipelines stay testable.

- **Permissions dashboard (backend + UI)**:
`GET /artists/{id}/connect/permissions-dashboard`,
`GET /permissions/ui`

- **File ingestion pipeline (PDF/CSV/XLSX/ZIP + scan/type detection/PDF split/OCR fallback)**:
`POST /artists/{id}/ingestion/upload-any`

Ingestion hardening:
- ClamAV scan is attempted first (configurable with `XR7_USE_CLAMAV`, `CLAMAV_HOST`, `CLAMAV_PORT`), with signature fallback when daemon is unavailable.
- Strict extension-vs-magic validation is enforced by default (`strict_validation=true`), blocking suspicious uploads.

- **Pluggable statement parser engine (distributor/PRO/publisher/MLC -> universal schema)**:
`POST /artists/{id}/parsers/distributor`,
`POST /artists/{id}/parsers/pro`,
`POST /artists/{id}/parsers/publisher`,
`POST /artists/{id}/parsers/mlc`

Parser plugin persistence:
- `PUT /artists/{id}/parsers/plugins` (register/update plugin metadata)
- `GET /artists/{id}/parsers/plugins` (list plugin registrations)

Parser plugin sandbox policy:
- Entry points are restricted to `XR7_PLUGIN_ALLOWED_PREFIXES` and denied when matching `XR7_PLUGIN_BLOCKED_PREFIXES`.
- When `XR7_PLUGIN_SIGNATURE_SECRET` is set, each plugin requires `plugin_signature` and is verified as `HMAC_SHA256(secret, plugin_entrypoint)`.

Async sync jobs with retries + status tracking:
- `POST /artists/{id}/sync/jobs` (enqueue job; optional async execution)
- `GET /artists/{id}/sync/jobs` (list job statuses)
- `GET /artists/{id}/sync/jobs/{job_id}` (single job detail)
- `POST /artists/{id}/sync/jobs/{job_id}/run` (manual run/retry)
- `POST /artists/{id}/sync/jobs/requeue-due` (scan + enqueue due retry jobs)

Queue backend behavior for `POST /artists/{id}/sync/jobs`:
- `queue_backend=inline` runs immediately in the request
- `queue_backend=background` uses FastAPI background tasks
- `queue_backend=celery` enqueues to Celery worker, with safe fallback to background mode if unavailable

- **Missing data detector**:
`GET /artists/{id}/ingestion/missing-data`

- **Catalog graph builder + confirmation + inference**:
`POST /artists/{id}/catalog/graph/build`,
`POST /artists/{id}/catalog/confirm`,
`GET /artists/{id}/catalog/confirm`,
`POST /artists/{id}/catalog/infer`

- **Variance detection engine**:
`POST /artists/{id}/variance/scan`

- **Evidence packet generator (audit packet endpoint)**:
`POST /claims/{claim_id}/evidence/generate-audit`

- **Recovery automation engine**:
`POST /artists/{id}/recovery/automate`

- **Immutable ledger**:
`GET /artists/{id}/ledger/immutable`

- **End-to-end workflow orchestration**:
`GET /artists/{id}/workflow/preview`,
`POST /artists/{id}/workflow/run`

OAuth connector mode behavior:
- If provider OAuth credentials are configured (env vars above), exchange/refresh calls use live provider token endpoints.
- If credentials are not configured, endpoints run in safe simulated mode so local development and tests still work.

Step-to-module mapping (implemented baseline):

- Step 1: OAuth/API Connector Layer -> `connect/oauth-session`, `connect/accounts/*`
- Step 1: Data Fetcher Modules -> `/fetchers/{integration}`
- Step 1: Permissions Dashboard -> `/connect/permissions-dashboard`, `/permissions/ui`
- Step 2: File Ingestion Pipeline -> `/ingestion/upload-any`
- Step 2: Statement Parser Engine -> `/parsers/{parser_type}`
- Step 2: Missing Data Detector -> `/ingestion/missing-data`
- Step 3: Catalog Graph Builder -> `/catalog/graph/build`
- Step 3: Catalog Confirmation UI backend -> `/catalog/confirm`
- Step 3: Auto-Inference Engine -> `/catalog/infer`
- Step 4: Variance Detection Engine -> `/variance/scan`
- Step 4: Evidence Packet Generator -> `/claims/{claim_id}/evidence/generate-audit`
- Step 4: Recovery Automation Engine -> `/recovery/automate`
- Step 4: Immutable Ledger -> `/ledger/immutable`

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
