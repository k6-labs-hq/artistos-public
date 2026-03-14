from __future__ import annotations

from typing import Any

from XR7.models.anomaly import Anomaly
from XR7.models.claim import Claim
from XR7.recovery.payer_playbooks.templates import DEFAULT_TEMPLATE, TEMPLATES_BY_PAYER, PayerPlaybookTemplate


def _detect_payer(claim: Claim, anomaly: Anomaly | None) -> str:
    evidence = claim.evidence or {}
    if isinstance(evidence, dict):
        contracts = ((evidence.get("legal_support") or {}).get("contract_basis") or [])
        if contracts and isinstance(contracts, list):
            counterparty = str((contracts[0] or {}).get("counterparty") or "").strip().lower()
            for key in TEMPLATES_BY_PAYER:
                if key in counterparty:
                    return key
    subtype = str(anomaly.subtype if anomaly else claim.claim_type or "").lower()
    for key in TEMPLATES_BY_PAYER:
        if key in subtype:
            return key
    return "generic"


def _template_for_payer(payer_key: str) -> PayerPlaybookTemplate:
    return TEMPLATES_BY_PAYER.get(payer_key, DEFAULT_TEMPLATE)


def build_claim_playbook(claim: Claim, anomaly: Anomaly | None = None) -> dict[str, Any]:
    """Return payer-specific claim packet guidance and escalation policy."""
    payer_key = _detect_payer(claim, anomaly)
    template = _template_for_payer(payer_key)
    packet = claim.evidence or {}
    reconciliation = packet.get("reconciliation", {}) if isinstance(packet, dict) else {}

    instructions = list(template.packet_instructions)
    discrepancy = float((reconciliation or {}).get("discrepancy_amount") or 0.0)
    if discrepancy > 0:
        instructions.append(f"Address reconciliation discrepancy ${discrepancy:,.2f} before submission.")

    return {
        "claim_id": claim.id,
        "artist_id": claim.artist_id,
        "payer": template.payer,
        "required_fields_checklist": template.required_fields,
        "sla_expectations": {
            "initial_response_days": template.sla_days,
            "follow_up_days": max(7, template.sla_days // 2),
        },
        "escalation_paths": template.escalation_path,
        "claim_packet_instructions": instructions,
    }


def summarize_artist_playbooks(claims: list[Claim], anomalies_by_id: dict[str, Anomaly]) -> dict[str, Any]:
    """Summarize playbook coverage and SLA heat-map across an artist's open claims."""
    rows = [
        build_claim_playbook(c, anomalies_by_id.get(c.anomaly_id))
        for c in claims
    ]
    if not rows:
        return {"total_claims": 0, "by_payer": {}, "slowest_sla_days": 0, "claims": []}

    by_payer: dict[str, int] = {}
    slowest = 0
    for row in rows:
        payer = str(row.get("payer") or "Unknown")
        by_payer[payer] = by_payer.get(payer, 0) + 1
        sla_days = int((row.get("sla_expectations") or {}).get("initial_response_days") or 0)
        slowest = max(slowest, sla_days)

    return {
        "total_claims": len(rows),
        "by_payer": by_payer,
        "slowest_sla_days": slowest,
        "claims": rows,
    }
