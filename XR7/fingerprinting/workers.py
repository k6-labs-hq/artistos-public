"""Celery background workers for the XR7 fingerprinting subsystem.

Workers:
    fp.batch_fingerprint_audio          — Process a batch of audio files
    fp.realtime_fingerprint_audio       — Single real-time fingerprint job
    fp.provider_health_check_all        — Check all provider health statuses
    fp.reprocess_failed_jobs            — Retry failed FingerprintJob rows
    fp.matching_engine_reconcile        — Batch matching engine reconciliation
    fp.anomaly_detection_sweep          — Periodic anomaly sweep for an artist
"""

from __future__ import annotations

import asyncio
from typing import Any

from XR7.celery_app import celery_app
from XR7.models.base import SessionLocal
from xr7_common.logging import get_logger

logger = get_logger(__name__)


def _run_async(coro):
    """Run an async coroutine from a synchronous Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ---------------------------------------------------------------------------
# Real-time fingerprinting
# ---------------------------------------------------------------------------


@celery_app.task(
    name="fp.realtime_fingerprint_audio",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def realtime_fingerprint_audio(
    self,
    artist_id: str,
    audio_s3_key: str | None = None,
    audio_url: str | None = None,
    isrc: str | None = None,
    providers: list[str] | None = None,
    tenant_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fingerprint a single audio file in real time.

    Downloads audio from S3 or URL, runs it through the orchestrator, and
    persists results.
    """
    from XR7.fingerprinting.observability import increment
    from XR7.fingerprinting.orchestrator import FingerprintingOrchestrator
    from XR7.fingerprinting.schema import FingerprintSubmitRequest

    increment("fp.tasks.realtime", {"artist_id": artist_id})

    audio_data = _fetch_audio(audio_s3_key=audio_s3_key, audio_url=audio_url)
    if not audio_data:
        logger.warning(
            "realtime_fingerprint_audio: no audio data artist_id=%s", artist_id
        )
        return {"status": "skipped", "reason": "no_audio_data"}

    request = FingerprintSubmitRequest(
        artist_id=artist_id,
        audio_s3_key=audio_s3_key,
        audio_url=audio_url,
        isrc=isrc,
        providers=providers,
        tenant_id=tenant_id,
        metadata=metadata or {},
    )

    db = SessionLocal()
    try:
        orchestrator = FingerprintingOrchestrator(db=db)
        results = _run_async(orchestrator.identify(audio_data, request))
        _run_async(orchestrator.aclose())
        return {
            "status": "completed",
            "artist_id": artist_id,
            "match_count": len(results),
            "matches": [
                {
                    "isrc": r.isrc,
                    "title": r.title,
                    "provider": r.provider,
                    "confidence": r.confidence_score,
                }
                for r in results
            ],
        }
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Batch fingerprinting
# ---------------------------------------------------------------------------


@celery_app.task(
    name="fp.batch_fingerprint_audio",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def batch_fingerprint_audio(
    self,
    artist_id: str,
    items: list[dict[str, Any]],
    tenant_id: str | None = None,
) -> dict[str, Any]:
    """Process a list of audio items in batch.

    Each item in ``items`` should be::

        {
            "audio_s3_key": "path/to/file.wav",
            "isrc": "USAT12345678",   # optional
            "providers": ["acrcloud"] # optional
        }
    """
    from XR7.fingerprinting.observability import increment

    increment("fp.tasks.batch", {"artist_id": artist_id})
    logger.info(
        "batch_fingerprint_audio artist_id=%s items=%d", artist_id, len(items)
    )

    results_summary: list[dict[str, Any]] = []
    for item in items:
        sub_result = realtime_fingerprint_audio.apply(
            kwargs={
                "artist_id": artist_id,
                "audio_s3_key": item.get("audio_s3_key"),
                "audio_url": item.get("audio_url"),
                "isrc": item.get("isrc"),
                "providers": item.get("providers"),
                "tenant_id": tenant_id,
            }
        )
        results_summary.append(sub_result.result or {})

    return {
        "status": "completed",
        "artist_id": artist_id,
        "total": len(items),
        "results": results_summary,
    }


# ---------------------------------------------------------------------------
# Provider health checks
# ---------------------------------------------------------------------------


@celery_app.task(name="fp.provider_health_check_all", bind=True)
def provider_health_check_all(self) -> dict[str, Any]:  # noqa: ANN001
    """Run health checks against all configured fingerprinting providers."""
    from XR7.fingerprinting.observability import alert_provider_outage
    from XR7.fingerprinting.orchestrator import FingerprintingOrchestrator
    from XR7.fingerprinting.schema import ProviderStatus

    orchestrator = FingerprintingOrchestrator()
    statuses = _run_async(orchestrator.health_check_all())
    _run_async(orchestrator.aclose())

    report: dict[str, Any] = {}
    for s in statuses:
        report[s.provider] = {
            "status": s.status.value,
            "latency_ms": s.latency_ms,
            "error": s.error_message,
        }
        if s.status == ProviderStatus.DOWN:
            alert_provider_outage(s.provider, s.error_message or "no details")

    logger.info("provider_health_check_all complete: %s", report)
    return report


# ---------------------------------------------------------------------------
# Reprocess failed jobs
# ---------------------------------------------------------------------------


@celery_app.task(name="fp.reprocess_failed_jobs", bind=True)
def reprocess_failed_jobs(self) -> dict[str, Any]:  # noqa: ANN001
    """Find FingerprintJob rows with status=FAILED and requeue them."""
    from XR7.models.fingerprint_job import FingerprintJob, FingerprintJobStatus

    db = SessionLocal()
    try:
        failed_jobs = (
            db.query(FingerprintJob)
            .filter(FingerprintJob.status == FingerprintJobStatus.FAILED)
            .filter(FingerprintJob.retry_count < 3)
            .limit(50)
            .all()
        )
        requeued = 0
        for job in failed_jobs:
            try:
                realtime_fingerprint_audio.delay(
                    artist_id=job.artist_id,
                    audio_s3_key=job.audio_s3_key,
                    audio_url=job.audio_url,
                    isrc=job.isrc,
                    tenant_id=job.tenant_id,
                    metadata=job.job_metadata,
                )
                job.retry_count = (job.retry_count or 0) + 1
                job.status = FingerprintJobStatus.PENDING
                requeued += 1
            except Exception as exc:
                logger.error("Failed to requeue job_id=%s: %s", job.id, exc)

        db.commit()
        logger.info("reprocess_failed_jobs: requeued=%d", requeued)
        return {"status": "completed", "requeued": requeued}
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Matching Engine batch reconciliation
# ---------------------------------------------------------------------------


@celery_app.task(
    name="fp.matching_engine_reconcile",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def matching_engine_reconcile(self, artist_id: str) -> dict[str, Any]:  # noqa: ANN001
    """Run the full Matching Engine reconciliation for one artist."""
    import time as _time

    from XR7.fingerprinting.matching.engine import MatchingEngine
    from XR7.fingerprinting.observability import audit_matching_run

    db = SessionLocal()
    try:
        start = _time.monotonic()
        engine = MatchingEngine(db)
        report = engine.run(artist_id, [])  # stub call — loads from DB internally
        duration_ms = (_time.monotonic() - start) * 1000.0

        audit_matching_run(
            artist_id=artist_id,
            fingerprint_count=len(report.fingerprint_results),
            catalog_match_count=len(report.catalog_matches),
            royalty_gap_count=len(report.royalty_gaps),
            anomaly_count=len(report.anomalies),
            duration_ms=duration_ms,
        )

        return {
            "status": "completed",
            "artist_id": artist_id,
            "catalog_matches": len(report.catalog_matches),
            "royalty_gaps": len(report.royalty_gaps),
            "anomalies": len(report.anomalies),
            "duration_ms": round(duration_ms, 2),
        }
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Anomaly detection sweep
# ---------------------------------------------------------------------------


@celery_app.task(name="fp.anomaly_detection_sweep", bind=True)
def anomaly_detection_sweep(self, artist_id: str | None = None) -> dict[str, Any]:  # noqa: ANN001
    """Run the fingerprinting anomaly sweep for one or all artists."""
    from XR7.fingerprinting.matching.engine import MatchingEngine
    from XR7.models.artist import Artist

    db = SessionLocal()
    try:
        if artist_id:
            artist_ids = [artist_id]
        else:
            artists = db.query(Artist).limit(200).all()
            artist_ids = [a.id for a in artists]

        total_anomalies = 0
        for aid in artist_ids:
            try:
                engine = MatchingEngine(db)
                anomalies = engine.run_anomaly_sweep(aid)
                total_anomalies += len(anomalies)
                logger.info(
                    "anomaly_detection_sweep artist_id=%s anomalies=%d",
                    aid,
                    len(anomalies),
                )
            except Exception as exc:
                logger.error(
                    "anomaly_detection_sweep failed artist_id=%s: %s", aid, exc
                )

        return {
            "status": "completed",
            "artists_processed": len(artist_ids),
            "total_anomalies": total_anomalies,
        }
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Audio fetch helper
# ---------------------------------------------------------------------------


def _fetch_audio(
    audio_s3_key: str | None = None,
    audio_url: str | None = None,
) -> bytes | None:
    """Download audio from S3 or a URL.  Returns raw bytes or None."""
    if audio_s3_key:
        return _fetch_from_s3(audio_s3_key)
    if audio_url:
        return _fetch_from_url(audio_url)
    return None


def _fetch_from_s3(s3_key: str) -> bytes | None:
    try:
        import boto3

        from xr7_common.settings import settings

        s3 = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
        )
        response = s3.get_object(Bucket=settings.s3_bucket, Key=s3_key)
        return response["Body"].read()
    except Exception as exc:
        logger.error("_fetch_from_s3 failed key=%s: %s", s3_key, exc)
        return None


def _fetch_from_url(url: str) -> bytes | None:
    try:
        import httpx

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.content
    except Exception as exc:
        logger.error("_fetch_from_url failed url=%s: %s", url, exc)
        return None
