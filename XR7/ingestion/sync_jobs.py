from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

from XR7.ingestion.fetchers import get_fetcher
from XR7.models.base import SessionLocal
from XR7.models.sync_job import SyncJob
from xr7_common.logging import get_logger

logger = get_logger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def run_sync_job_with_session(db, job_id: str) -> None:
    job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
    if not job:
        return
    if job.status == "COMPLETED":
        return

    job.status = "RUNNING"
    job.attempts = int(job.attempts or 0) + 1
    job.started_at = _now()
    job.updated_at = _now()
    db.commit()

    try:
        fetcher = get_fetcher(job.integration)
        bundle = fetcher.fetch_all(job.artist_id)
        result = {
            "historical_count": len(bundle.historical_statements),
            "catalog_count": len(bundle.catalog_metadata),
            "registration_count": len(bundle.registrations),
            "usage_count": len(bundle.usage_data),
            "normalized_count": len(bundle.normalized_events),
        }
        job.status = "COMPLETED"
        job.result_json = json.dumps(result, sort_keys=True)
        job.completed_at = _now()
        job.last_error = None
        job.next_run_at = None
        job.updated_at = _now()
        db.commit()
    except Exception as exc:  # noqa: BLE001
        job.last_error = str(exc)
        if job.attempts < job.max_attempts:
            job.status = "RETRYING"
            delay_minutes = min(30, 2 ** max(0, job.attempts - 1))
            job.next_run_at = _now() + timedelta(minutes=delay_minutes)
        else:
            job.status = "FAILED"
            job.completed_at = _now()
            job.next_run_at = None
        job.updated_at = _now()
        db.commit()


def _enqueue_celery(job_id: str) -> str | None:
    try:
        from XR7.tasks.sync_jobs import run_sync_job_task

        task = run_sync_job_task.delay(job_id)
        return task.id
    except Exception:  # noqa: BLE001
        logger.exception("Failed to enqueue sync job to Celery", extra={"job_id": job_id})
        return None


def enqueue_sync_job(job_id: str, *, queue_backend: str = "background", db=None) -> dict:
    queue_backend = (queue_backend or "background").strip().lower()
    if queue_backend not in {"inline", "background", "celery"}:
        queue_backend = "background"

    if queue_backend == "inline":
        run_sync_job(job_id)
        return {"mode": "inline", "enqueued": False, "task_id": None}

    if queue_backend == "celery":
        task_id = _enqueue_celery(job_id)
        if task_id:
            local_db = db or SessionLocal()
            try:
                row = local_db.query(SyncJob).filter(SyncJob.id == job_id).first()
                if row:
                    row.queue_backend = "celery"
                    row.last_task_id = task_id
                    row.enqueued_at = _now()
                    row.updated_at = _now()
                    local_db.commit()
            finally:
                if db is None:
                    local_db.close()
            return {"mode": "celery", "enqueued": True, "task_id": task_id}

        # Fallback to local background semantics if Celery is unavailable.
        queue_backend = "background"

    # Background mode: caller can run this from FastAPI BackgroundTasks.
    local_db = db or SessionLocal()
    try:
        row = local_db.query(SyncJob).filter(SyncJob.id == job_id).first()
        if row:
            row.queue_backend = "background"
            row.enqueued_at = _now()
            row.updated_at = _now()
            local_db.commit()
    finally:
        if db is None:
            local_db.close()
    return {"mode": "background", "enqueued": True, "task_id": None}


def run_due_sync_jobs(*, now: datetime | None = None, db=None) -> int:
    reference_now = now or _now()
    local_db = db or SessionLocal()
    try:
        due_jobs = (
            local_db.query(SyncJob)
            .filter(
                SyncJob.status == "RETRYING",
                SyncJob.next_run_at.is_not(None),
                SyncJob.next_run_at <= reference_now,
            )
            .all()
        )
        job_ids = [j.id for j in due_jobs]
    finally:
        if db is None:
            local_db.close()

    for job_id in job_ids:
        preferred = os.getenv("XR7_SYNC_QUEUE_MODE", "celery")
        enqueue_sync_job(job_id, queue_backend=preferred, db=db)

    return len(job_ids)


def run_sync_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        run_sync_job_with_session(db, job_id)
    finally:
        db.close()
