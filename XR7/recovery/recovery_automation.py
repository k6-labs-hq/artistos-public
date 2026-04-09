from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Correction packet helpers (previously in recovery_automation_engine.py)
# ---------------------------------------------------------------------------


def build_correction_packet(artist_id: str, finding: dict[str, Any]) -> dict[str, Any]:
    return {
        "artist_id": artist_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "packet_type": "CORRECTION_REQUEST",
        "finding_type": finding.get("type"),
        "payload": finding,
    }


def automate_recovery(artist_id: str, findings: list[dict[str, Any]]) -> dict[str, Any]:
    packets = [build_correction_packet(artist_id, f) for f in findings]
    submissions = [
        {
            "target": (f.get("row") or {}).get("counterparty") or "unknown_counterparty",
            "status": "QUEUED",
            "packet_type": "CORRECTION_REQUEST",
        }
        for f in findings
    ]
    return {
        "artist_id": artist_id,
        "generated_packets": len(packets),
        "queued_submissions": len(submissions),
        "packets": packets,
        "submission_queue": submissions,
        "remittance_tracking": {"status": "ACTIVE", "tracked_items": len(findings)},
        "recovery_triggered_billing": {"status": "ENABLED", "policy": "contingency_12pct"},
    }


# ---------------------------------------------------------------------------
# Automation-plan builder
# ---------------------------------------------------------------------------


def build_automation_plan(claim: dict[str, Any], deadline_risk: dict[str, Any] | None = None) -> dict[str, Any]:
    """Generate automated follow-up/escalation/evidence refresh actions for claims."""
    status = str(claim.get("status") or "IDENTIFIED")
    risk_color = str((deadline_risk or {}).get("risk_color") or "GREEN")

    reminders = [
        "Send payer follow-up every 7 days until state transition",
        "Refresh evidence packet every 14 days while unresolved",
    ]
    escalations = ["Trigger escalation when payer SLA breaches"]
    if risk_color == "RED":
        escalations.append("Immediate legal escalation notice")
    elif risk_color == "YELLOW":
        escalations.append("Manager review before next follow-up")

    next_steps = []
    if status in {"IDENTIFIED", "PREPARED"}:
        next_steps = ["Finalize packet", "Submit claim", "Schedule initial follow-up"]
    elif status in {"SUBMITTED", "FILED", "IN_REVIEW"}:
        next_steps = ["Auto-send reminder", "Escalate if no response", "Regenerate evidence appendix"]
    else:
        next_steps = ["Monitor settlement", "Track deposit status", "Close case checklist"]

    return {
        "automated_next_steps": next_steps,
        "automated_reminders": reminders,
        "automated_escalation_triggers": escalations,
        "automated_evidence_refresh": {
            "enabled": True,
            "refresh_interval_days": 14,
        },
        "automated_follow_ups": {
            "enabled": True,
            "cadence_days": 7,
        },
    }
