from datetime import datetime, timezone

from XR7.anomaly.rules.work_level_rules import (
    detect_coverage_gaps,
    detect_share_drift,
    detect_work_dropouts,
    normalize_work_title,
    payer_family,
    run_work_level_rules,
    work_level_rules_enabled,
)
from XR7.ingestion.statement_parser import parse_csv
from tests.test_mlc_parser import _MLC_HEADER, _row

NOW = datetime(2026, 11, 18, tzinfo=timezone.utc)
PRO_DSP = "BMI / Internet: Spotify"
MLC_DSP = "MLC / Spotify"


def ev(title, platform, y, m, amt, territory="US", share=None):
    return {
        "work_title": title,
        "platform": platform,
        "territory": territory,
        "timestamp": datetime(y, m, 15, tzinfo=timezone.utc),
        "quantity": 1,
        "unit_value": amt,
        "share_pct": share,
    }


def subtypes(findings):
    return sorted(f["subtype"] for f in findings)


# ── helpers ──────────────────────────────────────────────────────────────────


def test_payer_family_and_title_normalisation():
    assert payer_family("BMI / Internet: Spotify") == "BMI"
    assert payer_family("MLC / Apple") == "MLC"
    assert payer_family("SESAC / DIGITAL MEDIA") == "SESAC"
    assert payer_family("DistroKid / Spotify") is None
    assert normalize_work_title("Sunset Drive (feat. Bob) - Remastered 2011") == "SUNSET DRIVE"


# ── 1. coverage ──────────────────────────────────────────────────────────────


def _coverage_base():
    return [
        ev("Song A", PRO_DSP, 2025, 3, 200),
        ev("Song B", PRO_DSP, 2025, 3, 200),
        ev("Song B", MLC_DSP, 2025, 4, 250),
    ]


def test_pro_income_with_no_mlc_is_flagged_with_itemised_estimate():
    f = detect_coverage_gaps("a1", _coverage_base(), NOW)
    assert subtypes(f) == ["WORK_MISSING_MECHANICAL"]
    x = f[0]
    assert x["evidence"]["work_title"] == "Song A"
    assert x["evidence"]["estimated_mechanical_floor"] == 300.0
    assert x["estimated_recoverable"] == 0.0  # itemises the artist-level rule; no double count
    assert x["severity"] == "HIGH" and x["identity_key"] == "WORK_MISSING_MECHANICAL:SONG A"


def test_no_mlc_data_at_all_is_not_flagged_control():
    assert detect_coverage_gaps("a1", [ev("Song A", PRO_DSP, 2025, 3, 200)], NOW) == []


def test_title_variant_at_mlc_counts_as_match():
    events = [
        ev("Midnight Rain", PRO_DSP, 2025, 3, 200),
        ev("Midnight Rains", MLC_DSP, 2025, 4, 200),
        ev("Other", MLC_DSP, 2025, 4, 50),
        ev("Other", PRO_DSP, 2025, 3, 30),
    ]
    assert detect_coverage_gaps("a1", events, NOW) == []


def test_close_but_not_matching_title_is_reported_as_possible_mismatch():
    events = [
        ev("Midnight Rain Tonight", PRO_DSP, 2025, 3, 200),
        ev("Midnight Train", MLC_DSP, 2025, 4, 200),
    ]
    f = detect_coverage_gaps("a1", events, NOW)
    assert subtypes(f) == ["WORK_MISSING_MECHANICAL", "WORK_MISSING_PERFORMANCE"]
    mech = next(x for x in f if x["subtype"] == "WORK_MISSING_MECHANICAL")
    assert mech["evidence"]["closest_mlc_title"] == "MIDNIGHT TRAIN"


def test_recent_period_and_non_interactive_and_small_amounts_skipped():
    events = [
        ev("Recent", PRO_DSP, 2026, 9, 500),  # inside MLC lag window
        ev("Radio Only", "BMI / Radio", 2025, 3, 500),  # not MLC-eligible
        ev("Tiny", PRO_DSP, 2025, 3, 5),  # below threshold
        ev("Anchor", MLC_DSP, 2025, 4, 100),
    ]
    got = detect_coverage_gaps("a1", events, NOW)
    assert [x["evidence"]["work_title"] for x in got if x["subtype"] == "WORK_MISSING_MECHANICAL"] == []


def test_foreign_pro_income_not_expected_at_mlc():
    events = [ev("Abroad", PRO_DSP, 2025, 3, 500, territory="GB"), ev("Anchor", MLC_DSP, 2025, 4, 100)]
    assert [x for x in detect_coverage_gaps("a1", events, NOW) if x["subtype"] == "WORK_MISSING_MECHANICAL"] == []


def test_mlc_only_work_flags_missing_performance_when_pro_data_exists():
    events = [
        ev("Paid Both", PRO_DSP, 2025, 3, 100),
        ev("Paid Both", MLC_DSP, 2025, 3, 150),
        ev("Mech Only", MLC_DSP, 2025, 3, 300),
    ]
    f = [x for x in detect_coverage_gaps("a1", events, NOW) if x["subtype"] == "WORK_MISSING_PERFORMANCE"]
    assert len(f) == 1 and f[0]["evidence"]["estimated_performance_floor"] == 200.0


# ── 2. dropout ───────────────────────────────────────────────────────────────

Q_MONTHS = [(2024, 2), (2024, 5), (2024, 8), (2024, 11), (2025, 2), (2025, 5)]


def _dropout_base(x_amount=50.0, y_in_gap=100.0):
    events = []
    for i, (y, m) in enumerate(Q_MONTHS):
        if i < 4:
            events.append(ev("Work X", "ASCAP / Internet", y, m, x_amount))
        events.append(ev("Work Y", "ASCAP / Internet", y, m, 100.0 if i < 4 else y_in_gap))
    return events


def test_dropout_flagged_when_payer_keeps_paying_others():
    f = detect_work_dropouts("a1", _dropout_base(), NOW)
    assert subtypes(f) == ["WORK_INCOME_DROPOUT"]
    e = f[0]["evidence"]
    assert e["work_title"] == "Work X" and e["last_paid_quarter"] == "2024-Q4"
    assert e["quarters_without_income"] == ["2025-Q1", "2025-Q2"]
    assert e["income_if_unchanged"] == 100.0
    assert f[0]["estimated_recoverable"] == 0.0


def test_dropout_not_flagged_when_payer_itself_went_quiet():
    assert [x for x in detect_work_dropouts("a1", _dropout_base(y_in_gap=5.0), NOW)
            if x["evidence"]["work_title"] == "Work X"] == []


def test_dropout_skips_tiny_works_and_short_gaps_and_renames():
    assert [x for x in detect_work_dropouts("a1", _dropout_base(x_amount=2.0), NOW)
            if x["evidence"]["work_title"] == "Work X"] == []

    short = [e for e in _dropout_base() if not (e["work_title"] == "Work Y" and e["timestamp"].year == 2025 and e["timestamp"].month == 5)]
    assert [x for x in detect_work_dropouts("a1", short, NOW) if x["evidence"]["work_title"] == "Work X"] == []

    renamed = _dropout_base() + [ev("Work Xs", "ASCAP / Internet", 2025, 2, 50.0)]
    assert [x for x in detect_work_dropouts("a1", renamed, NOW) if x["evidence"]["work_title"] == "Work X"] == []


def test_dropout_ignores_periods_inside_payer_lag():
    # Gap quarters are within 270 days of "now": too recent to call.
    recent_now = datetime(2025, 7, 1, tzinfo=timezone.utc)
    assert detect_work_dropouts("a1", _dropout_base(), recent_now) == []


# ── 3. share drift ───────────────────────────────────────────────────────────


def _share_events(shares):
    months = [(2024, 2), (2024, 5), (2024, 8), (2024, 11)]
    return [ev("Shared Song", "SESAC / DIGITAL MEDIA", y, m, 40.0, share=s) for (y, m), s in zip(months, shares)]


def test_share_drop_flagged_with_impact():
    f = detect_share_drift("a1", _share_events([50, 50, 25, 25]), NOW)
    assert subtypes(f) == ["WORK_SHARE_DRIFT"]
    e = f[0]["evidence"]
    assert (e["share_before_pct"], e["share_after_pct"], e["drop_quarter"]) == (50.0, 25.0, "2024-Q3")
    assert e["income_at_lower_share"] == 80.0 and e["income_if_prior_share_correct"] == 80.0


def test_share_restored_or_within_tolerance_or_missing_not_flagged():
    assert detect_share_drift("a1", _share_events([50, 25, 50, 50]), NOW) == []
    assert detect_share_drift("a1", _share_events([50, 50, 49.8, 49.8]), NOW) == []
    assert detect_share_drift("a1", _share_events([None, None, None, None]), NOW) == []
    assert detect_share_drift("a1", _share_events([25, 25, 50, 50]), NOW) == []  # increase is fine


# ── wiring / plumbing ────────────────────────────────────────────────────────


def test_run_all_combines_detectors():
    events = _coverage_base() + _share_events([50, 50, 25, 25])
    assert {"WORK_MISSING_MECHANICAL", "WORK_SHARE_DRIFT"} <= set(subtypes(run_work_level_rules("a1", events, NOW)))


def test_flag_off_by_default(monkeypatch):
    monkeypatch.delenv("XR7_WORK_LEVEL_RULES", raising=False)
    assert work_level_rules_enabled() is False
    monkeypatch.setenv("XR7_WORK_LEVEL_RULES", "1")
    assert work_level_rules_enabled() is True


def test_mlc_parser_now_captures_work_payable_pct():
    csv = _MLC_HEADER + "\n" + _row(usages="1000", royalty_amount="5.0", distributed="5.0")
    ev0 = parse_csv(csv.encode(), artist_id="a1").events[0]
    assert ev0["share_pct"] == 100.0
