# XR7 API Documentation

This directory contains the human-readable API reference for the XR7 Engine 2 API.

The machine-readable source of truth is [`openapi/openapi.json`](../../openapi/openapi.json) (OpenAPI 3.1.0, 436 paths, 288 component schemas).

## Contents

| File | Domain | Endpoint count |
|------|--------|---------------|
| [auth.md](auth.md) | Authentication & identity | 5 |
| [artists.md](artists.md) | Artist portal (earnings, claims, ML) | 261 |
| [claims.md](claims.md) | Rights claims & evidence | 20 |
| [admin.md](admin.md) | Internal admin operations | 40 |
| [tvfilm.md](tvfilm.md) | TV/film sync licensing | 18 |
| [invites.md](invites.md) | Invitation & onboarding | 11 |
| [case-rooms.md](case-rooms.md) | Case management rooms | 10 |
| [management.md](management.md) | Artist management layer | 9 |
| [review-queue.md](review-queue.md) | Analyst review queue | 6 |
| [auxiliary.md](auxiliary.md) | Stats, workspace, anomalies, branding, etc. | 38 |
| [errors.md](errors.md) | Shared error models & HTTP status guide | — |
| [authentication.md](authentication.md) | Auth scheme deep dive | — |
| [adding-endpoints.md](adding-endpoints.md) | How to add a new endpoint | — |

## Security Model

All endpoints require a **Bearer token** (JWT, issued by `POST /auth/login/artist` or `POST /auth/login/admin`) unless otherwise stated in the per-endpoint reference.

```
Authorization: Bearer <token>
```

Tokens encode:
- `sub` — user ID
- `role` — `artist` | `admin` | `manager` | `analyst`
- `tenant_id` — multi-tenant isolation scope
- `exp` — expiry (24 hours for artists, 8 hours for admins)

Endpoints that omit security in the spec (visible in `auth: none` column of survey) are **not intentionally public** — they should be audited and secured in the `XR7-security` sprint. See [authentication.md](authentication.md) for status.

## Response Envelope

All successful responses use a consistent envelope:

```json
{
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2025-01-01T00:00:00Z"
  }
}
```

Paginated responses additionally include:

```json
{
  "items": [ ... ],
  "total": 100,
  "page": 1,
  "page_size": 50,
  "has_next": true
}
```

## HTTP Status Codes Used

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Resource created |
| 204 | Success, no body (DELETE) |
| 400 | Validation error (see [errors.md](errors.md)) |
| 401 | Missing or expired auth token |
| 403 | Valid token, insufficient permission |
| 404 | Resource not found |
| 409 | Conflict (duplicate, state violation) |
| 422 | Unprocessable entity (Pydantic validation) |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 503 | Downstream dependency unavailable |

## Versioning

The API does not currently use URL versioning (`/v1/`, `/v2/`). The `info.version` in `openapi.json` tracks schema version. Breaking changes are coordinated via the `XR7-next` migration sprint and communicated through the changelog.
