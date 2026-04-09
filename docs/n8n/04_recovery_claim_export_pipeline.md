# Blueprint 04: Recovery Pipeline → Claim Packaging → Export

## Purpose
Drive the full claim lifecycle from `IDENTIFIED` through evidence packaging, analyst review, filing, and final export to the payer or attorney. This is the core monetization workflow of XR7.

## Trigger
- **Schedule:** Nightly at 01:00 UTC — process all `IDENTIFIED` claims older than 24 hours
- **Manual:** `POST /webhooks/recovery-run` with `{ "artist_id": "...", "claim_ids": [...] }`
- **Downstream trigger:** Automatically triggered at end of Blueprint 01, 02, or 03 when claims are created

---

## Node Map

```
[Trigger]
    │
    ▼
[01] Load IDENTIFIED Claims
    │
    ▼
[02] For Each Claim: Compute Evidence Packet
    │
    ▼
[03] Seal Evidence Packet (cryptographic integrity)
    │
    ▼
[04] Score Claim Confidence
    │
    ├── HIGH confidence (≥0.90)  → [05a] Auto-advance to PREPARED
    ├── MEDIUM confidence (≥0.70) → [05b] Queue for Analyst Review
    └── LOW confidence (<0.70)   → [05c] Flag as Needs More Evidence
    │
    ▼ (after [05a] only)
[06] Advance Claim: PREPARED → SUBMITTED
    │
    ▼
[07] Generate Claim Document (PDF)
    │
    ▼
[08] File Claim (send to payer / PRO / registry)
    │
    ├── success → [09] Advance: SUBMITTED → FILED
    └── failure → [Error Handler]
    │
    ▼
[10] Export Claim Package
    │
    ▼
[11] Log to Immutable Ledger
    │
    ▼
[12] Notify Artist + Internal Team
```

---

## Node Specifications

### Node 01 — Load IDENTIFIED Claims
**Type:** HTTP Request  
**Method:** `GET`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/claims`  
**Auth:** Header Auth — `XR7 API`  
**Query params:**
```
artist_id = {{ $json.artist_id }}          (optional — omit for org-wide run)
status    = IDENTIFIED
older_than_hours = 24
limit     = 100
```

**Response fields:**
- `claims` — array of claim objects
- `total_count`

**Pagination:** If `total_count > 100`, use the `next_cursor` field to page through. Loop this node until `next_cursor` is null.

---

### Node 02 — For Each Claim: Compute Evidence Packet
**Type:** SplitInBatches (batch_size=10) then HTTP Request in loop

**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/evidence/build`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "claim_id": "{{ $json.id }}",
  "include_ledger_lines": true,
  "include_statement_rows": true,
  "include_pro_data": true
}
```

**Purpose:** Assembles the full evidence packet:
- Statement rows proving the reported amount
- PRO ledger data showing expected amount
- Metadata crosswalk proving work identity
- Rate model output showing the gap calculation

**Response fields:**
- `packet_id`
- `base_packet` — the unsigned evidence dict
- `prior_packet_hash` — hash of the previous packet in the artist's chain (or null for genesis)
- `ledger_evidence` — array of supporting ledger lines

**Retry:** 3 attempts, 10-second backoff

---

### Node 03 — Seal Evidence Packet
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/evidence/seal`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "packet_id": "{{ $node['Node 02'].json.packet_id }}",
  "base_packet": "{{ $node['Node 02'].json.base_packet }}",
  "prior_packet_hash": "{{ $node['Node 02'].json.prior_packet_hash }}"
}
```

**Purpose:** Calls `seal_packet()` from `XR7/core/integrity/evidence_crypto.py`. Returns the integrity block with HMAC or RSA signature, chain hash, and line hashes.

**Response fields:**
- `integrity` — the sealed integrity block
- `packet_hash`
- `chain_hash`
- `signature_algorithm`

**Do not retry if this fails** — a failed seal indicates a data integrity issue requiring human investigation.

---

### Node 04 — Score Claim Confidence
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/claims/{{ $json.id }}/score`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "packet_id": "{{ $node['Node 02'].json.packet_id }}"
}
```

**Purpose:** Runs `confidence_score()` and `classify_band()` from `XR7/core/scoring/`. Uses metadata match score, fingerprint coverage, history score, contract data, and conflict flags.

**Response fields:**
- `confidence`
- `band` — `"high"`, `"medium"`, or `"low"`
- `score_breakdown`

**Branching (Switch node after this):**
- `band == "high"` → Node 05a
- `band == "medium"` → Node 05b
- `band == "low"` → Node 05c

---

### Node 05a — Auto-advance to PREPARED
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/claims/{{ $json.id }}/advance`  
**Auth:** Header Auth — `XR7 API`  
**Body:** `{ "target_status": "PREPARED", "reason": "auto_high_confidence" }`

**Purpose:** Calls `next_status(ClaimStatus.IDENTIFIED)` → `PREPARED` via the state machine.

---

### Node 05b — Queue for Analyst Review
**Type:** HTTP Request (and Slack notification)  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/review-queue`  
**Body:** `{ "claim_id": "{{ $json.id }}", "confidence": "{{ $node['Node 04'].json.confidence }}", "reason": "medium_confidence_manual_review" }`

**Slack message:**
```json
{
  "text": "🔍 Claim {{ $json.id }} needs analyst review (confidence: {{ $node['Node 04'].json.confidence }})\nWork: {{ $json.work_title }} | Gap: ${{ $json.gap_amount }}\nhttps://{{ $vars.XR7_BASE_URL }}/claims/{{ $json.id }}"
}
```

**Do not continue to Node 06** — workflow ends here for this claim until an analyst advances it manually.

---

### Node 05c — Flag as Needs More Evidence
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/claims/{{ $json.id }}/flag`  
**Body:** `{ "reason": "low_confidence_insufficient_evidence", "band": "low" }`

**Workflow ends here** for this claim — it goes back to the ingestion team for additional data gathering.

---

### Node 06 — Advance: PREPARED → SUBMITTED
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/claims/{{ $json.id }}/advance`  
**Body:** `{ "target_status": "SUBMITTED", "reason": "auto_pipeline_advance" }`

---

### Node 07 — Generate Claim Document (PDF)
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/claims/{{ $json.id }}/generate-document`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "format": "pdf",
  "include_evidence_packet": true,
  "include_ledger_summary": true
}
```

**Purpose:** Calls `pdf_builder.py` to render the claim document for submission.

**Response fields:**
- `document_url` — signed S3/GCS URL to the generated PDF
- `document_id`

**Timeout:** 30 seconds (PDF generation can be slow for large evidence packets)  
**Retry:** 2 attempts, 15-second backoff

---

### Node 08 — File Claim
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/claims/{{ $json.id }}/file`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "document_id": "{{ $node['Node 07'].json.document_id }}",
  "filing_target": "{{ $json.payer_type }}",
  "submission_method": "api"
}
```

**`payer_type` values:** `"pro"`, `"dsp"`, `"distributor"`, `"mlc"`, `"attorney"`

**On success:** Continue to Node 09  
**On failure:** Route to Error Handler — do NOT auto-retry filing (idempotency risk with external systems)

---

### Node 09 — Advance: SUBMITTED → FILED
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/claims/{{ $json.id }}/advance`  
**Body:** `{ "target_status": "FILED", "reason": "successful_filing", "external_reference": "{{ $node['Node 08'].json.filing_reference }}" }`

---

### Node 10 — Export Claim Package
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/claims/{{ $json.id }}/export`  
**Auth:** Header Auth — `XR7 API`  
**Body:**
```json
{
  "formats": ["pdf", "json"],
  "include_integrity_block": true,
  "destination": "artist_portal"
}
```

**Response fields:**
- `export_urls` — map of format → signed URL

---

### Node 11 — Log to Immutable Ledger
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/ledger/append`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "claim_id": "{{ $json.id }}",
  "event_type": "CLAIM_FILED",
  "packet_id": "{{ $node['Node 02'].json.packet_id }}",
  "chain_hash": "{{ $node['Node 03'].json.chain_hash }}"
}
```

**Purpose:** Appends a `CLAIM_FILED` ledger entry. This entry is itself sealed with `seal_packet()` and chained to the artist's prior ledger entry.

**Do not skip this node even on partial failures** — fire-and-forget if the claim was filed.

---

### Node 12 — Notify
```json
{
  "text": "✅ Claim FILED: {{ $json.id }}\nWork: {{ $json.work_title }} | Gap: ${{ $json.gap_amount }} | Target: {{ $json.payer_type }}\nDocument: {{ $node['Node 10'].json.export_urls.pdf }}"
}
```

---

## Error Handler
For Node 08 failures specifically:

```json
{
  "text": "❌ CLAIM FILING FAILED: {{ $json.id }}\nWork: {{ $json.work_title }}\nError: {{ $json.error }}\nManual action required — do not re-run automatically."
}
```

Call `POST /api/v1/recovery/claims/{{ $json.id }}/flag` with `reason: "filing_failure_manual_review"`.

---

## Retry Logic Summary

| Node | Retries | Backoff | Notes |
|---|---|---|---|
| Node 02 — Build Evidence | 3 | 10s | Idempotent |
| Node 03 — Seal Packet | 0 | — | No retry — failure = data issue |
| Node 04 — Score | 2 | 5s | |
| Node 05a/b/c — Advance/Queue | 2 | 5s | |
| Node 07 — Generate PDF | 2 | 15s | Slow operation |
| Node 08 — File Claim | 0 | — | No auto-retry — external system risk |
| Node 09 — Advance FILED | 3 | 5s | |
| Node 10 — Export | 2 | 5s | |
| Node 11 — Ledger | 3 | 5s | Fire-and-forget on pipeline error |

---

## API Endpoints Summary

| Node | Method | Endpoint |
|---|---|---|
| 01 | GET | `/api/v1/recovery/claims` |
| 02 | POST | `/api/v1/recovery/evidence/build` |
| 03 | POST | `/api/v1/recovery/evidence/seal` |
| 04 | POST | `/api/v1/recovery/claims/{id}/score` |
| 05a | POST | `/api/v1/recovery/claims/{id}/advance` |
| 05b | POST | `/api/v1/recovery/review-queue` |
| 05c | POST | `/api/v1/recovery/claims/{id}/flag` |
| 06 | POST | `/api/v1/recovery/claims/{id}/advance` |
| 07 | POST | `/api/v1/recovery/claims/{id}/generate-document` |
| 08 | POST | `/api/v1/recovery/claims/{id}/file` |
| 09 | POST | `/api/v1/recovery/claims/{id}/advance` |
| 10 | POST | `/api/v1/recovery/claims/{id}/export` |
| 11 | POST | `/api/v1/recovery/ledger/append` |
