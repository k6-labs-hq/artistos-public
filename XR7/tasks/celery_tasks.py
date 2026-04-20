from __future__ import annotations

from datetime import datetime, timedelta, timezone

from XR7.agents.orchestrator import run_xr7_recovery_orchestra_sync
from XR7.celery_app import celery_app
from XR7.models.base import SessionLocal
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from XR7.services.artist_query import (
    active_soundcloud_artist_ids_since,
    all_artist_ids,
    artist_ids_with_new_statements,
    artist_ids_with_soundcloud_statements,
    artists_pending_onboarding,
)
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Shared retry / failure configuration
# ---------------------------------------------------------------------------
# All schedule-triggered scan tasks use these defaults so they are:
#  - retried up to 3 times with exponential backoff (2s → 4s → 8s)
#  - routed to a dead-letter queue via Celery's built-in task_reject_on_worker_lost
#    and a dedicated "failed_tasks" queue configured in celery_app.py
#  - logged (and optionally alerted) by _on_task_failure when all retries are exhausted.
_SCAN_RETRY_KWARGS = {
    "autoretry_for": (Exception,),
    "retry_backoff": 2,  # base delay in seconds; doubles each retry
    "retry_backoff_max": 60,  # cap at 60 s
    "retry_jitter": True,  # randomise ±50 % to avoid thundering herd
    "max_retries": 3,
}


def _on_task_failure(task_name: str, exc: Exception, task_id: str) -> None:
    """Called after all retries are exhausted.  Logs a CRITICAL message so it
    surfaces in any log-aggregation alert rule (e.g., CloudWatch / Sentry).
    Replace the body to integrate with your alerting backend (PagerDuty, etc.).
    """
    logger.critical(
        "celery.task.permanent_failure",
        extra={
            "task": task_name,
            "task_id": task_id,
            "exc_type": type(exc).__name__,
            "exc_msg": str(exc),
        },
    )


def _ledger(db, artist_id: str, entry_type: str, payload: dict) -> None:
    ImmutableLedgerService(db).append(artist_id, entry_type, payload)


@celery_app.task(
    name="xr7.workflow.run_artist_workflow",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def run_artist_workflow(self, artist_id: str, run_id: str | None = None) -> dict:  # noqa: ANN001
    state = run_xr7_recovery_orchestra_sync(artist_id, run_id)
    db = SessionLocal()
    try:
        _ledger(
            db,
            artist_id,
            "workflow_run_complete",
            {
                "run_id": state.get("run_id"),
                "current_step": state.get("current_step"),
                "final_payout": state.get("final_payout"),
            },
        )
    finally:
        db.close()
    return {
        "artist_id": artist_id,
        "run_id": state.get("run_id"),
        "status": "completed",
        "current_step": state.get("current_step"),
    }


@celery_app.task(name="xr7.workflow.run_onboarding_for_incomplete_artists", bind=True)
def run_onboarding_for_incomplete_artists(self) -> dict:  # noqa: ANN001
    # Backward-compatible alias to the new two-agent schedule task.
    return run_nightly_preparation_scan()


@celery_app.task(name="xr7.workflow.run_recovery_for_new_data", bind=True)
def run_recovery_for_new_data(self) -> dict:  # noqa: ANN001
    # Backward-compatible alias to the new two-agent schedule task.
    return run_daily_recovery_scan()


@celery_app.task(
    name="xr7.workflow.run_nightly_preparation_scan",
    bind=True,
    **_SCAN_RETRY_KWARGS,
)
def run_nightly_preparation_scan(self, *_args) -> dict:  # noqa: ANN001
    try:
        db = SessionLocal()
        try:
            artist_ids = artists_pending_onboarding(db)
        finally:
            db.close()
        for artist_id in artist_ids:
            run_artist_workflow.delay(artist_id)
        return {
            "triggered": len(artist_ids),
            "scope": "nightly_preparation_scan",
            "agent": "onboarding_preparation",
        }
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            _on_task_failure(self.name, exc, self.request.id or "")
        raise


@celery_app.task(
    name="xr7.workflow.run_daily_recovery_scan",
    bind=True,
    **_SCAN_RETRY_KWARGS,
)
def run_daily_recovery_scan(self, *_args) -> dict:  # noqa: ANN001
    try:
        since = datetime.now(timezone.utc) - timedelta(hours=6)
        db = SessionLocal()
        try:
            artist_ids = artist_ids_with_new_statements(db, since)
        finally:
            db.close()
        for artist_id in artist_ids:
            run_artist_workflow.delay(artist_id)
        return {
            "triggered": len(artist_ids),
            "scope": "daily_recovery_scan",
            "agent": "recovery_execution",
        }
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            _on_task_failure(self.name, exc, self.request.id or "")
        raise


@celery_app.task(
    name="xr7.workflow.run_follow_up_and_readiness",
    bind=True,
    **_SCAN_RETRY_KWARGS,
)
def run_follow_up_and_readiness(self) -> dict:  # noqa: ANN001
    try:
        db = SessionLocal()
        try:
            artist_ids = all_artist_ids(db)
        finally:
            db.close()
        for artist_id in artist_ids:
            run_artist_workflow.delay(artist_id)
        return {"triggered": len(artist_ids), "scope": "follow_up_readiness"}
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            _on_task_failure(self.name, exc, self.request.id or "")
        raise


@celery_app.task(name="xr7.workflow.on_statement_upload", bind=True)
def on_statement_upload(self, artist_id: str) -> dict:  # noqa: ANN001
    run_artist_workflow.delay(artist_id)
    return {"artist_id": artist_id, "trigger": "statement_upload"}


@celery_app.task(name="xr7.workflow.on_ugc_fetch", bind=True)
def on_ugc_fetch(self, artist_id: str) -> dict:  # noqa: ANN001
    run_artist_workflow.delay(artist_id)
    return {"artist_id": artist_id, "trigger": "ugc_fetch"}


@celery_app.task(name="xr7.workflow.on_soundcloud_statement_upload", bind=True)
def on_soundcloud_statement_upload(
    self, artist_id: str, statement_id: str | None = None
) -> dict:  # noqa: ANN001
    run_artist_workflow.delay(artist_id)
    return {
        "artist_id": artist_id,
        "statement_id": statement_id,
        "trigger": "soundcloud_statement_upload",
    }


@celery_app.task(
    name="xr7.workflow.run_soundcloud_sync_daily",
    bind=True,
    **_SCAN_RETRY_KWARGS,
)
def run_soundcloud_sync_daily(self) -> dict:  # noqa: ANN001
    try:
        db = SessionLocal()
        try:
            artist_ids = artist_ids_with_soundcloud_statements(db)
        finally:
            db.close()
        for artist_id in artist_ids:
            run_artist_workflow.delay(artist_id)
        return {"triggered": len(artist_ids), "scope": "soundcloud_daily_sync"}
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            _on_task_failure(self.name, exc, self.request.id or "")
        raise


@celery_app.task(
    name="xr7.workflow.run_soundcloud_healthcheck_hourly",
    bind=True,
    **_SCAN_RETRY_KWARGS,
)
def run_soundcloud_healthcheck_hourly(self) -> dict:  # noqa: ANN001
    try:
        since = datetime.now(timezone.utc) - timedelta(days=30)
        db = SessionLocal()
        try:
            artist_ids = active_soundcloud_artist_ids_since(db, since)
        finally:
            db.close()
        for artist_id in artist_ids:
            run_artist_workflow.delay(artist_id)
        return {"triggered": len(artist_ids), "scope": "soundcloud_hourly_healthcheck"}
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            _on_task_failure(self.name, exc, self.request.id or "")
        raise
