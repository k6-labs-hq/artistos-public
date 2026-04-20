# SDK Documentation Generation Guide

## Overview

This guide explains how to generate Python and TypeScript SDK documentation from the OpenAPI specification with real examplesvalues instead of TODO placeholders.

## Problem

SDK documentation previously contained ~100 Python and ~180 TypeScript placeholder TODOs like:

**Python:**
```python
# TODO update the JSON string below
json = "{}"
```

**TypeScript:**
```typescript
// TODO: Update the object below with actual values
const example = {
  "email": null,
  "password": null,
}
```

## Solution

### Prerequisites

**For Full SDK Regeneration:**
- Java JDK 8+ (required by openapi-generator-cli)
- OR Docker (alternative to Java)
- Node.js (for TypeScript SDK)
- Python 3.12+ (for Python SDK)

**For CI Checks Only:**
- Python 3.12+

### Step 1: Add Examples to OpenAPI Spec

Examples are automatically generated from schema field names and types using intelligent heuristics:

```bash
# Export fresh OpenAPI spec from FastAPI
python scripts/export_openapi.py

# Add realistic examples to all schemas
python scripts/add_openapi_examples.py
```

The `add_openapi_examples.py` script:
- Processes all 288+ schemas in the OpenAPI spec
- Generates contextual examples based on field names
  - `email` → `"artist@example.com"`
  - `artist_id` → `"art_2a1b3c4d5e6f"`
  - `created_at` → `"2026-04-16T10:30:00Z"`
  - `amount` → `1234.56`
- Adds both property-level and schema-level examples

### Step 2: Regenerate SDKs

**Unix/Linux/macOS:**
```bash
make sdks
```

**Windows (PowerShell):**
```powershell
# Python SDK
.\scripts\generate_sdk_python.ps1

# TypeScript SDK
.\scripts\generate_sdk_typescript.ps1

# Both SDKs
.\scripts\generate_sdks.ps1
```

**Manual (with Docker):**
```bash
# Python
docker run --rm \
  -v "$(pwd):/local" \
  openapitools/openapi-generator-cli generate \
  -i /local/openapi/openapi.json \
  -g python \
  -o /local/sdk/python \
  --additional-properties=packageName=xr7_sdk,projectName=xr7-python-sdk

# TypeScript
docker run --rm \
  -v "$(pwd):/local" \
  openapitools/openapi-generator-cli generate \
  -i /local/openapi/openapi.json \
  -g typescript-fetch \
  -o /local/sdk/typescript \
  --additional-properties=npmName=@xr7/sdk,npmVersion=2.0.0,supportsES6=true
```

### Step 3: Verify TODO Removal

```bash
# Run the CI check locally
python scripts/ci/check_sdk_todos.py

# Or via Make
make check-sdk-todos
```

Expected output when successful:
```
✅ No TODO placeholders found in SDK documentation!
```

## CI Integration

The SDK documentation quality check runs automatically on every PR:

**Workflow:** `.github/workflows/docs-consistency.yml`

**Job:** `sdk-docs-quality`

This ensures that SDK documentation always has real examples and never gets committed with TODO placeholders.

## Example Transformations

### Before (with TODOs):

**Python (`sdk/python/docs/AdminLoginRequest.md`):**
```python
# TODO update the JSON string below
json = "{}"
```

**TypeScript (`sdk/typescript/docs/AdminLoginRequest.md`):**
```typescript
// TODO: Update the object below with actual values
const example = {
  "email": null,
  "password": null,
}
```

### After (with real examples):

**Python:**
```python
from xr7_sdk.models.admin_login_request import AdminLoginRequest

json = '{"email": "artist@example.com", "password": "********"}'
admin_login_request_instance = AdminLoginRequest.from_json(json)
```

**TypeScript:**
```typescript
import type { AdminLoginRequest } from '@xr7/sdk'

const example = {
  "email": "artist@example.com",
  "password": "********",
} satisfies AdminLoginRequest
```

## Troubleshooting

### Java Not Found

If you see `'java' is not recognized...`:

1. Install Java JDK 8+: https://adoptium.net/
2. Or use Docker (no Java required)
3. Or use the provided PowerShell scripts with Docker fallback

### Docker Not Available

Install Docker Desktop:
- Windows: https://www.docker.com/products/docker-desktop
- macOS: https://www.docker.com/products/docker-desktop
- Linux: Use your package manager

### Verify Installation

```bash
# Check Java
java -version

# Check Docker
docker --version

# Check Python
python --version

# Check Node.js (for TypeScript SDK)
node --version
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/export_openapi.py` | Export OpenAPI spec from FastAPI app |
| `scripts/add_openapi_examples.py` | Add realistic examples to all schemas |
| `scripts/generate_sdk_python.sh` | Generate Python SDK (Unix) |
| `scripts/generate_sdk_typescript.sh` | Generate TypeScript SDK (Unix) |
| `scripts/generate_sdks.sh` | Generate both SDKs (Unix) |
| `scripts/generate_sdk_python.ps1` | Generate Python SDK (Windows) |
| `scripts/generate_sdk_typescript.ps1` | Generate TypeScript SDK (Windows) |
| `scripts/generate_sdks.ps1` | Generate both SDKs (Windows) |
| `scripts/ci/check_sdk_todos.py` | CI check for TODO placeholders |

## Maintenance

### Adding Examples to New Models

The example generation is automatic. When you add new Pydantic models:

1. Just regenerate the OpenAPI spec: `python scripts/export_openapi.py`
2. Add examples: `python scripts/add_openapi_examples.py`
3. Regenerate SDKs: `make sdks` (or Windows equivalent)

### Custom Examples

To override auto-generated examples for specific schemas, add examples directly to your Pydantic models:

```python
from pydantic import BaseModel, Field

class AdminLoginRequest(BaseModel):
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "admin@xr7.example.com",
                "password": "SuperSecurePassword123!"
            }
        }
    }

    email: str = Field(example="admin@xr7.example.com")
    password: str = Field(example="SuperSecurePassword123!")
```

Then regenerate the OpenAPI spec and SDKs.

## Related Documentation

- [OpenAPI Specification](../openapi/openapi.json)
- [API Reference Documentation](../docs/api/reference.md)
- [OpenAPI Maintenance Guide](../docs/openapi_maintenance_guide.md)
- [CI/CD Pipeline Reference](../docs/cicd_pipeline_reference.md)
