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
        # 100,000 streams on Spotify Premium in 2024.
        # Estimated mechanical: 100,000 × $0.00165 = $165.00.
        events = [
            _stream(qty=100_000, platform="ASCAP / Internet: SPOTIFY", year=2024),
        ]
        # ASCAP performance payment present, NO MLC payment.
        payments = [
            _payment(source="ASCAP / Internet: SPOTIFY", amount=50.0, year=2024),
        ]
        findings = _findings_of(
            "PROBABLE_UNCLAIMED_MECHANICALS",
            run_transparent_rules(ARTIST, events, payments, []),
        )
        assert len(findings) == 1
        f = findings[0]
        assert f["estimated_recoverable"] == 165.0
        assert f["evidence"]["mlc_eligible_stream_count"] == 100_000
        assert f["evidence"]["mlc_payments_received"] == 0.0
        assert f["evidence"]["mlc_coverage_pct"] == 0.0
        assert "17 U.S.C. § 115" in f["legal_basis"]
        assert "themlc.com" in f["evidence"]["citation_url"]

    def test_partial_mlc_coverage_subtracts_from_estimate(self):
        events = [
            _stream(qty=100_000, platform="ASCAP / Internet: SPOTIFY", year=2024),
        ]
        # Estimate is $165.00; artist received $65 from MLC.
        payments = [
            _payment(source="MLC / Spotify / regular", amount=65.0, year=2024),
        ]
        findings = _findings_of(
            "PROBABLE_UNCLAIMED_MECHANICALS",
            run_transparent_rules(ARTIST, events, payments, []),
        )
        assert len(findings) == 1
        # 165 − 65 = 100 (unclaimed shortfall).
        assert findings[0]["estimated_recoverable"] == 100.0
        assert findings[0]["evidence"]["mlc_payments_received"] == 65.0
        # Coverage = 65 / 165 ≈ 39.4%
        assert findings[0]["evidence"]["mlc_coverage_pct"] == 39.4

    def test_rate_uses_per_year_table(self):
        # 100,000 streams in 2020 at $0.00096 (Phonorecords III) = $96.00.
        # Below $100 threshold → finding suppressed.
        events_2020 = [_stream(qty=100_000, platform="Internet: TIDAL", year=2020)]
        assert (
            _findings_of(
                "PROBABLE_UNCLAIMED_MECHANICALS",
                run_transparent_rules(ARTIST, events_2020, [], []),
            )
            == []
        )
        # Same volume in 2023 (Phonorecords IV): 100k × $0.00155 = $155 — fires.
        events_2023 = [_stream(qty=100_000, platform="Internet: TIDAL", year=2023)]
        findings = _findings_of(
            "PROBABLE_UNCLAIMED_MECHANICALS",
            run_transparent_rules(ARTIST, events_2023, [], []),
        )
        assert len(findings) == 1
        assert findings[0]["estimated_recoverable"] == 155.0


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
        # 100k streams in 2024 → estimated $165 mechanical.
        # Artist already received $165 from MLC — no shortfall.
        events = [_stream(qty=100_000, platform="Internet: APPLE SUBSCRIPTION", year=2024)]
        payments = [_payment(source="MLC / Apple / regular", amount=200.0, year=2024)]
        findings = _findings_of(
            "PROBABLE_UNCLAIMED_MECHANICALS",
            run_transparent_rules(ARTIST, events, payments, []),
        )
        assert findings == []

    def test_estimate_below_100_threshold(self):
        # 10,000 streams in 2024 → only $16.50 mechanical estimate.
        events = [_stream(qty=10_000, platform="Internet: SPOTIFY", year=2024)]
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
