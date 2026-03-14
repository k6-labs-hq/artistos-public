class RecoveryUtilityRanker:
    """Rank actions by expected recovery utility, not just anomaly severity."""

    def rank(self, items: list[dict], analyst_hourly_cost: float = 75.0) -> list[dict]:
        scored = []
        for item in items:
            recoverable = float(item.get("estimated_recoverable", 0.0) or 0.0)
            success_prob = float(
                item.get(
                    "calibrated_success_probability",
                    item.get("success_probability", item.get("confidence_score", 0.5)),
                )
                or 0.5
            )
            effort_hours = float(item.get("effort_hours", 1.0) or 1.0)
            complexity_score = float(item.get("complexity_score", 0.0) or 0.0)
            complexity_penalty = complexity_score * analyst_hourly_cost * 0.25
            utility = recoverable * success_prob - effort_hours * analyst_hourly_cost
            utility -= complexity_penalty
            scored.append({
                **item,
                "expected_utility": round(utility, 4),
                "expected_recovery_value": round(recoverable * success_prob, 4),
                "complexity_penalty": round(complexity_penalty, 4),
            })

        scored.sort(key=lambda x: x["expected_utility"], reverse=True)
        for index, item in enumerate(scored, start=1):
            item["utility_rank"] = index
        return scored
