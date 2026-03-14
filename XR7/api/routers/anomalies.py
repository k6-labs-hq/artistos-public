from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.anomaly.engine import AnomalyEngine
from XR7.earnings.engine import EarningsEngine
from XR7.graph.rights_graph import RightsGraph
from XR7.models.anomaly import Anomaly, AnomalySchema
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.review_queue import ReviewSourceType
from XR7.recovery.payer_behavior_model import payer_behavior_profile
from XR7.recovery.recovery_probability_model import anomaly_recovery_probability
from XR7.services.review_queue import enqueue_review_item
from XR7.tasks.hubspot import hubspot_sync_recovery_update

router = APIRouter(tags=["anomalies"])


@router.get("/artists/{artist_id}/anomalies")
def list_anomalies(
    artist_id: str,
    status: str | None = None,
    debug: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(Anomaly).filter(Anomaly.artist_id == artist_id)
    if status:
        query = query.filter(Anomaly.status == status)
    rows = query.all()

    payload = []
    for r in rows:
        obj = {
            **AnomalySchema.model_validate(r).model_dump(mode="json"),
            "recovery_probability": anomaly_recovery_probability(
                {
                    "estimated_recoverable": r.estimated_recoverable,
                    "confidence_score": r.confidence_score,
                    "severity": str(r.severity),
                }
            ),
        }
        if debug:
            obj.update(
                {
                    "anomaly_score": r.anomaly_score,
                    "model_version": r.model_version,
                    "feature_snapshot": r.feature_snapshot,
                }
            )
        payload.append(obj)
    return payload


@router.get("/anomalies/{anomaly_id}", response_model=AnomalySchema)
def get_anomaly(anomaly_id: str, db: Session = Depends(get_db)):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    return anomaly


@router.get("/anomalies/{anomaly_id}/recovery-probability")
def anomaly_recovery_probability_endpoint(anomaly_id: str, db: Session = Depends(get_db)):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    behavior = payer_behavior_profile(
        "generic",
        [{"payer": "generic", "status": "IN_REVIEW", "settlement_days": 45, "settlement_percent": 0.7}],
    )
    probability = anomaly_recovery_probability(
        {
            "estimated_recoverable": anomaly.estimated_recoverable,
            "confidence_score": anomaly.confidence_score,
            "severity": str(anomaly.severity),
        },
        behavior,
    )
    return {
        "anomaly_id": anomaly_id,
        **probability,
    }


@router.post("/artists/{artist_id}/anomalies/detect")
def detect_anomalies(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    rg = RightsGraph()
    engine = AnomalyEngine(EarningsEngine(rg), rg)
    anomaly_dicts = engine.detect_all(artist_id, db)

    for row in anomaly_dicts:
        anomaly_id = row.get("id")
        priority = float(row.get("estimated_recoverable") or 0.0)
        reason = f"Anomaly detected: {row.get('subtype') or row.get('category') or 'UNKNOWN'}"
        enqueue_review_item(
            db,
            artist_id=artist_id,
            source_type=ReviewSourceType.ANOMALY,
            source_id=str(anomaly_id) if anomaly_id else None,
            reason=reason,
            priority_score=priority,
            payload=row,
        )
        if float(row.get("confidence_score") or 1.0) < 0.55:
            enqueue_review_item(
                db,
                artist_id=artist_id,
                source_type=ReviewSourceType.ML_CONFIDENCE,
                source_id=str(anomaly_id) if anomaly_id else None,
                reason="Low model confidence anomaly requires analyst review",
                priority_score=priority,
                payload=row,
            )

    try:
        hubspot_sync_recovery_update.delay(artist_id, event="anomalies_detected")
    except Exception:  # noqa: BLE001
        pass

    return {"artist_id": artist_id, "detected": anomaly_dicts}
