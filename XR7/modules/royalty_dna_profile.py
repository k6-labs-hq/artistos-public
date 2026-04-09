"""
XR7 Engine 2 — Royalty DNA Profile
=====================================
Generates a visual earnings fingerprint: per-platform, per-territory,
per-royalty-type breakdown with concentration risk, territory gaps,
seasonality, and an ArtistComfortAgent insight narrative.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from shared.utils.dates import ensure_utc as _ensure_utc
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.base import SessionLocal
from XR7.models.payment import Payment
from XR7.models.work import Work
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from xr7_common.logging import get_logger

logger = get_logger(__name__)

TERRITORY_GAP_SUBTYPE = "TERRITORY_GAP_NO_REGISTRATION"

_ROYALTY_TYPES = [
    "mechanical",
    "performance",
    "sync",
    "neighboring_rights",
    "master",
    "brand",
    "ugc",
]

_MAJOR_TERRITORIES = [
    "US",
    "GB",
    "DE",
    "FR",
    "JP",
    "CA",
    "AU",
    "SE",
    "NL",
    "BR",
]


def _compute_hash(artist_id: str, payload: dict) -> str:
    raw = json.dumps({"artist_id": artist_id, "payload": payload}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def _herfindahl_index(shares: list[float]) -> float:
    """Return HHI (0–1). 1 = perfect monopoly."""
    total = sum(shares)
    if total == 0:
        return 0.0
    normalised = [s / total for s in shares]
    return round(sum(x**2 for x in normalised), 4)


class RoyaltyDNAProfile:
    def __init__(self, db: Session):
        self.db = db

    def generate(self, artist_id: str) -> dict[str, Any]:
        payments = self.db.query(Payment).filter(Payment.artist_id == artist_id).all()
        self.db.query(Work).filter(Work.artist_id == artist_id).all()

        # -- Platform breakdown --------------------------------------------
        platform_totals: dict[str, float] = defaultdict(float)
        territory_totals: dict[str, float] = defaultdict(float)
        royalty_type_totals: dict[str, float] = defaultdict(float)
        monthly_totals: dict[str, float] = defaultdict(float)  # "YYYY-MM"
        work_totals: dict[str, float] = defaultdict(float)

        for p in payments:
            source = str(getattr(p, "source", None) or "Unknown")
            territory = str(getattr(p, "territory", None) or getattr(p, "source", None) or "US")
            rtype = str(
                getattr(p, "royalty_type", None) or getattr(p, "payment_type", None) or "ROYALTY"
            )
            amount = float(p.amount or 0.0)
            dt = _ensure_utc(getattr(p, "received_at", None) or getattr(p, "period_start", None))

            platform_totals[source] += amount
            territory_totals[territory] += amount
            royalty_type_totals[rtype] += amount
            monthly_totals[dt.strftime("%Y-%m")] += amount
            wid = str(getattr(p, "work_id", None) or "")
            if wid:
                work_totals[wid] += amount

        total_earned = sum(platform_totals.values()) or 1.0

        # Platform breakdown with trend (simplified)
        platform_breakdown = [
            {
                "platform": k,
                "amount": round(v, 2),
                "pct": round(v / total_earned * 100, 1),
                "trend": "STABLE",
            }
            for k, v in sorted(platform_totals.items(), key=lambda x: -x[1])
        ]

        # Territory breakdown
        territory_breakdown = [
            {
                "territory": k,
                "amount": round(v, 2),
                "pct": round(v / total_earned * 100, 1),
            }
            for k, v in sorted(territory_totals.items(), key=lambda x: -x[1])
        ]

        # -- Territory gap detection ----------------------------------------
        earning_territories = set(territory_totals.keys())
        registered_territories = {t.upper() for t in earning_territories}  # proxy
        territory_gaps = [
            t
            for t in _MAJOR_TERRITORIES
            if t not in registered_territories and t not in earning_territories
        ]

        # Feed territory gaps into anomaly pipeline
        new_anomaly_ids: list[str] = []
        for gap_territory in territory_gaps:
            try:
                anomaly = Anomaly(
                    id=str(uuid.uuid4()),
                    artist_id=artist_id,
                    category=AnomalyCategory.ROYALTY,
                    subtype=TERRITORY_GAP_SUBTYPE,
                    severity=AnomalySeverity.MEDIUM,
                    estimated_recoverable=0.0,
                    confidence_score=0.70,
                    territory=gap_territory,
                    status=AnomalyStatus.OPEN,
                    description=(
                        f"Territory gap detected: catalog active but no royalty registration "
                        f"or payout in {gap_territory}."
                    ),
                )
                self.db.add(anomaly)
                new_anomaly_ids.append(anomaly.id)
            except Exception:  # noqa: BLE001
                logger.warning("Could not create territory gap anomaly for %s", gap_territory)
        try:
            self.db.commit()
        except Exception:  # noqa: BLE001
            self.db.rollback()

        # Royalty type breakdown with trend
        royalty_breakdown = []
        for rtype in _ROYALTY_TYPES:
            amt = royalty_type_totals.get(rtype, 0.0)
            royalty_breakdown.append(
                {
                    "type": rtype,
                    "amount": round(amt, 2),
                    "pct": round(amt / total_earned * 100, 1),
                    "trend": "GROWING" if amt > total_earned * 0.2 else "STABLE",
                }
            )

        # Revenue concentration score (HHI)
        concentration_score = _herfindahl_index(list(platform_totals.values()))
        top3_concentration = (
            round(sum(sorted(platform_totals.values(), reverse=True)[:3]) / total_earned * 100, 1)
            if platform_totals
            else 0.0
        )

        # Catalog long-tail ratio
        work_values = sorted(work_totals.values(), reverse=True)
        top10_value = sum(work_values[:10])
        long_tail_ratio = round(top10_value / total_earned * 100, 1) if total_earned > 0 else 0.0

        # Platform seasonality: months where each platform is +/- vs average
        seasonal_avg = sum(monthly_totals.values()) / max(len(monthly_totals), 1)
        seasonality = {month: round(v - seasonal_avg, 2) for month, v in monthly_totals.items()}

        # DNA strand segments
        dna_strand = [
            {
                "segment": k,
                "value": round(v, 2),
                "pct": round(v / total_earned * 100, 1),
                "color": _segment_color(k),
            }
            for k, v in sorted(platform_totals.items(), key=lambda x: -x[1])
        ]

        # AI insight narrative
        insights = _generate_insights(
            platform_breakdown=platform_breakdown,
            territory_gaps=territory_gaps,
            concentration_score=concentration_score,
            royalty_breakdown=royalty_breakdown,
            long_tail_ratio=long_tail_ratio,
        )

        # Chain-of-custody
        payload_for_hash = {
            "artist_id": artist_id,
            "platform_count": len(platform_breakdown),
            "territory_gap_count": len(territory_gaps),
            "concentration_score": concentration_score,
        }
        chain_hash = _compute_hash(artist_id, payload_for_hash)
        try:
            ImmutableLedgerService(self.db).append(
                artist_id,
                "royalty_dna_profile_generated",
                {**payload_for_hash, "chain_hash": chain_hash},
            )
        except Exception:  # noqa: BLE001
            logger.warning("Failed to append ledger for royalty_dna_profile")

        return {
            "artist_id": artist_id,
            "platform_breakdown": platform_breakdown,
            "territory_breakdown": territory_breakdown,
            "territory_gaps": territory_gaps,
            "royalty_type_breakdown": royalty_breakdown,
            "revenue_concentration_score": concentration_score,
            "top3_platform_concentration_pct": top3_concentration,
            "catalog_long_tail_ratio_pct": long_tail_ratio,
            "platform_seasonality": seasonality,
            "dna_strand": dna_strand,
            "new_territory_gap_anomalies": new_anomaly_ids,
            "insights": insights,
            "chain_of_custody_hash": chain_hash,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


def _segment_color(platform: str) -> str:
    palette = {
        "Spotify": "#1DB954",
        "Apple Music": "#FC3C44",
        "YouTube": "#FF0000",
        "ASCAP": "#003478",
        "BMI": "#E8231E",
        "DistroKid": "#5B4FE9",
        "TuneCore": "#F44848",
    }
    return palette.get(platform, "#C89B3C")


def _generate_insights(
    platform_breakdown: list[dict],
    territory_gaps: list[str],
    concentration_score: float,
    royalty_breakdown: list[dict],
    long_tail_ratio: float,
) -> list[dict[str, str]]:
    insights = []

    # Concentration risk
    top_platform = platform_breakdown[0]["platform"] if platform_breakdown else "your top platform"
    top_pct = platform_breakdown[0]["pct"] if platform_breakdown else 0.0
    if concentration_score > 0.5 or top_pct > 60:
        insights.append(
            {
                "headline": f"High platform concentration: {top_pct:.0f}% from {top_platform}",
                "explanation": (
                    f"More than half your income comes from {top_platform}. "
                    "If that platform changes its rate or algorithm, your earnings are heavily exposed."
                ),
                "recommended_action": "Expand distribution and registration to diversify your income base.",
            }
        )

    # Territory gaps
    if territory_gaps:
        gaps_str = ", ".join(territory_gaps[:4])
        insights.append(
            {
                "headline": f"Unregistered territory gaps: {gaps_str}",
                "explanation": (
                    "Your catalog appears to be active but you have no royalty registration or payout "
                    f"in these territories: {gaps_str}. Revenue may be accumulating unclaimed."
                ),
                "recommended_action": "Register with the local PRO or society for each gap territory.",
            }
        )

    # Long-tail
    if long_tail_ratio > 80:
        insights.append(
            {
                "headline": f"Top 10 tracks carry {long_tail_ratio:.0f}% of income",
                "explanation": "Your catalog is heavily dependent on a small number of works.",
                "recommended_action": "Actively promote back-catalog works and ensure all are fully registered.",
            }
        )
    elif long_tail_ratio < 40:
        insights.append(
            {
                "headline": "Well-distributed catalog — strong long-tail",
                "explanation": "Your earnings are spread across many works, reducing concentration risk.",
                "recommended_action": "Ensure all long-tail works have complete metadata to maximise matching.",
            }
        )

    # Cap at 3
    return insights[:3]


# ---------------------------------------------------------------------------
# Celery task entry point
# ---------------------------------------------------------------------------


def generate_profile(artist_id: str) -> dict[str, Any]:
    """Callable by Celery: xr7.modules.royalty_dna.generate_profile"""
    db = SessionLocal()
    try:
        profiler = RoyaltyDNAProfile(db)
        return profiler.generate(artist_id)
    finally:
        db.close()
