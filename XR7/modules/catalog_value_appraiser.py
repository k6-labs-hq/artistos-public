"""
XR7 Engine 2 — Catalog Value Appraiser
=========================================
Estimates the fair market value of the artist's catalog using an NPS
multiple-based approach with catalog-specific quality adjustments.

Explicit disclaimer: this is an algorithmic estimate for informational
purposes only and is NOT a certified appraisal for transactional, legal,
or tax purposes.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly, AnomalyStatus
from XR7.models.base import SessionLocal
from XR7.models.payment import Payment
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from xr7_common.logging import get_logger

logger = get_logger(__name__)

VALUATION_DISCLAIMER = (
    "This is an algorithmic estimate for informational purposes only. "
    "It is not a certified appraisal and should not be used for transactional, "
    "legal, or tax purposes without independent professional advice."
)

# Industry multiple ranges (configurable)
_ACTIVE_MULTIPLE_LOW = 15.0
_ACTIVE_MULTIPLE_HIGH = 25.0
_DECLINING_MULTIPLE_LOW = 8.0
_DECLINING_MULTIPLE_HIGH = 15.0


def _compute_hash(artist_id: str, payload: dict) -> str:
    raw = json.dumps({"artist_id": artist_id, "payload": payload}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


class CatalogValueAppraiser:
    def __init__(self, db: Session):
        self.db = db

    def appraise(
        self,
        artist_id: str,
        catalog_health_score: float = 0.75,
        concentration_score: float = 0.3,
        territory_coverage_ratio: float = 0.7,
        trajectory: str = "STABLE",
    ) -> dict[str, Any]:
        # -- Trailing 12-month net earnings -----------------------------------
        now = datetime.now(timezone.utc)
        twelve_months_ago = now - timedelta(days=365)
        payments = (
            self.db.query(Payment)
            .filter(
                Payment.artist_id == artist_id,
                Payment.received_at >= twelve_months_ago,
            )
            .all()
        )
        trailing_nps = sum(float(p.amount or 0.0) for p in payments)

        # -- Recovery upside from open anomalies ------------------------------
        open_anomalies = (
            self.db.query(Anomaly)
            .filter(
                Anomaly.artist_id == artist_id,
                Anomaly.status != AnomalyStatus.CLOSED,
            )
            .all()
        )
        total_recoverable = sum(float(a.estimated_recoverable or 0.0) for a in open_anomalies)

        # -- Base multiple selection -------------------------------------------
        if trajectory in {"GROWING", "STABLE"}:
            base_low = _ACTIVE_MULTIPLE_LOW
            base_high = _ACTIVE_MULTIPLE_HIGH
        else:
            base_low = _DECLINING_MULTIPLE_LOW
            base_high = _DECLINING_MULTIPLE_HIGH
        base_expected = (base_low + base_high) / 2.0

        # -- Adjustment factors ------------------------------------------------
        # Catalog health premium: +0% to +20% of base
        catalog_health_premium = (catalog_health_score - 0.5) * 0.4  # -0.2 to +0.2

        # Recovery upside: adds recoverable pipeline to NPS base
        recovery_upside_multiplier = (total_recoverable / max(trailing_nps, 1.0)) * 0.5

        # Territory coverage: 0 to +15%
        territory_factor = (territory_coverage_ratio - 0.5) * 0.3

        # Concentration discount: high HHI = negative adjustment
        concentration_discount = -(concentration_score - 0.2) * 0.3

        # Age & trajectory
        trajectory_factor = {"GROWING": 0.10, "STABLE": 0.0, "DECLINING": -0.15}.get(
            trajectory, 0.0
        )

        # Aggregate multiplier adjustment
        total_adj = (
            catalog_health_premium
            + recovery_upside_multiplier
            + territory_factor
            + concentration_discount
            + trajectory_factor
        )
        total_adj = max(-0.40, min(0.50, total_adj))  # cap at ±40%

        # Final multiples
        multiple_low = round(base_low * (1 + total_adj * 0.8), 1)
        multiple_expected = round(base_expected * (1 + total_adj), 1)
        multiple_high = round(base_high * (1 + total_adj * 1.2), 1)

        # Valuations
        valuation_low = round(trailing_nps * multiple_low, 2)
        valuation_expected = round(trailing_nps * multiple_expected, 2)
        valuation_high = round(trailing_nps * multiple_high, 2)
        recovery_upside_value = round(total_recoverable * multiple_expected, 2)

        # Key drivers / risks
        drivers, risks = _compute_drivers_risks(
            catalog_health_score=catalog_health_score,
            concentration_score=concentration_score,
            territory_coverage_ratio=territory_coverage_ratio,
            trajectory=trajectory,
            total_recoverable=total_recoverable,
            trailing_nps=trailing_nps,
        )

        # Narrative
        narrative = _generate_narrative(
            artist_id=artist_id,
            trailing_nps=trailing_nps,
            valuation_expected=valuation_expected,
            valuation_low=valuation_low,
            valuation_high=valuation_high,
            recovery_upside_value=recovery_upside_value,
            trajectory=trajectory,
        )

        # Waterfall chart data
        waterfall = _build_waterfall(
            base_low=base_low,
            base_high=base_high,
            trailing_nps=trailing_nps,
            catalog_health_premium=catalog_health_premium,
            recovery_upside_multiplier=recovery_upside_multiplier,
            territory_factor=territory_factor,
            concentration_discount=concentration_discount,
            trajectory_factor=trajectory_factor,
            valuation_expected=valuation_expected,
        )

        # Chain-of-custody
        payload_for_hash = {
            "artist_id": artist_id,
            "trailing_nps": trailing_nps,
            "valuation_expected": valuation_expected,
            "multiple_expected": multiple_expected,
        }
        chain_hash = _compute_hash(artist_id, payload_for_hash)
        try:
            ImmutableLedgerService(self.db).append(
                artist_id, "catalog_value_appraisal", {**payload_for_hash, "chain_hash": chain_hash}
            )
        except Exception:  # noqa: BLE001
            logger.warning("Failed to append ledger for catalog_value_appraisal")

        return {
            "artist_id": artist_id,
            "trailing_12m_nps": round(trailing_nps, 2),
            "valuation_low": valuation_low,
            "valuation_expected": valuation_expected,
            "valuation_high": valuation_high,
            "multiple_applied_low": multiple_low,
            "multiple_applied_expected": multiple_expected,
            "multiple_applied_high": multiple_high,
            "recovery_upside_value": recovery_upside_value,
            "adjustment_factors": {
                "catalog_health_premium": round(catalog_health_premium, 4),
                "recovery_upside_multiplier": round(recovery_upside_multiplier, 4),
                "territory_coverage_factor": round(territory_factor, 4),
                "concentration_discount": round(concentration_discount, 4),
                "trajectory_factor": territory_factor,
            },
            "key_value_drivers": drivers,
            "key_value_risks": risks,
            "waterfall": waterfall,
            "narrative": narrative,
            "disclaimer": VALUATION_DISCLAIMER,
            "chain_of_custody_hash": chain_hash,
            "appraised_at": now.isoformat(),
        }


def _compute_drivers_risks(
    catalog_health_score: float,
    concentration_score: float,
    territory_coverage_ratio: float,
    trajectory: str,
    total_recoverable: float,
    trailing_nps: float,
) -> tuple[list[str], list[str]]:
    drivers: list[str] = []
    risks: list[str] = []

    if catalog_health_score > 0.75:
        drivers.append(
            f"High catalog health score ({catalog_health_score:.0%}) improves metadata matching and royalty capture."
        )
    if total_recoverable > 0:
        drivers.append(
            f"Recovery pipeline of ${total_recoverable:,.0f} represents upside not yet in trailing earnings."
        )
    if territory_coverage_ratio > 0.7:
        drivers.append(
            f"Strong territory coverage ({territory_coverage_ratio:.0%}) across major royalty markets."
        )
    if trajectory == "GROWING":
        drivers.append("Catalog is on a GROWING trajectory, supporting a higher earnings multiple.")

    if concentration_score > 0.5:
        risks.append(
            "High platform concentration — significant exposure if top platform changes rates."
        )
    if catalog_health_score < 0.5:
        risks.append(
            "Below-average catalog health reduces identifier matching and royalty capture."
        )
    if territory_coverage_ratio < 0.5:
        risks.append(
            "Limited territory coverage — significant royalty streams may be unregistered."
        )
    if trajectory == "DECLINING":
        risks.append("Declining catalog trajectory reduces the applicable earnings multiple.")
    if trailing_nps < 1000:
        risks.append(
            "Low trailing earnings base — valuation may shift significantly with small income changes."
        )

    return drivers[:3], risks[:3]


def _build_waterfall(
    base_low: float,
    base_high: float,
    trailing_nps: float,
    catalog_health_premium: float,
    recovery_upside_multiplier: float,
    territory_factor: float,
    concentration_discount: float,
    trajectory_factor: float,
    valuation_expected: float,
) -> list[dict[str, Any]]:
    base_val = trailing_nps * ((base_low + base_high) / 2.0)
    return [
        {"label": "Base NPS Multiple", "value": round(base_val, 2), "type": "base"},
        {
            "label": "Catalog Health Premium",
            "value": round(trailing_nps * catalog_health_premium, 2),
            "type": ("up" if catalog_health_premium >= 0 else "down"),
        },
        {
            "label": "Recovery Upside",
            "value": round(trailing_nps * recovery_upside_multiplier, 2),
            "type": "up",
        },
        {
            "label": "Territory Coverage",
            "value": round(trailing_nps * territory_factor, 2),
            "type": ("up" if territory_factor >= 0 else "down"),
        },
        {
            "label": "Concentration Discount",
            "value": round(trailing_nps * concentration_discount, 2),
            "type": ("up" if concentration_discount >= 0 else "down"),
        },
        {
            "label": "Trajectory Adjustment",
            "value": round(trailing_nps * trajectory_factor, 2),
            "type": ("up" if trajectory_factor >= 0 else "down"),
        },
        {"label": "Final Estimated Value", "value": valuation_expected, "type": "total"},
    ]


def _generate_narrative(
    artist_id: str,
    trailing_nps: float,
    valuation_expected: float,
    valuation_low: float,
    valuation_high: float,
    recovery_upside_value: float,
    trajectory: str,
) -> str:
    return (
        f"Based on ${trailing_nps:,.2f} in trailing 12-month net earnings and your catalog's "
        f"{trajectory.lower()} trajectory, XR7 estimates your catalog value in the range of "
        f"${valuation_low:,.0f}–${valuation_high:,.0f}, with an expected value of ${valuation_expected:,.0f}. "
        f"Your open recovery pipeline adds an estimated ${recovery_upside_value:,.0f} in potential upside "
        "if successfully recovered. " + VALUATION_DISCLAIMER
    )


# ---------------------------------------------------------------------------
# Celery task entry point
# ---------------------------------------------------------------------------


def run_appraisal(artist_id: str) -> dict[str, Any]:
    """Callable by Celery: xr7.modules.catalog_value.run_appraisal"""
    db = SessionLocal()
    try:
        appraiser = CatalogValueAppraiser(db)
        return appraiser.appraise(artist_id)
    finally:
        db.close()
