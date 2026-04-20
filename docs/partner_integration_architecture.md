# XR7 Partner Integration Architecture

**Version:** 1.0
**Date:** 2026-04-09
**Scope:** Technical integration strategy for labels, publishers, PROs, DSPs, MLC, CCLI, foreign societies, and TV/film metadata providers
**Principle:** Every partner integration is idempotent, retry-safe, and independently deployable. A failure in one partner integration never cascades.

---

## Table of Contents

1. [Partner Ecosystem Map](#1-partner-ecosystem-map)
2. [Integration Patterns by Partner Type](#2-integration-patterns-by-partner-type)
3. [Data Contract Requirements](#3-data-contract-requirements)
4. [Authentication & Authorization Patterns](#4-authentication--authorization-patterns)
5. [Webhook & Event-Driven Ingestion](#5-webhook--event-driven-ingestion)
6. [Retry, Reconciliation & Idempotency Rules](#6-retry-reconciliation--idempotency-rules)
7. [Partner Sandbox & Testing Environment](#7-partner-sandbox--testing-environment)
8. [Partner Certification Process](#8-partner-certification-process)
9. [Partner Integration Handbook](#9-partner-integration-handbook)
10. [Partner API Requirements Checklist](#10-partner-api-requirements-checklist)
11. [Partner Onboarding Workflow (n8n-ready)](#11-partner-onboarding-workflow-n8n-ready)

---

## 1. Partner Ecosystem Map

```
                         ┌─────────────────────────────┐
                         │         XR7 Platform         │
                         │  (Rights Intelligence Engine) │
                         └──────────────┬───────────────┘
                                        │
          ┌─────────────────────────────┼─────────────────────────────┐
          │                             │                             │
    ┌─────▼──────┐            ┌─────────▼────────┐         ┌────────▼────────┐
    │  SUPPLY     │            │  RIGHTS ORGS     │         │  METADATA       │
    │  PARTNERS   │            │  (Verification)  │         │  PROVIDERS      │
    │             │            │                  │         │                 │
    │ • Labels    │            │ • PROs           │         │ • MusicBrainz   │
    │ • Publishers│            │ • MLC            │         │ • AllMusic      │
    │ • Distrib.  │            │ • CCLI           │         │ • Discogs       │
    │ • Songwriters│           │ • Foreign socs.  │         │ • TV/Film dbs   │
    └─────────────┘            └──────────────────┘         └─────────────────┘
          │                             │                             │
    ┌─────▼──────┐            ┌─────────▼────────┐
    │   DSPs     │            │  FINANCIAL       │
    │ (Usage)    │            │  PARTNERS        │
    │            │            │                  │
    │ • Spotify  │            │ • Trolley        │
    │ • Apple    │            │ • Stripe         │
    │ • Amazon   │            │ • Banks          │
    │ • YouTube  │            │                  │
    │ • + 14 more│            └──────────────────┘
    └────────────┘
```

---

## 2. Integration Patterns by Partner Type

### 2.1 DSPs (Digital Service Providers)

**Integration type:** Pull (XR7 pulls statements from DSPs)
**Primary method:** SFTP pickup or authenticated REST/GraphQL API
**Data flow direction:** DSP → XR7 (one-way; XR7 does not write back to DSPs except claim submissions)

| DSP | Method | Format | Auth | Frequency |
|-----|--------|--------|------|-----------|
| Spotify | SFTP | CSV (Spotify CRD format) | SSH key pair | Monthly |
| Apple Music | API (Apple Music Reports API) | JSON | OAuth 2.0 (client credentials) | Monthly |
| Amazon Music | SFTP | TSV | SSH key pair | Monthly |
| YouTube Music | API (YouTube Analytics API) | JSON | OAuth 2.0 + service account | Daily |
| Tidal | SFTP | CSV | SSH key pair | Monthly |
| Deezer | API (REST) | JSON | API key (header) | Monthly |
| SoundCloud | API (REST) | JSON | OAuth 2.0 | Monthly |
| Beatport | SFTP | CSV | SSH key pair | Monthly |
| Pandora | SFTP | CSV | Password + IP allowlist | Monthly |
| iHeartRadio | Email attachment (manual) | CSV | N/A (manual) | Monthly |

**Claim submission back to DSPs:**
- Spotify, Apple: API-based claim submission (`POST /royalty-disputes/`)
- Others: Email + PDF bundle (automated generation; manual send via n8n workflow)

---

### 2.2 Labels & Distributors

**Integration type:** Push (labels push catalog + statements to XR7) or Pull (XR7 pulls via label API)
**Data types:** Catalog (works, recordings, splits), historical statements, rights configuration

| Partner type | Integration method | Auth | Data pushed |
|-------------|-------------------|------|-------------|
| Major label (direct) | XR7 Bulk Import API | API key (tenant-scoped) | Catalog, splits, historical statements |
| Distributor (e.g., DistroKid, TuneCore) | Webhook push OR SFTP | Webhook HMAC + IP allowlist | Statement data for all their artists |
| Small label | XR7 UI upload OR API | JWT (sub-tenant) | Catalog, statements manually |
| Music publisher | XR7 Publisher API | API key + IP allowlist | Works, IPI numbers, split sheets |

**Distributor integration model:**

When a distributor integrates with XR7, they become a "source tenant" — their artists are sub-tenants within the distributor's namespace:

```
Distributor: TuneCore
  └── Sub-tenant: Artist A (artist created their TuneCore account)
  └── Sub-tenant: Artist B
  └── Sub-tenant: Artist C

TuneCore pushes all statement data to XR7 via webhook.
Each artist sees only their own data in the XR7 artist portal.
```

---

### 2.3 PROs (Performing Rights Organizations)

**Integration type:** Pull (XR7 downloads statements from PROs)
**Direction:** PRO → XR7 (read-only; XR7 submits claims back via web portal or email for now)

| PRO | Region | Format | Auth | Frequency |
|-----|--------|--------|------|-----------|
| ASCAP | US | CSV (ASCAP-standard) | OAuth 2.0 (ASCAP API) | Quarterly |
| BMI | US | TSV (BMI-proprietary) | API key | Quarterly |
| PRS for Music | UK | DDEX-like XML | OAuth 2.0 | Monthly |
| SOCAN | CA | CSV | API key | Quarterly |
| SESAC | US | JSON (real-time API) | OAuth 2.0 | Real-time push |
| GEMA | DE | XML (GVL variant) | SFTP + password | Quarterly |
| SACEM | FR | CSV | SFTP + SSH key | Quarterly |
| SIAE | IT | CSV | SFTP + password | Quarterly |
| APRA AMCOS | AU/NZ | CSV | SFTP | Quarterly |

---

### 2.4 MLC (Mechanical Licensing Collective)

**Integration type:** Pull + submission
**MLC provides:** Mechanical royalty statements for US streaming
**XR7 submits:** Claim filings for unmatched works

```
XR7 → MLC API: POST /works  (register unmatched works for MLC matching)
MLC → XR7: Webhook push when work matched or royalties assigned
XR7 → MLC API: GET /statements (pull unmatched royalty pools)
```

**MLC-specific requirements:**
- Works must be registered with IPI (Interested Party Information) number
- ISWC required for matching
- Split sheets must sum to exactly 100%
- MLC uses ACH disbursement; XR7 tracks bank verification separately

---

### 2.5 CCLI (Christian Copyright Licensing International)

**Integration type:** Pull
**Scope:** Worship music licensing; XR7 ingests CCLI license reports

```
CCLI SFTP → XR7 ingestion:
  File: license_report_YYYYMM.csv
  Fields: song_title, artist, license_type, license_count, territory, period
  Mapping: CCLI song_id → XR7 work via title+artist fuzzy match (no ISRC)
```

---

### 2.6 Foreign Societies

Each foreign society has its own data model, identifier system, and delivery method. XR7 handles them via the **Society Adapter** pattern:

```
ForeignSocietyAdapterBase:
  - society_code: str          # "BUMA_STEMRA", "JASRAC", "SUISA"
  - identifier_type: str       # "LOCAL_WORK_ID", "ISWC", "ISRC"
  - statement_format: str      # "CSV", "XML", "XLSX"
  - delivery_method: str       # "SFTP", "EMAIL", "API"
  - parse(raw: bytes) → list[StatementRow]
  - map_identifiers(rows) → list[WorkMatch]
```

Key foreign societies supported:

| Society | Country | Identifier used | Notes |
|---------|---------|----------------|-------|
| BUMA/STEMRA | NL | Dutch work number | Monthly XML |
| JASRAC | JP | J-WID number | Quarterly; requires Japanese locale handling |
| SUISA | CH | SUISA work ID | Quarterly; EUR + CHF payment |
| IMRO | IE | IPI-based | Quarterly |
| ABRAMUS | BR | ECAD work number | Semi-annual |
| SAMRO | ZA | SAMRO catalog ID | Quarterly |

---

### 2.7 TV/Film Metadata Providers (Cue Sheet Sources)

**Integration type:** Pull + contribution
**Purpose:** Match music used in TV/film to Works in XR7 for sync + performance royalty recovery

| Source | Data type | XR7 use |
|--------|----------|---------|
| IMDB Pro (API) | Show/film metadata | Enrich cue sheet records with production info |
| Music Reports (NMPA) | Cue sheet database | Pull cue sheets to identify sync earnings |
| SLMC (Songfile) | HFA mechanical licenses | Cross-reference with MLC data |
| Gracenote / TiVo | Audio recognition + content ID | Fingerprint matching for TV broadcast |

---

## 3. Data Contract Requirements

### 3.1 Core Data Contracts

#### Work Contract

All partners supplying work (composition) data must provide:

```json
{
  "iswc": "T-034524680-1",                    // Preferred; null if unknown
  "work_title": "Shape of You",               // Required
  "work_title_normalized": null,              // XR7 computes this if null
  "language": "en",
  "parties": [
    {
      "role": "Composer",                     // Composer | Lyricist | Publisher | Admin
      "ipi": "00084466",
      "name": "Ed Sheeran",
      "share": 0.3333,                        // Must sum to 1.0 across all parties
      "society": "PRS"
    }
  ],
  "society_codes": {
    "ascap": null,
    "bmi": null,
    "prs": "TP0035246"
  }
}
```

#### Recording Contract

```json
{
  "isrc": "GBAHS1600463",                     // Required
  "recording_title": "Shape of You",
  "work_iswc": "T-034524680-1",               // Link to composition
  "artist_name": "Ed Sheeran",
  "label": "Asylum Records UK",
  "release_date": "2017-01-06",
  "duration_seconds": 234,
  "territory_codes": ["GB", "US", "DE"],      // null = worldwide
  "dsp_ids": {
    "spotify": "7qiZfU4dY1lWllzX7mPBI3",
    "apple": "1193701427"
  }
}
```

#### Statement Row Contract

```json
{
  "statement_id": "stmt_spotify_2025_q4",
  "dsp": "spotify",
  "period_from": "2025-10-01",
  "period_to": "2025-12-31",
  "isrc": "GBAHS1600463",
  "work_title": "Shape of You",
  "artist_name": "Ed Sheeran",
  "play_count": 450123,
  "amount": "12345.6789",
  "currency": "USD",
  "territory": "US",
  "rate_per_stream": "0.00002743",
  "statement_type": "streaming"              // streaming | download | performance
}
```

#### Split Sheet Contract

```json
{
  "work_id": "uuid",
  "version": 3,
  "effective_from": "2024-01-01",
  "splits": [
    {"party_id": "uuid", "name": "Ed Sheeran", "share": 0.3333, "role": "Composer"},
    {"party_id": "uuid", "name": "Johnny McDaid", "share": 0.3333, "role": "Composer"},
    {"party_id": "uuid", "name": "Steve Mac", "share": 0.3334, "role": "Producer"}
  ]
}
```

**Validation rule:** `sum(splits[].share) == 1.0` within floating-point tolerance of 0.0001.

#### Cue Sheet Contract

```json
{
  "production_title": "Stranger Things S4E03",
  "production_type": "tv_series",             // tv_series | film | commercial | trailer
  "broadcast_date": "2022-05-27",
  "broadcaster": "Netflix",
  "territory": "US",
  "cues": [
    {
      "sequence": 1,
      "isrc": "GBAHS1600463",
      "work_title": "Shape of You",
      "usage_type": "background",             // theme | background | feature | visual_vocal
      "duration_seconds": 45,
      "timecode_in": "00:12:34:12"
    }
  ]
}
```

---

## 4. Authentication & Authorization Patterns

### 4.1 Pattern Matrix by Partner Type

| Partner type | Auth method | XR7 stores | Rotation |
|-------------|------------|-----------|---------|
| **DSP (SFTP)** | SSH key pair | Private key in Vault | Annual (or on compromise) |
| **DSP (OAuth 2.0)** | Client credentials flow | client_id + client_secret in Vault | Per DSP policy |
| **PRO (API key)** | Header `X-API-Key` | Hashed key in Vault | Annual |
| **Label/Distributor (inbound webhook)** | HMAC-SHA256 signature | Signing secret in Vault | On rotation request |
| **Label/Distributor (outbound)** | XR7-issued API key | Key hash in DB | On request |
| **MLC** | OAuth 2.0 (authorization code) | Refresh token in Vault | Per expiry |
| **Foreign society (SFTP)** | Password + IP allowlist | Encrypted in Vault | Annual |

### 4.2 Inbound Webhook Security

When a partner pushes data to XR7's ingest webhook:

```python
# XR7 validates HMAC signature on all inbound partner webhooks
def verify_partner_webhook(request: Request, partner_id: str) -> bool:
    signing_secret = vault.get(f"partners/{partner_id}/webhook_secret")
    received_sig = request.headers.get("X-Signature-SHA256", "")
    body = await request.body()
    expected_sig = "sha256=" + hmac.new(
        signing_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(received_sig, expected_sig)
```

### 4.3 OAuth 2.0 Token Management

For partners using OAuth 2.0, XR7 manages token refresh automatically:

```python
class OAuthTokenManager:
    """Manages OAuth tokens for partner API integrations."""

    async def get_valid_token(self, partner_id: str) -> str:
        token_data = await vault.get(f"partners/{partner_id}/oauth_token")
        if is_expired(token_data["expires_at"], buffer_seconds=60):
            token_data = await self.refresh_token(partner_id, token_data["refresh_token"])
            await vault.put(f"partners/{partner_id}/oauth_token", token_data)
        return token_data["access_token"]
```

---

## 5. Webhook & Event-Driven Ingestion

### 5.1 Inbound Webhook Endpoints

XR7 exposes the following inbound webhook endpoints for partners:

```
POST /webhooks/ingest/statement
  Purpose: Partner pushes a new statement file URL or inline data
  Auth: HMAC-SHA256 on payload
  Body: { partner_id, statement_url (S3 or partner CDN), metadata }

POST /webhooks/ingest/catalog
  Purpose: Partner pushes catalog updates (new works, recordings, splits)
  Auth: HMAC-SHA256
  Body: { partner_id, operation: "upsert"|"delete", records: [...] }

POST /webhooks/ingest/cue-sheet
  Purpose: TV/film metadata provider pushes new cue sheet
  Auth: HMAC-SHA256
  Body: { source, production_id, cue_sheet: {...} }

POST /webhooks/events/claim-status
  Purpose: DSP confirms claim status change (accepted/rejected/under-review)
  Auth: HMAC-SHA256
  Body: { dsp, claim_ref, status, amount_usd, notes }
```

### 5.2 Outbound Webhook Delivery

XR7 delivers events to partners who subscribe:

```
POST {partner.webhook_url}
Headers:
  Content-Type: application/json
  X-XR7-Event: reconciliation.completed
  X-XR7-Delivery-ID: uuid
  X-XR7-Signature: sha256=<hmac>
  X-XR7-Timestamp: 1712620800

Body:
{
  "event": "reconciliation.completed",
  "occurred_at": "2026-04-09T10:00:00Z",
  "tenant_id": "uuid",
  "data": { ... event-specific payload ... }
}
```

**Subscribed events:**

| Event | Who subscribes | Payload |
|-------|---------------|---------|
| `ingestion.completed` | Labels, distributors | statement_id, row_count, match_rate |
| `reconciliation.completed` | Labels, publishers | reconciliation_id, variance_usd |
| `anomaly.detected` | Labels, publishers | anomaly_id, type, amount_usd, dsp |
| `claim.state_changed` | Labels, artists | claim_id, from_state, to_state |
| `claim.settled` | Labels, artists, recovery | claim_id, settled_amount_usd |

---

## 6. Retry, Reconciliation & Idempotency Rules

### 6.1 Idempotency

Every partner-facing operation is idempotent. Partners may safely retry any operation with the same idempotency key.

```python
# Idempotency key is required for all state-changing partner API calls
POST /partners/v1/statements/import
Headers:
  Idempotency-Key: client-generated-uuid-v4

# If the same key is resubmitted:
# - If the original request succeeded: return original 200 response
# - If the original request failed: retry the operation
# - If the original request is in-flight: return 409 with retry-after
```

Idempotency keys are stored for 24 hours.

### 6.2 Retry Policy (Outbound Webhooks)

```python
RETRY_SCHEDULE = [
    timedelta(seconds=30),       # Attempt 2
    timedelta(minutes=5),        # Attempt 3
    timedelta(minutes=30),       # Attempt 4
    timedelta(hours=2),          # Attempt 5
    timedelta(hours=8),          # Attempt 6 (Enterprise only)
    timedelta(hours=24),         # Attempt 7 (Enterprise only)
]

# After final retry failure → dead-letter queue
# Dead-letter alert → support team + partner notification email
```

### 6.3 Statement Import Reconciliation

After every DSP statement import, XR7 runs a reconciliation check:

```python
async def reconcile_statement_import(statement_id: str):
    """Verify the statement was imported completely and correctly."""
    reported_row_count = await get_dsp_row_count(statement_id)  # from DSP metadata
    imported_row_count = await count_imported_rows(statement_id)
    checksum_match = await verify_file_checksum(statement_id)

    if abs(reported_row_count - imported_row_count) > (reported_row_count * 0.001):
        # >0.1% row count discrepancy → re-import
        await schedule_reimport(statement_id, reason="row_count_mismatch")

    if not checksum_match:
        await schedule_reimport(statement_id, reason="checksum_mismatch")
```

### 6.4 Duplicate Detection

Partners may accidentally re-send the same statement file. Duplicate detection uses SHA-256 of the file content:

```python
class StatementIngestionService:
    async def ingest(self, file: bytes, metadata: StatementMeta) -> IngestionResult:
        checksum = hashlib.sha256(file).hexdigest()
        existing = await self.db.get_statement_by_checksum(checksum, metadata.tenant_id)
        if existing:
            return IngestionResult(status="duplicate", statement_id=existing.id)
        # ... proceed with ingestion
```

---

## 7. Partner Sandbox & Testing Environment

### 7.1 Sandbox Architecture

```
Production cluster                  Sandbox cluster
──────────────────────              ──────────────────────────────
Real DSP credentials                Synthetic data; no real DSPs
Real partner data                   Auto-reset every 7 days
                                    API keys: xr7_sandbox_...
                                    URL: sandbox.xr7.artistos.io
```

### 7.2 Sandbox Data Set

The sandbox is pre-populated with:
- 1,000 works (randomized but realistic ISWC/ISRC)
- 5 simulated DSP statement files (1 year of data, 5 DSPs)
- 3 PRO statement files (ASCAP/BMI/PRS)
- 50 pre-generated anomalies across different DSPs
- 20 claims in various states (DRAFT through SETTLED)
- 5 synthetic tenant accounts at different tiers

### 7.3 Partner Testing Capabilities

Partners can use the sandbox to:

1. **Test statement ingestion:** Push synthetic statement files and observe parsing + matching
2. **Test webhook delivery:** Trigger test webhook events and verify receipt
3. **Test catalog import:** Push catalog updates and verify they're processed
4. **Test claim workflow:** Create and progress claims through the full state machine
5. **Test API authentication:** Verify HMAC signatures, OAuth flows, API key rotation

### 7.4 Sandbox Reset Policy

- Sandbox auto-resets every Sunday at 00:00 UTC
- Partners receive 24h advance notice email before reset
- Partners can request a manual reset via `POST /sandbox/reset` (sandbox environment only)
- Reset preserves API keys; wipes all user data and imported statements

---

## 8. Partner Certification Process

Before a partner integration goes live in production, it must complete certification:

### Phase 1: Technical Review (1 week)

- [ ] Partner provides API documentation for their system (if they push data to XR7)
- [ ] XR7 reviews data contract compliance (Section 3 requirements)
- [ ] Test environment access granted
- [ ] Integration developer call scheduled

### Phase 2: Sandbox Validation (2 weeks)

- [ ] Partner completes sandbox integration
- [ ] XR7 validates: correct auth method, idempotency keys used, payloads match contract
- [ ] Partner validates: webhook receipt, error handling, retry logic
- [ ] End-to-end test: statement → match → anomaly → claim (synthetic data)
- [ ] Load test: partner sends 100 concurrent requests without errors

### Phase 3: Compliance Review

- [ ] Security review: auth credentials stored securely (not in code, not in logs)
- [ ] Data privacy review: no PII transmitted outside agreed fields
- [ ] For DSP integrations: DSP legal team approves XR7 as authorized middleware
- [ ] For PRO integrations: PRO confirms XR7 is authorized to ingest statements on behalf of members

### Phase 4: Production Onboarding

- [ ] Production credentials provisioned (via Vault; not emailed)
- [ ] Partner added to `partner_registry` table with certifier's sign-off
- [ ] Monitoring alerts configured for partner's integration health
- [ ] Runbook written for this partner integration's common failure modes
- [ ] Partner contacts documented in `docs/partner_contacts.md`

### Certification Badge Levels

| Level | Criteria |
|-------|---------|
| **Certified (Bronze)** | Sandbox validation passed; auth + idempotency correct |
| **Certified (Silver)** | Bronze + load test + security review |
| **Certified (Gold)** | Silver + compliance review + 90 days production uptime >99.5% |

---

## 9. Partner Integration Handbook

### Integrating as a Label or Distributor

**Step 1: Request an API key**
Contact your XR7 account manager or sign up at `https://partners.xr7.artistos.io`. API keys are issued with the minimum permissions required for your use case.

**Step 2: Catalog Import**
Push your work and recording catalog via the bulk import API:
```bash
curl -X POST https://api.xr7.artistos.io/v2/catalog/import/bulk \
  -H "Authorization: Bearer xr7_live_..." \
  -H "Idempotency-Key: $(uuidgen)" \
  -H "Content-Type: application/json" \
  -d @my_catalog.json
```

Response:
```json
{
  "import_id": "imp_abc123",
  "status": "accepted",
  "works_received": 5000,
  "recordings_received": 7200
}
```

**Step 3: Statement Push (Webhook)**
Configure your system to push statement files to:
```
POST https://api.xr7.artistos.io/webhooks/ingest/statement
X-Partner-ID: your_partner_id
X-Signature-SHA256: sha256=<hmac_of_body>
Content-Type: application/json

{
  "partner_id": "your_partner_id",
  "statement_url": "https://yourstorage.com/statements/2026-03.csv",
  "dsp": "spotify",
  "period_from": "2026-03-01",
  "period_to": "2026-03-31",
  "row_count": 45000
}
```

**Step 4: Subscribe to Webhooks**
Register your endpoint to receive XR7 events:
```bash
curl -X POST https://api.xr7.artistos.io/v2/webhooks \
  -H "Authorization: Bearer xr7_live_..." \
  -d '{"url": "https://yoursystem.com/xr7-events", "events": ["reconciliation.completed", "claim.settled"]}'
```

---

### Integrating as a PRO

PRO integrations are managed by XR7 on the partner's behalf. XR7's ingestion service connects to PRO portals using credentials issued to XR7 as an authorized representative. No changes required to PRO systems.

**PRO onboarding requirements:**
1. XR7 registers as an authorized "data recipient" with the PRO
2. PRO issues SFTP credentials or API credentials to XR7
3. XR7 associates those credentials with specific member (tenant) accounts
4. PRO statement data is ingested, normalized, and reconciled against DSP data

---

### Integrating as a DSP

DSP integrations ingest statement files or connect to DSP royalty reporting APIs.

**SFTP integration:**
1. Provide XR7 with SFTP host, port, username, and directory path
2. XR7 provides its public SSH key to authorize
3. XR7 pulls files from the directory on a scheduled basis (nightly)

**API integration (preferred):**
1. DSP provides API documentation and credentials (client_id + client_secret)
2. XR7 implements a new parser class in `XR7/ingestion/parsers/<dsp>_v1.py`
3. DSP adds XR7 to its authorized integrators list
4. XR7 pulls statements via API on schedule

---

## 10. Partner API Requirements Checklist

Use before certifying any partner integration for production.

### For Partners That Push Data to XR7 (Inbound)

**Security:**
- [ ] HMAC-SHA256 signature on all webhook payloads (`X-Signature-SHA256` header)
- [ ] Idempotency key (`Idempotency-Key` header) on all state-changing requests
- [ ] API key stored in partner's secrets manager (not in code or environment variables)
- [ ] TLS 1.2+ for all outbound calls to XR7

**Data quality:**
- [ ] Statement rows include ISRC (or work_title + artist_name as fallback)
- [ ] Monetary values are strings with 4 decimal places (not floating point)
- [ ] Dates in ISO 8601 format: `YYYY-MM-DD`
- [ ] Currency code in ISO 4217 format: `USD`, `EUR`, `GBP`
- [ ] All required fields present; no null in required positions
- [ ] Row count in metadata matches actual row count in payload

**Reliability:**
- [ ] Partner system retries failed deliveries with exponential backoff
- [ ] Partner system handles XR7 returning 409 (idempotency conflict) without creating duplicate data
- [ ] Partner system handles XR7 returning 503 (temporary unavailability) with retry
- [ ] Partner system handles XR7 returning 413 (payload too large) by splitting into smaller batches

### For Partners That Receive Data from XR7 (Outbound)

**Security:**
- [ ] Partner webhook endpoint verifies `X-XR7-Signature` header before processing
- [ ] Partner endpoint is HTTPS; no plaintext HTTP
- [ ] Partner endpoint returns 200 within 10 seconds (processing happens async in partner system)

**Reliability:**
- [ ] Partner endpoint is idempotent (same delivery_id received twice = no duplicate processing)
- [ ] Partner system stores delivery_id to detect duplicates
- [ ] Partner endpoint has a response timeout of < 30s (XR7 will retry if timeout exceeded)

---

## 11. Partner Onboarding Workflow (n8n-ready)

```json
{
  "name": "06_partner_onboarding_workflow",
  "nodes": [
    {
      "id": "1",
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "partner-onboarding",
        "method": "POST"
      },
      "notes": "Triggered by: partner_application_submitted event from partners portal"
    },
    {
      "id": "2",
      "name": "Validate Partner Application",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "={{$env.XR7_API_URL}}/internal/partners/validate",
        "body": {
          "partner_id": "={{$json.partner_id}}",
          "partner_type": "={{$json.partner_type}}",
          "company_name": "={{$json.company_name}}"
        }
      }
    },
    {
      "id": "3",
      "name": "Partner Type Router",
      "type": "n8n-nodes-base.switch",
      "parameters": {
        "value": "={{$json.partner_type}}",
        "rules": [
          {"value": "dsp", "output": 0},
          {"value": "label", "output": 1},
          {"value": "pro", "output": 2},
          {"value": "distributor", "output": 3}
        ]
      }
    },
    {
      "id": "4a",
      "name": "DSP: Create SFTP Credentials",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "={{$env.VAULT_URL}}/v1/ssh/creds/dsp-sftp",
        "headers": {"X-Vault-Token": "={{$env.VAULT_TOKEN}}"},
        "body": {"partner_id": "={{$json.partner_id}}"}
      }
    },
    {
      "id": "4b",
      "name": "Label: Generate API Key",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "={{$env.XR7_API_URL}}/internal/api-keys",
        "body": {
          "tenant_id": "={{$json.tenant_id}}",
          "name": "Partner Production Key",
          "permissions": ["statements:import", "catalog:write"]
        }
      }
    },
    {
      "id": "4c",
      "name": "PRO: Schedule Ingestion Job",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "={{$env.XR7_API_URL}}/internal/ingestion/schedules",
        "body": {
          "partner_id": "={{$json.partner_id}}",
          "schedule": "0 3 1 * *",
          "method": "={'sftp_pull'}"
        }
      }
    },
    {
      "id": "5",
      "name": "Create Partner Registry Entry",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "={{$env.XR7_API_URL}}/internal/partners",
        "body": {
          "partner_id": "={{$json.partner_id}}",
          "partner_type": "={{$json.partner_type}}",
          "status": "sandbox",
          "certification_level": "pending"
        }
      }
    },
    {
      "id": "6",
      "name": "Send Sandbox Welcome Package",
      "type": "n8n-nodes-base.emailSend",
      "parameters": {
        "toEmail": "={{$json.technical_contact_email}}",
        "subject": "XR7 Partner Sandbox Access Ready",
        "text": "Your sandbox API key: {{$json.sandbox_api_key}}\nDocs: https://docs.xr7.artistos.io/partners\nSandbox: https://sandbox.xr7.artistos.io"
      }
    },
    {
      "id": "7",
      "name": "Assign Integration Engineer",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "={{$env.ASANA_API_URL}}/tasks",
        "body": {
          "name": "Partner Integration: {{$json.company_name}}",
          "project": "={{$env.ASANA_PARTNER_PROJECT_ID}}",
          "notes": "Partner type: {{$json.partner_type}}\nContact: {{$json.technical_contact_email}}\nCertification target: 4 weeks"
        }
      }
    },
    {
      "id": "8",
      "name": "Notify #partner-integrations Slack",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#partner-integrations",
        "text": "New partner integration started: *{{$json.company_name}}* ({{$json.partner_type}})\nContact: {{$json.technical_contact_email}}\nAsana task created."
      }
    },
    {
      "id": "9",
      "name": "Schedule Certification Check (2 weeks)",
      "type": "n8n-nodes-base.wait",
      "parameters": {
        "amount": 14,
        "unit": "days"
      }
    },
    {
      "id": "10",
      "name": "Check Certification Progress",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "={{$env.XR7_API_URL}}/internal/partners/{{$json.partner_id}}/certification-status"
      }
    },
    {
      "id": "11",
      "name": "Certification Complete?",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "value1": "={{$json.certification_level}}",
          "operation": "equal",
          "value2": "bronze"
        }
      }
    },
    {
      "id": "12a",
      "name": "Promote to Production",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "PATCH",
        "url": "={{$env.XR7_API_URL}}/internal/partners/{{$json.partner_id}}",
        "body": {"status": "production"}
      }
    },
    {
      "id": "12b",
      "name": "Send Certification Reminder",
      "type": "n8n-nodes-base.emailSend",
      "parameters": {
        "toEmail": "={{$json.technical_contact_email}}",
        "subject": "XR7 Partner Certification - Action Required",
        "text": "Your certification is incomplete. Outstanding items: {{$json.outstanding_items}}"
      }
    }
  ],
  "connections": {
    "1 → 2 → 3": "sequential",
    "3[0] → 4a → 5": "DSP path",
    "3[1] → 4b → 5": "Label path",
    "3[2] → 4c → 5": "PRO path",
    "3[3] → 4b → 5": "Distributor path (same as label)",
    "5 → 6 → 7 → 8 → 9 → 10 → 11": "sequential",
    "11[true] → 12a": "certified",
    "11[false] → 12b": "not certified"
  }
}
```
