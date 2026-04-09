from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly, AnomalyStatus
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.metadata_issue import MetadataIssue
from XR7.models.work import Work


@dataclass
class RecoverableValuePredictor:
    model_version: str = "RecoverableValuePredictor-v2"

    def predict(
        self, *, open_recoverable: float, open_claims: int, metadata_backlog: int
    ) -> dict[str, float]:
        base = max(open_recoverable, 0.0)
        uplift = 1.0 + min(0.35, (open_claims * 0.015) + (metadata_backlog * 0.01))
        forecast = round(base * uplift, 2)
        return {
            "predicted_recoverable_90d": forecast,
            "predicted_recoverable_low": round(forecast * 0.72, 2),
            "predicted_recoverable_high": round(forecast * 1.2, 2),
        }


@dataclass
class PayerBehaviorPredictor:
    model_version: str = "PayerBehaviorPredictor-v2"

    def predict(
        self, *, active_claims: int, in_review_claims: int, paid_claims: int
    ) -> dict[str, float | str]:
        denominator = max(active_claims + paid_claims, 1)
        responsiveness = max(0.05, min(0.95, (paid_claims + 0.5) / denominator))
        resistance = round(1.0 - responsiveness, 4)
        return {
            "predicted_responsiveness": round(responsiveness, 4),
            "predicted_escalation_resistance": resistance,
            "suggested_posture": (
                "cooperative"
                if responsiveness >= 0.65
                else "neutral" if responsiveness >= 0.4 else "resistant"
            ),
            "in_review_claim_pressure": round(
                min(1.0, in_review_claims / max(active_claims, 1)), 4
            ),
        }


@dataclass
class MetadataDriftPredictor:
    model_version: str = "MetadataDriftPredictor-v2"

    def predict(self, *, total_works: int, open_issues: int) -> dict[str, float | str]:
        if total_works <= 0:
            return {
                "drift_risk_score": 0.0,
                "drift_grade": "LOW",
            }
        ratio = max(0.0, min(1.0, open_issues / total_works))
        grade = "LOW" if ratio < 0.15 else "MEDIUM" if ratio < 0.35 else "HIGH"
        return {
            "drift_risk_score": round(ratio, 4),
            "drift_grade": grade,
        }


@dataclass
class FutureLeakagePredictor2:
    model_version: str = "FutureLeakagePredictor2-v2"

    def predict(
        self, *, open_recoverable: float, drift_risk_score: float, active_claims: int
    ) -> dict[str, float]:
        leakage_base = max(open_recoverable * 0.25, 0.0)
        risk_multiplier = 1.0 + min(1.0, max(0.0, drift_risk_score))
        operations_multiplier = 1.0 + min(0.5, active_claims * 0.03)
        predicted = round(leakage_base * risk_multiplier * operations_multiplier, 2)
        return {
            "predicted_future_leakage_180d": predicted,
            "predicted_future_leakage_low": round(predicted * 0.7, 2),
            "predicted_future_leakage_high": round(predicted * 1.3, 2),
        }


def explain_artist_ml_suite(db: Session, artist_id: str) -> dict[str, Any]:
    anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    issues = db.query(MetadataIssue).filter(MetadataIssue.artist_id == artist_id).all()
    works = db.query(Work).filter(Work.artist_id == artist_id).all()

    open_anomalies = [a for a in anomalies if str(a.status) == AnomalyStatus.OPEN.value]
    open_recoverable = sum(float(a.estimated_recoverable or 0.0) for a in open_anomalies)

    active_claims = [
        c for c in claims if str(c.status) not in {ClaimStatus.PAID.value, ClaimStatus.CLOSED.value}
    ]
    in_review_claims = [c for c in active_claims if str(c.status) == ClaimStatus.IN_REVIEW.value]
    paid_claims = [c for c in claims if str(c.status) == ClaimStatus.PAID.value]

    open_issues = [
        i for i in issues if str(i.repair_status).upper() not in {"REPAIRED", "AUTO_REPAIRED"}
    ]

    recoverable_model = RecoverableValuePredictor()
    payer_model = PayerBehaviorPredictor()
    drift_model = MetadataDriftPredictor()
    leakage_model = FutureLeakagePredictor2()

    recoverable_pred = recoverable_model.predict(
        open_recoverable=open_recoverable,
        open_claims=len(active_claims),
        metadata_backlog=len(open_issues),
    )
    payer_pred = payer_model.predict(
        active_claims=len(active_claims),
        in_review_claims=len(in_review_claims),
        paid_claims=len(paid_claims),
    )
    drift_pred = drift_model.predict(
        total_works=len(works),
        open_issues=len(open_issues),
    )
    leakage_pred = leakage_model.predict(
        open_recoverable=open_recoverable,
        drift_risk_score=float(drift_pred["drift_risk_score"]),
        active_claims=len(active_claims),
    )

    return {
        "artist_id": artist_id,
        "model_versions": {
            "recoverable_value": recoverable_model.model_version,
            "payer_behavior": payer_model.model_version,
            "metadata_drift": drift_model.model_version,
            "future_leakage": leakage_model.model_version,
        },
        "inputs": {
            "open_anomaly_count": len(open_anomalies),
            "open_recoverable": round(open_recoverable, 2),
            "active_claim_count": len(active_claims),
            "in_review_claim_count": len(in_review_claims),
            "paid_claim_count": len(paid_claims),
            "metadata_backlog_count": len(open_issues),
            "catalog_work_count": len(works),
        },
        "outputs": {
            "recoverable_value": recoverable_pred,
            "payer_behavior": payer_pred,
            "metadata_drift": drift_pred,
            "future_leakage": leakage_pred,
        },
        "explanation": {
            "method": "deterministic feature-based risk forecasting",
            "notes": [
                "Predictions are guidance and not legal or financial guarantees.",
                "Model scores are constrained to transparent deterministic transformations for auditability.",
                "Calibration should be interpreted alongside realized outcomes and claim lifecycle changes.",
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
    }
