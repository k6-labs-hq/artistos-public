import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from arcos7.models.artist import Artist, ArtistCreate, ArtistSchema
from arcos7.models.anomaly import Anomaly
from arcos7.models.base import get_db
from arcos7.models.claim import Claim
from arcos7.models.payment import Payment
from arcos7.models.event import Event
from arcos7.models.contract import Contract
from arcos7.graph.rights_graph import RightsGraph
from arcos7.earnings.engine import EarningsEngine

router = APIRouter(prefix="/artists", tags=["artists"])


@router.get("/{artist_id}", response_model=ArtistSchema)
def get_artist(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@router.post("/", response_model=ArtistSchema, status_code=201)
def create_artist(artist_in: ArtistCreate, db: Session = Depends(get_db)):
    artist = Artist(
        id=str(uuid.uuid4()),
        name=artist_in.name,
        ipi_number=artist_in.ipi_number,
        stage_names=artist_in.stage_names,
        created_at=datetime.utcnow(),
    )
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist


@router.post("/{artist_id}/connect")
def connect_artist(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return {"status": "scheduled", "artist_id": artist_id, "message": "Historical ingestion job queued."}


@router.get("/{artist_id}/summary")
def artist_summary(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    rg = RightsGraph()
    engine = EarningsEngine(rg)
    summary = engine.get_earnings_summary(artist_id, db)
    anomaly_count = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).count()
    claim_count = db.query(Claim).filter(Claim.artist_id == artist_id).count()
    return {
        **summary,
        "anomaly_count": anomaly_count,
        "claim_count": claim_count,
    }
