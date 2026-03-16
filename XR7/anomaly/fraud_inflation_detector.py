from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from XR7.celery_app import celery_app
from XR7.ml.forecaster import EarningsForecaster


class FraudInflationDetector:
    def __init__(self):
        self.forecaster = EarningsForecaster()

    def monitor_stream_patterns(self, artist_id: str) -> dict[str, Any]:
        # Simulated detector using deterministic patterns.
        alerts = [
            {"type": "bot_like_geo_spike", "platform": "spotify", "risk": "high", "confidence": 0.84},
            {"type": "low_engagement_high_streams", "platform": "apple_music", "risk": "medium", "confidence": 0.73},
        ]
        return {"artist_id": artist_id, "alerts": alerts, "generated_at": datetime.now(timezone.utc).isoformat()}

    def calculate_pool_drain_impact(self, monitor_output: dict[str, Any]) -> float:
        return round(sum(1200.0 if a.get("risk") == "high" else 500.0 for a in monitor_output.get("alerts", [])), 2)

    def flag_anomalies_for_report(self, artist_id: str) -> dict[str, Any]:
        m = self.monitor_stream_patterns(artist_id)
        impact = self.calculate_pool_drain_impact(m)
        adjusted = self.forecaster.forecast_90d([])
        adjusted["predicted_total"] = max(0.0, float(adjusted.get("predicted_total") or 0.0) - impact)
        return {
            "artist_id": artist_id,
            "fraud_protection_health": "AT_RISK" if impact > 1000 else "STABLE",
            "estimated_protected": impact,
            "alerts": m.get("alerts", []),
            "adjusted_forecast": adjusted,
        }


@celery_app.task(name="xr7.pipeline.fraud_scan_hourly", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def fraud_scan_hourly(self, artist_id: str) -> dict:  # noqa: ANN001
    return FraudInflationDetector().flag_anomalies_for_report(artist_id)
