from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from XR7.ingestion.fetchers import get_fetcher
from XR7.models.base import SessionLocal
from XR7.models.sync_job import SyncJob


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


def run_sync_job(job_id: str) -> None:
    db = SessionLocal()
    try:
        run_sync_job_with_session(db, job_id)
    finally:
        db.close()
