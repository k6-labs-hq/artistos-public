"""Tests for the FingerprintAnomalyDetectionEngine."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

from XR7.fingerprinting.matching.anomaly import FingerprintAnomalyDetectionEngine
from XR7.fingerprinting.schema import (
    AnomalyType,
    CatalogMatchResult,
    MatchType,
    NormalizedMatchResult,
    RoyaltyGapResult,
    RoyaltyStatus,
)


def _fp(isrc=None, provider="acrcloud"):
    return NormalizedMatchResult(
        isrc=isrc,
        confidence_score=0.9,
        match_type=MatchType.STREAM,
        platform="spotify",
        territory="US",
        timestamp=datetime.now(timezone.utc),
        provider=provider,
        royalty_status=RoyaltyStatus.UNKNOWN,
        anomaly_type=AnomalyType.NONE,
    )


def _catalog_match(work_id="work-001", isrc="USAT12345678", iswc=None):
    return CatalogMatchResult(
        work_id=work_id,
        isrc=isrc,
        iswc=iswc,
        title="Track",
        confidence_score=1.0,
        match_method="isrc",
    )


class TestRoyaltyNoUsageDetection:
    def test_detects_royalty_no_usage(self):
        mock_db = MagicMock()
        # Simulate a payment with an ISRC that was NOT in fingerprints
        mock_payment = MagicMock()
        mock_payment.artist_id = "artist-001"
        mock_payment.source = "Spotify payment"
        mock_payment.notes = "ISRC GBZZZ9999999 royalty"
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = [
            mock_payment
        ]

        engine = FingerprintAnomalyDetectionEngine(mock_db)
        # Fingerprints have a different ISRC
        fingerprints = [_fp(isrc="USAT00000001")]
        anomalies = engine.detect(
            artist_id="artist-001",
            fingerprints=fingerprints,
            catalog_matches=[],
            usage_results=[],
            existing_gaps=[],
        )
        royalty_no_usage = [a for a in anomalies if a.anomaly_type == AnomalyType.ROYALTY_NO_USAGE]
        assert len(royalty_no_usage) >= 1

    def test_no_anomaly_when_fingerprint_covers_isrc(self):
        mock_db = MagicMock()
        mock_payment = MagicMock()
        mock_payment.artist_id = "artist-001"
        mock_payment.source = "Spotify"
        mock_payment.notes = "ISRC USAT12345678 payment"
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = [
            mock_payment
        ]

        engine = FingerprintAnomalyDetectionEngine(mock_db)
        fingerprints = [_fp(isrc="USAT12345678")]
        anomalies = engine.detect(
            artist_id="artist-001",
            fingerprints=fingerprints,
            catalog_matches=[],
            usage_results=[],
            existing_gaps=[],
        )
        royalty_no_usage = [a for a in anomalies if a.anomaly_type == AnomalyType.ROYALTY_NO_USAGE]
        assert len(royalty_no_usage) == 0


class TestISRCConflictDetection:
    def test_detects_isrc_shared_across_works(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        engine = FingerprintAnomalyDetectionEngine(mock_db)
        catalog_matches = [
            _catalog_match(work_id="work-A", isrc="USAT99999999"),
            _catalog_match(work_id="work-B", isrc="USAT99999999"),
        ]
        anomalies = engine.detect(
            artist_id="artist-001",
            fingerprints=[],
            catalog_matches=catalog_matches,
            usage_results=[],
            existing_gaps=[],
        )
        conflicts = [a for a in anomalies if a.anomaly_type == AnomalyType.ISRC_CONFLICT]
        assert len(conflicts) >= 1

    def test_no_conflict_for_unique_isrcs(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        engine = FingerprintAnomalyDetectionEngine(mock_db)
        catalog_matches = [
            _catalog_match(work_id="work-A", isrc="USAT00000001"),
            _catalog_match(work_id="work-B", isrc="USAT00000002"),
        ]
        anomalies = engine.detect(
            artist_id="artist-001",
            fingerprints=[],
            catalog_matches=catalog_matches,
            usage_results=[],
            existing_gaps=[],
        )
        conflicts = [a for a in anomalies if a.anomaly_type == AnomalyType.ISRC_CONFLICT]
        assert len(conflicts) == 0


class TestCatalogMismatchDetection:
    def test_detects_mismatch_when_fp_isrc_not_in_catalog(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        engine = FingerprintAnomalyDetectionEngine(mock_db)
        fingerprints = [_fp(isrc="GBXXX9999999")]
        catalog_matches = [_catalog_match(isrc="USAT00000001")]

        anomalies = engine.detect(
            artist_id="artist-001",
            fingerprints=fingerprints,
            catalog_matches=catalog_matches,
            usage_results=[],
            existing_gaps=[],
        )
        mismatches = [a for a in anomalies if a.anomaly_type == AnomalyType.CATALOG_MISMATCH]
        assert len(mismatches) >= 1


class TestDeduplicationVsExistingGaps:
    def test_no_duplicate_anomalies(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        existing_gap = RoyaltyGapResult(
            isrc="GBXXX9999999",
            platform=None,
            territory=None,
            match_type=MatchType.UNKNOWN,
            anomaly_type=AnomalyType.CATALOG_MISMATCH,
        )

        engine = FingerprintAnomalyDetectionEngine(mock_db)
        fingerprints = [_fp(isrc="GBXXX9999999")]
        catalog_matches = [_catalog_match(isrc="USAT00000001")]

        anomalies = engine.detect(
            artist_id="artist-001",
            fingerprints=fingerprints,
            catalog_matches=catalog_matches,
            usage_results=[],
            existing_gaps=[existing_gap],
        )
        mismatches = [a for a in anomalies if a.anomaly_type == AnomalyType.CATALOG_MISMATCH]
        assert len(mismatches) == 0
