# Blueprint 01: DSP Ingestion → Normalization → Matching → Storage

## Purpose
Trigger when a new DSP statement file arrives (via webhook, S3 event, or scheduled poll), parse it, extract identity signals, match catalog entities, and persist normalized statement rows.

## Trigger
- **Webhook** (preferred): `POST /webhooks/dsp-statement-arrived`
- **Schedule** (fallback): every 4 hours for each connected DSP

---

## Node Map

```
[Trigger]
    │
    ▼
[01] Validate Incoming Payload
    │
    ▼
[02] Upload Statement File to Ingestion API
    │
    ▼
[03] Poll Ingestion Status (loop until done)
    │ success branch ──────────────────────────────────────────────┐
    │ error branch → [Error Handler]                               │
    ▼                                                              │
[04] Extract Identity Signals                                      │
    │                                                              │
    ▼                                                              │
[05] Run Catalog Match                                             │
    │                                                              │
    ▼                                                              │
[06] Persist Matched Statement Rows                               ◄──┘
    │
    ▼
[07] Trigger Normalization / Metadata Repair
    │
    ▼
[08] Notify on Success / Failure
```

---

## Node Specifications

### Node 01 — Validate Incoming Payload
**Type:** Function  
**Purpose:** Guard against malformed trigger payloads before any API calls.

```javascript
// Input: $json (webhook body)
// Expected fields: artist_id, file_url OR file_bytes, dsp_name, statement_period
const required = ['artist_id', 'dsp_name', 'statement_period'];
for (const field of required) {
  if (!$json[field]) throw new Error(`Missing required field: ${field}`);
}
// Pass through
return [{ json: $json }];
```

**Output fields:** `artist_id`, `dsp_name`, `statement_period`, `file_url` (optional)

---

### Node 02 — Upload Statement File to Ingestion API
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/ingestion/upload`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "dsp_name": "{{ $json.dsp_name }}",
  "statement_period": "{{ $json.statement_period }}",
  "file_url": "{{ $json.file_url }}"
}
```

**On error:** Route to `[Error Handler]`  
**Retry:** 3 attempts, 10-second backoff

**Response fields used downstream:**
- `ingestion_job_id` — used to poll status in Node 03

---

### Node 03 — Poll Ingestion Status
**Type:** Loop (Wait → HTTP Request → IF)  
**Poll URL:** `GET {{ $vars.XR7_BASE_URL }}/api/v1/ingestion/jobs/{{ $node["Node 02"].json.ingestion_job_id }}`  
**Auth:** Header Auth — `XR7 API`  
**Poll interval:** 5 seconds  
**Max polls:** 60 (i.e., 5-minute timeout)

**Wait node settings:** 5 seconds between iterations

**IF condition (exit loop):** `{{ $json.status }}` equals `"completed"` OR `"failed"`

**On `failed` status:** Route to `[Error Handler]`  
**On `completed` status:** Continue to Node 04

**Response fields used downstream:**
- `statement_rows_count`
- `parsed_rows` (array of normalized statement row objects)

---

### Node 04 — Extract Identity Signals
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/ingestion/extract-signals`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "ingestion_job_id": "{{ $node['Node 02'].json.ingestion_job_id }}"
}
```

**Purpose:** Calls `XR7/ingestion/statement_signal_extractor.py → extract_statement_signals()`

**Response fields used downstream:**
- `signals.artist_name`
- `signals.isrcs` (array)
- `signals.iswcs` (array)
- `signals.upcs` (array)
- `signals.pro_writer_id`
- `signals.distributor_list` (array)

**On error:** Route to `[Error Handler]`  
**Retry:** 2 attempts, 5-second backoff

---

### Node 05 — Run Catalog Match
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/fingerprinting/match`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "signals": "{{ $node['Node 04'].json.signals }}"
}
```

**Purpose:** Calls `compute_identity_match()` + `persist_identity_match()`

**Response fields used downstream:**
- `match.score`
- `match.band` — `AUTO_ACCEPT`, `SOFT_CONFIRM`, or `REQUIRE_CONFIRMATION`
- `match.decision_status`
- `match.match_id`

**Branching (IF node after this):**
- `band == "REQUIRE_CONFIRMATION"` → send to analyst review queue Slack message, then continue
- `band == "AUTO_ACCEPT"` or `"SOFT_CONFIRM"` → continue to Node 06

**On error:** Route to `[Error Handler]`

---

### Node 06 — Persist Matched Statement Rows
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/ingestion/persist`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "ingestion_job_id": "{{ $node['Node 02'].json.ingestion_job_id }}",
  "match_id": "{{ $node['Node 05'].json.match.match_id }}"
}
```

**Purpose:** Writes normalized `Statement` rows to the database with catalog match linkage.

**Response fields used downstream:**
- `persisted_count`
- `statement_ids` (array)

**On error:** Route to `[Error Handler]`  
**Idempotency:** Node is idempotent — re-running with the same `ingestion_job_id` is safe.

---

### Node 07 — Trigger Normalization / Metadata Repair
**Type:** HTTP Request  
**Method:** `POST`  
**URL:** `{{ $vars.XR7_BASE_URL }}/api/v1/normalization/repair`  
**Auth:** Header Auth — `XR7 API`  
**Body (JSON):**
```json
{
  "artist_id": "{{ $json.artist_id }}",
  "statement_ids": "{{ $node['Node 06'].json.statement_ids }}"
}
```

**Purpose:** Triggers `metadata_repair_engine.run_historical_audit_and_repair()` for affected catalog Works.

**Mode:** Fire-and-forget (do not wait for completion — repair runs async)

**On error:** Log warning, do not fail the workflow.

---

### Node 08 — Notify on Success
**Type:** HTTP Request (or Slack node)  
**URL:** `{{ $vars.WEBHOOK_ERROR_CHANNEL }}`  
**Body:**
```json
{
  "text": "✅ DSP ingestion complete for {{ $json.artist_id }} ({{ $json.dsp_name }}): {{ $node['Node 06'].json.persisted_count }} rows ingested."
}
```

---

## Error Handler Node

**Type:** HTTP Request → Slack  
**Trigger:** Any node routes here on error.

```json
{
  "text": "❌ XR7 DSP ingestion FAILED\nArtist: {{ $json.artist_id }}\nDSP: {{ $json.dsp_name }}\nError: {{ $json.error }}\nNode: {{ $runIndex }}"
}
```

**Additional action:** Call `POST /api/v1/ingestion/jobs/{{ $json.ingestion_job_id }}/mark-failed` to update the job status in the DB.

---

## Retry Logic Summary

| Node | Retries | Backoff |
|---|---|---|
| Node 02 — Upload | 3 | 10s |
| Node 03 — Poll | 60 loops | 5s each |
| Node 04 — Signals | 2 | 5s |
| Node 05 — Match | 2 | 5s |
| Node 06 — Persist | 3 | 10s (idempotent) |
| Node 07 — Repair | 0 | fire-and-forget |

---

## n8n Workflow JSON (importable)

```json
{
  "name": "XR7 — DSP Ingestion Pipeline",
  "nodes": [
    {
      "id": "trigger",
      "name": "Webhook: DSP Statement Arrived",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "dsp-statement-arrived",
        "httpMethod": "POST",
        "responseMode": "onReceived"
      },
      "position": [250, 300]
    },
    {
      "id": "validate",
      "name": "01 Validate Payload",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "const required = ['artist_id','dsp_name','statement_period'];\nfor (const f of required) { if (!$json[f]) throw new Error('Missing: '+f); }\nreturn [{json: $json}];"
      },
      "position": [450, 300]
    },
    {
      "id": "upload",
      "name": "02 Upload to Ingestion API",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "={{ $vars.XR7_BASE_URL }}/api/v1/ingestion/upload",
        "authentication": "headerAuth",
        "bodyParametersUi": { "parameter": [
          {"name": "artist_id", "value": "={{ $json.artist_id }}"},
          {"name": "dsp_name", "value": "={{ $json.dsp_name }}"},
          {"name": "statement_period", "value": "={{ $json.statement_period }}"},
          {"name": "file_url", "value": "={{ $json.file_url }}"}
        ]},
        "options": {"retry": {"maxTries": 3, "waitBetweenTries": 10000}}
      },
      "position": [650, 300]
    }
  ],
  "connections": {
    "Webhook: DSP Statement Arrived": {"main": [[{"node": "01 Validate Payload", "type": "main", "index": 0}]]},
    "01 Validate Payload": {"main": [[{"node": "02 Upload to Ingestion API", "type": "main", "index": 0}]]}
  },
  "settings": {"executionOrder": "v1"},
  "meta": {"instanceId": "xr7-dsp-ingestion-v1"}
}
```

> **Note:** Expand this JSON with the remaining nodes (03–08) following the specifications above. The JSON is provided as a starting scaffold — add nodes programmatically in the n8n UI or extend the JSON array.
