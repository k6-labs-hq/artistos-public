from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from XR7.recovery.recoupment_tracker import compute_recoupment
from XR7.recovery.statute_tracker import classify_anomalies


@dataclass
class DeadlineRiskResult:
    risk_color: str
    days_remaining: int
    auto_escalation_triggers: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk_color": self.risk_color,
            "days_remaining": self.days_remaining,
            "auto_escalation_triggers": self.auto_escalation_triggers,
        }


def _to_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def evaluate_deadline_risk(
    anomalies: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    contracts: list[dict[str, Any]],
    payments: list[dict[str, Any]],
    payer_sla_windows: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Unify SOL, recoupment, claim age, and payer SLA windows into one risk output."""
    now = datetime.now(timezone.utc)
    classified = classify_anomalies(anomalies)
    recoupment = compute_recoupment(contracts, payments)

    min_sol_days = min(
        [int(a.get("sol_days_remaining")) for a in classified if isinstance(a.get("sol_days_remaining"), int)]
        or [9999]
    )

    sla_windows = payer_sla_windows or {
        "distrokid": 14,
        "tunecore": 21,
        "spotify": 30,
        "ascap": 45,
        "bmi": 45,
        "generic": 30,
    }

    triggers: list[dict[str, Any]] = []
    claim_days_left: list[int] = []

    for claim in claims:
        created_at = _to_utc(claim.get("created_at")) if isinstance(claim.get("created_at"), datetime) else None
        if created_at is None and claim.get("created_at"):
            try:
                created_at = _to_utc(datetime.fromisoformat(str(claim.get("created_at"))))
            except Exception:  # noqa: BLE001
                created_at = None
        if not created_at:
            continue

        payer_key = str(claim.get("payer") or "generic").lower()
        sla_days = int(sla_windows.get(payer_key, sla_windows.get("generic", 30)))
        age_days = max(0, (now - created_at).days)
        remaining = sla_days - age_days
        claim_days_left.append(remaining)

        if remaining <= 0:
            triggers.append(
                {
                    "trigger": "payer_sla_breached",
                    "claim_id": claim.get("id"),
                    "days_remaining": remaining,
                    "recommended_action": "escalate_now",
                }
            )
        elif remaining <= 5:
            triggers.append(
                {
                    "trigger": "payer_sla_near_breach",
                    "claim_id": claim.get("id"),
                    "days_remaining": remaining,
                    "recommended_action": "send_final_notice",
                }
            )

    for row in classified:
        if row.get("sol_status") in {"EXPIRED", "URGENT"}:
            triggers.append(
                {
                    "trigger": "sol_urgent",
                    "anomaly_id": row.get("id"),
                    "sol_status": row.get("sol_status"),
                    "days_remaining": row.get("sol_days_remaining"),
                    "recommended_action": "file_or_toll_immediately",
                }
            )

    for position in recoupment:
        flags = set(position.flags or [])
        if {"RECOUPMENT_DISCREPANCY", "EXCESS_RECOUPMENT"} & flags:
            triggers.append(
                {
                    "trigger": "recoupment_discrepancy",
                    "contract_id": position.contract_id,
                    "recommended_action": "audit_and_escalate",
                }
            )

    min_claim_days = min(claim_days_left or [9999])
    days_remaining = min(min_sol_days, min_claim_days)

    risk_color = "GREEN"
    if days_remaining <= 14 or any(t.get("trigger") == "sol_urgent" for t in triggers):
        risk_color = "RED"
    elif days_remaining <= 45 or triggers:
        risk_color = "YELLOW"

    return DeadlineRiskResult(
        risk_color=risk_color,
        days_remaining=int(days_remaining),
        auto_escalation_triggers=triggers,
    ).to_dict()
