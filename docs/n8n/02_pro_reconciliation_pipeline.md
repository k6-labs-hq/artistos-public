# Blueprint 02: PRO Ingestion → Reconciliation → Discrepancy Flagging

## Purpose
Fetch PRO (ASCAP / BMI / SESAC / PRS / SOCAN) statement data, reconcile it against the artist's registered works, and flag discrepancies for analyst review or automated recovery.

## Trigger
- **Schedule:** Daily at 02:00 UTC for each connected PRO account
- **Manual:** `POST /webhooks/pro-reconcile` with `{ "artist_id": "...", "pro_name": "...", "period": "2025-Q4" }`

---

## Node Map

```
[Trigger]
    │
    ▼
[01] Validate Trigger Payload
    │
    ▼
[02] Fetch PRO Statement Data
    │
    ▼
[03] Fetch Artist Registered Works
    │
    ▼
[04] Run Reconciliation
    │
    ├── [IF: discrepancies found]
    │       │
    │       ▼
    │   [05a] Flag Discrepancies / Create Anomaly Records
    │       │
    │       ▼
    │   [05b] Route by Severity
    │       ├── HIGH → [06a] Auto-open Recovery
    │       └── LOW  → [06b] Add to Watchlist
    │
    └── [IF: no discrepancies]
            │
            ▼
        [07] Mark Period Reconciled
    │
    ▼
[08] Notify
```

---

## Node Specifications

### Node 01 — Validate Trigger Payload
**Type:** Function

```javascript
const required = ['artist_id', 'pro_name', 'period'];
for (const f of required) {
  if (!$json[f]) throw new Error(`Missing: ${f}`);
}
const validPros = ['ascap', 'bmi', 'sesac', 'prs', 'socan', 'sabam', 'gema', 'sacem'];
if (!validPros.includes($json.pro_name.toLowerCase())) {
  throw new Error(`Unknown PRO: ${$json.pro_name}`);
}
return [{ json: $json }];
```

---

### Node 02 — Fetch PRO Statement Data
**Type:** HTTP Request
**Method:** `GET`
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/ingestion/pro-statement`
**Auth:** Header Auth — `XR7 API`
**Query params:**
```
artist_id = {{ $json.artist_id }}
pro_name  = {{ $json.pro_name }}
period    = {{ $json.period }}
```

**Purpose:** Calls the PRO connector to fetch statement rows from the PRO's API or from uploaded files already ingested by the ingestion pipeline.

**Response fields:**
- `statement_rows` — array of `{ work_title, isrc, iswc, amount, territory, period }`
- `statement_id`
- `total_reported`

**Retry:** 3 attempts, 15-second backoff
**On error:** Route to Error Handler

---

### Node 03 — Fetch Artist Registered Works
**Type:** HTTP Request
**Method:** `GET`
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/catalog/works`
**Auth:** Header Auth — `XR7 API`
**Query params:**
```
artist_id = {{ $json.artist_id }}
include_ids = isrc,iswc,ipi
```

**Response fields:**
- `works` — array of `{ work_id, work_title, isrc, iswc, ipi, registered_territories }`
- `work_count`

---

### Node 04 — Run Reconciliation
**Type:** HTTP Request
**Method:** `POST`
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/reconcile`
**Auth:** Header Auth — `XR7 API`
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "statement_id": "{{ $node['Node 02'].json.statement_id }}",
  "pro_name": "{{ $json.pro_name }}",
  "period": "{{ $json.period }}"
}
```

**Purpose:** Runs the XR7 reconciliation engine — compares PRO-reported amounts against catalog registrations and expected royalties, applying rate models.

**Response fields:**
- `reconciliation_id`
- `discrepancy_count`
- `discrepancies` — array of:
  ```json
  {
    "work_id": "...",
    "work_title": "...",
    "expected_amount": 420.00,
    "reported_amount": 180.00,
    "gap": 240.00,
    "gap_pct": 57.1,
    "severity": "HIGH",
    "anomaly_category": "ROYALTY",
    "territory": "US"
  }
  ```
- `total_expected`
- `total_reported`
- `total_gap`

**Branching (IF node after):**
- `discrepancy_count > 0` → Node 05a
- `discrepancy_count == 0` → Node 07

---

### Node 05a — Flag Discrepancies / Create Anomaly Records
**Type:** HTTP Request
**Method:** `POST`
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/anomalies/bulk-create`
**Auth:** Header Auth — `XR7 API`
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "reconciliation_id": "{{ $node['Node 04'].json.reconciliation_id }}",
  "discrepancies": "{{ $node['Node 04'].json.discrepancies }}"
}
```

**Response fields:**
- `anomaly_ids` — array of created anomaly UUIDs
- `high_severity_count`
- `low_severity_count`

---

### Node 05b — Route by Severity
**Type:** IF
**Condition:** `{{ $json.high_severity_count }} > 0`
- **True branch** → Node 06a (Auto-open Recovery)
- **False branch** → Node 06b (Add to Watchlist)

---

### Node 06a — Auto-open Recovery
**Type:** HTTP Request
**Method:** `POST`
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/open`
**Auth:** Header Auth — `XR7 API`
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "anomaly_ids": "{{ $node['Node 05a'].json.anomaly_ids }}",
  "source": "pro_reconciliation",
  "auto_file": false
}
```

**Purpose:** Creates `Claim` records in `IDENTIFIED` status. Sets `auto_file=false` — an analyst must advance to PREPARED before submission.

**Retry:** 2 attempts, 10-second backoff

---

### Node 06b — Add to Watchlist
**Type:** HTTP Request
**Method:** `POST`
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/watchlist`
**Auth:** Header Auth — `XR7 API`
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "anomaly_ids": "{{ $node['Node 05a'].json.anomaly_ids }}",
  "reason": "low_severity_pro_discrepancy"
}
```

---

### Node 07 — Mark Period Reconciled
**Type:** HTTP Request
**Method:** `POST`
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/reconciliation/{{ $node['Node 04'].json.reconciliation_id }}/mark-complete`
**Auth:** Header Auth — `XR7 API`

---

### Node 08 — Notify
**Type:** HTTP Request (Slack)

```json
{
  "text": "PRO Reconciliation — {{ $json.pro_name.toUpperCase() }} | Artist {{ $json.artist_id }} | Period {{ $json.period }}\nDiscrepancies: {{ $node['Node 04'].json.discrepancy_count }} | Gap: ${{ $node['Node 04'].json.total_gap }}\nStatus: {{ $node['Node 05a'].json.high_severity_count > 0 ? 'RECOVERY OPENED' : 'WATCHLISTED' }}"
}
```

---

## Error Handler
Same pattern as Blueprint 01. Call `POST /api/v1/recovery/reconciliation/{{ $json.reconciliation_id }}/mark-failed` if Node 04 or later fails.

---

## Retry Logic Summary

| Node | Retries | Backoff |
|---|---|---|
| Node 02 — Fetch PRO | 3 | 15s |
| Node 03 — Fetch Works | 2 | 5s |
| Node 04 — Reconcile | 2 | 10s |
| Node 05a — Flag | 3 | 10s (idempotent) |
| Node 06a — Open Recovery | 2 | 10s |
| Node 06b — Watchlist | 2 | 5s |

---

## API Endpoints Summary

| Node | Method | Endpoint |
|---|---|---|
| 02 | GET | `/api/v1/ingestion/pro-statement` |
| 03 | GET | `/api/v1/catalog/works` |
| 04 | POST | `/api/v1/recovery/reconcile` |
| 05a | POST | `/api/v1/anomalies/bulk-create` |
| 06a | POST | `/api/v1/recovery/open` |
| 06b | POST | `/api/v1/recovery/watchlist` |
| 07 | POST | `/api/v1/recovery/reconciliation/{id}/mark-complete` |
