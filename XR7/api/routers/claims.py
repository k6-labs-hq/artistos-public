import asyncio
import csv
import io
import json
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.agents.orchestrator import run_export_prep_pipeline_sync
from XR7.api.authz import (
    authorize_advance_approval_access,
    authorize_claim_edit_access,
    require_admin_session,
)
from XR7.api.routers.auth import (
    enforce_claim_access,
    get_auth_payload,
    get_optional_auth_payload,
    require_artist_access,
)
from XR7.auth.event_notifications import send_event_notification
from XR7.blockchain.evidence_anchor import EvidenceAnchor as BlockchainEvidenceAnchor
from XR7.models.admin_audit_log import AdminAuditLog
from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.claim import Claim, ClaimSchema, ClaimStatus
from XR7.models.evidence_anchor import EvidenceAnchor as EvidenceAnchorModel
from XR7.models.ml_feedback import CalibrationSnapshot
from XR7.models.notification_preference import NotificationPreference
from XR7.models.payment import Payment
from XR7.models.review_queue import ReviewSourceType
from XR7.recovery.attorney_escalation import AttorneyNetworkEscalator
from XR7.recovery.cash_recovery_forecast import build_claim_forecast
from XR7.recovery.claims_evidence_package_builder import ClaimsEvidencePackageBuilder
from XR7.recovery.discovery_rule_engine import DiscoveryRuleEngine
from XR7.recovery.evidence_strength import score_evidence_strength
from XR7.recovery.negotiation_intelligence import build_negotiation_intel
from XR7.recovery.orchestrator import ClaimsOrchestrator
from XR7.recovery.payer_behavior_model import payer_behavior_profile
from XR7.recovery.payer_playbooks import build_claim_playbook
from XR7.recovery.recoverability_classifier import build_recoverability_payload
from XR7.recovery.recovery_automation import build_automation_plan
from XR7.recovery.sla_predictor import predict_claim_sla_dates
from XR7.recovery.sol_calculator import SOL_DISCLAIMER, calculate_sol
from XR7.recovery.trust_defensibility import TrustDefensibilityService
from XR7.services.branding import (
    apply_brand_placeholders,
    branding_metadata,
    get_branding_for_artist,
    inject_branding_metadata,
    org_id_for_artist,
)
from XR7.services.live_updates import broadcast_live_update
from XR7.services.pdf_builder import build_simple_pdf as _build_simple_pdf
from XR7.services.pdf_builder import safe_pdf_text as _safe_pdf_text
from XR7.services.review_queue import enqueue_review_item
from XR7.services.router_v21_phase1 import router_service_for
from XR7.services.webhook_delivery import OutboundWebhookService
from XR7.tasks.hubspot import hubspot_sync_recovery_update
from XR7.tasks.webhooks import deliver_webhook_event
from xr7_common.logging import get_logger

router = APIRouter(tags=["claims"])
_router_service = router_service_for("claims")
logger = get_logger(__name__)


def _audit(
    db: Session,
    *,
    actor: str,
    action: str,
    resource_type: str,
    resource_id: str | None,
    details: dict | None = None,
) -> None:
    db.add(
        AdminAuditLog(
            actor=actor,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
        )
    )


def _export_agent_fields(state: dict | None) -> dict:
    s = state or {}
    return {
        "legal_authority_sections": s.get("legal_authority_sections") or [],
        "legal_methodology_summary": s.get("legal_methodology_summary") or "",
        "legal_compliance_statements": s.get("legal_compliance_statements") or [],
        "legal_structured_packet": s.get("legal_structured_packet") or {},
        "legal_appendix": s.get("legal_appendix") or {},
        "legal_risk_score": s.get("legal_risk_score"),
        "settlement_probability": s.get("settlement_probability"),
        "escalation_readiness_score": s.get("escalation_readiness_score"),
        "escalation_prepared_packet": s.get("escalation_prepared_packet") or {},
        "negotiation_tone_profile": s.get("negotiation_tone_profile") or {},
        "adapted_messages": s.get("adapted_messages") or [],
        "payer_behavior_profile": s.get("payer_behavior_profile") or {},
        "predicted_responsiveness": s.get("predicted_responsiveness"),
        "predicted_settlement_speed_days": s.get("predicted_settlement_speed_days"),
        "predicted_settlement_probability": s.get("predicted_settlement_probability"),
        "predicted_escalation_resistance": s.get("predicted_escalation_resistance"),
        "recommended_negotiation_strategy": s.get("recommended_negotiation_strategy") or "",
        "recommended_packet_emphasis": s.get("recommended_packet_emphasis") or [],
        "attorney_briefing_packet": s.get("attorney_briefing_packet") or {},
        "attorney_case_file": s.get("attorney_case_file") or {},
        "attorney_case_file_summary": s.get("attorney_case_file_summary") or "",
        "attorney_exhibits_index": s.get("attorney_exhibits_index") or [],
        "attorney_chain_of_custody_summary": s.get("attorney_chain_of_custody_summary") or "",
        "attorney_packet_metadata": s.get("attorney_packet_metadata") or {},
        "predicted_recovery_amount": s.get("predicted_recovery_amount"),
        "predicted_recovery_low": s.get("predicted_recovery_low"),
        "predicted_recovery_high": s.get("predicted_recovery_high"),
        "predicted_expected_value": s.get("predicted_expected_value"),
        "predicted_settlement_timeline_days": s.get("predicted_settlement_timeline_days"),
        "predicted_escalation_probability": s.get("predicted_escalation_probability"),
        "predicted_full_payout_probability": s.get("predicted_full_payout_probability"),
        "attorney_export_package": s.get("attorney_export_package") or {},
        "attorney_export_manifest": s.get("attorney_export_manifest") or {},
        "attorney_export_summary": s.get("attorney_export_summary") or "",
        "narrative_summary": s.get("narrative_summary") or "",
        "narrative_sections": s.get("narrative_sections") or {},
        "narrative_highlights": s.get("narrative_highlights") or [],
    }


def _build_multipage_pdf(pages: list[list[str]]) -> bytes:
    if not pages:
        return _build_simple_pdf(["XR7 Attorney Evidence Package", "No data available."])

    objects: list[bytes] = []
    output = io.BytesIO()

    # Object layout:
    # 1: catalog, 2: pages, 3..N: page objects, then font object, then content objects.
    page_count = len(pages)
    first_page_obj = 3
    font_obj = first_page_obj + page_count
    first_content_obj = font_obj + 1

    page_refs = " ".join([f"{first_page_obj + i} 0 R" for i in range(page_count)])
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(
        f"2 0 obj << /Type /Pages /Count {page_count} /Kids [{page_refs}] >> endobj\n".encode(
            "utf-8"
        )
    )

    for i in range(page_count):
        page_obj_id = first_page_obj + i
        content_obj_id = first_content_obj + i
        objects.append(
            (
                f"{page_obj_id} 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 {font_obj} 0 R >> >> /Contents {content_obj_id} 0 R >> endobj\n"
            ).encode("utf-8")
        )

    objects.append(
        f"{font_obj} 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n".encode(
            "utf-8"
        )
    )

    for i, lines in enumerate(pages):
        content_obj_id = first_content_obj + i
        page_lines = lines[:46]
        content_ops = ["BT", "/F1 10 Tf", "50 780 Td", "12 TL"]
        for line in page_lines:
            content_ops.append(f"({_safe_pdf_text(str(line))}) Tj")
            content_ops.append("T*")
        content_ops.append("ET")
        content = "\n".join(content_ops).encode("utf-8")
        objects.append(
            f"{content_obj_id} 0 obj << /Length {len(content)} >> stream\n".encode("utf-8")
            + content
            + b"\nendstream endobj\n"
        )

    output.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(output.tell())
        output.write(obj)

    xref_start = output.tell()
    output.write(f"xref\n0 {len(objects) + 1}\n".encode("utf-8"))
    output.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        output.write(f"{off:010d} 00000 n \n".encode("utf-8"))
    output.write(
        (
            f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF"
        ).encode("utf-8")
    )
    return output.getvalue()


def _status_matches_proof_submitted(status: str | object) -> bool:
    value = str(getattr(status, "value", status) or "").strip().lower()
    return value in {"proof_submitted", "proof submitted"}


def _utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _attorney_escalation_state(claim: Claim, default_grace_days: int) -> dict:
    now = datetime.now(timezone.utc)
    grace_days = int(claim.grace_period_days or default_grace_days or 60)
    if grace_days < 1:
        grace_days = 1

    proof_submitted_at = _utc(claim.proof_submitted_at)
    days_elapsed = 0
    days_remaining = grace_days
    progress = 0.0
    deadline = None
    if proof_submitted_at is not None:
        elapsed = now - proof_submitted_at
        days_elapsed = max(0, int(elapsed.total_seconds() // 86400))
        days_remaining = max(0, grace_days - days_elapsed)
        progress = min(1.0, max(0.0, days_elapsed / float(grace_days)))
        deadline = (proof_submitted_at + timedelta(days=grace_days)).date().isoformat()

    eligible = (
        _status_matches_proof_submitted(claim.status)
        and proof_submitted_at is not None
        and days_elapsed >= grace_days
        and not bool(claim.attorney_file_generated)
    )

    return {
        "is_proof_submitted": _status_matches_proof_submitted(claim.status),
        "proof_submitted_at": proof_submitted_at.isoformat() if proof_submitted_at else None,
        "grace_period_days": grace_days,
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "progress": progress,
        "payment_response_deadline": deadline,
        "eligible_to_prepare": eligible,
        "attorney_file_generated": bool(claim.attorney_file_generated),
        "attorney_file_generated_at": (
            _utc(claim.attorney_file_generated_at).isoformat()
            if claim.attorney_file_generated_at
            else None
        ),
        "countdown_message": f"Payer has {days_remaining} days remaining to respond",
        "countdown_subtext": (
            f"If payment is not received by {deadline}, you may escalate to your attorney."
            if deadline
            else "If payment is not received by the deadline, you may escalate to your attorney."
        ),
    }


class AttorneyEvidenceRequest(BaseModel):
    additional_notes: str | None = None
    attorney_engagement_deadline: datetime | None = None


class ClaimCreateRequest(BaseModel):
    anomaly_id: str
    claim_type: str = "RECOVERY"


def _evidence_summary_lines(packet: dict, brand: dict | None = None) -> list[str]:
    brand_payload = brand or {}
    anomaly = packet.get("anomaly", {})
    proof = packet.get("proof", {})
    totals = proof.get("totals", {})
    recon = packet.get("reconciliation", {})
    integrity = packet.get("integrity", {})

    lines = [
        "{{BRAND.NAME}} Evidence Packet",
        f"Claim ID: {packet.get('claim_id')}",
        f"Generated At: {packet.get('generated_at')}",
        f"Anomaly: {anomaly.get('category')} / {anomaly.get('subtype')}",
        f"Description: {anomaly.get('description')}",
        "",
        "Missed Money Proof",
        f"Missing Money Amount: {proof.get('missing_money_amount')}",
        f"Ledger Rows Cited: {totals.get('ledger_row_count', 0)}",
        f"Total Expected: {totals.get('total_expected_amount', 0)}",
        f"Total Received: {totals.get('total_received_amount', 0)}",
        f"Ledger Shortfall: {totals.get('ledger_shortfall_amount', 0)}",
        "",
        "Reconciliation",
        f"Model Shortfall: {recon.get('model_shortfall_amount')}",
        f"Proof Shortfall: {recon.get('proof_shortfall_amount')}",
        f"Discrepancy Amount: {recon.get('discrepancy_amount')}",
        f"Discrepancy Flag: {recon.get('discrepancy_flag')}",
        "",
        "Integrity",
        f"Packet Hash: {integrity.get('packet_hash')}",
        f"Prior Packet Hash: {integrity.get('prior_packet_hash')}",
        f"Chain Hash: {integrity.get('chain_hash')}",
        f"Signature: {integrity.get('signature')}",
        "",
        "{{BRAND.LEGAL_DISCLAIMER}}",
    ]
    return apply_brand_placeholders(lines, brand_payload)


def _resolve_source_file(source_file: str | None) -> Path | None:
    if not source_file:
        return None
    p = Path(source_file)
    if p.is_absolute() and p.exists() and p.is_file():
        return p
    repo_root = Path(__file__).resolve().parents[3]
    candidates = [Path.cwd() / source_file, repo_root / source_file]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


@router.get(
    "/artists/{artist_id}/claims",
    openapi_extra={
        "responses": {
            "200": {
                "description": "List of claims with forecast and SOL metadata",
                "content": {
                    "application/json": {
                        "example": [
                            {
                                "claim": {
                                    "id": "clm_abc123",
                                    "artist_id": "art_xyz",
                                    "status": "submitted",
                                    "amount_claimed": 1500.0,
                                },
                                "forecast": {"predicted_amount": 1350.0},
                                "sol": {"status": "active", "days_remaining": 120},
                            }
                        ]
                    }
                },
            }
        }
    },
)
def list_claims(
    artist_id: str,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
):
    claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    default_grace_days = int((artist.default_attorney_grace_period_days if artist else 60) or 60)
    snapshots = (
        db.query(CalibrationSnapshot).filter(CalibrationSnapshot.artist_id == artist_id).all()
    )
    historical_claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()

    payload = []
    for claim in claims:
        anomaly = db.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
        sol = calculate_sol(
            governing_law_state=claim.governing_law_state,
            contract_type=claim.contract_type,
            infringement_date=claim.infringement_date,
            discovery_date=claim.discovery_date,
        )
        forecast = build_claim_forecast(claim, anomaly, snapshots, historical_claims).to_dict()
        payload.append(
            {
                "claim": ClaimSchema.model_validate(claim).model_dump(mode="json"),
                "forecast": forecast,
                "attorney_escalation": _attorney_escalation_state(claim, default_grace_days),
                "sol": {
                    "status": sol.get("sol_status"),
                    "days_remaining": sol.get("sol_days_remaining"),
                    "deadline": (
                        sol.get("sol_deadline").isoformat() if sol.get("sol_deadline") else None
                    ),
                    "citation": sol.get("sol_citation_source"),
                    "disclaimer": SOL_DISCLAIMER,
                },
            }
        )
    return payload


@router.get(
    "/artists/{artist_id}/claims/export.csv",
    openapi_extra={
        "responses": {
            "200": {
                "description": "CSV file of all claims for the artist",
                "content": {
                    "text/csv": {
                        "example": "id,artist_id,status,...\nclm_abc123,art_xyz,submitted,..."
                    }
                },
            }
        }
    },
)
def export_claims_csv(
    artist_id: str,
    status: str | None = Query(default=None, description="Filter by claim status"),
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
):
    """Download all claims for an artist as a CSV file."""
    _router_service.get_artist_or_404(artist_id, db)

    # CRITICAL SECURITY: Validate status filter against ClaimStatus enum (Issue #75)
    if status:
        valid_statuses = {s.value for s in ClaimStatus}
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid claim status '{status}'. Valid statuses: {', '.join(sorted(valid_statuses))}",
            )

    q = db.query(Claim).filter(Claim.artist_id == artist_id)
    if status:
        q = q.filter(Claim.status == status)
    claims = q.order_by(Claim.created_at.desc()).all()

    fields = [
        "id",
        "artist_id",
        "status",
        "contract_type",
        "governing_law_state",
        "amount_claimed",
        "amount_recovered",
        "description",
        "infringement_date",
        "discovery_date",
        "created_at",
        "updated_at",
    ]

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for claim in claims:
        row = {f: getattr(claim, f, None) for f in fields}
        # Normalize non-string values
        for k, v in row.items():
            if hasattr(v, "isoformat"):
                row[k] = v.isoformat()
            elif hasattr(v, "value"):
                row[k] = v.value
        writer.writerow(row)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"claims_{artist_id}_{timestamp}.csv"
    return Response(
        content=buf.getvalue().encode("utf-8"),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/artists/{artist_id}/claims/search")
def search_claims(
    artist_id: str,
    q: str = Query(..., min_length=2, description="Search query string"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
):
    """Full-text search over claims for an artist.

    Uses PostgreSQL ``to_tsvector`` / ``plainto_tsquery`` when available,
    falling back to ILIKE pattern matching for SQLite (test environments).
    Searches across ``description``, ``contract_type``, and ``governing_law_state``.
    """
    _router_service.get_artist_or_404(artist_id, db)

    from sqlalchemy import text as sa_text

    # Detect dialect
    dialect = db.bind.dialect.name if db.bind else "sqlite"  # type: ignore[union-attr]

    if dialect == "postgresql":
        # PostgreSQL full-text search using tsvector/tsquery
        stmt = sa_text(
            """
            SELECT id FROM claims
            WHERE artist_id = :artist_id
              AND to_tsvector('english',
                  coalesce(description,'') || ' ' ||
                  coalesce(contract_type,'') || ' ' ||
                  coalesce(governing_law_state,'')
              ) @@ plainto_tsquery('english', :query)
            ORDER BY created_at DESC
            LIMIT :limit
            """
        )
        rows = db.execute(stmt, {"artist_id": artist_id, "query": q, "limit": limit}).fetchall()
        claim_ids = [row[0] for row in rows]
        claims = db.query(Claim).filter(Claim.id.in_(claim_ids)).all()
        # Re-apply order
        id_order = {cid: idx for idx, cid in enumerate(claim_ids)}
        claims.sort(key=lambda c: id_order.get(c.id, 9999))
    else:
        # SQLite fallback: ILIKE via case-insensitive LIKE
        pattern = f"%{q}%"
        claims = (
            db.query(Claim)
            .filter(
                Claim.artist_id == artist_id,
                (
                    Claim.description.ilike(pattern)
                    | Claim.contract_type.ilike(pattern)
                    | Claim.governing_law_state.ilike(pattern)
                ),
            )
            .order_by(Claim.created_at.desc())
            .limit(limit)
            .all()
        )

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "query": q,
            "total": len(claims),
            "claims": [ClaimSchema.model_validate(c).model_dump(mode="json") for c in claims],
        },
    )


def _anomaly_to_payload(anomaly: Anomaly) -> dict:
    """Serialize an Anomaly ORM row to the standard payload dict used by trust/recoverability services."""
    return {
        "id": anomaly.id,
        "artist_id": anomaly.artist_id,
        "category": str(anomaly.category),
        "subtype": anomaly.subtype,
        "severity": str(anomaly.severity),
        "estimated_recoverable": anomaly.estimated_recoverable,
        "confidence_score": anomaly.confidence_score,
        "time_window_start": anomaly.time_window_start,
        "time_window_end": anomaly.time_window_end,
        "description": anomaly.description,
        "feature_snapshot": anomaly.feature_snapshot,
        "created_at": anomaly.created_at,
    }


def _compute_anomaly_trust(anomaly_payload: dict) -> tuple[dict, dict]:
    """Return (recoverability_payload, trust_result) for an anomaly payload dict."""
    recoverability = build_recoverability_payload(anomaly_payload)
    discovery = DiscoveryRuleEngine().evaluate(anomaly_payload)
    trust = TrustDefensibilityService().trust_score(
        data_completeness=0.85 if anomaly_payload.get("description") else 0.6,
        model_confidence=float(anomaly_payload.get("confidence_score") or 0.0),
        contract_evidence_quality=0.7 if recoverability.get("contract_recoverability") else 0.45,
        sol_risk=1.0 if discovery.get("urgent_flag") else 0.25,
    )
    return recoverability, trust


@router.get("/claims/{claim_id}", response_model=ClaimSchema)
def get_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.post("/artists/{artist_id}/claims", response_model=ClaimSchema, status_code=201)
def create_claim_for_artist(
    artist_id: str,
    payload: ClaimCreateRequest,
    db: Session = Depends(get_db),
    auth_payload: dict = Depends(require_artist_access),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    _router_service.get_artist_or_404(artist_id, db)
    authorize_claim_edit_access(
        artist_id,
        db,
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )

    anomaly = (
        db.query(Anomaly)
        .filter(Anomaly.id == payload.anomaly_id, Anomaly.artist_id == artist_id)
        .first()
    )
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found for artist")

    existing = db.query(Claim).filter(Claim.anomaly_id == anomaly.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Claim already exists for anomaly")

    anomaly_payload = _anomaly_to_payload(anomaly)
    recoverability, trust = _compute_anomaly_trust(anomaly_payload)
    if not bool(recoverability.get("claim_draft_allowed")):
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Claim drafting is not allowed for this anomaly recoverability class",
                "recoverability_class": (recoverability.get("recoverability") or {}).get(
                    "recoverability_class"
                ),
                "recommended_action": (recoverability.get("recoverability") or {}).get(
                    "recommended_action"
                ),
                "rule_applied": (recoverability.get("black_box_expiration") or {}).get(
                    "rule_applied"
                ),
            },
        )

    claim = ClaimsOrchestrator(db).create_claim(
        anomaly_id=anomaly.id,
        claim_type=payload.claim_type.strip() or "RECOVERY",
    )
    claim.trust_score = float(trust.get("trust_score") or 0.0)
    claim.attorney_review_required = bool(trust.get("requires_attorney_review"))
    claim.claim_strength_rating = None
    _audit(
        db,
        actor=str(auth_payload.get("sub") or f"artist:{artist_id}"),
        action="claim_created",
        resource_type="claim",
        resource_id=claim.id,
        details={
            "artist_id": artist_id,
            "anomaly_id": anomaly.id,
            "claim_type": payload.claim_type,
            "trust_score": claim.trust_score,
            "attorney_review_required": claim.attorney_review_required,
        },
    )
    db.commit()
    db.refresh(claim)
    return claim


@router.post("/claims/{claim_id}/advance", response_model=ClaimSchema)
def advance_claim(
    claim_id: str,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    orchestrator = ClaimsOrchestrator(db)
    try:
        existing = db.query(Claim).filter(Claim.id == claim_id).first()
        if not existing:
            raise HTTPException(status_code=404, detail="Claim not found")
        # Only enforce stronger evidence quality checks when packet exists.
        if isinstance(existing.evidence, dict) and existing.evidence:
            anchor_count = (
                db.query(EvidenceAnchorModel)
                .filter(EvidenceAnchorModel.claim_id == claim_id)
                .count()
            )
            strength = score_evidence_strength(claim_id, existing.evidence, anchor_count)
            if float(strength.get("overall_strength_score") or 0.0) < 35.0:
                enqueue_review_item(
                    db,
                    artist_id=existing.artist_id,
                    source_type=ReviewSourceType.EVIDENCE,
                    source_id=existing.id,
                    reason="Claim advance blocked by weak evidence strength score",
                    priority_score=35.0 - float(strength.get("overall_strength_score") or 0.0),
                    payload={"claim_id": existing.id, "strength": strength},
                )
                raise HTTPException(
                    status_code=400, detail="Evidence strength is too low to advance claim"
                )

        status_value_before = (
            existing.status.value if hasattr(existing.status, "value") else str(existing.status)
        )
        authorize_advance_approval_access(
            existing.artist_id,
            db,
            actor_email=x_actor_email,
            actor_role=x_actor_role,
        )
        if status_value_before in {"PREPARED", "FILED"} and bool(existing.attorney_review_required):
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Attorney review required before filing due to low TrustScore",
                    "trust_score": existing.trust_score,
                    "attorney_review_required": True,
                },
            )

        updated = orchestrator.advance_claim(claim_id)
        _audit(
            db,
            actor=f"artist:{updated.artist_id}",
            action="claim_advanced",
            resource_type="claim",
            resource_id=updated.id,
            details={
                "artist_id": updated.artist_id,
                "status_before": status_value_before,
                "status_after": (
                    updated.status.value
                    if hasattr(updated.status, "value")
                    else str(updated.status)
                ),
            },
        )
        db.commit()
        pref = db.query(NotificationPreference).first()
        send_event_notification(
            pref,
            "claim_advanced",
            "{{BRAND.NAME}} claim status updated",
            f"Claim {updated.id} advanced to {updated.status}. {{BRAND.LEGAL_DISCLAIMER}}",
            current_hour_utc=datetime.now(timezone.utc).hour,
            org_id=org_id_for_artist(db, updated.artist_id),
            db=db,
        )
        status_value = (
            updated.status.value if hasattr(updated.status, "value") else str(updated.status)
        )

        if status_value in {"IN_REVIEW", "ACCEPTED"}:
            enqueue_review_item(
                db,
                artist_id=updated.artist_id,
                source_type=ReviewSourceType.CLAIM,
                source_id=updated.id,
                reason=f"Claim advanced to {status_value}; analyst check required",
                priority_score=float(updated.recovered_amount or 0.0),
                payload={"claim_id": updated.id, "status": status_value},
            )
        if status_value == "FILED" and float(updated.recovered_amount or 0.0) >= 10000:
            enqueue_review_item(
                db,
                artist_id=updated.artist_id,
                source_type=ReviewSourceType.CLAIM,
                source_id=updated.id,
                reason="High-value claim filed; analyst priority review required",
                priority_score=float(updated.recovered_amount or 0.0),
                payload={"claim_id": updated.id, "status": status_value, "threshold": 10000},
            )
        if status_value in {"SUBMITTED", "FILED"}:
            event = OutboundWebhookService(db).queue_event(
                event_type="claim.submitted",
                payload={
                    "claim_id": updated.id,
                    "artist_id": updated.artist_id,
                    "status": status_value,
                    "recovered_amount": float(updated.recovered_amount or 0.0),
                },
            )
            deliver_webhook_event.delay(event.id)
            broadcast_live_update(
                "claim.status_changed",
                {
                    "claim_id": updated.id,
                    "artist_id": updated.artist_id,
                    "status": status_value,
                },
            )
        if status_value in {"FILED", "IN_REVIEW", "PAID", "CLOSED"}:
            try:
                hubspot_sync_recovery_update.delay(
                    updated.artist_id, event=f"claim_{status_value.lower()}"
                )
            except Exception:  # noqa: BLE001
                logger.exception(
                    "Failed to enqueue HubSpot claim lifecycle sync",
                    extra={
                        "artist_id": updated.artist_id,
                        "claim_id": updated.id,
                        "status": status_value,
                    },
                )

        if status_value in {"SUBMITTED", "FILED", "IN_REVIEW"}:
            historical = (
                db.query(Claim)
                .filter(Claim.artist_id == updated.artist_id, Claim.id != updated.id)
                .all()
            )
            intel = build_negotiation_intel(updated, historical)
            enqueue_review_item(
                db,
                artist_id=updated.artist_id,
                source_type=ReviewSourceType.CLAIM,
                source_id=updated.id,
                reason="Negotiation intelligence generated for active claim",
                priority_score=float((intel.get("settlement_ranges") or {}).get("midpoint") or 0.0),
                payload={"claim_id": updated.id, "negotiation_intelligence": intel},
            )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/claims/{claim_id}/evidence")
def generate_evidence(claim_id: str, db: Session = Depends(get_db)):
    orchestrator = ClaimsOrchestrator(db)
    try:
        packet = orchestrator.generate_evidence_packet(claim_id)
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if claim:
            recon = packet.get("reconciliation", {}) if isinstance(packet, dict) else {}
            discrepancy = float(recon.get("discrepancy_amount") or 0.0)
            enqueue_review_item(
                db,
                artist_id=claim.artist_id,
                source_type=ReviewSourceType.EVIDENCE,
                source_id=claim_id,
                reason="Evidence packet generated; analyst validation pending",
                priority_score=max(float(claim.recovered_amount or 0.0), discrepancy),
                payload={"claim_id": claim_id, "reconciliation": recon},
            )
            anomaly = db.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
            if anomaly:
                anomaly_payload = _anomaly_to_payload(anomaly)
                recoverability, trust = _compute_anomaly_trust(anomaly_payload)
                package = ClaimsEvidencePackageBuilder().build(
                    claim={
                        "id": claim.id,
                        "artist_id": claim.artist_id,
                        "governing_law_state": claim.governing_law_state,
                    },
                    anomaly=anomaly_payload,
                    recoverability_payload=recoverability,
                    trust_score=float(trust.get("trust_score") or 0.0),
                )
                claim.trust_score = float(trust.get("trust_score") or 0.0)
                claim.attorney_review_required = bool(trust.get("requires_attorney_review"))
                claim.legal_defensibility_report = (
                    TrustDefensibilityService().legal_defensibility_report(
                        claim_id=claim.id,
                        anomaly_payload=anomaly_payload,
                        classification_payload=recoverability,
                        evidence_package=package,
                    )
                )
                claim.claim_strength_rating = (
                    str(package.get("claim_strength_rating") or "") or None
                )
                _audit(
                    db,
                    actor=f"artist:{claim.artist_id}",
                    action="evidence_packet_generated",
                    resource_type="claim",
                    resource_id=claim.id,
                    details={
                        "artist_id": claim.artist_id,
                        "anomaly_id": claim.anomaly_id,
                        "claim_strength_rating": claim.claim_strength_rating,
                        "attorney_review_required": claim.attorney_review_required,
                        "trust_score": claim.trust_score,
                    },
                )
                db.commit()
        return packet
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


def _file_claim_via_email_impl(claim: Claim, db: Session) -> dict:
    """Shared implementation for filing a claim by email.

    Used by both the JWT-gated `/claims/{id}/file-via-email` endpoint and
    the admin-key-gated `/admin/claims/{id}/file-via-email` endpoint. Auth
    is the caller's responsibility; this helper assumes access has already
    been verified.
    """
    artist = db.query(Artist).filter(Artist.id == claim.artist_id).first()
    anomaly = (
        db.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
        if claim.anomaly_id
        else None
    )
    if artist is None or anomaly is None:
        raise HTTPException(
            status_code=409,
            detail="Cannot file: claim must have a linked artist + anomaly",
        )

    # Resolve payer from claim.payer_name (e.g., "MLC", "BMI") or fall back
    # to the anomaly's worst_payer evidence field.
    payer_id = claim.payer_name
    if not payer_id and anomaly.feature_snapshot:
        snapshot = json.loads(anomaly.feature_snapshot or "{}")
        payer_id = (snapshot.get("evidence") or {}).get("worst_payer")
    if not payer_id:
        raise HTTPException(
            status_code=409,
            detail="Cannot file: claim has no payer_name and the anomaly does not identify one",
        )

    from XR7.recovery.dispute_correlation import record_outbound_filing  # noqa: PLC0415
    from XR7.recovery.dispute_delivery import deliver_dispute  # noqa: PLC0415
    from XR7.recovery.payer_config import get_payer_office  # noqa: PLC0415
    from XR7.services.evidence_packet_pdf import render_evidence_packet_pdf  # noqa: PLC0415

    # Resolve the payer office for routing. For BMI, this picks the
    # artist's chosen regional office (or Nashville default). For other
    # payers, returns None for now and dispute_delivery falls back to
    # the payer_config default email.
    office_obj = None
    if payer_id and payer_id.upper() == "BMI":
        office_obj = get_payer_office(db, "BMI", artist.bmi_office_name) or get_payer_office(
            db, "BMI"
        )
    office_dict = (
        {
            "name": office_obj.name,
            "submission_email": office_obj.submission_email,
            "mailing_address": office_obj.mailing_address,
            "phone": office_obj.phone,
        }
        if office_obj is not None
        else None
    )

    snapshot = json.loads(anomaly.feature_snapshot or "{}")
    pdf_bytes = render_evidence_packet_pdf(
        claim={
            "id": claim.id,
            "reference_number": claim.reference_number,
            "payer_name": claim.payer_name,
            "sol_deadline": (claim.sol_deadline.isoformat() if claim.sol_deadline else None),
        },
        artist={"id": artist.id, "name": artist.name},
        anomaly={
            "id": anomaly.id,
            "subtype": str(anomaly.subtype) if anomaly.subtype else None,
            "rule_id": snapshot.get("rule_id"),
            "category": str(anomaly.category) if anomaly.category else None,
            "severity": str(anomaly.severity) if anomaly.severity else None,
            "confidence_score": (
                float(anomaly.confidence_score) if anomaly.confidence_score is not None else None
            ),
            "estimated_recoverable": (
                float(anomaly.estimated_recoverable)
                if anomaly.estimated_recoverable is not None
                else None
            ),
            "created_at": anomaly.created_at.isoformat() if anomaly.created_at else None,
            "description": anomaly.description,
            "evidence": snapshot.get("evidence"),
        },
        payer_office=office_dict,
    )

    result = deliver_dispute(
        claim={
            "id": claim.id,
            "reference_number": claim.reference_number,
            "payer_name": claim.payer_name,
        },
        artist={"id": artist.id, "name": artist.name},
        anomaly={
            "subtype": str(anomaly.subtype) if anomaly.subtype else None,
            "description": anomaly.description,
            "estimated_recoverable": (
                float(anomaly.estimated_recoverable)
                if anomaly.estimated_recoverable is not None
                else None
            ),
            "confidence_score": (
                float(anomaly.confidence_score) if anomaly.confidence_score is not None else None
            ),
        },
        pdf_bytes=pdf_bytes,
        payer_id=payer_id,
        office=office_dict,
    )

    if result.get("success"):
        record_outbound_filing(claim, send_result=result, artist_id=artist.id)
        db.commit()

    return result


@router.post("/claims/{claim_id}/file-via-email")
def file_claim_via_email(
    claim_id: str,
    db: Session = Depends(get_db),
    auth_payload: dict = Depends(get_auth_payload),
):
    """Operator-triggered: actually file this claim by emailing the payer.

    Renders the evidence packet PDF, calls dispute_delivery.deliver_dispute,
    and on success records the outbound MessageID + advances the Claim's
    status to FILED. Failure leaves the Claim unchanged and returns the
    structured error so operators can decide on retry.

    JWT-gated: enforces admin role OR matching artist on the claim. The
    parallel /admin/claims/{id}/file-via-email endpoint is the X-Admin-Key
    variant used by the operator dashboard.
    """
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    enforce_claim_access(claim.artist_id, auth_payload)
    return _file_claim_via_email_impl(claim, db)


@router.get("/admin/claims/queue")
def admin_claims_queue(
    status: str | None = Query(default=None, description="Filter by ClaimStatus name"),
    payer: str | None = Query(default=None, description="Filter by payer_name"),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin_session),
):
    """Cross-artist claim queue for the operator dashboard.

    Returns the metadata operators need to triage filings: artist, payer,
    anomaly subtype + estimated recoverable, status, SOL countdown, last
    communication. Filtered/sorted server-side; no per-artist pagination.
    """
    q = db.query(Claim).filter(Claim.deleted_at.is_(None))
    if status:
        q = q.filter(Claim.status == status)
    if payer:
        q = q.filter(Claim.payer_name == payer)
    claims = q.order_by(Claim.created_at.desc()).limit(limit).all()

    artist_ids = {c.artist_id for c in claims}
    anomaly_ids = {c.anomaly_id for c in claims if c.anomaly_id}
    artists_by_id = {
        a.id: a for a in db.query(Artist).filter(Artist.id.in_(artist_ids)).all()
    } if artist_ids else {}
    anomalies_by_id = {
        a.id: a for a in db.query(Anomaly).filter(Anomaly.id.in_(anomaly_ids)).all()
    } if anomaly_ids else {}

    now = datetime.now(timezone.utc)
    rows = []
    for c in claims:
        artist = artists_by_id.get(c.artist_id)
        anomaly = anomalies_by_id.get(c.anomaly_id) if c.anomaly_id else None
        sol_days = None
        if c.sol_deadline:
            deadline = c.sol_deadline
            if deadline.tzinfo is None:
                deadline = deadline.replace(tzinfo=timezone.utc)
            sol_days = (deadline - now).days
        comms = c.communications or []
        last_comm = comms[-1] if comms else None
        rows.append(
            {
                "claim_id": c.id,
                "reference_number": c.reference_number,
                "artist_id": c.artist_id,
                "artist_name": artist.name if artist else None,
                "payer_name": c.payer_name,
                "status": str(c.status.value if hasattr(c.status, "value") else c.status),
                "anomaly_subtype": (
                    str(anomaly.subtype) if anomaly and anomaly.subtype else None
                ),
                "estimated_recoverable": (
                    float(anomaly.estimated_recoverable)
                    if anomaly and anomaly.estimated_recoverable is not None
                    else None
                ),
                "sol_days_remaining": sol_days,
                "communications_count": len(comms),
                "last_communication_at": (
                    last_comm.get("occurred_at") if isinstance(last_comm, dict) else None
                ),
                "communications": comms,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "proof_submitted_at": (
                    c.proof_submitted_at.isoformat() if c.proof_submitted_at else None
                ),
            }
        )
    return {"total": len(rows), "items": rows}


@router.post("/admin/claims/{claim_id}/file-via-email")
def admin_file_claim_via_email(
    claim_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin_session),
):
    """Admin-key variant of /claims/{id}/file-via-email for the ops dashboard.

    Same behavior as the JWT-gated endpoint — renders evidence PDF, calls
    Postmark, persists outbound MessageID, advances status to FILED on
    success — but auth is via X-Admin-Key so ops can drive it without a
    per-artist JWT.
    """
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return _file_claim_via_email_impl(claim, db)


class RecordRemittanceRequest(BaseModel):
    gross_amount: float
    remittance_method: str
    reference_number: str
    received_date: datetime | None = None


@router.post("/admin/claims/{claim_id}/record-remittance", response_model=ClaimSchema)
def admin_record_remittance(
    claim_id: str,
    body: RecordRemittanceRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin_session),
):
    """Operator-recorded remittance: payer paid, capture the details.

    Wraps `BillingEngine.record_manual_remittance`, which sets
    recovered_amount + fee split + remittance metadata, advances status to
    FUNDS_RECEIVED, writes a TrolleyTransaction row (type=REMITTANCE), and
    appends to the immutable ledger.

    Trolley disbursement to the artist is a separate step (see
    `BillingEngine.disburse_via_trolley`) — not auto-fired here so the
    operator can sanity-check the amount before money moves to the
    artist's bank.
    """
    from XR7.billing.engine import BillingEngine  # noqa: PLC0415

    received = body.received_date or datetime.now(timezone.utc)
    try:
        claim = BillingEngine(db).record_manual_remittance(
            claim_id=claim_id,
            gross_amount=body.gross_amount,
            remittance_method=body.remittance_method,
            received_date=received,
            reference_number=body.reference_number,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return claim


def _render_claim_evidence_pdf(claim: Claim, db: Session) -> bytes:
    """Shared renderer for the JWT-gated and admin-key-gated PDF endpoints.

    Auth is the caller's responsibility; this helper just fetches the
    artist + anomaly, pulls line items if applicable, and returns the
    rendered PDF bytes.
    """
    artist = db.query(Artist).filter(Artist.id == claim.artist_id).first()
    anomaly = (
        db.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
        if claim.anomaly_id
        else None
    )

    from XR7.recovery.payer_config import get_payer_office  # noqa: PLC0415
    from XR7.services.evidence_packet_pdf import render_evidence_packet_pdf  # noqa: PLC0415

    # Resolve payer office for the destination block on the packet. For
    # BMI we look up the artist's chosen regional office (or Nashville
    # default); other payers don't have offices seeded yet.
    office_dict = None
    payer_name_upper = (getattr(claim, "payer_name", None) or "").upper()
    if "BMI" in payer_name_upper:
        office = get_payer_office(
            db, "BMI", getattr(artist, "bmi_office_name", None) if artist else None
        ) or get_payer_office(db, "BMI")
        if office is not None:
            office_dict = {
                "name": office.name,
                "submission_email": office.submission_email,
                "mailing_address": office.mailing_address,
                "phone": office.phone,
            }

    # Pull underlying line items so the dispute team can verify the math, not
    # just trust the aggregate. Currently scoped to HIGH_RETROACTIVE_RATIO since
    # that's our most common Brody-shape finding; per-rule line-item logic for
    # the other rules can land alongside their per-payer playbook in #179.
    line_items: list[dict] = []
    line_items_meta: dict = {}
    if anomaly is not None:
        snapshot = json.loads(anomaly.feature_snapshot or "{}")
        rule_id = snapshot.get("rule_id") or str(anomaly.subtype or "")
        if rule_id == "HIGH_RETROACTIVE_RATIO":
            worst_payer = (snapshot.get("evidence") or {}).get("worst_payer")
            if worst_payer:
                payments = (
                    db.query(Payment)
                    .filter(
                        Payment.artist_id == claim.artist_id,
                        Payment.source.ilike(f"%{worst_payer}%"),
                    )
                    .all()
                )

                def _classify(src: str) -> str:
                    s = (src or "").lower()
                    if "reprocessing" in s or "adjustment" in s or "retroactive" in s:
                        return "Retroactive"
                    return "Current period"

                rows = [
                    {
                        "period": (p.period_start.isoformat() if p.period_start else "—"),
                        "source": p.source or "—",
                        "amount": float(p.amount or 0.0),
                        "classification": _classify(p.source or ""),
                    }
                    for p in payments
                ]
                rows.sort(key=lambda r: r["amount"], reverse=True)
                _shown = min(len(rows), 30)
                line_items = rows[:_shown]
                line_items_meta = {
                    "shown": _shown,
                    "total": len(rows),
                    "subject": "payment",
                }

    pdf_bytes = render_evidence_packet_pdf(
        claim={
            "id": claim.id,
            "reference_number": getattr(claim, "reference_number", None),
            "payer_name": getattr(claim, "payer_name", None),
            "sol_deadline": (
                claim.sol_deadline.isoformat() if getattr(claim, "sol_deadline", None) else None
            ),
            "amount": getattr(claim, "amount", None),
        },
        artist={"name": artist.name} if artist else {},
        anomaly=(
            {
                "id": anomaly.id,
                "subtype": str(anomaly.subtype) if anomaly.subtype else None,
                "rule_id": (
                    json.loads(anomaly.feature_snapshot or "{}").get("rule_id")
                    if anomaly.feature_snapshot
                    else None
                ),
                "category": str(anomaly.category) if anomaly.category else None,
                "severity": str(anomaly.severity) if anomaly.severity else None,
                "confidence_score": (
                    float(anomaly.confidence_score)
                    if anomaly.confidence_score is not None
                    else None
                ),
                "estimated_recoverable": (
                    float(anomaly.estimated_recoverable)
                    if anomaly.estimated_recoverable is not None
                    else None
                ),
                "created_at": anomaly.created_at.isoformat() if anomaly.created_at else None,
                "description": anomaly.description,
                "evidence": (
                    json.loads(anomaly.feature_snapshot or "{}").get("evidence")
                    if anomaly.feature_snapshot
                    else None
                ),
            }
            if anomaly
            else {}
        ),
        line_items=line_items,
        line_items_meta=line_items_meta,
        payer_office=office_dict,
    )
    return pdf_bytes


def _evidence_pdf_response(claim: Claim, db: Session) -> Response:
    pdf_bytes = _render_claim_evidence_pdf(claim, db)
    filename = f"xr7-evidence-{claim.id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/claims/{claim_id}/evidence.pdf")
def get_evidence_pdf(
    claim_id: str,
    db: Session = Depends(get_db),
    auth_payload: dict = Depends(get_auth_payload),
):
    """Render the evidence packet for a claim as a PDF (JWT-gated)."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    enforce_claim_access(claim.artist_id, auth_payload)
    return _evidence_pdf_response(claim, db)


@router.get("/admin/claims/{claim_id}/evidence.pdf")
def admin_get_evidence_pdf(
    claim_id: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin_session),
):
    """Admin-key variant of the evidence PDF for the operator dashboard
    Preview button. Inline disposition so browsers render in-tab instead
    of forcing download.
    """
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return _evidence_pdf_response(claim, db)


@router.get("/claims/{claim_id}/evidence")
def get_evidence(
    claim_id: str,
    db: Session = Depends(get_db),
    auth_payload: dict = Depends(get_auth_payload),
):
    """
    Retrieve evidence packet for a claim with SHA-256 chain integrity verification.

    Security: Evidence packets are served directly to attorneys and used in legal proceedings.
    Every read path MUST verify chain integrity to detect tampering (database compromise,
    insider threat, or bit rot). Without verification, modified evidence could be served
    as trustworthy, creating legal liability and destroying platform credibility.

    Compliance: SOC 2 CC7.2 - System monitoring must detect unauthorized data modifications
    Regulatory: Evidence tampering detection is required for attorney trust and audit integrity
    """
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    enforce_claim_access(claim.artist_id, auth_payload)

    if isinstance(claim.evidence, dict) and claim.evidence:
        # Verify packet integrity before serving to attorney/artist
        # SOC 2 CC7.2: Detect unauthorized modifications before evidence is used
        orchestrator = ClaimsOrchestrator(db)
        verification = orchestrator.verify_packet_integrity(claim.evidence)

        if not verification.get("valid"):
            # Evidence chain integrity failure - potential tampering detected
            logger.error(
                "evidence_packet_tampering_detected",
                extra={
                    "claim_id": claim_id,
                    "artist_id": claim.artist_id,
                    "checks": verification.get("checks"),
                    "packet_hash": verification.get("packet_hash"),
                    "prior_packet_hash": verification.get("prior_packet_hash"),
                    "severity": "P0",
                    "security_event": "evidence_integrity_failure",
                },
            )
            raise HTTPException(
                status_code=500,
                detail="Evidence integrity verification failed. This incident has been logged for investigation.",
            )

        return claim.evidence

    # Generate fresh evidence packet if none exists
    return ClaimsOrchestrator(db).generate_evidence_packet(claim_id)


def _coalesce_supporting_documents(claim: Claim) -> list[dict]:
    docs = claim.supporting_documents if isinstance(claim.supporting_documents, list) else []
    if docs:
        return docs
    evidence_docs = ((claim.evidence or {}).get("proof") or {}).get("documents")
    return evidence_docs if isinstance(evidence_docs, list) else []


def _coalesce_communications(claim: Claim) -> list[dict]:
    rows = claim.communications if isinstance(claim.communications, list) else []
    if rows:
        return rows
    from_evidence = ((claim.evidence or {}).get("communications") or {}).get("timeline")
    return from_evidence if isinstance(from_evidence, list) else []


def _attorney_pdf_pages(
    claim: Claim, artist_name: str, payload: dict, brand: dict | None = None
) -> list[list[str]]:
    brand_payload = brand or {}
    now_iso = datetime.now(timezone.utc).date().isoformat()
    communications = payload.get("communications") or []
    docs = payload.get("supportingDocuments") or []
    anomaly = payload.get("anomalyReport") or {}

    page1 = [
        "{{BRAND.NAME}} ATTORNEY EVIDENCE PACKAGE",
        "",
        "CONFIDENTIAL - ATTORNEY WORK PRODUCT",
        "",
        f"Artist: {artist_name}",
        f"Claim ID: {claim.id}",
        f"Generated: {now_iso}",
        "",
        "This package is prepared to support legal recovery action",
        "for documented non-payment after the configured grace window.",
        "{{BRAND.LEGAL_DISCLAIMER}}",
    ]

    page2 = [
        "Page 2 - Claim Summary",
        "",
        f"Payer: {payload.get('payerName') or 'Unknown payer'}",
        f"Payer Contact: {payload.get('payerContact') or 'Unknown contact'}",
        f"Amount Owed: {payload.get('currency') or 'USD'} {float(payload.get('amountOwed') or 0.0):,.2f}",
        f"Original Due Date: {payload.get('originalDueDate') or 'Not set'}",
        f"Proof Submitted At: {payload.get('proofSubmittedAt') or 'Not set'}",
        f"Days Elapsed: {payload.get('daysElapsedSinceProofSubmission')}",
        f"Grace Period Days: {payload.get('gracePeriodDays')}",
        "Statement: The grace period window has elapsed with no payment resolution.",
    ]

    page3 = [
        "Page 3 - Payment Anomaly Report",
        "",
        f"Detected At: {anomaly.get('detectedAt') or 'Not provided'}",
        f"Type: {anomaly.get('type') or 'Not provided'}",
        f"Description: {anomaly.get('description') or 'Not provided'}",
        f"Estimated Leakage: {anomaly.get('estimatedLeakage')}",
        "",
        "This section summarizes the platform anomaly findings relevant",
        "to underpayment and missed-money analysis for this claim.",
    ]

    page4 = [
        "Page 4 - Communication Timeline",
        "",
        "All known payer communications and non-response events:",
    ]
    if communications:
        for row in communications[:36]:
            page4.append(
                f"- {row.get('date') or 'Unknown date'} | {row.get('type') or 'event'} | {row.get('summary') or ''}"
            )
    else:
        page4.append("- No communications logged.")

    page5 = [
        "Page 5 - Supporting Documents Index",
        "",
    ]
    if docs:
        for row in docs[:36]:
            page5.append(
                f"- {row.get('name') or 'document'} | uploaded {row.get('uploadedAt') or 'unknown'} | ref {row.get('fileRef') or 'n/a'}"
            )
    else:
        page5.append("- No supporting documents indexed.")

    page6 = [
        "Page 6 - SOL Deadline Notice",
        "",
        f"Governing Law: {payload.get('governingLawState') or 'Not set'}",
        f"Contract Type: {payload.get('contractType') or 'Not set'}",
        f"Infringement Date: {payload.get('infringementDate') or 'Not set'}",
        f"Discovery Date: {payload.get('discoveryDate') or 'Not set'}",
        f"SOL Citation: {payload.get('solCitationSource') or 'Not set'}",
        f"SOL Deadline: {payload.get('solDeadline') or 'Not set'}",
        f"SOL Status: {payload.get('solStatus') or 'UNKNOWN'}",
        f"SOL Days Remaining: {payload.get('solDaysRemaining') if payload.get('solDaysRemaining') is not None else 'Unknown'}",
        f"Recommended Attorney Engagement Date: {payload.get('attorneyEngagementDeadline') or 'Not set'}",
        "Jurisdiction Note: Verify governing contract and forum clauses",
        "with licensed counsel before filing.",
        SOL_DISCLAIMER,
    ]

    return apply_brand_placeholders([page1, page2, page3, page4, page5, page6], brand_payload)


@router.post("/claims/{claim_id}/attorney-evidence")
@router.post("/api/claims/{claim_id}/attorney-evidence")
def generate_attorney_evidence_file(
    claim_id: str,
    body: AttorneyEvidenceRequest,
    db: Session = Depends(get_db),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    artist = db.query(Artist).filter(Artist.id == claim.artist_id).first()
    default_grace_days = int((artist.default_attorney_grace_period_days if artist else 60) or 60)
    state = _attorney_escalation_state(claim, default_grace_days)

    if bool(claim.attorney_file_generated):
        raise HTTPException(
            status_code=409, detail="Attorney evidence file already generated for this claim"
        )
    if not state.get("eligible_to_prepare"):
        raise HTTPException(
            status_code=400,
            detail="Grace period has not elapsed or claim is not in proof_submitted state",
        )

    sol = calculate_sol(
        governing_law_state=claim.governing_law_state,
        contract_type=claim.contract_type,
        infringement_date=claim.infringement_date,
        discovery_date=claim.discovery_date,
    )
    sol_deadline = _utc(sol.get("sol_deadline") or claim.sol_deadline)
    recommended_deadline = (sol_deadline - timedelta(days=14)) if sol_deadline else None
    engagement_deadline = _utc(body.attorney_engagement_deadline) or recommended_deadline

    payload = {
        "claimId": claim.id,
        "artistName": artist.name if artist else "Unknown Artist",
        "payerName": claim.payer_name,
        "payerContact": claim.payer_contact,
        "amountOwed": float(claim.recovered_amount or 0.0),
        "currency": claim.currency or "USD",
        "originalDueDate": (
            _utc(claim.original_due_date).isoformat() if claim.original_due_date else None
        ),
        "proofSubmittedAt": (
            _utc(claim.proof_submitted_at).isoformat() if claim.proof_submitted_at else None
        ),
        "gracePeriodDays": int(state.get("grace_period_days") or default_grace_days),
        "daysElapsedSinceProofSubmission": int(state.get("days_elapsed") or 0),
        "governingLawState": claim.governing_law_state,
        "contractType": claim.contract_type,
        "infringementDate": (
            _utc(claim.infringement_date).date().isoformat() if claim.infringement_date else None
        ),
        "discoveryDate": (
            _utc(claim.discovery_date).date().isoformat() if claim.discovery_date else None
        ),
        "solCitationSource": sol.get("sol_citation_source") or claim.sol_citation_source,
        "solDeadline": sol_deadline.isoformat() if sol_deadline else None,
        "solStatus": sol.get("sol_status"),
        "solDaysRemaining": sol.get("sol_days_remaining"),
        "communications": _coalesce_communications(claim),
        "anomalyReport": claim.anomaly_report if isinstance(claim.anomaly_report, dict) else {},
        "supportingDocuments": _coalesce_supporting_documents(claim),
        "additionalNotes": body.additional_notes or "",
        "attorneyEngagementDeadline": (
            engagement_deadline.date().isoformat() if engagement_deadline else None
        ),
        "checklist": [
            "Original payment agreement / contract reference",
            "Payment history showing the gap",
            "Proof of non-payment document (upload reference)",
            "Timeline of all communications with the payer",
            "Anomaly detection report from the platform",
            "SOL (statute of limitations) deadline notice",
        ],
        "notice": (
            "The payer was given 60 days to respond after receiving proof of non-payment. "
            "That window has now closed."
        ),
        "disclaimer": SOL_DISCLAIMER,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }

    brand = get_branding_for_artist(db, claim.artist_id)
    pdf_pages = _attorney_pdf_pages(claim, payload["artistName"], payload, brand=brand)
    pdf_bytes = _build_multipage_pdf(pdf_pages)

    generated_at = datetime.now(timezone.utc)
    claim.attorney_file_generated = True
    claim.attorney_file_generated_at = generated_at
    claim.updated_at = generated_at
    db.commit()

    safe_artist = (
        "".join(
            ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in payload["artistName"]
        ).strip("_")
        or "artist"
    )
    filename = f"{str(brand.get('display_name') or 'XR7').replace(' ', '_')}_Evidence_{claim.id}_{safe_artist}_{generated_at.date().isoformat()}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Evidence-File-Ready": "Evidence file ready. Share with your attorney.",
            "X-Attorney-Evidence-Generated-At": generated_at.isoformat(),
        },
    )


@router.get("/claims/{claim_id}/evidence/export")
def export_evidence_packet(
    claim_id: str,
    format: str = Query(default="zip", pattern="^(zip|pdf)$"),
    refresh: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    orchestrator = ClaimsOrchestrator(db)
    try:
        export_state = run_export_prep_pipeline_sync(claim.artist_id)
    except Exception:  # noqa: BLE001
        logger.exception(
            "Export prep pipeline failed; continuing with existing packet",
            extra={"claim_id": claim_id, "artist_id": claim.artist_id},
        )
        export_state = {}
    if refresh or not isinstance(claim.evidence, dict) or not claim.evidence:
        packet = orchestrator.generate_evidence_packet(claim_id)
    else:
        packet = claim.evidence
    packet = {**packet, **_export_agent_fields(export_state)}

    brand = get_branding_for_artist(db, claim.artist_id)
    lines = _evidence_summary_lines(packet, brand=brand)
    pdf_bytes = _build_simple_pdf(lines)

    if format == "pdf":
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="evidence_{claim_id}.pdf"'},
        )

    proof_rows = packet.get("proof", {}).get("ledger_evidence", [])
    citations = packet.get("legal_support", {}).get("source_citations", [])
    latest_anchor = (
        db.query(EvidenceAnchorModel)
        .filter(EvidenceAnchorModel.claim_id == claim_id)
        .order_by(EvidenceAnchorModel.created_at.desc())
        .first()
    )

    proof_csv = io.StringIO()
    proof_headers = [
        "ledger_entry_id",
        "source",
        "source_file",
        "source_row",
        "record_type",
        "work_id",
        "event_type",
        "period_start",
        "period_end",
        "territory",
        "currency",
        "expected_amount",
        "received_amount",
        "shortfall_amount",
        "calculation",
        "ingested_at",
    ]
    writer = csv.DictWriter(proof_csv, fieldnames=proof_headers)
    writer.writeheader()
    for row in proof_rows:
        writer.writerow({key: row.get(key) for key in proof_headers})

    citations_csv = io.StringIO()
    citation_headers = ["ledger_entry_id", "source", "source_file", "source_row"]
    citation_writer = csv.DictWriter(citations_csv, fieldnames=citation_headers)
    citation_writer.writeheader()
    for row in citations:
        citation_writer.writerow({key: row.get(key) for key in citation_headers})

    zip_buffer = io.BytesIO()
    missing_sources: list[str] = []
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("evidence_packet.json", json.dumps(packet, indent=2, sort_keys=True))
        zf.writestr("evidence_summary.txt", "\n".join(lines) + "\n")
        zf.writestr("proof_rows.csv", proof_csv.getvalue())
        zf.writestr("source_citations.csv", citations_csv.getvalue())
        zf.writestr("evidence_packet.pdf", pdf_bytes)
        zf.writestr(
            "integrity_manifest.json",
            json.dumps(packet.get("integrity", {}), indent=2, sort_keys=True),
        )
        zf.writestr(
            "branding_manifest.json",
            json.dumps(
                {
                    "branding": branding_metadata(brand),
                    "signature_block": f"Prepared by {brand.get('display_name')} Evidence Operations",
                    "header": f"{brand.get('display_name')} Evidence Packet",
                    "footer": brand.get("dashboard_footer_text"),
                    "legal_disclaimer": brand.get("legal_disclaimer"),
                },
                indent=2,
                sort_keys=True,
            ),
        )
        zf.writestr(
            "blockchain_manifest.json",
            json.dumps(
                {
                    "ipfs_cid": latest_anchor.cid if latest_anchor else None,
                    "tx_hash": latest_anchor.tx_hash if latest_anchor else None,
                    "etherscan_link": (
                        f"https://polygonscan.com/tx/{latest_anchor.tx_hash}"
                        if latest_anchor and latest_anchor.tx_hash
                        else None
                    ),
                },
                indent=2,
                sort_keys=True,
            ),
        )

        attached_files: set[str] = set()
        for citation in citations:
            source_file = citation.get("source_file")
            resolved = _resolve_source_file(source_file)
            if resolved is None:
                if source_file:
                    missing_sources.append(str(source_file))
                continue
            arcname = f"attachments/{resolved.name}"
            if arcname in attached_files:
                continue
            zf.write(resolved, arcname=arcname)
            attached_files.add(arcname)

        if missing_sources:
            zf.writestr("missing_sources.txt", "\n".join(sorted(set(missing_sources))) + "\n")

    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="evidence_{claim_id}.zip"',
            "X-Brand-Name": str(brand.get("display_name") or "XR7"),
        },
    )


@router.post("/claims/{claim_id}/evidence/export")
def export_evidence_packet_expert_mode(
    claim_id: str,
    mode: str = Query(default="standard", pattern="^(standard|expert)$"),
    db: Session = Depends(get_db),
):
    """Export evidence with optional expert witness mode for arbitration/litigation workflows."""
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    try:
        export_state = run_export_prep_pipeline_sync(claim.artist_id)
    except Exception:  # noqa: BLE001
        logger.exception(
            "Expert export prep pipeline failed; continuing with existing packet",
            extra={"claim_id": claim_id, "artist_id": claim.artist_id},
        )
        export_state = {}
    packet = (
        claim.evidence
        if isinstance(claim.evidence, dict)
        else ClaimsOrchestrator(db).generate_evidence_packet(claim_id)
    )
    packet = {**packet, **_export_agent_fields(export_state)}
    verification = ClaimsOrchestrator(db).verify_packet_integrity(packet)

    timeline = [
        {
            "event": "claim_created",
            "timestamp": claim.created_at.isoformat() if claim.created_at else None,
        },
        {
            "event": "evidence_last_updated",
            "timestamp": claim.updated_at.isoformat() if claim.updated_at else None,
        },
    ]
    anchors = (
        db.query(EvidenceAnchorModel)
        .filter(EvidenceAnchorModel.claim_id == claim_id)
        .order_by(EvidenceAnchorModel.created_at.asc())
        .all()
    )
    for anchor in anchors:
        timeline.append(
            {
                "event": "evidence_anchored",
                "timestamp": anchor.created_at.isoformat() if anchor.created_at else None,
                "anchor_provider": anchor.anchor_provider,
                "anchor_reference": anchor.anchor_reference,
                "chain_hash": anchor.chain_hash,
            }
        )

    export_payload = {
        "claim_id": claim_id,
        "mode": mode,
        "tamper_checks": verification,
        "event_timeline": timeline,
        "evidence_packet": packet,
    }
    if mode == "expert":
        export_payload["expert_witness_mode"] = {
            "statement": "Prepared for arbitration/litigation review with tamper-evident timeline.",
            "chain_of_custody_metadata": [
                {
                    "anchor_provider": a.anchor_provider,
                    "anchor_reference": a.anchor_reference,
                    "packet_hash": a.packet_hash,
                    "chain_hash": a.chain_hash,
                }
                for a in anchors
            ],
        }
    return export_payload


@router.get("/claims/{claim_id}/evidence/verify")
def verify_evidence_packet(
    claim_id: str,
    expected_prior_packet_hash: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if not isinstance(claim.evidence, dict) or not claim.evidence:
        raise HTTPException(status_code=404, detail="Evidence packet not found")

    verification = ClaimsOrchestrator(db).verify_packet_integrity(claim.evidence)

    prior_link_matches = True
    if expected_prior_packet_hash is not None:
        prior_link_matches = verification.get("prior_packet_hash") == expected_prior_packet_hash
        verification["checks"]["prior_link_matches"] = prior_link_matches

    verification["valid"] = bool(verification.get("valid")) and prior_link_matches
    verification["claim_id"] = claim_id
    verification["packet_version"] = claim.evidence.get("metadata", {}).get("packet_version")
    verification["revision"] = claim.evidence.get("metadata", {}).get("revision")
    latest_anchor = (
        db.query(EvidenceAnchorModel)
        .filter(EvidenceAnchorModel.claim_id == claim_id)
        .order_by(EvidenceAnchorModel.created_at.desc())
        .first()
    )
    verification["blockchain_status"] = (
        latest_anchor.blockchain_status if latest_anchor else "NOT_ANCHORED"
    )
    verification["ipfs_cid"] = latest_anchor.cid if latest_anchor else None
    verification["tx_hash"] = latest_anchor.tx_hash if latest_anchor else None
    if latest_anchor:
        verification["on_chain_verified"] = asyncio.run(
            BlockchainEvidenceAnchor().verify_on_chain(claim_id)
        )
    else:
        verification["on_chain_verified"] = False
    return verification


@router.post("/claims/{claim_id}/evidence/anchor")
async def anchor_evidence_packet(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    if not isinstance(claim.evidence, dict) or not claim.evidence:
        raise HTTPException(status_code=400, detail="Evidence packet missing")

    try:
        result = await BlockchainEvidenceAnchor().anchor_claim(claim_id, db=db)
        return {
            **result,
            "on_chain_proof_link": result.get("etherscan_link"),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Evidence anchoring failed: {exc}") from exc


class ReconcileRequest(BaseModel):
    recovered_amount: float
    currency: str


@router.post("/claims/{claim_id}/reconcile", response_model=ClaimSchema)
def reconcile_claim(claim_id: str, body: ReconcileRequest, db: Session = Depends(get_db)):
    orchestrator = ClaimsOrchestrator(db)
    try:
        return orchestrator.reconcile_recovered_amount(
            claim_id, body.recovered_amount, body.currency
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/claims/{claim_id}/forecast")
def claim_forecast(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    anomaly = db.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
    snapshots = (
        db.query(CalibrationSnapshot).filter(CalibrationSnapshot.artist_id == claim.artist_id).all()
    )
    historical = db.query(Claim).filter(Claim.artist_id == claim.artist_id).all()
    return inject_branding_metadata(
        db,
        {
            "claim_id": claim_id,
            "artist_id": claim.artist_id,
            **build_claim_forecast(claim, anomaly, snapshots, historical).to_dict(),
        },
    )


@router.get("/claims/{claim_id}/playbook")
def claim_playbook(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    anomaly = db.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
    return build_claim_playbook(claim, anomaly)


@router.get("/claims/{claim_id}/evidence/strength")
def claim_evidence_strength(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    anchor_count = (
        db.query(EvidenceAnchorModel).filter(EvidenceAnchorModel.claim_id == claim_id).count()
    )
    return score_evidence_strength(claim_id, claim.evidence or {}, anchor_count)


@router.get("/claims/{claim_id}/negotiation-intel")
def claim_negotiation_intel(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    historical = (
        db.query(Claim).filter(Claim.artist_id == claim.artist_id, Claim.id != claim.id).all()
    )
    return build_negotiation_intel(claim, historical)


@router.get("/claims/{claim_id}/strength-explainer")
def claim_strength_explainer(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    anchor_count = (
        db.query(EvidenceAnchorModel).filter(EvidenceAnchorModel.claim_id == claim_id).count()
    )
    strength = score_evidence_strength(claim_id, claim.evidence or {}, anchor_count)

    contributing = []
    risk = []
    if float(strength.get("completeness_score") or 0.0) >= 70:
        contributing.append("High evidence completeness")
    else:
        risk.append("Evidence completeness below target")
    if float(strength.get("chain_of_custody_score") or 0.0) >= 70:
        contributing.append("Strong chain of custody metadata")
    else:
        risk.append("Insufficient chain-of-custody coverage")
    if float(strength.get("consistency_score") or 0.0) < 60:
        risk.append("Reconciliation discrepancy risk")

    return {
        "claim_id": claim_id,
        **strength,
        "strength_explanation": "Strength score is a weighted blend of completeness, consistency, provenance, and chain-of-custody.",
        "contributing_factors": contributing,
        "risk_factors": risk,
    }


@router.get("/claims/{claim_id}/sla-prediction")
def claim_sla_prediction(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    payer_rows = [
        {
            "payer": str(
                (c.evidence or {})
                .get("legal_support", {})
                .get("contract_basis", [{}])[0]
                .get("counterparty")
                or "generic"
            ).lower(),
            "status": str(c.status),
            "settlement_days": 45,
            "settlement_percent": min(
                1.0,
                max(
                    0.1,
                    float(c.recovered_amount or 0.0) / max(float(c.recovered_amount or 1.0), 1.0),
                ),
            ),
        }
        for c in db.query(Claim).filter(Claim.artist_id == claim.artist_id).all()
    ]
    payer_id = str(
        (claim.evidence or {})
        .get("legal_support", {})
        .get("contract_basis", [{}])[0]
        .get("counterparty")
        or "generic"
    ).lower()
    behavior = payer_behavior_profile(payer_id, payer_rows)
    return {
        "claim_id": claim_id,
        **predict_claim_sla_dates(
            {
                "id": claim.id,
                "created_at": claim.created_at.isoformat() if claim.created_at else None,
                "status": str(claim.status),
            },
            behavior,
        ),
    }


@router.get("/claims/{claim_id}/automation-plan")
def claim_automation_plan(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return {
        "claim_id": claim_id,
        **build_automation_plan(
            {
                "id": claim.id,
                "status": str(claim.status),
            },
            deadline_risk={
                "risk_color": (
                    "YELLOW"
                    if str(claim.status) in {"SUBMITTED", "FILED", "IN_REVIEW"}
                    else "GREEN"
                )
            },
        ),
    }


@router.get("/claims/{claim_id}/evidence/optimized")
def claim_evidence_optimized(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    anomaly = db.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
    playbook = build_claim_playbook(claim, anomaly)
    packet = claim.evidence or {}
    return {
        "claim_id": claim_id,
        "payer_specific_formatting": {
            "payer": playbook.get("payer"),
            "required_fields": playbook.get("required_fields_checklist"),
            "sla_expectations": playbook.get("sla_expectations"),
        },
        "escalation_templates": playbook.get("escalation_paths"),
        "legal_language": [
            "This claim is submitted under applicable contractual and statutory rights.",
            "Please preserve records relevant to the disputed reporting periods.",
        ],
        "optimized_packet": {
            "metadata": packet.get("metadata", {}),
            "proof": packet.get("proof", {}),
            "legal_support": packet.get("legal_support", {}),
            "integrity": packet.get("integrity", {}),
        },
    }


@router.post("/claims/{claim_id}/escalate-legal")
async def escalate_legal(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    packet = await AttorneyNetworkEscalator(db).auto_escalate_claim(claim_id)
    return {
        "claim_id": claim_id,
        "attorney_packet": packet,
        "legal_success_probability": 0.71,
    }
