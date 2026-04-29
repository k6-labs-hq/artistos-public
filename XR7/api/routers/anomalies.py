import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.ai_music.influence_detector import InfluenceDetector
from XR7.anomaly.engine import AnomalyEngine
from XR7.anomaly.fraud_inflation_detector import FraudInflationDetector
from XR7.api.routers.auth import get_optional_auth_payload
from XR7.earnings.engine import EarningsEngine
from XR7.graph.rights_graph import RightsGraph
from XR7.ml.confidence_gating import ConfidenceGatingService
from XR7.models.anomaly import (
    Anomaly,
    AnomalyCategory,
    AnomalyRecoveryProbabilityResponseSchema,
    AnomalySchema,
    AnomalySeverity,
    AnomalyStatus,
    AnomalyWithRecoverabilitySchema,
    DetectAnomaliesResponseSchema,
)
from XR7.models.base import get_db
from XR7.models.review_queue import ReviewSourceType
from XR7.models.xr7_royalty import XR7AIDecisionAuditLog
from XR7.recovery.discovery_rule_engine import DiscoveryRuleEngine
from XR7.recovery.gap_explainer import GapExplainerService
from XR7.recovery.payer_behavior_model import payer_behavior_profile
from XR7.recovery.recoverability_classifier import build_recoverability_payload
from XR7.recovery.recovery_probability_model import anomaly_recovery_probability
from XR7.recovery.trust_defensibility import TrustDefensibilityService
from XR7.services.branding import (
    branding_metadata,
    get_branding_for_artist,
    inject_branding_metadata,
)
from XR7.services.cache import cached_response
from XR7.services.review_queue import enqueue_review_item
from XR7.services.router_v21_phase1 import router_service_for
from XR7.tasks.hubspot import hubspot_sync_recovery_update
from xr7_common.logging import get_logger

router = APIRouter(tags=["anomalies"])
_router_service = router_service_for("anomalies")
logger = get_logger(__name__)


def _deterministic_anomaly_id(artist_id: str, rule_id: str, identity_key: str) -> str:
    """Stable id so re-running detection is idempotent (#216).

    Hashes on (artist_id, rule_id, identity_key). The identity_key is what
    distinguishes multiple findings of the same rule for the same artist —
    e.g. worst_payer for HIGH_RETROACTIVE_PAYMENT_RATIO, work_title for
    TRACK_RATE_OUTLIER. Rules that fire at most once per artist pass an
    empty string. Crucially, time-varying counts (payment_count, etc.)
    are NOT in the hash anymore — those used to make every re-detection
    insert a fresh row instead of upserting in place.
    """
    h = hashlib.sha256()
    h.update(artist_id.encode())
    h.update(b"|")
    h.update(rule_id.encode())
    h.update(b"|")
    h.update(identity_key.encode())
    return f"anm_{h.hexdigest()[:24]}"


def _persist_anomaly(db: Session, artist_id: str, row: dict, confidence: float) -> Anomaly:
    """Upsert an anomaly detected by the rule engine. Returns the persisted row."""
    rule_id = str(row.get("rule_id") or row.get("subtype") or "UNKNOWN")
    evidence = row.get("evidence") or {}
    # Each rule declares an `identity_key` that's stable across re-detections.
    # Defaults to empty string for rules that fire at most once per artist.
    identity_key = str(row.get("identity_key") or "")
    anomaly_id = _deterministic_anomaly_id(artist_id, rule_id, identity_key)

    existing = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if existing is not None:
        existing.confidence_score = confidence
        existing.estimated_recoverable = row.get("estimated_recoverable")
        existing.expected_amount = row.get("expected_amount")
        existing.actual_amount = row.get("actual_amount")
        existing.urgent_flag = bool(row.get("urgent_flag"))
        return existing

    anomaly = Anomaly(
        id=anomaly_id,
        artist_id=artist_id,
        category=AnomalyCategory(str(row.get("category") or "ROYALTY")),
        subtype=str(row.get("subtype") or "UNKNOWN"),
        severity=AnomalySeverity(str(row.get("severity") or "LOW")),
        expected_amount=row.get("expected_amount"),
        actual_amount=row.get("actual_amount"),
        estimated_recoverable=row.get("estimated_recoverable"),
        confidence_score=confidence,
        status=AnomalyStatus.OPEN,
        description=row.get("description"),
        feature_snapshot=json.dumps(
            {
                "rule_id": rule_id,
                "rule_name": row.get("rule_name"),
                "evidence": evidence,
            },
            default=str,
        ),
        urgent_flag=bool(row.get("urgent_flag")),
    )
    db.add(anomaly)
    db.flush()
    return anomaly


@router.get(
    "/artists/{artist_id}/anomalies",
    response_model=list[AnomalyWithRecoverabilitySchema],
    openapi_extra={
        "responses": {
            "200": {
                "description": "List of detected anomalies with recoverability metadata",
                "content": {
                    "application/json": {
                        "example": [
                            {
                                "id": "anm_abc123",
                                "artist_id": "art_xyz789",
                                "category": "ROYALTY",
                                "severity": "HIGH",
                                "status": "OPEN",
                                "estimated_recoverable": 1200.50,
                                "confidence_score": 0.87,
                                "description": "Underreported streaming royalties Q3 2023",
                                "recovery_probability": 0.74,
                                "trust_score": 0.81,
                                "urgent_flag": False,
                            }
                        ]
                    }
                },
            },
            "404": {"description": "Artist not found"},
        }
    },
)
@cached_response("anomalies_list", ttl_seconds=90)
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
            contract_evidence_quality=(
                0.7 if recoverability_payload.get("contract_recoverability") else 0.45
            ),
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
            "redistribution_risk_score": (
                recoverability_payload.get("black_box_expiration") or {}
            ).get("redistribution_risk_score"),
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


@router.get(
    "/anomalies/{anomaly_id}/recovery-probability",
    response_model=AnomalyRecoveryProbabilityResponseSchema,
)
def anomaly_recovery_probability_endpoint(anomaly_id: str, db: Session = Depends(get_db)):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    behavior = payer_behavior_profile(
        "generic",
        [
            {
                "payer": "generic",
                "status": "IN_REVIEW",
                "settlement_days": 45,
                "settlement_percent": 0.7,
            }
        ],
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
        "redistribution_risk_score": (recoverability.get("black_box_expiration") or {}).get(
            "redistribution_risk_score"
        ),
        "trust_score": trust.get("trust_score"),
        "urgent_flag": bool(discovery.get("urgent_flag")),
    }


def run_detection_and_persist(artist_id: str, db: Session) -> list[dict]:
    """Run the anomaly engine, gate by confidence, persist accepted findings, and
    route REVIEW-tier items into the review queue.

    Returns the list of enriched anomaly dicts (each with persisted ``id``). Used
    by both ``POST /anomalies/detect`` and the post-upload flow in
    ``ingestion.upload_statement`` so findings are persisted and not silently
    dropped.
    """
    rg = RightsGraph()
    engine = AnomalyEngine(EarningsEngine(rg), rg)
    anomaly_dicts = engine.detect_all(artist_id, db)

    gating = ConfidenceGatingService(db)
    enriched: list[dict] = []
    rejected_count = 0
    auto_accepted_count = 0

    for row in anomaly_dicts:
        # Apply confidence gating
        confidence = float(row.get("confidence_score") or 0.0)
        decision = gating.evaluate(
            confidence=confidence,
            context={
                "anomaly_type": row.get("subtype") or row.get("category"),
                "estimated_recoverable": float(row.get("estimated_recoverable") or 0.0),
                "artist_id": artist_id,
                "urgency_flag": bool(row.get("urgent_flag")),
            },
        )

        # Skip rejected anomalies (too low confidence)
        if not decision.should_create:
            rejected_count += 1
            logger.debug(
                "anomaly_rejected_by_gating",
                extra={
                    "artist_id": artist_id,
                    "confidence": confidence,
                    "tier": decision.tier.value,
                    "reasoning": decision.reasoning,
                },
            )
            continue

        # Persist (or upsert) the anomaly so downstream flows can reference it by id.
        persisted = _persist_anomaly(db, artist_id, row, confidence)
        anomaly_id = persisted.id

        # Enrich anomaly metadata
        row_payload = dict(row)
        row_payload["id"] = anomaly_id
        row_payload.update(build_recoverability_payload(row_payload))
        row_payload["gating_decision"] = {
            "tier": decision.tier.value,
            "priority_score": decision.priority_score,
            "reasoning": decision.reasoning,
        }
        enriched.append(row_payload)

        reason = f"Anomaly detected: {row.get('subtype') or row.get('category') or 'UNKNOWN'}"

        # Route to review queue if required (REVIEW tier)
        if decision.requires_review:
            enqueue_review_item(
                db,
                artist_id=artist_id,
                source_type=ReviewSourceType.ML_CONFIDENCE,
                source_id=anomaly_id,
                reason=f"{reason} (confidence: {confidence:.2f})",
                priority_score=decision.priority_score,
                payload=row_payload,
            )
        else:
            # AUTO_ACCEPT tier: log for auditing, bypass manual review
            auto_accepted_count += 1
            logger.info(
                "anomaly_auto_accepted",
                extra={
                    "artist_id": artist_id,
                    "anomaly_id": anomaly_id,
                    "confidence": confidence,
                    "estimated_recoverable": row.get("estimated_recoverable"),
                },
            )

    db.commit()

    # Log gating metrics
    gating_metrics = gating.get_metrics()
    logger.info(
        "anomaly_detection_gating_complete",
        extra={
            "artist_id": artist_id,
            "total_detected": len(anomaly_dicts),
            "enriched_count": len(enriched),
            "rejected_count": rejected_count,
            "auto_accepted_count": auto_accepted_count,
            "gating_metrics": gating_metrics,
        },
    )

    return enriched


@router.post("/artists/{artist_id}/anomalies/detect", response_model=DetectAnomaliesResponseSchema)
def detect_anomalies(artist_id: str, db: Session = Depends(get_db)):
    _router_service.get_artist_or_404(artist_id, db)
    enriched = run_detection_and_persist(artist_id, db)

    try:
        hubspot_sync_recovery_update.delay(artist_id, event="anomalies_detected")
    except Exception:  # noqa: BLE001
        logger.exception("Failed to enqueue HubSpot anomalies sync", extra={"artist_id": artist_id})

    return inject_branding_metadata(db, {"artist_id": artist_id, "detected": enriched})


@router.post("/artists/{artist_id}/ai-music/scan-influence")
async def scan_ai_influence(artist_id: str, db: Session = Depends(get_db)):
    _router_service.get_artist_or_404(artist_id, db)

    detector = InfluenceDetector(db)
    matches = await detector.scan_new_ai_releases(artist_id)
    claim_ids: list[str] = []
    evidence = []
    for match in matches:
        claim_id = await detector.auto_create_claim(artist_id, match)
        claim_ids.append(claim_id)
        evidence.append(await detector.generate_influence_evidence(match))

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "potential_claims": matches,
            "claim_ids": claim_ids,
            "evidence_packets": evidence,
            "leakage_discovered_increment": len(claim_ids),
        },
    )


@router.post("/artists/{artist_id}/anomalies/fraud-scan")
def fraud_scan(artist_id: str, db: Session = Depends(get_db)):
    _router_service.get_artist_or_404(artist_id, db)
    result = FraudInflationDetector().flag_anomalies_for_report(artist_id)
    if isinstance(result, dict):
        return inject_branding_metadata(db, {"artist_id": artist_id, **result})
    return inject_branding_metadata(db, {"artist_id": artist_id, "result": result})


@router.get("/anomalies/{anomaly_id}/explain")
def explain_anomaly(anomaly_id: str, db: Session = Depends(get_db)):
    """Explain-my-gap endpoint: plain-language explanation with evidence citations.

    Generates a natural-language explanation of why a royalty gap exists,
    including summary, top drivers, confidence, and recommended actions.
    """
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    anomaly_payload = AnomalySchema.model_validate(anomaly).model_dump(mode="json")

    service = GapExplainerService(db=db)
    explanation = service.explain_gap_sync(anomaly_payload)

    # Log the explanation decision to audit trail
    audit_log = XR7AIDecisionAuditLog(
        tenant_id="default",
        artist_id=anomaly.artist_id,
        decision_type="gap_explanation",
        model_provider=service.provider,
        model_version=service.model,
        prompt_hash="",  # Would be hash of prompt in production
        input_ref=f"anomaly:{anomaly_id}",
        output_ref=f"gap_explanation:{anomaly_id}",
    )
    db.add(audit_log)
    db.commit()

    return inject_branding_metadata(
        db,
        {
            "anomaly_id": anomaly_id,
            "explanation": explanation,
        },
    )


@router.get("/artists/{artist_id}/anomalies/{anomaly_id}/explain")
def explain_artist_anomaly(artist_id: str, anomaly_id: str, db: Session = Depends(get_db)):
    """Artist-scoped explain-my-gap endpoint."""
    anomaly = (
        db.query(Anomaly).filter(Anomaly.id == anomaly_id, Anomaly.artist_id == artist_id).first()
    )
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found for this artist")

    anomaly_payload = AnomalySchema.model_validate(anomaly).model_dump(mode="json")

    service = GapExplainerService(db=db)
    explanation = service.explain_gap_sync(anomaly_payload)

    # Log the explanation decision to audit trail
    audit_log = XR7AIDecisionAuditLog(
        tenant_id="default",
        artist_id=artist_id,
        decision_type="gap_explanation",
        model_provider=service.provider,
        model_version=service.model,
        prompt_hash="",  # Would be hash of prompt in production
        input_ref=f"anomaly:{anomaly_id}",
        output_ref=f"gap_explanation:{anomaly_id}",
    )
    db.add(audit_log)
    db.commit()

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "anomaly_id": anomaly_id,
            "explanation": explanation,
        },
    )
