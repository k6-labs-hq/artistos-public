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

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.claim import Claim
from XR7.models.contract import Contract
from XR7.models.event import Event
from XR7.models.payment import Payment
from XR7.models.statement import Statement
from XR7.models.work import Work
from XR7.recovery.audit_tracker import analyze_audit_eligibility, audit_summary
from XR7.recovery.cash_recovery_forecast import build_claim_forecast
from XR7.recovery.deadline_risk_engine import evaluate_deadline_risk
from XR7.recovery.payer_playbooks import summarize_artist_playbooks
from XR7.recovery.priority_ranker import build_action_queue
from XR7.recovery.recoupment_tracker import compute_recoupment, recoupment_summary
from XR7.recovery.split_verification import upsert_split_conflict_anomalies, verify_splits
from XR7.recovery.statute_tracker import classify_anomalies, sol_summary
from XR7.ml.rate_benchmarker import RateBenchmarker
from XR7.ml.catalog_segmenter import CatalogSegmenter
from XR7.models.ml_feedback import CalibrationSnapshot

router = APIRouter(prefix="/artists", tags=["recovery"])


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
        "status": str(c.status),
        "estimated_recoverable": c.recovered_amount,
        "confidence_score": 0.7,
        "created_at": c.created_at.isoformat() if c.created_at else None,
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


@router.get("/{artist_id}/recovery/sol-status")
def sol_status(artist_id: str, db: Session = Depends(get_db)):
    """
    Return statute-of-limitations classification for all open anomalies.

    Each anomaly is classified as EXPIRED, URGENT (<90 days), AT_RISK
    (90–180 days), or OK (>180 days remaining), sorted most-urgent first.
    Also returns an overall SOL exposure summary.
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    anomalies = [
        _anomaly_to_dict(a)
        for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    ]
    classified = classify_anomalies(anomalies)
    summary = sol_summary(anomalies)

    return {
        "artist_id": artist_id,
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
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    events = [
        _event_to_dict(e)
        for e in db.query(Event).filter(Event.artist_id == artist_id).all()
    ]
    benchmarker = RateBenchmarker()
    report = benchmarker.benchmark(artist_id, events)
    return report.to_dict()


@router.get("/{artist_id}/recovery/audit-eligibility")
def audit_eligibility(artist_id: str, db: Session = Depends(get_db)):
    """
    Return audit-rights eligibility for all contracts.

    Contracts are ranked by estimated potential recovery and eligibility
    status (NEVER_AUDITED, ELIGIBLE, ELIGIBLE_SOON, NOT_YET_ELIGIBLE).
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    contracts = [
        _contract_to_dict(c)
        for c in db.query(Contract).filter(Contract.artist_id == artist_id).all()
    ]
    payments = [
        _payment_to_dict(p)
        for p in db.query(Payment).filter(Payment.artist_id == artist_id).all()
    ]
    recommendations = analyze_audit_eligibility(contracts, payments)
    summary = audit_summary(recommendations)

    return {
        "artist_id": artist_id,
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
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    contracts = [
        _contract_to_dict(c)
        for c in db.query(Contract).filter(Contract.artist_id == artist_id).all()
    ]
    payments = [
        _payment_to_dict(p)
        for p in db.query(Payment).filter(Payment.artist_id == artist_id).all()
    ]
    positions = compute_recoupment(contracts, payments)
    summary = recoupment_summary(positions)

    return {
        "artist_id": artist_id,
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
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

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
    anomalies_by_id = {a.id: a for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()}
    snapshots = db.query(CalibrationSnapshot).filter(CalibrationSnapshot.artist_id == artist_id).all()

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
        row["confidence_score"] = float(forecast.get("confidence") or row.get("confidence_score") or 0.7)
        row["effort_adjustment"] = float(row.get("effort_adjustment") or 1.0) * max(
            0.8,
            min(1.4, float(forecast.get("time_to_cash_days") or 30) / 30.0),
        )

    # Enrich anomalies with SOL status before ranking
    classified_anomalies = classify_anomalies(anomalies_raw)

    queue = build_action_queue(classified_anomalies, claims_raw)

    return {
        "artist_id": artist_id,
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
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    anomaly_rows = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    anomalies_by_id = {a.id: a for a in anomaly_rows}
    return {
        "artist_id": artist_id,
        **summarize_artist_playbooks(claims, anomalies_by_id),
    }


@router.get("/{artist_id}/recovery/deadline-risk")
def deadline_risk(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

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
    contracts = [_contract_to_dict(c) for c in db.query(Contract).filter(Contract.artist_id == artist_id).all()]
    payments = [_payment_to_dict(p) for p in db.query(Payment).filter(Payment.artist_id == artist_id).all()]

    risk = evaluate_deadline_risk(anomalies, claims, contracts, payments)
    return {
        "artist_id": artist_id,
        **risk,
    }


@router.get("/{artist_id}/splits/verification")
def split_verification(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

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
    existing = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    new_anomalies = upsert_split_conflict_anomalies(artist_id, verification, existing)
    for anomaly in new_anomalies:
        db.add(anomaly)
    if new_anomalies:
        db.commit()

    return {
        "artist_id": artist_id,
        **verification,
        "split_conflict_anomalies_created": len(new_anomalies),
    }


@router.get("/{artist_id}/splits/conflicts")
def split_conflicts(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    rows = (
        db.query(Anomaly)
        .filter(Anomaly.artist_id == artist_id, Anomaly.subtype == "split_conflict")
        .order_by(Anomaly.created_at.desc())
        .all()
    )
    return {
        "artist_id": artist_id,
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
