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


def _ledger(db, artist_id: str, entry_type: str, payload: dict) -> None:
    ImmutableLedgerService(db).append(artist_id, entry_type, payload)


@celery_app.task(name="xr7.workflow.run_artist_workflow", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
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


@celery_app.task(name="xr7.workflow.run_nightly_preparation_scan", bind=True)
def run_nightly_preparation_scan(self=None) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        artist_ids = artists_pending_onboarding(db)
    finally:
        db.close()
    for artist_id in artist_ids:
        run_artist_workflow.delay(artist_id)
    return {"triggered": len(artist_ids), "scope": "nightly_preparation_scan", "agent": "onboarding_preparation"}


@celery_app.task(name="xr7.workflow.run_daily_recovery_scan", bind=True)
def run_daily_recovery_scan(self=None) -> dict:  # noqa: ANN001
    since = datetime.now(timezone.utc) - timedelta(hours=6)
    db = SessionLocal()
    try:
        artist_ids = artist_ids_with_new_statements(db, since)
    finally:
        db.close()
    for artist_id in artist_ids:
        run_artist_workflow.delay(artist_id)
    return {"triggered": len(artist_ids), "scope": "daily_recovery_scan", "agent": "recovery_execution"}


@celery_app.task(name="xr7.workflow.run_follow_up_and_readiness", bind=True)
def run_follow_up_and_readiness(self) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        artist_ids = all_artist_ids(db)
    finally:
        db.close()
    for artist_id in artist_ids:
        run_artist_workflow.delay(artist_id)
    return {"triggered": len(artist_ids), "scope": "follow_up_readiness"}


@celery_app.task(name="xr7.workflow.on_statement_upload", bind=True)
def on_statement_upload(self, artist_id: str) -> dict:  # noqa: ANN001
    run_artist_workflow.delay(artist_id)
    return {"artist_id": artist_id, "trigger": "statement_upload"}


@celery_app.task(name="xr7.workflow.on_ugc_fetch", bind=True)
def on_ugc_fetch(self, artist_id: str) -> dict:  # noqa: ANN001
    run_artist_workflow.delay(artist_id)
    return {"artist_id": artist_id, "trigger": "ugc_fetch"}


@celery_app.task(name="xr7.workflow.on_soundcloud_statement_upload", bind=True)
def on_soundcloud_statement_upload(self, artist_id: str, statement_id: str | None = None) -> dict:  # noqa: ANN001
    run_artist_workflow.delay(artist_id)
    return {
        "artist_id": artist_id,
        "statement_id": statement_id,
        "trigger": "soundcloud_statement_upload",
    }


@celery_app.task(name="xr7.workflow.run_soundcloud_sync_daily", bind=True)
def run_soundcloud_sync_daily(self) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        artist_ids = artist_ids_with_soundcloud_statements(db)
    finally:
        db.close()
    for artist_id in artist_ids:
        run_artist_workflow.delay(artist_id)
    return {"triggered": len(artist_ids), "scope": "soundcloud_daily_sync"}


@celery_app.task(name="xr7.workflow.run_soundcloud_healthcheck_hourly", bind=True)
def run_soundcloud_healthcheck_hourly(self) -> dict:  # noqa: ANN001
    since = datetime.now(timezone.utc) - timedelta(days=30)
    db = SessionLocal()
    try:
        artist_ids = active_soundcloud_artist_ids_since(db, since)
    finally:
        db.close()
    for artist_id in artist_ids:
        run_artist_workflow.delay(artist_id)
    return {"triggered": len(artist_ids), "scope": "soundcloud_hourly_healthcheck"}
