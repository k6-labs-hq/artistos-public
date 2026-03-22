from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.api.routers.auth import require_artist_access
from XR7.ml.sovereignty_suite_v2 import explain_artist_ml_suite
from XR7.ml.success_probability_calibrator import SuccessProbabilityCalibrator
from XR7.ml.predictive_recoverable import PredictiveRecoverableModel
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["ml_suite"])


# ---------------------------------------------------------------------------
# Predictive Recoverable — schemas
# ---------------------------------------------------------------------------

_ALLOWED_HORIZONS = {6, 12, 24, 36, 60}


class PredictRecoverableRequest(BaseModel):
    horizon_months: int = Field(
        ...,
        description="Forecast horizon in months. Allowed: 6, 12, 24, 36, 60",
    )


class PredictRecoverableResponse(BaseModel):
    artist_id: str
    horizon_months: int
    low_usd: float
    mid_usd: float
    high_usd: float
    confidence: float = Field(..., ge=0.0, le=1.0)
    key_drivers: list[str]


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/artists/{artist_id}/ml/predict-recoverable",
    response_model=PredictRecoverableResponse,
    summary="Ensemble prediction of total recoverable value over a time horizon",
)
def predict_recoverable(
    artist_id: str,
    body: PredictRecoverableRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> PredictRecoverableResponse:
    """
    Returns low / mid / high total recoverable USD estimates with a confidence
    score and human-readable key drivers.  Uses an ensemble of:

    - Deterministic earnings growth forecaster (DeterministicGrowthV1)
    - Bayesian posterior success rate from historical claim outcomes
    - SOL decay curve for open anomalies near their deadline windows
    - Active claim pipeline multiplier
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    if body.horizon_months not in _ALLOWED_HORIZONS:
        raise HTTPException(
            status_code=422,
            detail=f"horizon_months must be one of {sorted(_ALLOWED_HORIZONS)}",
        )

    model = PredictiveRecoverableModel()
    result = model.predict(
        artist_id=artist_id,
        horizon_months=body.horizon_months,
        db=db,
    )

    return PredictRecoverableResponse(
        artist_id=artist_id,
        horizon_months=result["horizon_months"],
        low_usd=result["low_usd"],
        mid_usd=result["mid_usd"],
        high_usd=result["high_usd"],
        confidence=result["confidence"],
        key_drivers=result["key_drivers"],
    )


@router.get("/artists/{artist_id}/ml/explain")
def ml_explain(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    payload = explain_artist_ml_suite(db, artist_id)
    return inject_branding_metadata(db, payload)


@router.get("/artists/{artist_id}/ml/calibration-dashboard")
def ml_calibration_dashboard(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    summary = SuccessProbabilityCalibrator().calibration_summary(artist_id, db)
    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "calibration": summary,
        "dashboard": {
            "status": "healthy" if float(summary.get("avg_posterior_success_rate") or 0.0) >= 0.55 else "watch",
            "recommended_actions": [
                "Feed new claim outcomes to keep posterior rates calibrated.",
                "Review low-confidence categories in analyst queue.",
                "Compare forecast confidence bands against realized deposits monthly.",
            ],
        },
    })
