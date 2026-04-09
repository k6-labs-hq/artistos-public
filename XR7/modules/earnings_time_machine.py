"""
XR7 Engine 2 — Earnings Time Machine
=====================================
Reconstructs what the artist would have earned if their catalog had been
clean from day one. The delta between that "clean world" number and actual
earnings received is their cumulative lifetime leakage, visualised as a
diverging timeline.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from shared.utils.dates import period_key as _period_key
from XR7.models.anomaly import Anomaly
from XR7.models.base import SessionLocal
from XR7.models.payment import Payment
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_METADATA_UPLIFT_RATE = 0.12   # 12% uplift for perfect metadata
_ANOMALY_RECOVERY_RATE = 0.80  # 80% of estimated_recoverable captured in clean world
_SPLIT_CORRECTION_RATE = 0.05  # 5% average uplift from corrected splits
_FOREIGN_SOCIETY_RATE = 0.08   # 8% uplift for full foreign society crosswalk
_DSP_ATTRIBUTION_RATE = 0.04   # 4% uplift for resolved DSP/PRO attribution errors


def _compute_hash(artist_id: str, payload: dict) -> str:
    raw = json.dumps({"artist_id": artist_id, "payload": payload}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()



def _ensure_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class EarningsTimeMachine:
    """Compute clean-world vs actual earnings per calendar period."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(
        self,
        artist_id: str,
        granularity: str = "year",
        metadata_repair_log: list[dict] | None = None,
        anomaly_history: list[dict] | None = None,
        split_verification_history: list[dict] | None = None,
        catalog_health_scores: list[dict] | None = None,
    ) -> dict[str, Any]:
        metadata_repair_log = metadata_repair_log or []
        anomaly_history = anomaly_history or []
        split_verification_history = split_verification_history or []
        catalog_health_scores = catalog_health_scores or []

        # -- Gather actual payments ----------------------------------------
        payments = (
            self.db.query(Payment)
            .filter(Payment.artist_id == artist_id)
            .all()
        )

        # -- Gather open / historical anomalies -----------------------------
        anomalies_db = (
            self.db.query(Anomaly)
            .filter(Anomaly.artist_id == artist_id)
            .all()
        )

        # -- Build period buckets -------------------------------------------
        actual_by_period: dict[str, float] = defaultdict(float)
        for p in payments:
            dt = _ensure_utc(getattr(p, "received_at", None) or getattr(p, "period_start", None)) or datetime.now(timezone.utc)
            key = _period_key(dt, granularity)
            actual_by_period[key] += float(p.amount or 0.0)

        # Include anomaly history external records
        for rec in anomaly_history:
            if rec.get("status") == "CLOSED":
                continue
            ts_str = rec.get("event_date") or rec.get("created_at")
            if not ts_str:
                continue
            try:
                dt = datetime.fromisoformat(str(ts_str)).replace(tzinfo=timezone.utc)
            except (ValueError, TypeError):
                continue
            key = _period_key(dt, granularity)
            # anomaly amounts are leakage, not actual earnings — excluded from actual

        # -- Compute clean-world uplift per period --------------------------
        metadata_uplift_total = sum(
            float(r.get("estimated_value_impact", 0.0)) for r in metadata_repair_log
        ) * _METADATA_UPLIFT_RATE if not metadata_repair_log else sum(
            float(r.get("value_delta", 0.0)) for r in metadata_repair_log if float(r.get("value_delta", 0.0)) > 0
        )

        anomaly_uplift_total = sum(
            float(a.estimated_recoverable or 0.0) for a in anomalies_db
        ) * _ANOMALY_RECOVERY_RATE
        for rec in anomaly_history:
            anomaly_uplift_total += float(rec.get("recoverable_estimate", 0.0)) * _ANOMALY_RECOVERY_RATE

        split_uplift = sum(
            float(r.get("split_delta", 0.0)) for r in split_verification_history if float(r.get("split_delta", 0.0)) > 0
        )

        total_actual = sum(actual_by_period.values())

        # Distribute uplifts proportionally across periods
        periods_sorted = sorted(actual_by_period.keys())
        n = max(len(periods_sorted), 1)
        per_period_metadata = metadata_uplift_total / n
        per_period_anomaly = anomaly_uplift_total / n
        per_period_split = split_uplift / n
        per_period_foreign = total_actual * _FOREIGN_SOCIETY_RATE / n
        per_period_dsp = total_actual * _DSP_ATTRIBUTION_RATE / n

        # If no payment data at all, synthesise one bucket for the current year
        if not periods_sorted:
            periods_sorted = [str(datetime.now(timezone.utc).year)]
            actual_by_period[periods_sorted[0]] = 0.0

        # -- Build time series ---------------------------------------------
        time_series: list[dict[str, Any]] = []
        cumulative_actual = 0.0
        cumulative_clean = 0.0
        cumulative_leakage = 0.0

        for period in periods_sorted:
            actual = actual_by_period.get(period, 0.0)
            clean_uplift = (
                per_period_metadata
                + per_period_anomaly
                + per_period_split
                + per_period_foreign
                + per_period_dsp
            )
            clean = actual + clean_uplift
            delta = clean - actual
            cumulative_actual += actual
            cumulative_clean += clean
            cumulative_leakage += delta
            time_series.append(
                {
                    "period": period,
                    "actual_earned": round(actual, 2),
                    "estimated_clean_world_earned": round(clean, 2),
                    "delta": round(delta, 2),
                    "cumulative_leakage_to_date": round(cumulative_leakage, 2),
                    "uplift_breakdown": {
                        "metadata_repair": round(per_period_metadata, 2),
                        "anomaly_underpayments": round(per_period_anomaly, 2),
                        "split_corrections": round(per_period_split, 2),
                        "foreign_society_gaps": round(per_period_foreign, 2),
                        "dsp_attribution_errors": round(per_period_dsp, 2),
                    },
                }
            )

        total_leakage_expected = round(cumulative_leakage, 2)
        total_leakage_low = round(total_leakage_expected * 0.65, 2)
        total_leakage_high = round(total_leakage_expected * 1.40, 2)

        # -- Chain-of-custody hash -----------------------------------------
        payload_for_hash = {
            "artist_id": artist_id,
            "granularity": granularity,
            "period_count": len(time_series),
            "total_leakage_expected": total_leakage_expected,
        }
        chain_hash = _compute_hash(artist_id, payload_for_hash)
        try:
            ImmutableLedgerService(self.db).append(
                artist_id,
                "earnings_time_machine_run",
                {**payload_for_hash, "chain_hash": chain_hash},
            )
        except Exception:  # noqa: BLE001
            logger.warning("Failed to append ledger entry for earnings_time_machine")

        # -- Plain-language summary ----------------------------------------
        summary = _generate_summary(
            artist_id=artist_id,
            total_actual=round(cumulative_actual, 2),
            total_clean=round(cumulative_clean, 2),
            total_leakage=total_leakage_expected,
            period_count=len(time_series),
            granularity=granularity,
        )

        return {
            "artist_id": artist_id,
            "granularity": granularity,
            "time_series": time_series,
            "total_actual_earned": round(cumulative_actual, 2),
            "total_clean_world_earned": round(cumulative_clean, 2),
            "total_lifetime_leakage": total_leakage_expected,
            "confidence_band": {
                "low": total_leakage_low,
                "expected": total_leakage_expected,
                "high": total_leakage_high,
            },
            "summary": summary,
            "chain_of_custody_hash": chain_hash,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# Plain-language ArtistComfortAgent summary
# ---------------------------------------------------------------------------

def _generate_summary(
    artist_id: str,
    total_actual: float,
    total_clean: float,
    total_leakage: float,
    period_count: int,
    granularity: str,
) -> str:
    pct = round((total_leakage / total_actual * 100), 1) if total_actual > 0 else 0.0
    return (
        f"Based on {period_count} {granularity}s of earnings history, XR7 estimates your catalog "
        f"would have generated ${total_clean:,.2f} in a clean world — compared to the ${total_actual:,.2f} "
        f"you actually received. That gap of ${total_leakage:,.2f} ({pct}%) represents your estimated "
        "lifetime leakage from metadata issues, unmatched royalties, split errors, foreign society gaps, "
        "and DSP attribution failures. This is not a guarantee of recovery — it is a map of what the "
        "system cost you."
    )


# ---------------------------------------------------------------------------
# Celery task entry point
# ---------------------------------------------------------------------------

def run_analysis(artist_id: str, granularity: str = "year") -> dict[str, Any]:
    """Callable by Celery: xr7.modules.earnings_time_machine.run_analysis"""
    db = SessionLocal()
    try:
        engine = EarningsTimeMachine(db)
        return engine.run(artist_id, granularity=granularity)
    finally:
        db.close()
