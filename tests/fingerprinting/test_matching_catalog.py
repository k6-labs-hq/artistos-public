"""Tests for the CatalogMatchingModule."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from XR7.fingerprinting.matching.catalog import CatalogMatchingModule
from XR7.fingerprinting.schema import (
    AnomalyType,
    MatchType,
    NormalizedMatchResult,
    RoyaltyStatus,
)


def _make_work(
    work_id="work-001",
    title="Test Track",
    isrc="USAT12345678",
    iswc="T-123456789-0",
):
    work = MagicMock()
    work.id = work_id
    work.title = title
    work.isrc = isrc
    work.iswc = iswc
    work.artist_id = "artist-001"
    return work


def _make_fingerprint(isrc=None, iswc=None, ipi=None, title=None, artist_name=None, track_id=None):
    return NormalizedMatchResult(
        isrc=isrc,
        iswc=iswc,
        ipi=ipi,
        track_id=track_id,
        confidence_score=0.9,
        match_type=MatchType.STREAM,
        platform="spotify",
        territory="US",
        timestamp=datetime.now(timezone.utc),
        provider="acrcloud",
        royalty_status=RoyaltyStatus.UNKNOWN,
        anomaly_type=AnomalyType.NONE,
        title=title,
        artist_name=artist_name,
    )


class TestCatalogMatchingByISRC:
    def test_isrc_match_returns_correct_work(self):
        mock_db = MagicMock()
        work = _make_work(isrc="USAT12345678")
        mock_db.query.return_value.filter.return_value.first.return_value = work

        module = CatalogMatchingModule(mock_db)
        fp = _make_fingerprint(isrc="USAT12345678")
        results = module.match(fp)

        assert len(results) == 1
        assert results[0].isrc == "USAT12345678"
        assert results[0].match_method == "isrc"
        assert results[0].confidence_score == 1.0

    def test_no_isrc_returns_empty(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        module = CatalogMatchingModule(mock_db)
        fp = _make_fingerprint(isrc="USAT00000000")
        results = module.match(fp)
        assert results == []


class TestCatalogMatchingByISWC:
    def test_iswc_fallback_used_when_no_isrc(self):
        mock_db = MagicMock()
        work = _make_work(iswc="T-111111111-1")

        # First query (ISRC) returns None; second (ISWC) returns work
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            None,  # ISRC not found
            work,  # ISWC found
        ]

        module = CatalogMatchingModule(mock_db)
        fp = _make_fingerprint(iswc="T-111111111-1")
        results = module.match(fp)

        assert len(results) == 1
        assert results[0].match_method == "iswc"
        assert results[0].confidence_score == pytest.approx(0.95)


class TestCatalogMatchingByTitle:
    def test_title_fuzzy_match(self):
        mock_db = MagicMock()
        work = _make_work(title="Test Song")
        work.artist = MagicMock()
        work.artist.name = "Test Artist"

        # ISRC, ISWC, IPI all return None; title query returns [work]
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = [
            work
        ]

        module = CatalogMatchingModule(mock_db)
        fp = _make_fingerprint(title="Test Song", artist_name="Test Artist")
        results = module.match(fp)

        # Should find a fuzzy match
        assert len(results) >= 1
        assert results[0].match_method == "title_artist_fuzzy"

    def test_dissimilar_title_no_match(self):
        mock_db = MagicMock()
        work = _make_work(title="Completely Different")
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = [
            work
        ]

        module = CatalogMatchingModule(mock_db)
        fp = _make_fingerprint(title="Nothing Like It")
        results = module.match(fp)
        assert results == []


class TestCatalogMatchBatch:
    def test_batch_returns_dict_keyed_by_index(self):
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        module = CatalogMatchingModule(mock_db)
        fps = [_make_fingerprint(title="A"), _make_fingerprint(title="B")]
        batch_result = module.match_batch(fps)
        assert 0 in batch_result
        assert 1 in batch_result
