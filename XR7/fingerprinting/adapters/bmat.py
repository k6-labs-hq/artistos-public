"""BMAT Musiio fingerprinting provider adapter.

BMAT acquired Musiio in 2021.  The combined platform exposes a REST API
with Bearer-token authentication.

Supported operations:
    POST /detect          — synchronous audio identification
    POST /catalog         — register a reference track
    GET  /catalog/{id}/events — monitoring / usage events
    GET  /health          — service health probe

Set XR7_BMAT_ENABLED=1 and BMAT_API_KEY=<key> to activate.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import httpx

from XR7.fingerprinting._resilience import (
    ProviderCircuitOpenError,
    get_circuit_registry,
    get_rate_limiter,
)
from XR7.fingerprinting.config import BMATConfig
from XR7.fingerprinting.interface import IFingerprintingProvider
from XR7.fingerprinting.schema import (
    AnomalyType,
    MatchType,
    NormalizedMatchResult,
    ProviderHealthStatus,
    ProviderStatus,
    RoyaltyStatus,
)
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# BMAT detection_type → XR7 MatchType
_BMAT_MATCH_TYPE_MAP: dict[str, MatchType] = {
    "broadcast": MatchType.BROADCAST,
    "radio": MatchType.RADIO,
    "streaming": MatchType.STREAM,
    "stream": MatchType.STREAM,
    "sync": MatchType.SYNC,
    "ugc": MatchType.UGC,
    "live": MatchType.LIVE,
    "social": MatchType.UGC,
    "digital": MatchType.STREAM,
}


class BMATAdapter(IFingerprintingProvider):
    """Provider adapter for BMAT Musiio audio recognition API.

    Authentication: ``Authorization: Bearer {api_key}``

    The identify endpoint (``/detect``) is synchronous.  Reference registration
    (``/catalog``) returns a ``track_id`` usable for monitoring queries.
    """

    def __init__(self, config: BMATConfig | None = None) -> None:
        from XR7.fingerprinting.config import fingerprinting_config

        self._cfg = config or fingerprinting_config.bmat
        self._client: httpx.AsyncClient | None = None
        self._cb = get_circuit_registry().get(self.provider_name)
        self._limiter = get_rate_limiter(
            self.provider_name, self._cfg.rate_limit_per_minute
        )

    @property
    def provider_name(self) -> str:
        return "bmat"

    def _client_(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._cfg.timeout_seconds,
                headers={
                    "Authorization": f"Bearer {self._cfg.api_key}",
                    "Accept": "application/json",
                    "User-Agent": "XR7-FingerprintingEngine/1.0",
                },
            )
        return self._client

    async def _guarded(self, coro):
        """Wrap a provider call with circuit-breaker + rate-limiter guards."""
        if self._cb.is_open():
            raise ProviderCircuitOpenError(self.provider_name)
        await self._limiter.acquire()
        try:
            result = await coro
            self._cb.record_success()
            return result
        except Exception:
            self._cb.record_failure()
            raise

    async def submit_audio_fingerprint(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        results = await self.match_audio(audio_data, metadata=metadata)
        return results[0].track_id or "no-match" if results else "no-match"

    async def submit_reference_file(
        self,
        audio_data: bytes,
        *,
        isrc: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Register a reference track in BMAT's catalog."""
        client = self._client_()
        form_data: dict[str, str] = {}
        if isrc:
            form_data["isrc"] = isrc
        if metadata:
            form_data.update({k: str(v) for k, v in metadata.items() if isinstance(v, (str, int, float))})

        endpoint = f"{self._cfg.endpoint}/catalog"
        response = await self._guarded(
            client.post(
                endpoint,
                files={"audio": ("reference.wav", audio_data, "audio/wav")},
                data=form_data,
            )
        )
        response.raise_for_status()
        data = response.json()
        track_id: str = data.get("track_id") or data.get("id") or data.get("musiio_id") or "unknown"
        logger.info("BMAT: registered reference track_id=%s isrc=%s", track_id, isrc)
        return track_id

    async def match_audio(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[NormalizedMatchResult]:
        """Identify audio via BMAT /detect."""
        client = self._client_()
        form_data: dict[str, str] = {}
        if metadata:
            form_data.update({k: str(v) for k, v in metadata.items() if isinstance(v, (str, int, float))})

        endpoint = f"{self._cfg.endpoint}/detect"
        try:
            response = await self._guarded(
                client.post(
                    endpoint,
                    files={"audio": ("sample.wav", audio_data, "audio/wav")},
                    data=form_data,
                )
            )
            response.raise_for_status()
            raw = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("BMAT HTTP error status=%d url=%s", exc.response.status_code, endpoint)
            raise
        except httpx.TimeoutException:
            logger.error("BMAT detect request timed out endpoint=%s", endpoint)
            raise

        return self.normalize_provider_response(raw)

    async def detect_usage(
        self,
        reference_id: str,
        *,
        territory: str | None = None,
    ) -> list[NormalizedMatchResult]:
        """Fetch monitoring events for a BMAT-registered reference track."""
        client = self._client_()
        params: dict[str, str] = {}
        if territory:
            params["territory"] = territory

        endpoint = f"{self._cfg.endpoint}/catalog/{reference_id}/events"
        try:
            response = await self._guarded(
                client.get(endpoint, params=params)
            )
            response.raise_for_status()
            raw = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("BMAT detect_usage HTTP error: %s", exc)
            raise

        events: list[dict[str, Any]] = raw.get("events", []) or raw.get("matches", [])
        results: list[NormalizedMatchResult] = []
        for evt in events:
            det_type = (evt.get("detection_type") or evt.get("type") or "").lower()
            results.append(
                NormalizedMatchResult(
                    track_id=reference_id,
                    isrc=evt.get("isrc"),
                    iswc=evt.get("iswc"),
                    confidence_score=float(evt.get("confidence", 1.0)),
                    match_type=_BMAT_MATCH_TYPE_MAP.get(det_type, MatchType.UNKNOWN),
                    platform=evt.get("channel") or evt.get("platform"),
                    territory=territory or evt.get("territory") or evt.get("country"),
                    timestamp=datetime.now(timezone.utc),
                    provider=self.provider_name,
                    royalty_status=RoyaltyStatus.UNKNOWN,
                    anomaly_type=AnomalyType.NONE,
                    title=evt.get("title"),
                    artist_name=evt.get("artist"),
                    raw_provider_payload=evt,
                )
            )
        return results

    async def get_match_results(self, job_id: str) -> list[NormalizedMatchResult]:
        """BMAT /detect is synchronous; polls /catalog/{job_id}/events as fallback."""
        try:
            return await self.detect_usage(job_id)
        except Exception as exc:
            logger.warning("BMAT get_match_results job_id=%s: %s", job_id, exc)
            return []

    async def get_provider_health(self) -> ProviderHealthStatus:
        client = self._client_()
        start = time.monotonic()
        endpoint = f"{self._cfg.endpoint}/health"
        try:
            response = await client.get(endpoint, timeout=5.0)
            latency_ms = (time.monotonic() - start) * 1000.0
            status = (
                ProviderStatus.HEALTHY if response.status_code < 500 else ProviderStatus.DEGRADED
            )
            return ProviderHealthStatus(
                provider=self.provider_name,
                status=status,
                latency_ms=latency_ms,
                checked_at=datetime.now(timezone.utc),
            )
        except Exception as exc:
            latency_ms = (time.monotonic() - start) * 1000.0
            logger.warning("BMAT health check failed: %s", exc)
            return ProviderHealthStatus(
                provider=self.provider_name,
                status=ProviderStatus.DOWN,
                latency_ms=latency_ms,
                error_message=str(exc),
                checked_at=datetime.now(timezone.utc),
            )

    def normalize_provider_response(
        self, raw: dict[str, Any]
    ) -> list[NormalizedMatchResult]:
        """Normalize BMAT /detect response.

        Expected shape::

            {
              "status": "success",
              "matches": [
                {
                  "track_id": "bmat-12345",
                  "isrc": "USAT12345678",
                  "title": "Song Title",
                  "artist": "Artist Name",
                  "confidence": 0.95,
                  "detection_type": "broadcast",
                  "territory": "US"
                }
              ]
            }
        """
        status = raw.get("status", "")
        if status not in ("success", "ok", "completed", ""):
            logger.debug("BMAT: non-success status=%s", status)
            return []

        raw_matches: list[dict[str, Any]] = (
            raw.get("matches") or raw.get("results") or raw.get("detections") or []
        )
        results: list[NormalizedMatchResult] = []
        for item in raw_matches:
            confidence = float(item.get("confidence", 0.0))
            det_type = (item.get("detection_type") or item.get("type") or "").lower()
            results.append(
                NormalizedMatchResult(
                    track_id=item.get("track_id") or item.get("musiio_id") or item.get("id"),
                    isrc=item.get("isrc"),
                    iswc=item.get("iswc"),
                    confidence_score=min(confidence, 1.0),
                    match_type=_BMAT_MATCH_TYPE_MAP.get(det_type, MatchType.UNKNOWN),
                    platform=item.get("platform") or item.get("channel"),
                    territory=item.get("territory") or item.get("country"),
                    timestamp=datetime.now(timezone.utc),
                    provider=self.provider_name,
                    royalty_status=RoyaltyStatus.UNKNOWN,
                    anomaly_type=AnomalyType.NONE,
                    title=item.get("title"),
                    artist_name=item.get("artist") or item.get("artist_name"),
                    duration_seconds=(
                        item.get("duration_seconds")
                        or (item.get("duration_ms") / 1000.0 if item.get("duration_ms") else None)
                        or item.get("duration")
                    ),
                    raw_provider_payload=item,
                )
            )
        return results

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
