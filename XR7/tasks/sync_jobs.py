from __future__ import annotations

from datetime import datetime, timezone

from XR7.celery_app import celery_app
from XR7.ingestion.sync_jobs import run_due_sync_jobs, run_sync_job
from xr7_common.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(name="xr7.sync_jobs.run", bind=True, max_retries=0)
def run_sync_job_task(self, job_id: str) -> str:  # noqa: ANN001
    logger.info("Running sync job task", extra={"job_id": job_id})
    run_sync_job(job_id)
    return job_id


@celery_app.task(name="xr7.sync_jobs.requeue_due", bind=True, max_retries=0)
def requeue_due_jobs_task(self) -> dict[str, int]:  # noqa: ANN001
    now = datetime.now(timezone.utc)
    enqueued = run_due_sync_jobs(now=now)
    logger.info("Requeued due sync jobs", extra={"count": enqueued})
    return {"enqueued": enqueued}
