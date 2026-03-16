# Celery Workflows and Schedules

## Core Runtime
- Broker/backend configured via CELERY_BROKER_URL and CELERY_RESULT_BACKEND.
- Task registration via XR7.tasks package import side effects.

## Workflow Tasks
- xr7.workflow.run_artist_workflow
- xr7.workflow.run_onboarding_for_incomplete_artists
- xr7.workflow.run_recovery_for_new_data
- xr7.workflow.run_follow_up_and_readiness
- xr7.workflow.on_statement_upload
- xr7.workflow.on_ugc_fetch

## Beat Schedule
- Every 6 hours:
  - run_onboarding_for_incomplete_artists
  - run_recovery_for_new_data
- Every 24 hours:
  - run_follow_up_and_readiness

## Event Triggers
- Statement upload event enqueues autonomous workflow run.
- UGC fetch event enqueues autonomous workflow run.

## Reliability
- Retries for run_artist_workflow with bounded backoff.
- Immutable ledger append on workflow completion.
