"""ACRCloud audio fingerprinting provider adapter.

ACRCloud uses HMAC-SHA1 request signing.  Each audio identify call is
synchronous (response returned inline) while reference-track registration
returns an ``audio_id``.

Docs: https://docs.acrcloud.com/reference/identification-api
Phase 2 provider.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from XR7.fingerprinting.config import ACRCloudConfig
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

_SIGNATURE_VERSION = "1"
_DATA_TYPE_AUDIO = "audio"


class ACRCloudAdapter(IFingerprintingProvider):
    """Adapter for the ACRCloud Audio Recognition Service (Phase 2).

    Supports:
    - Real-time audio identification via ``/v1/identify``
    - Custom content library registration via ``/v1/audios``
    - Broadcast monitoring via ``/v1/audios/{id}/events``
    - HMAC-SHA1 per-request authentication
    - Async and batch modes
    """

    def __init__(self, config: ACRCloudConfig | None = None) -> None:
        from XR7.fingerprinting.config import fingerprinting_config

        self._cfg = config or fingerprinting_config.acrcloud
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # IFingerprintingProvider identity
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "acrcloud"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _client_(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._cfg.timeout_seconds,
                headers={"User-Agent": "XR7-FingerprintingEngine/1.0"},
            )
        return self._client

    def _sign(self, method: str, uri: str, data_type: str, timestamp: str) -> str:
        string_to_sign = "\n".join(
            [method, uri, self._cfg.access_key, data_type, _SIGNATURE_VERSION, timestamp]
        )
        digest = hmac.new(
            self._cfg.access_secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha1,
        ).digest()
        return base64.b64encode(digest).decode("utf-8")

    def _identify_params(self, audio_len: int, timestamp: str) -> dict[str, str]:
        return {
            "access_key": self._cfg.access_key,
            "data_type": _DATA_TYPE_AUDIO,
            "signature_version": _SIGNATURE_VERSION,
            "signature": self._sign("POST", "/v1/identify", _DATA_TYPE_AUDIO, timestamp),
            "sample_bytes": str(audio_len),
            "timestamp": timestamp,
        }

    # ------------------------------------------------------------------
    # IFingerprintingProvider implementation
    # ------------------------------------------------------------------

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
        """Register a track in ACRCloud's custom content library."""
        client = self._client_()
        timestamp = str(int(time.time()))
        http_uri = "/v1/audios"
        params: dict[str, str] = {
            "access_key": self._cfg.access_key,
            "data_type": _DATA_TYPE_AUDIO,
            "signature_version": _SIGNATURE_VERSION,
            "signature": self._sign("POST", http_uri, _DATA_TYPE_AUDIO, timestamp),
            "timestamp": timestamp,
        }
        if isrc:
            params["isrc"] = isrc
        if metadata:
            for k, v in metadata.items():
                params[k] = str(v)

        files = {"file": ("reference.wav", audio_data, "audio/wav")}
        endpoint = f"{self._cfg.endpoint}{http_uri}"
        response = await client.post(endpoint, data=params, files=files)
        response.raise_for_status()
        result = response.json()
        audio_id: str = result.get("audio_id") or result.get("id") or "unknown"
        logger.info("ACRCloud: registered reference audio_id=%s isrc=%s", audio_id, isrc)
        return audio_id

    async def match_audio(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[NormalizedMatchResult]:
        """Identify audio via ACRCloud /v1/identify."""
        client = self._client_()
        timestamp = str(int(time.time()))
        params = self._identify_params(len(audio_data), timestamp)
        files = {"sample": ("sample.wav", audio_data, "audio/wav")}
        endpoint = f"{self._cfg.endpoint}/v1/identify"

        try:
            response = await client.post(endpoint, data=params, files=files)
            response.raise_for_status()
            raw = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "ACRCloud HTTP error status=%s url=%s", exc.response.status_code, endpoint
            )
            raise
        except httpx.TimeoutException:
            logger.error("ACRCloud identify request timed out endpoint=%s", endpoint)
            raise

        return self.normalize_provider_response(raw)

    async def detect_usage(
        self,
        reference_id: str,
        *,
        territory: str | None = None,
    ) -> list[NormalizedMatchResult]:
        """Fetch broadcast/monitoring events for a registered reference track."""
        client = self._client_()
        timestamp = str(int(time.time()))
        http_uri = f"/v1/audios/{reference_id}/events"
        params: dict[str, str] = {
            "access_key": self._cfg.access_key,
            "signature_version": _SIGNATURE_VERSION,
            "signature": self._sign("GET", http_uri, "events", timestamp),
            "timestamp": timestamp,
        }
        if territory:
            params["country"] = territory

        endpoint = f"{self._cfg.endpoint}{http_uri}"
        try:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            raw = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("ACRCloud detect_usage HTTP error: %s", exc)
            raise

        events: list[dict[str, Any]] = raw.get("events", [])
        results: list[NormalizedMatchResult] = []
        for evt in events:
            channel: str | None = evt.get("channel_name") or evt.get("channel")
            results.append(
                NormalizedMatchResult(
                    track_id=reference_id,
                    isrc=evt.get("isrc"),
                    confidence_score=1.0,
                    match_type=MatchType.BROADCAST,
                    platform=channel,
                    territory=territory or evt.get("country"),
                    timestamp=datetime.now(timezone.utc),
                    provider=self.provider_name,
                    royalty_status=RoyaltyStatus.UNKNOWN,
                    anomaly_type=AnomalyType.NONE,
                    raw_provider_payload=evt,
                )
            )
        return results

    async def get_match_results(self, job_id: str) -> list[NormalizedMatchResult]:
        """ACRCloud identify is synchronous — async polling is not supported."""
        logger.debug("ACRCloud does not support async job polling; job_id=%s", job_id)
        return []

    async def get_provider_health(self) -> ProviderHealthStatus:
        client = self._client_()
        start = time.monotonic()
        try:
            response = await client.head(self._cfg.endpoint, timeout=5.0)
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
            logger.warning("ACRCloud health check failed: %s", exc)
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
        """Normalize ACRCloud JSON identify response.

        Response shape::

            {
              "status": {"code": 0, "msg": "Success"},
              "metadata": {
                "music": [
                  {"acrid": "...", "title": "...", "score": 95,
                   "artists": [{"name": "..."}], "external_ids": {"isrc": "..."},
                   "duration_ms": 210000}
                ]
              }
            }
        """
        status = raw.get("status", {})
        if status.get("code") != 0:
            logger.debug(
                "ACRCloud: no match code=%s msg=%s",
                status.get("code"),
                status.get("msg"),
            )
            return []

        music_list: list[dict[str, Any]] = raw.get("metadata", {}).get("music", [])
        results: list[NormalizedMatchResult] = []

        for track in music_list:
            score_raw = track.get("score", 0)
            confidence = min(float(score_raw) / 100.0, 1.0)

            # Extract ISRC from external_ids map
            ext_ids: dict[str, str] = track.get("external_ids", {})
            isrc: str | None = ext_ids.get("isrc") or ext_ids.get("ISRC")

            artist_name: str = ", ".join(
                a.get("name", "") for a in track.get("artists", [])
            )
            duration_ms: int | None = track.get("duration_ms")

            results.append(
                NormalizedMatchResult(
                    track_id=track.get("acrid"),
                    isrc=isrc,
                    confidence_score=confidence,
                    match_type=MatchType.UNKNOWN,
                    timestamp=datetime.now(timezone.utc),
                    provider=self.provider_name,
                    royalty_status=RoyaltyStatus.UNKNOWN,
                    anomaly_type=AnomalyType.NONE,
                    title=track.get("title"),
                    artist_name=artist_name or None,
                    album=track.get("album", {}).get("name") if isinstance(track.get("album"), dict) else track.get("album"),
                    duration_seconds=duration_ms / 1000.0 if duration_ms else None,
                    raw_provider_payload=track,
                )
            )

        return results

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
