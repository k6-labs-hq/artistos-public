"""
Tests for the two new transparent anomaly rules added to support real PRO
data ingestion (#160 BMI + #162 MLC):

- HIGH_RETROACTIVE_RATIO: per-payer reprocessing/adjustment percentage,
  designed to catch the "64% MLC reprocessing" pattern even when other
  current-period payers (like BMI) dilute the artist-wide ratio.
- TRACK_RATE_OUTLIER: per-track per-stream rate variance, flags tracks
  earning < 50% of the artist's median.

Fixtures use the same dict-shape the AnomalyEngine produces internally
via _events_to_dicts / _payments_to_dicts, so we test the rule logic
end-to-end without hitting the DB.
"""

from __future__ import annotations

from datetime import datetime, timezone

from XR7.anomaly.rules.transparent_rules import run_transparent_rules

ARTIST = "test-artist-1"
NOW = datetime.now(timezone.utc)


def _stream(*, title: str, qty: int, unit_value: float) -> dict:
    return {
        "id": f"e-{title}-{qty}",
        "event_type": "STREAM",
        "work_title": title,
        "platform": "Test",
        "quantity": qty,
        "unit_value": unit_value,
        "currency": "USD",
        "territory": "US",
        "timestamp": NOW,
    }


def _payment(*, source: str, amount: float, received_at=NOW) -> dict:
    return {
        "id": f"p-{source}-{amount}",
        "payment_type": "ROYALTY",
        "amount": amount,
        "currency": "USD",
        "source": source,
        "received_at": received_at,
    }


def _findings_by_rule(findings: list[dict], rule_id: str) -> list[dict]:
    return [f for f in findings if f.get("rule_id") == rule_id]


# ─── HIGH_RETROACTIVE_RATIO ──────────────────────────────────────────────


def test_high_retroactive_ratio_fires_for_mlc_above_threshold():
    """MLC with 74% retroactive should fire even when BMI dollar volume dominates."""
    payments = [
        # MLC: $50 total, $40 retroactive (80%) → above 30% threshold
        _payment(source="MLC / Spotify / regular", amount=10.00),
        _payment(source="MLC / Spotify / reprocessing", amount=30.00),
        _payment(source="MLC / Apple Music / adjustment", amount=10.00),
        # BMI: $500 total, all current — would dilute artist-wide ratio if aggregated
        _payment(source="BMI / SPOTIFY PREM", amount=500.00),
    ]
    findings = run_transparent_rules(ARTIST, events=[], payments=payments, contracts=[])
    matches = _findings_by_rule(findings, "HIGH_RETROACTIVE_RATIO")
    assert len(matches) == 1
    f = matches[0]
    assert f["severity"] == "HIGH"  # MLC ratio > 50%
    assert f["evidence"]["worst_payer"] == "MLC"
    assert "MLC" in f["evidence"]["by_payer"]
    assert "BMI" not in f["evidence"]["by_payer"]  # BMI didn't trip the threshold
    assert f["evidence"]["by_payer"]["MLC"]["retroactive_ratio"] == 0.8


def test_high_retroactive_ratio_does_not_fire_when_below_threshold():
    """All payers below 30% retroactive → no finding."""
    payments = [
        _payment(source="MLC / Spotify / regular", amount=80.00),
        _payment(source="MLC / Spotify / reprocessing", amount=20.00),  # 20%
        _payment(source="BMI / SPOTIFY PREM", amount=500.00),
    ]
    findings = run_transparent_rules(ARTIST, events=[], payments=payments, contracts=[])
    assert _findings_by_rule(findings, "HIGH_RETROACTIVE_RATIO") == []


def test_high_retroactive_ratio_handles_spaces_in_source_label():
    """Real parser produces 'MLC / Spotify / reprocessing' with spaces — match must work."""
    payments = [
        _payment(source="MLC / Spotify / regular", amount=20.00),
        _payment(source="MLC / Spotify / reprocessing", amount=80.00),  # 80%
    ]
    findings = run_transparent_rules(ARTIST, events=[], payments=payments, contracts=[])
    matches = _findings_by_rule(findings, "HIGH_RETROACTIVE_RATIO")
    assert len(matches) == 1
    assert matches[0]["evidence"]["by_payer"]["MLC"]["retroactive_ratio"] == 0.8


def test_high_retroactive_ratio_severity_medium_between_30_and_50():
    """Between 30% and 50% retroactive → MEDIUM severity."""
    payments = [
        _payment(source="MLC / Spotify / regular", amount=60.00),
        _payment(source="MLC / Spotify / reprocessing", amount=40.00),  # 40%
    ]
    findings = run_transparent_rules(ARTIST, events=[], payments=payments, contracts=[])
    matches = _findings_by_rule(findings, "HIGH_RETROACTIVE_RATIO")
    assert len(matches) == 1
    assert matches[0]["severity"] == "MEDIUM"


# ─── TRACK_RATE_OUTLIER ──────────────────────────────────────────────────


def test_track_outlier_fires_for_below_half_median():
    """One track at 45% of median across a meaningful catalog → fires."""
    events = [
        _stream(title="Track A", qty=100_000, unit_value=0.001),  # rate 0.001
        _stream(title="Track B", qty=100_000, unit_value=0.001),  # 0.001
        _stream(title="Track C", qty=100_000, unit_value=0.0011),  # 0.0011
        _stream(title="Track D", qty=100_000, unit_value=0.0009),  # 0.0009
        _stream(
            title="Track E", qty=100_000, unit_value=0.0004
        ),  # 0.0004 ← outlier (40% of median)
    ]
    findings = run_transparent_rules(ARTIST, events=events, payments=[], contracts=[])
    matches = _findings_by_rule(findings, "TRACK_RATE_OUTLIER")
    assert len(matches) == 1
    f = matches[0]
    titles = [o["title"] for o in f["evidence"]["top_outliers"]]
    assert "Track E" in titles


def test_track_outlier_skips_low_volume_tracks():
    """Tracks with <1000 streams shouldn't trip the outlier rule (insufficient data)."""
    events = [
        _stream(title="Track A", qty=100_000, unit_value=0.001),
        _stream(title="Track B", qty=100_000, unit_value=0.001),
        _stream(title="Track C", qty=100_000, unit_value=0.001),
        _stream(title="Track D", qty=100_000, unit_value=0.001),
        # Outlier but only 100 streams → ignored
        _stream(title="LowVolume", qty=100, unit_value=0.0001),
    ]
    findings = run_transparent_rules(ARTIST, events=events, payments=[], contracts=[])
    assert _findings_by_rule(findings, "TRACK_RATE_OUTLIER") == []


def test_track_outlier_needs_minimum_4_tracks():
    """With <4 tracks, median is unreliable; rule shouldn't fire."""
    events = [
        _stream(title="A", qty=100_000, unit_value=0.001),
        _stream(title="B", qty=100_000, unit_value=0.001),
        _stream(title="C", qty=100_000, unit_value=0.0001),  # would be outlier with more data
    ]
    findings = run_transparent_rules(ARTIST, events=events, payments=[], contracts=[])
    assert _findings_by_rule(findings, "TRACK_RATE_OUTLIER") == []


def test_track_outlier_recoverable_amount_is_volume_weighted():
    """Recoverable estimate = sum of (median - outlier_rate) * outlier_volume."""
    events = [
        _stream(title="A", qty=100_000, unit_value=0.001),
        _stream(title="B", qty=100_000, unit_value=0.001),
        _stream(title="C", qty=100_000, unit_value=0.001),
        _stream(title="D", qty=100_000, unit_value=0.001),
        # Outlier: 200K streams at 0.0002 → median is 0.001, gap = 0.0008 → 200K * 0.0008 = $160
        _stream(title="Outlier", qty=200_000, unit_value=0.0002),
    ]
    findings = run_transparent_rules(ARTIST, events=events, payments=[], contracts=[])
    matches = _findings_by_rule(findings, "TRACK_RATE_OUTLIER")
    assert len(matches) == 1
    # Recoverable should be ~$160 (rounded)
    assert matches[0]["estimated_recoverable"] == 160.0
