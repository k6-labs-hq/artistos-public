"""Shared fixtures for the fingerprinting test suite."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tests.fingerprinting.mocks.mock_provider import MockFingerprintingProvider
from XR7.fingerprinting.schema import (
    AnomalyType,
    FingerprintSubmitRequest,
    MatchType,
    NormalizedMatchResult,
    RoyaltyStatus,
)


@pytest.fixture
def mock_provider():
    return MockFingerprintingProvider(provider_name="mock")


@pytest.fixture
def unhealthy_mock_provider():
    return MockFingerprintingProvider(provider_name="mock_down", healthy=False)


@pytest.fixture
def sample_fingerprint_result() -> NormalizedMatchResult:
    return NormalizedMatchResult(
        track_id="test-track-001",
        isrc="USAT12345678",
        iswc="T-123456789-0",
        confidence_score=0.95,
        match_type=MatchType.STREAM,
        platform="spotify",
        territory="US",
        timestamp=datetime.now(timezone.utc),
        provider="acrcloud",
        royalty_status=RoyaltyStatus.UNKNOWN,
        anomaly_type=AnomalyType.NONE,
        title="Test Track",
        artist_name="Test Artist",
        duration_seconds=210.0,
        raw_provider_payload={"acrid": "test-001", "score": 95},
    )


@pytest.fixture
def ugc_fingerprint_result() -> NormalizedMatchResult:
    return NormalizedMatchResult(
        track_id="ugc-track-001",
        isrc="USAT98765432",
        confidence_score=0.88,
        match_type=MatchType.UGC,
        platform="tiktok",
        territory="US",
        timestamp=datetime.now(timezone.utc),
        provider="acrcloud",
        royalty_status=RoyaltyStatus.UNKNOWN,
        anomaly_type=AnomalyType.NONE,
        title="Viral Track",
        artist_name="Test Artist",
        raw_provider_payload={},
    )


@pytest.fixture
def foreign_fingerprint_result() -> NormalizedMatchResult:
    return NormalizedMatchResult(
        track_id="foreign-track-001",
        isrc="GBXXX1234567",
        confidence_score=0.92,
        match_type=MatchType.BROADCAST,
        platform="bbc_radio",
        territory="UK",
        timestamp=datetime.now(timezone.utc),
        provider="gracenote",
        royalty_status=RoyaltyStatus.UNKNOWN,
        anomaly_type=AnomalyType.NONE,
        title="Foreign Broadcast Track",
        artist_name="Test Artist",
        raw_provider_payload={},
    )


@pytest.fixture
def fingerprint_request() -> FingerprintSubmitRequest:
    return FingerprintSubmitRequest(
        artist_id="artist-uuid-001",
        isrc="USAT12345678",
        title="Test Track",
        artist_name="Test Artist",
        providers=["mock"],
    )
