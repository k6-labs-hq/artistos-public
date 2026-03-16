from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import numpy as np


@dataclass
class ForecastBand:
    days: int
    low: float
    expected: float
    high: float
    confidence_interval: dict[str, float]


class PostRepairEarningsForecaster:
    """
    Post-repair earnings forecaster.

    This is a production-safe, deterministic forecaster that emulates
    Prophet-style seasonality and Bayesian-style shrinkage while keeping
    dependencies lightweight for the XR7 service runtime.
    """

    def _trend_and_dispersion(self, rows: list[dict[str, Any]]) -> tuple[float, float, float]:
        if not rows:
            return 0.0, 0.0, 0.0
        series = sorted(rows, key=lambda r: r.get("timestamp") or datetime.min)
        x = np.array([float(i + 1) for i in range(len(series))], dtype=float)
        y = np.array([float(r.get("net") or 0.0) for r in series], dtype=float)
        if len(series) == 1:
            return float(y[0]), 0.0, 0.0
        slope, intercept = np.polyfit(x, y, 1)
        baseline = float(max(y.mean(), 0.0))
        residual = y - (slope * x + intercept)
        sigma = float(np.std(residual))
        return baseline, float(slope), sigma

    def _seasonality_factor(self, rows: list[dict[str, Any]]) -> float:
        if not rows:
            return 1.0
        months = [int((r.get("timestamp") or datetime.utcnow()).month) for r in rows]
        winter = sum(1 for m in months if m in {11, 12, 1, 2})
        summer = sum(1 for m in months if m in {6, 7, 8})
        # Mild seasonality swing to avoid overfit in sparse catalogs.
        if winter > summer:
            return 1.04
        if summer > winter:
            return 0.98
        return 1.0

    def _trend_label(self, slope: float, baseline: float) -> str:
        threshold = max(0.01 * max(baseline, 1.0), 1e-6)
        if slope > threshold:
            return "GROWING"
        if slope < -threshold:
            return "DECLINING"
        return "STABLE"

    def _stream_bucket(self, event_type: str, territory: str | None) -> str:
        et = (event_type or "").upper()
        terr = (territory or "US").upper()
        if "STREAM" in et:
            return "streaming"
        if "SALE" in et:
            return "mechanicals"
        if "SYNC" in et:
            return "sync_backend"
        if terr not in {"US", "USA"}:
            return "foreign_royalties"
        return "pro_performance"

    def forecast(
        self,
        historical_rows: list[dict[str, Any]],
        *,
        metadata_quality: float,
        split_correction_factor: float,
        rate_correction_factor: float,
        ugc_virality_multiplier: float,
        foreign_lag_factor: float,
        confidence_level: float = 0.95,
    ) -> dict[str, Any]:
        baseline, slope, sigma = self._trend_and_dispersion(historical_rows)
        seasonality = self._seasonality_factor(historical_rows)

        # Bayesian-style shrinkage toward stable baseline for noisy catalogs.
        shrink = max(0.55, min(0.95, 1.0 - (sigma / max(baseline + sigma, 1.0)) * 0.4))
        effective_slope = slope * shrink

        repair_factor = (
            max(0.7, min(1.25, metadata_quality))
            * max(0.8, min(1.2, split_correction_factor))
            * max(0.8, min(1.2, rate_correction_factor))
            * max(0.8, min(1.3, ugc_virality_multiplier))
            * max(0.75, min(1.15, foreign_lag_factor))
        )

        horizons = [30, 60, 90, 180]
        horizon_rows: dict[str, dict[str, Any]] = {}
        for h in horizons:
            expected = max(0.0, (baseline + (effective_slope * h * 0.5)) * h * seasonality * repair_factor)
            band = max(expected * (1.0 - confidence_level) * 0.9, sigma * np.sqrt(max(h / 30.0, 1.0)))
            low = max(0.0, expected - band)
            high = max(0.0, expected + band)
            horizon_rows[str(h)] = {
                "days": h,
                "low": round(float(low), 2),
                "expected": round(float(expected), 2),
                "high": round(float(high), 2),
                "confidence_interval": {
                    "level": confidence_level,
                    "low": round(float(low), 2),
                    "high": round(float(high), 2),
                },
            }

        stream_totals = {
            "streaming": 0.0,
            "mechanicals": 0.0,
            "pro_performance": 0.0,
            "ugc_monetization": 0.0,
            "sync_backend": 0.0,
            "foreign_royalties": 0.0,
        }
        work_totals: dict[str, float] = {}

        for row in historical_rows:
            amt = float(row.get("net") or 0.0)
            bucket = self._stream_bucket(str(row.get("event_type") or ""), row.get("territory"))
            stream_totals[bucket] = stream_totals.get(bucket, 0.0) + amt
            if str(row.get("platform") or "").lower() in {"youtube", "tiktok", "instagram"}:
                stream_totals["ugc_monetization"] += amt * 0.3
            work_id = str(row.get("work_id") or "")
            if work_id:
                work_totals[work_id] = work_totals.get(work_id, 0.0) + amt

        expected_90 = float(horizon_rows["90"]["expected"])
        total_hist = max(sum(work_totals.values()), 1.0)
        per_work_forecast = [
            {
                "work_id": wid,
                "predicted_next_90_days": round(expected_90 * (amt / total_hist), 2),
            }
            for wid, amt in sorted(work_totals.items(), key=lambda x: x[1], reverse=True)
        ]

        stream_hist_total = max(sum(stream_totals.values()), 1.0)
        per_stream_forecast = {
            key: round(expected_90 * (val / stream_hist_total), 2)
            for key, val in stream_totals.items()
        }

        points = len(historical_rows)
        if points >= 120 and sigma <= max(baseline, 1.0):
            confidence_band = "HIGH"
        elif points >= 45:
            confidence_band = "MEDIUM"
        else:
            confidence_band = "LOW"

        return {
            "horizons": horizon_rows,
            "predicted_total_next_90_days": horizon_rows["90"]["expected"],
            "predicted_low": horizon_rows["90"]["low"],
            "predicted_high": horizon_rows["90"]["high"],
            "confidence_band": confidence_band,
            "trend_indicator": self._trend_label(effective_slope, baseline),
            "per_work_forecast": per_work_forecast,
            "per_revenue_stream_forecast": per_stream_forecast,
            "model_metadata": {
                "model_name": "PostRepairEarningsForecaster",
                "style": "BayesianRegressionWithSeasonality",
                "seasonality_factor": round(float(seasonality), 4),
                "repair_factor": round(float(repair_factor), 4),
                "data_points": points,
            },
        }
