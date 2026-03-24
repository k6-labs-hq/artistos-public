"""
XR7 Engine 2 — Black Box Countdown
=====================================
Tracks society-specific redistribution deadlines for every open anomaly.
Distinct from the SOL tracker: this is about the point at which unmatched
royalties are redistributed to other rights holders and become unrecoverable.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly, AnomalyStatus
from XR7.models.base import SessionLocal
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Redistribution rules per society / payer type
# Default window is the *minimum* redistribution window (conservative).
# ---------------------------------------------------------------------------
_REDISTRIBUTION_RULES: dict[str, int] = {
    # Society: days until redistribution
    "ASCAP": 730,          # 2 years
    "BMI": 730,
    "MLC": 1095,           # 3 years (digital mechanicals)
    "JASRAC": 548,         # ~18 months conservatively
    "PRS": 1095,
    "GEMA": 1095,
    "SACEM": 1095,
    "SOCAN": 1095,
    "APRA": 730,
    "SAG_AFTRA": 730,
    "WGA": 730,
    "DGA": 730,
    "FOREIGN_RESIDUAL": 548,  # 18 months conservative
    "DEFAULT": 730,
}

GREEN_DAYS = 180
AMBER_DAYS = 30
RED_DAYS = 7


def _urgency_tier(days: int, is_expired: bool) -> str:
    if is_expired:
        return "EXPIRED"
    if days <= RED_DAYS:
        return "CRITICAL"
    if days <= AMBER_DAYS:
        return "RED"
    if days <= GREEN_DAYS:
        return "AMBER"
    return "GREEN"


def _compute_hash(artist_id: str, payload: dict) -> str:
    raw = json.dumps({"artist_id": artist_id, "payload": payload}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def _ensure_utc(dt: datetime | None) -> datetime:
    now = datetime.now(timezone.utc)
    if dt is None:
        return now
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _society_from_anomaly(anomaly: Anomaly) -> str:
    """Infer society from anomaly territory/description or default."""
    description = (anomaly.description or "").upper()
    territory = (anomaly.territory or "").upper()
    for key in _REDISTRIBUTION_RULES:
        if key in description or key in territory:
            return key
    if territory in {"JP", "JAPAN"}:
        return "JASRAC"
    if territory in {"GB", "UK"}:
        return "PRS"
    if territory in {"DE", "GERMANY"}:
        return "GEMA"
    if territory in {"FR", "FRANCE"}:
        return "SACEM"
    if territory in {"CA", "CANADA"}:
        return "SOCAN"
    if territory in {"AU", "AUSTRALIA"}:
        return "APRA"
    return "DEFAULT"


# ---------------------------------------------------------------------------
# Freeze events store (in-memory; persisted via ledger in production)
# ---------------------------------------------------------------------------
_freeze_registry: dict[str, datetime] = {}  # society -> freeze_until


def apply_freeze(society: str, freeze_until: datetime) -> None:
    _freeze_registry[society.upper()] = freeze_until


def is_frozen(society: str, as_of: datetime) -> bool:
    until = _freeze_registry.get(society.upper())
    return until is not None and as_of < until


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class BlackBoxCountdown:
    def __init__(self, db: Session):
        self.db = db

    def compute_all(self, artist_id: str) -> dict[str, Any]:
        anomalies = (
            self.db.query(Anomaly)
            .filter(
                Anomaly.artist_id == artist_id,
                Anomaly.status != AnomalyStatus.CLOSED,
            )
            .all()
        )

        now = datetime.now(timezone.utc)
        results: list[dict[str, Any]] = []

        for anomaly in anomalies:
            entry = self._compute_single(anomaly, now)
            results.append(entry)

        # Sort: CRITICAL first, then RED, then AMBER, then GREEN, then EXPIRED
        tier_order = {"CRITICAL": 0, "RED": 1, "AMBER": 2, "GREEN": 3, "EXPIRED": 4}
        results.sort(key=lambda r: tier_order.get(r["urgency_tier"], 5))

        at_risk_30 = sum(
            r["estimated_at_risk_value"]
            for r in results
            if r["urgency_tier"] in {"CRITICAL", "RED"} and not r["is_expired"]
        )
        critical_count = sum(1 for r in results if r["urgency_tier"] == "CRITICAL")

        payload_for_hash = {
            "artist_id": artist_id,
            "anomaly_count": len(results),
            "critical_count": critical_count,
        }
        chain_hash = _compute_hash(artist_id, payload_for_hash)
        try:
            ImmutableLedgerService(self.db).append(
                artist_id, "black_box_countdown_refresh", {**payload_for_hash, "chain_hash": chain_hash}
            )
        except Exception:  # noqa: BLE001
            logger.warning("Failed to append ledger for black_box_countdown")

        return {
            "artist_id": artist_id,
            "countdowns": results,
            "critical_count": critical_count,
            "at_risk_value_next_30_days": round(at_risk_30, 2),
            "chain_of_custody_hash": chain_hash,
            "computed_at": now.isoformat(),
        }

    def compute_single(self, artist_id: str, anomaly_id: str) -> dict[str, Any] | None:
        anomaly = (
            self.db.query(Anomaly)
            .filter(Anomaly.id == anomaly_id, Anomaly.artist_id == artist_id)
            .first()
        )
        if not anomaly:
            return None
        return self._compute_single(anomaly, datetime.now(timezone.utc))

    def _compute_single(self, anomaly: Anomaly, now: datetime) -> dict[str, Any]:
        society = _society_from_anomaly(anomaly)
        window_days = _REDISTRIBUTION_RULES.get(society, _REDISTRIBUTION_RULES["DEFAULT"])
        created = _ensure_utc(anomaly.time_window_start or anomaly.created_at)
        deadline = created + timedelta(days=window_days)

        # Apply freeze if active
        frozen = is_frozen(society, now)
        if frozen:
            freeze_until = _freeze_registry.get(society.upper(), now)
            freeze_extension = max(0, (freeze_until - now).days)
            deadline = deadline + timedelta(days=freeze_extension)

        diff = deadline - now
        days_remaining = max(0, diff.days)
        hours_remaining = max(0, int(diff.total_seconds() / 3600))
        is_expired = now >= deadline

        urgency = _urgency_tier(days_remaining, is_expired)

        return {
            "anomaly_id": str(anomaly.id),
            "society": society,
            "redistribution_deadline": deadline.isoformat(),
            "days_remaining": days_remaining,
            "hours_remaining": hours_remaining,
            "urgency_tier": urgency,
            "is_expired": is_expired,
            "is_frozen": frozen,
            "estimated_at_risk_value": round(float(anomaly.estimated_recoverable or 0.0), 2),
            "payer": society,
            "description": anomaly.description,
            "category": str(anomaly.category),
            "severity": str(anomaly.severity),
        }


# ---------------------------------------------------------------------------
# Celery task entry point
# ---------------------------------------------------------------------------

def refresh_countdowns(artist_id: str) -> dict[str, Any]:
    """Callable by Celery: xr7.modules.black_box_countdown.refresh_countdowns"""
    db = SessionLocal()
    try:
        engine = BlackBoxCountdown(db)
        return engine.compute_all(artist_id)
    finally:
        db.close()
