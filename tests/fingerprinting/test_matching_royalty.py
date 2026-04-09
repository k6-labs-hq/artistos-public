"""Tests for the RoyaltyMatchingModule."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

from XR7.fingerprinting.matching.royalty import RoyaltyMatchingModule
from XR7.fingerprinting.schema import (
    AnomalyType,
    MatchType,
    NormalizedMatchResult,
    RoyaltyStatus,
    UsageMatchResult,
)


def _fp(isrc="USAT001", provider="acrcloud"):
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


def _usage(platform, match_type=MatchType.STREAM, territory="US", reported=False):
    return UsageMatchResult(
        isrc="USAT001",
        platform=platform,
        territory=territory,
        match_type=match_type,
        detected_at=datetime.now(timezone.utc),
        reported=reported,
        provider="acrcloud",
    )


class TestRoyaltyMatchingBasic:
    def test_unreported_usage_returns_gap(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        module = RoyaltyMatchingModule(mock_db)
        fp = _fp()
        usage = [_usage("spotify", reported=False)]

        gaps = module.compare(fp, usage, artist_id="artist-001")
        assert len(gaps) >= 1
        assert all(not g.royalty_received for g in gaps)

    def test_no_usage_no_gap(self):
        mock_db = MagicMock()
        module = RoyaltyMatchingModule(mock_db)
        fp = _fp()
        gaps = module.compare(fp, [], artist_id="artist-001")
        assert gaps == []


class TestRoyaltyForeignUsageAnomaly:
    def test_foreign_usage_no_pro_detected(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        module = RoyaltyMatchingModule(mock_db)
        fp = _fp(isrc="GBXXX1234567")
        usage = [_usage("bbc_radio", match_type=MatchType.BROADCAST, territory="UK", reported=True)]

        gaps = module.compare(fp, usage, artist_id="artist-001")
        foreign_gaps = [
            g for g in gaps if g.anomaly_type == AnomalyType.FOREIGN_USAGE_NO_PRO
        ]
        assert len(foreign_gaps) >= 1


class TestRoyaltyLivePerformanceAnomaly:
    def test_live_no_pro_detected(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        module = RoyaltyMatchingModule(mock_db)
        fp = _fp()
        usage = [_usage("ticketmaster", match_type=MatchType.LIVE, territory="US", reported=True)]

        gaps = module.compare(fp, usage, artist_id="artist-001")
        live_gaps = [
            g for g in gaps if g.anomaly_type == AnomalyType.LIVE_NO_PRO_PERFORMANCE
        ]
        assert len(live_gaps) >= 1


class TestRoyaltySocialNoDistributorAnomaly:
    def test_tiktok_no_distributor_detected(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        module = RoyaltyMatchingModule(mock_db)
        fp = _fp()
        usage = [_usage("tiktok", match_type=MatchType.UGC, territory="US", reported=True)]

        gaps = module.compare(fp, usage, artist_id="artist-001")
        social_gaps = [
            g for g in gaps if g.anomaly_type == AnomalyType.SOCIAL_NO_DISTRIBUTOR
        ]
        assert len(social_gaps) >= 1


class TestRoyaltyBatchCompare:
    def test_batch_compare_returns_all_gaps(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        module = RoyaltyMatchingModule(mock_db)
        fps = [_fp("USAT001"), _fp("USAT002")]
        usage_map = {
            0: [_usage("spotify", reported=False)],
            1: [_usage("tiktok", match_type=MatchType.UGC, reported=False)],
        }
        gaps = module.compare_batch(fps, usage_map, artist_id="artist-001")
        assert len(gaps) >= 2
