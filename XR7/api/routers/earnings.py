from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.earnings.engine import EarningsEngine
from XR7.graph.rights_graph import RightsGraph
from XR7.ml.forecaster import EarningsForecaster
from XR7.ml.rate_benchmarker import RateBenchmarker
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.event import Event
from XR7.services.metadata_repair_engine import MetadataRepairEngine

router = APIRouter(tags=["earnings"])

# Earliest date used when reconstructing the full available earnings history.
# This pre-dates modern digital music distribution and acts as a catch-all floor.
_DEFAULT_HISTORICAL_START_DATE = datetime(2000, 1, 1)


def get_engine():
    rg = RightsGraph()
    return EarningsEngine(rg)


@router.get("/artists/{artist_id}/earnings")
def get_earnings_summary(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    engine = get_engine()
    return engine.get_earnings_summary(artist_id, db)


@router.get("/artists/{artist_id}/earnings/history")
def get_earnings_history(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    engine = get_engine()
    end = datetime.now(timezone.utc)
    return engine.reconstruct_historical(artist_id, _DEFAULT_HISTORICAL_START_DATE, end, db)


class ReconstructRequest(BaseModel):
    start_date: datetime
    end_date: datetime


@router.post("/artists/{artist_id}/earnings/reconstruct")
def reconstruct_earnings(artist_id: str, body: ReconstructRequest, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    engine = get_engine()
    results = engine.reconstruct_historical(artist_id, body.start_date, body.end_date, db)

    metadata_engine = MetadataRepairEngine(db)
    metadata_audit = metadata_engine.run_historical_audit_and_repair(
        artist_id,
        body.start_date,
        body.end_date,
    )
    metadata_health = metadata_engine.get_metadata_health(artist_id)

    events = (
        db.query(Event)
        .filter(
            Event.artist_id == artist_id,
            Event.timestamp >= body.start_date,
            Event.timestamp <= body.end_date,
        )
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
    rate_report["metadata_health_context"] = {
        "consistency_score": metadata_health.get("consistency_score"),
        "identifier_coverage": metadata_health.get("identifier_coverage"),
    }

    return {
        "artist_id": artist_id,
        "records": results,
        "metadata_audit": {
            "issues_found": metadata_audit.issues_found,
            "issues_auto_repaired": metadata_audit.auto_repaired,
            "issues_requiring_review": metadata_audit.requires_review,
            "projected_leakage_avoided": metadata_audit.projected_leakage_avoided,
            "catalog_graph_version": metadata_audit.graph_version,
            "metadata_health": metadata_health,
        },
        "rate_benchmark": rate_report,
    }


class ForecastRequest(BaseModel):
    horizon_days: int = 90
    confidence: float = 0.95
    by_category: bool = False


@router.post("/artists/{artist_id}/ml/forecast")
def forecast_earnings(artist_id: str, body: ForecastRequest, db: Session = Depends(get_db)):
    """
    Use a linear-regression trend model to forecast the artist's earnings for
    the next *horizon_days* days.

    Set ``by_category=true`` to receive a per-event-type breakdown.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    engine = get_engine()
    end = datetime.now(timezone.utc)
    historical = engine.reconstruct_historical(artist_id, _DEFAULT_HISTORICAL_START_DATE, end, db)

    forecaster = EarningsForecaster()
    if body.by_category:
        result = forecaster.forecast_by_category(
            historical, horizon_days=body.horizon_days, confidence=body.confidence
        )
    else:
        result = forecaster.forecast(
            historical, horizon_days=body.horizon_days, confidence=body.confidence
        )
    return {"artist_id": artist_id, "forecast": result}

