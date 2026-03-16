# Developer Onboarding Guide

## Local Setup
1. Copy .env.example to .env and configure local values.
2. Create and activate virtualenv.
3. Install requirements.
4. Run migrations if required.
5. Start API and worker.

## Run Commands
- API: uvicorn XR7.api.app:app --reload
- Worker: celery -A XR7.celery_app.celery_app worker -l info
- Beat: celery -A XR7.celery_app.celery_app beat -l info
- Tests: pytest -q

## Branding Contract (Required)

- Any non-admin endpoint returning a top-level dict with `artist_id` or `org_id` must include top-level `branding` metadata.
- Preferred implementation: wrap payloads with `inject_branding_metadata(db, payload)`.
- Direct `branding_metadata(...)` is acceptable where explicit brand objects are already present.

## Branding Performance + Observability

- Branding resolution uses request-scoped caching via SQLAlchemy `Session.info` in `XR7/services/branding.py`.
- This avoids repeated profile and artist-org lookups in a single API request path.
- Branding observability counters/logs are available through:
	- `branding_observability_snapshot()`
	- `reset_branding_observability()`

## CI Guardrails

- Branding contract checks run in GitHub Actions via `.github/workflows/branding-contract.yml`.
- Local equivalent:
	- `pytest -q tests/test_branding.py tests/test_branding_contract_guard.py tests/test_branding_service.py`
- The guard test statically scans router endpoints and fails when identity payloads miss branding injection.

## Add a New Agent
1. Implement async agent in XR7/agents/onboarding_agents.py.
2. Update typed state in XR7/agents/state.py.
3. Register in XR7/agents/orchestrator.py AGENTS map.
4. Add routing logic and reflection behavior.
5. Add tests and dashboard field mapping if surfaced.

## Extend Orchestrator
- Add node function.
- Add conditional edge path from supervisor.
- Add reflection/interrupt behavior for risk-sensitive steps.

## Add Ingestion Format
1. Extend parser logic in ingestion parser modules.
2. Register format metadata for supported formats endpoint.
3. Add tests for positive and fallback parsing behavior.

## Add Dashboard Field
1. Compute value in earnings dashboard engine or orchestrator state.
2. Merge value in dashboard router response.
3. Document field in dashboard_schema_reference.md.
4. Add API tests.
