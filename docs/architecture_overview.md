# XR7 Engine 2 Architecture Overview

> **Superseded by [`docs/architecture/`](architecture/README.md).**
> Start at [`docs/architecture/README.md`](architecture/README.md). The content below is retained for historical reference.

XR7 Engine 2 is a FastAPI + SQLAlchemy + Celery platform for artist royalty recovery.

## Core Layers
- API layer: request validation, auth checks, orchestration triggers, dashboard endpoints.
- Domain services: recovery, evidence, intelligence, ingestion, and payout logic.
- Persistence: PostgreSQL/SQLite via SQLAlchemy models and Alembic migrations.
- Queue/runtime: Celery workers for long-running and scheduled workflows.
- Agent orchestration: LangGraph-compatible stateful multi-agent execution.

## Recovery Lifecycle
1. Ingestion captures statement data or connector data.
2. Anomaly detection identifies underpayments/missing revenue.
3. Claims are drafted and evidence packets generated.
4. Negotiation and escalation execute policy-aware recovery.
5. Disbursement finalizes payout and records immutable ledger trail.
6. Calibration updates posterior performance metrics.

## Reliability + Safety
- Immutable ledger append for critical decisions.
- Confidence scoring and reflection loops for agent outputs.
- Human-in-the-loop interruption before escalation/disbursement.
- Celery retries with bounded backoff for resilient background processing.

## Runtime Components
- API app: XR7/api/app.py
- Agent state: XR7/agents/state.py
- Agent implementations: XR7/agents/onboarding_agents.py
- Orchestrator: XR7/agents/orchestrator.py
- Celery tasks: XR7/tasks/pipeline.py, XR7/tasks/celery_tasks.py
- Dashboard engine: XR7/earnings/dashboard.py
