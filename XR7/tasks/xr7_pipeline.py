from __future__ import annotations

import base64

from XR7.celery_app import celery_app
from XR7.models.base import SessionLocal
from XR7.services.xr7_pipelines import (
    run_api_ingestion_pipeline,
    run_black_box_detection,
    run_file_ingestion_pipeline,
    run_fingerprinting_pipeline,
    run_reconciliation_pipeline,
)
from XR7.tasks.xr7_job_schemas import (
    APIIngestionJobPayload,
    BlackBoxJobPayload,
    FileIngestionJobPayload,
    FingerprintJobPayload,
    ReconciliationJobPayload,
)


@celery_app.task(name="xr7.xr7_pipeline.api_ingestion", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def api_ingestion_task(self, payload: dict) -> dict:  # noqa: ANN001
    body = APIIngestionJobPayload.model_validate(payload)
    db = SessionLocal()
    try:
        out = run_api_ingestion_pipeline(
            db,
            tenant_id=body.tenant_id,
            artist_id=body.artist_id,
            providers=body.providers,
            since=body.since,
            until=body.until,
        )
        return out.model_dump()
    finally:
        db.close()


@celery_app.task(name="xr7.xr7_pipeline.file_ingestion", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def file_ingestion_task(self, payload: dict) -> dict:  # noqa: ANN001
    body = FileIngestionJobPayload.model_validate(payload)
    db = SessionLocal()
    try:
        content = base64.b64decode(body.content_base64.encode("ascii"))
        out = run_file_ingestion_pipeline(
            db,
            tenant_id=body.tenant_id,
            artist_id=body.artist_id,
            source_system=body.source_system,
            filename=body.filename,
            content=content,
        )
        return out.model_dump()
    finally:
        db.close()


@celery_app.task(name="xr7.xr7_pipeline.fingerprinting", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 4})
def fingerprinting_task(self, payload: dict) -> dict:  # noqa: ANN001
    body = FingerprintJobPayload.model_validate(payload)
    db = SessionLocal()
    try:
        out = run_fingerprinting_pipeline(
            db,
            tenant_id=body.tenant_id,
            artist_id=body.artist_id,
            platform=body.platform,
            detections=body.detections,
        )
        return out.model_dump()
    finally:
        db.close()


@celery_app.task(name="xr7.xr7_pipeline.reconciliation", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def reconciliation_task(self, payload: dict) -> dict:  # noqa: ANN001
    body = ReconciliationJobPayload.model_validate(payload)
    db = SessionLocal()
    try:
        out = run_reconciliation_pipeline(
            db,
            tenant_id=body.tenant_id,
            artist_id=body.artist_id,
            min_auto_match=body.min_auto_match,
        )
        return out.model_dump()
    finally:
        db.close()


@celery_app.task(name="xr7.xr7_pipeline.black_box_detection", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def black_box_detection_task(self, payload: dict) -> dict:  # noqa: ANN001
    body = BlackBoxJobPayload.model_validate(payload)
    db = SessionLocal()
    try:
        out = run_black_box_detection(
            db,
            tenant_id=body.tenant_id,
            artist_id=body.artist_id,
            min_confidence=body.min_confidence,
        )
        return out.model_dump()
    finally:
        db.close()
