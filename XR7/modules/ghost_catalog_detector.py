"""
XR7 Engine 2 — Ghost Catalog Detector
======================================
Identifies works in the artist's catalog that are registered with PROs and
present on DSPs but have returned $0 for one or more periods where activity
data suggests revenue should have been generated.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalyStatus, AnomalySeverity
from XR7.models.base import SessionLocal
from XR7.models.payment import Payment
from XR7.models.work import Work
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from xr7_common.logging import get_logger

logger = get_logger(__name__)

GHOST_ZERO_INCOME_WINDOW_DAYS = 60
GHOST_WORK_ANOMALY_SUBTYPE = "GHOST_WORK_ZERO_INCOME"
AUTO_ESCALATE_THRESHOLD = 0.85


def _compute_hash(artist_id: str, payload: dict) -> str:
    raw = json.dumps({"artist_id": artist_id, "payload": payload}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def _ensure_utc(dt: datetime | None) -> datetime:
    now = datetime.now(timezone.utc)
    if dt is None:
        return now
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


SUSPECTED_CAUSES = [
    "metadata_mismatch",
    "registration_gap",
    "routing_failure",
    "dsp_attribution_error",
    "unknown",
]


def _infer_cause(work: Work, payments_for_work: list[Payment]) -> str:
    if not work.isrc and not work.iswc:
        return "registration_gap"
    if work.isrc and not work.iswc:
        return "metadata_mismatch"
    if payments_for_work:
        return "routing_failure"
    return "unknown"


def _ghost_score(work: Work, zero_days: int, has_activity_signal: bool) -> float:
    """Score 0.0–1.0. Higher = more confident this is a genuine ghost work."""
    score = 0.0
    if has_activity_signal:
        score += 0.40
    if zero_days >= GHOST_ZERO_INCOME_WINDOW_DAYS * 3:
        score += 0.30
    elif zero_days >= GHOST_ZERO_INCOME_WINDOW_DAYS:
        score += 0.20
    if not work.isrc:
        score += 0.15
    if not work.iswc:
        score += 0.10
    return min(round(score, 3), 1.0)


def _estimate_missing_value(work: Work, peer_avg_monthly: float, zero_months: int) -> float:
    """Estimate missing value using peer catalog averages."""
    return round(peer_avg_monthly * zero_months, 2)


class GhostCatalogDetector:
    """Detect catalog ghost works for a given artist."""

    # Configurable peer benchmark (used when no rate benchmarker is available)
    _PEER_AVG_MONTHLY_USD = 35.0

    def __init__(self, db: Session):
        self.db = db

    def scan(self, artist_id: str) -> dict[str, Any]:
        works = self.db.query(Work).filter(Work.artist_id == artist_id).all()
        payments = self.db.query(Payment).filter(Payment.artist_id == artist_id).all()
        anomalies_existing = (
            self.db.query(Anomaly)
            .filter(
                Anomaly.artist_id == artist_id,
                Anomaly.status != AnomalyStatus.CLOSED,
            )
            .all()
        )

        # Build set of work_ids already being tracked as underpayment anomalies
        underpayment_work_ids: set[str] = {
            str(a.description or "").split("work_id=")[-1].split()[0]
            for a in anomalies_existing
            if "work_id=" in (a.description or "")
        }

        # Build payment timeline per work
        payments_by_work: dict[str, list[Payment]] = {}
        for p in payments:
            wid = getattr(p, "work_id", None) or ""
            payments_by_work.setdefault(wid, []).append(p)

        now = datetime.now(timezone.utc)
        ghost_works: list[dict[str, Any]] = []
        new_anomalies_created: list[str] = []

        for work in works:
            work_payments = payments_by_work.get(str(work.id), [])

            # Determine last payment date (or use a far-past sentinel)
            if work_payments:
                last_pay_dt = max(
                    _ensure_utc(getattr(p, "received_at", None) or getattr(p, "period_start", None)) for p in work_payments
                )
                zero_days = (now - last_pay_dt).days
            else:
                zero_days = GHOST_ZERO_INCOME_WINDOW_DAYS + 1  # no payment ever
                last_pay_dt = None

            if zero_days < GHOST_ZERO_INCOME_WINDOW_DAYS:
                continue  # Work is paying — not a ghost

            # Activity signal: we treat having an ISRC as a proxy for confirmed streaming presence
            has_activity_signal = bool(work.isrc)

            # Skip works that have no activity signal AND no registration
            if not has_activity_signal and not work.iswc:
                continue

            score = _ghost_score(work, zero_days, has_activity_signal)
            zero_months = max(1, zero_days // 30)
            missing_value = _estimate_missing_value(
                work, self._PEER_AVG_MONTHLY_USD, zero_months
            )
            cause = _infer_cause(work, work_payments)
            ghost_start = (
                last_pay_dt.isoformat()
                if last_pay_dt
                else (now - timedelta(days=zero_days)).isoformat()
            )

            ghost_entry: dict[str, Any] = {
                "work_id": str(work.id),
                "title": work.title,
                "isrc": work.isrc,
                "iswc": work.iswc,
                "ghost_score": score,
                "estimated_missing_value": missing_value,
                "ghost_start_date": ghost_start,
                "zero_income_days": zero_days,
                "suspected_cause": cause,
                "recommended_action": _recommended_action(cause),
                "auto_escalate": score >= AUTO_ESCALATE_THRESHOLD,
            }
            ghost_works.append(ghost_entry)

            # Feed into anomaly pipeline as GHOST_WORK_ZERO_INCOME
            if str(work.id) not in underpayment_work_ids:
                try:
                    new_anomaly = Anomaly(
                        id=str(uuid.uuid4()),
                        artist_id=artist_id,
                        category=AnomalyCategory.ROYALTY,
                        subtype=GHOST_WORK_ANOMALY_SUBTYPE,
                        severity=(
                            AnomalySeverity.CRITICAL
                            if score >= AUTO_ESCALATE_THRESHOLD
                            else AnomalySeverity.HIGH
                        ),
                        estimated_recoverable=missing_value,
                        confidence_score=score,
                        status=AnomalyStatus.OPEN,
                        description=(
                            f"Ghost work detected: {work.title} (work_id={work.id}). "
                            f"Zero income for {zero_days} days. Cause: {cause}."
                        ),
                    )
                    self.db.add(new_anomaly)
                    new_anomalies_created.append(new_anomaly.id)
                except Exception:  # noqa: BLE001
                    logger.warning("Could not persist ghost anomaly for work %s", work.id)

        try:
            self.db.commit()
        except Exception:  # noqa: BLE001
            self.db.rollback()

        # Sort by estimated_missing_value descending
        ghost_works.sort(key=lambda g: g["estimated_missing_value"], reverse=True)

        payload_for_hash = {
            "artist_id": artist_id,
            "ghost_count": len(ghost_works),
            "total_missing_value": sum(g["estimated_missing_value"] for g in ghost_works),
        }
        chain_hash = _compute_hash(artist_id, payload_for_hash)
        try:
            ImmutableLedgerService(self.db).append(
                artist_id, "ghost_catalog_scan", {**payload_for_hash, "chain_hash": chain_hash}
            )
        except Exception:  # noqa: BLE001
            logger.warning("Failed to append ledger entry for ghost_catalog_scan")

        return {
            "artist_id": artist_id,
            "ghost_works": ghost_works,
            "ghost_count": len(ghost_works),
            "total_estimated_missing_value": round(
                sum(g["estimated_missing_value"] for g in ghost_works), 2
            ),
            "new_anomalies_created": new_anomalies_created,
            "chain_of_custody_hash": chain_hash,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
        }


def _recommended_action(cause: str) -> str:
    mapping = {
        "metadata_mismatch": "Update ISRC/ISWC identifiers and resubmit to your PRO and distributor.",
        "registration_gap": "Register this work immediately with your PRO and all relevant societies.",
        "routing_failure": "Contact your distributor to investigate royalty routing for this work.",
        "dsp_attribution_error": "File a dispute with the relevant DSP(s) citing streaming data.",
        "unknown": "Contact your PRO and distributor with streaming evidence to investigate.",
    }
    return mapping.get(cause, "Investigate with your PRO and distributor.")


# ---------------------------------------------------------------------------
# Celery task entry point
# ---------------------------------------------------------------------------

def run_scan(artist_id: str) -> dict[str, Any]:
    """Callable by Celery: xr7.modules.ghost_catalog.run_scan"""
    db = SessionLocal()
    try:
        detector = GhostCatalogDetector(db)
        return detector.scan(artist_id)
    finally:
        db.close()
