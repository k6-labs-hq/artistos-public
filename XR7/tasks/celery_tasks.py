from __future__ import annotations

from datetime import datetime, timedelta, timezone

from XR7.agents.orchestrator import run_xr7_recovery_orchestra_sync
from XR7.celery_app import celery_app
from XR7.models.artist import Artist, ArtistLifecycleStatus
from XR7.models.base import SessionLocal
from XR7.models.statement import Statement
from XR7.recovery.immutable_ledger import ImmutableLedgerService
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
    db = SessionLocal()
    try:
        artists = db.query(Artist).filter(Artist.status != ArtistLifecycleStatus.ACTIVE.value).all()
        triggered = 0
        for artist in artists:
            run_artist_workflow.delay(artist.id)
            triggered += 1
        return {"triggered": triggered, "scope": "incomplete_onboarding"}
    finally:
        db.close()


@celery_app.task(name="xr7.workflow.run_recovery_for_new_data", bind=True)
def run_recovery_for_new_data(self) -> dict:  # noqa: ANN001
    threshold = datetime.now(timezone.utc) - timedelta(hours=6)
    db = SessionLocal()
    try:
        rows = db.query(Statement).filter(Statement.uploaded_at >= threshold).all()
        artist_ids = sorted({r.artist_id for r in rows})
        for artist_id in artist_ids:
            run_artist_workflow.delay(artist_id)
        return {"triggered": len(artist_ids), "scope": "new_statements"}
    finally:
        db.close()


@celery_app.task(name="xr7.workflow.run_follow_up_and_readiness", bind=True)
def run_follow_up_and_readiness(self) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        artist_ids = [a.id for a in db.query(Artist.id).all()]
        for artist_id in artist_ids:
            run_artist_workflow.delay(artist_id)
        return {"triggered": len(artist_ids), "scope": "follow_up_readiness"}
    finally:
        db.close()


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
        rows = db.query(Statement).filter(Statement.format_detected == "soundcloud").all()
        artist_ids = sorted({r.artist_id for r in rows})
        for artist_id in artist_ids:
            run_artist_workflow.delay(artist_id)
        return {"triggered": len(artist_ids), "scope": "soundcloud_daily_sync"}
    finally:
        db.close()


@celery_app.task(name="xr7.workflow.run_soundcloud_healthcheck_hourly", bind=True)
def run_soundcloud_healthcheck_hourly(self) -> dict:  # noqa: ANN001
    db = SessionLocal()
    try:
        threshold = datetime.now(timezone.utc) - timedelta(days=30)
        rows = db.query(Statement).filter(Statement.format_detected == "soundcloud", Statement.uploaded_at >= threshold).all()
        artist_ids = sorted({r.artist_id for r in rows})
        for artist_id in artist_ids:
            run_artist_workflow.delay(artist_id)
        return {"triggered": len(artist_ids), "scope": "soundcloud_hourly_healthcheck"}
    finally:
        db.close()
