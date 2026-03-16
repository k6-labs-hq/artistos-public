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
