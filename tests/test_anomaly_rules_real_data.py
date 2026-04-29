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

from datetime import date, datetime, timezone

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


def _payment(*, source: str, amount: float, received_at=NOW, period_start=None) -> dict:
    return {
        "id": f"p-{source}-{amount}",
        "payment_type": "ROYALTY",
        "amount": amount,
        "currency": "USD",
        "source": source,
        "received_at": received_at,
        "period_start": period_start,
    }


def test_stream_month_without_payment_does_not_fire_when_period_matches():
    """Regression for #208.

    Real shape: an artist uploads Feb 2026 statement on Apr 29 2026. Events
    have timestamp=2026-02-*, payments have period_start=2026-02-01 but
    received_at=now() (today). Pre-fix the rule bucketed payments by
    received_at, which always landed in "today's month" and so the rule fired
    saying Feb has no payments — even though Feb has 369 of them.

    Post-fix, period_start drives the bucketing and the rule stays silent.
    """
    feb = datetime(2026, 2, 15, tzinfo=timezone.utc)
    # Real ingestion stores period_start as a date, not a datetime — that
    # subtype dispatch is what tripped #208's first patch. Pin the date type.
    feb_period = date(2026, 2, 1)
    today = datetime(2026, 4, 29, tzinfo=timezone.utc)

    events = [
        {
            "id": f"e-{i}",
            "event_type": "STREAM",
            "work_title": "Some Track",
            "platform": "Spotify",
            "quantity": 1000,
            "unit_value": 0.004,
            "currency": "USD",
            "territory": "US",
            "timestamp": feb,
        }
        for i in range(5)
    ]
    payments = [
        _payment(source="DistroKid", amount=4.0, received_at=today, period_start=feb_period)
        for _ in range(5)
    ]

    findings = run_transparent_rules(ARTIST, events=events, payments=payments, contracts=[])
    subtypes = {f["subtype"] for f in findings}
    assert "STREAM_MONTH_WITHOUT_PAYMENT" not in subtypes, (
        f"Rule 4 should not fire when payment period_start matches event month; "
        f"got findings: {subtypes}"
    )


def _stream_in_month(
    *, year: int, month: int, day: int = 15, qty: int = 1000, rate: float = 0.004
) -> dict:
    """Helper for #209 lag-gate tests — produces a stream event in a specific month."""
    return {
        "id": f"e-{year}-{month}-{day}-{qty}",
        "event_type": "STREAM",
        "work_title": f"Track-{year}-{month}",
        "platform": "Spotify",
        "quantity": qty,
        "unit_value": rate,
        "currency": "USD",
        "territory": "US",
        "timestamp": datetime(year, month, day, tzinfo=timezone.utc),
    }


def test_stream_month_does_not_fire_when_only_one_month_uploaded():
    """Min-coverage gate (#209): single-statement upload has no comparison baseline.

    Without 3+ months of history, we can't tell "the artist has a missing-payment
    pattern" from "the artist only uploaded one statement." Stay quiet rather
    than fire a high-stakes claim.
    """
    feb = datetime(2026, 2, 15, tzinfo=timezone.utc)
    events = [
        {
            "id": f"e-{i}",
            "event_type": "STREAM",
            "work_title": "Some Track",
            "platform": "Spotify",
            "quantity": 1000,
            "unit_value": 0.004,
            "currency": "USD",
            "territory": "US",
            "timestamp": feb,
        }
        for i in range(5)
    ]
    findings = run_transparent_rules(ARTIST, events=events, payments=[], contracts=[])
    subtypes = {f["subtype"] for f in findings}
    assert "STREAM_MONTH_WITHOUT_PAYMENT" not in subtypes


def test_stream_month_does_not_fire_within_lag_window():
    """Lag gate (#209): recent months without payments aren't anomalous.

    Distributors and DSPs typically pay 60-90 days after the period closes.
    Streams in the last 90 days with no payment yet is normal cadence, not a
    missing payment. Set up 4 months ending in the current month, with the
    most recent month missing a payment — should not fire because the missing
    month is within the lag window.
    """
    today = datetime.now(timezone.utc).date()

    def _months_ago(n: int) -> tuple[int, int]:
        # Walk back n months from today's first-of-month.
        y, m = today.year, today.month
        for _ in range(n):
            m -= 1
            if m == 0:
                m = 12
                y -= 1
        return y, m

    months = [_months_ago(n) for n in range(4)]  # most recent → 3 months back
    events = [_stream_in_month(year=y, month=m) for (y, m) in months]
    # All months have a payment EXCEPT the most-recent one (still in lag).
    payments = [
        _payment(
            source="DistroKid",
            amount=4.0,
            received_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            period_start=date(y, m, 1),
        )
        for (y, m) in months[1:]
    ]
    findings = run_transparent_rules(ARTIST, events=events, payments=payments, contracts=[])
    subtypes = {f["subtype"] for f in findings}
    assert "STREAM_MONTH_WITHOUT_PAYMENT" not in subtypes


def test_stream_month_still_fires_for_old_unpaid_months():
    """Lag gate must NOT mask real signal — months from 6+ months ago should still fire.

    Sets up 6 months of events, all paid except for the OLDEST (6 months back).
    That month is well past the 90-day lag window → real missing-payment signal.
    """
    today = datetime.now(timezone.utc).date()

    def _months_ago(n: int) -> tuple[int, int]:
        y, m = today.year, today.month
        for _ in range(n):
            m -= 1
            if m == 0:
                m = 12
                y -= 1
        return y, m

    months = [_months_ago(n) for n in range(2, 8)]  # 2 to 7 months back, all past lag
    events = [_stream_in_month(year=y, month=m) for (y, m) in months]
    # All months EXCEPT the oldest get a payment.
    payments = [
        _payment(
            source="DistroKid",
            amount=4.0,
            received_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            period_start=date(y, m, 1),
        )
        for (y, m) in months[:-1]
    ]
    findings = run_transparent_rules(ARTIST, events=events, payments=payments, contracts=[])
    subtypes = {f["subtype"] for f in findings}
    assert "STREAM_MONTH_WITHOUT_PAYMENT" in subtypes
    f = next(x for x in findings if x["subtype"] == "STREAM_MONTH_WITHOUT_PAYMENT")
    # Recoverable should be the conservative 30% of unpaid stream value, not the full amount.
    gross = f["evidence"]["gross_unpaid_estimate"]
    assert f["estimated_recoverable"] < gross
    assert abs(f["estimated_recoverable"] - gross * 0.30) < 0.01


def test_stream_month_without_payment_falls_back_to_received_at_when_period_missing():
    """Pre-existing payment dicts without period_start (legacy data) keep working.

    Some existing rows in the DB may have been ingested before payments
    started carrying period_start consistently. The rule must fall back to
    received_at gracefully so we don't break existing behavior.
    """
    feb = datetime(2026, 2, 15, tzinfo=timezone.utc)
    same_month_received = datetime(2026, 2, 20, tzinfo=timezone.utc)

    events = [
        {
            "id": f"e-{i}",
            "event_type": "STREAM",
            "work_title": "Some Track",
            "platform": "Spotify",
            "quantity": 1000,
            "unit_value": 0.004,
            "currency": "USD",
            "territory": "US",
            "timestamp": feb,
        }
        for i in range(5)
    ]
    # No period_start — legacy shape — but received_at is in the same month.
    payments = [
        _payment(source="DistroKid", amount=4.0, received_at=same_month_received) for _ in range(5)
    ]

    findings = run_transparent_rules(ARTIST, events=events, payments=payments, contracts=[])
    subtypes = {f["subtype"] for f in findings}
    assert "STREAM_MONTH_WITHOUT_PAYMENT" not in subtypes


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
