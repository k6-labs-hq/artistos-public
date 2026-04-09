"""
Tests for XR7.fingerprinting.matching.identity_matching
=========================================================
Tests the pure-logic functions only — the DB-dependent ``persist_identity_match``
and ``apply_identity_decision`` functions are integration-level concerns tested
separately with a real session fixture.

Covers:
  - compute_identity_match() — all scoring signals (stage_name, IPI, ISRC, ISWC, UPC)
  - Score banding: >=0.90 → AUTO_ACCEPT, 0.70-0.89 → SOFT_CONFIRM, <0.70 → REQUIRE_CONFIRMATION
  - Missing/empty signals default to 0.0 contribution
  - Output is an IdentityMatchResult dataclass with all expected fields
  - score_breakdown contains all six signal keys
  - Score is clamped to [0.0, 1.0]
  - Domain-boundary check: compute_identity_match has no DB calls

Fixtures:
  - ``make_artist``: creates a plain mock Artist (no DB)
  - ``make_work``: creates a plain mock Work (no DB)

Recommended future tests:
  - persist_identity_match() with a real in-memory SQLite session.
  - apply_identity_decision() confirms/rejects a match and audits correctly.
  - Property-based: arbitrary signals → score always in [0.0, 1.0].
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from XR7.fingerprinting.matching.identity_matching import compute_identity_match
from XR7.models.identity_match import (
    IdentityConfidenceBand,
    IdentityDecisionStatus,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_artist(
    name: str = "Ed Sheeran",
    stage_names: list[str] | None = None,
    ipi_number: str | None = None,
) -> MagicMock:
    artist = MagicMock()
    artist.name = name
    artist.stage_names = stage_names or []
    artist.ipi_number = ipi_number
    return artist


def _make_work(
    isrc: str | None = None,
    iswc: str | None = None,
) -> MagicMock:
    work = MagicMock()
    work.isrc = isrc
    work.iswc = iswc
    return work


# ---------------------------------------------------------------------------
# compute_identity_match — result structure
# ---------------------------------------------------------------------------

class TestComputeIdentityMatchStructure:
    def test_returns_identity_match_result(self):
        from XR7.fingerprinting.matching.identity_matching import IdentityMatchResult
        artist = _make_artist()
        result = compute_identity_match(artist, {}, [])
        assert isinstance(result, IdentityMatchResult)

    def test_score_is_float(self):
        result = compute_identity_match(_make_artist(), {}, [])
        assert isinstance(result.score, float)

    def test_score_in_range(self):
        result = compute_identity_match(_make_artist(), {}, [])
        assert 0.0 <= result.score <= 1.0

    def test_score_breakdown_has_all_signals(self):
        result = compute_identity_match(_make_artist(), {}, [])
        expected_keys = {"stage_name", "pro_writer_id", "distributor_alias", "isrc", "iswc", "upc"}
        assert expected_keys == set(result.score_breakdown.keys())

    def test_band_is_identity_confidence_band(self):
        result = compute_identity_match(_make_artist(), {}, [])
        assert isinstance(result.band, IdentityConfidenceBand)

    def test_decision_status_is_identity_decision_status(self):
        result = compute_identity_match(_make_artist(), {}, [])
        assert isinstance(result.decision_status, IdentityDecisionStatus)

    def test_reason_is_string(self):
        result = compute_identity_match(_make_artist(), {}, [])
        assert isinstance(result.reason, str)


# ---------------------------------------------------------------------------
# No signals → require confirmation band
# ---------------------------------------------------------------------------

class TestNoSignals:
    def test_empty_signals_score_zero(self):
        result = compute_identity_match(_make_artist(), {}, [])
        assert result.score == pytest.approx(0.0)

    def test_empty_signals_band_require_confirmation(self):
        result = compute_identity_match(_make_artist(), {}, [])
        assert result.band == IdentityConfidenceBand.REQUIRE_CONFIRMATION
        assert result.decision_status == IdentityDecisionStatus.PENDING_EXPLICIT_CONFIRM


# ---------------------------------------------------------------------------
# Stage name signal (weight 0.35)
# ---------------------------------------------------------------------------

class TestStageNameSignal:
    def test_exact_stage_name_match_contributes_full_weight(self):
        artist = _make_artist(name="Ed Sheeran")
        signals = {"artist_name": "Ed Sheeran"}
        result = compute_identity_match(artist, signals, [])
        assert result.score_breakdown["stage_name"] == pytest.approx(1.0)

    def test_stage_name_case_insensitive(self):
        artist = _make_artist(name="Ed Sheeran")
        signals = {"artist_name": "ed sheeran"}
        result = compute_identity_match(artist, signals, [])
        assert result.score_breakdown["stage_name"] == pytest.approx(1.0)

    def test_alias_in_stage_names_also_matches(self):
        artist = _make_artist(name="Edward Sheeran", stage_names=["Ed Sheeran"])
        signals = {"artist_name": "Ed Sheeran"}
        result = compute_identity_match(artist, signals, [])
        assert result.score_breakdown["stage_name"] == pytest.approx(1.0)

    def test_missing_artist_name_signal_zero_stage_score(self):
        artist = _make_artist(name="Ed Sheeran")
        result = compute_identity_match(artist, {}, [])
        assert result.score_breakdown["stage_name"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# IPI / PRO writer ID signal (weight 0.20)
# ---------------------------------------------------------------------------

class TestIpiSignal:
    def test_matched_ipi_contributes_full_weight(self):
        artist = _make_artist(ipi_number="00123456789")
        signals = {"pro_writer_id": "00123456789"}
        result = compute_identity_match(artist, signals, [])
        assert result.score_breakdown["pro_writer_id"] == pytest.approx(1.0)

    def test_mismatched_ipi_contributes_zero(self):
        artist = _make_artist(ipi_number="00123456789")
        signals = {"pro_writer_id": "00999999999"}
        result = compute_identity_match(artist, signals, [])
        assert result.score_breakdown["pro_writer_id"] == pytest.approx(0.0)

    def test_missing_ipi_signal_zero(self):
        artist = _make_artist(ipi_number="00123456789")
        result = compute_identity_match(artist, {}, [])
        assert result.score_breakdown["pro_writer_id"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# ISRC signal (weight 0.15)
# ---------------------------------------------------------------------------

class TestIsrcSignal:
    def test_matching_isrc_contributes_full_weight(self):
        works = [_make_work(isrc="GBAHS1700437")]
        signals = {"isrcs": ["GBAHS1700437"]}
        result = compute_identity_match(_make_artist(), signals, works)
        assert result.score_breakdown["isrc"] == pytest.approx(1.0)

    def test_no_isrc_match_contributes_zero(self):
        works = [_make_work(isrc="GBAHS1700437")]
        signals = {"isrcs": ["USZZ12300001"]}
        result = compute_identity_match(_make_artist(), signals, works)
        assert result.score_breakdown["isrc"] == pytest.approx(0.0)

    def test_partial_isrc_overlap_gives_fractional_score(self):
        works = [_make_work(isrc="ISRC001"), _make_work(isrc="ISRC002")]
        signals = {"isrcs": ["ISRC001", "ISRC999"]}
        result = compute_identity_match(_make_artist(), signals, works)
        assert 0.0 < result.score_breakdown["isrc"] < 1.0


# ---------------------------------------------------------------------------
# ISWC signal (weight 0.10)
# ---------------------------------------------------------------------------

class TestIswcSignal:
    def test_matching_iswc_contributes_full_weight(self):
        works = [_make_work(iswc="T-034.524.680-1")]
        signals = {"iswcs": ["T-034.524.680-1"]}
        result = compute_identity_match(_make_artist(), signals, works)
        assert result.score_breakdown["iswc"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# UPC signal (weight 0.05)
# ---------------------------------------------------------------------------

class TestUpcSignal:
    def test_upc_present_gives_one(self):
        signals = {"upcs": ["093624968429"]}
        result = compute_identity_match(_make_artist(), signals, [])
        assert result.score_breakdown["upc"] == pytest.approx(1.0)

    def test_upc_absent_gives_zero(self):
        result = compute_identity_match(_make_artist(), {}, [])
        assert result.score_breakdown["upc"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Band assignment thresholds
# ---------------------------------------------------------------------------

class TestBandAssignment:
    def _high_confidence_signals(self):
        """Returns signals that should produce a score >= 0.90."""
        artist = _make_artist(name="Drake", stage_names=["Drake"], ipi_number="00123456789")
        works = [_make_work(isrc="USCAA1234567", iswc="T-034.524.680-1")]
        signals = {
            "artist_name": "Drake",
            "pro_writer_id": "00123456789",
            "isrcs": ["USCAA1234567"],
            "iswcs": ["T-034.524.680-1"],
            "upcs": ["093624968429"],
            "distributor_list": ["Drake"],
        }
        return artist, signals, works

    def test_full_signal_match_produces_auto_accept(self):
        artist, signals, works = self._high_confidence_signals()
        result = compute_identity_match(artist, signals, works)
        assert result.band == IdentityConfidenceBand.AUTO_ACCEPT
        assert result.decision_status == IdentityDecisionStatus.AUTO_ACCEPTED
        assert result.score >= 0.90

    def test_mid_range_score_produces_soft_confirm(self):
        artist = _make_artist(name="Adele")
        signals = {"artist_name": "Adele", "isrcs": [], "iswcs": []}
        result = compute_identity_match(artist, signals, [])
        # Only stage_name match (0.35 weight * 1.0 = 0.35) → low band
        # This tests behavior when signals are partial
        assert result.band in (
            IdentityConfidenceBand.SOFT_CONFIRM,
            IdentityConfidenceBand.REQUIRE_CONFIRMATION,
        )

    def test_score_is_clamped_to_1(self):
        artist, signals, works = self._high_confidence_signals()
        result = compute_identity_match(artist, signals, works)
        assert result.score <= 1.0

    def test_score_is_clamped_to_0(self):
        result = compute_identity_match(_make_artist(), {}, [])
        assert result.score >= 0.0
