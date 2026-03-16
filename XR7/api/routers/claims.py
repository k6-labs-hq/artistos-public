import csv
import io
import json
import asyncio
from pathlib import Path
import zipfile
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.auth.event_notifications import send_event_notification
from XR7.blockchain.evidence_anchor import EvidenceAnchor as BlockchainEvidenceAnchor
from XR7.models.base import get_db
from XR7.models.anomaly import Anomaly
from XR7.models.claim import Claim, ClaimSchema
from XR7.models.evidence_anchor import EvidenceAnchor as EvidenceAnchorModel
from XR7.models.ml_feedback import CalibrationSnapshot
from XR7.models.notification_preference import NotificationPreference
from XR7.models.review_queue import ReviewSourceType
from XR7.recovery.cash_recovery_forecast import build_claim_forecast
from XR7.recovery.evidence_strength import score_evidence_strength
from XR7.recovery.negotiation_intelligence import build_negotiation_intel
from XR7.recovery.orchestrator import ClaimsOrchestrator
from XR7.recovery.payer_behavior_model import payer_behavior_profile
from XR7.recovery.payer_playbooks import build_claim_playbook
from XR7.recovery.recovery_automation import build_automation_plan
from XR7.recovery.sla_predictor import predict_claim_sla_dates
from XR7.services.review_queue import enqueue_review_item
from XR7.tasks.hubspot import hubspot_sync_recovery_update

router = APIRouter(tags=["claims"])


def _safe_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_simple_pdf(lines: list[str]) -> bytes:
    # Minimal single-page PDF generator to avoid external dependencies.
    page_lines = lines[:46]
    content_ops = ["BT", "/F1 10 Tf", "50 780 Td", "12 TL"]
    for line in page_lines:
        content_ops.append(f"({_safe_pdf_text(line)}) Tj")
        content_ops.append("T*")
    content_ops.append("ET")
    content = "\n".join(content_ops).encode("utf-8")

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Count 1 /Kids [3 0 R] >> endobj\n")
    objects.append(
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
    )
    objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    objects.append(f"5 0 obj << /Length {len(content)} >> stream\n".encode("utf-8") + content + b"\nendstream endobj\n")

    output = io.BytesIO()
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


def _evidence_summary_lines(packet: dict) -> list[str]:
    anomaly = packet.get("anomaly", {})
    proof = packet.get("proof", {})
    totals = proof.get("totals", {})
    recon = packet.get("reconciliation", {})
    integrity = packet.get("integrity", {})

    return [
        "XR7 Evidence Packet",
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
    ]


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


@router.get("/artists/{artist_id}/claims")
def list_claims(artist_id: str, db: Session = Depends(get_db)):
    claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    snapshots = (
        db.query(CalibrationSnapshot)
        .filter(CalibrationSnapshot.artist_id == artist_id)
        .all()
    )
    historical_claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()

    payload = []
    for claim in claims:
        anomaly = db.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
        forecast = build_claim_forecast(claim, anomaly, snapshots, historical_claims).to_dict()
        payload.append(
            {
                "claim": ClaimSchema.model_validate(claim).model_dump(mode="json"),
                "forecast": forecast,
            }
        )
    return payload


@router.get("/claims/{claim_id}", response_model=ClaimSchema)
def get_claim(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.post("/claims/{claim_id}/advance", response_model=ClaimSchema)
def advance_claim(claim_id: str, db: Session = Depends(get_db)):
    orchestrator = ClaimsOrchestrator(db)
    try:
        existing = db.query(Claim).filter(Claim.id == claim_id).first()
        if not existing:
            raise HTTPException(status_code=404, detail="Claim not found")

        # Only enforce stronger evidence quality checks when packet exists.
        if isinstance(existing.evidence, dict) and existing.evidence:
            anchor_count = db.query(EvidenceAnchorModel).filter(EvidenceAnchorModel.claim_id == claim_id).count()
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
                raise HTTPException(status_code=400, detail="Evidence strength is too low to advance claim")

        updated = orchestrator.advance_claim(claim_id)
        pref = (
            db.query(NotificationPreference)
            .filter(NotificationPreference.artist_id == updated.artist_id)
            .first()
        )
        send_event_notification(
            pref,
            "claim_advanced",
            "Claim status updated",
            f"Claim {updated.id} advanced to {updated.status}.",
            current_hour_utc=datetime.now(timezone.utc).hour,
        )
        status_value = updated.status.value if hasattr(updated.status, "value") else str(updated.status)

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
        if status_value in {"FILED", "IN_REVIEW", "PAID", "CLOSED"}:
            try:
                hubspot_sync_recovery_update.delay(updated.artist_id, event=f"claim_{status_value.lower()}")
            except Exception:  # noqa: BLE001
                pass

        if status_value in {"SUBMITTED", "FILED", "IN_REVIEW"}:
            historical = db.query(Claim).filter(Claim.artist_id == updated.artist_id, Claim.id != updated.id).all()
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
        return packet
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


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
    if refresh or not isinstance(claim.evidence, dict) or not claim.evidence:
        packet = orchestrator.generate_evidence_packet(claim_id)
    else:
        packet = claim.evidence

    lines = _evidence_summary_lines(packet)
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
        zf.writestr("integrity_manifest.json", json.dumps(packet.get("integrity", {}), indent=2, sort_keys=True))
        zf.writestr(
            "blockchain_manifest.json",
            json.dumps(
                {
                    "ipfs_cid": latest_anchor.cid if latest_anchor else None,
                    "tx_hash": latest_anchor.tx_hash if latest_anchor else None,
                    "etherscan_link": f"https://polygonscan.com/tx/{latest_anchor.tx_hash}" if latest_anchor and latest_anchor.tx_hash else None,
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
        headers={"Content-Disposition": f'attachment; filename="evidence_{claim_id}.zip"'},
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

    packet = claim.evidence if isinstance(claim.evidence, dict) else ClaimsOrchestrator(db).generate_evidence_packet(claim_id)
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
    anchors = db.query(EvidenceAnchorModel).filter(EvidenceAnchorModel.claim_id == claim_id).order_by(EvidenceAnchorModel.created_at.asc()).all()
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
    verification["blockchain_status"] = latest_anchor.blockchain_status if latest_anchor else "NOT_ANCHORED"
    verification["ipfs_cid"] = latest_anchor.cid if latest_anchor else None
    verification["tx_hash"] = latest_anchor.tx_hash if latest_anchor else None
    if latest_anchor:
        verification["on_chain_verified"] = asyncio.run(BlockchainEvidenceAnchor().verify_on_chain(claim_id))
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
        result = await BlockchainEvidenceAnchor().anchor_claim(claim_id)
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
        return orchestrator.reconcile_recovered_amount(claim_id, body.recovered_amount, body.currency)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/claims/{claim_id}/forecast")
def claim_forecast(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    anomaly = db.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
    snapshots = db.query(CalibrationSnapshot).filter(CalibrationSnapshot.artist_id == claim.artist_id).all()
    historical = db.query(Claim).filter(Claim.artist_id == claim.artist_id).all()
    return {
        "claim_id": claim_id,
        "artist_id": claim.artist_id,
        **build_claim_forecast(claim, anomaly, snapshots, historical).to_dict(),
    }


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
    anchor_count = db.query(EvidenceAnchorModel).filter(EvidenceAnchorModel.claim_id == claim_id).count()
    return score_evidence_strength(claim_id, claim.evidence or {}, anchor_count)


@router.get("/claims/{claim_id}/negotiation-intel")
def claim_negotiation_intel(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    historical = db.query(Claim).filter(Claim.artist_id == claim.artist_id, Claim.id != claim.id).all()
    return build_negotiation_intel(claim, historical)


@router.get("/claims/{claim_id}/strength-explainer")
def claim_strength_explainer(claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    anchor_count = db.query(EvidenceAnchorModel).filter(EvidenceAnchorModel.claim_id == claim_id).count()
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
            "payer": str((c.evidence or {}).get("legal_support", {}).get("contract_basis", [{}])[0].get("counterparty") or "generic").lower(),
            "status": str(c.status),
            "settlement_days": 45,
            "settlement_percent": min(1.0, max(0.1, float(c.recovered_amount or 0.0) / max(float(c.recovered_amount or 1.0), 1.0))),
        }
        for c in db.query(Claim).filter(Claim.artist_id == claim.artist_id).all()
    ]
    payer_id = str((claim.evidence or {}).get("legal_support", {}).get("contract_basis", [{}])[0].get("counterparty") or "generic").lower()
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
            deadline_risk={"risk_color": "YELLOW" if str(claim.status) in {"SUBMITTED", "FILED", "IN_REVIEW"} else "GREEN"},
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
