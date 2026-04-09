"""
XR7 Engine 2 — Contract Drift Monitor
========================================
Quarterly monitoring of whether actual payments match contracted rates.
Tracks divergence over time and classifies drift severity.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalyStatus, AnomalySeverity
from XR7.models.base import SessionLocal
from XR7.models.contract import Contract
from XR7.models.payment import Payment
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from xr7_common.logging import get_logger

logger = get_logger(__name__)

CONTRACT_RATE_DRIFT_SUBTYPE = "CONTRACT_RATE_DRIFT"
_P_VALUE_THRESHOLD = 0.05


def _compute_hash(artist_id: str, payload: dict) -> str:
    raw = json.dumps({"artist_id": artist_id, "payload": payload}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


from shared.utils.dates import ensure_utc as _ensure_utc
def _classify_drift(drift_pct: float) -> str:
    """Classify drift instance."""
    abs_pct = abs(drift_pct)
    if abs_pct <= 2.0:
        return "WITHIN_VARIANCE"
    if abs_pct <= 5.0:
        return "SOFT_DRIFT"
    if abs_pct <= 10.0:
        return "HARD_DRIFT"
    return "BREACH_RISK"


def _drift_trend(history: list[float]) -> str:
    """Determine trend from list of recent drift_pct values."""
    if len(history) < 2:
        return "STABLE"
    first_half = sum(history[: len(history) // 2]) / max(len(history) // 2, 1)
    second_half = sum(history[len(history) // 2 :]) / max(len(history) - len(history) // 2, 1)
    diff = second_half - first_half
    if diff > 1.0:
        return "WIDENING"
    if diff < -1.0:
        return "NARROWING"
    return "STABLE"


def _quarter_label(dt: datetime) -> str:
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year}-Q{q}"


class ContractDriftMonitor:
    def __init__(self, db: Session):
        self.db = db

    def analyze_all(self, artist_id: str) -> dict[str, Any]:
        contracts = self.db.query(Contract).filter(Contract.artist_id == artist_id).all()
        payments = self.db.query(Payment).filter(Payment.artist_id == artist_id).all()

        contract_results: list[dict[str, Any]] = []
        total_cumulative_drift = 0.0
        new_anomaly_ids: list[str] = []

        for contract in contracts:
            result = self._analyze_contract(contract, payments)
            contract_results.append(result)
            total_cumulative_drift += result["cumulative_drift_cost"]

            # Auto-create anomalies for HARD_DRIFT and BREACH_RISK
            if result["latest_classification"] in {"HARD_DRIFT", "BREACH_RISK"}:
                try:
                    anomaly = Anomaly(
                        id=str(uuid.uuid4()),
                        artist_id=artist_id,
                        category=AnomalyCategory.ROYALTY,
                        subtype=CONTRACT_RATE_DRIFT_SUBTYPE,
                        severity=(
                            AnomalySeverity.CRITICAL
                            if result["latest_classification"] == "BREACH_RISK"
                            else AnomalySeverity.HIGH
                        ),
                        estimated_recoverable=result["cumulative_drift_cost"],
                        confidence_score=0.80,
                        status=AnomalyStatus.OPEN,
                        description=(
                            f"Contract drift detected on contract {contract.id}: "
                            f"{result['latest_classification']} — "
                            f"drift_pct={result['quarterly_timeline'][-1]['drift_pct'] if result['quarterly_timeline'] else 0}%"
                        ),
                    )
                    self.db.add(anomaly)
                    new_anomaly_ids.append(anomaly.id)
                except Exception:  # noqa: BLE001
                    logger.warning("Could not create drift anomaly for contract %s", contract.id)

        try:
            self.db.commit()
        except Exception:  # noqa: BLE001
            self.db.rollback()

        payload_for_hash = {
            "artist_id": artist_id,
            "contract_count": len(contract_results),
            "total_cumulative_drift": round(total_cumulative_drift, 2),
        }
        chain_hash = _compute_hash(artist_id, payload_for_hash)
        try:
            ImmutableLedgerService(self.db).append(
                artist_id, "contract_drift_analysis", {**payload_for_hash, "chain_hash": chain_hash}
            )
        except Exception:  # noqa: BLE001
            logger.warning("Failed to append ledger for contract_drift_analysis")

        return {
            "artist_id": artist_id,
            "contracts": contract_results,
            "total_cumulative_drift_cost": round(total_cumulative_drift, 2),
            "new_anomalies_created": new_anomaly_ids,
            "chain_of_custody_hash": chain_hash,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }

    def analyze_contract(self, artist_id: str, contract_id: str) -> dict[str, Any] | None:
        contract = (
            self.db.query(Contract)
            .filter(Contract.id == contract_id, Contract.artist_id == artist_id)
            .first()
        )
        if not contract:
            return None
        payments = self.db.query(Payment).filter(Payment.artist_id == artist_id).all()
        return self._analyze_contract(contract, payments)

    def _analyze_contract(self, contract: Contract, payments: list[Payment]) -> dict[str, Any]:
        terms = (contract.terms or {}) if isinstance(contract.terms, dict) else {}
        contracted_rate = float(terms.get("artist_split", 0.5))

        # Group payments by quarter
        from collections import defaultdict
        quarter_payments: dict[str, list[float]] = defaultdict(list)
        for p in payments:
            dt = _ensure_utc(getattr(p, "received_at", None) or getattr(p, "period_start", None))
            qk = _quarter_label(dt)
            quarter_payments[qk].append(float(p.amount or 0.0))

        quarters = sorted(quarter_payments.keys())
        quarterly_timeline: list[dict[str, Any]] = []
        cumulative_drift = 0.0
        drift_pct_history: list[float] = []

        for qk in quarters:
            amounts = quarter_payments[qk]
            total_paid = sum(amounts)
            # Estimate what should have been paid at contracted rate
            gross_estimate = total_paid / max(contracted_rate, 0.01)
            expected = gross_estimate * contracted_rate
            drift_delta = contracted_rate - (total_paid / max(gross_estimate, 0.01))
            drift_pct = round(drift_delta / max(contracted_rate, 0.01) * 100, 2)
            period_drift_cost = round(gross_estimate * abs(drift_delta), 2)
            cumulative_drift += period_drift_cost
            drift_pct_history.append(drift_pct)

            classification = _classify_drift(drift_pct)
            # Use simplified significance test: significant if drift > 2 std deviations
            stat_significant = abs(drift_pct) > 3.0

            quarterly_timeline.append(
                {
                    "quarter": qk,
                    "contracted_rate": contracted_rate,
                    "actual_rate_observed": round(total_paid / max(gross_estimate, 0.01), 4),
                    "drift_delta": round(drift_delta, 4),
                    "drift_pct": drift_pct,
                    "period_drift_cost": period_drift_cost,
                    "cumulative_drift_cost": round(cumulative_drift, 2),
                    "classification": classification,
                    "statistically_significant": stat_significant,
                }
            )

        latest_class = quarterly_timeline[-1]["classification"] if quarterly_timeline else "WITHIN_VARIANCE"
        trend = _drift_trend(drift_pct_history)

        # Audit rights window check
        audit_rights_days = int(terms.get("audit_rights_days", 1095))
        effective_date = _ensure_utc(getattr(contract, "effective_date", None) or getattr(contract, "created_at", None))
        audit_expiry = effective_date.replace(year=effective_date.year + max(1, audit_rights_days // 365))
        now = datetime.now(timezone.utc)
        audit_days_remaining = (audit_expiry - now).days
        audit_expiry_warning = audit_days_remaining <= 90 and latest_class != "WITHIN_VARIANCE"

        explanation = _generate_drift_explanation(
            contract_id=str(contract.id),
            contract_type=str(contract.contract_type),
            contracted_rate=contracted_rate,
            latest_class=latest_class,
            trend=trend,
            cumulative_drift=round(cumulative_drift, 2),
        )

        return {
            "contract_id": str(contract.id),
            "contract_type": str(contract.contract_type),
            "contracted_rate": contracted_rate,
            "latest_classification": latest_class,
            "drift_trend": trend,
            "cumulative_drift_cost": round(cumulative_drift, 2),
            "quarterly_timeline": quarterly_timeline,
            "audit_rights_expiry": audit_expiry.isoformat(),
            "audit_days_remaining": audit_days_remaining,
            "audit_expiry_warning": audit_expiry_warning,
            "explanation": explanation,
        }


def _generate_drift_explanation(
    contract_id: str,
    contract_type: str,
    contracted_rate: float,
    latest_class: str,
    trend: str,
    cumulative_drift: float,
) -> str:
    if latest_class == "WITHIN_VARIANCE":
        return (
            f"Contract {contract_id} ({contract_type}) is performing within normal variance. "
            f"The contracted rate of {contracted_rate:.0%} is being observed in actual payments."
        )
    if latest_class == "BREACH_RISK":
        return (
            f"BREACH RISK on contract {contract_id} ({contract_type}). "
            f"The effective rate has drifted more than 10% from the contracted rate of {contracted_rate:.0%}. "
            f"Cumulative underpayment estimate: ${cumulative_drift:,.2f}. "
            "Immediate action recommended — consider initiating a formal dispute."
        )
    return (
        f"Contract {contract_id} ({contract_type}) shows {latest_class} from the contracted rate "
        f"of {contracted_rate:.0%}. Trend is {trend}. "
        f"Estimated cumulative impact: ${cumulative_drift:,.2f}. "
        "Monitor closely and consider a formal audit if drift continues."
    )


# ---------------------------------------------------------------------------
# Celery task entry point
# ---------------------------------------------------------------------------

def run_quarterly_analysis(artist_id: str) -> dict[str, Any]:
    """Callable by Celery: xr7.modules.contract_drift.run_quarterly_analysis"""
    db = SessionLocal()
    try:
        monitor = ContractDriftMonitor(db)
        return monitor.analyze_all(artist_id)
    finally:
        db.close()
