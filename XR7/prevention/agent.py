from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from XR7.celery_app import celery_app
from XR7.ml.forecaster import EarningsForecaster
from XR7.recovery.deadline_risk_engine import evaluate_deadline_risk
from XR7.ugc.usage_monitor import UGCUsageMonitor


class PreventiveAgent:
    """Proactive leak prevention assistant."""

    def __init__(self):
        self.forecaster = EarningsForecaster()
        self.ugc = UGCUsageMonitor()

    async def predict_future_leaks(self, artist_id: str) -> list[dict[str, Any]]:
        ugc = await self.ugc.scan_for_uses(artist_id, days_back=14)
        trend = self.forecaster.forecast([], horizon_days=90)
        risk = evaluate_deadline_risk([], [], [], [])
        risks: list[dict[str, Any]] = []
        if ugc:
            risks.append({"risk": "unclaimed_ugc_growth", "count": len(ugc), "priority": "high"})
        if trend.get("trend") == "DECLINING":
            risks.append({"risk": "declining_earnings", "priority": "medium"})
        risks.append({"risk": "deadline_drift", "risk_color": risk.get("risk_color", "GREEN"), "priority": "high"})
        return risks

    def generate_prevention_actions(self, risks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        actions = []
        for risk in risks:
            name = str(risk.get("risk") or "unknown")
            if name == "unclaimed_ugc_growth":
                actions.append({"action": "Run global UGC scan and auto-create claims", "priority": 1})
            elif name == "declining_earnings":
                actions.append({"action": "Run royalty optimization simulation", "priority": 2})
            else:
                actions.append({"action": "Escalate urgent SOL anomalies", "priority": 1})
        actions.sort(key=lambda x: x["priority"])
        return actions


@celery_app.task(name="xr7.pipeline.preventive_agent_daily", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def preventive_agent_daily(self, artist_id: str) -> dict:  # noqa: ANN001
    agent = PreventiveAgent()
    import asyncio

    risks = asyncio.run(agent.predict_future_leaks(artist_id))
    actions = agent.generate_prevention_actions(risks)
    return {
        "artist_id": artist_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "risks": risks,
        "actions": actions,
    }
