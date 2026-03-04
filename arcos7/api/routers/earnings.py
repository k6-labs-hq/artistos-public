from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from arcos7.earnings.engine import EarningsEngine
from arcos7.graph.rights_graph import RightsGraph
from arcos7.models.artist import Artist
from arcos7.models.base import get_db

router = APIRouter(tags=["earnings"])


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
    start = datetime(2000, 1, 1)
    end = datetime.now(timezone.utc)
    return engine.reconstruct_historical(artist_id, start, end, db)


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
