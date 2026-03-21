"""Pex fingerprinting provider adapter.

Pex is an AI-driven rights management platform with audio and video
fingerprinting capabilities.

Authentication: API-key-as-Bearer or OAuth2 client_credentials flow.
    If ``client_secret`` is configured, a session token is fetched
    automatically via ``POST /oauth2/token``.  Otherwise, ``api_key``
    is used directly as the Bearer token.

Supported operations:
    POST /identify           — synchronous audio identification
    POST /assets             — register a reference asset
    GET  /assets/{id}/occurrences — monitoring / usage occurrences
    GET  /health             — service health probe

Set XR7_PEX_ENABLED=1, PEX_API_KEY=<key> [+ PEX_CLIENT_SECRET=<secret>] to
activate.
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
from XR7.fingerprinting.config import PexConfig
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

_PEX_MATCH_TYPE_MAP: dict[str, MatchType] = {
    "broadcast": MatchType.BROADCAST,
    "radio": MatchType.RADIO,
    "online": MatchType.STREAM,
    "streaming": MatchType.STREAM,
    "ugc": MatchType.UGC,
    "user_generated": MatchType.UGC,
    "live": MatchType.LIVE,
    "sync": MatchType.SYNC,
    "social": MatchType.UGC,
}


class PexAdapter(IFingerprintingProvider):
    """Provider adapter for the Pex rights-management audio fingerprinting API.

    If ``PEX_CLIENT_SECRET`` is set, a session token is fetched via
    OAuth2 ``client_credentials`` and cached for the lifetime of the
    instance.  Otherwise ``PEX_API_KEY`` is used as a raw Bearer token.
    """

    def __init__(self, config: PexConfig | None = None) -> None:
        from XR7.fingerprinting.config import fingerprinting_config

        self._cfg = config or fingerprinting_config.pex
        self._client: httpx.AsyncClient | None = None
        self._access_token: str | None = None
        self._token_expiry: float = 0.0
        self._cb = get_circuit_registry().get(self.provider_name)
        self._limiter = get_rate_limiter(
            self.provider_name, self._cfg.rate_limit_per_minute
        )

    @property
    def provider_name(self) -> str:
        return "pex"

    def _http_client(self) -> httpx.AsyncClient:
        """Return a reusable httpx client (no auth headers — added per-request)."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._cfg.timeout_seconds,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "XR7-FingerprintingEngine/1.0",
                },
            )
        return self._client

    async def _bearer_token(self) -> str:
        """Return a valid Bearer token, refreshing via OAuth2 if needed."""
        client_secret = getattr(self._cfg, "client_secret", "")
        if not client_secret:
            # Direct API-key mode
            return self._cfg.api_key

        # OAuth2 client_credentials mode
        if self._access_token and time.monotonic() < self._token_expiry - 30:
            return self._access_token

        token_url = f"{self._cfg.endpoint}/oauth2/token"
        client = self._http_client()
        response = await client.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._cfg.api_key,
                "client_secret": client_secret,
            },
        )
        response.raise_for_status()
        token_data = response.json()
        self._access_token = token_data["access_token"]
        expires_in = int(token_data.get("expires_in", 3600))
        self._token_expiry = time.monotonic() + expires_in
        logger.debug("Pex: OAuth2 token refreshed expires_in=%ds", expires_in)
        return self._access_token

    async def _auth_headers(self) -> dict[str, str]:
        token = await self._bearer_token()
        return {"Authorization": f"Bearer {token}"}

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
        """Create a Pex asset and upload the reference audio."""
        client = self._http_client()
        auth = await self._auth_headers()

        asset_body: dict[str, Any] = {}
        if isrc:
            asset_body["isrc"] = isrc
        if metadata:
            asset_body.update({k: v for k, v in metadata.items()})

        # Step 1: Create asset record
        create_endpoint = f"{self._cfg.endpoint}/assets"
        response = await self._guarded(
            client.post(create_endpoint, json=asset_body, headers=auth)
        )
        response.raise_for_status()
        asset_id: str = response.json().get("asset_id") or response.json().get("id") or "unknown"

        # Step 2: Upload audio to asset
        upload_endpoint = f"{self._cfg.endpoint}/assets/{asset_id}/audio"
        upload_response = await self._guarded(
            client.put(
                upload_endpoint,
                content=audio_data,
                headers={**auth, "Content-Type": "audio/wav"},
            )
        )
        upload_response.raise_for_status()
        logger.info("Pex: registered reference asset_id=%s isrc=%s", asset_id, isrc)
        return asset_id

    async def match_audio(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[NormalizedMatchResult]:
        """Identify audio via Pex /identify."""
        client = self._http_client()
        auth = await self._auth_headers()
        endpoint = f"{self._cfg.endpoint}/identify"

        try:
            response = await self._guarded(
                client.post(
                    endpoint,
                    files={"audio": ("sample.wav", audio_data, "audio/wav")},
                    headers=auth,
                )
            )
            response.raise_for_status()
            raw = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Pex HTTP error status=%d url=%s", exc.response.status_code, endpoint)
            raise
        except httpx.TimeoutException:
            logger.error("Pex identify request timed out endpoint=%s", endpoint)
            raise

        return self.normalize_provider_response(raw)

    async def detect_usage(
        self,
        reference_id: str,
        *,
        territory: str | None = None,
    ) -> list[NormalizedMatchResult]:
        """Retrieve usage occurrences for a Pex asset."""
        client = self._http_client()
        auth = await self._auth_headers()
        params: dict[str, str] = {}
        if territory:
            params["territory"] = territory

        endpoint = f"{self._cfg.endpoint}/assets/{reference_id}/occurrences"
        try:
            response = await self._guarded(
                client.get(endpoint, params=params, headers=auth)
            )
            response.raise_for_status()
            raw = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error("Pex detect_usage HTTP error: %s", exc)
            raise

        occurrences: list[dict[str, Any]] = (
            raw.get("occurrences") or raw.get("matches") or []
        )
        results: list[NormalizedMatchResult] = []
        for occ in occurrences:
            occ_type = (occ.get("type") or occ.get("match_type") or occ.get("detection_type") or "").lower()
            results.append(
                NormalizedMatchResult(
                    track_id=reference_id,
                    isrc=occ.get("isrc"),
                    iswc=occ.get("iswc"),
                    confidence_score=float(occ.get("confidence", 1.0)),
                    match_type=_PEX_MATCH_TYPE_MAP.get(occ_type, MatchType.UNKNOWN),
                    platform=occ.get("platform") or occ.get("channel") or occ.get("service"),
                    territory=territory or occ.get("territory") or occ.get("country"),
                    timestamp=datetime.now(timezone.utc),
                    provider=self.provider_name,
                    royalty_status=RoyaltyStatus.UNKNOWN,
                    anomaly_type=AnomalyType.NONE,
                    title=occ.get("title"),
                    artist_name=occ.get("artist"),
                    raw_provider_payload=occ,
                )
            )
        return results

    async def get_match_results(self, job_id: str) -> list[NormalizedMatchResult]:
        """Pex /identify is synchronous; poll occurrences as job result proxy."""
        try:
            return await self.detect_usage(job_id)
        except Exception as exc:
            logger.warning("Pex get_match_results job_id=%s: %s", job_id, exc)
            return []

    async def get_provider_health(self) -> ProviderHealthStatus:
        client = self._http_client()
        start = time.monotonic()
        endpoint = f"{self._cfg.endpoint}/health"
        try:
            auth = await self._bearer_token()
            response = await client.get(
                endpoint,
                headers={"Authorization": f"Bearer {auth}"},
                timeout=5.0,
            )
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
            logger.warning("Pex health check failed: %s", exc)
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
        """Normalize Pex /identify response.

        Expected shape::

            {
              "status": "success",
              "results": [
                {
                  "asset_id": "pex-abc",
                  "isrc": "USAT12345678",
                  "title": "Track Title",
                  "artist": "Artist Name",
                  "confidence": 0.97,
                  "type": "online",
                  "platform": "youtube",
                  "territory": "US"
                }
              ]
            }
        """
        status = raw.get("status", "")
        if status not in ("success", "ok", "found", ""):
            logger.debug("Pex: non-success status=%s", status)
            return []

        raw_results: list[dict[str, Any]] = (
            raw.get("results") or raw.get("matches") or raw.get("occurrences") or []
        )
        results: list[NormalizedMatchResult] = []
        for item in raw_results:
            confidence = float(item.get("confidence", 0.0))
            occ_type = (item.get("type") or item.get("match_type") or item.get("detection_type") or "").lower()
            results.append(
                NormalizedMatchResult(
                    track_id=item.get("asset_id") or item.get("track_id") or item.get("id"),
                    isrc=item.get("isrc"),
                    iswc=item.get("iswc"),
                    confidence_score=min(confidence, 1.0),
                    match_type=_PEX_MATCH_TYPE_MAP.get(occ_type, MatchType.UNKNOWN),
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
        self._access_token = None
