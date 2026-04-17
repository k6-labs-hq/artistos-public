# OpenAPI Examples Implementation Guide

## Overview
OpenAPI examples improve developer experience by showing real-world request/response payloads in Swagger UI and API docs. This guide covers how to add examples to FastAPI endpoints.

## Current Coverage

**Status:** 1.5% (7/470 endpoints)

**Priority Implementation Order:**
1. **Core Artist Operations** (GET /artists/{id}, POST /artists)
2. **Claims Management** (POST /artists/{id}/claims, GET /claims/{id})
3. **Statement Upload** (POST /artists/{id}/statements/upload)
4. **Authentication** (POST /auth/login, POST /auth/refresh)
5. **Webhooks** (POST /connectors/webhook/ingest)

## Implementation Pattern

### Basic Example Template

```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ArtistCreate(BaseModel):
    name: str
    email: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "MC Hammer",
                "email": "hammer@example.com"
            }
        }

@router.post(
    "/artists",
    response_model=ArtistSchema,
    openapi_extra={
        "responses": {
            201: {
                "description": "Artist created successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "name": "MC Hammer",
                            "email": "hammer@example.com",
                            "created_at": "2026-04-16T19:35:00Z",
                            "country_code": "US"
                        }
                    }
                }
            },
            422: {
                "description": "Validation error",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                {
                                    "loc": ["body", "email"],
                                    "msg": "value is not a valid email address",
                                    "type": "value_error.email"
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
)
def create_artist(artist_in: ArtistCreate, db: Session = Depends(get_db)):
    # Implementation...
    pass
```

### Multiple Examples

For endpoints with multiple use cases:

```python
@router.post(
    "/artists/{artist_id}/claims",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "mechanical": {
                            "summary": "Mechanical royalty claim",
                            "value": {
                                "work_title": "Can't Touch This",
                                "claim_type": "mechanical",
                                "amount_usd": 5000.00,
                                "period_start": "2020-01-01",
                                "period_end": "2020-12-31"
                            }
                        },
                        "performance": {
                            "summary": "Performance royalty claim",
                            "value": {
                                "work_title": "U Can't Touch This (Live)",
                                "claim_type": "performance",
                                "amount_usd": 12000.00,
                                "venue": "Oakland Arena"
                            }
                        }
                    }
                }
            }
        },
        "responses": {
            201: {
                "content": {
                    "application/json": {
                        "example": {
                            "claim_id": "clm_abc123",
                            "status": "draft",
                            "estimated_recovery_probability": 0.78
                        }
                    }
                }
            }
        }
    }
)
def create_claim(...):
    pass
```

## Error Response Standards

### Common Error Examples

**401 Unauthorized:**
```json
{
  "detail": "Invalid or missing API key"
}
```

**403 Forbidden:**
```json
{
  "detail": "Insufficient role. Required: manager, attorney. Current: analyst"
}
```

**404 Not Found:**
```json
{
  "detail": "Artist not found"
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "amount_usd"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

**429 Rate Limit:**
```json
{
  "detail": "Rate limit exceeded. Retry after 60 seconds.",
  "retry_after": 60
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error. Request ID: req_xyz789",
  "request_id": "req_xyz789"
}
```

## Pydantic Schema Examples

Add examples directly to Pydantic models:

```python
from pydantic import BaseModel, Field

class ClaimCreate(BaseModel):
    work_title: str = Field(
        ...,
        description="Title of the work being claimed",
        example="Can't Touch This"
    )
    claim_type: str = Field(
        ...,
        description="Type of royalty claim",
        example="mechanical",
        pattern="^(mechanical|performance|sync|master)$"
    )
    amount_usd: float = Field(
        ...,
        description="Claim amount in USD",
        example=5000.00,
        gt=0
    )
```

## Priority Endpoint Checklist

### Tier 1: External API Surface (Public/Partner)
- [ ] POST /auth/login
- [ ] POST /auth/refresh
- [ ] GET /artists/{id}
- [ ] POST /artists
- [ ] POST /artists/{id}/statements/upload
- [ ] GET /artists/{id}/dashboard
- [ ] POST /connectors/webhook/ingest

### Tier 2: Core Artist Workflows
- [ ] POST /artists/{id}/claims
- [ ] GET /claims/{id}
- [ ] GET /artists/{id}/anomalies
- [ ] POST /artists/{id}/earnings/forecast
- [ ] GET /artists/{id}/earnings/summary

### Tier 3: Admin/Internal
- [ ] GET /admin/artists
- [ ] GET /admin/claims
- [ ] POST /admin/advances/run-nightly-eval
- [ ] GET /admin/ops/backup-report

### Tier 4: Advanced Features
- [ ] POST /artists/{id}/ml/catalog-valuation
- [ ] POST /artists/{id}/fingerprints/identify
- [ ] POST /artists/{id}/recovery/auto
- [ ] GET /artists/{id}/ugc/opportunities

## Automation Opportunities

### Generate Examples from Tests

Extract examples from existing integration tests:

```python
# tests/test_claims.py
def test_create_claim():
    response = client.post(
        "/artists/550e8400-e29b-41d4-a716-446655440000/claims",
        json={
            "work_title": "Test Song",
            "claim_type": "mechanical",
            "amount_usd": 1000.00
        }
    )
    assert response.status_code == 201
    # This payload can be extracted as an OpenAPI example
```

### Use OpenAPI Generator

Auto-generate client SDKs with rich examples:

```bash
openapi-generator generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-axios \
  -o sdk/typescript \
  --additional-properties=withSeparateModelsAndApi=true
```

## Best Practices

1. **Use Real Data:**  Use realistic artist names, claim amounts, and dates (not "foo", "test", "123")
2. **Include Edge Cases:** Show examples for both success and error scenarios
3. **Keep Examples Current:** Update examples when request/response schemas change
4. **Test Examples:** Validate that examples actually work with the endpoint
5. **Document Assumptions:** Note any prerequisites (e.g., "Artist must have at least one statement uploaded")

## References

- **FastAPI OpenAPI Docs:** https://fastapi.tiangolo.com/advanced/extending-openapi/
- **OpenAPI 3.1 Spec:** https://swagger.io/specification/
- **Current Implementation:** `XR7/api/routers/onboarding.py` (lines 180-250) - see `POST /artists/{id}/onboarding/auto`

## Rollout Plan

**Week 1:** Add examples to Tier 1 endpoints (7 endpoints)
**Week 2:** Add examples to Tier 2 endpoints (10 endpoints)
**Week 3:** Add examples to Tier 3 endpoints (15 endpoints)
**Ongoing:** Add examples to new endpoints as they're created

**Target:** 10% coverage (47 endpoints) by end of month 1
