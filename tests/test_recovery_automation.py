"""Tests for XR7/recovery/recovery_automation.py (merged from engine file)."""
from __future__ import annotations

import pytest

from XR7.recovery.recovery_automation import (
    automate_recovery,
    build_automation_plan,
    build_correction_packet,
)
from XR7.recovery.recovery_automation_engine import (
    automate_recovery as automate_recovery_shim,
)
from XR7.recovery.recovery_automation_engine import (
    build_correction_packet as build_correction_packet_shim,
)

# ---------------------------------------------------------------------------
# build_correction_packet
# ---------------------------------------------------------------------------


def test_correction_packet_structure():
    finding = {"type": "UNDERPAYMENT", "amount": 500.0, "row": {"counterparty": "BMI"}}
    packet = build_correction_packet("artist-99", finding)

    assert packet["artist_id"] == "artist-99"
    assert packet["packet_type"] == "CORRECTION_REQUEST"
    assert packet["finding_type"] == "UNDERPAYMENT"
    assert packet["payload"] is finding
    assert "generated_at" in packet


def test_correction_packet_missing_finding_type():
    packet = build_correction_packet("artist-1", {})
    assert packet["finding_type"] is None


def test_correction_packet_generated_at_is_iso():
    packet = build_correction_packet("a", {"type": "X"})
    ts = packet["generated_at"]
    assert "T" in ts  # ISO-8601


# ---------------------------------------------------------------------------
# automate_recovery
# ---------------------------------------------------------------------------


def test_automate_recovery_empty_findings():
    result = automate_recovery("artist-x", [])
    assert result["artist_id"] == "artist-x"
    assert result["generated_packets"] == 0
    assert result["queued_submissions"] == 0
    assert result["packets"] == []
    assert result["submission_queue"] == []


def test_automate_recovery_multiple_findings():
    findings = [
        {"type": "UNDERPAYMENT", "row": {"counterparty": "ASCAP"}, "amount": 200.0},
        {"type": "MISSING_STATEMENT", "row": {"counterparty": "BMI"}, "amount": 100.0},
        {"type": "METADATA_MISMATCH", "row": None, "amount": 50.0},
    ]
    result = automate_recovery("artist-2", findings)

    assert result["generated_packets"] == 3
    assert result["queued_submissions"] == 3
    assert len(result["packets"]) == 3
    assert len(result["submission_queue"]) == 3


def test_automate_recovery_submission_counterparty():
    findings = [{"type": "X", "row": {"counterparty": "TuneCore"}}]
    result = automate_recovery("artist-3", findings)
    assert result["submission_queue"][0]["target"] == "TuneCore"


def test_automate_recovery_unknown_counterparty_fallback():
    findings = [{"type": "X", "row": {}}]
    result = automate_recovery("artist-4", findings)
    assert result["submission_queue"][0]["target"] == "unknown_counterparty"


def test_automate_recovery_null_row_fallback():
    findings = [{"type": "X"}]  # no "row" key at all
    result = automate_recovery("artist-5", findings)
    assert result["submission_queue"][0]["target"] == "unknown_counterparty"


def test_automate_recovery_billing_policy():
    result = automate_recovery("artist-6", [{"type": "X"}])
    assert result["recovery_triggered_billing"]["policy"] == "contingency_12pct"
    assert result["remittance_tracking"]["status"] == "ACTIVE"


# ---------------------------------------------------------------------------
# build_automation_plan — next-steps branching
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status,expected_first_step",
    [
        ("IDENTIFIED", "Finalize packet"),
        ("PREPARED", "Finalize packet"),
        ("SUBMITTED", "Auto-send reminder"),
        ("FILED", "Auto-send reminder"),
        ("IN_REVIEW", "Auto-send reminder"),
        ("SETTLED", "Monitor settlement"),
        ("CLOSED", "Monitor settlement"),
        ("UNKNOWN_STATUS", "Monitor settlement"),
    ],
)
def test_automation_plan_next_steps(status, expected_first_step):
    plan = build_automation_plan({"status": status})
    assert plan["automated_next_steps"][0] == expected_first_step


def test_automation_plan_red_risk_adds_legal_escalation():
    plan = build_automation_plan({"status": "SUBMITTED"}, deadline_risk={"risk_color": "RED"})
    assert "Immediate legal escalation notice" in plan["automated_escalation_triggers"]


def test_automation_plan_yellow_risk_adds_manager_review():
    plan = build_automation_plan({"status": "IDENTIFIED"}, deadline_risk={"risk_color": "YELLOW"})
    assert "Manager review before next follow-up" in plan["automated_escalation_triggers"]


def test_automation_plan_green_risk_no_extra_escalation():
    plan = build_automation_plan({"status": "IDENTIFIED"}, deadline_risk={"risk_color": "GREEN"})
    triggers = plan["automated_escalation_triggers"]
    assert "Immediate legal escalation notice" not in triggers
    assert "Manager review before next follow-up" not in triggers


def test_automation_plan_has_evidence_refresh():
    plan = build_automation_plan({"status": "SUBMITTED"})
    refresh = plan["automated_evidence_refresh"]
    assert refresh["enabled"] is True
    assert refresh["refresh_interval_days"] == 14


def test_automation_plan_has_follow_ups():
    plan = build_automation_plan({"status": "SUBMITTED"})
    assert plan["automated_follow_ups"]["enabled"] is True
    assert plan["automated_follow_ups"]["cadence_days"] == 7


def test_automation_plan_no_deadline_risk_defaults_green():
    plan = build_automation_plan({"status": "SUBMITTED"})
    triggers = plan["automated_escalation_triggers"]
    assert "Immediate legal escalation notice" not in triggers


# ---------------------------------------------------------------------------
# Backward-compat shim re-exports
# ---------------------------------------------------------------------------


def test_shim_build_correction_packet_identical():
    finding = {"type": "UNDERPAYMENT"}
    direct = build_correction_packet("a", finding)
    via_shim = build_correction_packet_shim("a", finding)
    # Both call the same function; shim should return identical structure
    assert direct.keys() == via_shim.keys()
    assert direct["packet_type"] == via_shim["packet_type"]


def test_shim_automate_recovery_identical():
    direct = automate_recovery("a", [])
    via_shim = automate_recovery_shim("a", [])
    assert direct == via_shim
