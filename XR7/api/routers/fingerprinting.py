"""FastAPI router for the XR7 audio fingerprinting subsystem.

Endpoints
---------
POST /artists/{artist_id}/fingerprints/identify
    Synchronous audio identification (multipart upload).
POST /artists/{artist_id}/fingerprints/identify/async
    Queue a Celery task and return immediately with a job_id.
POST /artists/{artist_id}/fingerprints/references
    Register a reference track with one or more providers.
GET  /artists/{artist_id}/fingerprints/jobs
    Paginated list of FingerprintJobs for an artist.
GET  /artists/{artist_id}/fingerprints/jobs/{job_id}
    Job detail with associated FingerprintMatch rows.
POST /artists/{artist_id}/fingerprints/reconcile
    Trigger a matching-engine reconciliation Celery task.
GET  /artists/{artist_id}/fingerprints/report
    Run the matching engine synchronously and return a report.
GET  /fingerprints/providers/health
    Health-check all configured providers.
GET  /fingerprints/providers/circuit-breakers
    Return current circuit-breaker states (ops dashboard).
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.routers.auth import get_optional_auth_payload
from XR7.fingerprinting.orchestrator import FingerprintingOrchestrator
from XR7.fingerprinting.schema import (
    FingerprintSubmitRequest,
    NormalizedMatchResult,
    ProviderHealthStatus,
)
from XR7.models.base import get_db
from XR7.models.fingerprint_job import FingerprintJob, FingerprintJobStatus
from XR7.models.fingerprint_match import FingerprintMatch
from xr7_common.logging import get_logger

router = APIRouter(tags=["fingerprinting"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class AsyncJobEnqueuedResponse(BaseModel):
    job_id: str
    status: str = "queued"
    message: str = "Fingerprinting job queued for async processing."


class ReferenceRegistrationResponse(BaseModel):
    reference_id: str
    provider: str
    isrc: str | None = None


class ReconcileJobResponse(BaseModel):
    task_id: str
    status: str = "queued"
    message: str = "Matching engine reconciliation task queued."


class CircuitBreakerStatusResponse(BaseModel):
    provider: str
    state: str
    failure_count: int
    last_failure_time: float | None = None


class FingerprintMatchSchema(BaseModel):
    id: str
    job_id: str
    provider: str
    track_id: str | None
    isrc: str | None
    iswc: str | None
    ipi: str | None
    title: str | None
    artist_name: str | None
    confidence_score: float
    match_type: str
    platform: str | None
    territory: str | None
    royalty_status: str
    anomaly_type: str
    matched_at: str

    model_config = {"from_attributes": True}


class FingerprintJobSchema(BaseModel):
    id: str
    artist_id: str
    status: str
    mode: str
    provider: str | None
    audio_url: str | None
    audio_s3_key: str | None
    isrc: str | None
    tenant_id: str | None
    error_message: str | None
    retry_count: int
    created_at: str
    updated_at: str
    matches: list[FingerprintMatchSchema] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _job_to_dict(job: FingerprintJob, matches: list[FingerprintMatch] | None = None) -> dict[str, Any]:
    return {
        "id": job.id,
        "artist_id": job.artist_id,
        "status": job.status if isinstance(job.status, str) else job.status.value,
        "mode": job.mode if isinstance(job.mode, str) else job.mode.value,
        "provider": job.provider,
        "audio_url": job.audio_url,
        "audio_s3_key": job.audio_s3_key,
        "isrc": job.isrc,
        "tenant_id": job.tenant_id,
        "error_message": job.error_message,
        "retry_count": job.retry_count,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        "matches": [_match_to_dict(m) for m in (matches or [])],
    }


def _match_to_dict(m: FingerprintMatch) -> dict[str, Any]:
    return {
        "id": m.id,
        "job_id": m.job_id,
        "provider": m.provider,
        "track_id": m.track_id,
        "isrc": m.isrc,
        "iswc": m.iswc,
        "ipi": m.ipi,
        "title": m.title,
        "artist_name": m.artist_name,
        "confidence_score": m.confidence_score,
        "match_type": m.match_type,
        "platform": m.platform,
        "territory": m.territory,
        "royalty_status": m.royalty_status,
        "anomaly_type": m.anomaly_type,
        "matched_at": m.matched_at.isoformat() if m.matched_at else None,
    }


# ---------------------------------------------------------------------------
# Sync identify
# ---------------------------------------------------------------------------


@router.post(
    "/artists/{artist_id}/fingerprints/identify",
    response_model=list[NormalizedMatchResult],
    summary="Synchronous audio fingerprint identification",
)
async def identify_audio(
    artist_id: str,
    audio: UploadFile = File(..., description="Audio file (WAV/MP3/FLAC, ≤10 MB)"),
    isrc: str | None = Form(default=None),
    providers: str | None = Form(default=None, description="Comma-separated provider names"),
    tenant_id: str | None = Form(default=None),
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> list[NormalizedMatchResult]:
    """Identify audio synchronously.  Returns normalized match results immediately.

    This endpoint is intended for low-latency use cases such as real-time
    monitoring dashboards.  For large batch jobs use the ``/async`` variant.
    """
    audio_data = await audio.read()
    if len(audio_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file exceeds 10 MB limit.")
    if not audio_data:
        raise HTTPException(status_code=400, detail="Audio file is empty.")

    provider_list: list[str] | None = None
    if providers:
        provider_list = [p.strip() for p in providers.split(",") if p.strip()]

    request = FingerprintSubmitRequest(
        artist_id=artist_id,
        isrc=isrc,
        providers=provider_list,
        tenant_id=tenant_id,
    )

    try:
        orchestrator = FingerprintingOrchestrator(db=db)
        results = await orchestrator.identify(audio_data=audio_data, request=request)
    except Exception as exc:
        logger.error("identify_audio failed artist_id=%s: %s", artist_id, exc)
        raise HTTPException(status_code=502, detail="Fingerprinting service error.") from exc

    return results


# ---------------------------------------------------------------------------
# Async identify (Celery)
# ---------------------------------------------------------------------------


@router.post(
    "/artists/{artist_id}/fingerprints/identify/async",
    response_model=AsyncJobEnqueuedResponse,
    status_code=202,
    summary="Queue asynchronous audio fingerprint identification",
)
async def identify_audio_async(
    artist_id: str,
    audio_url: str | None = Form(default=None),
    audio_s3_key: str | None = Form(default=None),
    isrc: str | None = Form(default=None),
    providers: str | None = Form(default=None),
    tenant_id: str | None = Form(default=None),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> AsyncJobEnqueuedResponse:
    """Queue a fingerprinting job for background processing.

    Either ``audio_url`` or ``audio_s3_key`` must be provided.
    Returns a ``job_id`` that can be polled via ``GET .../jobs/{job_id}``.
    """
    if not audio_url and not audio_s3_key:
        raise HTTPException(
            status_code=400,
            detail="Provide either audio_url or audio_s3_key.",
        )

    provider_list: list[str] | None = None
    if providers:
        provider_list = [p.strip() for p in providers.split(",") if p.strip()]

    from XR7.fingerprinting.workers import realtime_fingerprint_audio

    task = realtime_fingerprint_audio.delay(
        artist_id=artist_id,
        audio_url=audio_url,
        audio_s3_key=audio_s3_key,
        isrc=isrc,
        providers=provider_list,
        tenant_id=tenant_id,
    )

    return AsyncJobEnqueuedResponse(job_id=task.id)


# ---------------------------------------------------------------------------
# Register reference track
# ---------------------------------------------------------------------------


@router.post(
    "/artists/{artist_id}/fingerprints/references",
    response_model=ReferenceRegistrationResponse,
    status_code=201,
    summary="Register a reference track with fingerprinting providers",
)
async def register_reference(
    artist_id: str,
    audio: UploadFile = File(..., description="Reference audio file (WAV/MP3/FLAC, ≤10 MB)"),
    isrc: str | None = Form(default=None),
    title: str | None = Form(default=None),
    artist_name: str | None = Form(default=None),
    provider: str | None = Form(default=None, description="Target provider name (default: first active)"),
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> ReferenceRegistrationResponse:
    """Register a reference track for monitoring / broadcast detection."""
    audio_data = await audio.read()
    if len(audio_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Audio file exceeds 10 MB limit.")
    if not audio_data:
        raise HTTPException(status_code=400, detail="Audio file is empty.")

    metadata: dict[str, Any] = {}
    if title:
        metadata["title"] = title
    if artist_name:
        metadata["artist_name"] = artist_name

    try:
        orchestrator = FingerprintingOrchestrator(db=db)
        # Resolve which provider to use
        if provider:
            adapter = orchestrator._registry.get(provider)
            if adapter is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Provider '{provider}' not configured or disabled.",
                )
        else:
            if not orchestrator._registry:
                raise HTTPException(status_code=503, detail="No fingerprinting providers configured.")
            adapter = next(iter(orchestrator._registry.values()))

        ref_id = await adapter.submit_reference_file(
            audio_data, isrc=isrc, metadata=metadata
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("register_reference failed artist_id=%s: %s", artist_id, exc)
        raise HTTPException(status_code=502, detail="Reference registration failed.") from exc

    return ReferenceRegistrationResponse(
        reference_id=ref_id,
        provider=adapter.provider_name,
        isrc=isrc,
    )


# ---------------------------------------------------------------------------
# Jobs list
# ---------------------------------------------------------------------------


@router.get(
    "/artists/{artist_id}/fingerprints/jobs",
    summary="List fingerprinting jobs for an artist",
)
def list_fingerprint_jobs(
    artist_id: str,
    status: str | None = Query(default=None, description="Filter by job status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Paginated list of FingerprintJob rows for an artist."""
    query = db.query(FingerprintJob).filter(FingerprintJob.artist_id == artist_id)
    if status:
        try:
            status_enum = FingerprintJobStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{status}'. Valid: {[s.value for s in FingerprintJobStatus]}",
            )
        query = query.filter(FingerprintJob.status == status_enum.value)

    total = query.count()
    jobs = (
        query.order_by(FingerprintJob.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_job_to_dict(j) for j in jobs],
    }


# ---------------------------------------------------------------------------
# Job detail
# ---------------------------------------------------------------------------


@router.get(
    "/artists/{artist_id}/fingerprints/jobs/{job_id}",
    summary="Get a fingerprinting job with its match results",
)
def get_fingerprint_job(
    artist_id: str,
    job_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Return a FingerprintJob and all associated FingerprintMatch rows."""
    job = (
        db.query(FingerprintJob)
        .filter(FingerprintJob.id == job_id, FingerprintJob.artist_id == artist_id)
        .first()
    )
    if job is None:
        raise HTTPException(status_code=404, detail="Fingerprint job not found.")

    matches = (
        db.query(FingerprintMatch)
        .filter(FingerprintMatch.job_id == job_id)
        .order_by(FingerprintMatch.confidence_score.desc())
        .all()
    )

    return _job_to_dict(job, matches)


# ---------------------------------------------------------------------------
# Reconcile (async)
# ---------------------------------------------------------------------------


@router.post(
    "/artists/{artist_id}/fingerprints/reconcile",
    response_model=ReconcileJobResponse,
    status_code=202,
    summary="Trigger matching engine reconciliation",
)
def trigger_reconcile(
    artist_id: str,
    providers: list[str] | None = Body(default=None, embed=True),
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> ReconcileJobResponse:
    """Queue a matching-engine reconciliation task for an artist.

    The task will cross-reference detected fingerprint matches against the
    artist's royalty records and flag discrepancies.
    """
    from XR7.fingerprinting.workers import matching_engine_reconcile

    task = matching_engine_reconcile.delay(artist_id=artist_id, providers=providers)

    return ReconcileJobResponse(task_id=task.id)


# ---------------------------------------------------------------------------
# Report (sync)
# ---------------------------------------------------------------------------


@router.get(
    "/artists/{artist_id}/fingerprints/report",
    summary="Run matching engine and return synchronous report",
)
async def get_fingerprint_report(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Run the matching engine synchronously and return a compiled report.

    This is intended for on-demand dashboard reads.  For large catalogs,
    use the ``/reconcile`` endpoint to queue an async task instead.
    """
    from XR7.fingerprinting.matching.engine import MatchingEngine

    try:
        engine = MatchingEngine(db=db)
        report = await engine.run(artist_id=artist_id)
    except Exception as exc:
        logger.error("fingerprint_report failed artist_id=%s: %s", artist_id, exc)
        raise HTTPException(status_code=502, detail="Matching engine error.") from exc

    # Serialize: convert Pydantic models to dicts
    if hasattr(report, "model_dump"):
        return report.model_dump(mode="json")
    return report if isinstance(report, dict) else vars(report)


# ---------------------------------------------------------------------------
# Provider health
# ---------------------------------------------------------------------------


@router.get(
    "/fingerprints/providers/health",
    response_model=list[ProviderHealthStatus],
    summary="Health-check all configured fingerprinting providers",
)
async def provider_health() -> list[ProviderHealthStatus]:
    """Check health for all enabled fingerprinting providers concurrently."""
    try:
        orchestrator = FingerprintingOrchestrator()
        statuses = await orchestrator.health_check_all()
    except Exception as exc:
        logger.error("provider_health_check failed: %s", exc)
        raise HTTPException(status_code=502, detail="Health check failed.") from exc
    return statuses


# ---------------------------------------------------------------------------
# Circuit-breaker status (ops)
# ---------------------------------------------------------------------------


@router.get(
    "/fingerprints/providers/circuit-breakers",
    response_model=list[CircuitBreakerStatusResponse],
    summary="Return circuit-breaker state for all fingerprinting providers",
)
def circuit_breaker_status(
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> list[CircuitBreakerStatusResponse]:
    """Return the current circuit-breaker state for every active provider.

    Intended for use by the XR7 operations dashboard.
    """
    orchestrator = FingerprintingOrchestrator()
    statuses = orchestrator.circuit_breaker_status()

    return [
        CircuitBreakerStatusResponse(
            provider=provider,
            state=info.get("state", "closed"),
            failure_count=info.get("failure_count", 0),
            last_failure_time=info.get("last_failure_time"),
        )
        for provider, info in statuses.items()
    ]
