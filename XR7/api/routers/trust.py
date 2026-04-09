"""Pillar 1 — Real-time Trust & Transparency trace feed."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from XR7.api.routers.auth import require_artist_access
from XR7.models.anomaly import Anomaly
from XR7.models.base import get_db
from XR7.models.claim import Claim
from XR7.models.legal_defensibility_event import LegalDefensibilityEvent
from XR7.recovery.trust_defensibility import TrustDefensibilityService
from XR7.services.branding import inject_branding_metadata
from XR7.services.trust_trace import get_latest_trace

router = APIRouter(tags=["trust"])


@router.get("/artists/{artist_id}/trust/trace")
def get_trust_trace(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """Return the real-time pipeline trace feed for this artist.

    Each entry contains stage, sub_stage, confidence (0-1), eta_seconds,
    and a plain-English explanation of what XR7 is doing right now.
    """
    events = get_latest_trace(db, artist_id)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "trace": events,
            "latest_stage": events[-1]["stage"] if events else None,
        },
    )


@router.get("/artists/{artist_id}/trust/defensibility")
def get_trust_defensibility(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    avg_conf = sum(float(a.confidence_score or 0.0) for a in anomalies) / max(len(anomalies), 1)
    avg_trust = sum(float(a.trust_score or 0.0) for a in anomalies) / max(len(anomalies), 1)
    pending_attorney = sum(1 for c in claims if bool(c.attorney_review_required))
    rating = "green" if avg_trust >= 75 else ("yellow" if avg_trust >= 50 else "red")
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "trust_score": round(avg_trust, 2),
            "average_model_confidence": round(avg_conf, 4),
            "defensibility_rating": rating,
            "attorney_review_required_claims": pending_attorney,
        },
    )


@router.post("/artists/{artist_id}/trust/classification-audit")
def append_classification_audit(
    artist_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    service = TrustDefensibilityService(db)
    logged = service.log_classification_decision(
        artist_id=artist_id,
        anomaly_id=str(payload.get("anomaly_id") or ""),
        inputs=dict(payload.get("inputs") or {}),
        model_version=str(payload.get("model_version") or "unknown"),
        rule_version=str(payload.get("rule_version") or "unknown"),
        agent_id=str(payload.get("agent_id") or "manual"),
        confidence_score=float(payload.get("confidence_score") or 0.0),
        human_review_flag=bool(payload.get("human_review_flag")),
    )
    row = LegalDefensibilityEvent(
        artist_id=artist_id,
        anomaly_id=str(payload.get("anomaly_id") or "") or None,
        claim_id=str(payload.get("claim_id") or "") or None,
        model_version=str(payload.get("model_version") or "unknown"),
        rule_version=str(payload.get("rule_version") or "unknown"),
        agent_id=str(payload.get("agent_id") or "manual"),
        confidence_score=float(payload.get("confidence_score") or 0.0),
        human_review_flag=bool(payload.get("human_review_flag")),
        input_hash=str(logged.get("decision_hash") or ""),
        payload_json=str(payload),
    )
    db.add(row)
    db.commit()

    return inject_branding_metadata(db, {"artist_id": artist_id, "audit": logged})
