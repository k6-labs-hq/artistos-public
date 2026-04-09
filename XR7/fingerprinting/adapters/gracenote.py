"""Gracenote MusicID / Media Recognition adapter.

Gracenote uses Client ID + User ID header authentication.  The API
returns JSON when the ``Accept: application/json`` header is sent.

Docs: https://developer.gracenote.com/web-api
Phase 4 provider.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import httpx

from XR7.fingerprinting.config import GracenoteConfig
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

_GN_MATCH_TYPE_MAP: dict[str, MatchType] = {
    "BROADCAST": MatchType.BROADCAST,
    "RADIO": MatchType.RADIO,
    "STREAM": MatchType.STREAM,
    "LIVE": MatchType.LIVE,
}


class GracenoteAdapter(IFingerprintingProvider):
    """Adapter for Gracenote MusicID content recognition service (Phase 4).

    Supports:
    - Audio fingerprint recognition
    - Reference content registration
    - Usage monitoring
    - Client ID / User ID authentication via request headers
    """

    def __init__(self, config: GracenoteConfig | None = None) -> None:
        from XR7.fingerprinting.config import fingerprinting_config

        self._cfg = config or fingerprinting_config.gracenote
        self._client: httpx.AsyncClient | None = None

    @property
    def provider_name(self) -> str:
        return "gracenote"

    def _client_(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._cfg.timeout_seconds,
                headers={
                    "X-GN-Client-ID": self._cfg.client_id,
                    "X-GN-User-ID": self._cfg.user_id,
                    "X-GN-API-Key": self._cfg.api_key,
                    "Accept": "application/json",
                    "User-Agent": "XR7-FingerprintingEngine/1.0",
                },
            )
        return self._client

    async def submit_audio_fingerprint(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        results = await self.match_audio(audio_data, metadata=metadata)
        if results:
            return results[0].track_id or "no-match"
        return "no-match"

    async def submit_reference_file(
        self,
        audio_data: bytes,
        *,
        isrc: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Register a reference track in Gracenote's content library."""
        client = self._client_()
        payload: dict[str, Any] = {}
        if isrc:
            payload["isrc"] = isrc
        if metadata:
            payload.update(metadata)

        endpoint = f"{self._cfg.endpoint}/references"
        response = await client.post(
            endpoint,
            files={"audio": ("reference.wav", audio_data, "audio/wav")},
            data=payload,
        )
        response.raise_for_status()
        data = response.json()
        ref_id: str = data.get("reference_id") or data.get("gn_id") or data.get("id") or "unknown"
        logger.info("Gracenote: registered reference ref_id=%s isrc=%s", ref_id, isrc)
        return ref_id

    async def match_audio(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[NormalizedMatchResult]:
        """Identify audio via Gracenote MusicID."""
        client = self._client_()
        payload: dict[str, Any] = {}
        if metadata:
            payload.update(metadata)

        endpoint = f"{self._cfg.endpoint}/recognize"
        try:
            response = await client.post(
                endpoint,
                files={"audio": ("sample.wav", audio_data, "audio/wav")},
                data=payload,
            )
            response.raise_for_status()
            raw = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Gracenote HTTP error status=%s", exc.response.status_code)
            raise
        except httpx.TimeoutException:
            logger.error("Gracenote recognize timed out endpoint=%s", endpoint)
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

        endpoint = f"{self._cfg.endpoint}/references/{reference_id}/detections"
        try:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            raw = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Gracenote detect_usage HTTP error: %s", exc)
            raise

        detections: list[dict[str, Any]] = raw.get("detections", [])
        results: list[NormalizedMatchResult] = []
        for det in detections:
            results.append(
                NormalizedMatchResult(
                    track_id=reference_id,
                    isrc=det.get("isrc"),
                    confidence_score=float(det.get("confidence", 1.0)),
                    match_type=_GN_MATCH_TYPE_MAP.get(det.get("match_type", ""), MatchType.UNKNOWN),
                    platform=det.get("channel") or det.get("service"),
                    territory=territory or det.get("territory"),
                    timestamp=datetime.now(timezone.utc),
                    provider=self.provider_name,
                    royalty_status=RoyaltyStatus.UNKNOWN,
                    anomaly_type=AnomalyType.NONE,
                    raw_provider_payload=det,
                )
            )
        return results

    async def get_match_results(self, job_id: str) -> list[NormalizedMatchResult]:
        """Poll an async recognition job result."""
        client = self._client_()
        endpoint = f"{self._cfg.endpoint}/jobs/{job_id}/results"
        try:
            response = await client.get(endpoint)
            response.raise_for_status()
            raw = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Gracenote get_match_results HTTP error job_id=%s: %s", job_id, exc)
            raise
        return self.normalize_provider_response(raw)

    async def get_provider_health(self) -> ProviderHealthStatus:
        client = self._client_()
        start = time.monotonic()
        try:
            response = await client.get(f"{self._cfg.endpoint}/health", timeout=5.0)
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
            return ProviderHealthStatus(
                provider=self.provider_name,
                status=ProviderStatus.DOWN,
                latency_ms=latency_ms,
                error_message=str(exc),
                checked_at=datetime.now(timezone.utc),
            )

    def normalize_provider_response(self, raw: dict[str, Any]) -> list[NormalizedMatchResult]:
        """Normalize Gracenote JSON recognition response.

        Expected shape::

            {
              "status": "OK",
              "results": [
                {
                  "gn_id": "...",
                  "isrc": "...",
                  "title": "...",
                  "artist": "...",
                  "confidence": 0.95,
                  "match_type": "BROADCAST",
                  "territory": "US"
                }
              ]
            }
        """
        if raw.get("status") not in ("OK", "SUCCESS", None):
            logger.debug("Gracenote: non-OK status=%s", raw.get("status"))
            return []

        raw_results: list[dict[str, Any]] = raw.get("results") or raw.get("matches") or []
        results: list[NormalizedMatchResult] = []

        for item in raw_results:
            confidence = float(item.get("confidence", 0.0))
            results.append(
                NormalizedMatchResult(
                    track_id=item.get("gn_id") or item.get("id"),
                    isrc=item.get("isrc"),
                    iswc=item.get("iswc"),
                    confidence_score=min(confidence, 1.0),
                    match_type=_GN_MATCH_TYPE_MAP.get(
                        item.get("match_type", ""), MatchType.UNKNOWN
                    ),
                    platform=item.get("platform") or item.get("channel"),
                    territory=item.get("territory"),
                    timestamp=datetime.now(timezone.utc),
                    provider=self.provider_name,
                    royalty_status=RoyaltyStatus.UNKNOWN,
                    anomaly_type=AnomalyType.NONE,
                    title=item.get("title"),
                    artist_name=item.get("artist"),
                    duration_seconds=item.get("duration_seconds"),
                    raw_provider_payload=item,
                )
            )
        return results

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
