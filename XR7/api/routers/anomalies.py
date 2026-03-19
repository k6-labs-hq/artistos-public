from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.api.routers.auth import get_optional_auth_payload
from XR7.ai_music.influence_detector import InfluenceDetector
from XR7.anomaly.fraud_inflation_detector import FraudInflationDetector
from XR7.anomaly.engine import AnomalyEngine
from XR7.earnings.engine import EarningsEngine
from XR7.graph.rights_graph import RightsGraph
from XR7.models.anomaly import (
    Anomaly,
    AnomalyRecoveryProbabilityResponseSchema,
    AnomalySchema,
    AnomalyWithRecoverabilitySchema,
    DetectAnomaliesResponseSchema,
)
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.review_queue import ReviewSourceType
from XR7.recovery.payer_behavior_model import payer_behavior_profile
from XR7.recovery.recoverability_classifier import build_recoverability_payload
from XR7.recovery.recovery_probability_model import anomaly_recovery_probability
from XR7.recovery.discovery_rule_engine import DiscoveryRuleEngine
from XR7.recovery.trust_defensibility import TrustDefensibilityService
from XR7.services.branding import inject_branding_metadata, branding_metadata, get_branding_for_artist
from XR7.services.review_queue import enqueue_review_item
from XR7.tasks.hubspot import hubspot_sync_recovery_update
from xr7_common.logging import get_logger

router = APIRouter(tags=["anomalies"])
logger = get_logger(__name__)


@router.get("/artists/{artist_id}/anomalies", response_model=list[AnomalyWithRecoverabilitySchema])
def list_anomalies(
    artist_id: str,
    status: str | None = None,
    debug: bool = False,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
):
    query = db.query(Anomaly).filter(Anomaly.artist_id == artist_id)
    if status:
        query = query.filter(Anomaly.status == status)
    rows = query.all()
    brand_meta = branding_metadata(get_branding_for_artist(db, artist_id))

    payload = []
    for r in rows:
        anomaly_payload = AnomalySchema.model_validate(r).model_dump(mode="json")
        recoverability_payload = build_recoverability_payload(anomaly_payload)
        discovery = DiscoveryRuleEngine().evaluate(anomaly_payload)
        trust = TrustDefensibilityService().trust_score(
            data_completeness=0.85 if anomaly_payload.get("description") else 0.6,
            model_confidence=float(anomaly_payload.get("confidence_score") or 0.0),
            contract_evidence_quality=0.7 if recoverability_payload.get("contract_recoverability") else 0.45,
            sol_risk=1.0 if discovery.get("urgent_flag") else 0.25,
        )
        obj = {
            **anomaly_payload,
            "branding": brand_meta,
            "recovery_probability": anomaly_recovery_probability(
                {
                    "estimated_recoverable": r.estimated_recoverable,
                    "confidence_score": r.confidence_score,
                    "severity": str(r.severity),
                }
            ),
            **recoverability_payload,
            "redistribution_risk_score": (recoverability_payload.get("black_box_expiration") or {}).get("redistribution_risk_score"),
            "trust_score": trust.get("trust_score"),
            "urgent_flag": bool(discovery.get("urgent_flag")),
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


@router.get("/anomalies/{anomaly_id}/recovery-probability", response_model=AnomalyRecoveryProbabilityResponseSchema)
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
    anomaly_payload = AnomalySchema.model_validate(anomaly).model_dump(mode="json")
    discovery = DiscoveryRuleEngine().evaluate(anomaly_payload)
    recoverability = build_recoverability_payload(anomaly_payload)
    trust = TrustDefensibilityService().trust_score(
        data_completeness=0.85 if anomaly_payload.get("description") else 0.6,
        model_confidence=float(anomaly_payload.get("confidence_score") or 0.0),
        contract_evidence_quality=0.7 if recoverability.get("contract_recoverability") else 0.45,
        sol_risk=1.0 if discovery.get("urgent_flag") else 0.25,
    )
    return {
        "anomaly_id": anomaly_id,
        **probability,
        **recoverability,
        "redistribution_risk_score": (recoverability.get("black_box_expiration") or {}).get("redistribution_risk_score"),
        "trust_score": trust.get("trust_score"),
        "urgent_flag": bool(discovery.get("urgent_flag")),
    }


@router.post("/artists/{artist_id}/anomalies/detect", response_model=DetectAnomaliesResponseSchema)
def detect_anomalies(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    rg = RightsGraph()
    engine = AnomalyEngine(EarningsEngine(rg), rg)
    anomaly_dicts = engine.detect_all(artist_id, db)

    enriched: list[dict] = []
    for row in anomaly_dicts:
        row_payload = dict(row)
        row_payload.update(build_recoverability_payload(row_payload))
        enriched.append(row_payload)
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
            payload=row_payload,
        )
        if float(row.get("confidence_score") or 1.0) < 0.55:
            enqueue_review_item(
                db,
                artist_id=artist_id,
                source_type=ReviewSourceType.ML_CONFIDENCE,
                source_id=str(anomaly_id) if anomaly_id else None,
                reason="Low rule confidence anomaly requires analyst review",
                priority_score=priority,
                payload=row_payload,
            )

    try:
        hubspot_sync_recovery_update.delay(artist_id, event="anomalies_detected")
    except Exception:  # noqa: BLE001
        logger.exception("Failed to enqueue HubSpot anomalies sync", extra={"artist_id": artist_id})

    return inject_branding_metadata(db, {"artist_id": artist_id, "detected": enriched})


@router.post("/artists/{artist_id}/ai-music/scan-influence")
async def scan_ai_influence(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    detector = InfluenceDetector(db)
    matches = await detector.scan_new_ai_releases(artist_id)
    claim_ids: list[str] = []
    evidence = []
    for match in matches:
        claim_id = await detector.auto_create_claim(artist_id, match)
        claim_ids.append(claim_id)
        evidence.append(await detector.generate_influence_evidence(match))

    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "potential_claims": matches,
        "claim_ids": claim_ids,
        "evidence_packets": evidence,
        "leakage_discovered_increment": len(claim_ids),
    })


@router.post("/artists/{artist_id}/anomalies/fraud-scan")
def fraud_scan(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    result = FraudInflationDetector().flag_anomalies_for_report(artist_id)
    if isinstance(result, dict):
        return inject_branding_metadata(db, {"artist_id": artist_id, **result})
    return inject_branding_metadata(db, {"artist_id": artist_id, "result": result})
