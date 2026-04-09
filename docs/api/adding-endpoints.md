# How to Add a New API Endpoint

This guide covers the complete workflow for adding a new endpoint to the XR7 API, from router creation through OpenAPI documentation.

---

## Step-by-Step Checklist

### 1. Determine the domain

Identify which domain the endpoint belongs to:

| Domain | Module | Notes |
|--------|--------|-------|
| Artist portal | `XR7/api/routers/artists/` | Largest domain — 260+ routes |
| Claims/evidence | `XR7/api/routers/claims.py` | Claim state machine aware |
| Admin | `XR7/api/routers/admin/` | Requires admin role check |
| TV/Film | `XR7/api/routers/tvfilm.py` | |
| Auth | `XR7/api/routers/auth.py` | |

If no existing domain fits, create a new router file and register it in `XR7/api/app.py`.

---

### 2. Write the Pydantic schemas

Add request and response schemas in the appropriate `XR7/schemas/` file (or `XR7/api/schemas/`):

```python
# XR7/schemas/my_domain.py
from pydantic import BaseModel, Field
from datetime import datetime

class MyResourceRequest(BaseModel):
    """Request body for creating a MyResource."""
    name: str = Field(..., min_length=1, max_length=200)
    isrc: str | None = Field(None, pattern=r"^[A-Z]{2}[A-Z0-9]{3}[0-9]{7}$")

class MyResourceResponse(BaseModel):
    """Response for a MyResource."""
    resource_id: str
    name: str
    created_at: datetime
```

**Naming conventions:**
- Request bodies: `<Action><Resource>Request` (e.g., `CreateClaimRequest`)
- Responses: `<Resource>Response` (e.g., `ClaimResponse`)
- Lists: `<Resource>ListResponse` (e.g., `ClaimListResponse`)
- Do NOT use `track_title`, `song_id`. Use `work_title`, `isrc`. See [naming standards](../developer_onboarding.md).

---

### 3. Write the service function

Business logic lives in `XR7/services/`, not in the router:

```python
# XR7/services/my_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from XR7.schemas.my_domain import MyResourceRequest, MyResourceResponse

async def create_my_resource(
    db: AsyncSession,
    request: MyResourceRequest,
    tenant_id: str,
) -> MyResourceResponse:
    # ... implementation
    pass
```

**Boundary rules:**
- Services may import from `XR7.core`, `shared.utils`, `sqlalchemy`
- Services must NOT import from `XR7.api`
- Core functions (`XR7/core/`) must NOT import from services or SQLAlchemy

---

### 4. Write the router endpoint

```python
# XR7/api/routers/my_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from XR7.api.dependencies import get_db, get_current_user
from XR7.schemas.my_domain import MyResourceRequest, MyResourceResponse
from XR7.services.my_service import create_my_resource

router = APIRouter(prefix="/my-resources", tags=["my-resources"])

@router.post(
    "/",
    response_model=MyResourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a MyResource",
    description="Creates a new MyResource for the authenticated user's tenant.",
    responses={
        409: {"description": "Duplicate resource"},
        422: {"description": "Validation error"},
    },
)
async def create(
    body: MyResourceRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> MyResourceResponse:
    return await create_my_resource(db, body, current_user.tenant_id)
```

**Required for every endpoint:**
- `response_model=` — type the response
- `summary=` — one-line description (appears in Swagger UI)
- `responses=` — document all non-2xx codes
- Auth dependency (`Depends(get_current_user)`) unless the endpoint is intentionally public

---

### 5. Register the router

In `XR7/api/app.py`:

```python
from XR7.api.routers.my_router import router as my_router

app.include_router(my_router)
```

---

### 6. Write tests

Create `tests/test_api_my_resources.py`:

```python
import pytest
from httpx import AsyncClient
from XR7.api.app import app

@pytest.mark.asyncio
async def test_create_my_resource_success(auth_headers):
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.post(
            "/my-resources/",
            json={"name": "Test Resource"},
            headers=auth_headers,
        )
    assert r.status_code == 201
    assert r.json()["name"] == "Test Resource"

@pytest.mark.asyncio
async def test_create_my_resource_unauthenticated():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = await client.post("/my-resources/", json={"name": "Test"})
    assert r.status_code == 401
```

Minimum required test cases:
- Happy path (201/200)
- Unauthenticated (401)
- Invalid request body (422)
- Relevant business rule failures (400, 409)

---

### 7. Update the OpenAPI spec

The OpenAPI spec (`openapi/openapi.json`) is auto-generated from FastAPI. After adding a new endpoint:

```bash
python -c "
import json
from XR7.api.app import app
with open('openapi/openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)
print('openapi.json regenerated')
"
```

Then commit the updated `openapi/openapi.json`.

---

### 8. Add API documentation

Add an entry to the appropriate file in `docs/api/` following the format used in [claims.md](claims.md):

```markdown
### `POST /my-resources`

Brief description.

**Auth:** Bearer  
**Request body** — `MyResourceRequest`:
...
**Response 201** — `MyResourceResponse`:
...
```

---

## Common Mistakes

| Mistake | Correct pattern |
|---------|----------------|
| ORM query in router (`db.query(...)`) | Move to service layer |
| `track_title` field name | Use `work_title` |
| Missing `response_model=` | Always specify response type |
| No 401 test | Always test unauthenticated access |
| Business logic in schema validators | Move to service function |
| Import from `XR7.api` inside `XR7.core` | Only services/api can import core, not vice versa |
