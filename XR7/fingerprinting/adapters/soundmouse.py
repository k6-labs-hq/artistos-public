"""Soundmouse audio fingerprinting provider adapter.

Soundmouse is a UK-based music identification and monitoring service.
Authentication uses an API key in the ``X-SM-API-Key`` header.

Supported operations:
    POST /audio/identify     — synchronous audio identification
    POST /catalog            — register a reference track
    GET  /catalog/{id}/detections — monitoring / usage detections
    GET  /health             — service health probe

Set XR7_SOUNDMOUSE_ENABLED=1 and SOUNDMOUSE_API_KEY=<key> to activate.
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
from XR7.fingerprinting.config import SoundmouseConfig
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

_SM_MATCH_TYPE_MAP: dict[str, MatchType] = {
    "broadcast": MatchType.BROADCAST,
    "radio": MatchType.RADIO,
    "stream": MatchType.STREAM,
    "streaming": MatchType.STREAM,
    "ugc": MatchType.UGC,
    "user_generated": MatchType.UGC,
    "sync": MatchType.SYNC,
    "live": MatchType.LIVE,
}


class SoundmouseAdapter(IFingerprintingProvider):
    """Provider adapter for Soundmouse audio identification service.

    Authentication: ``X-SM-API-Key: {api_key}`` request header.

    The ``/audio/identify`` endpoint is synchronous.  Reference tracks are
    registered via ``/catalog`` and detections are retrieved with
    ``GET /catalog/{ref_id}/detections``.
    """

    def __init__(self, config: SoundmouseConfig | None = None) -> None:
        from XR7.fingerprinting.config import fingerprinting_config

        self._cfg = config or fingerprinting_config.soundmouse
        self._client: httpx.AsyncClient | None = None
        self._cb = get_circuit_registry().get(self.provider_name)
        self._limiter = get_rate_limiter(
            self.provider_name, self._cfg.rate_limit_per_minute
        )

    @property
    def provider_name(self) -> str:
        return "soundmouse"

    def _client_(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._cfg.timeout_seconds,
                headers={
                    "X-SM-API-Key": self._cfg.api_key,
                    "Accept": "application/json",
                    "User-Agent": "XR7-FingerprintingEngine/1.0",
                },
            )
        return self._client

    async def _guarded(self, coro):
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
        """Register a reference track in Soundmouse's catalog."""
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
        ref_id: str = data.get("ref_id") or data.get("id") or data.get("track_id") or "unknown"
        logger.info("Soundmouse: registered reference ref_id=%s isrc=%s", ref_id, isrc)
        return ref_id

    async def match_audio(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[NormalizedMatchResult]:
        """Identify audio via Soundmouse /audio/identify."""
        client = self._client_()
        form_data: dict[str, str] = {}
        if metadata:
            form_data.update({k: str(v) for k, v in metadata.items() if isinstance(v, (str, int, float))})

        endpoint = f"{self._cfg.endpoint}/audio/identify"
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
            logger.error("Soundmouse HTTP error status=%d url=%s", exc.response.status_code, endpoint)
            raise
        except httpx.TimeoutException:
            logger.error("Soundmouse identify request timed out endpoint=%s", endpoint)
            raise

        return self.normalize_provider_response(raw)

    async def detect_usage(
        self,
        reference_id: str,
        *,
        territory: str | None = None,
    ) -> list[NormalizedMatchResult]:
        """Retrieve monitoring detections for a registered reference."""
        client = self._client_()
        params: dict[str, str] = {}
        if territory:
            params["territory"] = territory

        endpoint = f"{self._cfg.endpoint}/catalog/{reference_id}/detections"
        try:
            response = await self._guarded(
                client.get(endpoint, params=params)
            )
            response.raise_for_status()
            raw = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Soundmouse detect_usage HTTP error: %s", exc)
            raise

        detections: list[dict[str, Any]] = raw.get("detections", []) or raw.get("matches", [])
        results: list[NormalizedMatchResult] = []
        for det in detections:
            det_type = (det.get("type") or det.get("detection_type") or "").lower()
            results.append(
                NormalizedMatchResult(
                    track_id=reference_id,
                    isrc=det.get("isrc"),
                    iswc=det.get("iswc"),
                    confidence_score=float(det.get("confidence", 1.0)),
                    match_type=_SM_MATCH_TYPE_MAP.get(det_type, MatchType.UNKNOWN),
                    platform=det.get("platform") or det.get("channel") or det.get("service"),
                    territory=territory or det.get("territory") or det.get("country"),
                    timestamp=datetime.now(timezone.utc),
                    provider=self.provider_name,
                    royalty_status=RoyaltyStatus.UNKNOWN,
                    anomaly_type=AnomalyType.NONE,
                    title=det.get("title"),
                    artist_name=det.get("artist"),
                    raw_provider_payload=det,
                )
            )
        return results

    async def get_match_results(self, job_id: str) -> list[NormalizedMatchResult]:
        """Soundmouse identify is synchronous; poll detections for tracking."""
        try:
            return await self.detect_usage(job_id)
        except Exception as exc:
            logger.warning("Soundmouse get_match_results job_id=%s: %s", job_id, exc)
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
            logger.warning("Soundmouse health check failed: %s", exc)
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
        """Normalize Soundmouse /audio/identify response.

        Expected shape::

            {
              "status": "success",
              "matches": [
                {
                  "ref_id": "sm-abc",
                  "isrc": "GBXXX1234567",
                  "title": "Track Title",
                  "artist": "Artist Name",
                  "confidence": 0.92,
                  "type": "broadcast",
                  "territory": "GB"
                }
              ]
            }
        """
        status = raw.get("status", "")
        if status not in ("success", "ok", "found", ""):
            logger.debug("Soundmouse: non-success status=%s", status)
            return []

        raw_matches: list[dict[str, Any]] = (
            raw.get("matches") or raw.get("results") or []
        )
        results: list[NormalizedMatchResult] = []
        for item in raw_matches:
            confidence = float(item.get("confidence", 0.0))
            det_type = (item.get("type") or item.get("detection_type") or "").lower()
            results.append(
                NormalizedMatchResult(
                    track_id=item.get("ref_id") or item.get("track_id") or item.get("id"),
                    isrc=item.get("isrc"),
                    iswc=item.get("iswc"),
                    confidence_score=min(confidence, 1.0),
                    match_type=_SM_MATCH_TYPE_MAP.get(det_type, MatchType.UNKNOWN),
                    platform=item.get("platform") or item.get("service") or item.get("channel"),
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
