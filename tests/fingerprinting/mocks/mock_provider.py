"""In-memory mock fingerprinting provider for CI / unit tests.

The MockFingerprintingProvider lets tests inject deterministic results
without network calls.  It fully implements IFingerprintingProvider.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from XR7.fingerprinting.interface import IFingerprintingProvider
from XR7.fingerprinting.schema import (
    AnomalyType,
    MatchType,
    NormalizedMatchResult,
    ProviderHealthStatus,
    ProviderStatus,
    RoyaltyStatus,
)


def _default_result(provider: str = "mock") -> NormalizedMatchResult:
    return NormalizedMatchResult(
        track_id="mock-track-001",
        isrc="USAT12345678",
        iswc="T-123456789-0",
        confidence_score=0.95,
        match_type=MatchType.STREAM,
        platform="spotify",
        territory="US",
        timestamp=datetime.now(timezone.utc),
        provider=provider,
        royalty_status=RoyaltyStatus.UNKNOWN,
        anomaly_type=AnomalyType.NONE,
        title="Mock Track Title",
        artist_name="Mock Artist",
        duration_seconds=210.0,
        raw_provider_payload={"mock": True},
    )


class MockFingerprintingProvider(IFingerprintingProvider):
    """Deterministic in-memory provider for testing.

    Usage::

        provider = MockFingerprintingProvider()
        provider.set_results([my_result])   # inject custom results
        results = await provider.match_audio(b"audio_bytes")
    """

    def __init__(
        self,
        provider_name: str = "mock",
        healthy: bool = True,
        results: list[NormalizedMatchResult] | None = None,
    ) -> None:
        self._provider_name = provider_name
        self._healthy = healthy
        self._results: list[NormalizedMatchResult] = results or [
            _default_result(provider_name)
        ]
        self.call_log: list[dict[str, Any]] = []

    @property
    def provider_name(self) -> str:
        return self._provider_name

    def set_results(self, results: list[NormalizedMatchResult]) -> None:
        self._results = results

    def set_healthy(self, healthy: bool) -> None:
        self._healthy = healthy

    # ------------------------------------------------------------------
    # IFingerprintingProvider implementation
    # ------------------------------------------------------------------

    async def submit_audio_fingerprint(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        self.call_log.append({"method": "submit_audio_fingerprint", "len": len(audio_data)})
        return self._results[0].track_id or "mock-job-001"

    async def submit_reference_file(
        self,
        audio_data: bytes,
        *,
        isrc: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        self.call_log.append({"method": "submit_reference_file", "isrc": isrc})
        return "mock-ref-001"

    async def match_audio(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[NormalizedMatchResult]:
        self.call_log.append({"method": "match_audio", "len": len(audio_data)})
        return list(self._results)

    async def detect_usage(
        self,
        reference_id: str,
        *,
        territory: str | None = None,
    ) -> list[NormalizedMatchResult]:
        self.call_log.append(
            {"method": "detect_usage", "reference_id": reference_id, "territory": territory}
        )
        return list(self._results)

    async def get_match_results(self, job_id: str) -> list[NormalizedMatchResult]:
        self.call_log.append({"method": "get_match_results", "job_id": job_id})
        return list(self._results)

    async def get_provider_health(self) -> ProviderHealthStatus:
        self.call_log.append({"method": "get_provider_health"})
        return ProviderHealthStatus(
            provider=self._provider_name,
            status=ProviderStatus.HEALTHY if self._healthy else ProviderStatus.DOWN,
            latency_ms=5.0,
            error_message=None if self._healthy else "Mock provider is unhealthy",
            checked_at=datetime.now(timezone.utc),
        )

    def normalize_provider_response(
        self, raw: dict[str, Any]
    ) -> list[NormalizedMatchResult]:
        return list(self._results)
