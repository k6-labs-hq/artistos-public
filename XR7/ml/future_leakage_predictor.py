from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass
class FutureLeakagePrediction:
    work_id: str
    probability: float
    risk_band: str
    recommended_repairs: list[str]


class FutureLeakagePredictor:
    """Heuristic ML-style predictor for per-work future leakage risk."""

    def predict_per_work(
        self,
        works: list[dict[str, Any]],
        *,
        metadata_completeness: float,
        identifier_coverage: float,
        anomaly_density: float,
        payment_regularity: float,
        catalog_age_years: float,
        distributor_footprint: int,
    ) -> list[FutureLeakagePrediction]:
        rows: list[FutureLeakagePrediction] = []
        for work in works:
            missing_ids = 1.0 if not (work.get("isrc") and work.get("iswc")) else 0.0
            raw = (
                1.8 * missing_ids
                + 1.2 * (1.0 - metadata_completeness)
                + 1.1 * (1.0 - identifier_coverage)
                + 1.0 * anomaly_density
                + 0.9 * (1.0 - payment_regularity)
                + 0.3 * min(catalog_age_years / 10.0, 1.0)
                + 0.2 * min(distributor_footprint / 8.0, 1.0)
                - 1.9
            )
            probability = 1.0 / (1.0 + math.exp(-raw))
            if probability >= 0.7:
                band = "HIGH"
            elif probability >= 0.4:
                band = "MEDIUM"
            else:
                band = "LOW"

            repairs: list[str] = []
            if missing_ids > 0:
                repairs.append("Infer and register missing ISRC/ISWC identifiers")
            if probability >= 0.4:
                repairs.append("Run split/rights repair and verify PRO registrations")
                repairs.append("Enable UGC auto-registration and fingerprint sync")

            rows.append(
                FutureLeakagePrediction(
                    work_id=str(work.get("id") or ""),
                    probability=round(float(probability), 4),
                    risk_band=band,
                    recommended_repairs=repairs,
                )
            )
        return rows
