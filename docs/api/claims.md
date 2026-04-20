# Claims API

Base path: `/claims`
Tag: `claims`
Auth required: Varies per endpoint (see table below)

The Claims API manages the full lifecycle of rights recovery claims — from creation through evidence generation, analyst review, and legal export.

For the state machine governing allowed transitions, see [claims_state_machine.md](../claims_state_machine.md).

---

## Endpoint Summary

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/claims/{claim_id}` | none¹ | Retrieve a claim by ID |
| POST | `/claims/{claim_id}/advance` | none¹ | Advance claim to next state |
| POST | `/claims/{claim_id}/evidence` | none¹ | Generate evidence package |
| GET | `/claims/{claim_id}/evidence` | Bearer | Download evidence package |
| POST | `/claims/{claim_id}/attorney-evidence` | none¹ | Generate attorney evidence file |
| GET | `/claims/{claim_id}/evidence/export` | none¹ | Export evidence packet (analyst) |
| POST | `/claims/{claim_id}/evidence/export` | none¹ | Export evidence packet (expert mode) |
| GET | `/claims/{claim_id}/timeline` | none¹ | Get claim event timeline |
| GET | `/claims/{claim_id}/signature` | none¹ | Get evidence packet signature |
| POST | `/claims/{claim_id}/submit` | none¹ | Submit claim to DSP |
| GET | `/claims` | Bearer | List all claims for tenant |
| POST | `/claims` | Bearer | Create a new claim |
| GET | `/claims/{claim_id}/history` | Bearer | Paged event history |
| POST | `/claims/{claim_id}/notes` | Bearer | Add analyst note |
| DELETE | `/claims/{claim_id}` | Bearer | Delete draft claim |
| GET | `/claims/{claim_id}/audit` | Bearer | Claim audit log |
| PATCH | `/claims/{claim_id}/state` | Bearer | Force state transition (admin) |
| GET | `/claims/stats` | Bearer | Aggregated claim statistics |
| GET | `/claims/{claim_id}/documents` | Bearer | List claim documents |
| POST | `/claims/{claim_id}/documents` | Bearer | Upload claim document |

¹ Auth gap — these endpoints lack `security` in the current OpenAPI spec and are tracked for the `XR7-security` sprint.

---

## Endpoints (detail)

### `GET /claims/{claim_id}`

Retrieves a claim by its ID.

**Path params:** `claim_id` (string)

**Response 200** — `ClaimResponse`:
```json
{
  "claim_id":    "clm_abc123",
  "artist_id":   "usr_abc123",
  "isrc":        "USRC12345678",
  "work_title":  "Song of the Year",
  "state":       "EVIDENCE_READY",
  "payer":       "spotify",
  "amount_usd":  1250.00,
  "period_from": "2024-01-01",
  "period_to":   "2024-12-31",
  "created_at":  "2025-01-15T10:00:00Z"
}
```

| Code | Description |
|------|-------------|
| 200 | Claim found |
| 404 | Claim not found |

---

### `POST /claims/{claim_id}/advance`

Advances the claim to the next state in the state machine.

Allowed transitions:

| From | To | Trigger |
|------|----|---------|
| `DRAFT` | `EVIDENCE_PENDING` | Evidence generation requested |
| `EVIDENCE_PENDING` | `EVIDENCE_READY` | Evidence generated successfully |
| `EVIDENCE_READY` | `SUBMITTED` | Submitted to DSP |
| `SUBMITTED` | `UNDER_REVIEW` | DSP acknowledged |
| `UNDER_REVIEW` | `RESOLVED` | DSP accepted |
| `UNDER_REVIEW` | `DISPUTED` | DSP rejected |
| `DISPUTED` | `ESCALATED` | Analyst escalated |

**Request body** — `ClaimAdvanceRequest`:
```json
{
  "target_state": "SUBMITTED",
  "reason": "Evidence verified by analyst"
}
```

| Code | Description |
|------|-------------|
| 200 | State advanced |
| 409 | Transition not allowed from current state |

---

### `POST /claims/{claim_id}/evidence`

Triggers asynchronous evidence package generation. Evidence includes:
- Earnings comparison table (expected vs. actual)
- Royalty calculation audit trail
- HMAC-signed evidence hash
- DSP ingestion metadata

**Response 200** — `EvidenceGenerationResponse`:
```json
{
  "job_id":     "job_abc123",
  "status":     "queued",
  "eta_seconds": 30
}
```

---

### `GET /claims/{claim_id}/evidence`

Downloads the sealed evidence package as a JSON document.

**Auth:** Bearer
**Response 200** — `EvidencePacket`:
```json
{
  "claim_id":        "clm_abc123",
  "generated_at":    "2025-01-15T10:05:00Z",
  "hmac_signature":  "sha256:abc...",
  "evidence_items":  [ ... ],
  "earnings_delta":  1250.00,
  "currency":        "USD"
}
```

---

### `GET /claims/{claim_id}/timeline`

Returns the chronological event log for a claim, showing all state transitions, notes, submissions, and DSP responses.

**Response 200** — `ClaimTimeline`:
```json
{
  "claim_id": "clm_abc123",
  "events": [
    {
      "ts":     "2025-01-15T10:00:00Z",
      "event":  "CREATED",
      "actor":  "usr_abc123",
      "detail": "Claim created for period 2024-01"
    }
  ]
}
```

---

### `GET /claims` (list)

Returns all claims in the caller's tenant scope, with pagination.

**Query params:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `state` | string | all | Filter by claim state |
| `payer` | string | all | Filter by DSP/payer |
| `page` | integer | 1 | Page number |
| `page_size` | integer | 50 | Records per page (max 200) |

**Response 200:**
```json
{
  "items":     [ ... ],
  "total":     84,
  "page":      1,
  "page_size": 50,
  "has_next":  true
}
```

---

### `POST /claims` (create)

Creates a new draft claim.

**Auth:** Bearer
**Request body** — `CreateClaimRequest`:
```json
{
  "artist_id":   "usr_abc123",
  "isrc":        "USRC12345678",
  "work_title":  "Song of the Year",
  "payer":       "spotify",
  "period_from": "2024-01-01",
  "period_to":   "2024-12-31",
  "amount_usd":  1250.00
}
```

| Code | Description |
|------|-------------|
| 201 | Claim created; returns `ClaimResponse` |
| 409 | Duplicate claim for same ISRC + period + payer |
| 422 | Validation error |

---

## Related Documentation

- [Claims State Machine](../claims_state_machine.md) — full state diagram
- [Evidence Security Runbook](../evidence_security_runbook.md) — HMAC signing process
- [Recovery Intelligence Backlog](../recovery_intelligence_backlog.md) — ML-assisted claim detection
