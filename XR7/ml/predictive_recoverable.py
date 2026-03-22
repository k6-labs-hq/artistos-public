"""
Predictive Total Recoverable Value Model — XR7 Engine 2.

Ensemble of:
  1. Deterministic earnings forecaster (existing DeterministicGrowthV1)
  2. Bayesian posterior blend from SuccessProbabilityCalibrator
  3. SOL decay curve (open anomalies near deadline get discounted)
  4. Recovery pipeline factor (value already in active claims)

Returns low / mid / high USD estimates with a confidence score and key drivers.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly, AnomalyStatus
from XR7.models.claim import Claim, ClaimStatus
from XR7.ml.forecaster import forecast_earnings
from XR7.ml.success_probability_calibrator import SuccessProbabilityCalibrator
from XR7.models.xr7_royalty import XR7RoyaltyStatement
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HORIZON_MONTHS_ALLOWED = frozenset([6, 12, 24, 36, 60])
_TERMINAL_CLAIM_STATUSES = frozenset([
    ClaimStatus.PAID.value, ClaimStatus.CLOSED.value,
])
_ACTIVE_CLAIM_STATUSES = frozenset([
    ClaimStatus.IDENTIFIED.value, ClaimStatus.PREPARED.value,
    ClaimStatus.FILED.value, ClaimStatus.SUBMITTED.value,
    ClaimStatus.PROOF_SUBMITTED.value, ClaimStatus.IN_REVIEW.value,
    ClaimStatus.ACCEPTED.value, ClaimStatus.FUNDS_RECEIVED.value,
])


# ---------------------------------------------------------------------------
# SOL decay helpers
# ---------------------------------------------------------------------------

def _sol_decay_factor(sol_deadline: datetime | None, now: datetime) -> float:
    """
    Return a [0, 1] multiplier capturing urgency/risk from SOL proximity.

    - deadline > 365 days away  → 1.00  (no decay)
    - deadline in 180–365 days  → 0.90
    - deadline in 90–180 days   → 0.75  (at risk)
    - deadline in 0–90 days     → 0.50  (urgent)
    - past deadline             → 0.10  (near-expired / last resort)
    """
    if sol_deadline is None:
        return 0.95  # assume reasonably safe if not tracked

    deadline = sol_deadline.replace(tzinfo=timezone.utc) if sol_deadline.tzinfo is None else sol_deadline
    days_remaining = (deadline - now).days

    if days_remaining > 365:
        return 1.00
    if days_remaining > 180:
        return 0.90
    if days_remaining > 90:
        return 0.75
    if days_remaining >= 0:
        return 0.50
    return 0.10


def _compute_sol_adjusted_value(anomalies: list[Anomaly], claims: list[Claim]) -> tuple[float, list[str]]:
    """
    For each open anomaly, apply its SOL decay factor.
    Returns (total_sol_adjusted_value, key_driver_strings).
    """
    now = datetime.now(timezone.utc)
    claim_by_anomaly: dict[str, Claim] = {c.anomaly_id: c for c in claims}

    urgent_count = 0
    closing_soon_count = 0
    total = 0.0

    for anomaly in anomalies:
        if str(anomaly.status).upper() in ("CLOSED",):
            continue
        raw_value = float(anomaly.estimated_recoverable or 0.0)
        if raw_value <= 0:
            continue

        claim = claim_by_anomaly.get(anomaly.id)
        sol_deadline: datetime | None = getattr(claim, "sol_deadline", None) if claim else None
        decay = _sol_decay_factor(sol_deadline, now)
        total += raw_value * decay

        if sol_deadline:
            days = (sol_deadline.replace(tzinfo=timezone.utc) - now).days
            if days < 90:
                urgent_count += 1
            elif days < 365:
                closing_soon_count += 1

    drivers: list[str] = []
    if urgent_count:
        drivers.append(f"{urgent_count} claim window{'s' if urgent_count > 1 else ''} closing in < 90 days — act now")
    if closing_soon_count:
        drivers.append(f"{closing_soon_count} foreign PRO window{'s' if closing_soon_count > 1 else ''} closing within 12 months")

    return round(total, 2), drivers


# ---------------------------------------------------------------------------
# Main ensemble
# ---------------------------------------------------------------------------

class PredictiveRecoverableModel:
    """
    Ensemble predictive model for total recoverable value over a horizon.

    The ensemble combines:
      1. **Earnings trajectory** — projected incremental earnings leakage
         driven by DeterministicGrowthV1.
      2. **Open anomaly pipeline** — SOL-discounted value of all open anomalies.
      3. **Bayesian confidence blend** — success_rate posterior from
         SuccessProbabilityCalibrator scales the mid estimate.
      4. **Active claim multiplier** — value already filed boosts conviction.

    Confidence is derived from:
      - Posterior sample count (more feedback = more confidence)
      - Forecaster R² (how well the growth model fits)
      - Anomaly count (more data points = higher confidence)
    """

    _calibrator = SuccessProbabilityCalibrator()

    def predict(
        self,
        *,
        artist_id: str,
        horizon_months: int,
        db: Session,
    ) -> dict[str, Any]:
        if horizon_months not in _HORIZON_MONTHS_ALLOWED:
            raise ValueError(f"horizon_months must be one of {sorted(_HORIZON_MONTHS_ALLOWED)}")

        now = datetime.now(timezone.utc)
        anomalies: list[Anomaly] = (
            db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        )
        claims: list[Claim] = (
            db.query(Claim).filter(Claim.artist_id == artist_id).all()
        )

        # ── 1. Earnings trajectory ─────────────────────────────────────────
        royalty_stmts = (
            db.query(XR7RoyaltyStatement)
            .filter(XR7RoyaltyStatement.artist_id == artist_id)
            .all()
        )
        earnings_records = [
            {
                "timestamp": (
                    r.period_end.isoformat()
                    if r.period_end
                    else (r.period_start.isoformat() if r.period_start else now.isoformat())
                ),
                "net": float(r.net_amount or 0.0),
            }
            for r in royalty_stmts
        ]
        horizon_days = horizon_months * 30
        forecast = forecast_earnings(earnings_records, horizon_days=horizon_days)
        projected_earnings = float(forecast.get("explanation", {}).get("projected_total") or 0.0)
        forecast_r2 = float(forecast.get("r_squared") or 0.0)
        forecast_trend = str(forecast.get("trend") or "INSUFFICIENT_DATA")

        # ── 2. SOL-adjusted open anomaly pipeline ──────────────────────────
        sol_adjusted_pipeline, sol_drivers = _compute_sol_adjusted_value(anomalies, claims)

        # ── 3. Bayesian posterior success rate ─────────────────────────────
        try:
            posterior_rate, sample_count = self._calibrator.posterior_success_rate(artist_id, db)
        except Exception:
            logger.exception("Failed to compute posterior success rate; using prior")
            posterior_rate = 0.5
            sample_count = 0

        # ── 4. Active claim pipeline ───────────────────────────────────────
        active_claims = [c for c in claims if str(c.status) in _ACTIVE_CLAIM_STATUSES]
        active_pipeline_value = sum(
            float(c.recovered_amount or 0.0) or
            float(
                next((a.estimated_recoverable for a in anomalies if a.id == c.anomaly_id), None) or 0.0
            )
            for c in active_claims
        )

        # ── Combine into low / mid / high ─────────────────────────────────
        # Scale projected earnings leakage proportionally to horizon
        horizon_scale = min(horizon_months / 12.0, 5.0)

        # Mid = posterior-weighted blend of earnings projection + anomaly pipeline
        raw_mid = (
            projected_earnings * horizon_scale * 0.25  # incremental leakage share
            + sol_adjusted_pipeline * posterior_rate    # expected recovery success
            + active_pipeline_value * 0.85             # 85% of active claims expected to close
        )

        # Spread driven by forecast uncertainty + horizon length
        spread_pct = max(
            0.20,
            min(0.60, (1.0 - forecast_r2) * 0.4 + 0.15 * math.log1p(horizon_months / 6.0)),
        )
        low_usd = max(0.0, round(raw_mid * (1.0 - spread_pct), 2))
        mid_usd = round(raw_mid, 2)
        high_usd = round(raw_mid * (1.0 + spread_pct), 2)

        # ── Confidence score ──────────────────────────────────────────────
        # Combine: sample count weight + R² weight + anomaly count weight
        sample_weight = min(1.0, sample_count / 20.0) * 0.35
        r2_weight = float(forecast_r2) * 0.35
        anomaly_weight = min(1.0, len(anomalies) / 15.0) * 0.30
        confidence = round(sample_weight + r2_weight + anomaly_weight, 3)
        confidence = max(0.05, min(0.99, confidence))

        # ── Key drivers ───────────────────────────────────────────────────
        drivers: list[str] = list(sol_drivers)

        if forecast_trend == "GROWING":
            drivers.append("Earnings trend growing — projected leakage rate increasing")
        elif forecast_trend == "DECLINING":
            drivers.append("Earnings trend declining — window to recover shrinking")

        if active_pipeline_value > 0:
            drivers.append(
                f"${active_pipeline_value:,.0f} already in active claim pipeline "
                f"({len(active_claims)} claim{'s' if len(active_claims) != 1 else ''})"
            )

        if posterior_rate >= 0.65:
            drivers.append(
                f"High historical success rate ({posterior_rate:.0%}) "
                "boosts recovery confidence"
            )
        elif posterior_rate < 0.40 and sample_count >= 5:
            drivers.append(
                "Historical success rate below average — improve claim quality to increase recoverable"
            )

        open_anomaly_count = sum(1 for a in anomalies if str(a.status).upper() != "CLOSED")
        if open_anomaly_count:
            drivers.append(
                f"{open_anomaly_count} open anomal{'ies' if open_anomaly_count != 1 else 'y'} "
                f"with ${sol_adjusted_pipeline:,.0f} SOL-adjusted recoverable value"
            )

        if not drivers:
            drivers.append("Insufficient historical data; estimate based on industry priors")

        return {
            "artist_id": artist_id,
            "horizon_months": horizon_months,
            "low_usd": low_usd,
            "mid_usd": mid_usd,
            "high_usd": high_usd,
            "confidence": confidence,
            "key_drivers": drivers[:6],  # cap at 6 for UI
            "components": {
                "projected_earnings_leakage": round(projected_earnings * horizon_scale * 0.25, 2),
                "sol_adjusted_pipeline": sol_adjusted_pipeline,
                "active_claim_pipeline": round(active_pipeline_value * 0.85, 2),
                "posterior_success_rate": round(posterior_rate, 4),
                "forecast_trend": forecast_trend,
                "spread_pct": round(spread_pct, 4),
            },
        }
