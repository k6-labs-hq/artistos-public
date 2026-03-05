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
from XR7.models.work import Work
from XR7.recovery.audit_tracker import analyze_audit_eligibility, audit_summary
from XR7.recovery.priority_ranker import build_action_queue
from XR7.recovery.recoupment_tracker import compute_recoupment, recoupment_summary
from XR7.recovery.statute_tracker import classify_anomalies, sol_summary
from XR7.ml.rate_benchmarker import RateBenchmarker

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

    # Enrich anomalies with SOL status before ranking
    classified_anomalies = classify_anomalies(anomalies_raw)

    queue = build_action_queue(classified_anomalies, claims_raw)

    return {
        "artist_id": artist_id,
        "total_items": len(queue),
        "total_estimated_recoverable": round(
            sum(item.get("estimated_recoverable", 0.0) or 0.0 for item in queue), 2
        ),
        "queue": queue,
    }
