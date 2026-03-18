from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.api.routers.auth import require_artist_access
from XR7.ml.sovereignty_suite_v2 import explain_artist_ml_suite
from XR7.ml.success_probability_calibrator import SuccessProbabilityCalibrator
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["ml_suite"])


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
