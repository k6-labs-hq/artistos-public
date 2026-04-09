"""Tests for the UsageMatchingModule."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

from XR7.fingerprinting.matching.usage import (
    UsageMatchingModule,
    _infer_match_type,
)
from XR7.fingerprinting.schema import (
    AnomalyType,
    MatchType,
    NormalizedMatchResult,
    RoyaltyStatus,
)


def _fp(platform=None, isrc=None, match_type=MatchType.UNKNOWN):
    return NormalizedMatchResult(
        isrc=isrc,
        confidence_score=0.9,
        match_type=match_type,
        platform=platform,
        territory="US",
        timestamp=datetime.now(timezone.utc),
        provider="acrcloud",
        royalty_status=RoyaltyStatus.UNKNOWN,
        anomaly_type=AnomalyType.NONE,
    )


class TestInferMatchType:
    def test_youtube_is_ugc(self):
        assert _infer_match_type("youtube") == MatchType.UGC

    def test_tiktok_is_ugc(self):
        assert _infer_match_type("tiktok") == MatchType.UGC

    def test_spotify_is_stream(self):
        assert _infer_match_type("spotify") == MatchType.STREAM

    def test_ticketmaster_is_live(self):
        assert _infer_match_type("ticketmaster") == MatchType.LIVE

    def test_bbc_radio_is_radio(self):
        assert _infer_match_type("bbc_radio") == MatchType.RADIO

    def test_unknown_platform(self):
        assert _infer_match_type("random_platform") == MatchType.UNKNOWN

    def test_none_platform(self):
        assert _infer_match_type(None) == MatchType.UNKNOWN


class TestUsageMatchingModule:
    def test_match_with_platform_returns_usage_result(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        module = UsageMatchingModule(mock_db)
        fp = _fp(platform="spotify", isrc="USAT001")
        results = module.match(fp)

        assert len(results) >= 1
        assert results[0].platform == "spotify"
        assert results[0].match_type == MatchType.STREAM

    def test_match_ugc_platform_flagged_as_unreported(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        module = UsageMatchingModule(mock_db)
        fp = _fp(platform="tiktok", match_type=MatchType.UGC)
        results = module.match(fp)

        ugc_results = [r for r in results if r.match_type == MatchType.UGC]
        assert len(ugc_results) >= 1
        assert any(not r.reported for r in ugc_results)

    def test_match_no_platform_returns_empty_from_platform_stage(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        module = UsageMatchingModule(mock_db)
        fp = _fp(platform=None)
        results = module.match(fp)
        # No platform → no direct platform result returned
        platform_results = [r for r in results if r.platform is not None]
        assert len(platform_results) == 0

    def test_match_batch(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
        module = UsageMatchingModule(mock_db)
        fps = [_fp(platform="spotify"), _fp(platform="tiktok")]
        batch = module.match_batch(fps)
        assert 0 in batch
        assert 1 in batch
