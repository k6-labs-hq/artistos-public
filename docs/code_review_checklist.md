# XR7 Senior Engineer Code Review Checklist

**Version:** 2.0  
**Use:** Apply to every PR before approving. All CRITICAL items are blockers.

Copy this checklist into the PR review or use it as a mental model when reviewing.

---

## Section 1: Architecture & Domain Boundaries

> **Reference:** [handbook.md §A.3](handbook.md#a3-layer-boundaries-critical),  
> `scripts/check_domain_boundaries.py`

| # | Check | Severity |
|---|-------|----------|
| 1.1 | `XR7/core/` files have **no imports** from `XR7.services`, `XR7.api`, `XR7.recovery`, or `sqlalchemy` | **CRITICAL** |
| 1.2 | `shared/utils/` files have **no imports** from `XR7.*` (zero-dep utilities) | **CRITICAL** |
| 1.3 | `XR7/api/routers/` files do **not call** `db.query()` or `db.execute()` directly (ORM stays in services) | **CRITICAL** |
| 1.4 | New business logic is placed in `XR7/services/` or `XR7/core/`, not inlined in router functions | HIGH |
| 1.5 | `XR7/ml/` does not import from `XR7/recovery/` or `XR7/blockchain/` | HIGH |
| 1.6 | Any new utility function that is reusable and stateless is placed in `shared/utils/` | MEDIUM |

---

## Section 2: Naming Conventions

> **Reference:** [handbook.md §B.1](handbook.md#b1-naming-conventions),  
> `scripts/check_naming_conventions.py`

| # | Check | Severity |
|---|-------|----------|
| 2.1 | No `track_title` in non-parser code — use `work_title` | **CRITICAL** |
| 2.2 | No `track_count` in non-parser code — use `work_count` | **CRITICAL** |
| 2.3 | No `song_id` or `song_title` in internal field names — use `isrc` / `work_title` | **CRITICAL** |
| 2.4 | No `"entity": "track"` or `"entity": "song"` literals in XR7 source — use `"entity": "recording"` | **CRITICAL** |
| 2.5 | Royalty type values use specific forms: `master_sync` or `pub_sync`, not bare `sync` | HIGH |
| 2.6 | New Pydantic models follow the `<Action><Resource>Request` / `<Resource>Response` naming pattern | MEDIUM |
| 2.7 | Parser/adapter files that read external DSP data are the ONLY exception to naming rules — verify the exception is warranted | MEDIUM |

---

## Section 3: Authentication & Authorization

> **Reference:** [docs/api/authentication.md](api/authentication.md)

| # | Check | Severity |
|---|-------|----------|
| 3.1 | Every new endpoint has `Depends(get_current_user)` unless explicitly and intentionally public | **CRITICAL** |
| 3.2 | Intentionally public endpoints are documented with a comment explaining why they are public | HIGH |
| 3.3 | `tenant_id` is extracted from JWT claims (via `get_current_user`), never from the request body | **CRITICAL** |
| 3.4 | Admin-only endpoints check for `role == "admin"` or use the `require_admin` dependency | **CRITICAL** |
| 3.5 | Analyst endpoints check for `role in ("admin", "analyst")` | HIGH |
| 3.6 | No hardcoded credentials, API keys, or secrets in code or tests | **CRITICAL** |

---

## Section 4: Test Coverage

> **Reference:** [handbook.md §B.8](handbook.md#b8-test-requirements)

| # | Check | Severity |
|---|-------|----------|
| 4.1 | Every new endpoint has at least one test for the happy path (200/201) | **CRITICAL** |
| 4.2 | Every new endpoint has a test for the unauthenticated case (401) | **CRITICAL** |
| 4.3 | Every new endpoint has a test for invalid input (422) | HIGH |
| 4.4 | Relevant business-rule failures are tested (404, 409, 400) | HIGH |
| 4.5 | New `XR7/core/` functions are covered at >= 95% | HIGH |
| 4.6 | New `shared/utils/` functions are covered at >= 95% | HIGH |
| 4.7 | Tests use test fixtures / mocked DB — not production data or hardcoded IDs | **CRITICAL** |
| 4.8 | CI coverage threshold (60% overall) still passes after this PR | HIGH |

---

## Section 5: Data Integrity & Tenant Isolation

| # | Check | Severity |
|---|-------|----------|
| 5.1 | Every ORM query in services includes `WHERE tenant_id = ?` | **CRITICAL** |
| 5.2 | No raw SQL strings with user-controllable input (use parameterised queries / SQLAlchemy constructs only) | **CRITICAL** |
| 5.3 | Cross-tenant resource access is impossible via the new code paths (verify by reading the service function) | **CRITICAL** |
| 5.4 | Pydantic models validate and constrain user input at system boundaries (e.g., ISRC regex, date ranges) | HIGH |
| 5.5 | Numeric fields use `Decimal` / `Numeric(12, 2)` not `float` for financial values | HIGH |

---

## Section 6: Claims State Machine

> **Reference:** [claims_state_machine.md](claims_state_machine.md)

| # | Check | Severity |
|---|-------|----------|
| 6.1 | Any code that transitions a claim state uses `XR7/core/claims_state_machine.py` — no ad-hoc state setting | **CRITICAL** |
| 6.2 | Invalid transitions raise `ClaimTransitionError`, not `ValueError` or silent failures | HIGH |
| 6.3 | Tests cover all expected state transitions for new claim logic | HIGH |
| 6.4 | Evidence packets are sealed before a claim can move to `SUBMITTED` | HIGH |

---

## Section 7: Type Safety

> **Reference:** [handbook.md §B.2](handbook.md#b2-type-annotations)

| # | Check | Severity |
|---|-------|----------|
| 7.1 | All new functions have full type annotations (parameters + return type) | HIGH |
| 7.2 | No `Any` types in `XR7/core/` or `shared/utils/` — these are mypy-strict zones | HIGH |
| 7.3 | Pydantic model fields use constrained types where appropriate (`Field(ge=0)`, `Field(pattern=...)`) | MEDIUM |
| 7.4 | No `# type: ignore` comments without a documented justification | MEDIUM |

---

## Section 8: Error Handling & Observability

> **Reference:** [docs/api/errors.md](api/errors.md)

| # | Check | Severity |
|---|-------|----------|
| 8.1 | Errors use the standard `ErrorResponse` envelope (`error`, `message`, `request_id`) | HIGH |
| 8.2 | HTTP status codes are appropriate — 404 for not found, 409 for conflict, not generic 400 for everything | MEDIUM |
| 8.3 | Log statements do NOT contain PII (names, emails, bank details, addresses) — only IDs | **CRITICAL** |
| 8.4 | Log statements include structured extras (`extra={...}`) with `tenant_id`, relevant IDs, and operation name | MEDIUM |
| 8.5 | `try/except` is only at system boundaries (router entry, Celery task entry) — not wrapping every call | MEDIUM |
| 8.6 | Every caught exception logs enough context to reconstruct what happened | HIGH |

---

## Section 9: OpenAPI & API Contract

> **Reference:** [docs/api/adding-endpoints.md](api/adding-endpoints.md)

| # | Check | Severity |
|---|-------|----------|
| 9.1 | New endpoints have `response_model=`, `summary=`, and `responses=` (non-2xx codes documented) | HIGH |
| 9.2 | `openapi/openapi.json` is regenerated and committed if endpoints were added/changed | HIGH |
| 9.3 | The relevant `docs/api/*.md` file is updated to document new endpoints | MEDIUM |
| 9.4 | No breaking changes to existing response shapes without a version increment discussion | HIGH |

---

## Section 10: Database & Migrations

> **Reference:** [xr7_database_migration_rollout_plan.md](xr7_database_migration_rollout_plan.md)

| # | Check | Severity |
|---|-------|----------|
| 10.1 | Any schema change has an Alembic migration file | **CRITICAL** |
| 10.2 | The migration file has a working `downgrade()` function | HIGH |
| 10.3 | Column renames use multi-step migration (add → backfill → remove) to avoid downtime | HIGH |
| 10.4 | New columns that are NOT NULL have a `server_default` or are added in a two-step migration | HIGH |
| 10.5 | Indexes are added for new foreign keys and commonly-queried filter columns | MEDIUM |
| 10.6 | `mapped_column()` `Mapped[T]` style is used — not `Column()` (SQLAlchemy 2.0 standard) | MEDIUM |

---

## Section 11: Performance

| # | Check | Severity |
|---|-------|----------|
| 11.1 | No N+1 query patterns — collections loaded with `selectinload()` or `joinedload()`, not iterated lazy-loading | HIGH |
| 11.2 | Expensive operations (evidence generation, ML scoring) are enqueued as Celery tasks, not run inline in a request | HIGH |
| 11.3 | Pagination is implemented on any endpoint that returns a collection (`page` + `page_size` params, max 200) | HIGH |
| 11.4 | No synchronous blocking calls inside `async def` functions (use `asyncio.to_thread()` if needed) | HIGH |

---

## Section 12: Security (OWASP Top 10 Alignment)

| # | Check | OWASP | Severity |
|---|-------|-------|----------|
| 12.1 | All user input is validated before being used in queries or external calls | A03: Injection | **CRITICAL** |
| 12.2 | No `subprocess` with user-controlled strings | A03: Injection | **CRITICAL** |
| 12.3 | No MD5 or SHA1 for security-sensitive hashing (use SHA256 minimum) | A02: Crypto Failures | **CRITICAL** |
| 12.4 | HMAC signatures are verified with `hmac.compare_digest()` (timing-safe) | A02: Crypto Failures | **CRITICAL** |
| 12.5 | `assert` is not used for security checks (disabled in optimised Python) | A05: Misconfiguration | HIGH |
| 12.6 | Error messages do not leak internal implementation details to API consumers | A01: Broken Access Control | HIGH |
| 12.7 | Dependencies added via `pip install` are pinned to a specific version in `requirements.txt` | A06: Vulnerable Components | HIGH |
| 12.8 | File uploads (if any) validate MIME type and size limits | A04: Insecure Design | HIGH |

---

## Section 13: n8n Compatibility

> Only applies to PRs that modify workflow-triggered endpoints or async job endpoints.

| # | Check | Severity |
|---|-------|----------|
| 13.1 | Job-triggering endpoints return `{job_id, status: "queued"}` consistently | HIGH |
| 13.2 | `GET /jobs/{job_id}/status` returns `{status: "running" | "completed" | "failed", error?: ...}` | HIGH |
| 13.3 | Webhook endpoints validate `X-XR7-Signature` before processing the payload | HIGH |
| 13.4 | Long-running operations do not block — they enqueue and return immediately | HIGH |

---

## Quick Approval Decision Tree

```
Are all CRITICAL items ✅?  →  NO  →  Request changes (block merge)
       ↓ YES
Are all HIGH items ✅?       →  NO  →  Comment + request fix in this PR (usually block)
       ↓ YES
Are MEDIUM items noted?      →  NO  →  Leave comments for follow-up (do not block)
       ↓ YES
                            →  APPROVE
```

---

## Reviewer Sign-off Template

Copy into the PR review comment when approving:

```
## Code Review Sign-off

Reviewed against XR7 Senior Engineer Checklist v2.0

- [ ] Architecture boundaries — PASS / N/A
- [ ] Naming conventions — PASS / N/A
- [ ] Auth & tenant isolation — PASS / N/A
- [ ] Test coverage — PASS (coverage check: ___)
- [ ] Data integrity — PASS / N/A
- [ ] Claims state machine — PASS / N/A
- [ ] Type safety — PASS / N/A
- [ ] Error handling & logging — PASS / N/A
- [ ] OpenAPI contract — PASS / N/A
- [ ] DB migrations — PASS / N/A
- [ ] Performance — PASS / N/A
- [ ] Security — PASS / N/A
- [ ] n8n compatibility — PASS / N/A

Notes: ___

✅ Approved
```
