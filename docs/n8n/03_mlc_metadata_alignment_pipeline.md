# Blueprint 03: MLC Ingestion → Metadata Alignment → Claim Generation

## Purpose
Process MLC (Mechanical Licensing Collective) bulk data files — align metadata against the catalog, auto-repair gaps, and generate mechanical royalty claims for unmatched or underpaid works.

## Trigger
- **Schedule:** Weekly on Monday at 06:00 UTC
- **Webhook:** `POST /webhooks/mlc-file-received` with `{ "artist_id": "...", "file_url": "...", "reporting_period": "2025-Q3" }`

---

## Node Map

```
[Trigger]
    │
    ▼
[01] Validate Payload + Authenticate MLC File
    │
    ▼
[02] Ingest MLC Bulk File
    │
    ▼
[03] Run Metadata Alignment (Crosswalk)
    │
    ├── [04a] Works with Gaps → Trigger Metadata Repair
    │
    └── [04b] All works aligned → Skip to [05]
    │
    ▼
[05] Compute Expected Mechanical Royalties
    │
    ▼
[06] Compare vs Reported MLC Amounts
    │
    ├── [IF: gap > threshold] → [07] Generate Claims
    │
    └── [IF: no gap] → [08] Mark MLC Period Clean
    │
    ▼
[09] Update Catalog with MLC IDs
    │
    ▼
[10] Notify
```

---

## Node Specifications

### Node 01 — Validate Payload + Authenticate MLC File
**Type:** Function

```javascript
const required = ['artist_id', 'file_url', 'reporting_period'];
for (const f of required) {
  if (!$json[f]) throw new Error(`Missing: ${f}`);
}
// Validate period format YYYY-QN or YYYY-MM
if (!/^\d{4}-(Q[1-4]|\d{2})$/.test($json.reporting_period)) {
  throw new Error(`Invalid reporting_period format: ${$json.reporting_period}`);
}
return [{ json: $json }];
```

---

### Node 02 — Ingest MLC Bulk File
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/ingestion/upload`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "dsp_name": "mlc",
  "statement_period": "{{ $json.reporting_period }}",
  "file_url": "{{ $json.file_url }}"
}
```

**This is the same ingestion endpoint as Blueprint 01** — the system identifies MLC files by `dsp_name: "mlc"` and routes them to the MLC-specific parser internally.

**Response fields:**
- `ingestion_job_id`

**Poll for completion** using `GET /api/v1/ingestion/jobs/{ingestion_job_id}` (same pattern as Blueprint 01, Node 03).

**Fields returned on completion:**
- `parsed_rows` — array of `{ work_title, iswc, isrc, territory, reported_mechanical_rate, reported_amount }`
- `unmatched_rows` — rows where no catalog Work was found by ISWC/ISRC

---

### Node 03 — Run Metadata Alignment (Crosswalk)
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/normalization/crosswalk`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "ingestion_job_id": "{{ $node['Node 02 Poll Result'].json.ingestion_job_id }}"
}
```

**Purpose:** Calls `metadata_repair_engine._scan_statement_crosswalk_gaps()` — aligns ISWC, ISRC, IPI identifiers between the MLC file and the catalog.

**Response fields:**
- `alignment_id`
- `aligned_count`
- `gap_count` — works that could not be aligned
- `gap_work_ids` — array of `work_id` values with gaps

**Branching (IF node):**
- `gap_count > 0` → Node 04a  
- `gap_count == 0` → Node 05 directly

---

### Node 04a — Trigger Metadata Repair for Gap Works
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/normalization/repair`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "work_ids": "{{ $node['Node 03'].json.gap_work_ids }}",
  "repair_mode": "mlc_alignment"
}
```

**Wait for repair:** Poll `GET /api/v1/normalization/repair/{repair_id}` until `status == "completed"`.

**Purpose:** Calls `metadata_repair_engine.run_historical_audit_and_repair()` on only the gap works. This may auto-infer missing ISRCs from ML models or PRO registry lookups.

**Response fields:**
- `repair_id`
- `repaired_count`
- `still_unresolved_count`

---

### Node 05 — Compute Expected Mechanical Royalties
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/compute-expected`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "alignment_id": "{{ $node['Node 03'].json.alignment_id }}",
  "royalty_type": "mechanical",
  "period": "{{ $json.reporting_period }}"
}
```

**Purpose:** Applies statutory mechanical rates (US: $0.091/copy or streaming formula) to aligned Works for the reporting period.

**Response fields:**
- `expected_total`
- `work_expectations` — array of `{ work_id, work_title, expected_amount, statutory_rate, distribution }`

---

### Node 06 — Compare vs Reported MLC Amounts
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/compare`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "alignment_id": "{{ $node['Node 03'].json.alignment_id }}",
  "expected_amounts": "{{ $node['Node 05'].json.work_expectations }}"
}
```

**Response fields:**
- `comparison_id`
- `total_gap`
- `gap_by_work` — array of `{ work_id, work_title, expected, reported, gap, gap_pct, territory }`
- `gap_work_count`
- `threshold_exceeded` — boolean (true when `total_gap > $200 OR gap_by_work.some(w => w.gap_pct > 20)`)

**Branching (IF node):**
- `threshold_exceeded == true` → Node 07 (Generate Claims)
- `threshold_exceeded == false` → Node 08 (Mark Clean)

---

### Node 07 — Generate Claims
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/claims/generate`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "comparison_id": "{{ $node['Node 06'].json.comparison_id }}",
  "source": "mlc_reconciliation",
  "anomaly_category": "ROYALTY",
  "auto_advance_to_prepared": false
}
```

**Purpose:** Creates `Claim` records in `IDENTIFIED` status. An analyst must review before advancing to `PREPARED`.

**Response fields:**
- `claim_ids` — array of created claim UUIDs
- `claims_created`

---

### Node 08 — Mark MLC Period Clean
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/recovery/mlc-period/{{ $json.reporting_period }}/mark-clean`  
**Auth:** Header Auth — `XR7 API`  
**Body:** `{ "artist_id": "{{ $json.artist_id }}" }`

---

### Node 09 — Update Catalog with MLC IDs
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/catalog/update-identifiers`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "alignment_id": "{{ $node['Node 03'].json.alignment_id }}"
}
```

**Purpose:** Persists any MLC-provided ISWC or IPI values back to the catalog `Work` records for future matching accuracy.

---

### Node 10 — Notify
```json
{
  "text": "MLC Pipeline — {{ $json.reporting_period }} | Artist {{ $json.artist_id }}\nAligned: {{ $node['Node 03'].json.aligned_count }} | Gaps repaired: {{ $node['Node 04a'].json.repaired_count }}\nTotal gap: ${{ $node['Node 06'].json.total_gap }} | Claims created: {{ $node['Node 07'].json.claims_created || 0 }}"
}
```

---

## Retry Logic Summary

| Node | Retries | Backoff | Idempotent? |
|---|---|---|---|
| Node 02 — Ingest | 3 | 15s | Yes |
| Node 03 — Crosswalk | 2 | 10s | Yes |
| Node 04a — Repair | 2 | 10s | Yes |
| Node 05 — Expected | 2 | 5s | Yes |
| Node 06 — Compare | 2 | 5s | Yes |
| Node 07 — Claims | 3 | 10s | Yes (upserts by comparison_id) |
| Node 09 — Update IDs | 2 | 5s | Yes |

---

## API Endpoints Summary

| Node | Method | Endpoint |
|---|---|---|
| 02 | POST | `/api/v1/ingestion/upload` |
| 03 | POST | `/api/v1/normalization/crosswalk` |
| 04a | POST | `/api/v1/normalization/repair` |
| 05 | POST | `/api/v1/recovery/compute-expected` |
| 06 | POST | `/api/v1/recovery/compare` |
| 07 | POST | `/api/v1/recovery/claims/generate` |
| 08 | POST | `/api/v1/recovery/mlc-period/{period}/mark-clean` |
| 09 | POST | `/api/v1/catalog/update-identifiers` |
