from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly
from XR7.models.claim import Claim
from XR7.models.ml_feedback import CalibrationSnapshot
from XR7.models.recovery_intelligence import FeedbackOutcome, RecoveryOutcomeFeedback
from XR7.services.ml_feedback import aggregate_feedback_and_update_calibration


class SuccessProbabilityCalibrator:
    """Calibrate model confidence using feedback snapshots and historical outcomes."""

    _ALPHA_PRIOR = 2.0
    _BETA_PRIOR = 2.0
    _MIN_SCOPE_SAMPLES = 3

    def _snapshot_map(
        self, artist_id: str, db: Session
    ) -> dict[tuple[str, str], CalibrationSnapshot]:
        rows = (
            db.query(CalibrationSnapshot).filter(CalibrationSnapshot.artist_id == artist_id).all()
        )
        return {(str(r.scope_type), str(r.scope_key)): r for r in rows}

    def posterior_success_rate(self, artist_id: str, db: Session) -> tuple[float, int]:
        aggregate_feedback_and_update_calibration(artist_id, db)
        snap = self._snapshot_map(artist_id, db).get(("overall", "overall"))
        if snap:
            return float(snap.posterior_mean), int(snap.sample_count)

        feedback_rows = (
            db.query(RecoveryOutcomeFeedback)
            .filter(RecoveryOutcomeFeedback.artist_id == artist_id)
            .all()
        )
        return self._posterior_from_rows(feedback_rows)

    def _posterior_from_rows(
        self, feedback_rows: list[RecoveryOutcomeFeedback]
    ) -> tuple[float, int]:
        successes = 0
        failures = 0
        for row in feedback_rows:
            if row.outcome in (FeedbackOutcome.RECOVERED, FeedbackOutcome.SETTLED):
                successes += 1
            elif row.outcome == FeedbackOutcome.DISMISSED:
                failures += 1

        posterior = (self._ALPHA_PRIOR + successes) / (
            self._ALPHA_PRIOR + self._BETA_PRIOR + successes + failures
        )
        return float(posterior), successes + failures

    def _subtype_map(self, artist_id: str, db: Session) -> tuple[dict[str, str], dict[str, str]]:
        anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
        anomaly_subtype = {a.id: a.subtype for a in anomalies}
        claim_subtype = {c.id: (anomaly_subtype.get(c.anomaly_id) or c.claim_type) for c in claims}
        return anomaly_subtype, claim_subtype

    def _feedback_rows_by_subtype(
        self,
        artist_id: str,
        db: Session,
    ) -> tuple[dict[str, list[RecoveryOutcomeFeedback]], list[RecoveryOutcomeFeedback]]:
        rows = (
            db.query(RecoveryOutcomeFeedback)
            .filter(RecoveryOutcomeFeedback.artist_id == artist_id)
            .all()
        )
        anomaly_subtype, claim_subtype = self._subtype_map(artist_id, db)

        grouped: dict[str, list[RecoveryOutcomeFeedback]] = {}
        for row in rows:
            subtype = None
            if row.anomaly_id:
                subtype = anomaly_subtype.get(row.anomaly_id)
            if subtype is None and row.claim_id:
                subtype = claim_subtype.get(row.claim_id)
            if subtype is None:
                continue
            grouped.setdefault(str(subtype), []).append(row)
        return grouped, rows

    def calibration_summary(self, artist_id: str, db: Session) -> dict:
        aggregate_feedback_and_update_calibration(artist_id, db)
        snapshot_map = self._snapshot_map(artist_id, db)
        overall_snapshot = snapshot_map.get(("overall", "overall"))

        if overall_snapshot:
            overall = {
                "posterior_success_rate": round(float(overall_snapshot.posterior_mean), 6),
                "sample_count": int(overall_snapshot.sample_count),
                "sufficient_samples": int(overall_snapshot.sample_count) >= self._MIN_SCOPE_SAMPLES,
                "credible_interval": [
                    round(float(overall_snapshot.lower_credible), 6),
                    round(float(overall_snapshot.upper_credible), 6),
                ],
                "alpha": round(float(overall_snapshot.alpha), 4),
                "beta": round(float(overall_snapshot.beta), 4),
                "last_updated_at": (
                    overall_snapshot.last_updated_at.isoformat()
                    if overall_snapshot.last_updated_at
                    else None
                ),
            }
        else:
            rows_by_subtype, all_rows = self._feedback_rows_by_subtype(artist_id, db)
            overall_rate, overall_samples = self._posterior_from_rows(all_rows)
            _ = rows_by_subtype
            overall = {
                "posterior_success_rate": round(overall_rate, 6),
                "sample_count": overall_samples,
                "sufficient_samples": overall_samples >= self._MIN_SCOPE_SAMPLES,
                "credible_interval": [0.0, 1.0],
                "alpha": self._ALPHA_PRIOR,
                "beta": self._BETA_PRIOR,
                "last_updated_at": datetime.now(timezone.utc).isoformat(),
            }

        def _scope(scope_type: str) -> dict[str, dict]:
            output: dict[str, dict] = {}
            for (stype, skey), row in snapshot_map.items():
                if stype != scope_type:
                    continue
                output[skey] = {
                    "posterior_success_rate": round(float(row.posterior_mean), 6),
                    "sample_count": int(row.sample_count),
                    "sufficient_samples": int(row.sample_count) >= self._MIN_SCOPE_SAMPLES,
                    "credible_interval": [
                        round(float(row.lower_credible), 6),
                        round(float(row.upper_credible), 6),
                    ],
                    "alpha": round(float(row.alpha), 4),
                    "beta": round(float(row.beta), 4),
                    "last_updated_at": (
                        row.last_updated_at.isoformat() if row.last_updated_at else None
                    ),
                }
            return output

        return {
            "overall": overall,
            "by_subtype": _scope("subtype"),
            "by_category": _scope("category"),
            "by_segment": _scope("segment"),
            "minimum_scope_samples": self._MIN_SCOPE_SAMPLES,
            "method": "beta_binomial_posterior_with_credible_intervals",
        }

    def calibrate_items(self, artist_id: str, items: list[dict], db: Session) -> list[dict]:
        aggregate_feedback_and_update_calibration(artist_id, db)
        snapshots = self._snapshot_map(artist_id, db)
        overall = snapshots.get(("overall", "overall"))
        global_rate = float(overall.posterior_mean) if overall else 0.5
        global_samples = int(overall.sample_count) if overall else 0
        calibrated: list[dict] = []

        for item in items:
            base_prob = float(
                item.get("success_probability", item.get("confidence_score", 0.5)) or 0.5
            )

            subtype = str(item.get("subtype") or "")
            category = str(item.get("category") or "")
            segment = str(item.get("artist_profile_segment") or item.get("segment") or "")

            if subtype and ("subtype", subtype) in snapshots:
                scope_row = snapshots[("subtype", subtype)]
                scope_rate, scope_samples = float(scope_row.posterior_mean), int(
                    scope_row.sample_count
                )
                scope_interval = [float(scope_row.lower_credible), float(scope_row.upper_credible)]
                scope = f"subtype:{subtype}"
            elif category and ("category", category) in snapshots:
                scope_row = snapshots[("category", category)]
                scope_rate, scope_samples = float(scope_row.posterior_mean), int(
                    scope_row.sample_count
                )
                scope_interval = [float(scope_row.lower_credible), float(scope_row.upper_credible)]
                scope = f"category:{category}"
            elif segment and ("segment", segment) in snapshots:
                scope_row = snapshots[("segment", segment)]
                scope_rate, scope_samples = float(scope_row.posterior_mean), int(
                    scope_row.sample_count
                )
                scope_interval = [float(scope_row.lower_credible), float(scope_row.upper_credible)]
                scope = f"segment:{segment}"
            else:
                scope_rate, scope_samples = global_rate, global_samples
                scope_interval = (
                    [0.0, 1.0]
                    if not overall
                    else [float(overall.lower_credible), float(overall.upper_credible)]
                )
                scope = "global"

            if scope_samples >= self._MIN_SCOPE_SAMPLES:
                calibrated_prob = 0.6 * base_prob + 0.4 * scope_rate
            else:
                calibrated_prob = base_prob

            calibrated.append(
                {
                    **item,
                    "base_success_probability": round(base_prob, 6),
                    "calibrated_success_probability": round(calibrated_prob, 6),
                    "calibration": {
                        "posterior_success_rate": round(scope_rate, 6),
                        "sample_count": scope_samples,
                        "credible_interval": [
                            round(scope_interval[0], 6),
                            round(scope_interval[1], 6),
                        ],
                        "scope": scope,
                        "sufficient_samples": scope_samples >= self._MIN_SCOPE_SAMPLES,
                        "fallback_global_posterior": round(global_rate, 6),
                        "global_sample_count": global_samples,
                        "method": "beta_binomial_posterior_blend",
                    },
                }
            )

        return calibrated
