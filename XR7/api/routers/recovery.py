"""
Recovery-focused API endpoints for XR7 Engine 2.

Provides artist-centric money-recovery tools:
- Statute-of-limitations status for anomalies
- Rate benchmarking vs. industry standards
- Audit-rights eligibility ranking
- Recoupment position tracking
- Unified priority action queue
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.agents.onboarding_agents import (
    AutoEvidenceBuilderAgent,
    AutoPayerChaserAgent,
    AutoSettlementTrackerAgent,
    AutoSOLGuardianAgent,
    RightsRegistrationAgent,
)
from XR7.api.deps import get_artist_or_404
from XR7.api.routers.auth import require_artist_access
from XR7.blockchain.split_verifier import SplitVerifier
from XR7.ml.catalog_segmenter import CatalogSegmenter
from XR7.ml.rate_benchmarker import RateBenchmarker
from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.catalog_graph import CatalogGraphSnapshot
from XR7.models.claim import Claim
from XR7.models.contract import Contract
from XR7.models.event import Event
from XR7.models.ml_feedback import CalibrationSnapshot
from XR7.models.payment import Payment
from XR7.models.society_signal_log import SocietySignalLog
from XR7.models.statement import Statement
from XR7.models.work import Work
from XR7.network.coop_recovery import CoopRecoveryNetwork
from XR7.recovery.audit_tracker import analyze_audit_eligibility, audit_summary
from XR7.recovery.benchmarking import cross_artist_benchmarks
from XR7.recovery.black_box_expiration import (
    export_black_box_model_snapshot,
    train_black_box_expiration_probability_model_from_csv,
)
from XR7.recovery.cash_recovery_forecast import build_claim_forecast
from XR7.recovery.catalog_integrity import assess_catalog_integrity
from XR7.recovery.claims_evidence_package_builder import ClaimsEvidencePackageBuilder
from XR7.recovery.deadline_risk_engine import evaluate_deadline_risk
from XR7.recovery.discovery_rule_engine import DiscoveryRuleEngine
from XR7.recovery.edm_festival_auditor import EDMFestivalAuditor
from XR7.recovery.fraud_detection import run_fraud_scan
from XR7.recovery.leakage_benchmark_engine import LeakageBenchmarkEngine
from XR7.recovery.payer_behavior_model import payer_behavior_profile
from XR7.recovery.payer_playbooks import summarize_artist_playbooks
from XR7.recovery.priority_ranker import build_action_queue
from XR7.recovery.rate_benchmark_advanced import advanced_rate_benchmark
from XR7.recovery.recoupment_tracker import compute_recoupment, recoupment_summary
from XR7.recovery.recoverability_classifier import build_recoverability_payload
from XR7.recovery.recovery_attribution import attribute_recovery
from XR7.recovery.recovery_funnel import compute_recovery_funnel
from XR7.recovery.recovery_playbook import generate_recovery_playbook
from XR7.recovery.recovery_probability_model import anomaly_recovery_probability
from XR7.recovery.recovery_roi import recovery_roi_summary
from XR7.recovery.recovery_value_model import portfolio_expected_recovery_value
from XR7.recovery.sla_guarantee import sla_status_for_artist
from XR7.recovery.society_signal_feed import SocietySignalFeed
from XR7.recovery.split_verification import upsert_split_conflict_anomalies, verify_splits
from XR7.recovery.statute_tracker import classify_anomalies, sol_summary
from XR7.recovery.touring_auditor import TouringRecoupmentAuditor
from XR7.recovery.trust_defensibility import TrustDefensibilityService
from XR7.recovery.ugc_claim_generator import UGCClaimGenerator
from XR7.recovery.underpayment_heatmap import build_underpayment_heatmap
from XR7.recovery.underpayment_reconstruction import reconstruct_historical_underpayment
from XR7.services.branding import (
    branding_metadata,
    get_branding_for_artist,
    inject_branding_metadata,
)
from XR7.services.foreign_society_crosswalk_engine import ForeignSocietyCrosswalkEngine
from XR7.services.metadata_repair_engine import MetadataRepairEngine
from XR7.services.rate_drift_correction_engine import RateDriftCorrectionEngine
from XR7.ugc.global_scanner import GlobalUGCScanner
from XR7.ugc.hiphop_brand_auditor import HipHopBrandAuditor
from XR7.ugc.usage_monitor import UGCUsageMonitor

router = APIRouter(prefix="/artists", tags=["recovery"])


class RecoveryAutoRequest(BaseModel):
    include_rights_registration: bool = True


def _merge_agent_state(base: dict, update: dict) -> dict:
    merged = dict(base)
    append_keys = {"agent_activity", "evidence_hashes", "error_log"}
    for key, value in update.items():
        if key in append_keys:
            merged[key] = [*(merged.get(key) or []), *(value or [])]
        else:
            merged[key] = value
    return merged


def _anomaly_to_dict(a: Anomaly) -> dict:
    return {
        "id": a.id,
        "artist_id": a.artist_id,
        "category": str(a.category),
        "subtype": a.subtype,
        "severity": str(a.severity),
        "status": str(a.status),
        "estimated_recoverable": a.estimated_recoverable,
        "confidence_score": a.confidence_score,
        "territory": a.territory,
        "description": a.description,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }


def _payment_to_dict(p: Payment) -> dict:
    return {
        "id": p.id,
        "payment_type": str(p.payment_type),
        "amount": p.amount,
        "currency": p.currency,
        "source": p.source,
        "received_at": p.received_at.isoformat() if p.received_at else None,
        "period_start": p.period_start.isoformat() if p.period_start else None,
    }


def _contract_to_dict(c: Contract) -> dict:
    return {
        "id": c.id,
        "contract_type": str(c.contract_type),
        "counterparty": c.counterparty,
        "territory": c.territory,
        "effective_date": c.effective_date.isoformat() if c.effective_date else None,
        "expiry_date": c.expiry_date.isoformat() if c.expiry_date else None,
        "terms": c.terms or {},
    }


def _event_to_dict(e: Event) -> dict:
    return {
        "id": e.id,
        "event_type": str(e.event_type),
        "unit_value": e.unit_value,
        "quantity": e.quantity,
        "territory": e.territory,
        "currency": e.currency,
    }


def _claim_to_dict(c: Claim) -> dict:
    return {
        "id": c.id,
        "artist_id": c.artist_id,
        "claim_type": c.claim_type,
        "payer": _claim_payer(c),
        "status": str(c.status),
        "estimated_recoverable": c.recovered_amount,
        "confidence_score": 0.7,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def _statement_to_dict(s: Statement) -> dict:
    return {
        "id": s.id,
        "artist_id": s.artist_id,
        "file_hash": s.file_hash,
        "row_count": s.row_count,
        "events_created": s.events_created,
        "status": s.status,
        # Used only for local tamper/fraud heuristics in tests/dev.
        "raw_content": f"{s.filename}:{s.row_count}:{s.events_created}",
    }


def _claim_payer(c: Claim) -> str:
    evidence = c.evidence or {}
    if isinstance(evidence, dict):
        legal = evidence.get("legal_support", {})
        contracts = legal.get("contract_basis", []) if isinstance(legal, dict) else []
        if contracts and isinstance(contracts, list):
            counterparty = str((contracts[0] or {}).get("counterparty") or "").strip().lower()
            if counterparty:
                return counterparty
    return "generic"


@router.post("/{artist_id}/recovery/auto")
def run_recovery_autopilot(
    artist_id: str,
    payload: RecoveryAutoRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
):
    """Run autonomous recovery-management agents for this artist.

    Executes payer chasing, evidence packet generation, SOL monitoring,
    settlement tracking, and optionally rights registration planning.
    """
    get_artist_or_404(artist_id, db)

    state: dict = {
        "artist_id": artist_id,
        "confidence_scores": {},
        "agent_activity": [],
        "_db_session": db,
    }

    for node in [
        AutoPayerChaserAgent,
        AutoEvidenceBuilderAgent,
        AutoSOLGuardianAgent,
        AutoSettlementTrackerAgent,
    ]:
        state = _merge_agent_state(state, asyncio.run(node(state)))

    if payload.include_rights_registration:
        state = _merge_agent_state(state, asyncio.run(RightsRegistrationAgent(state)))

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "autopilot": {
                "executed_agents": [a.get("step") for a in state.get("agent_activity") or []],
                "confidence_scores": state.get("confidence_scores") or {},
                "payer_chase_actions": state.get("payer_chase_actions") or [],
                "sol_guardian_alerts": state.get("sol_guardian_alerts") or [],
                "settlement_tracker": state.get("settlement_tracker") or {},
                "rights_registration_plan": (
                    state.get("rights_registration_plan")
                    if payload.include_rights_registration
                    else None
                ),
                "evidence_packet": state.get("recovery_evidence_packet") or {},
            },
        },
    )


@router.get("/{artist_id}/recovery/sol-status")
def sol_status(artist_id: str, db: Session = Depends(get_db)):
    """
    Return statute-of-limitations classification for all open anomalies.

    Each anomaly is classified as EXPIRED, URGENT (<90 days), AT_RISK
    (90–180 days), or OK (>180 days remaining), sorted most-urgent first.
    Also returns an overall SOL exposure summary.
    """
    get_artist_or_404(artist_id, db)

    anomalies = [
        _anomaly_to_dict(a) for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    ]
    classified = classify_anomalies(anomalies)
    summary = sol_summary(anomalies)

    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "summary": summary,
        "anomalies": classified,
    }


@router.get("/{artist_id}/recovery/rate-benchmark")
def rate_benchmark(artist_id: str, db: Session = Depends(get_db)):
    """
    Compare the artist's actual payment rates against industry benchmarks.

    Returns a full report including per-event-type comparisons, estimated
    underpayment amounts, and a tier classification
    (ABOVE_MARKET, AT_MARKET, BELOW_MARKET, CRITICAL).
    """
    get_artist_or_404(artist_id, db)

    events = [_event_to_dict(e) for e in db.query(Event).filter(Event.artist_id == artist_id).all()]
    benchmarker = RateBenchmarker()
    report = benchmarker.benchmark(artist_id, events)
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **report.to_dict(),
    }


@router.get("/{artist_id}/recovery/audit-eligibility")
def audit_eligibility(artist_id: str, db: Session = Depends(get_db)):
    """
    Return audit-rights eligibility for all contracts.

    Contracts are ranked by estimated potential recovery and eligibility
    status (NEVER_AUDITED, ELIGIBLE, ELIGIBLE_SOON, NOT_YET_ELIGIBLE).
    """
    get_artist_or_404(artist_id, db)

    contracts = [
        _contract_to_dict(c)
        for c in db.query(Contract).filter(Contract.artist_id == artist_id).all()
    ]
    payments = [
        _payment_to_dict(p) for p in db.query(Payment).filter(Payment.artist_id == artist_id).all()
    ]
    recommendations = analyze_audit_eligibility(contracts, payments)
    summary = audit_summary(recommendations)

    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "summary": summary,
        "recommendations": [r.to_dict() for r in recommendations],
    }


@router.get("/{artist_id}/recovery/recoupment")
def recoupment(artist_id: str, db: Session = Depends(get_db)):
    """
    Return recoupment position and any discrepancy flags for all contracts
    with advance/recoupment provisions.

    Flags RECOUPMENT_DISCREPANCY when the calculated balance differs from
    the counterparty-reported balance, and EXCESS_RECOUPMENT when more than
    the advance has been recouped.
    """
    get_artist_or_404(artist_id, db)

    contracts = [
        _contract_to_dict(c)
        for c in db.query(Contract).filter(Contract.artist_id == artist_id).all()
    ]
    payments = [
        _payment_to_dict(p) for p in db.query(Payment).filter(Payment.artist_id == artist_id).all()
    ]
    positions = compute_recoupment(contracts, payments)
    summary = recoupment_summary(positions)

    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "summary": summary,
        "positions": [p.to_dict() for p in positions],
    }


@router.get("/{artist_id}/recovery/priority-queue")
def priority_queue(artist_id: str, db: Session = Depends(get_db)):
    """
    Return a unified, prioritised action queue for the artist.

    Merges open anomalies and in-flight claims into a single ranked list,
    scoring each item by (estimated_recoverable × confidence × urgency) / age.
    The artist (or their representative) should work through this list
    top-to-bottom to maximise recovery.
    """
    get_artist_or_404(artist_id, db)

    anomalies_raw = [
        _anomaly_to_dict(a)
        for a in db.query(Anomaly)
        .filter(Anomaly.artist_id == artist_id, Anomaly.status != "CLOSED")
        .all()
    ]
    claims_raw = [
        _claim_to_dict(c)
        for c in db.query(Claim)
        .filter(Claim.artist_id == artist_id, Claim.status.notin_(["PAID", "CLOSED"]))
        .all()
    ]
    claims_full = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    anomalies_by_id = {
        a.id: a for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    }
    snapshots = (
        db.query(CalibrationSnapshot).filter(CalibrationSnapshot.artist_id == artist_id).all()
    )

    works = db.query(Work).filter(Work.artist_id == artist_id).all()
    payments = db.query(Payment).filter(Payment.artist_id == artist_id).all()
    segment = CatalogSegmenter().segment(
        [{"id": w.id} for w in works],
        [{"amount": p.amount} for p in payments],
        anomalies_raw,
    )
    for row in anomalies_raw:
        row["threshold_adjustment"] = segment.get("threshold_adjustment", 1.0)
        row["effort_adjustment"] = segment.get("effort_adjustment", 1.0)
        row["segment"] = segment.get("segment")
    for row in claims_raw:
        row["threshold_adjustment"] = segment.get("threshold_adjustment", 1.0)
        row["effort_adjustment"] = segment.get("effort_adjustment", 1.0)
        row["segment"] = segment.get("segment")

    payer_behavior_cache: dict[str, dict] = {}
    claim_behavior_rows = [
        {
            "payer": _claim_payer(c),
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
        for c in claims_full
    ]
    for claim in claims_full:
        payer_key = _claim_payer(claim)
        if payer_key not in payer_behavior_cache:
            payer_behavior_cache[payer_key] = payer_behavior_profile(payer_key, claim_behavior_rows)

    payer_behavior_rows = list(payer_behavior_cache.values())

    forecast_index: dict[str, dict] = {}
    for claim in claims_full:
        forecast = build_claim_forecast(
            claim,
            anomalies_by_id.get(claim.anomaly_id),
            snapshots,
            claims_full,
        ).to_dict()
        forecast_index[claim.id] = forecast

    for row in claims_raw:
        forecast = forecast_index.get(row.get("id")) or {}
        payer_behavior = payer_behavior_cache.get(str(row.get("payer") or "generic"), {})
        row["confidence_score"] = float(
            forecast.get("confidence") or row.get("confidence_score") or 0.7
        )
        row["confidence_score"] = min(
            0.99,
            max(
                0.05,
                (row["confidence_score"] * 0.7)
                + (float(payer_behavior.get("acceptance_probability") or 0.5) * 0.3),
            ),
        )
        row["effort_adjustment"] = float(row.get("effort_adjustment") or 1.0) * max(
            0.8,
            min(1.4, float(forecast.get("time_to_cash_days") or 30) / 30.0),
        )

    for row in anomalies_raw:
        behavior = payer_behavior_rows[0] if payer_behavior_rows else None
        rp = anomaly_recovery_probability(row, behavior)
        row["confidence_score"] = float(
            rp.get("probability_of_recovery") or row.get("confidence_score") or 0.5
        )
        row["effort_adjustment"] = float(row.get("effort_adjustment") or 1.0) * max(
            0.8,
            min(1.6, float(rp.get("expected_effort_hours") or 4.0) / 6.0),
        )

    # Enrich anomalies with SOL status before ranking
    classified_anomalies = classify_anomalies(anomalies_raw)

    queue = build_action_queue(classified_anomalies, claims_raw)

    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "segment": segment,
        "claim_forecasts": forecast_index,
        "total_items": len(queue),
        "total_estimated_recoverable": round(
            sum(item.get("estimated_recoverable", 0.0) or 0.0 for item in queue), 2
        ),
        "queue": queue,
    }


@router.get("/{artist_id}/recovery/playbook-summary")
def playbook_summary(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)

    claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    anomaly_rows = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    anomalies_by_id = {a.id: a for a in anomaly_rows}
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **summarize_artist_playbooks(claims, anomalies_by_id),
    }


@router.get("/{artist_id}/recovery/deadline-risk")
def deadline_risk(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)

    anomalies = [
        {
            "id": a.id,
            "category": str(a.category),
            "subtype": a.subtype,
            "territory": a.territory,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "estimated_recoverable": float(a.estimated_recoverable or 0.0),
        }
        for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    ]
    claims = [
        {
            "id": c.id,
            "status": str(c.status),
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "payer": _claim_payer(c),
        }
        for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()
    ]
    contracts = [
        _contract_to_dict(c)
        for c in db.query(Contract).filter(Contract.artist_id == artist_id).all()
    ]
    payments = [
        _payment_to_dict(p) for p in db.query(Payment).filter(Payment.artist_id == artist_id).all()
    ]

    risk = evaluate_deadline_risk(anomalies, claims, contracts, payments)
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **risk,
    }


@router.get("/{artist_id}/splits/verification")
async def split_verification(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)

    works = db.query(Work).filter(Work.artist_id == artist_id).all()
    contracts = db.query(Contract).filter(Contract.artist_id == artist_id).all()
    events = db.query(Event).filter(Event.artist_id == artist_id).all()

    expected_split = 1.0
    for c in contracts:
        terms = c.terms or {}
        if "artist_split" in terms:
            expected_split = float(terms.get("artist_split") or expected_split)
            break

    rights_rows = []
    for w in works:
        rights_rows.append(
            {
                "work_id": w.id,
                "territory": "GLOBAL",
                "platform": "ALL",
                "expected_split": expected_split,
                "estimated_value": 1000.0,
            }
        )

    payout_rows = []
    for e in events:
        payout_rows.append(
            {
                "work_id": e.work_id,
                "territory": e.territory or "GLOBAL",
                "platform": e.platform or "ALL",
                "actual_split": 1.0,
            }
        )

    verification = verify_splits(artist_id, rights_rows, payout_rows)
    chain_payload = {
        "artist_splits": {"artist": expected_split, "counterparty": max(0.0, 1.0 - expected_split)},
        "contract_address": (
            db.query(CatalogGraphSnapshot.contract_address)
            .filter(CatalogGraphSnapshot.artist_id == artist_id)
            .order_by(CatalogGraphSnapshot.created_at.desc())
            .scalar()
        ),
    }
    verifier = SplitVerifier(db)
    verification["on_chain_verified"] = await verifier.verify_on_chain(chain_payload)

    if not chain_payload.get("contract_address"):
        try:
            deployed_address = await verifier.deploy_testnet_contract(artist_id)
            verification["contract_address"] = deployed_address
        except Exception as exc:  # noqa: BLE001
            verification["contract_deploy_error"] = str(exc)
    existing = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    new_anomalies = upsert_split_conflict_anomalies(artist_id, verification, existing)
    for anomaly in new_anomalies:
        db.add(anomaly)
    if new_anomalies:
        db.commit()

    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **verification,
        "split_conflict_anomalies_created": len(new_anomalies),
    }


@router.get("/{artist_id}/splits/conflicts")
def split_conflicts(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)

    rows = (
        db.query(Anomaly)
        .filter(Anomaly.artist_id == artist_id, Anomaly.subtype == "split_conflict")
        .order_by(Anomaly.created_at.desc())
        .all()
    )
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "count": len(rows),
        "conflicts": [
            {
                "id": r.id,
                "severity": str(r.severity),
                "estimated_recoverable": float(r.estimated_recoverable or 0.0),
                "description": r.description,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }


@router.get("/{artist_id}/recovery/expected-value")
def recovery_expected_value(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)

    anomalies = [
        _anomaly_to_dict(a) for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    ]
    claims = [_claim_to_dict(c) for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()]
    contracts = [
        _contract_to_dict(c)
        for c in db.query(Contract).filter(Contract.artist_id == artist_id).all()
    ]

    total_claims = max(len(claims), 1)
    paid_claims = sum(1 for c in claims if str(c.get("status")) in {"PAID", "CLOSED"})
    historical_recovery_rate = float(paid_claims) / float(total_claims)

    payer_rows = [
        payer_behavior_profile(str(c.get("payer") or "generic"), claims) for c in claims[:10]
    ]
    catalog_health_score = max(40.0, 100.0 - (len(anomalies) * 2.0))

    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **portfolio_expected_recovery_value(
            anomalies=anomalies,
            claims=claims,
            catalog_health=catalog_health_score,
            payer_behavior_rows=payer_rows,
            contracts=contracts,
            historical_recovery_rate=historical_recovery_rate,
        ),
    }


@router.get("/{artist_id}/recovery/funnel")
def recovery_funnel(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    anomalies = [
        _anomaly_to_dict(a) for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    ]
    claims = [
        {
            **_claim_to_dict(c),
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }
        for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()
    ]
    deposits = [
        _payment_to_dict(p)
        for p in db.query(Payment)
        .filter(Payment.artist_id == artist_id, Payment.payment_type == "PAYOUT")
        .all()
    ]
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **compute_recovery_funnel(anomalies, claims, deposits),
    }


@router.get("/{artist_id}/catalog/integrity")
def catalog_integrity(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    works = [
        {
            "id": w.id,
            "title": w.title,
            "isrc": w.isrc,
            "iswc": w.iswc,
        }
        for w in db.query(Work).filter(Work.artist_id == artist_id).all()
    ]
    contracts = [
        _contract_to_dict(c)
        for c in db.query(Contract).filter(Contract.artist_id == artist_id).all()
    ]
    events = [
        {
            "work_id": e.work_id,
            "platform": e.platform,
            "quantity": e.quantity,
            "unit_value": e.unit_value,
        }
        for e in db.query(Event).filter(Event.artist_id == artist_id).all()
    ]
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **assess_catalog_integrity(works, contracts, events),
    }


@router.get("/{artist_id}/recovery/rate-benchmark-advanced")
def rate_benchmark_advanced(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    events = [
        {
            "platform": e.platform,
            "territory": e.territory,
            "unit_value": e.unit_value,
            "quantity": e.quantity,
        }
        for e in db.query(Event).filter(Event.artist_id == artist_id).all()
    ]
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **advanced_rate_benchmark(events),
    }


@router.post("/{artist_id}/fraud-scan")
def fraud_scan(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    claims = [
        {
            "id": c.id,
            "anomaly_id": c.anomaly_id,
            "claim_type": c.claim_type,
        }
        for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()
    ]
    statements = [
        _statement_to_dict(s)
        for s in db.query(Statement).filter(Statement.artist_id == artist_id).all()
    ]
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **run_fraud_scan(claims, statements),
    }


@router.get("/{artist_id}/sla/status")
def sla_status(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    claims = [_claim_to_dict(c) for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()]
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **sla_status_for_artist(claims),
    }


@router.get("/{artist_id}/recovery/heatmap")
def underpayment_heatmap(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    anomalies = [
        _anomaly_to_dict(a) for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    ]
    claims = [_claim_to_dict(c) for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()]
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **build_underpayment_heatmap(anomalies, claims),
    }


@router.get("/{artist_id}/recovery/roi")
def recovery_roi(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    anomalies = [
        _anomaly_to_dict(a) for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    ]
    claims = [_claim_to_dict(c) for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()]
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **recovery_roi_summary(claims, anomalies),
    }


@router.post("/{artist_id}/recovery/reconstruct-historical")
def reconstruct_historical(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)

    events = [
        {
            "expected_amount": float(e.unit_value or 0.0) * float(e.quantity or 0.0),
            "unit_value": e.unit_value,
            "quantity": e.quantity,
        }
        for e in db.query(Event).filter(Event.artist_id == artist_id).all()
    ]
    payments = [
        {"amount": p.amount} for p in db.query(Payment).filter(Payment.artist_id == artist_id).all()
    ]
    end = datetime.now(timezone.utc)
    start = datetime(2000, 1, 1, tzinfo=timezone.utc)
    metadata_result = MetadataRepairEngine(db).run_historical_audit_and_repair(
        artist_id, start, end
    )
    metadata_health = MetadataRepairEngine(db).get_metadata_health(artist_id)
    rate_drift = RateDriftCorrectionEngine(db).detect_and_record(artist_id)
    foreign_crosswalk = ForeignSocietyCrosswalkEngine(db).analyze(artist_id)

    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **reconstruct_historical_underpayment(events, payments),
        "metadata_audit": {
            "issues_found": metadata_result.issues_found,
            "issues_auto_repaired": metadata_result.auto_repaired,
            "issues_requiring_review": metadata_result.requires_review,
            "projected_leakage_avoided": metadata_result.projected_leakage_avoided,
            "catalog_graph_version": metadata_result.graph_version,
            "metadata_health": metadata_health,
        },
        "rate_drift_correction": {
            "issues_found": rate_drift.issues_found,
            "contract_discrepancies": rate_drift.contract_discrepancies,
            "discrepancy_reports": rate_drift.discrepancy_reports,
            "projected_future_leakage": rate_drift.projected_future_leakage,
            "future_risk_anomaly_subtype": "RATE_DRIFT_FUTURE_RISK",
        },
        "foreign_society_crosswalk": {
            "findings": foreign_crosswalk.findings,
            "auto_registration_packets": foreign_crosswalk.registration_packets,
        },
    }


@router.get("/{artist_id}/recovery/attribution")
def recovery_attribution(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    anomalies = [
        _anomaly_to_dict(a) for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    ]
    claims = [
        {
            **_claim_to_dict(c),
            "anomaly_id": c.anomaly_id,
            "recovered_amount": c.recovered_amount,
        }
        for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()
    ]
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **attribute_recovery(anomalies, claims),
    }


@router.get("/{artist_id}/benchmarking")
def artist_benchmarking(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)

    artists = db.query(Artist).all()
    peer_population = []
    for peer in artists:
        peer_anomalies = db.query(Anomaly).filter(Anomaly.artist_id == peer.id).all()
        peer_claims = db.query(Claim).filter(Claim.artist_id == peer.id).all()
        peer_population.append(
            {
                "leakage": sum(float(a.estimated_recoverable or 0.0) for a in peer_anomalies),
                "recovery": sum(float(c.recovered_amount or 0.0) for c in peer_claims),
                "anomaly_density": float(len(peer_anomalies))
                / max(1.0, float(len(peer_claims) or 1.0)),
                "catalog_health": max(20.0, 100.0 - (len(peer_anomalies) * 2.0)),
            }
        )

    current_anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    current_claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    artist_summary = {
        "leakage": sum(float(a.estimated_recoverable or 0.0) for a in current_anomalies),
        "recovery": sum(float(c.recovered_amount or 0.0) for c in current_claims),
        "anomaly_density": float(len(current_anomalies))
        / max(1.0, float(len(current_claims) or 1.0)),
        "catalog_health": max(20.0, 100.0 - (len(current_anomalies) * 2.0)),
    }
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **cross_artist_benchmarks(artist_summary, peer_population),
    }


@router.get("/{artist_id}/recovery/playbook")
def recovery_playbook(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)

    queue = priority_queue(artist_id, db)
    deadline = deadline_risk(artist_id, db)
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **generate_recovery_playbook(
            priority_items=queue.get("queue") or [],
            deadline_risk=deadline,
            evidence_requirements=[
                "signed_evidence_packet",
                "source_citations_csv",
                "contract_basis_docs",
            ],
            negotiation_strategy="anchor_high_then_settle_midpoint_with_deadline_pressure",
        ),
    }


@router.get("/{artist_id}/ugc/monitor")
async def ugc_monitor(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    monitor = UGCUsageMonitor()
    uses = await monitor.scan_for_uses(artist_id, days_back=30)
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "viral_usage": uses,
        "ugc_opportunities": [
            {**u, "estimated_recoverable": monitor.calculate_lost_sync_value(u)} for u in uses
        ],
    }


@router.post("/{artist_id}/ugc/claim")
async def ugc_claim(
    artist_id: str, use_data: dict, platform: str = "tiktok", db: Session = Depends(get_db)
):
    get_artist_or_404(artist_id, db)
    generator = UGCClaimGenerator(db)
    claim_id = await generator.create_claim(artist_id, platform, use_data)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "claim_id": claim_id,
            "evidence_export": f"/claims/{claim_id}/evidence/export?format=zip",
        },
    )


@router.post("/{artist_id}/ugc/global-scan")
async def ugc_global_scan(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    scanner = GlobalUGCScanner()
    uses = await scanner.scan_global_uses(artist_id)
    packets = [scanner.auto_generate_evidence_packet(u) for u in uses]
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "detected_uses": uses,
        "global_ugc_potential": round(
            sum(float(p.get("estimated_recoverable") or 0.0) for p in packets), 2
        ),
        "evidence_packets": packets,
    }


@router.post("/{artist_id}/recovery/ugc-auto-claim")
async def ugc_auto_claim(artist_id: str, platform: str, use_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    use_data = {
        "use_id": use_id,
        "platform": platform,
        "views": 1000000,
        "url": f"https://example.com/{platform}/{use_id}",
    }
    claim_id = await UGCClaimGenerator(db).create_claim(artist_id, platform, use_data)
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "claim_id": claim_id,
            "quick_approve_url": f"/claims/{claim_id}/advance",
        },
    )


@router.post("/{artist_id}/recovery/touring-audit")
async def touring_audit(
    artist_id: str, settlement_csv: str = "", merch_csv: str = "", db: Session = Depends(get_db)
):
    get_artist_or_404(artist_id, db)
    auditor = TouringRecoupmentAuditor(db)
    discrepancies = auditor.detect_settlement_discrepancies(settlement_csv, merch_csv)
    overages = auditor.analyze_recoupment_overages(artist_id)
    letter = await auditor.generate_audit_demand_letter(
        artist_id, {"discrepancies": discrepancies, "overages": overages}
    )
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "discrepancies": discrepancies,
            "recoupment": overages,
            "audit_letter": letter,
        },
    )


@router.get("/{artist_id}/recovery/recoupment-deep-audit")
def recoupment_deep_audit(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    payload = TouringRecoupmentAuditor(db).analyze_recoupment_overages(artist_id)
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        **payload,
    }


@router.post("/{artist_id}/recovery/hiphop-brand-audit")
async def hiphop_brand_audit(artist_id: str, db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    auditor = HipHopBrandAuditor(db)
    rows = await auditor.scan_brand_deals_and_ugc(artist_id)
    claim_ids = [await auditor.auto_create_claim(artist_id, item) for item in rows]
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "anomalies": rows,
            "claim_ids": claim_ids,
            "brand_ugc_potential": sum(float(r.get("estimated_value") or 0.0) for r in rows),
        },
    )


@router.post("/{artist_id}/recovery/edm-festival-audit")
async def edm_festival_audit(
    artist_id: str,
    settlements: list[dict] | None = None,
    merch: list[dict] | None = None,
    packages: list[dict] | None = None,
    db: Session = Depends(get_db),
):
    auditor = EDMFestivalAuditor()
    discrepancies = auditor.detect_settlement_and_merch_discrepancies(
        settlements or [], merch or []
    )
    recoup = auditor.analyze_recoupment_for_tour_packages(packages or [])
    letter = await auditor.generate_audit_letter(
        artist_id, {"discrepancies": discrepancies, "recoupment": recoup}
    )
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "discrepancies": discrepancies,
            "recoupment": recoup,
            "audit_letter": letter,
        },
    )


@router.post("/{artist_id}/network/pooled-claim")
def pooled_claim(artist_id: str, anomaly_ids: list[str], db: Session = Depends(get_db)):
    payload = CoopRecoveryNetwork().pooled_claim_submission(artist_id, anomaly_ids)
    if isinstance(payload, dict):
        return inject_branding_metadata(db, {"artist_id": artist_id, **payload})
    return {
        "artist_id": artist_id,
        "branding": branding_metadata(get_branding_for_artist(db, artist_id)),
        "result": payload,
    }


@router.post("/{artist_id}/recovery/discovery-rule")
def run_discovery_rule(artist_id: str, anomaly: dict[str, Any], db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)
    result = DiscoveryRuleEngine(db=db).evaluate({**anomaly, "artist_id": artist_id})
    return inject_branding_metadata(db, {"artist_id": artist_id, **result})


@router.post("/{artist_id}/recovery/black-box/train")
def train_black_box_model(artist_id: str, payload: dict[str, Any], db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)

    csv_path = str(payload.get("csv_path") or "")
    if csv_path:
        training = train_black_box_expiration_probability_model_from_csv(csv_path)
    else:
        training = {
            "ingested_events": 0,
            "model_version": "xr7-blackbox-prob-v1",
            "trained_at": datetime.now(timezone.utc).isoformat(),
        }
    return inject_branding_metadata(
        db, {"artist_id": artist_id, **training, "snapshot": export_black_box_model_snapshot()}
    )


@router.post("/{artist_id}/recovery/leakage-benchmark")
def leakage_benchmark(artist_id: str, payload: dict[str, Any], db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)

    engine = LeakageBenchmarkEngine(epsilon=float(payload.get("epsilon") or 1.0))
    client_profile = payload.get("client_profile") or {}
    peers = payload.get("peer_profiles") or []
    result = engine.compare_against_cohort(client_profile, peers)
    return inject_branding_metadata(db, {"artist_id": artist_id, **result})


@router.post("/{artist_id}/recovery/society-signal")
def ingest_society_signal(artist_id: str, payload: dict[str, Any], db: Session = Depends(get_db)):
    get_artist_or_404(artist_id, db)

    anomalies = [
        _anomaly_to_dict(a) for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    ]
    feed = SocietySignalFeed()
    result = feed.apply_signal(payload, anomalies)

    row = SocietySignalLog(
        source=str((result.get("signal") or {}).get("source") or "partner_feed"),
        signal_type=str((result.get("signal") or {}).get("signal_type") or "unknown"),
        payer_or_society=str((result.get("signal") or {}).get("payer_or_society") or "GENERIC"),
        affected_anomaly_count=int(result.get("affected_anomaly_count") or 0),
        classification_impact_json=json.dumps(result.get("classification_impact") or {}),
    )
    db.add(row)
    db.commit()
    return inject_branding_metadata(
        db, {"artist_id": artist_id, **result, "society_activity_feed": feed.dashboard_feed()}
    )


@router.post("/{artist_id}/claims/{claim_id}/evidence-package")
def build_claim_evidence_package(
    artist_id: str,
    claim_id: str,
    payload: dict[str, Any] | None = None,
    db: Session = Depends(get_db),
):
    get_artist_or_404(artist_id, db)
    claim = db.query(Claim).filter(Claim.id == claim_id, Claim.artist_id == artist_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    anomaly = db.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    anomaly_payload = _anomaly_to_dict(anomaly)
    anomaly_payload["description"] = anomaly.description
    anomaly_payload["event_date"] = (
        anomaly.time_window_end.isoformat() if anomaly.time_window_end else None
    )
    anomaly_payload["created_at"] = anomaly.created_at.isoformat() if anomaly.created_at else None

    recoverability = build_recoverability_payload(anomaly_payload)
    discovery = DiscoveryRuleEngine().evaluate(anomaly_payload)
    trust = TrustDefensibilityService(db).trust_score(
        data_completeness=0.85 if anomaly.description else 0.6,
        model_confidence=float(anomaly.confidence_score or 0.0),
        contract_evidence_quality=0.7 if recoverability.get("contract_recoverability") else 0.45,
        sol_risk=1.0 if bool(discovery.get("urgent_flag")) else 0.25,
    )

    builder = ClaimsEvidencePackageBuilder(
        confidence_gate_threshold=float((payload or {}).get("confidence_gate_threshold") or 0.65)
    )
    package = builder.build(
        claim={
            "id": claim.id,
            "artist_id": claim.artist_id,
            "governing_law_state": claim.governing_law_state,
        },
        anomaly=anomaly_payload,
        recoverability_payload=recoverability,
        trust_score=float(trust.get("trust_score") or 0.0),
        precedent_refs=(payload or {}).get("precedent_refs") or [],
    )

    claim.trust_score = float(trust.get("trust_score") or 0.0)
    claim.attorney_review_required = bool(trust.get("requires_attorney_review"))
    claim.claim_strength_rating = str(package.get("claim_strength_rating") or "") or None
    claim.legal_defensibility_report = TrustDefensibilityService(db).legal_defensibility_report(
        claim_id=claim.id,
        anomaly_payload=anomaly_payload,
        classification_payload=recoverability,
        evidence_package=package,
    )
    db.commit()

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "claim_id": claim_id,
            "claim_strength_rating": package.get("claim_strength_rating"),
            "human_attorney_review_required": package.get("human_attorney_review_required"),
            "json": package,
            "pdf_text": builder.export_pdf_text(package),
            "xlsx_csv": builder.export_xlsx_bytes(package).decode("utf-8"),
        },
    )


@router.get("/{artist_id}/claims/{claim_id}/legal-defensibility-report")
def get_legal_defensibility_report(artist_id: str, claim_id: str, db: Session = Depends(get_db)):
    claim = db.query(Claim).filter(Claim.id == claim_id, Claim.artist_id == artist_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "claim_id": claim_id,
            "trust_score": claim.trust_score,
            "attorney_review_required": claim.attorney_review_required,
            "claim_strength_rating": claim.claim_strength_rating,
            "legal_defensibility_report": claim.legal_defensibility_report or {},
        },
    )
