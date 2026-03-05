"""
Earnings forecaster for XR7 Engine 2.

Provides:
- Linear-regression trend forecasting over historical earnings data.
- Confidence intervals (based on residual standard deviation).
- A per-category breakdown so managers can see which revenue streams are
  growing, flat, or declining.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np
from sklearn.linear_model import LinearRegression


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Multiplier applied to the residual standard deviation to determine whether
# a slope is significant enough to classify as GROWING or DECLINING.
# A slope whose magnitude is less than _TREND_THRESHOLD_MULTIPLIER × σ_residual
# is treated as statistically indistinguishable from zero (FLAT).
# 0.01 is deliberately conservative — it classifies a trend as non-flat only
# when the per-day slope is at least 1 % of the typical earnings scatter.
_TREND_THRESHOLD_MULTIPLIER = 0.01

# Z-values for common confidence levels (normal approximation).
# Using a lookup table avoids adding a scipy dependency.
_Z_FOR_CONFIDENCE: dict[float, float] = {
    0.80: 1.282,
    0.85: 1.440,
    0.90: 1.645,
    0.95: 1.960,
    0.99: 2.576,
}
_DEFAULT_Z = 1.960  # fallback for confidence levels not in the table


def _z_for_confidence(confidence: float) -> float:
    """Return the two-tailed z-value for *confidence* (e.g. 0.95 → 1.96)."""
    # Round to 2 decimal places to allow slight floating-point imprecision.
    key = round(confidence, 2)
    if key in _Z_FOR_CONFIDENCE:
        return _Z_FOR_CONFIDENCE[key]
    # Linear interpolation between the two nearest table entries.
    keys = sorted(_Z_FOR_CONFIDENCE)
    for lo, hi in zip(keys, keys[1:]):
        if lo <= key <= hi:
            t = (key - lo) / (hi - lo)
            return _Z_FOR_CONFIDENCE[lo] + t * (_Z_FOR_CONFIDENCE[hi] - _Z_FOR_CONFIDENCE[lo])
    return _DEFAULT_Z


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _earnings_to_series(earnings_records: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert a list of earnings records into a (timestamps_ordinal, net_values)
    pair of 1-D arrays sorted by time.

    Each record must contain ``timestamp`` (datetime or ISO string) and ``net``
    (float).
    """

    def _parse(r: dict) -> tuple[datetime, float]:
        ts = r.get("timestamp") or r.get("event_timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)
        elif ts is None:
            ts = datetime.now(timezone.utc)
        return ts, float(r.get("net", 0.0))

    parsed = sorted([_parse(r) for r in earnings_records], key=lambda x: x[0])
    if not parsed:
        return np.array([]), np.array([])

    timestamps = np.array([t.toordinal() for t, _ in parsed], dtype=float)
    values = np.array([v for _, v in parsed], dtype=float)
    return timestamps, values


# ---------------------------------------------------------------------------
# Core forecasting logic
# ---------------------------------------------------------------------------

def forecast_earnings(
    earnings_records: list[dict],
    horizon_days: int = 90,
    confidence: float = 0.95,
) -> dict:
    """
    Fit a linear trend model on historical earnings and project forward.

    Parameters
    ----------
    earnings_records:
        List of dicts produced by ``EarningsEngine.reconstruct_historical()``.
        Each record must have ``timestamp`` and ``net``.
    horizon_days:
        Number of days ahead to forecast.
    confidence:
        Confidence level for the prediction interval (0–1).  ``0.95`` returns
        a ~95 % interval using ±1.96 residual standard deviations.

    Returns
    -------
    A dict with keys:
    - ``model``: ``"LinearTrend"``
    - ``data_points``: number of training records
    - ``slope_per_day``: trend slope (earnings per ordinal day)
    - ``r_squared``: goodness of fit
    - ``forecast``: list of ``{date, predicted, lower, upper}`` dicts
    - ``trend``: ``"GROWING"`` | ``"FLAT"`` | ``"DECLINING"``
    """
    timestamps, values = _earnings_to_series(earnings_records)
    n = len(timestamps)

    if n == 0:
        return {
            "model": "LinearTrend",
            "data_points": 0,
            "slope_per_day": 0.0,
            "r_squared": None,
            "forecast": [],
            "trend": "INSUFFICIENT_DATA",
        }

    X = timestamps.reshape(-1, 1)
    reg = LinearRegression()
    reg.fit(X, values)

    slope = float(reg.coef_[0])
    y_pred = reg.predict(X)
    ss_res = float(np.sum((values - y_pred) ** 2))
    ss_tot = float(np.sum((values - values.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    residual_std = float(np.sqrt(ss_res / max(n - 2, 1)))

    # Look up the two-tailed z-value for the requested confidence level.
    z = _z_for_confidence(confidence)

    # Generate future timestamps
    last_ts = datetime.fromordinal(int(timestamps[-1]))
    forecast_points = []
    for day in range(1, horizon_days + 1):
        future_dt = last_ts + timedelta(days=day)
        future_ord = float(future_dt.toordinal())
        predicted = float(reg.predict([[future_ord]])[0])
        margin = z * residual_std
        forecast_points.append(
            {
                "date": future_dt.date().isoformat(),
                "predicted": round(max(predicted, 0.0), 4),
                "lower": round(max(predicted - margin, 0.0), 4),
                "upper": round(max(predicted + margin, 0.0), 4),
            }
        )

    # Classify trend using _TREND_THRESHOLD_MULTIPLIER × residual_std as the
    # significance threshold for the slope.
    if slope > residual_std * _TREND_THRESHOLD_MULTIPLIER:
        trend = "GROWING"
    elif slope < -residual_std * _TREND_THRESHOLD_MULTIPLIER:
        trend = "DECLINING"
    else:
        trend = "FLAT"

    return {
        "model": "LinearTrend",
        "data_points": n,
        "slope_per_day": round(slope, 6),
        "r_squared": round(r2, 4),
        "forecast": forecast_points,
        "trend": trend,
    }


def forecast_by_category(
    earnings_records: list[dict],
    horizon_days: int = 90,
    confidence: float = 0.95,
) -> dict[str, dict]:
    """
    Run ``forecast_earnings`` independently for each ``event_type`` found in
    *earnings_records* and return a dict keyed by event type.

    Parameters
    ----------
    earnings_records:
        List of dicts.  Each record must have ``event_type`` in addition to the
        fields required by ``forecast_earnings``.

    Returns
    -------
    ``{event_type: forecast_result, ...}``
    """
    by_type: dict[str, list[dict]] = {}
    for r in earnings_records:
        et = str(r.get("event_type", "UNKNOWN"))
        by_type.setdefault(et, []).append(r)

    return {
        et: forecast_earnings(records, horizon_days=horizon_days, confidence=confidence)
        for et, records in by_type.items()
    }


# ---------------------------------------------------------------------------
# Public class wrapper
# ---------------------------------------------------------------------------

class EarningsForecaster:
    """
    High-level interface for earnings trend forecasting.

    Usage::

        forecaster = EarningsForecaster()
        result = forecaster.forecast(earnings_records, horizon_days=90)
        by_category = forecaster.forecast_by_category(earnings_records)
    """

    def forecast(
        self,
        earnings_records: list[dict],
        horizon_days: int = 90,
        confidence: float = 0.95,
    ) -> dict:
        """Aggregate forecast across all earnings records."""
        return forecast_earnings(earnings_records, horizon_days=horizon_days, confidence=confidence)

    def forecast_by_category(
        self,
        earnings_records: list[dict],
        horizon_days: int = 90,
        confidence: float = 0.95,
    ) -> dict[str, dict]:
        """Per-category (event_type) forecasts."""
        return forecast_by_category(earnings_records, horizon_days=horizon_days, confidence=confidence)
