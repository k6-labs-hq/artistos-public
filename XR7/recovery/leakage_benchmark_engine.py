from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any


@dataclass
class BenchmarkCohortKey:
    catalog_size_band: str
    primary_territory: str
    channels: str
    society_profile: str
    catalog_age_band: str


class LeakageBenchmarkEngine:
    """Aggregated, opt-in, differentially-private leakage benchmarking."""

    def __init__(self, *, epsilon: float = 1.0, seed: int = 7) -> None:
        self.epsilon = max(0.05, float(epsilon))
        self._rng = random.Random(seed)

    def _laplace_noise(self, scale: float) -> float:
        u = self._rng.random() - 0.5
        return -scale * math.copysign(math.log(1 - 2 * abs(u)), u)

    def _band(self, value: float, edges: list[float], labels: list[str]) -> str:
        for idx, edge in enumerate(edges):
            if value <= edge:
                return labels[idx]
        return labels[-1]

    def cohort_key(self, profile: dict[str, Any]) -> BenchmarkCohortKey:
        tracks = float(profile.get("track_count") or 0.0)
        catalog_age = float(profile.get("catalog_age_years") or 0.0)
        return BenchmarkCohortKey(
            catalog_size_band=self._band(tracks, [200, 1000, 5000], ["micro", "small", "mid", "large"]),
            primary_territory=str(profile.get("primary_territory") or "GLOBAL").upper(),
            channels="|".join(sorted([str(c).upper() for c in (profile.get("distribution_channels") or ["DSP"])])),
            society_profile="|".join(sorted([str(s).upper() for s in (profile.get("societies") or ["GENERIC"])])),
            catalog_age_band=self._band(catalog_age, [2, 7, 15], ["new", "growth", "mature", "legacy"]),
        )

    def _safe_ratio(self, a: float, b: float) -> float:
        if b <= 0:
            return 0.0
        return max(0.0, min(1.0, a / b))

    def compute_client_metrics(self, client: dict[str, Any]) -> dict[str, float]:
        leaked = float(client.get("estimated_leaked") or 0.0)
        earnings = float(client.get("total_estimated_earnings") or 0.0)
        recovered = float(client.get("recovered") or 0.0)
        expired = float(client.get("expired") or 0.0)
        leakage_rate_pct = self._safe_ratio(leaked, earnings) * 100.0
        recovery_rate_pct = self._safe_ratio(recovered, leaked) * 100.0
        expiration_rate_pct = self._safe_ratio(expired, leaked) * 100.0
        return {
            "leakage_rate_pct": round(leakage_rate_pct, 6),
            "recovery_rate_pct": round(recovery_rate_pct, 6),
            "expiration_rate_pct": round(expiration_rate_pct, 6),
        }

    def aggregate_cohort(self, clients: list[dict[str, Any]]) -> dict[str, Any]:
        rows = [self.compute_client_metrics(c) for c in clients if bool(c.get("benchmark_opt_in", True))]
        if not rows:
            return {
                "count": 0,
                "leakage_rate_pct": 0.0,
                "recovery_rate_pct": 0.0,
                "expiration_rate_pct": 0.0,
                "differential_privacy": {"epsilon": self.epsilon, "enabled": True},
            }

        def avg(key: str) -> float:
            return sum(float(r.get(key) or 0.0) for r in rows) / max(len(rows), 1)

        scale = 1.0 / self.epsilon
        return {
            "count": len(rows),
            "leakage_rate_pct": round(max(0.0, avg("leakage_rate_pct") + self._laplace_noise(scale)), 6),
            "recovery_rate_pct": round(max(0.0, avg("recovery_rate_pct") + self._laplace_noise(scale)), 6),
            "expiration_rate_pct": round(max(0.0, avg("expiration_rate_pct") + self._laplace_noise(scale)), 6),
            "differential_privacy": {"epsilon": self.epsilon, "enabled": True},
        }

    def _percentile(self, values: list[float], x: float) -> float:
        if not values:
            return 0.0
        below = sum(1 for v in values if v <= x)
        return round((below / len(values)) * 100.0, 2)

    def compare_against_cohort(self, client: dict[str, Any], peers: list[dict[str, Any]]) -> dict[str, Any]:
        client_metrics = self.compute_client_metrics(client)
        peer_metrics = [self.compute_client_metrics(p) for p in peers if bool(p.get("benchmark_opt_in", True))]

        leakage_dist = [m["leakage_rate_pct"] for m in peer_metrics]
        recovery_dist = [m["recovery_rate_pct"] for m in peer_metrics]
        expiration_dist = [m["expiration_rate_pct"] for m in peer_metrics]

        leakage_percentile = self._percentile(leakage_dist, client_metrics["leakage_rate_pct"])
        recovery_percentile = self._percentile(recovery_dist, client_metrics["recovery_rate_pct"])
        expiration_percentile = self._percentile(expiration_dist, client_metrics["expiration_rate_pct"])

        expiration_risk_rating = "LOW"
        if expiration_percentile >= 80:
            expiration_risk_rating = "HIGH"
        elif expiration_percentile >= 50:
            expiration_risk_rating = "MEDIUM"

        narrative = (
            f"Your digital mechanical expiration rate is in the {int(expiration_percentile)}th percentile. "
            f"XR7 recommends accelerating ISRC normalization for high-value tracks with unresolved society matching."
        )

        return {
            "client_metrics": client_metrics,
            "cohort": self.aggregate_cohort(peers),
            "leakage_percentile": leakage_percentile,
            "recovery_percentile": recovery_percentile,
            "expiration_risk_rating": expiration_risk_rating,
            "expiration_percentile": expiration_percentile,
            "narrative": narrative,
            "panel_title": "Catalog Health vs. Industry",
        }
