from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.xr7_royalty import XR7ConnectorCredentialUpsert
from XR7.services.xr7_pipelines import (
    build_royalty_gap_report,
    create_sync_job,
    run_api_ingestion_pipeline,
    run_black_box_detection,
    run_file_ingestion_pipeline,
    run_fingerprinting_pipeline,
    run_reconciliation_pipeline,
    upsert_connector_credential,
)
from XR7.tasks.xr7_job_schemas import RETRY_POLICIES
from XR7.tasks.xr7_pipeline import (
    api_ingestion_task,
    black_box_detection_task,
    file_ingestion_task,
    fingerprinting_task,
    reconciliation_task,
)
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["xr7-forensics"])


class APIIngestionRequest(BaseModel):
    tenant_id: str = "default"
    providers: list[str] = Field(default_factory=list)
    since: datetime | None = None
    until: datetime | None = None
    queue_backend: str = "celery"


class FingerprintingRequest(BaseModel):
    tenant_id: str = "default"
    platform: str
    detections: list[dict[str, object]] = Field(default_factory=list)
    queue_backend: str = "celery"


class ReconciliationRequest(BaseModel):
    tenant_id: str = "default"
    min_auto_match: float = 0.92
    queue_backend: str = "celery"


class BlackBoxRequest(BaseModel):
    tenant_id: str = "default"
    min_confidence: float = 0.85
    queue_backend: str = "celery"


def _dispatch_task(queue_backend: str, task_fn, payload: dict[str, Any], inline_fn):
    mode = (queue_backend or "celery").strip().lower()
    if mode == "inline":
        result = inline_fn()
        return {"mode": "inline", "task_id": None, "result": result}
    task = task_fn.delay(payload)
    return {"mode": mode, "task_id": task.id, "result": None}


@router.post("/artists/{artist_id}/xr7/credentials")
def upsert_xr7_credentials(artist_id: str, payload: XR7ConnectorCredentialUpsert, db: Session = Depends(get_db)):
    expires_at = None
    if payload.expires_in_seconds is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=max(0, payload.expires_in_seconds))
    row = upsert_connector_credential(
        db,
        tenant_id=payload.tenant_id,
        artist_id=artist_id,
        provider=payload.provider,
        external_account_id=payload.external_account_id,
        access_token=payload.access_token,
        refresh_token=payload.refresh_token,
        expires_at=expires_at,
        scopes=payload.granted_scopes,
    )
    return inject_branding_metadata(
        db,
        {
            "id": row.id,
            "artist_id": row.artist_id,
            "tenant_id": row.tenant_id,
            "provider": row.provider,
            "external_account_id": row.external_account_id,
            "status": row.status,
        },
    )


@router.post("/artists/{artist_id}/xr7/pipelines/api-ingestion")
def run_api_ingestion(artist_id: str, payload: APIIngestionRequest, db: Session = Depends(get_db)):
    out = run_api_ingestion_pipeline(
        db,
        tenant_id=payload.tenant_id,
        artist_id=artist_id,
        providers=payload.providers,
        since=payload.since,
        until=payload.until,
    )
    return out.model_dump()


@router.post("/artists/{artist_id}/xr7/pipelines/file-ingestion")
async def run_file_ingestion(
    artist_id: str,
    source_system: str = Form(...),
    tenant_id: str = Form("default"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()
    out = run_file_ingestion_pipeline(
        db,
        tenant_id=tenant_id,
        artist_id=artist_id,
        source_system=source_system,
        filename=file.filename or "upload.bin",
        content=content,
    )
    return out.model_dump()


@router.post("/artists/{artist_id}/xr7/pipelines/fingerprinting")
def run_fingerprinting(artist_id: str, payload: FingerprintingRequest, db: Session = Depends(get_db)):
    out = run_fingerprinting_pipeline(
        db,
        tenant_id=payload.tenant_id,
        artist_id=artist_id,
        platform=payload.platform,
        detections=payload.detections,
    )
    return out.model_dump()


@router.post("/artists/{artist_id}/xr7/pipelines/reconciliation")
def run_reconciliation(artist_id: str, payload: ReconciliationRequest, db: Session = Depends(get_db)):
    out = run_reconciliation_pipeline(
        db,
        tenant_id=payload.tenant_id,
        artist_id=artist_id,
        min_auto_match=payload.min_auto_match,
    )
    return out.model_dump()


@router.post("/artists/{artist_id}/xr7/pipelines/black-box-detection")
def run_black_box(artist_id: str, payload: BlackBoxRequest, db: Session = Depends(get_db)):
    out = run_black_box_detection(
        db,
        tenant_id=payload.tenant_id,
        artist_id=artist_id,
        min_confidence=payload.min_confidence,
    )
    return out.model_dump()


@router.get("/artists/{artist_id}/xr7/reconciliation/gaps")
def get_gap_report(artist_id: str, tenant_id: str = "default", db: Session = Depends(get_db)):
    return build_royalty_gap_report(db, tenant_id=tenant_id, artist_id=artist_id).model_dump()


@router.post("/artists/{artist_id}/xr7/queue/api-ingestion")
def queue_api_ingestion(artist_id: str, payload: APIIngestionRequest, db: Session = Depends(get_db)):
    retry = RETRY_POLICIES["api_ingestion"]
    job_payload = payload.model_dump(mode="json")
    dispatch = _dispatch_task(
        payload.queue_backend,
        api_ingestion_task,
        job_payload,
        lambda: run_api_ingestion_pipeline(
            db,
            tenant_id=payload.tenant_id,
            artist_id=artist_id,
            providers=payload.providers,
            since=payload.since,
            until=payload.until,
        ).model_dump(),
    )
    job = create_sync_job(
        db,
        artist_id=artist_id,
        integration="xr7_api_ingestion",
        payload=job_payload,
        max_attempts=retry.max_retries,
        queue_backend=dispatch["mode"],
    )
    if dispatch["task_id"]:
        job.last_task_id = dispatch["task_id"]
        db.commit()
    return {
        "job_id": job.id,
        "status": job.status,
        "max_attempts": job.max_attempts,
        "queue_backend": dispatch["mode"],
        "task_id": dispatch["task_id"],
        "inline_result": dispatch["result"],
    }


@router.post("/artists/{artist_id}/xr7/queue/file-ingestion")
async def queue_file_ingestion(
    artist_id: str,
    source_system: str = Form(...),
    tenant_id: str = Form("default"),
    queue_backend: str = Form("celery"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    retry = RETRY_POLICIES["file_ingestion"]
    content = await file.read()
    payload = {
        "tenant_id": tenant_id,
        "artist_id": artist_id,
        "source_system": source_system,
        "filename": file.filename or "upload.bin",
        "content_base64": base64.b64encode(content).decode("ascii"),
    }
    dispatch = _dispatch_task(
        queue_backend,
        file_ingestion_task,
        payload,
        lambda: run_file_ingestion_pipeline(
            db,
            tenant_id=tenant_id,
            artist_id=artist_id,
            source_system=source_system,
            filename=file.filename or "upload.bin",
            content=content,
        ).model_dump(),
    )
    job = create_sync_job(
        db,
        artist_id=artist_id,
        integration="xr7_file_ingestion",
        payload=payload,
        max_attempts=retry.max_retries,
        queue_backend=dispatch["mode"],
    )
    if dispatch["task_id"]:
        job.last_task_id = dispatch["task_id"]
        db.commit()
    return {
        "job_id": job.id,
        "status": job.status,
        "max_attempts": job.max_attempts,
        "queue_backend": dispatch["mode"],
        "task_id": dispatch["task_id"],
        "inline_result": dispatch["result"],
    }


@router.post("/artists/{artist_id}/xr7/queue/fingerprinting")
def queue_fingerprinting(artist_id: str, payload: FingerprintingRequest, db: Session = Depends(get_db)):
    retry = RETRY_POLICIES["fingerprinting"]
    job_payload = payload.model_dump(mode="json")
    dispatch = _dispatch_task(
        payload.queue_backend,
        fingerprinting_task,
        job_payload,
        lambda: run_fingerprinting_pipeline(
            db,
            tenant_id=payload.tenant_id,
            artist_id=artist_id,
            platform=payload.platform,
            detections=payload.detections,
        ).model_dump(),
    )
    job = create_sync_job(
        db,
        artist_id=artist_id,
        integration="xr7_fingerprinting",
        payload=job_payload,
        max_attempts=retry.max_retries,
        queue_backend=dispatch["mode"],
    )
    if dispatch["task_id"]:
        job.last_task_id = dispatch["task_id"]
        db.commit()
    return {"job_id": job.id, "task_id": dispatch["task_id"], "inline_result": dispatch["result"]}


@router.post("/artists/{artist_id}/xr7/queue/reconciliation")
def queue_reconciliation(artist_id: str, payload: ReconciliationRequest, db: Session = Depends(get_db)):
    retry = RETRY_POLICIES["reconciliation"]
    job_payload = payload.model_dump(mode="json")
    dispatch = _dispatch_task(
        payload.queue_backend,
        reconciliation_task,
        job_payload,
        lambda: run_reconciliation_pipeline(
            db,
            tenant_id=payload.tenant_id,
            artist_id=artist_id,
            min_auto_match=payload.min_auto_match,
        ).model_dump(),
    )
    job = create_sync_job(
        db,
        artist_id=artist_id,
        integration="xr7_reconciliation",
        payload=job_payload,
        max_attempts=retry.max_retries,
        queue_backend=dispatch["mode"],
    )
    if dispatch["task_id"]:
        job.last_task_id = dispatch["task_id"]
        db.commit()
    return {"job_id": job.id, "task_id": dispatch["task_id"], "inline_result": dispatch["result"]}


@router.post("/artists/{artist_id}/xr7/queue/black-box-detection")
def queue_black_box(artist_id: str, payload: BlackBoxRequest, db: Session = Depends(get_db)):
    retry = RETRY_POLICIES["black_box_detection"]
    job_payload = payload.model_dump(mode="json")
    dispatch = _dispatch_task(
        payload.queue_backend,
        black_box_detection_task,
        job_payload,
        lambda: run_black_box_detection(
            db,
            tenant_id=payload.tenant_id,
            artist_id=artist_id,
            min_confidence=payload.min_confidence,
        ).model_dump(),
    )
    job = create_sync_job(
        db,
        artist_id=artist_id,
        integration="xr7_black_box_detection",
        payload=job_payload,
        max_attempts=retry.max_retries,
        queue_backend=dispatch["mode"],
    )
    if dispatch["task_id"]:
        job.last_task_id = dispatch["task_id"]
        db.commit()
    return {"job_id": job.id, "task_id": dispatch["task_id"], "inline_result": dispatch["result"]}
