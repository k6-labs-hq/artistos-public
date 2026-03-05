from __future__ import annotations

from sqlalchemy.orm import Session

from arcos7.models.anomaly import Anomaly
from arcos7.models.claim import Claim
from arcos7.models.recovery_intelligence import FeedbackOutcome, RecoveryOutcomeFeedback


class SuccessProbabilityCalibrator:
    """Calibrate model confidence using historical recovery outcomes."""

    # Beta prior keeps estimates stable for low sample sizes.
    _ALPHA_PRIOR = 2.0
    _BETA_PRIOR = 2.0
    _MIN_SCOPE_SAMPLES = 3

    def posterior_success_rate(self, artist_id: str, db: Session) -> tuple[float, int]:
        feedback_rows = (
            db.query(RecoveryOutcomeFeedback)
            .filter(RecoveryOutcomeFeedback.artist_id == artist_id)
            .all()
        )
        return self._posterior_from_rows(feedback_rows)

    def _posterior_from_rows(self, feedback_rows: list[RecoveryOutcomeFeedback]) -> tuple[float, int]:
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
        claim_subtype = {
            c.id: (anomaly_subtype.get(c.anomaly_id) or c.claim_type)
            for c in claims
        }
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
        rows_by_subtype, all_rows = self._feedback_rows_by_subtype(artist_id, db)
        overall_rate, overall_samples = self._posterior_from_rows(all_rows)

        by_subtype = {}
        for subtype, rows in rows_by_subtype.items():
            rate, sample_count = self._posterior_from_rows(rows)
            by_subtype[subtype] = {
                "posterior_success_rate": round(rate, 6),
                "sample_count": sample_count,
                "sufficient_samples": sample_count >= self._MIN_SCOPE_SAMPLES,
            }

        return {
            "overall": {
                "posterior_success_rate": round(overall_rate, 6),
                "sample_count": overall_samples,
                "sufficient_samples": overall_samples >= self._MIN_SCOPE_SAMPLES,
            },
            "by_subtype": by_subtype,
            "minimum_scope_samples": self._MIN_SCOPE_SAMPLES,
            "method": "beta_posterior_blend",
        }

    def calibrate_items(self, artist_id: str, items: list[dict], db: Session) -> list[dict]:
        rows_by_subtype, all_rows = self._feedback_rows_by_subtype(artist_id, db)
        global_rate, global_samples = self._posterior_from_rows(all_rows)
        calibrated: list[dict] = []

        for item in items:
            base_prob = float(item.get("success_probability", item.get("confidence_score", 0.5)) or 0.5)

            subtype = item.get("subtype")
            if subtype and subtype in rows_by_subtype:
                scope_rate, scope_samples = self._posterior_from_rows(rows_by_subtype[subtype])
                scope = f"subtype:{subtype}"
            else:
                scope_rate, scope_samples = global_rate, global_samples
                scope = "global"

            # Blend only when enough scoped observations exist.
            if scope_samples >= self._MIN_SCOPE_SAMPLES:
                calibrated_prob = 0.6 * base_prob + 0.4 * scope_rate
            else:
                # Scoped samples are thin: back off to base probability.
                calibrated_prob = base_prob

            calibrated.append(
                {
                    **item,
                    "base_success_probability": round(base_prob, 6),
                    "calibrated_success_probability": round(calibrated_prob, 6),
                    "calibration": {
                        "posterior_success_rate": round(scope_rate, 6),
                        "sample_count": scope_samples,
                        "scope": scope,
                        "sufficient_samples": scope_samples >= self._MIN_SCOPE_SAMPLES,
                        "fallback_global_posterior": round(global_rate, 6),
                        "global_sample_count": global_samples,
                        "method": "beta_posterior_blend",
                    },
                }
            )

        return calibrated
