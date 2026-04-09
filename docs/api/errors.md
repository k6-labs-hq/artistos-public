# API Error Models

This document describes all standard error responses returned by the XR7 API.

---

## Standard Error Envelope

All non-2xx responses return a consistent error body:

```json
{
  "error": "error_code",
  "message": "Human-readable description",
  "request_id": "req_abc123",
  "detail": { }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `error` | string | Machine-readable error code (use for programmatic handling) |
| `message` | string | Human-readable explanation |
| `request_id` | string | Use this in support tickets for trace correlation |
| `detail` | object? | Optional — field-level details for validation errors |

---

## HTTP Status Reference

### 400 Bad Request

The request is malformed or contains invalid data that cannot be processed.

```json
{
  "error": "bad_request",
  "message": "Statement date must be after 2010-01-01",
  "request_id": "req_abc"
}
```

### 401 Unauthorized

No auth token was provided, or the token has expired / been revoked.

```json
{
  "error": "unauthorized",
  "message": "Token has expired. Please re-authenticate.",
  "request_id": "req_abc"
}
```

**Fix:** `POST /auth/login/artist` to get a new token.

### 403 Forbidden

Token is valid but the user does not have the required permission.

```json
{
  "error": "forbidden",
  "message": "Role 'artist' does not have access to admin audit logs",
  "request_id": "req_abc"
}
```

### 404 Not Found

The requested resource does not exist in the caller's tenant scope.

```json
{
  "error": "not_found",
  "message": "Artist usr_xyz not found",
  "request_id": "req_abc"
}
```

### 409 Conflict

The operation would create a duplicate, or a state machine transition is invalid.

```json
{
  "error": "conflict",
  "message": "Claim c_abc is already in SUBMITTED state and cannot be reopened",
  "request_id": "req_abc"
}
```

**Common causes:**
- Submitting a claim that was already submitted
- Creating an artist account with an already-registered email
- Attempting a non-allowed state machine transition (see [claims state machine](../claims_state_machine.md))

### 422 Unprocessable Entity

Pydantic validation failed. The `detail` array identifies the exact field(s).

```json
{
  "detail": [
    {
      "loc": ["body", "isrc"],
      "msg": "ISRC must match pattern [A-Z]{2}[A-Z0-9]{3}[0-9]{7}",
      "type": "value_error.str.regex",
      "input": "bad-isrc"
    }
  ]
}
```

**Note:** 422 is a FastAPI/Pydantic response. For application-level validation errors (business rules), 400 is used.

### 429 Too Many Requests

Rate limit exceeded. Retry after the indicated time.

```json
{
  "error": "rate_limited",
  "message": "Too many requests. Retry after 30 seconds.",
  "request_id": "req_abc",
  "retry_after": 30
}
```

**Rate limits:**
- Public endpoints: 60 requests/minute
- Authenticated artist endpoints: 300 requests/minute
- Admin endpoints: 600 requests/minute
- Evidence export: 10 requests/minute

### 500 Internal Server Error

Unexpected server error. The `request_id` should be submitted to the on-call team.

```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred. Please contact support with request_id.",
  "request_id": "req_abc"
}
```

### 503 Service Unavailable

A downstream dependency (DSP API, payment processor, ML model) is temporarily unavailable.

```json
{
  "error": "service_unavailable",
  "message": "Spotify reconciliation service is temporarily unavailable",
  "request_id": "req_abc",
  "retry_after": 120
}
```

---

## Named Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `unauthorized` | 401 | No token or expired token |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not in caller's scope |
| `conflict` | 409 | Duplicate or invalid state transition |
| `bad_request` | 400 | Business rule validation failed |
| `rate_limited` | 429 | Too many requests |
| `internal_error` | 500 | Unexpected server error |
| `service_unavailable` | 503 | Downstream dependency down |
| `claim_locked` | 409 | Claim is locked by analyst review — cannot modify |
| `evidence_sealed` | 409 | Evidence packet is sealed — cannot add/remove items |
| `ingestion_in_progress` | 409 | Another ingestion job is already running for this artist |
| `tenant_mismatch` | 403 | Resource belongs to a different tenant |
| `insufficient_data` | 400 | Not enough historical data to compute (ML / forecasting) |

---

## Component Schema: `ErrorResponse`

```yaml
ErrorResponse:
  type: object
  required:
    - error
    - message
    - request_id
  properties:
    error:
      type: string
      description: Machine-readable error code
      example: unauthorized
    message:
      type: string
      description: Human-readable explanation
    request_id:
      type: string
      description: Correlation ID for tracing
    detail:
      type: object
      description: Optional structured detail (validation errors, conflict context)
      nullable: true
```
