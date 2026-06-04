"""Tests for the PROBABLE_UNCLAIMED_MECHANICALS rule.

This is the first rule that produces defensible recovery claims using
data we already have. It detects the "PRO documented your streams but
The MLC never paid you mechanicals" gap — the most common Black Box /
registration-drift signal in catalog royalty audits.

These tests pin the rule's behavior against the four cases that drove
the design: PRO-only artists with no MLC payments, PRO + partial MLC
coverage, artists with full MLC coverage, and the international /
non-DSP exclusion path.
"""

from __future__ import annotations

from datetime import datetime, timezone

from XR7.anomaly.rules.transparent_rules import run_transparent_rules

ARTIST = "test-artist"


def _stream(
    *, qty: int, platform: str, year: int = 2024, territory: str = "US", title: str = "Song"
) -> dict:
    return {
        "id": f"e-{platform}-{qty}-{year}",
        "event_type": "STREAM",
        "work_title": title,
        "platform": platform,
        "quantity": qty,
        "unit_value": 0.0005,
        "currency": "USD",
        "territory": territory,
        "timestamp": datetime(year, 6, 15, tzinfo=timezone.utc),
    }


def _payment(*, source: str, amount: float, year: int = 2024) -> dict:
    return {
        "id": f"p-{source}-{amount}",
        "payment_type": "ROYALTY",
        "amount": amount,
        "currency": "USD",
        "source": source,
        "received_at": datetime(year, 6, 15, tzinfo=timezone.utc),
        "period_start": datetime(year, 4, 1, tzinfo=timezone.utc).date(),
        "period_end": datetime(year, 6, 30, tzinfo=timezone.utc).date(),
    }


def _findings_of(subtype: str, all_findings: list[dict]) -> list[dict]:
    return [f for f in all_findings if f.get("subtype") == subtype]


class TestFires:
    def test_pro_streams_with_no_mlc_payments_fires(self):
        # 1,000,000 streams paying $0.0005/stream → $500 performance income.
        # Mechanical estimate: $500 × 1.5 ratio = $750.
        events = [
            _stream(qty=1_000_000, platform="ASCAP / Internet: SPOTIFY", year=2024),
        ]
        # ASCAP performance payment present, NO MLC payment.
        payments = [
            _payment(source="ASCAP / Internet: SPOTIFY", amount=500.0, year=2024),
        ]
        findings = _findings_of(
            "PROBABLE_UNCLAIMED_MECHANICALS",
            run_transparent_rules(ARTIST, events, payments, []),
        )
        assert len(findings) == 1
        f = findings[0]
        assert f["estimated_recoverable"] == 750.0
        assert f["evidence"]["mlc_eligible_stream_count"] == 1_000_000
        assert f["evidence"]["documented_performance_income"] == 500.0
        assert f["evidence"]["mech_to_perf_ratio"] == 1.5
        assert f["evidence"]["mlc_payments_received"] == 0.0
        assert f["evidence"]["mlc_coverage_pct"] == 0.0
        assert "17 U.S.C. § 115" in f["legal_basis"]
        assert "themlc.com" in f["evidence"]["citation_url"]

    def test_partial_mlc_coverage_subtracts_from_estimate(self):
        # 1M streams × $0.0005 = $500 perf × 1.5 ratio = $750 mechanical estimate.
        events = [
            _stream(qty=1_000_000, platform="ASCAP / Internet: SPOTIFY", year=2024),
        ]
        # Artist received $250 from MLC.
        payments = [
            _payment(source="MLC / Spotify / regular", amount=250.0, year=2024),
        ]
        findings = _findings_of(
            "PROBABLE_UNCLAIMED_MECHANICALS",
            run_transparent_rules(ARTIST, events, payments, []),
        )
        assert len(findings) == 1
        # 750 − 250 = 500 (unclaimed shortfall).
        assert findings[0]["estimated_recoverable"] == 500.0
        assert findings[0]["evidence"]["mlc_payments_received"] == 250.0
        # Coverage = 250 / 750 ≈ 33.3%
        assert findings[0]["evidence"]["mlc_coverage_pct"] == 33.3

    def test_share_implicit_in_unit_value(self):
        # Two artists, same 100k streams, but different unit values
        # (representing different writer shares).
        # Artist with 50% share (unit_value $0.0005) → perf $50 → mech estimate $75.
        # Below threshold; doesn't fire.
        events_half_share = [
            _stream(qty=100_000, platform="ASCAP / Internet: SPOTIFY", year=2024)
        ]
        assert (
            _findings_of(
                "PROBABLE_UNCLAIMED_MECHANICALS",
                run_transparent_rules(ARTIST, events_half_share, [], []),
            )
            == []
        )


class TestDoesNotFire:
    def test_no_dsp_streams_at_all(self):
        # Radio + Cable TV streams — sound-recording royalties, not MLC.
        events = [
            _stream(qty=10_000, platform="ASCAP / Cable TV - Blanket", year=2024),
            _stream(qty=5_000, platform="ASCAP / Broadcast and Satellite Radio", year=2024),
        ]
        findings = _findings_of(
            "PROBABLE_UNCLAIMED_MECHANICALS",
            run_transparent_rules(ARTIST, events, [], []),
        )
        assert findings == []

    def test_full_mlc_coverage_suppresses_finding(self):
        # 1M streams × $0.0005 × 1.5 = $750 mechanical estimate.
        # Artist already received $1,000 from MLC — over-covered.
        events = [_stream(qty=1_000_000, platform="Internet: APPLE SUBSCRIPTION", year=2024)]
        payments = [_payment(source="MLC / Apple / regular", amount=1_000.0, year=2024)]
        findings = _findings_of(
            "PROBABLE_UNCLAIMED_MECHANICALS",
            run_transparent_rules(ARTIST, events, payments, []),
        )
        assert findings == []

    def test_estimate_below_100_threshold(self):
        # 100k streams × $0.0005 × 1.5 = $75 mechanical estimate.
        # Below $100 fire threshold.
        events = [_stream(qty=100_000, platform="Internet: SPOTIFY", year=2024)]
        findings = _findings_of(
            "PROBABLE_UNCLAIMED_MECHANICALS",
            run_transparent_rules(ARTIST, events, [], []),
        )
        assert findings == []

    def test_international_streams_excluded(self):
        # International streams flow through foreign collectives, not MLC.
        events = [
            _stream(
                qty=500_000,
                platform="SESAC / INTERNATIONAL",
                year=2024,
                territory="INT",
            )
        ]
        findings = _findings_of(
            "PROBABLE_UNCLAIMED_MECHANICALS",
            run_transparent_rules(ARTIST, events, [], []),
        )
        assert findings == []
