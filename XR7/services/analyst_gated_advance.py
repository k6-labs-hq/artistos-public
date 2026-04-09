from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.advance_approval import AdvanceApproval, ApprovalDecision, ApprovalStage
from XR7.models.advance_offer import AdvanceOffer, AdvanceOfferStatus
from XR7.models.advance_opportunity import AdvanceOpportunity, AdvanceOpportunityStatus
from XR7.models.advance_recovery_packet import AdvanceRecoveryPacket
from XR7.models.anomaly import Anomaly
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.liquidity_advance import AdvanceStatus, RecoverableLiquidityAdvance
from XR7.recovery.immutable_ledger import ImmutableLedgerService

MIN_SIGNAL_CONFIDENCE = 0.82
MAX_ADVANCE_PCT_OF_PREDICTED = 0.60
HARD_ADVANCE_CAP = 75_000.0
MAX_EFFECTIVE_FEE_CAP_PERCENT = 24.0
ADVANCE_EXPIRY_DAYS = 7


def _normalize_signer_role(role: str) -> str:
    value = str(role or "").strip().lower()
    if value in {"exec", "executive", "ceo", "cfo"}:
        return "executive"
    if value in {"legal", "counsel", "general_counsel"}:
        return "legal"
    if value == "analyst":
        return "analyst"
    return value


def _fee_band_for_score(score: float) -> float:
    if score >= 0.92:
        return 2.5
    if score >= 0.86:
        return 3.5
    if score >= 0.78:
        return 4.5
    return 6.0


def _ensemble_score(*, anomaly: Anomaly | None, claim: Claim | None) -> dict[str, float]:
    anomaly_conf = float(anomaly.confidence_score or 0.0) if anomaly else 0.0
    claim_stage = (
        str(claim.status.value if isinstance(claim.status, ClaimStatus) else claim.status)
        if claim
        else ""
    )
    claim_stage_boost = 0.0
    if claim_stage in {"IN_REVIEW", "SUBMITTED", "FILED"}:
        claim_stage_boost = 0.08
    if claim_stage in {"ACCEPTED", "FUNDS_RECEIVED"}:
        claim_stage_boost = 0.12

    recoverable = 0.0
    if anomaly and anomaly.estimated_recoverable is not None:
        recoverable = float(anomaly.estimated_recoverable)
    elif claim and claim.recovered_amount is not None:
        recoverable = float(claim.recovered_amount)

    amount_signal = min(1.0, max(0.0, recoverable / 50_000.0))

    calibration_model = round(min(1.0, 0.75 * anomaly_conf + 0.25 * amount_signal), 4)
    historical_model = round(
        min(1.0, 0.70 * anomaly_conf + 0.30 * (amount_signal + claim_stage_boost)), 4
    )
    legal_model = round(min(1.0, 0.80 * anomaly_conf + 0.20 * (0.60 + claim_stage_boost)), 4)
    ensemble = round((calibration_model + historical_model + legal_model) / 3.0, 4)
    return {
        "calibration_model": calibration_model,
        "historical_model": historical_model,
        "legal_model": legal_model,
        "ensemble": ensemble,
    }


def _has_unrepaid_active_advance(db: Session, artist_id: str) -> bool:
    row = (
        db.query(RecoverableLiquidityAdvance)
        .filter(
            RecoverableLiquidityAdvance.artist_id == artist_id,
            RecoverableLiquidityAdvance.status.in_(
                [AdvanceStatus.ACCEPTED, AdvanceStatus.DISBURSED]
            ),
        )
        .first()
    )
    return row is not None


def run_nightly_advance_opportunity_scan(db: Session) -> dict[str, Any]:
    created = 0
    skipped = 0

    candidate_anomalies = (
        db.query(Anomaly).filter(Anomaly.confidence_score >= MIN_SIGNAL_CONFIDENCE).all()
    )
    anomalies = []
    for anomaly in candidate_anomalies:
        status_value = str(getattr(anomaly, "status", "") or "")
        if status_value.endswith("OPEN"):
            anomalies.append(anomaly)

    for anomaly in anomalies:
        existing = (
            db.query(AdvanceOpportunity)
            .filter(
                AdvanceOpportunity.artist_id == anomaly.artist_id,
                AdvanceOpportunity.anomaly_id == anomaly.id,
                AdvanceOpportunity.status.in_(
                    [
                        AdvanceOpportunityStatus.QUEUED_ANALYST,
                        AdvanceOpportunityStatus.ANALYST_APPROVED,
                        AdvanceOpportunityStatus.QUEUED_EXEC,
                        AdvanceOpportunityStatus.EXEC_APPROVED,
                        AdvanceOpportunityStatus.OFFER_GENERATED,
                    ]
                ),
            )
            .first()
        )
        if existing:
            skipped += 1
            continue

        claim = (
            db.query(Claim)
            .filter(
                Claim.artist_id == anomaly.artist_id,
                Claim.anomaly_id == anomaly.id,
                Claim.status.in_(
                    [
                        ClaimStatus.FILED,
                        ClaimStatus.SUBMITTED,
                        ClaimStatus.IN_REVIEW,
                        ClaimStatus.ACCEPTED,
                    ]
                ),
            )
            .order_by(Claim.updated_at.desc())
            .first()
        )

        scores = _ensemble_score(anomaly=anomaly, claim=claim)
        ensemble = float(scores["ensemble"])
        predicted = float(anomaly.estimated_recoverable or 0.0)
        if predicted <= 0 or ensemble < MIN_SIGNAL_CONFIDENCE:
            skipped += 1
            continue

        max_advance = round(min(predicted * MAX_ADVANCE_PCT_OF_PREDICTED, HARD_ADVANCE_CAP), 2)
        if max_advance <= 0:
            skipped += 1
            continue

        fee_percent = _fee_band_for_score(ensemble)
        opp = AdvanceOpportunity(
            artist_id=anomaly.artist_id,
            anomaly_id=anomaly.id,
            claim_id=claim.id if claim else None,
            status=AdvanceOpportunityStatus.QUEUED_ANALYST,
            model_score=ensemble,
            ensemble_scores=scores,
            predicted_recovery_amount=predicted,
            max_advance_amount=max_advance,
            proposed_advance_fee_percent=fee_percent,
            currency="USD",
            source_snapshot={
                "anomaly_id": anomaly.id,
                "anomaly_subtype": anomaly.subtype,
                "anomaly_category": str(anomaly.category),
                "claim_id": claim.id if claim else None,
            },
        )
        db.add(opp)
        created += 1

    db.commit()
    return {"created": created, "skipped": skipped, "signals_scanned": len(anomalies)}


def list_analyst_queue(db: Session) -> list[AdvanceOpportunity]:
    return (
        db.query(AdvanceOpportunity)
        .filter(AdvanceOpportunity.status == AdvanceOpportunityStatus.QUEUED_ANALYST)
        .order_by(AdvanceOpportunity.created_at.asc())
        .all()
    )


def list_executive_queue(db: Session) -> list[AdvanceOpportunity]:
    return (
        db.query(AdvanceOpportunity)
        .filter(AdvanceOpportunity.status == AdvanceOpportunityStatus.QUEUED_EXEC)
        .order_by(AdvanceOpportunity.created_at.asc())
        .all()
    )


def analyst_decision(
    db: Session,
    *,
    opportunity_id: str,
    approved: bool,
    actor_subject: str,
    actor_role: str,
    notes: str | None,
) -> AdvanceOpportunity:
    opp = db.query(AdvanceOpportunity).filter(AdvanceOpportunity.id == opportunity_id).first()
    if not opp:
        raise ValueError("Opportunity not found")
    if opp.status != AdvanceOpportunityStatus.QUEUED_ANALYST:
        raise ValueError("Opportunity is not in analyst queue")

    opp.status = (
        AdvanceOpportunityStatus.QUEUED_EXEC
        if approved
        else AdvanceOpportunityStatus.ANALYST_REJECTED
    )
    opp.analyst_notes = notes
    db.add(
        AdvanceApproval(
            opportunity_id=opp.id,
            stage=ApprovalStage.ANALYST,
            decision=ApprovalDecision.APPROVED if approved else ApprovalDecision.REJECTED,
            actor_subject=actor_subject,
            actor_role=actor_role,
            notes=notes,
        )
    )
    db.commit()
    db.refresh(opp)
    return opp


def executive_decision(
    db: Session,
    *,
    opportunity_id: str,
    approved: bool,
    actor_subject: str,
    actor_role: str,
    notes: str | None,
) -> AdvanceOpportunity:
    opp = db.query(AdvanceOpportunity).filter(AdvanceOpportunity.id == opportunity_id).first()
    if not opp:
        raise ValueError("Opportunity not found")
    if opp.status != AdvanceOpportunityStatus.QUEUED_EXEC:
        raise ValueError("Opportunity is not in executive queue")

    opp.status = (
        AdvanceOpportunityStatus.EXEC_APPROVED
        if approved
        else AdvanceOpportunityStatus.EXEC_REJECTED
    )
    opp.executive_notes = notes
    db.add(
        AdvanceApproval(
            opportunity_id=opp.id,
            stage=ApprovalStage.EXECUTIVE,
            decision=ApprovalDecision.APPROVED if approved else ApprovalDecision.REJECTED,
            actor_subject=actor_subject,
            actor_role=actor_role,
            notes=notes,
        )
    )
    db.commit()
    db.refresh(opp)
    return opp


def publish_artist_offer(db: Session, *, opportunity_id: str) -> AdvanceOffer:
    opp = db.query(AdvanceOpportunity).filter(AdvanceOpportunity.id == opportunity_id).first()
    if not opp:
        raise ValueError("Opportunity not found")
    if opp.status != AdvanceOpportunityStatus.EXEC_APPROVED:
        raise ValueError("Opportunity is not executive-approved")
    if _has_unrepaid_active_advance(db, opp.artist_id):
        raise ValueError("Artist already has an active unrepaid advance")

    proposed_fee = float(opp.proposed_advance_fee_percent)
    if 12.0 + proposed_fee > MAX_EFFECTIVE_FEE_CAP_PERCENT:
        raise ValueError("Offer breaches effective fee cap")

    expires_at = datetime.now(timezone.utc) + timedelta(days=ADVANCE_EXPIRY_DAYS)
    liquidity_advance = RecoverableLiquidityAdvance(
        artist_id=opp.artist_id,
        offered_amount=float(opp.max_advance_amount),
        currency=opp.currency,
        predicted_low_forecast=float(opp.predicted_recovery_amount),
        advance_fee_pct=proposed_fee,
        status=AdvanceStatus.OFFERED,
        notes="Created from analyst/exec approved opportunity.",
        expires_at=expires_at,
    )
    db.add(liquidity_advance)
    db.flush()

    offer = AdvanceOffer(
        opportunity_id=opp.id,
        artist_id=opp.artist_id,
        liquidity_advance_id=liquidity_advance.id,
        offered_amount=float(opp.max_advance_amount),
        currency=opp.currency,
        advance_fee_percent=proposed_fee,
        effective_total_fee_cap_percent=MAX_EFFECTIVE_FEE_CAP_PERCENT,
        visible_to_artist=True,
        status=AdvanceOfferStatus.PENDING_ARTIST,
        expires_at=expires_at,
    )
    opp.status = AdvanceOpportunityStatus.OFFER_GENERATED
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


def list_visible_artist_offers(db: Session, *, artist_id: str) -> list[AdvanceOffer]:
    return (
        db.query(AdvanceOffer)
        .filter(
            AdvanceOffer.artist_id == artist_id,
            AdvanceOffer.visible_to_artist.is_(True),
            AdvanceOffer.status == AdvanceOfferStatus.PENDING_ARTIST,
        )
        .order_by(AdvanceOffer.created_at.desc())
        .all()
    )


def artist_accept_offer(db: Session, *, artist_id: str, offer_id: str) -> AdvanceOffer:
    offer = (
        db.query(AdvanceOffer)
        .filter(
            AdvanceOffer.id == offer_id,
            AdvanceOffer.artist_id == artist_id,
            AdvanceOffer.visible_to_artist.is_(True),
        )
        .first()
    )
    if not offer:
        raise ValueError("Offer not found")
    if offer.status != AdvanceOfferStatus.PENDING_ARTIST:
        raise ValueError("Offer is not pending")

    liquidity = (
        db.query(RecoverableLiquidityAdvance)
        .filter(RecoverableLiquidityAdvance.id == offer.liquidity_advance_id)
        .first()
    )
    if not liquidity:
        raise ValueError("Underlying liquidity advance not found")

    liquidity.status = AdvanceStatus.ACCEPTED
    liquidity.accepted_at = datetime.now(timezone.utc)
    offer.status = AdvanceOfferStatus.ACCEPTED
    db.commit()
    db.refresh(offer)
    return offer


def generate_failed_advance_recovery_packet(
    db: Session,
    *,
    offer_id: str,
    failure_reason: str,
    actor_subject: str,
    actor_role: str,
) -> AdvanceRecoveryPacket:
    offer = db.query(AdvanceOffer).filter(AdvanceOffer.id == offer_id).first()
    if not offer:
        raise ValueError("Offer not found")

    custody = [
        {
            "event": "offer_failure_detected",
            "at": datetime.now(timezone.utc).isoformat(),
            "actor_subject": actor_subject,
            "actor_role": actor_role,
            "reason": failure_reason,
        },
        {
            "event": "evidence_snapshot_frozen",
            "at": datetime.now(timezone.utc).isoformat(),
            "actor_subject": "system",
            "actor_role": "orchestrator",
        },
    ]
    required_signers = [
        {"role": "analyst", "required": True},
        {"role": "executive", "required": True},
        {"role": "legal", "required": True},
    ]

    ledger_row = ImmutableLedgerService(db).append(
        offer.artist_id,
        "advance_failed_recovery_packet",
        {
            "offer_id": offer.id,
            "opportunity_id": offer.opportunity_id,
            "failure_reason": failure_reason,
            "chain_of_custody": custody,
            "required_signers": required_signers,
        },
    )

    packet = AdvanceRecoveryPacket(
        offer_id=offer.id,
        artist_id=offer.artist_id,
        chain_of_custody=custody,
        required_signers=required_signers,
        collected_signatures=[
            {
                "subject": actor_subject,
                "role": _normalize_signer_role(actor_role),
                "signed_at": datetime.now(timezone.utc).isoformat(),
            }
        ],
        legal_basis={
            "collection_mode": "failed_advance_recoupment",
            "fee_cap_percent": MAX_EFFECTIVE_FEE_CAP_PERCENT,
        },
        failure_reason=failure_reason,
        immutable_ledger_hash=ledger_row.entry_hash,
        status="READY",
    )
    offer.status = AdvanceOfferStatus.FAILED
    db.add(packet)
    db.commit()
    db.refresh(packet)
    return packet


def add_failed_packet_signature(
    db: Session,
    *,
    packet_id: str,
    actor_subject: str,
    actor_role: str,
    note: str | None,
) -> AdvanceRecoveryPacket:
    packet = db.query(AdvanceRecoveryPacket).filter(AdvanceRecoveryPacket.id == packet_id).first()
    if not packet:
        raise ValueError("Packet not found")
    if str(packet.status or "").upper() == "COMPLETE":
        raise ValueError("Packet already completed")

    normalized_role = _normalize_signer_role(actor_role)
    required_roles = {
        _normalize_signer_role(str(row.get("role") or ""))
        for row in list(packet.required_signers or [])
        if bool(row.get("required", True))
    }
    if normalized_role not in required_roles:
        raise ValueError("Actor role is not an allowed signer for this packet")

    signatures = list(packet.collected_signatures or [])
    if any(
        _normalize_signer_role(str(sig.get("role") or "")) == normalized_role for sig in signatures
    ):
        raise ValueError(f"{normalized_role} signature already recorded")

    signatures.append(
        {
            "subject": actor_subject,
            "role": normalized_role,
            "signed_at": datetime.now(timezone.utc).isoformat(),
            "note": note,
        }
    )
    packet.collected_signatures = signatures

    custody = list(packet.chain_of_custody or [])
    custody.append(
        {
            "event": "packet_signed",
            "at": datetime.now(timezone.utc).isoformat(),
            "actor_subject": actor_subject,
            "actor_role": normalized_role,
            "note": note,
        }
    )
    packet.chain_of_custody = custody
    db.commit()
    db.refresh(packet)
    return packet


def complete_failed_packet(
    db: Session,
    *,
    packet_id: str,
    actor_subject: str,
    actor_role: str,
) -> AdvanceRecoveryPacket:
    packet = db.query(AdvanceRecoveryPacket).filter(AdvanceRecoveryPacket.id == packet_id).first()
    if not packet:
        raise ValueError("Packet not found")

    required_roles = {
        _normalize_signer_role(str(row.get("role") or ""))
        for row in list(packet.required_signers or [])
        if bool(row.get("required", True))
    }
    signed_roles = {
        _normalize_signer_role(str(row.get("role") or ""))
        for row in list(packet.collected_signatures or [])
    }
    missing = sorted([r for r in required_roles if r not in signed_roles])
    if missing:
        raise ValueError(f"Missing required signatures: {', '.join(missing)}")

    packet.status = "COMPLETE"
    custody = list(packet.chain_of_custody or [])
    custody.append(
        {
            "event": "packet_completed",
            "at": datetime.now(timezone.utc).isoformat(),
            "actor_subject": actor_subject,
            "actor_role": _normalize_signer_role(actor_role),
            "signed_roles": sorted(signed_roles),
        }
    )
    packet.chain_of_custody = custody

    ledger_row = ImmutableLedgerService(db).append(
        packet.artist_id,
        "advance_failed_packet_completed",
        {
            "packet_id": packet.id,
            "offer_id": packet.offer_id,
            "signed_roles": sorted(signed_roles),
        },
    )
    packet.immutable_ledger_hash = ledger_row.entry_hash
    db.commit()
    db.refresh(packet)
    return packet
