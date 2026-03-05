class RecoveryUtilityRanker:
    """Rank actions by expected recovery utility, not just anomaly severity."""

    def rank(self, items: list[dict], analyst_hourly_cost: float = 75.0) -> list[dict]:
        scored = []
        for item in items:
            recoverable = float(item.get("estimated_recoverable", 0.0) or 0.0)
            success_prob = float(item.get("success_probability", item.get("confidence_score", 0.5)) or 0.5)
            effort_hours = float(item.get("effort_hours", 1.0) or 1.0)
            utility = recoverable * success_prob - effort_hours * analyst_hourly_cost
            scored.append({
                **item,
                "expected_utility": round(utility, 4),
                "expected_recovery_value": round(recoverable * success_prob, 4),
            })

        scored.sort(key=lambda x: x["expected_utility"], reverse=True)
        for index, item in enumerate(scored, start=1):
            item["utility_rank"] = index
        return scored
