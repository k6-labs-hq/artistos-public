"""Batch ingestion router."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.batch_ingestion_job import (
    BatchIngestionFile,
    BatchIngestionFileSchema,
    BatchIngestionJob,
    BatchIngestionJobCreate,
    BatchIngestionJobSchema,
)

router = APIRouter(tags=["ingestion"])


@router.post(
    "/artists/{artist_id}/statements/batch",
    response_model=BatchIngestionJobSchema,
    status_code=201,
)
def create_batch_job(
    artist_id: str,
    body: BatchIngestionJobCreate,
    db: Session = Depends(get_db),
):
    """Submit a batch of statement filenames for ingestion.

    Idempotent: re-submitting the same ``idempotency_key`` returns the
    original job without creating a duplicate.
    """
    if body.idempotency_key:
        existing = (
            db.query(BatchIngestionJob)
            .filter(BatchIngestionJob.idempotency_key == body.idempotency_key)
            .first()
        )
        if existing:
            return existing

    job = BatchIngestionJob(
        artist_id=artist_id,
        org_id=body.org_id,
        idempotency_key=body.idempotency_key,
        status="pending",
        total_files=len(body.filenames),
    )
    db.add(job)
    db.flush()  # get the PK before adding children

    for fname in body.filenames:
        db.add(BatchIngestionFile(job_id=job.id, filename=fname, status="pending"))

    db.commit()
    db.refresh(job)
    return job


@router.get(
    "/artists/{artist_id}/statements/batch/{job_id}",
    response_model=BatchIngestionJobSchema,
)
def get_batch_job(artist_id: str, job_id: str, db: Session = Depends(get_db)):
    job = (
        db.query(BatchIngestionJob)
        .filter(
            BatchIngestionJob.id == job_id,
            BatchIngestionJob.artist_id == artist_id,
        )
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found")
    return job


@router.get(
    "/artists/{artist_id}/statements/batch/{job_id}/files",
    response_model=List[BatchIngestionFileSchema],
)
def get_batch_job_files(
    artist_id: str,
    job_id: str,
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    job = (
        db.query(BatchIngestionJob)
        .filter(
            BatchIngestionJob.id == job_id,
            BatchIngestionJob.artist_id == artist_id,
        )
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found")

    q = db.query(BatchIngestionFile).filter(BatchIngestionFile.job_id == job_id)
    if status:
        q = q.filter(BatchIngestionFile.status == status)
    return q.all()


@router.post(
    "/artists/{artist_id}/statements/batch/{job_id}/retry-failed",
    response_model=BatchIngestionJobSchema,
)
def retry_failed_files(artist_id: str, job_id: str, db: Session = Depends(get_db)):
    """Reset all failed files in a job back to 'pending' for re-processing."""
    job = (
        db.query(BatchIngestionJob)
        .filter(
            BatchIngestionJob.id == job_id,
            BatchIngestionJob.artist_id == artist_id,
        )
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Batch job not found")

    failed_files = (
        db.query(BatchIngestionFile)
        .filter(
            BatchIngestionFile.job_id == job_id,
            BatchIngestionFile.status == "failed",
        )
        .all()
    )
    for f in failed_files:
        f.status = "pending"
        f.error_msg = None

    job.status = "pending"
    job.failed_files = 0
    db.commit()
    db.refresh(job)
    return job
