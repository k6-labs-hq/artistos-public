from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from XR7.earnings.engine import EarningsEngine
from XR7.graph.rights_graph import RightsGraph
from XR7.ml.future_leakage_predictor import FutureLeakagePredictor
from XR7.ml.post_repair_earnings_forecaster import PostRepairEarningsForecaster
from XR7.ml.rate_benchmarker import RateBenchmarker
from XR7.models.event import Event
from XR7.models.work import Work
from XR7.services.foreign_society_crosswalk_engine import ForeignSocietyCrosswalkEngine
from XR7.services.metadata_repair_engine import MetadataRepairEngine
from XR7.services.split_rights_repair_engine import SplitRightsRepairEngine
from XR7.services.ugc_repair_engine import UGCRepairEngine

FORECAST_DISCLAIMER = (
    "Forecasted royalties are approximate estimates based on historical data, "
    "metadata quality, catalog repairs, platform seasonality, and machine learning models. "
    "Actual future earnings may vary due to market conditions, platform behavior, "
    "release schedules, and other external factors."
)


class PostRepairForecastPipeline:
    def __init__(self, db: Session):
        self.db = db

    def _cleaned_historical_rows(
        self,
        artist_id: str,
        start_date: datetime,
        end_date: datetime,
        historical_records: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        if historical_records is None:
            historical_records = EarningsEngine(RightsGraph()).reconstruct_historical(
                artist_id,
                start_date,
                end_date,
                self.db,
            )
        events = {
            str(e.id): e
            for e in self.db.query(Event)
            .filter(Event.artist_id == artist_id, Event.timestamp >= start_date, Event.timestamp <= end_date)
            .all()
        }

        rows: list[dict[str, Any]] = []
        for r in historical_records:
            e = events.get(str(r.get("event_id") or ""))
            rows.append(
                {
                    "event_id": r.get("event_id"),
                    "timestamp": r.get("timestamp"),
                    "net": float(r.get("net") or 0.0),
                    "event_type": str(getattr(e, "event_type", "STREAM")),
                    "work_id": str(getattr(e, "work_id", "") or ""),
                    "platform": getattr(e, "platform", None),
                    "territory": getattr(e, "territory", None),
                }
            )
        return rows

    def run(
        self,
        artist_id: str,
        start_date: datetime,
        end_date: datetime,
        historical_records: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        # Stage: post_repair_forecast_pipeline (after reconstruction + repair).
        metadata_engine = MetadataRepairEngine(self.db)
        metadata_health = metadata_engine.get_metadata_health(artist_id)
        repair_logs = metadata_engine.catalog_repairs(artist_id, limit=500)

        works = self.db.query(Work).filter(Work.artist_id == artist_id).all()
        unified_work_nodes = [{"id": w.id, "title": w.title, "isrc": w.isrc, "iswc": w.iswc} for w in works]

        rights_rows = [
            {
                "work_id": w.id,
                "territory": "GLOBAL",
                "platform": "ALL",
                "expected_split": 1.0,
                "estimated_value": 1000.0,
                "contributors": [{"name": "Primary Artist", "split": 1.0}],
                "pro_registered": bool(w.iswc),
                "pro": "ASCAP" if w.iswc else "",
                "publisher": "Independent",
                "societies": ["ASCAP"] if w.iswc else [],
            }
            for w in works
        ]
        payout_rows = [
            {
                "work_id": w.id,
                "territory": "GLOBAL",
                "platform": "ALL",
                "actual_split": 0.95,
            }
            for w in works
        ]
        split_repairs = SplitRightsRepairEngine().apply_high_confidence_repairs(
            artist_id,
            rights_rows,
            payout_rows,
            metadata_repairs=repair_logs,
        )

        events = (
            self.db.query(Event)
            .filter(Event.artist_id == artist_id, Event.timestamp >= start_date, Event.timestamp <= end_date)
            .all()
        )
        rate_report = RateBenchmarker().benchmark(
            artist_id,
            [
                {
                    "event_type": str(e.event_type),
                    "unit_value": float(e.unit_value or 0.0),
                    "quantity": float(e.quantity or 0.0),
                    "territory": e.territory,
                    "metadata_quality_score": metadata_health.get("consistency_score"),
                }
                for e in events
            ],
        ).to_dict()

        ugc_report = self._run_ugc_analysis_sync(artist_id)
        foreign_report = ForeignSocietyCrosswalkEngine(self.db).analyze(artist_id)

        cleaned_rows = self._cleaned_historical_rows(
            artist_id,
            start_date,
            end_date,
            historical_records=historical_records,
        )

        metadata_quality = float(metadata_health.get("consistency_score") or 0.5)
        split_factor = 1.0 + (float(split_repairs.corrections_applied) / max(float(split_repairs.mismatch_count or 1), 1.0)) * 0.08
        corrected_rate_events = float((rate_report.get("summary") or {}).get("events_below_p50") or 0.0)
        total_rate_events = max(float((rate_report.get("summary") or {}).get("total_events") or 1.0), 1.0)
        rate_factor = max(0.85, min(1.15, 1.0 - (corrected_rate_events / total_rate_events) * 0.1))
        ugc_mult = 1.0 + min(float(ugc_report.get("auto_claim_count") or 0.0) * 0.01, 0.18)
        foreign_lag_factor = 1.0 - min(len(foreign_report.findings) * 0.015, 0.12)

        base = PostRepairEarningsForecaster().forecast(
            cleaned_rows,
            metadata_quality=metadata_quality,
            split_correction_factor=split_factor,
            rate_correction_factor=rate_factor,
            ugc_virality_multiplier=ugc_mult,
            foreign_lag_factor=foreign_lag_factor,
            confidence_level=0.95,
        )

        leakage_predictor = FutureLeakagePredictor()
        leakage_rows = leakage_predictor.predict_per_work(
            unified_work_nodes,
            metadata_completeness=float(metadata_health.get("completeness_score") or 0.0),
            identifier_coverage=float((metadata_health.get("identifier_coverage") or {}).get("both_coverage") or 0.0),
            anomaly_density=float(len(events)) / max(float(len(unified_work_nodes) or 1), 1.0),
            payment_regularity=max(0.0, min(1.0, rate_factor)),
            catalog_age_years=4.0 if unified_work_nodes else 0.0,
            distributor_footprint=len({str(e.platform or "").strip().lower() for e in events if str(e.platform or "").strip()}),
        )
        avg_risk = 0.0
        if leakage_rows:
            avg_risk = sum(float(r.probability) for r in leakage_rows) / len(leakage_rows)
        repair_uplift = min(float(metadata_health.get("projected_leakage_avoided") or 0.0) / 100000.0, 0.2)
        risk_penalty = min(avg_risk * 0.12, 0.18)
        adjust_factor = max(0.75, min(1.25, 1.0 - risk_penalty + repair_uplift))

        for horizon in ("30", "60", "90", "180"):
            if horizon not in base.get("horizons", {}):
                continue
            row = base["horizons"][horizon]
            row["expected"] = round(float(row.get("expected") or 0.0) * adjust_factor, 2)
            row["low"] = round(float(row.get("low") or 0.0) * adjust_factor, 2)
            row["high"] = round(float(row.get("high") or 0.0) * adjust_factor, 2)
            if isinstance(row.get("confidence_interval"), dict):
                row["confidence_interval"]["low"] = row["low"]
                row["confidence_interval"]["high"] = row["high"]

        base["predicted_total_next_90_days"] = float((base.get("horizons") or {}).get("90", {}).get("expected") or 0.0)
        base["predicted_low"] = float((base.get("horizons") or {}).get("90", {}).get("low") or 0.0)
        base["predicted_high"] = float((base.get("horizons") or {}).get("90", {}).get("high") or 0.0)
        base["forecast_adjusted_for_repairs"] = True
        base["leakage_avoided_metrics"] = {
            "projected_leakage_avoided": float(metadata_health.get("projected_leakage_avoided") or 0.0),
            "adjustment_factor": round(float(adjust_factor), 4),
            "risk_penalty": round(float(risk_penalty), 4),
            "repair_uplift": round(float(repair_uplift), 4),
        }

        return {
            "stage": "post_repair_forecast_pipeline",
            "inputs": {
                "cleaned_historical_earnings_count": len(cleaned_rows),
                "repaired_metadata": {
                    "issues_auto_repaired": metadata_health.get("issues_auto_repaired"),
                    "identifier_coverage": metadata_health.get("identifier_coverage"),
                },
                "unified_work_nodes": len(unified_work_nodes),
                "corrected_splits": {
                    "mismatch_count": split_repairs.mismatch_count,
                    "corrections_applied": split_repairs.corrections_applied,
                },
                "corrected_rate_benchmarks": rate_report.get("summary") or {},
                "ugc_monetization_signals": {
                    "auto_claim_count": ugc_report.get("auto_claim_count"),
                    "finding_count": len(ugc_report.get("findings") or []),
                },
                "foreign_royalty_crosswalks": {
                    "finding_count": len(foreign_report.findings),
                    "registration_packet_count": len(foreign_report.registration_packets),
                },
            },
            "forecast": {
                "horizons": base.get("horizons", {}),
                "predicted_total_next_90_days": base.get("predicted_total_next_90_days"),
                "predicted_low": base.get("predicted_low"),
                "predicted_high": base.get("predicted_high"),
                "confidence_band": base.get("confidence_band"),
                "trend_indicator": base.get("trend_indicator"),
                "per_work_forecast": base.get("per_work_forecast", []),
                "per_stream_forecast": base.get("per_revenue_stream_forecast", {}),
                "forecast_adjusted_for_repairs": base.get("forecast_adjusted_for_repairs", False),
                "leakage_avoided_metrics": base.get("leakage_avoided_metrics", {}),
                "confidence_intervals": {
                    horizon: (base.get("horizons", {}).get(horizon, {}).get("confidence_interval") or {})
                    for horizon in ("30", "60", "90", "180")
                },
            },
            "forecast_disclaimer": FORECAST_DISCLAIMER,
            "metadata": {
                "forecast_disclaimer": FORECAST_DISCLAIMER,
                "model": (base.get("model_metadata") or {}).get("model_name", "PostRepairEarningsForecaster"),
            },
        }

    @staticmethod
    def _run_ugc_analysis_sync(artist_id: str) -> dict[str, Any]:
        """Run async UGC analysis from both sync and async call sites safely."""
        coro = UGCRepairEngine().analyze(artist_id)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)

        # We are already inside an event loop (e.g. FastAPI thread worker calling
        # async orchestration). Run in an isolated thread with its own loop.
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(lambda: asyncio.run(coro)).result()
