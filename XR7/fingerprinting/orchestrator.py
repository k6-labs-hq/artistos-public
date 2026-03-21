"""FingerprintingOrchestrator — provider-agnostic routing, aggregation and
ingestion pipeline integration.

The orchestrator:
1. Resolves which providers to use (config, tenant overrides, per-request list)
2. Runs providers in priority order with parallel or sequential execution
3. Falls back to the next provider when one fails or returns no results
4. Deduplicates and merges match results from multiple providers
5. Emits normalized events to the XR7 ingestion pipeline
6. Persists FingerprintJob records and FingerprintMatch records to the DB
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.fingerprinting.config import FingerprintingConfig, fingerprinting_config
from XR7.fingerprinting._resilience import (
    ProviderCircuitOpenError,
    get_circuit_registry,
    CircuitBreakerRegistry,
)
from XR7.fingerprinting.interface import IFingerprintingProvider
from XR7.fingerprinting.schema import (
    FingerprintSubmitRequest,
    NormalizedMatchResult,
    ProviderHealthStatus,
)
from XR7.ingestion.universal_schema import to_universal_royalty_event
from xr7_common.logging import get_logger

logger = get_logger(__name__)


def _build_provider_registry(
    cfg: FingerprintingConfig,
) -> dict[str, IFingerprintingProvider]:
    """Instantiate all enabled provider adapters, sorted by priority."""
    from XR7.fingerprinting.adapters.acrcloud import ACRCloudAdapter
    from XR7.fingerprinting.adapters.audible_magic import AudibleMagicAdapter
    from XR7.fingerprinting.adapters.bmat import BMATAdapter
    from XR7.fingerprinting.adapters.gracenote import GracenoteAdapter
    from XR7.fingerprinting.adapters.pex import PexAdapter
    from XR7.fingerprinting.adapters.soundmouse import SoundmouseAdapter

    candidates: list[tuple[int, str, IFingerprintingProvider]] = []

    if cfg.acrcloud.enabled:
        candidates.append(
            (cfg.acrcloud.priority, "acrcloud", ACRCloudAdapter(cfg.acrcloud))
        )
    if cfg.audible_magic.enabled:
        candidates.append(
            (
                cfg.audible_magic.priority,
                "audible_magic",
                AudibleMagicAdapter(cfg.audible_magic),
            )
        )
    if cfg.gracenote.enabled:
        candidates.append(
            (cfg.gracenote.priority, "gracenote", GracenoteAdapter(cfg.gracenote))
        )
    if cfg.bmat.enabled:
        candidates.append((cfg.bmat.priority, "bmat", BMATAdapter(cfg.bmat)))
    if cfg.soundmouse.enabled:
        candidates.append(
            (cfg.soundmouse.priority, "soundmouse", SoundmouseAdapter(cfg.soundmouse))
        )
    if cfg.pex.enabled:
        candidates.append((cfg.pex.priority, "pex", PexAdapter(cfg.pex)))

    candidates.sort(key=lambda t: t[0])
    return {name: adapter for _, name, adapter in candidates}


def _dedup_results(
    results: list[NormalizedMatchResult],
) -> list[NormalizedMatchResult]:
    """Deduplicate results by (isrc, provider) keeping highest confidence."""
    seen: dict[tuple[str | None, str], NormalizedMatchResult] = {}
    for r in results:
        key = (r.isrc, r.provider)
        if key not in seen or r.confidence_score > seen[key].confidence_score:
            seen[key] = r
    return sorted(seen.values(), key=lambda r: r.confidence_score, reverse=True)


def _parse_tenant_map(raw: str) -> dict[str, list[str]]:
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}


class FingerprintingOrchestrator:
    """Routes fingerprint requests to the correct providers and aggregates results.

    Usage::

        orchestrator = FingerprintingOrchestrator(db=db_session)
        results = await orchestrator.identify(audio_data=wav_bytes, request=req)
    """

    def __init__(
        self,
        db: Session | None = None,
        config: FingerprintingConfig | None = None,
    ) -> None:
        self._cfg = config or fingerprinting_config
        self._db = db
        self._registry: dict[str, IFingerprintingProvider] = _build_provider_registry(
            self._cfg
        )
        self._tenant_map: dict[str, list[str]] = _parse_tenant_map(
            self._cfg.orchestrator.tenant_provider_map_raw
        )
        self._cb_registry: CircuitBreakerRegistry = get_circuit_registry()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def identify(
        self,
        audio_data: bytes,
        request: FingerprintSubmitRequest,
    ) -> list[NormalizedMatchResult]:
        """Fingerprint audio and return deduplicated normalized results.

        Routing order:
        1. Per-request ``providers`` list (if specified)
        2. Per-tenant provider map (if tenant_id matches)
        3. Global priority order from config
        """
        job_id = str(uuid.uuid4())
        providers = self._resolve_providers(
            request.providers, request.tenant_id
        )

        logger.info(
            "Fingerprinting job_id=%s artist_id=%s providers=%s",
            job_id,
            request.artist_id,
            [p.provider_name for p in providers],
        )

        # Persist job record if DB session is available
        self._persist_job(job_id, request, [p.provider_name for p in providers])

        ocfg = self._cfg.orchestrator
        all_results: list[NormalizedMatchResult] = []

        if ocfg.multi_provider_aggregation:
            all_results = await self._run_parallel(providers, audio_data, request)
        else:
            all_results = await self._run_with_fallback(providers, audio_data, request)

        # Filter by confidence threshold
        min_conf = ocfg.min_confidence_threshold
        filtered = [r for r in all_results if r.confidence_score >= min_conf]
        deduped = _dedup_results(filtered)

        # Emit to XR7 ingestion pipeline
        for match in deduped:
            self._emit_ingestion_event(request.artist_id, match)

        # Persist matches
        self._persist_matches(job_id, deduped)

        logger.info(
            "Fingerprinting job_id=%s completed matches=%d",
            job_id,
            len(deduped),
        )
        return deduped

    async def detect_usage(
        self,
        reference_id: str,
        artist_id: str,
        *,
        provider_name: str | None = None,
        territory: str | None = None,
    ) -> list[NormalizedMatchResult]:
        """Detect usage of a registered reference track."""
        if provider_name:
            adapter = self._registry.get(provider_name)
            if adapter is None:
                raise ValueError(f"Provider '{provider_name}' not registered")
            return await adapter.detect_usage(reference_id, territory=territory)

        results: list[NormalizedMatchResult] = []
        for adapter in self._registry.values():
            try:
                detections = await adapter.detect_usage(
                    reference_id, territory=territory
                )
                results.extend(detections)
            except Exception as exc:
                logger.warning(
                    "detect_usage failed provider=%s: %s",
                    adapter.provider_name,
                    exc,
                )
        return _dedup_results(results)

    async def health_check_all(self) -> list[ProviderHealthStatus]:
        """Run health checks against all registered providers concurrently."""
        tasks = [adapter.get_provider_health() for adapter in self._registry.values()]
        statuses: list[ProviderHealthStatus] = await asyncio.gather(
            *tasks, return_exceptions=False
        )
        for s in statuses:
            logger.info(
                "Health check provider=%s status=%s latency_ms=%.1f",
                s.provider,
                s.status.value,
                s.latency_ms or 0.0,
            )
        return statuses

    # ------------------------------------------------------------------
    # Internal routing
    # ------------------------------------------------------------------

    def _resolve_providers(
        self,
        requested: list[str] | None,
        tenant_id: str | None,
    ) -> list[IFingerprintingProvider]:
        """Return an ordered list of provider adapters to use."""
        if requested:
            return [
                self._registry[name]
                for name in requested
                if name in self._registry
            ]
        if tenant_id and tenant_id in self._tenant_map:
            names = self._tenant_map[tenant_id]
            return [
                self._registry[name]
                for name in names
                if name in self._registry
            ]
        return list(self._registry.values())[
            : self._cfg.orchestrator.max_parallel_providers
        ]

    async def _run_parallel(
        self,
        providers: list[IFingerprintingProvider],
        audio_data: bytes,
        request: FingerprintSubmitRequest,
    ) -> list[NormalizedMatchResult]:
        """Query all providers concurrently and aggregate results."""
        timeout = self._cfg.orchestrator.provider_timeout_seconds

        async def _safe_match(
            adapter: IFingerprintingProvider,
        ) -> list[NormalizedMatchResult]:
            cb = self._cb_registry.get(adapter.provider_name)
            if cb.is_open():
                logger.warning(
                    "Circuit OPEN — skipping provider=%s", adapter.provider_name
                )
                return []
            try:
                results = await asyncio.wait_for(
                    adapter.match_audio(
                        audio_data,
                        metadata={
                            "isrc": request.isrc,
                            "title": request.title,
                            "artist": request.artist_name,
                        },
                    ),
                    timeout=timeout,
                )
                cb.record_success()
                return results
            except ProviderCircuitOpenError:
                return []
            except asyncio.TimeoutError:
                cb.record_failure()
                logger.warning(
                    "Provider %s timed out after %.1fs",
                    adapter.provider_name,
                    timeout,
                )
                return []
            except Exception as exc:
                cb.record_failure()
                logger.warning(
                    "Provider %s raised: %s", adapter.provider_name, exc
                )
                return []

        nested = await asyncio.gather(*[_safe_match(p) for p in providers])
        return [r for sub in nested for r in sub]

    async def _run_with_fallback(
        self,
        providers: list[IFingerprintingProvider],
        audio_data: bytes,
        request: FingerprintSubmitRequest,
    ) -> list[NormalizedMatchResult]:
        """Try providers in priority order, stop at first successful result."""
        for adapter in providers:
            cb = self._cb_registry.get(adapter.provider_name)
            if cb.is_open():
                logger.warning(
                    "Fallback: circuit OPEN, skipping provider=%s",
                    adapter.provider_name,
                )
                continue
            try:
                results = await adapter.match_audio(
                    audio_data,
                    metadata={
                        "isrc": request.isrc,
                        "title": request.title,
                        "artist": request.artist_name,
                    },
                )
                if results:
                        cb.record_success()
                        logger.debug(
                            "Fallback: returning results from provider=%s",
                            adapter.provider_name,
                        )
                        return results
                cb.record_success()
            except Exception as exc:
                cb.record_failure()
                logger.warning(
                    "Fallback: provider=%s failed, trying next. Error: %s",
                    adapter.provider_name,
                    exc,
                )
        return []

    # ------------------------------------------------------------------
    # Ingestion pipeline integration
    # ------------------------------------------------------------------

    def _emit_ingestion_event(
        self, artist_id: str, match: NormalizedMatchResult
    ) -> None:
        """Emit a normalized royalty event to the XR7 ingestion pipeline."""
        try:
            event = to_universal_royalty_event(
                artist_id=artist_id,
                source_type="fingerprinting",
                source_name=match.provider,
                record_type="fingerprint_match",
                event_type=match.match_type.value
                if hasattr(match.match_type, "value")
                else str(match.match_type),
                amount=0.0,
                quantity=1.0,
                territory=match.territory,
                work_title=match.title,
                isrc=match.isrc,
                metadata={
                    "confidence_score": match.confidence_score,
                    "platform": match.platform,
                    "provider": match.provider,
                    "royalty_status": match.royalty_status.value
                    if hasattr(match.royalty_status, "value")
                    else str(match.royalty_status),
                    "anomaly_type": match.anomaly_type.value
                    if hasattr(match.anomaly_type, "value")
                    else str(match.anomaly_type),
                },
            )
            logger.debug("Emitted ingestion event isrc=%s provider=%s", match.isrc, match.provider)
            return event
        except Exception as exc:
            logger.error("Failed to emit ingestion event: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _persist_job(
        self,
        job_id: str,
        request: FingerprintSubmitRequest,
        provider_names: list[str],
    ) -> None:
        if self._db is None:
            return
        try:
            from XR7.models.fingerprint_job import FingerprintJob, FingerprintJobMode, FingerprintJobStatus

            job = FingerprintJob(
                id=job_id,
                artist_id=request.artist_id,
                status=FingerprintJobStatus.PROCESSING,
                mode=FingerprintJobMode.REALTIME,
                provider=",".join(provider_names),
                audio_url=request.audio_url,
                audio_s3_key=request.audio_s3_key,
                isrc=request.isrc,
                tenant_id=request.tenant_id,
                job_metadata=request.metadata,
            )
            self._db.add(job)
            self._db.commit()
        except Exception as exc:
            logger.error("Failed to persist FingerprintJob: %s", exc)
            if self._db:
                self._db.rollback()

    def _persist_matches(
        self,
        job_id: str,
        results: list[NormalizedMatchResult],
    ) -> None:
        if self._db is None:
            return
        try:
            from XR7.models.fingerprint_match import FingerprintMatch

            for r in results:
                match = FingerprintMatch(
                    id=str(uuid.uuid4()),
                    job_id=job_id,
                    provider=r.provider,
                    track_id=r.track_id,
                    isrc=r.isrc,
                    iswc=r.iswc,
                    ipi=r.ipi,
                    title=r.title,
                    artist_name=r.artist_name,
                    confidence_score=r.confidence_score,
                    match_type=r.match_type.value
                    if hasattr(r.match_type, "value")
                    else str(r.match_type),
                    platform=r.platform,
                    territory=r.territory,
                    royalty_status=r.royalty_status.value
                    if hasattr(r.royalty_status, "value")
                    else str(r.royalty_status),
                    anomaly_type=r.anomaly_type.value
                    if hasattr(r.anomaly_type, "value")
                    else str(r.anomaly_type),
                    raw_payload=r.raw_provider_payload,
                    matched_at=r.timestamp,
                )
                self._db.add(match)

            # Mark job as completed
            from XR7.models.fingerprint_job import FingerprintJob, FingerprintJobStatus

            job = self._db.query(FingerprintJob).filter(FingerprintJob.id == job_id).first()
            if job:
                job.status = FingerprintJobStatus.COMPLETED
            self._db.commit()
        except Exception as exc:
            logger.error("Failed to persist FingerprintMatches: %s", exc)
            if self._db:
                self._db.rollback()

    # ------------------------------------------------------------------
    # Property accessors
    # ------------------------------------------------------------------

    @property
    def registered_providers(self) -> list[str]:
        return list(self._registry.keys())

    def circuit_breaker_status(self) -> list[dict]:
        """Return circuit-breaker state for all registered providers."""
        return self._cb_registry.all_statuses()

    async def aclose(self) -> None:
        for adapter in self._registry.values():
            await adapter.aclose()
