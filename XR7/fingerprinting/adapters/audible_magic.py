"""Audible Magic enterprise content recognition adapter.

Audible Magic uses bearer-token authentication and a REST JSON API.
This is a Phase 3 provider.

Docs: https://www.audiblemagic.com/compliance-service/
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import httpx

from XR7.fingerprinting.config import AudibleMagicConfig
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

# Audible Magic match-type → XR7 MatchType mapping
_AM_MATCH_TYPE_MAP: dict[str, MatchType] = {
    "broadcast": MatchType.BROADCAST,
    "radio": MatchType.RADIO,
    "ugc": MatchType.UGC,
    "sync": MatchType.SYNC,
    "stream": MatchType.STREAM,
    "live": MatchType.LIVE,
}


class AudibleMagicAdapter(IFingerprintingProvider):
    """Adapter for Audible Magic compliance / content recognition service (Phase 3).

    Supports:
    - Audio fingerprint submission and recognition
    - Reference track registration
    - Usage monitoring queries
    - Bearer token authentication
    """

    def __init__(self, config: AudibleMagicConfig | None = None) -> None:
        from XR7.fingerprinting.config import fingerprinting_config

        self._cfg = config or fingerprinting_config.audible_magic
        self._client: httpx.AsyncClient | None = None

    @property
    def provider_name(self) -> str:
        return "audible_magic"

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

    async def submit_audio_fingerprint(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Submit audio for async fingerprint processing; returns job_id."""
        client = self._client_()
        payload: dict[str, Any] = {"format": "wav"}
        if metadata:
            payload.update(metadata)

        endpoint = f"{self._cfg.endpoint}/recognize/submit"
        response = await client.post(
            endpoint,
            files={"audio": ("sample.wav", audio_data, "audio/wav")},
            data=payload,
        )
        response.raise_for_status()
        data = response.json()
        job_id: str = data.get("job_id") or data.get("id") or "unknown"
        logger.info("AudibleMagic: submitted fingerprint job_id=%s", job_id)
        return job_id

    async def submit_reference_file(
        self,
        audio_data: bytes,
        *,
        isrc: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Register a reference track in Audible Magic's reference library."""
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
        ref_id: str = data.get("reference_id") or data.get("id") or "unknown"
        logger.info(
            "AudibleMagic: registered reference ref_id=%s isrc=%s", ref_id, isrc
        )
        return ref_id

    async def match_audio(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[NormalizedMatchResult]:
        """Synchronous audio recognition call."""
        client = self._client_()
        payload: dict[str, Any] = {"synchronous": "true"}
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
            logger.error(
                "AudibleMagic HTTP error status=%s", exc.response.status_code
            )
            raise

        return self.normalize_provider_response(raw)

    async def detect_usage(
        self,
        reference_id: str,
        *,
        territory: str | None = None,
    ) -> list[NormalizedMatchResult]:
        """Retrieve monitoring events for a registered reference."""
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
            logger.error("AudibleMagic detect_usage HTTP error: %s", exc)
            raise

        detections: list[dict[str, Any]] = raw.get("detections", [])
        results: list[NormalizedMatchResult] = []
        for det in detections:
            results.append(
                NormalizedMatchResult(
                    track_id=reference_id,
                    isrc=det.get("isrc"),
                    confidence_score=float(det.get("confidence", 1.0)),
                    match_type=_AM_MATCH_TYPE_MAP.get(
                        det.get("detection_type", ""), MatchType.UNKNOWN
                    ),
                    platform=det.get("channel") or det.get("platform"),
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
        """Poll results for a previously submitted async fingerprint job."""
        client = self._client_()
        endpoint = f"{self._cfg.endpoint}/recognize/{job_id}/results"
        try:
            response = await client.get(endpoint)
            response.raise_for_status()
            raw = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "AudibleMagic get_match_results HTTP error job_id=%s: %s", job_id, exc
            )
            raise
        return self.normalize_provider_response(raw)

    async def get_provider_health(self) -> ProviderHealthStatus:
        client = self._client_()
        start = time.monotonic()
        try:
            response = await client.get(
                f"{self._cfg.endpoint}/health", timeout=5.0
            )
            latency_ms = (time.monotonic() - start) * 1000.0
            status = (
                ProviderStatus.HEALTHY
                if response.status_code < 500
                else ProviderStatus.DEGRADED
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

    def normalize_provider_response(
        self, raw: dict[str, Any]
    ) -> list[NormalizedMatchResult]:
        """Normalize Audible Magic recognition response.

        Expected shape::

            {
              "status": "success",
              "results": [
                {
                  "track_id": "am-12345",
                  "isrc": "USAT12345678",
                  "title": "...",
                  "artist": "...",
                  "confidence": 0.98,
                  "match_type": "broadcast",
                  "territory": "US"
                }
              ]
            }
        """
        if raw.get("status") not in ("success", "completed", None):
            logger.debug("AudibleMagic: non-success status=%s", raw.get("status"))
            return []

        raw_results: list[dict[str, Any]] = raw.get("results") or raw.get("matches") or []
        results: list[NormalizedMatchResult] = []

        for item in raw_results:
            confidence = float(item.get("confidence", 0.0))
            match_type_raw = item.get("match_type", "")
            results.append(
                NormalizedMatchResult(
                    track_id=item.get("track_id") or item.get("id"),
                    isrc=item.get("isrc"),
                    iswc=item.get("iswc"),
                    confidence_score=min(confidence, 1.0),
                    match_type=_AM_MATCH_TYPE_MAP.get(match_type_raw, MatchType.UNKNOWN),
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
