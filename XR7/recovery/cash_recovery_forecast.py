from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import mean
from typing import Any

from XR7.models.anomaly import Anomaly
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.ml_feedback import CalibrationSnapshot


class RecommendedNextAction:
    COLLECT_EVIDENCE = "COLLECT_EVIDENCE"
    FILE_CLAIM = "FILE_CLAIM"
    ESCALATE_PAYER = "ESCALATE_PAYER"
    NEGOTIATE_SETTLEMENT = "NEGOTIATE_SETTLEMENT"
    WAIT_FOR_RESPONSE = "WAIT_FOR_RESPONSE"
    CLOSE_AND_COLLECT = "CLOSE_AND_COLLECT"


@dataclass
class CashRecoveryForecast:
    expected_payout: float
    confidence: float
    time_to_cash_days: int
    recommended_next_action: str
    reasoning_summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "expected_payout": round(float(self.expected_payout), 2),
            "confidence": round(max(0.0, min(1.0, float(self.confidence))), 6),
            "time_to_cash_days": int(max(0, self.time_to_cash_days)),
            "recommended_next_action": self.recommended_next_action,
            "reasoning_summary": self.reasoning_summary,
        }


def _payer_key(claim: Claim) -> str:
    evidence = claim.evidence or {}
    legal = evidence.get("legal_support", {}) if isinstance(evidence, dict) else {}
    basis = legal.get("contract_basis", []) if isinstance(legal, dict) else []
    if basis and isinstance(basis, list):
        top = basis[0] if isinstance(basis[0], dict) else {}
        payer = str(top.get("counterparty") or "").strip()
        if payer:
            return payer.lower()
    return "unknown_payer"


def _duration_days(start: datetime | None, end: datetime | None) -> int | None:
    if not start or not end:
        return None
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    return max(0, int((end - start).days))


def _pick_confidence(
    claim: Claim, anomaly: Anomaly | None, snapshots: list[CalibrationSnapshot]
) -> float:
    if not snapshots:
        return float(anomaly.confidence_score if anomaly else 0.6)

    subtype = str(anomaly.subtype if anomaly else claim.claim_type or "").lower()
    category = str(anomaly.category if anomaly else claim.claim_type or "").lower()

    for scope_type, key in (("subtype", subtype), ("category", category), ("global", "global")):
        for snap in snapshots:
            if str(snap.scope_type).lower() == scope_type and str(snap.scope_key).lower() == key:
                return float(snap.posterior_mean)

    return float(anomaly.confidence_score if anomaly else 0.6)


def _payer_cycle_days(claim: Claim, historical_claims: list[Claim]) -> int:
    payer = _payer_key(claim)
    durations: list[int] = []
    for row in historical_claims:
        if _payer_key(row) != payer:
            continue
        if str(row.status) not in {ClaimStatus.PAID, ClaimStatus.CLOSED}:
            continue
        days = _duration_days(row.created_at, row.updated_at)
        if days is not None:
            durations.append(days)
    if durations:
        return int(round(mean(durations)))
    return 45


def _lifecycle_days(status: str) -> int:
    status_key = str(status)
    mapping = {
        str(ClaimStatus.IDENTIFIED): 50,
        str(ClaimStatus.PREPARED): 40,
        str(ClaimStatus.SUBMITTED): 32,
        str(ClaimStatus.FILED): 28,
        str(ClaimStatus.IN_REVIEW): 20,
        str(ClaimStatus.ACCEPTED): 10,
        str(ClaimStatus.PAID): 3,
        str(ClaimStatus.CLOSED): 0,
    }
    return int(mapping.get(status_key, 30))


def _complexity_penalty(claim: Claim, anomaly: Anomaly | None) -> float:
    evidence = claim.evidence or {}
    proof_rows = 0
    if isinstance(evidence, dict):
        proof_rows = len((evidence.get("proof", {}) or {}).get("ledger_evidence", []) or [])
    base = 1.0 + min(0.4, proof_rows / 100.0)
    if anomaly and str(anomaly.severity) == "CRITICAL":
        base += 0.15
    return base


def _recommended_action(claim: Claim, confidence: float, time_to_cash_days: int) -> str:
    status_key = str(claim.status)
    if status_key in {str(ClaimStatus.IDENTIFIED), str(ClaimStatus.PREPARED)}:
        return (
            RecommendedNextAction.FILE_CLAIM
            if confidence >= 0.5
            else RecommendedNextAction.COLLECT_EVIDENCE
        )
    if status_key in {str(ClaimStatus.SUBMITTED), str(ClaimStatus.FILED)}:
        return (
            RecommendedNextAction.ESCALATE_PAYER
            if time_to_cash_days > 35
            else RecommendedNextAction.WAIT_FOR_RESPONSE
        )
    if status_key == str(ClaimStatus.IN_REVIEW):
        return RecommendedNextAction.NEGOTIATE_SETTLEMENT
    if status_key in {str(ClaimStatus.ACCEPTED), str(ClaimStatus.PAID)}:
        return RecommendedNextAction.CLOSE_AND_COLLECT
    return RecommendedNextAction.WAIT_FOR_RESPONSE


def build_claim_forecast(
    claim: Claim,
    anomaly: Anomaly | None,
    snapshots: list[CalibrationSnapshot],
    historical_claims: list[Claim],
) -> CashRecoveryForecast:
    """Compute expected payout and timing for a single claim using lightweight heuristics."""
    baseline_expected = float(claim.recovered_amount or 0.0)
    if baseline_expected <= 0.0 and anomaly is not None:
        baseline_expected = float(anomaly.estimated_recoverable or 0.0)
    if baseline_expected <= 0.0:
        baseline_expected = 250.0

    confidence = _pick_confidence(claim, anomaly, snapshots)
    complexity = _complexity_penalty(claim, anomaly)
    cycle_days = _payer_cycle_days(claim, historical_claims)
    lifecycle_days = _lifecycle_days(str(claim.status))

    expected = baseline_expected * max(0.5, min(1.2, confidence + 0.2)) / complexity
    time_to_cash_days = int(round((cycle_days + lifecycle_days) * complexity))
    recommended = _recommended_action(claim, confidence, time_to_cash_days)

    reason = (
        f"Forecast blends calibration confidence ({confidence:.2f}), payer-cycle baseline ({cycle_days} days), "
        f"lifecycle stage ({claim.status}), and complexity factor ({complexity:.2f})."
    )

    return CashRecoveryForecast(
        expected_payout=max(0.0, expected),
        confidence=max(0.0, min(1.0, confidence)),
        time_to_cash_days=max(0, time_to_cash_days),
        recommended_next_action=recommended,
        reasoning_summary=reason,
    )
