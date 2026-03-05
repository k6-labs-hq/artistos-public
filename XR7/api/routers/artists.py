import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.models.artist import Artist, ArtistCreate, ArtistSchema
from XR7.models.anomaly import Anomaly
from XR7.models.base import get_db
from XR7.models.claim import Claim
from XR7.models.payment import Payment
from XR7.models.event import Event
from XR7.models.work import Work
from XR7.models.contract import Contract
from XR7.graph.rights_graph import RightsGraph
from XR7.earnings.engine import EarningsEngine
from XR7.ml.catalog_scorer import CatalogScorer

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
    """
    Check which data connectors are configured for this artist and return
    their credential status.

    This endpoint validates that the required environment variables are set
    for each connector.  It does NOT make real API calls — it only confirms
    that the credentials are present and the connector is ready to use.

    For connectors that are not yet configured, use the statement file upload
    workflow: POST /artists/{artist_id}/statements/upload
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    from XR7.ingestion.connectors.pro import PROConnector
    from XR7.ingestion.connectors.dsp import DSPConnector
    from XR7.ingestion.connectors.platform import PlatformConnector
    from XR7.ingestion.connectors.ticketing import TicketingConnector
    from XR7.ingestion.connectors.mlc import MLCConnector
    from XR7.ingestion.connectors.international_pro import (
        APRAAMCOSConnector,
        JASRACConnector,
        KOMCAConnector,
        SACEMConnector,
    )

    def _check(connector_cls, name: str, **kwargs) -> dict:
        try:
            c = connector_cls(config={}, **kwargs)
            ok = c.connect()
            return {"source": name, "configured": ok,
                    "status": "ready" if ok else "missing_credentials"}
        except Exception as exc:  # noqa: BLE001
            return {"source": name, "configured": False, "status": f"error: {exc}"}

    sources = (
        [_check(PROConnector, pro, pro_name=pro) for pro in ("ASCAP", "BMI", "SESAC")]
        + [_check(DSPConnector, dsp, dsp_name=dsp) for dsp in ("Spotify", "Apple Music")]
        + [_check(PlatformConnector, p, platform_name=p) for p in ("YouTube", "TikTok")]
        + [_check(TicketingConnector, t, platform_name=t) for t in ("Ticketmaster", "AXS")]
        + [_check(APRAAMCOSConnector, "APRA AMCOS")]
        + [_check(JASRACConnector, "JASRAC")]
        + [_check(KOMCAConnector, "KOMCA")]
        + [_check(SACEMConnector, "SACEM")]
        + [_check(MLCConnector, "MLC")]
    )

    configured_count = sum(1 for s in sources if s["configured"])
    return {
        "artist_id": artist_id,
        "status": "ready" if configured_count > 0 else "no_connectors_configured",
        "configured_sources": configured_count,
        "total_sources": len(sources),
        "sources": sources,
        "next_steps": (
            "Configure connector credentials via environment variables (see .env.example), "
            "then call this endpoint again.  Alternatively, upload royalty statement CSV files "
            "directly at POST /artists/{artist_id}/statements/upload — no API keys required."
            if configured_count == 0
            else "Use POST /artists/{artist_id}/statements/upload to ingest data from configured sources."
        ),
    }


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
