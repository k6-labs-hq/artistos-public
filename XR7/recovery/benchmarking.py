from __future__ import annotations

from typing import Any


def cross_artist_benchmarks(artist_summary: dict[str, Any], peer_population: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute cross-artist benchmarking metrics and simple percentiles."""
    leakage_values = sorted(float(p.get("leakage", 0.0) or 0.0) for p in peer_population) or [0.0]
    recovery_values = sorted(float(p.get("recovery", 0.0) or 0.0) for p in peer_population) or [0.0]
    density_values = sorted(float(p.get("anomaly_density", 0.0) or 0.0) for p in peer_population) or [0.0]
    health_values = sorted(float(p.get("catalog_health", 0.0) or 0.0) for p in peer_population) or [0.0]

    def _pct(values: list[float], value: float) -> float:
        below = sum(1 for v in values if v <= value)
        return round((below / max(len(values), 1)) * 100.0, 2)

    return {
        "average_leakage": round(sum(leakage_values) / max(len(leakage_values), 1), 2),
        "average_recovery": round(sum(recovery_values) / max(len(recovery_values), 1), 2),
        "anomaly_density": float(artist_summary.get("anomaly_density") or 0.0),
        "catalog_health_percentiles": {
            "artist_percentile": _pct(health_values, float(artist_summary.get("catalog_health") or 0.0)),
        },
        "peer_percentiles": {
            "leakage": _pct(leakage_values, float(artist_summary.get("leakage") or 0.0)),
            "recovery": _pct(recovery_values, float(artist_summary.get("recovery") or 0.0)),
            "anomaly_density": _pct(density_values, float(artist_summary.get("anomaly_density") or 0.0)),
        },
    }
