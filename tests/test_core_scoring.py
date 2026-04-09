"""
Tests for XR7.core.scoring.confidence_band and XR7.core.scoring.metadata_match
================================================================================
confidence_band covers:
  - classify_band() boundary values (exactly at HIGH, MEDIUM, just below)
  - classify_band() edge inputs (0.0, 1.0, negative, >1.0)
  - HIGH and MEDIUM threshold constants are stable
  - Domain-boundary check: no DB imports

metadata_match covers:
  - normalize_text() strips punctuation, lowercases, collapses whitespace
  - normalize_text() handles None / empty input
  - text_similarity() perfect match, total mismatch, partial match
  - text_similarity() None inputs return 0.0
  - metadata_triangulation_score() all weights sum correctly
  - metadata_triangulation_score() id_match=True boosts score
  - metadata_triangulation_score() absent durations default to 0.5 weight
  - metadata_triangulation_score() output clamped to [0.0, 1.0]
  - confidence_score() logistic output in (0, 1)
  - confidence_score() conflict_penalty reduces score
  - Domain-boundary check: no DB imports

Mocks/fixtures: none — all pure functions.

Recommended future tests:
  - Property-based: confidence in [0,1], penalties in [0,1] → result in (0,1).
  - Fuzzing normalize_text() with unicode, control characters, emojis.
  - Verify metadata_triangulation_score against human-rated test pairs.
"""

from __future__ import annotations

import pytest

from XR7.core.scoring.confidence_band import HIGH, MEDIUM, classify_band
from XR7.core.scoring.metadata_match import (
    confidence_score,
    metadata_triangulation_score,
    normalize_text,
    text_similarity,
)

# ===========================================================================
# confidence_band
# ===========================================================================


class TestConfidenceBandDomainBoundary:
    def test_no_db_imports(self):
        import XR7.core.scoring.confidence_band as mod

        with open(mod.__file__) as f:
            source = f.read()

        for token in ["sqlalchemy", "SessionLocal", "from XR7.services", "from XR7.api"]:
            assert token not in source, f"Pure module must not import '{token}'"


class TestClassifyBand:
    # --- boundary: exactly at thresholds ---

    def test_exactly_high_threshold_returns_high(self):
        assert classify_band(HIGH) == "high"

    def test_exactly_medium_threshold_returns_medium(self):
        assert classify_band(MEDIUM) == "medium"

    def test_just_below_high_returns_medium(self):
        assert classify_band(HIGH - 0.001) == "medium"

    def test_just_below_medium_returns_low(self):
        assert classify_band(MEDIUM - 0.001) == "low"

    # --- typical values ---

    def test_perfect_confidence_is_high(self):
        assert classify_band(1.0) == "high"

    def test_zero_confidence_is_low(self):
        assert classify_band(0.0) == "low"

    def test_mid_range_is_medium(self):
        assert classify_band(0.80) == "medium"

    def test_very_low_is_low(self):
        assert classify_band(0.10) == "low"

    # --- edge / unusual inputs ---

    def test_negative_confidence_returns_low(self):
        # No domain constraint prevents this; function should still return a band
        assert classify_band(-1.0) == "low"

    def test_above_one_returns_high(self):
        assert classify_band(1.5) == "high"

    def test_returns_string(self):
        for val in (0.0, 0.5, 0.75, 0.95, 1.0):
            assert isinstance(classify_band(val), str)

    def test_only_three_possible_bands(self):
        bands = {classify_band(v / 100) for v in range(101)}
        assert bands == {"high", "medium", "low"}


class TestThresholdConstants:
    def test_high_above_medium(self):
        assert HIGH > MEDIUM

    def test_high_is_09(self):
        assert HIGH == pytest.approx(0.90)

    def test_medium_is_07(self):
        assert MEDIUM == pytest.approx(0.70)


# ===========================================================================
# metadata_match
# ===========================================================================


class TestMetadataMatchDomainBoundary:
    def test_no_db_imports(self):
        import XR7.core.scoring.metadata_match as mod

        with open(mod.__file__) as f:
            source = f.read()

        for token in ["sqlalchemy", "SessionLocal", "from XR7.services", "from XR7.api"]:
            assert token not in source, f"Pure module must not import '{token}'"


class TestNormalizeText:
    def test_lowercases(self):
        assert normalize_text("HELLO WORLD") == "hello world"

    def test_strips_punctuation(self):
        assert normalize_text("Hello, World!") == "hello world"

    def test_collapses_whitespace(self):
        assert normalize_text("a  b   c") == "a b c"

    def test_handles_none(self):
        assert normalize_text(None) == ""

    def test_handles_empty_string(self):
        assert normalize_text("") == ""

    def test_keeps_alphanumeric(self):
        result = normalize_text("Work #42 — remix")
        assert "work" in result
        assert "42" in result
        assert "remix" in result
        assert "#" not in result
        assert "—" not in result

    def test_returns_string(self):
        assert isinstance(normalize_text("test"), str)
        assert isinstance(normalize_text(None), str)


class TestTextSimilarity:
    def test_identical_strings_return_one(self):
        assert text_similarity("Shape of You", "Shape of You") == pytest.approx(1.0)

    def test_completely_different_returns_low(self):
        score = text_similarity("alpha", "zygote")
        assert score < 0.5

    def test_partial_overlap_returns_intermediate(self):
        score = text_similarity("Shape of You (Remix)", "Shape of You")
        assert 0.5 < score < 1.0

    def test_none_left_returns_zero(self):
        assert text_similarity(None, "some title") == pytest.approx(0.0)

    def test_none_right_returns_zero(self):
        assert text_similarity("some title", None) == pytest.approx(0.0)

    def test_both_none_returns_zero(self):
        assert text_similarity(None, None) == pytest.approx(0.0)

    def test_empty_strings_return_zero(self):
        assert text_similarity("", "") == pytest.approx(0.0)

    def test_returns_float(self):
        assert isinstance(text_similarity("a", "b"), float)

    def test_symmetric(self):
        a, b = "Blinding Lights", "The Blinding Lights Remix"
        assert text_similarity(a, b) == pytest.approx(text_similarity(b, a))

    def test_case_insensitive_via_normalize(self):
        assert text_similarity("WORK TITLE", "work title") == pytest.approx(1.0)


class TestMetadataTriangulationScore:
    def _perfect(self):
        return dict(
            title_a="Shape of You",
            title_b="Shape of You",
            artist_a="Ed Sheeran",
            artist_b="Ed Sheeran",
            duration_ms_a=234000,
            duration_ms_b=234000,
            id_match=True,
            context_match=True,
        )

    def test_perfect_match_is_near_one(self):
        score = metadata_triangulation_score(**self._perfect())
        assert score > 0.95

    def test_zero_match_is_near_zero(self):
        score = metadata_triangulation_score(
            title_a="Alpha",
            title_b="Zygote",
            artist_a="Artist A",
            artist_b="Artist Z",
            duration_ms_a=60000,
            duration_ms_b=600000,
            id_match=False,
            context_match=False,
        )
        assert score < 0.30

    def test_id_match_true_boosts_score(self):
        base = dict(
            title_a="x",
            title_b="y",
            artist_a="a",
            artist_b="b",
            duration_ms_a=None,
            duration_ms_b=None,
            context_match=False,
        )
        without_id = metadata_triangulation_score(**base, id_match=False)
        with_id = metadata_triangulation_score(**base, id_match=True)
        assert with_id > without_id

    def test_none_durations_use_neutral_weight(self):
        score_no_dur = metadata_triangulation_score(
            title_a="Work A",
            title_b="Work A",
            artist_a="Art A",
            artist_b="Art A",
            duration_ms_a=None,
            duration_ms_b=None,
            id_match=False,
            context_match=False,
        )
        # With matching title+artist but no duration (neutral 0.5 weight),
        # score should still be meaningful (>0.5)
        assert score_no_dur > 0.5

    def test_zero_duration_treated_as_absent(self):
        score_zero = metadata_triangulation_score(
            title_a="Work A",
            title_b="Work A",
            artist_a="Art A",
            artist_b="Art A",
            duration_ms_a=0,
            duration_ms_b=60000,
            id_match=False,
            context_match=False,
        )
        score_none = metadata_triangulation_score(
            title_a="Work A",
            title_b="Work A",
            artist_a="Art A",
            artist_b="Art A",
            duration_ms_a=None,
            duration_ms_b=60000,
            id_match=False,
            context_match=False,
        )
        # Both should use neutral duration weight
        assert score_zero == pytest.approx(score_none)

    def test_output_clamped_to_0_1(self):
        for _ in range(10):
            score = metadata_triangulation_score(
                title_a="T",
                title_b="T",
                artist_a="A",
                artist_b="A",
                duration_ms_a=120000,
                duration_ms_b=120000,
                id_match=True,
                context_match=True,
            )
            assert 0.0 <= score <= 1.0

    def test_returns_float(self):
        score = metadata_triangulation_score(
            title_a="A",
            title_b="B",
            artist_a="x",
            artist_b="y",
            duration_ms_a=None,
            duration_ms_b=None,
            id_match=False,
            context_match=False,
        )
        assert isinstance(score, float)

    def test_close_duration_scores_high(self):
        close = metadata_triangulation_score(
            title_a="T",
            title_b="T",
            artist_a="A",
            artist_b="A",
            duration_ms_a=180000,
            duration_ms_b=180100,  # 100ms diff
            id_match=False,
            context_match=False,
        )
        far = metadata_triangulation_score(
            title_a="T",
            title_b="T",
            artist_a="A",
            artist_b="A",
            duration_ms_a=180000,
            duration_ms_b=360000,  # 3min diff
            id_match=False,
            context_match=False,
        )
        assert close > far


class TestConfidenceScore:
    def test_high_signals_returns_high_score(self):
        score = confidence_score(
            metadata_score=0.9,
            fingerprint_score=0.9,
            history_score=0.8,
            contract_score=0.8,
            conflict_penalty=0.0,
        )
        assert score > 0.9

    def test_low_signals_returns_low_score(self):
        score = confidence_score(
            metadata_score=0.1,
            fingerprint_score=0.1,
            history_score=0.1,
            contract_score=0.1,
            conflict_penalty=1.0,
        )
        assert score < 0.5

    def test_output_in_open_interval_0_1(self):
        for ms, fs in [(0.0, 0.0), (0.5, 0.5), (1.0, 1.0)]:
            score = confidence_score(
                metadata_score=ms,
                fingerprint_score=fs,
                history_score=0.5,
                contract_score=0.5,
                conflict_penalty=0.0,
            )
            assert 0.0 < score < 1.0

    def test_conflict_penalty_reduces_score(self):
        base_kwargs = dict(
            metadata_score=0.7,
            fingerprint_score=0.7,
            history_score=0.7,
            contract_score=0.7,
        )
        no_penalty = confidence_score(**base_kwargs, conflict_penalty=0.0)
        with_penalty = confidence_score(**base_kwargs, conflict_penalty=1.0)
        assert no_penalty > with_penalty

    def test_fingerprint_weight_exceeds_history(self):
        """Fingerprint has weight 1.8 vs history 0.8; increasing fingerprint should help more."""
        fp_boosted = confidence_score(
            metadata_score=0.5,
            fingerprint_score=0.8,
            history_score=0.3,
            contract_score=0.3,
            conflict_penalty=0.0,
        )
        hist_boosted = confidence_score(
            metadata_score=0.5,
            fingerprint_score=0.3,
            history_score=0.8,
            contract_score=0.3,
            conflict_penalty=0.0,
        )
        assert fp_boosted > hist_boosted

    def test_returns_float(self):
        result = confidence_score(0.5, 0.5, 0.5, 0.5, 0.0)
        assert isinstance(result, float)
