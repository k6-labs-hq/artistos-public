"""
Deterministic earnings forecaster for XR7.

This module intentionally avoids black-box prediction models. It uses recent
month-over-month net earnings growth and projects that forward with explicit,
auditable assumptions.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


def _parse_ts(raw: Any) -> datetime:
    if isinstance(raw, datetime):
        ts = raw
    elif isinstance(raw, str):
        ts = datetime.fromisoformat(raw)
    else:
        ts = datetime.now(timezone.utc)
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def _earnings_monthly_totals(earnings_records: list[dict]) -> list[tuple[datetime, float]]:
    by_month: dict[tuple[int, int], float] = {}
    for row in earnings_records:
        ts = _parse_ts(row.get("timestamp") or row.get("event_timestamp"))
        key = (ts.year, ts.month)
        by_month[key] = by_month.get(key, 0.0) + float(row.get("net", 0.0) or 0.0)

    ordered = sorted(by_month.items(), key=lambda kv: kv[0])
    return [
        (datetime(year=k[0], month=k[1], day=1, tzinfo=timezone.utc), float(v)) for k, v in ordered
    ]


def _trend_from_growth(rate: float) -> str:
    if rate > 0.01:
        return "GROWING"
    if rate < -0.01:
        return "DECLINING"
    return "FLAT"


def forecast_earnings(
    earnings_records: list[dict],
    horizon_days: int = 90,
    confidence: float = 0.95,
) -> dict:
    monthly = _earnings_monthly_totals(earnings_records)
    n = len(monthly)
    if n == 0:
        return {
            "model": "DeterministicGrowthV1",
            "data_points": 0,
            "slope_per_day": 0.0,
            "r_squared": 0.0,
            "forecast": [],
            "trend": "INSUFFICIENT_DATA",
            "explanation": {
                "method": "6-month moving average growth",
                "monthly_growth_rate": 0.0,
                "projected_total": 0.0,
                "confidence_band": [0.0, 0.0],
                "inputs": {
                    "months_analyzed": 0,
                    "recent_monthly_nets": [],
                },
            },
        }

    monthly_values = [v for _, v in monthly]
    lookback = monthly_values[-6:]

    growth_rates: list[float] = []
    for prev, cur in zip(lookback[:-1], lookback[1:]):
        base = abs(prev) if abs(prev) > 1e-9 else 1.0
        growth_rates.append((cur - prev) / base)

    mean_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0.0
    # Keep deterministic projection stable by clipping extreme single-period swings.
    mean_growth = max(-0.8, min(1.5, mean_growth))

    last_month_net = lookback[-1]
    projected_monthly: list[float] = []
    cur_val = last_month_net
    for _ in range(6):
        cur_val = max(cur_val * (1.0 + mean_growth), 0.0)
        projected_monthly.append(cur_val)

    last_dt = monthly[-1][0]
    if len(monthly) >= 2:
        prior_dt = monthly[-2][0]
        slope_per_day = (monthly[-1][1] - monthly[-2][1]) / max((last_dt - prior_dt).days, 1)
    else:
        slope_per_day = 0.0

    volatility = 0.0
    if len(growth_rates) >= 2:
        mu = sum(growth_rates) / len(growth_rates)
        variance = sum((g - mu) ** 2 for g in growth_rates) / (len(growth_rates) - 1)
        volatility = variance**0.5

    # Approximate fit metric for deterministic method compatibility.
    if len(lookback) >= 2:
        baseline = sum(lookback) / len(lookback)
        sst = sum((x - baseline) ** 2 for x in lookback)
        if sst > 0:
            fitted = []
            fv = lookback[0]
            fitted.append(fv)
            for _ in lookback[1:]:
                fv = fv * (1.0 + mean_growth)
                fitted.append(fv)
            sse = sum((a - b) ** 2 for a, b in zip(lookback, fitted))
            r2 = max(0.0, min(1.0, 1.0 - (sse / sst)))
        else:
            r2 = 1.0
    else:
        r2 = 0.0

    horizon_months = max(1, (horizon_days + 29) // 30)
    projection_pool = projected_monthly[:horizon_months]
    projected_total = float(sum(projection_pool))
    margin = projected_total * (0.15 + min(volatility, 0.35))
    low_total = max(projected_total - margin, 0.0)
    high_total = max(projected_total + margin, 0.0)

    forecast_points: list[dict] = []
    running_date = last_dt
    for day in range(1, horizon_days + 1):
        running_date = last_dt + timedelta(days=day)
        month_idx = min((day - 1) // 30, max(len(projected_monthly) - 1, 0))
        monthly_amount = projected_monthly[month_idx] if projected_monthly else 0.0
        daily_amount = monthly_amount / 30.0
        day_margin = daily_amount * (0.15 + min(volatility, 0.35))
        forecast_points.append(
            {
                "date": running_date.date().isoformat(),
                "predicted": round(max(daily_amount, 0.0), 4),
                "lower": round(max(daily_amount - day_margin, 0.0), 4),
                "upper": round(max(daily_amount + day_margin, 0.0), 4),
            }
        )

    return {
        "model": "DeterministicGrowthV1",
        "data_points": len(earnings_records),
        "slope_per_day": round(float(slope_per_day), 6),
        "r_squared": round(float(r2), 4),
        "forecast": forecast_points,
        "trend": _trend_from_growth(mean_growth),
        "explanation": {
            "method": "6-month moving average growth",
            "monthly_growth_rate": round(float(mean_growth), 6),
            "projected_total": round(projected_total, 2),
            "confidence_band": [round(low_total, 2), round(high_total, 2)],
            "inputs": {
                "months_analyzed": len(lookback),
                "recent_monthly_nets": [round(v, 2) for v in lookback],
            },
        },
    }


def forecast_by_category(
    earnings_records: list[dict],
    horizon_days: int = 90,
    confidence: float = 0.95,
) -> dict[str, dict]:
    by_type: dict[str, list[dict]] = {}
    for r in earnings_records:
        et = str(r.get("event_type", "UNKNOWN"))
        by_type.setdefault(et, []).append(r)

    return {
        et: forecast_earnings(records, horizon_days=horizon_days, confidence=confidence)
        for et, records in by_type.items()
    }


class EarningsForecaster:
    def forecast(
        self,
        earnings_records: list[dict],
        horizon_days: int = 90,
        confidence: float = 0.95,
    ) -> dict:
        return forecast_earnings(earnings_records, horizon_days=horizon_days, confidence=confidence)

    def forecast_by_category(
        self,
        earnings_records: list[dict],
        horizon_days: int = 90,
        confidence: float = 0.95,
    ) -> dict[str, dict]:
        return forecast_by_category(
            earnings_records, horizon_days=horizon_days, confidence=confidence
        )
