from __future__ import annotations


class CatalogSegmenter:
    """Heuristic catalog segmentation used to tune thresholding and prioritization."""

    def segment(self, works: list[dict], payments: list[dict], anomalies: list[dict]) -> dict:
        work_count = len(works)
        payment_total = sum(float(p.get("amount") or 0.0) for p in payments)
        anomaly_density = float(len(anomalies)) / max(float(work_count), 1.0)

        if work_count >= 30 and anomaly_density < 0.25:
            segment = "long_tail_catalog"
            score = 0.65
        elif payment_total > 50000 and work_count >= 8:
            segment = "frontline_releases"
            score = 0.8
        elif anomaly_density >= 0.4:
            segment = "high_sync_potential"
            score = 0.72
        else:
            segment = "balanced_catalog"
            score = 0.6

        return {
            "segment": segment,
            "score": score,
            "features": {
                "work_count": work_count,
                "payment_total": round(payment_total, 2),
                "anomaly_density": round(anomaly_density, 6),
            },
            "threshold_adjustment": 0.9 if segment == "frontline_releases" else 1.1,
            "effort_adjustment": 1.1 if segment == "high_sync_potential" else 1.0,
        }
