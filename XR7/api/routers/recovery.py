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
from XR7.recovery.benchmarking import cross_artist_benchmarks
from XR7.recovery.cash_recovery_forecast import build_claim_forecast
from XR7.recovery.catalog_integrity import assess_catalog_integrity
from XR7.recovery.deadline_risk_engine import evaluate_deadline_risk
from XR7.recovery.fraud_detection import run_fraud_scan
from XR7.recovery.payer_behavior_model import payer_behavior_profile
from XR7.recovery.payer_playbooks import summarize_artist_playbooks
from XR7.recovery.rate_benchmark_advanced import advanced_rate_benchmark
from XR7.recovery.recovery_attribution import attribute_recovery
from XR7.recovery.recovery_funnel import compute_recovery_funnel
from XR7.recovery.recovery_playbook import generate_recovery_playbook
from XR7.recovery.recovery_probability_model import anomaly_recovery_probability
from XR7.recovery.recovery_roi import recovery_roi_summary
from XR7.recovery.recovery_value_model import portfolio_expected_recovery_value
from XR7.recovery.sla_guarantee import sla_status_for_artist
from XR7.recovery.priority_ranker import build_action_queue
from XR7.recovery.recoupment_tracker import compute_recoupment, recoupment_summary
from XR7.recovery.split_verification import upsert_split_conflict_anomalies, verify_splits
from XR7.recovery.statute_tracker import classify_anomalies, sol_summary
from XR7.recovery.underpayment_heatmap import build_underpayment_heatmap
from XR7.recovery.underpayment_reconstruction import reconstruct_historical_underpayment
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

    payer_behavior_cache: dict[str, dict] = {}
    claim_behavior_rows = [
        {
            "payer": _claim_payer(c),
            "status": str(c.status),
            "settlement_days": 45,
            "settlement_percent": min(1.0, max(0.1, float(c.recovered_amount or 0.0) / max(float(c.recovered_amount or 1.0), 1.0))),
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
        row["confidence_score"] = float(forecast.get("confidence") or row.get("confidence_score") or 0.7)
        row["confidence_score"] = min(
            0.99,
            max(0.05, (row["confidence_score"] * 0.7) + (float(payer_behavior.get("acceptance_probability") or 0.5) * 0.3)),
        )
        row["effort_adjustment"] = float(row.get("effort_adjustment") or 1.0) * max(
            0.8,
            min(1.4, float(forecast.get("time_to_cash_days") or 30) / 30.0),
        )

    for row in anomalies_raw:
        behavior = payer_behavior_rows[0] if payer_behavior_rows else None
        rp = anomaly_recovery_probability(row, behavior)
        row["confidence_score"] = float(rp.get("probability_of_recovery") or row.get("confidence_score") or 0.5)
        row["effort_adjustment"] = float(row.get("effort_adjustment") or 1.0) * max(
            0.8,
            min(1.6, float(rp.get("expected_effort_hours") or 4.0) / 6.0),
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


@router.get("/{artist_id}/recovery/expected-value")
def recovery_expected_value(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    anomalies = [_anomaly_to_dict(a) for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()]
    claims = [_claim_to_dict(c) for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()]
    contracts = [_contract_to_dict(c) for c in db.query(Contract).filter(Contract.artist_id == artist_id).all()]

    total_claims = max(len(claims), 1)
    paid_claims = sum(1 for c in claims if str(c.get("status")) in {"PAID", "CLOSED"})
    historical_recovery_rate = float(paid_claims) / float(total_claims)

    payer_rows = [payer_behavior_profile(str(c.get("payer") or "generic"), claims) for c in claims[:10]]
    catalog_health_score = max(40.0, 100.0 - (len(anomalies) * 2.0))

    return {
        "artist_id": artist_id,
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
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    anomalies = [_anomaly_to_dict(a) for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()]
    claims = [
        {
            **_claim_to_dict(c),
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }
        for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()
    ]
    deposits = [
        _payment_to_dict(p)
        for p in db.query(Payment).filter(Payment.artist_id == artist_id, Payment.payment_type == "PAYOUT").all()
    ]
    return {
        "artist_id": artist_id,
        **compute_recovery_funnel(anomalies, claims, deposits),
    }


@router.get("/{artist_id}/catalog/integrity")
def catalog_integrity(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    works = [
        {
            "id": w.id,
            "title": w.title,
            "isrc": w.isrc,
            "iswc": w.iswc,
        }
        for w in db.query(Work).filter(Work.artist_id == artist_id).all()
    ]
    contracts = [_contract_to_dict(c) for c in db.query(Contract).filter(Contract.artist_id == artist_id).all()]
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
        **assess_catalog_integrity(works, contracts, events),
    }


@router.get("/{artist_id}/recovery/rate-benchmark-advanced")
def rate_benchmark_advanced(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
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
        **advanced_rate_benchmark(events),
    }


@router.post("/{artist_id}/fraud-scan")
def fraud_scan(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    claims = [
        {
            "id": c.id,
            "anomaly_id": c.anomaly_id,
            "claim_type": c.claim_type,
        }
        for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()
    ]
    statements = [_statement_to_dict(s) for s in db.query(Statement).filter(Statement.artist_id == artist_id).all()]
    return {
        "artist_id": artist_id,
        **run_fraud_scan(claims, statements),
    }


@router.get("/{artist_id}/sla/status")
def sla_status(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    claims = [_claim_to_dict(c) for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()]
    return {
        "artist_id": artist_id,
        **sla_status_for_artist(claims),
    }


@router.get("/{artist_id}/recovery/heatmap")
def underpayment_heatmap(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    anomalies = [_anomaly_to_dict(a) for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()]
    claims = [_claim_to_dict(c) for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()]
    return {
        "artist_id": artist_id,
        **build_underpayment_heatmap(anomalies, claims),
    }


@router.get("/{artist_id}/recovery/roi")
def recovery_roi(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    anomalies = [_anomaly_to_dict(a) for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()]
    claims = [_claim_to_dict(c) for c in db.query(Claim).filter(Claim.artist_id == artist_id).all()]
    return {
        "artist_id": artist_id,
        **recovery_roi_summary(claims, anomalies),
    }


@router.post("/{artist_id}/recovery/reconstruct-historical")
def reconstruct_historical(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    events = [
        {
            "expected_amount": float(e.unit_value or 0.0) * float(e.quantity or 0.0),
            "unit_value": e.unit_value,
            "quantity": e.quantity,
        }
        for e in db.query(Event).filter(Event.artist_id == artist_id).all()
    ]
    payments = [
        {"amount": p.amount}
        for p in db.query(Payment).filter(Payment.artist_id == artist_id).all()
    ]
    return {
        "artist_id": artist_id,
        **reconstruct_historical_underpayment(events, payments),
    }


@router.get("/{artist_id}/recovery/attribution")
def recovery_attribution(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    anomalies = [_anomaly_to_dict(a) for a in db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()]
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
        **attribute_recovery(anomalies, claims),
    }


@router.get("/{artist_id}/benchmarking")
def artist_benchmarking(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    artists = db.query(Artist).all()
    peer_population = []
    for peer in artists:
        peer_anomalies = db.query(Anomaly).filter(Anomaly.artist_id == peer.id).all()
        peer_claims = db.query(Claim).filter(Claim.artist_id == peer.id).all()
        peer_population.append(
            {
                "leakage": sum(float(a.estimated_recoverable or 0.0) for a in peer_anomalies),
                "recovery": sum(float(c.recovered_amount or 0.0) for c in peer_claims),
                "anomaly_density": float(len(peer_anomalies)) / max(1.0, float(len(peer_claims) or 1.0)),
                "catalog_health": max(20.0, 100.0 - (len(peer_anomalies) * 2.0)),
            }
        )

    current_anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    current_claims = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    artist_summary = {
        "leakage": sum(float(a.estimated_recoverable or 0.0) for a in current_anomalies),
        "recovery": sum(float(c.recovered_amount or 0.0) for c in current_claims),
        "anomaly_density": float(len(current_anomalies)) / max(1.0, float(len(current_claims) or 1.0)),
        "catalog_health": max(20.0, 100.0 - (len(current_anomalies) * 2.0)),
    }
    return {
        "artist_id": artist_id,
        **cross_artist_benchmarks(artist_summary, peer_population),
    }


@router.get("/{artist_id}/recovery/playbook")
def recovery_playbook(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    queue = priority_queue(artist_id, db)
    deadline = deadline_risk(artist_id, db)
    return {
        "artist_id": artist_id,
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
