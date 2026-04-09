"""Contract tests for the normalized schema.

Verifies that the shared schema behaves predictably and that all provider
adapters produce outputs that conform to ``NormalizedMatchResult``.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from XR7.fingerprinting.schema import (
    AnomalyType,
    CatalogMatchResult,
    FingerprintSubmitRequest,
    MatchingEngineReport,
    MatchType,
    NormalizedMatchResult,
    ProviderHealthStatus,
    ProviderStatus,
    RoyaltyStatus,
)


class TestNormalizedMatchResultContract:
    def test_valid_result_constructs(self):
        r = NormalizedMatchResult(
            isrc="USAT12345678",
            confidence_score=0.95,
            timestamp=datetime.now(timezone.utc),
            provider="acrcloud",
        )
        assert r.provider == "acrcloud"
        assert r.confidence_score == pytest.approx(0.95)
        assert r.match_type == MatchType.UNKNOWN
        assert r.royalty_status == RoyaltyStatus.UNKNOWN
        assert r.anomaly_type == AnomalyType.NONE

    def test_confidence_rejects_above_1(self):
        with pytest.raises(ValidationError):
            NormalizedMatchResult(
                confidence_score=1.5,
                timestamp=datetime.now(timezone.utc),
                provider="test",
            )

    def test_confidence_rejects_below_0(self):
        with pytest.raises(ValidationError):
            NormalizedMatchResult(
                confidence_score=-0.1,
                timestamp=datetime.now(timezone.utc),
                provider="test",
            )

    def test_optional_fields_default_to_none(self):
        r = NormalizedMatchResult(
            timestamp=datetime.now(timezone.utc),
            provider="test",
        )
        assert r.isrc is None
        assert r.iswc is None
        assert r.ipi is None
        assert r.track_id is None
        assert r.platform is None
        assert r.territory is None
        assert r.title is None
        assert r.artist_name is None

    def test_raw_provider_payload_defaults_empty_dict(self):
        r = NormalizedMatchResult(
            timestamp=datetime.now(timezone.utc),
            provider="test",
        )
        assert r.raw_provider_payload == {}

    def test_all_match_types_valid(self):
        for mt in MatchType:
            r = NormalizedMatchResult(
                match_type=mt,
                timestamp=datetime.now(timezone.utc),
                provider="test",
            )
            assert r.match_type == mt

    def test_all_royalty_statuses_valid(self):
        for rs in RoyaltyStatus:
            r = NormalizedMatchResult(
                royalty_status=rs,
                timestamp=datetime.now(timezone.utc),
                provider="test",
            )
            assert r.royalty_status == rs

    def test_all_anomaly_types_valid(self):
        for at in AnomalyType:
            r = NormalizedMatchResult(
                anomaly_type=at,
                timestamp=datetime.now(timezone.utc),
                provider="test",
            )
            assert r.anomaly_type == at


class TestProviderHealthStatusContract:
    def test_healthy_status(self):
        h = ProviderHealthStatus(
            provider="acrcloud",
            status=ProviderStatus.HEALTHY,
            latency_ms=5.5,
            checked_at=datetime.now(timezone.utc),
        )
        assert h.status == ProviderStatus.HEALTHY
        assert h.error_message is None

    def test_down_status_with_error(self):
        h = ProviderHealthStatus(
            provider="acrcloud",
            status=ProviderStatus.DOWN,
            error_message="Connection refused",
            checked_at=datetime.now(timezone.utc),
        )
        assert h.error_message == "Connection refused"


class TestFingerprintSubmitRequestContract:
    def test_minimal_request(self):
        req = FingerprintSubmitRequest(artist_id="artist-001")
        assert req.artist_id == "artist-001"
        assert req.providers is None
        assert req.metadata == {}

    def test_full_request(self):
        req = FingerprintSubmitRequest(
            artist_id="artist-001",
            audio_url="https://example.com/track.wav",
            isrc="USAT12345678",
            providers=["acrcloud", "gracenote"],
            tenant_id="tenant-x",
            metadata={"source": "upload"},
        )
        assert len(req.providers) == 2
        assert req.tenant_id == "tenant-x"


class TestMatchingEngineReportContract:
    def test_empty_report(self):
        report = MatchingEngineReport(
            artist_id="artist-001",
            generated_at=datetime.now(timezone.utc),
        )
        assert report.fingerprint_results == []
        assert report.catalog_matches == []
        assert report.usage_matches == []
        assert report.royalty_gaps == []
        assert report.anomalies == []
        assert report.schema_version == "xr7.fingerprinting.matching_report.v1"

    def test_report_with_data(self):
        fp = NormalizedMatchResult(
            isrc="USAT001",
            confidence_score=0.9,
            timestamp=datetime.now(timezone.utc),
            provider="acrcloud",
        )
        catalog = CatalogMatchResult(
            work_id="work-001",
            isrc="USAT001",
            confidence_score=1.0,
            match_method="isrc",
        )
        report = MatchingEngineReport(
            artist_id="artist-001",
            fingerprint_results=[fp],
            catalog_matches=[catalog],
            generated_at=datetime.now(timezone.utc),
        )
        assert len(report.fingerprint_results) == 1
        assert len(report.catalog_matches) == 1


class TestMockProviderOutputConformsToSchema:
    """Verify that MockFingerprintingProvider output passes schema validation."""

    @pytest.mark.asyncio
    async def test_mock_match_audio_output_valid(self):
        from tests.fingerprinting.mocks.mock_provider import MockFingerprintingProvider

        provider = MockFingerprintingProvider()
        results = await provider.match_audio(b"audio")
        assert len(results) == 1
        r = results[0]
        # Pydantic model should already validate; double-check key fields
        assert isinstance(r.confidence_score, float)
        assert 0.0 <= r.confidence_score <= 1.0
        assert isinstance(r.provider, str)
        assert r.timestamp is not None
