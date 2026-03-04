import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from arcos7.models.artist import Artist, ArtistCreate, ArtistSchema
from arcos7.models.anomaly import Anomaly
from arcos7.models.base import get_db
from arcos7.models.claim import Claim
from arcos7.models.payment import Payment
from arcos7.models.event import Event
from arcos7.models.work import Work
from arcos7.models.contract import Contract
from arcos7.graph.rights_graph import RightsGraph
from arcos7.earnings.engine import EarningsEngine
from arcos7.ml.catalog_scorer import CatalogScorer

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
        created_at=datetime.now(timezone.utc),
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


@router.get("/{artist_id}/ml/catalog-health")
def catalog_health(artist_id: str, db: Session = Depends(get_db)):
    """
    Return an ML-derived catalog health score (0–100) and grade for the artist.

    Combines metadata completeness, payment regularity, anomaly density,
    recovery rate, and earnings accuracy into a single composite score.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    works = [
        {"id": w.id, "isrc": w.isrc, "iswc": w.iswc}
        for w in db.query(Work).filter(Work.artist_id == artist_id).all()
    ]
    payments = [
        {"id": p.id, "amount": p.amount, "currency": p.currency, "received_at": p.received_at.isoformat()}
        for p in db.query(Payment).filter(Payment.artist_id == artist_id).all()
    ]
    anomalies = [
        {"id": a.id, "status": a.status}
        for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    ]
    claims = [
        {"id": c.id, "status": c.status, "recovered_amount": c.recovered_amount}
        for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()
    ]
    rg = RightsGraph()
    engine = EarningsEngine(rg)
    earnings_summary = engine.get_earnings_summary(artist_id, db)

    scorer = CatalogScorer()
    report = scorer.score(
        artist_id=artist_id,
        works=works,
        payments=payments,
        anomalies=anomalies,
        claims=claims,
        earnings_summary=earnings_summary,
    )
    return report.to_dict()
