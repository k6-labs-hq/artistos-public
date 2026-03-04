from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from arcos7.earnings.engine import EarningsEngine
from arcos7.graph.rights_graph import RightsGraph
from arcos7.ml.forecaster import EarningsForecaster
from arcos7.models.artist import Artist
from arcos7.models.base import get_db

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
    return {"artist_id": artist_id, "records": results}


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

