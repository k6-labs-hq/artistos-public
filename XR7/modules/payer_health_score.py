"""
XR7 Engine 2 — Payer Health Score
=====================================
Generates a live counterparty risk rating (0–100) for every distributor,
PRO, label, streaming platform, and payer organisation in the artist's
earnings ecosystem.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly, AnomalyStatus
from XR7.models.base import SessionLocal
from XR7.models.claim import Claim
from XR7.models.payment import Payment
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from xr7_common.logging import get_logger

logger = get_logger(__name__)

RISK_TIERS = {
    (80, 100): "TRUSTED",
    (60, 79): "RELIABLE",
    (40, 59): "WATCH",
    (20, 39): "ELEVATED_RISK",
    (0, 19): "HIGH_RISK",
}


def _risk_tier(score: int) -> str:
    for (lo, hi), label in RISK_TIERS.items():
        if lo <= score <= hi:
            return label
    return "HIGH_RISK"


def _compute_hash(artist_id: str, payload: dict) -> str:
    raw = json.dumps({"artist_id": artist_id, "payload": payload}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def _ensure_utc(dt: datetime | None) -> datetime:
    now = datetime.now(timezone.utc)
    if dt is None:
        return now
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _payer_from_payment(p: Payment) -> str:
    return str(getattr(p, "source", None) or "Unknown")


def _payer_from_claim(c: Claim) -> str:
    evidence = c.evidence or {}
    if isinstance(evidence, dict):
        legal = evidence.get("legal_support", {})
        if isinstance(legal, dict):
            contracts = legal.get("contract_basis", [])
            if contracts and isinstance(contracts, list):
                cp = str((contracts[0] or {}).get("counterparty") or "").strip()
                if cp:
                    return cp
    return "Unknown"


class PayerHealthScorer:
    def __init__(self, db: Session):
        self.db = db

    def score_all(self, artist_id: str) -> dict[str, Any]:
        payments = self.db.query(Payment).filter(Payment.artist_id == artist_id).all()
        anomalies = self.db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        claims = self.db.query(Claim).filter(Claim.artist_id == artist_id).all()

        # Group by payer
        payer_payments: dict[str, list[Payment]] = defaultdict(list)
        for p in payments:
            payer_payments[_payer_from_payment(p)].append(p)

        payer_anomalies: dict[str, list[Anomaly]] = defaultdict(list)
        for a in anomalies:
            payer = str(a.territory or "Unknown")  # territory ≈ payer proxy
            payer_anomalies[payer].append(a)

        payer_claims: dict[str, list[Claim]] = defaultdict(list)
        for c in claims:
            payer_claims[_payer_from_claim(c)].append(c)

        payers = set(payer_payments.keys()) | set(payer_claims.keys())
        scores: list[dict[str, Any]] = []
        for payer in sorted(payers):
            entry = self._score_payer(
                payer=payer,
                payments=payer_payments.get(payer, []),
                anomalies=payer_anomalies.get(payer, []),
                claims=payer_claims.get(payer, []),
                all_payments=payments,
            )
            scores.append(entry)

        # Sort ascending (highest risk first)
        scores.sort(key=lambda x: x["composite_score"])

        payload_for_hash = {
            "artist_id": artist_id,
            "payer_count": len(scores),
        }
        chain_hash = _compute_hash(artist_id, payload_for_hash)
        try:
            ImmutableLedgerService(self.db).append(
                artist_id, "payer_health_scores_refreshed", {**payload_for_hash, "chain_hash": chain_hash}
            )
        except Exception:  # noqa: BLE001
            logger.warning("Failed to append ledger for payer_health_scores")

        return {
            "artist_id": artist_id,
            "payer_scores": scores,
            "chain_of_custody_hash": chain_hash,
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

    def score_single(self, artist_id: str, payer_id: str) -> dict[str, Any] | None:
        all_result = self.score_all(artist_id)
        for entry in all_result["payer_scores"]:
            if entry["payer_id"] == payer_id or entry["payer_name"].lower() == payer_id.lower():
                return entry
        return None

    def _score_payer(
        self,
        payer: str,
        payments: list[Payment],
        anomalies: list[Anomaly],
        claims: list[Claim],
        all_payments: list[Payment],
    ) -> dict[str, Any]:
        total_all = len(all_payments) or 1

        # 1. Payment accuracy (0–25): anomaly rate
        open_anomalies = [a for a in anomalies if a.status != AnomalyStatus.CLOSED]
        payer_payment_count = len(payments) or 1
        anomaly_rate = min(len(open_anomalies) / payer_payment_count, 1.0)
        payment_accuracy = round((1 - anomaly_rate) * 25)

        # 2. Redistribution timing (0–20): heuristic — trusted PROs score higher
        trusted_payers = {"ASCAP", "BMI", "PRS", "GEMA", "SACEM"}
        redistribution_timing = 18 if payer.upper() in trusted_payers else 12

        # 3. Rate drift (0–20): no contract extractor wired yet — neutral default
        rate_drift = 14

        # 4. Dispute resolution (0–20): closed claims ratio
        closed_claims = [c for c in claims if str(c.status) in {"CLOSED", "SETTLED"}]
        total_claims = len(claims) or 1
        resolution_rate = len(closed_claims) / total_claims
        dispute_resolution = round(resolution_rate * 20)

        # 5. Data quality (0–15): payments with complete data
        complete_payments = sum(
            1 for p in payments
            if getattr(p, "amount", None) is not None and (getattr(p, "received_at", None) is not None or getattr(p, "period_start", None) is not None)
        )
        data_quality = round((complete_payments / payer_payment_count) * 15)

        composite = payment_accuracy + redistribution_timing + rate_drift + dispute_resolution + data_quality
        composite = max(0, min(100, composite))
        tier = _risk_tier(composite)

        payment_volume = sum(float(p.amount or 0.0) for p in payments)

        risk_summary = _generate_payer_summary(payer, composite, tier, len(open_anomalies))

        return {
            "payer_id": payer.lower().replace(" ", "_"),
            "payer_name": payer,
            "composite_score": composite,
            "risk_tier": tier,
            "sub_scores": {
                "payment_accuracy": payment_accuracy,
                "redistribution_timing": redistribution_timing,
                "rate_drift": rate_drift,
                "dispute_resolution": dispute_resolution,
                "data_quality": data_quality,
            },
            "payment_volume": round(payment_volume, 2),
            "open_anomaly_count": len(open_anomalies),
            "risk_summary": risk_summary,
        }


def _generate_payer_summary(payer: str, score: int, tier: str, open_anomalies: int) -> str:
    if tier in {"HIGH_RISK", "ELEVATED_RISK"}:
        return (
            f"{payer} has a Payer Health Score of {score}/100 ({tier}). "
            f"There are {open_anomalies} unresolved anomalies linked to this payer. "
            "Extra scrutiny is recommended — consider escalating open claims."
        )
    if tier == "WATCH":
        return (
            f"{payer} scores {score}/100 ({tier}). "
            "Performance is adequate but some irregularities have been observed. "
            "Monitor closely for rate drift and payment timing."
        )
    return (
        f"{payer} scores {score}/100 ({tier}). "
        "Payment history with this payer is reliable based on your earnings data."
    )


def global_aggregate_scores(db: Session, limit: int = 20) -> dict[str, Any]:
    """Anonymised, privacy-preserving platform-wide aggregate."""
    # In production this would query a pre-aggregated table.
    # Here we return a structural placeholder.
    return {
        "note": "Platform-wide aggregate scores are anonymised and computed from all opted-in artists.",
        "data": [],
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Celery task entry point
# ---------------------------------------------------------------------------

def refresh_scores(artist_id: str) -> dict[str, Any]:
    """Callable by Celery: xr7.modules.payer_health.refresh_scores"""
    db = SessionLocal()
    try:
        scorer = PayerHealthScorer(db)
        return scorer.score_all(artist_id)
    finally:
        db.close()
