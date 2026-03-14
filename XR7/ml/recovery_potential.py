from __future__ import annotations


class RecoveryPotentialModel:
    """Estimate artist-level lifetime recovery potential and complexity."""

    def score(
        self,
        *,
        anomalies: list[dict],
        contracts: list[dict],
        catalog_health_score: float,
        peer_multiplier: float = 1.0,
    ) -> dict:
        anomaly_value = sum(float(a.get("estimated_recoverable") or 0.0) for a in anomalies)
        open_anomaly_count = sum(1 for a in anomalies if str(a.get("status")) != "CLOSED")
        contract_complexity = sum(1 for c in contracts if c.get("territory") and str(c.get("territory")).upper() not in {"US", "USA"})
        contract_complexity += len(contracts)

        health_factor = max(0.5, min(1.5, (100.0 - float(catalog_health_score or 0.0)) / 50.0))
        lifetime_potential = max(0.0, anomaly_value * health_factor * float(peer_multiplier or 1.0))

        complexity_score = min(1.0, (0.03 * open_anomaly_count) + (0.05 * contract_complexity))
        return {
            "lifetime_recovery_potential": round(lifetime_potential, 2),
            "complexity_score": round(complexity_score, 6),
            "components": {
                "anomaly_value": round(anomaly_value, 2),
                "open_anomaly_count": open_anomaly_count,
                "contract_complexity": contract_complexity,
                "health_factor": round(health_factor, 6),
                "peer_multiplier": round(float(peer_multiplier or 1.0), 6),
            },
        }
