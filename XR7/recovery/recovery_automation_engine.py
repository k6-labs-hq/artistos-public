from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


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
