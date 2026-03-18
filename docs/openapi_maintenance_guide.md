# OpenAPI Maintenance Guide

This guide defines how XR7 API contracts are changed, validated, and published safely.

## Source of Truth

- API route implementations under XR7/api/routers.
- Generated contract under openapi/openapi.json.
- Human-readable API docs under docs/api/reference.md and domain docs.

## Contract Change Workflow

1) Update route handlers and Pydantic request and response schemas.
2) Regenerate OpenAPI JSON using project scripts.
3) Regenerate API reference docs from OpenAPI.
4) Run contract diff review and backward-compatibility checks.
5) Update SDKs for Python and TypeScript.

## Required Commands

Generate OpenAPI and docs:

```bash
python scripts/export_openapi.py
python scripts/generate_api_reference.py
```

Generate SDKs:

```bash
make sdks
```

Validation check for accidental drift:

```bash
git diff --exit-code -- openapi/openapi.json docs/api/reference.md
```

## Backward Compatibility Rules

- Additive changes are preferred.
- Do not remove or rename existing fields without deprecation window.
- Do not change field types for existing stable schemas.
- New required request fields require versioning or safe defaults.

## Operation Design Standards

- Every write endpoint should support idempotency strategy.
- Every async endpoint should return job metadata.
- Every AI-influenced endpoint should expose explainability references.
- Error models should include machine-readable code and request_id.

## Release Checklist

- OpenAPI JSON regenerated and committed.
- API reference regenerated and committed.
- SDK generation completed and passing smoke tests.
- Changelog entry added for new/changed operations.
- Contract consumer review completed (frontend, partner, support).

## XR7 Enhanced Contract References

- docs/xr7_api_contract_diffs_and_scaffolds.md
- docs/xr7_master_specification_2026_2027.md
