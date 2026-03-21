"""Integration tests for the FingerprintingOrchestrator."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tests.fingerprinting.mocks.mock_provider import MockFingerprintingProvider
from XR7.fingerprinting.orchestrator import (
    FingerprintingOrchestrator,
    _dedup_results,
)
from XR7.fingerprinting.schema import (
    AnomalyType,
    FingerprintSubmitRequest,
    MatchType,
    NormalizedMatchResult,
    ProviderStatus,
    RoyaltyStatus,
)


def _make_result(
    isrc: str,
    provider: str,
    confidence: float = 0.9,
) -> NormalizedMatchResult:
    return NormalizedMatchResult(
        isrc=isrc,
        track_id=f"track-{isrc}",
        confidence_score=confidence,
        match_type=MatchType.STREAM,
        platform="spotify",
        territory="US",
        timestamp=datetime.now(timezone.utc),
        provider=provider,
        royalty_status=RoyaltyStatus.UNKNOWN,
        anomaly_type=AnomalyType.NONE,
    )


class TestDeduplication:
    def test_dedup_keeps_highest_confidence(self):
        r1 = _make_result("USAT001", "acrcloud", confidence=0.8)
        r2 = _make_result("USAT001", "acrcloud", confidence=0.95)
        deduped = _dedup_results([r1, r2])
        assert len(deduped) == 1
        assert deduped[0].confidence_score == pytest.approx(0.95)

    def test_dedup_different_providers_kept_separately(self):
        r1 = _make_result("USAT001", "acrcloud", confidence=0.9)
        r2 = _make_result("USAT001", "gracenote", confidence=0.85)
        deduped = _dedup_results([r1, r2])
        assert len(deduped) == 2

    def test_dedup_returns_sorted_by_confidence(self):
        r1 = _make_result("USAT001", "acrcloud", confidence=0.7)
        r2 = _make_result("USAT002", "gracenote", confidence=0.95)
        deduped = _dedup_results([r1, r2])
        assert deduped[0].confidence_score > deduped[1].confidence_score

    def test_dedup_empty_list(self):
        assert _dedup_results([]) == []


class TestOrchestratorRegistration:
    def test_registered_providers_with_mock(self):
        orchestrator = FingerprintingOrchestrator(db=None)
        # No providers enabled in test env — registry is empty
        assert isinstance(orchestrator.registered_providers, list)


class TestOrchestratorIdentifyWithMock:
    @pytest.mark.asyncio
    async def test_identify_returns_results_from_mock(self):
        mock = MockFingerprintingProvider(provider_name="mock")
        orchestrator = FingerprintingOrchestrator(db=None)
        # Inject mock directly into registry
        orchestrator._registry = {"mock": mock}

        request = FingerprintSubmitRequest(
            artist_id="artist-001",
            providers=["mock"],
        )
        results = await orchestrator.identify(b"audio_bytes", request)
        assert len(results) >= 1
        assert results[0].provider == "mock"

    @pytest.mark.asyncio
    async def test_identify_filters_low_confidence(self):
        from XR7.fingerprinting.config import FingerprintingOrchestratorConfig

        low_conf_result = _make_result("USAT001", "mock", confidence=0.1)
        mock = MockFingerprintingProvider()
        mock.set_results([low_conf_result])

        orchestrator = FingerprintingOrchestrator(db=None)
        orchestrator._registry = {"mock": mock}
        # Force high threshold
        orchestrator._cfg.orchestrator.__class__.min_confidence_threshold = property(
            lambda self: 0.5
        )
        request = FingerprintSubmitRequest(
            artist_id="artist-001",
            providers=["mock"],
        )
        # With default threshold 0.5, low_conf_result (0.1) should be filtered
        results = await orchestrator.identify(b"audio", request)
        filtered = [r for r in results if r.confidence_score < 0.5]
        assert len(filtered) == 0

    @pytest.mark.asyncio
    async def test_identify_with_unhealthy_provider_falls_back(self):
        failing_mock = MockFingerprintingProvider(provider_name="failing")

        async def raise_error(audio_data, *, metadata=None):
            raise RuntimeError("provider unavailable")

        failing_mock.match_audio = raise_error  # type: ignore[method-assign]

        good_mock = MockFingerprintingProvider(provider_name="good")

        orchestrator = FingerprintingOrchestrator(db=None)
        orchestrator._registry = {
            "failing": failing_mock,
            "good": good_mock,
        }
        orchestrator._cfg.orchestrator.__class__.multi_provider_aggregation = property(
            lambda self: False
        )

        request = FingerprintSubmitRequest(
            artist_id="artist-001",
            providers=["failing", "good"],
        )
        results = await orchestrator.identify(b"audio", request)
        providers_used = {r.provider for r in results}
        assert "good" in providers_used

    @pytest.mark.asyncio
    async def test_health_check_all(self):
        mock = MockFingerprintingProvider(provider_name="mock", healthy=True)
        orchestrator = FingerprintingOrchestrator(db=None)
        orchestrator._registry = {"mock": mock}

        statuses = await orchestrator.health_check_all()
        assert len(statuses) == 1
        assert statuses[0].status == ProviderStatus.HEALTHY
