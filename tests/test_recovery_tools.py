"""
Tests for the new artist-centric money-recovery modules:
- statute_tracker: SOL classification and summaries
- rate_benchmarker: comparable-rate comparison and reports
- audit_tracker: audit eligibility analysis and summaries
- priority_ranker: action queue scoring and ranking
- recoupment_tracker: recoupment position and discrepancy detection
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pytest

from arcos7.recovery.statute_tracker import (
    classify_anomalies,
    get_urgent_anomalies,
    sol_summary,
    SOLStatus,
    DEFAULT_SOL_WINDOWS,
)
from arcos7.ml.rate_benchmarker import (
    RateBenchmarker,
    compare_event_rates,
    RateTier,
    DEFAULT_BENCHMARKS,
)
from arcos7.recovery.audit_tracker import (
    analyze_audit_eligibility,
    audit_summary,
    AuditEligibility,
)
from arcos7.recovery.priority_ranker import (
    rank_anomalies,
    rank_claims,
    build_action_queue,
    PriorityItem,
    ActionType,
)
from arcos7.recovery.recoupment_tracker import (
    compute_recoupment,
    recoupment_summary,
    RecoupmentStatus,
    RecoupmentFlag,
)


# ===========================================================================
# Helpers
# ===========================================================================

def _make_anomaly(
    category: str = "ROYALTY",
    subtype: str = "MISSING_PAYMENT",
    created_days_ago: int = 100,
    territory: str | None = None,
    estimated_recoverable: float | None = 500.0,
    confidence_score: float = 0.8,
    status: str = "OPEN",
    anomaly_id: str = "a-1",
) -> dict:
    created = datetime.now(timezone.utc) - timedelta(days=created_days_ago)
    return {
        "id": anomaly_id,
        "artist_id": "artist-test",
        "category": category,
        "subtype": subtype,
        "territory": territory,
        "estimated_recoverable": estimated_recoverable,
        "confidence_score": confidence_score,
        "status": status,
        "description": f"{category}/{subtype} anomaly",
        "created_at": created.isoformat(),
    }


def _make_contract(
    contract_type: str = "LABEL",
    counterparty: str = "Big Label LLC",
    terms: dict | None = None,
    contract_id: str = "c-1",
) -> dict:
    return {
        "id": contract_id,
        "contract_type": contract_type,
        "counterparty": counterparty,
        "territory": "US",
        "effective_date": "2020-01-01",
        "terms": terms or {},
    }


def _make_payment(
    amount: float = 1000.0,
    payment_type: str = "ROYALTY",
    received_at: str = "2024-01-01",
) -> dict:
    return {
        "id": "p-1",
        "payment_type": payment_type,
        "amount": amount,
        "currency": "USD",
        "received_at": received_at,
        "period_start": received_at,
    }


def _make_event(
    event_type: str = "STREAM",
    unit_value: float = 0.004,
    quantity: int = 1000,
    territory: str | None = "US",
) -> dict:
    return {
        "event_type": event_type,
        "unit_value": unit_value,
        "quantity": quantity,
        "territory": territory,
    }


# ===========================================================================
# statute_tracker
# ===========================================================================

class TestStatuteTracker:
    def test_ok_anomaly_recent(self):
        anomaly = _make_anomaly(created_days_ago=30)
        results = classify_anomalies([anomaly])
        assert len(results) == 1
        assert results[0]["sol_status"] == SOLStatus.OK
        assert results[0]["sol_days_remaining"] > 180

    def test_urgent_anomaly_close_to_deadline(self):
        # 3-year SOL window → deadline in ~1095 days; create 1050 days ago → ~45 left
        anomaly = _make_anomaly(created_days_ago=1050)
        results = classify_anomalies([anomaly])
        assert results[0]["sol_status"] == SOLStatus.URGENT
        assert 0 < results[0]["sol_days_remaining"] <= 90

    def test_at_risk_anomaly(self):
        # Created 950 days ago on a 1095-day window → ~145 days left
        anomaly = _make_anomaly(created_days_ago=950)
        results = classify_anomalies([anomaly])
        assert results[0]["sol_status"] == SOLStatus.AT_RISK

    def test_expired_anomaly(self):
        anomaly = _make_anomaly(created_days_ago=1200)  # past 3-year window
        results = classify_anomalies([anomaly])
        assert results[0]["sol_status"] == SOLStatus.EXPIRED
        assert results[0]["sol_days_remaining"] < 0

    def test_unknown_status_when_no_created_at(self):
        anomaly = {"id": "a-1", "category": "ROYALTY", "subtype": "X", "artist_id": "artist-1"}
        results = classify_anomalies([anomaly])
        assert results[0]["sol_status"] == SOLStatus.UNKNOWN
        assert results[0]["sol_days_remaining"] is None

    def test_territory_override_gb(self):
        # GB has 6-year window (2190 days); created 1500 days ago → should be OK
        anomaly = _make_anomaly(created_days_ago=1500, territory="GB")
        results = classify_anomalies([anomaly])
        assert results[0]["sol_status"] == SOLStatus.OK
        assert results[0]["sol_window_days"] == 2190

    def test_sorted_most_urgent_first(self):
        recent = _make_anomaly(created_days_ago=10, anomaly_id="recent")
        old = _make_anomaly(created_days_ago=1080, anomaly_id="old")
        results = classify_anomalies([recent, old])
        assert results[0]["id"] == "old"  # most urgent first

    def test_get_urgent_anomalies_filters_ok(self):
        ok_anomaly = _make_anomaly(created_days_ago=50, anomaly_id="ok")
        urgent_anomaly = _make_anomaly(created_days_ago=1050, anomaly_id="urgent")
        results = get_urgent_anomalies([ok_anomaly, urgent_anomaly])
        ids = [r["id"] for r in results]
        assert "urgent" in ids
        assert "ok" not in ids

    def test_sol_summary_counts_correctly(self):
        anomalies = [
            _make_anomaly(created_days_ago=1200, anomaly_id="expired"),
            _make_anomaly(created_days_ago=1060, anomaly_id="urgent"),
            _make_anomaly(created_days_ago=950, anomaly_id="at_risk"),
            _make_anomaly(created_days_ago=30, anomaly_id="ok"),
        ]
        summary = sol_summary(anomalies)
        assert summary["counts_by_status"][SOLStatus.EXPIRED] == 1
        assert summary["counts_by_status"][SOLStatus.URGENT] == 1
        assert summary["counts_by_status"][SOLStatus.AT_RISK] == 1
        assert summary["counts_by_status"][SOLStatus.OK] == 1
        assert summary["action_required"] is True
        assert summary["total_anomalies"] == 4

    def test_sol_summary_action_not_required_when_all_ok(self):
        anomalies = [_make_anomaly(created_days_ago=30, anomaly_id=f"a{i}") for i in range(3)]
        summary = sol_summary(anomalies)
        assert summary["action_required"] is False

    def test_classify_augments_original_dict(self):
        anomaly = _make_anomaly()
        results = classify_anomalies([anomaly])
        assert "sol_status" in results[0]
        assert "sol_days_remaining" in results[0]
        assert "sol_deadline" in results[0]
        assert "sol_window_days" in results[0]

    def test_touring_shorter_sol_window(self):
        # TOURING default window is 730 days (2 years)
        anomaly = _make_anomaly(category="TOURING", created_days_ago=100)
        results = classify_anomalies([anomaly])
        assert results[0]["sol_window_days"] == 730


# ===========================================================================
# rate_benchmarker
# ===========================================================================

class TestRateBenchmarker:
    def test_critical_tier_below_50_percent_of_median(self):
        events = [_make_event(unit_value=0.001)]  # < 50% of $0.004 median
        results = compare_event_rates("artist-1", events)
        assert results[0]["rate_tier"] == RateTier.CRITICAL
        assert results[0]["estimated_underpayment"] > 0

    def test_below_market_tier(self):
        events = [_make_event(unit_value=0.0025)]  # ~62% of median
        results = compare_event_rates("artist-1", events)
        assert results[0]["rate_tier"] == RateTier.BELOW_MARKET

    def test_at_market_tier(self):
        events = [_make_event(unit_value=0.004)]  # exactly at median
        results = compare_event_rates("artist-1", events)
        assert results[0]["rate_tier"] == RateTier.AT_MARKET

    def test_above_market_tier(self):
        events = [_make_event(unit_value=0.006)]  # > 110% of median
        results = compare_event_rates("artist-1", events)
        assert results[0]["rate_tier"] == RateTier.ABOVE_MARKET

    def test_no_benchmark_for_unknown_event_type(self):
        events = [{"event_type": "UNKNOWN_TYPE", "unit_value": 5.0, "quantity": 100}]
        results = compare_event_rates("artist-1", events)
        assert results[0]["rate_tier"] == RateTier.NO_BENCHMARK

    def test_shortfall_is_zero_above_market(self):
        events = [_make_event(unit_value=0.009)]
        results = compare_event_rates("artist-1", events)
        assert results[0]["shortfall_per_unit"] == 0.0
        assert results[0]["estimated_underpayment"] == 0.0

    def test_estimated_underpayment_scales_with_quantity(self):
        events_low = [_make_event(unit_value=0.001, quantity=100)]
        events_high = [_make_event(unit_value=0.001, quantity=10000)]
        r_low = compare_event_rates("artist-1", events_low)[0]
        r_high = compare_event_rates("artist-1", events_high)[0]
        assert r_high["estimated_underpayment"] == pytest.approx(r_low["estimated_underpayment"] * 100)

    def test_benchmarker_report_structure(self):
        events = [_make_event(unit_value=0.001), _make_event(unit_value=0.004)]
        benchmarker = RateBenchmarker()
        report = benchmarker.benchmark("artist-1", events)
        d = report.to_dict()
        assert "total_estimated_underpayment" in d
        assert "by_event_type" in d
        assert "tier_counts" in d
        assert "comparisons" in d
        assert d["artist_id"] == "artist-1"

    def test_benchmarker_total_underpayment_non_negative(self):
        events = [_make_event(unit_value=0.009, quantity=100)]
        benchmarker = RateBenchmarker()
        report = benchmarker.benchmark("artist-1", events)
        assert report.total_estimated_underpayment >= 0.0

    def test_benchmarker_empty_events(self):
        benchmarker = RateBenchmarker()
        report = benchmarker.benchmark("artist-1", [])
        assert report.total_estimated_underpayment == 0.0
        assert report.comparisons == []

    def test_custom_benchmark_override(self):
        custom = {"STREAM": {"DEFAULT": {"p25": 0.001, "p50": 0.002, "p75": 0.003}}}
        events = [_make_event(unit_value=0.002)]
        results = compare_event_rates("artist-1", events, benchmarks=custom)
        assert results[0]["rate_tier"] == RateTier.AT_MARKET

    def test_territory_specific_benchmark_used(self):
        # US benchmark p50 for STREAM is 0.0042; event at 0.001 → CRITICAL
        events = [{"event_type": "STREAM", "unit_value": 0.001, "quantity": 100, "territory": "US"}]
        results = compare_event_rates("artist-1", events)
        assert results[0]["benchmark_p50"] == pytest.approx(0.0042)
        assert results[0]["rate_tier"] == RateTier.CRITICAL


# ===========================================================================
# audit_tracker
# ===========================================================================

class TestAuditTracker:
    def test_never_audited_is_highest_priority(self):
        contracts = [_make_contract(terms={})]  # no last_audit_date
        recs = analyze_audit_eligibility(contracts)
        assert recs[0].eligibility == AuditEligibility.NEVER_AUDITED

    def test_eligible_after_interval_passed(self):
        last_audit = (date.today() - timedelta(days=3 * 365 + 30)).isoformat()
        contracts = [_make_contract(terms={"last_audit_date": last_audit})]
        recs = analyze_audit_eligibility(contracts)
        assert recs[0].eligibility == AuditEligibility.ELIGIBLE
        assert recs[0].days_until_eligible is None

    def test_eligible_soon_within_90_days(self):
        # Interval is 3 years for LABEL; make it eligible in 60 days
        last_audit = (date.today() - timedelta(days=3 * 365 - 60)).isoformat()
        contracts = [_make_contract(terms={"last_audit_date": last_audit})]
        recs = analyze_audit_eligibility(contracts)
        assert recs[0].eligibility == AuditEligibility.ELIGIBLE_SOON
        assert 0 < recs[0].days_until_eligible <= 90

    def test_not_yet_eligible(self):
        last_audit = date.today().isoformat()  # just audited today
        contracts = [_make_contract(terms={"last_audit_date": last_audit})]
        recs = analyze_audit_eligibility(contracts)
        assert recs[0].eligibility == AuditEligibility.NOT_YET_ELIGIBLE
        assert recs[0].days_until_eligible > 90

    def test_estimated_recovery_uses_payment_total(self):
        contracts = [_make_contract(terms={})]
        payments = [_make_payment(amount=10000.0)]
        recs = analyze_audit_eligibility(contracts, payments=payments)
        # LABEL default rate is 15%
        assert recs[0].estimated_recovery == pytest.approx(10000.0 * 0.15)
        assert recs[0].total_payments_in_period == pytest.approx(10000.0)

    def test_sorted_by_estimated_recovery_within_eligibility(self):
        # Two never-audited contracts; one with more payments should rank first
        c1 = _make_contract(counterparty="A", contract_id="c1")
        c2 = _make_contract(counterparty="B", contract_id="c2")
        payments = [_make_payment(amount=50000.0), _make_payment(amount=1000.0)]
        recs = analyze_audit_eligibility([c1, c2], payments=payments)
        # Both never-audited; higher estimated recovery first
        assert recs[0].estimated_recovery >= recs[1].estimated_recovery

    def test_audit_summary_structure(self):
        contracts = [
            _make_contract(terms={}, contract_id="c1"),
            _make_contract(
                terms={"last_audit_date": (date.today() - timedelta(days=365 * 4)).isoformat()},
                contract_id="c2",
            ),
        ]
        recs = analyze_audit_eligibility(contracts)
        summary = audit_summary(recs)
        assert "total_contracts" in summary
        assert "eligible_for_audit" in summary
        assert "total_potential_recovery" in summary
        assert "immediately_actionable_recovery" in summary
        assert summary["total_contracts"] == 2

    def test_publishing_has_2_year_interval(self):
        last_audit = (date.today() - timedelta(days=2 * 365 + 30)).isoformat()
        contracts = [_make_contract(contract_type="PUBLISHING", terms={"last_audit_date": last_audit})]
        recs = analyze_audit_eligibility(contracts)
        assert recs[0].audit_interval_years == 2
        assert recs[0].eligibility == AuditEligibility.ELIGIBLE


# ===========================================================================
# priority_ranker
# ===========================================================================

class TestPriorityRanker:
    def test_rank_anomalies_returns_list(self):
        anomalies = [_make_anomaly(anomaly_id=f"a{i}") for i in range(3)]
        results = rank_anomalies(anomalies)
        assert len(results) == 3
        assert all(isinstance(r, PriorityItem) for r in results)

    def test_higher_recoverable_gets_higher_rank(self):
        low_rec = _make_anomaly(estimated_recoverable=100.0, anomaly_id="low")
        high_rec = _make_anomaly(estimated_recoverable=10000.0, anomaly_id="high")
        results = rank_anomalies([low_rec, high_rec])
        assert results[0].item_id == "high"

    def test_higher_confidence_gets_higher_score(self):
        low_conf = _make_anomaly(confidence_score=0.3, anomaly_id="low")
        high_conf = _make_anomaly(confidence_score=0.95, anomaly_id="high")
        results = rank_anomalies([low_conf, high_conf])
        assert results[0].item_id == "high"

    def test_urgent_sol_boosts_rank(self):
        ok_anomaly = _make_anomaly(anomaly_id="ok")
        ok_anomaly["sol_status"] = "OK"
        urgent_anomaly = _make_anomaly(anomaly_id="urgent")
        urgent_anomaly["sol_status"] = "URGENT"
        results = rank_anomalies([ok_anomaly, urgent_anomaly])
        assert results[0].item_id == "urgent"

    def test_rank_anomalies_normalised_scores_0_to_100(self):
        anomalies = [_make_anomaly(anomaly_id=f"a{i}", estimated_recoverable=float(100 * (i + 1))) for i in range(5)]
        results = rank_anomalies(anomalies)
        scores = [r.normalised_score for r in results]
        assert max(scores) == pytest.approx(100.0)
        assert min(scores) >= 0.0

    def test_rank_anomalies_rank_starts_at_1(self):
        anomalies = [_make_anomaly(anomaly_id=f"a{i}") for i in range(3)]
        results = rank_anomalies(anomalies)
        ranks = sorted(r.priority_rank for r in results)
        assert ranks[0] == 1

    def test_rank_claims_returns_correct_action(self):
        claims = [
            {"id": "cl-1", "artist_id": "artist-1", "claim_type": "ROYALTY", "status": "SUBMITTED",
             "created_at": datetime.now(timezone.utc).isoformat()}
        ]
        results = rank_claims(claims)
        assert len(results) == 1
        assert results[0].action == ActionType.ADVANCE_CLAIM
        assert results[0].item_type == "CLAIM"

    def test_build_action_queue_merges_anomalies_and_claims(self):
        anomalies = [_make_anomaly(anomaly_id="a1")]
        claims = [
            {"id": "c1", "artist_id": "artist-1", "claim_type": "ROYALTY", "status": "SUBMITTED",
             "created_at": datetime.now(timezone.utc).isoformat()}
        ]
        queue = build_action_queue(anomalies, claims)
        assert len(queue) == 2
        item_types = {item["item_type"] for item in queue}
        assert "ANOMALY" in item_types
        assert "CLAIM" in item_types

    def test_build_action_queue_empty_inputs(self):
        queue = build_action_queue([], [])
        assert queue == []

    def test_priority_item_to_dict_has_required_keys(self):
        anomalies = [_make_anomaly()]
        results = rank_anomalies(anomalies)
        d = results[0].to_dict()
        for key in ("item_id", "item_type", "action", "priority_rank",
                    "normalised_score", "estimated_recoverable", "confidence_score"):
            assert key in d

    def test_expired_sol_gets_highest_urgency_boost(self):
        ok = _make_anomaly(anomaly_id="ok", estimated_recoverable=1000.0)
        ok["sol_status"] = "OK"
        expired = _make_anomaly(anomaly_id="expired", estimated_recoverable=1000.0)
        expired["sol_status"] = "EXPIRED"
        results = rank_anomalies([ok, expired])
        assert results[0].item_id == "expired"


# ===========================================================================
# recoupment_tracker
# ===========================================================================

class TestRecoupmentTracker:
    def test_unrecouped_when_payments_below_advance(self):
        contracts = [_make_contract(terms={"advance": 50000.0, "recoupment_rate": 1.0})]
        payments = [_make_payment(amount=10000.0)]
        positions = compute_recoupment(contracts, payments)
        assert len(positions) == 1
        assert positions[0].recoupment_status == RecoupmentStatus.UNRECOUPED
        assert positions[0].recoupment_balance == pytest.approx(40000.0)

    def test_recouped_when_payments_equal_advance(self):
        # Payments exactly equal the advance → cleanly recouped, balance zero
        contracts = [_make_contract(terms={"advance": 10000.0, "recoupment_rate": 1.0})]
        payments = [_make_payment(amount=10000.0)]
        positions = compute_recoupment(contracts, payments)
        assert positions[0].recoupment_status == RecoupmentStatus.RECOUPED
        assert positions[0].recoupment_balance == pytest.approx(0.0)

    def test_over_recouped_when_payments_exceed_advance(self):
        # More was deducted than the advance → OVER_RECOUPED flag
        contracts = [_make_contract(terms={"advance": 10000.0, "recoupment_rate": 1.0})]
        payments = [_make_payment(amount=15000.0)]
        positions = compute_recoupment(contracts, payments)
        assert positions[0].recoupment_status == RecoupmentStatus.OVER_RECOUPED

    def test_partial_recoupment_rate(self):
        # 50% of payments applied to recoupment; $10k payment → $5k recouped; balance $5k
        contracts = [_make_contract(terms={"advance": 10000.0, "recoupment_rate": 0.5})]
        payments = [_make_payment(amount=10000.0)]
        positions = compute_recoupment(contracts, payments)
        assert positions[0].recoupment_balance == pytest.approx(5000.0)
        assert positions[0].recoupment_status == RecoupmentStatus.UNRECOUPED

    def test_recoupment_discrepancy_flag(self):
        # Our calculation says balance=40k, counterparty claims 60k
        contracts = [_make_contract(terms={
            "advance": 50000.0,
            "recoupment_rate": 1.0,
            "recoupment_balance": 60000.0,  # reported is much higher
        })]
        payments = [_make_payment(amount=10000.0)]
        positions = compute_recoupment(contracts, payments)
        assert RecoupmentFlag.RECOUPMENT_DISCREPANCY in positions[0].flags

    def test_no_flag_when_balance_matches(self):
        contracts = [_make_contract(terms={
            "advance": 50000.0,
            "recoupment_rate": 1.0,
            "recoupment_balance": 40000.0,  # matches our calculation
        })]
        payments = [_make_payment(amount=10000.0)]
        positions = compute_recoupment(contracts, payments)
        assert RecoupmentFlag.RECOUPMENT_DISCREPANCY not in positions[0].flags

    def test_skip_contracts_without_advance(self):
        contracts = [_make_contract(terms={"rate": 0.1})]  # no advance
        positions = compute_recoupment(contracts)
        assert positions == []

    def test_skip_non_recoupable_contract_types(self):
        contracts = [_make_contract(contract_type="TOURING", terms={"advance": 5000.0})]
        positions = compute_recoupment(contracts)
        assert positions == []

    def test_sorted_largest_balance_first(self):
        c1 = _make_contract(terms={"advance": 50000.0, "recoupment_rate": 1.0}, contract_id="c1")
        c2 = _make_contract(terms={"advance": 5000.0, "recoupment_rate": 1.0}, contract_id="c2")
        positions = compute_recoupment([c1, c2], [_make_payment(amount=1000.0)])
        assert positions[0].recoupment_balance > positions[1].recoupment_balance

    def test_recoupment_summary_structure(self):
        contracts = [_make_contract(terms={"advance": 10000.0, "recoupment_rate": 1.0})]
        payments = [_make_payment(amount=4000.0)]
        positions = compute_recoupment(contracts, payments)
        summary = recoupment_summary(positions)
        assert "total_advance" in summary
        assert "total_recouped" in summary
        assert "total_remaining_balance" in summary
        assert "flagged_contracts" in summary
        assert summary["total_advance"] == pytest.approx(10000.0)
        assert summary["total_recouped"] == pytest.approx(4000.0)
        assert summary["total_remaining_balance"] == pytest.approx(6000.0)

    def test_position_to_dict_has_required_keys(self):
        contracts = [_make_contract(terms={"advance": 5000.0})]
        payments = [_make_payment(amount=1000.0)]
        positions = compute_recoupment(contracts, payments)
        d = positions[0].to_dict()
        for key in ("contract_id", "contract_type", "advance", "recoupment_balance",
                    "recoupment_status", "flags", "anomalies"):
            assert key in d

    def test_excess_recoupment_flag(self):
        # More recouped than the advance — possible accounting error
        contracts = [_make_contract(terms={"advance": 5000.0, "recoupment_rate": 1.0})]
        payments = [_make_payment(amount=20000.0)]
        positions = compute_recoupment(contracts, payments)
        assert RecoupmentFlag.EXCESS_RECOUPMENT in positions[0].flags
        assert positions[0].recoupment_status == RecoupmentStatus.OVER_RECOUPED

    def test_multiple_contracts_tracked_independently(self):
        c1 = _make_contract(contract_id="c1", terms={"advance": 10000.0})
        c2 = _make_contract(contract_id="c2", contract_type="PUBLISHING", terms={"advance": 20000.0})
        positions = compute_recoupment([c1, c2])
        assert len(positions) == 2
        ids = {p.contract_id for p in positions}
        assert "c1" in ids and "c2" in ids
