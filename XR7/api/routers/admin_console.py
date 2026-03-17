from __future__ import annotations

import hmac
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.models.admin_audit_log import AdminAuditLog, AdminAuditLogSchema
from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist, ArtistSchema
from XR7.models.base import get_db
from XR7.models.claim import Claim, ClaimSchema
from XR7.models.review_queue import ReviewItem, ReviewItemSchema
from XR7.models.trolley_transaction import TrolleyTransaction, TrolleyTransactionSchema
from XR7.recovery.sol_calculator import SOL_DISCLAIMER, calculate_sol
from XR7.services.founder_program import founder_status_payload, get_or_create_platform_config

router = APIRouter(prefix="/admin", tags=["admin"])


class FounderAssignRequest(BaseModel):
    contingency_fee_percent: float | None = None
    reason: str | None = None


class FounderCohortLimitUpdateRequest(BaseModel):
    founder_cohort_limit: int


def _require_admin(
    x_admin_key: str = Header(default="", alias="X-Admin-Key"),
    x_admin_actor: str | None = Header(default=None, alias="X-Admin-Actor"),
) -> str:
    expected = os.environ.get("ADMIN_API_KEY") or os.environ.get("WIDGET_ADMIN_KEY", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Admin API key is not configured on this server.")
    if not x_admin_key or not hmac.compare_digest(x_admin_key, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing admin key.")
    return (x_admin_actor or "unknown-admin")[:128]


def _log(db: Session, actor: str, action: str, resource_type: str, details: dict | None = None) -> None:
    row = AdminAuditLog(actor=actor, action=action, resource_type=resource_type, details=details or {})
    db.add(row)
    db.commit()


def _paginated_response(items: list, total: int, limit: int, offset: int) -> dict:
    return {"total": int(total), "limit": limit, "offset": offset, "items": items}


def _founder_label(artist: Artist) -> str:
    if artist.is_founder and artist.founder_slot_number is not None:
        return f"Founder #{int(artist.founder_slot_number)} ✓"
    return "Standard"


@router.get("/artists")
def list_artists(
    status: str | None = Query(default=None),
    q: str | None = Query(default=None),
    sort: str = Query(default="created_at_desc", pattern="^(created_at_desc|created_at_asc|name_asc|name_desc)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    actor: str = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Artist)
    if status:
        query = query.filter(Artist.status == status)
    if q:
        query = query.filter(Artist.name.ilike(f"%{q.strip()}%"))

    total = query.count()
    if sort == "created_at_asc":
        query = query.order_by(Artist.created_at.asc())
    elif sort == "name_asc":
        query = query.order_by(Artist.name.asc())
    elif sort == "name_desc":
        query = query.order_by(Artist.name.desc())
    else:
        query = query.order_by(Artist.created_at.desc())

    rows = query.offset(offset).limit(limit).all()
    _log(db, actor, "list", "artists", {"total": total, "status": status, "q": q, "sort": sort})
    items = []
    for r in rows:
        payload = ArtistSchema.model_validate(r).model_dump()
        payload["founder_label"] = _founder_label(r)
        items.append(payload)
    return _paginated_response(items, total, limit, offset)


@router.get("/claims")
def list_claims(
    status: str | None = Query(default=None),
    artist_id: str | None = Query(default=None),
    jurisdiction: str | None = Query(default=None),
    sort: str = Query(default="updated_at_desc", pattern="^(updated_at_desc|updated_at_asc|amount_desc|amount_asc)$"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    actor: str = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Claim)
    if status:
        query = query.filter(Claim.status == status)
    if artist_id:
        query = query.filter(Claim.artist_id == artist_id)
    if jurisdiction:
        query = query.filter(func.lower(Claim.governing_law_state) == jurisdiction.strip().lower())

    total = query.count()
    if sort == "updated_at_asc":
        query = query.order_by(Claim.updated_at.asc())
    elif sort == "amount_desc":
        query = query.order_by(func.coalesce(Claim.recovered_amount, 0.0).desc())
    elif sort == "amount_asc":
        query = query.order_by(func.coalesce(Claim.recovered_amount, 0.0).asc())
    else:
        query = query.order_by(Claim.updated_at.desc())

    rows = query.offset(offset).limit(limit).all()
    _log(
        db,
        actor,
        "list",
        "claims",
        {"total": total, "status": status, "artist_id": artist_id, "jurisdiction": jurisdiction, "sort": sort},
    )
    return _paginated_response([ClaimSchema.model_validate(r).model_dump() for r in rows], total, limit, offset)


@router.get("/reports/sol-risk")
def sol_risk_report(
    jurisdiction: str | None = Query(default=None),
    actor: str = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Claim)
    if jurisdiction:
        query = query.filter(func.lower(Claim.governing_law_state) == jurisdiction.strip().lower())
    rows = query.all()

    risk_rows = []
    counts = {"EXPIRED": 0, "URGENT": 0, "AT_RISK": 0, "OK": 0, "UNKNOWN": 0}
    for claim in rows:
        sol = calculate_sol(
            governing_law_state=claim.governing_law_state,
            contract_type=claim.contract_type,
            infringement_date=claim.infringement_date,
            discovery_date=claim.discovery_date,
        )
        status = str(sol.get("sol_status") or "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1
        risk_rows.append(
            {
                "claim_id": claim.id,
                "artist_id": claim.artist_id,
                "status": status,
                "days_remaining": sol.get("sol_days_remaining"),
                "deadline": sol.get("sol_deadline").date().isoformat() if sol.get("sol_deadline") else None,
                "governing_law_state": sol.get("governing_law_state"),
                "contract_type": sol.get("contract_type"),
                "citation": sol.get("sol_citation_source"),
            }
        )

    risk_rows.sort(key=lambda x: (x["days_remaining"] is None, x["days_remaining"] or 999999))
    _log(
        db,
        actor,
        "report",
        "sol_risk",
        {"jurisdiction": jurisdiction, "rows": len(risk_rows), "counts": counts},
    )
    return {
        "total_claims": len(risk_rows),
        "counts_by_status": counts,
        "claims": risk_rows,
        "legal_disclaimer": SOL_DISCLAIMER,
    }


@router.get("/anomalies")
def list_anomalies(
    status: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    artist_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    actor: str = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Anomaly)
    if status:
        query = query.filter(Anomaly.status == status)
    if severity:
        query = query.filter(Anomaly.severity == severity)
    if artist_id:
        query = query.filter(Anomaly.artist_id == artist_id)

    total = query.count()
    rows = query.order_by(Anomaly.created_at.desc()).offset(offset).limit(limit).all()
    _log(
        db,
        actor,
        "list",
        "anomalies",
        {"total": total, "status": status, "severity": severity, "artist_id": artist_id},
    )
    return _paginated_response(
        [
            {
                "id": r.id,
                "artist_id": r.artist_id,
                "category": str(r.category),
                "subtype": r.subtype,
                "severity": str(r.severity),
                "status": str(r.status),
                "estimated_recoverable": r.estimated_recoverable,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
        total,
        limit,
        offset,
    )


@router.get("/transactions")
def list_transactions(
    status: str | None = Query(default=None),
    tx_type: str | None = Query(default=None),
    artist_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    actor: str = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(TrolleyTransaction)
    if status:
        query = query.filter(TrolleyTransaction.status == status)
    if tx_type:
        query = query.filter(TrolleyTransaction.type == tx_type)
    if artist_id:
        query = query.filter(TrolleyTransaction.artist_id == artist_id)

    total = query.count()
    rows = query.order_by(TrolleyTransaction.updated_at.desc()).offset(offset).limit(limit).all()
    _log(db, actor, "list", "transactions", {"total": total, "status": status, "tx_type": tx_type, "artist_id": artist_id})
    return _paginated_response([TrolleyTransactionSchema.model_validate(r).model_dump() for r in rows], total, limit, offset)


@router.get("/review-queue")
def list_review_queue(
    status: str | None = Query(default=None),
    artist_id: str | None = Query(default=None),
    source_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    actor: str = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(ReviewItem)
    if status:
        query = query.filter(ReviewItem.status == status)
    if artist_id:
        query = query.filter(ReviewItem.artist_id == artist_id)
    if source_type:
        query = query.filter(ReviewItem.source_type == source_type)

    total = query.count()
    rows = query.order_by(ReviewItem.created_at.desc()).offset(offset).limit(limit).all()
    _log(
        db,
        actor,
        "list",
        "review_queue",
        {"total": total, "status": status, "artist_id": artist_id, "source_type": source_type},
    )
    return _paginated_response([ReviewItemSchema.model_validate(r).model_dump() for r in rows], total, limit, offset)


@router.get("/audit-logs", response_model=list[AdminAuditLogSchema])
def list_audit_logs(
    actor_filter: str | None = Query(default=None),
    action: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    actor: str = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(AdminAuditLog)
    if actor_filter:
        query = query.filter(AdminAuditLog.actor == actor_filter)
    if action:
        query = query.filter(AdminAuditLog.action == action)
    rows = query.order_by(AdminAuditLog.created_at.desc()).offset(offset).limit(limit).all()
    _log(db, actor, "list", "audit_logs", {"actor_filter": actor_filter, "action": action, "returned": len(rows)})
    return rows


@router.get("/overview")
def admin_overview(actor: str = Depends(_require_admin), db: Session = Depends(get_db)):
    founder = founder_status_payload(db)
    snapshot = {
        "artists": db.query(func.count(Artist.id)).scalar() or 0,
        "claims": db.query(func.count(Claim.id)).scalar() or 0,
        "anomalies": db.query(func.count(Anomaly.id)).scalar() or 0,
        "transactions": db.query(func.count(TrolleyTransaction.id)).scalar() or 0,
        "review_queue_open": db.query(func.count(ReviewItem.id)).filter(ReviewItem.status == "OPEN").scalar() or 0,
        "founder_cohort": {
            "slots_total": founder["slots_total"],
            "slots_filled": founder["slots_filled"],
            "slots_remaining": founder["slots_remaining"],
            "cohort_open": founder["cohort_open"],
        },
    }
    _log(db, actor, "overview", "admin", snapshot)
    return snapshot


@router.get("/founders")
def founder_roster(
    limit: int = Query(default=200, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    actor: str = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Artist)
        .filter(Artist.is_founder.is_(True))
        .order_by(Artist.founder_slot_number.asc(), Artist.activated_at.asc())
    )
    total = query.count()
    rows = query.offset(offset).limit(limit).all()
    items = [
        {
            "artist_id": row.id,
            "artist_name": row.name,
            "slot_number": row.founder_slot_number,
            "activated_at": row.activated_at.isoformat() if row.activated_at else None,
            "founder_locked_at": row.founder_locked_at.isoformat() if row.founder_locked_at else None,
            "contingency_fee_percent": float(row.contingency_fee_percent or 0.0),
        }
        for row in rows
    ]
    _log(db, actor, "report", "founder_roster", {"total": total, "limit": limit, "offset": offset})
    return _paginated_response(items, total, limit, offset)


@router.get("/reports/founder-cohort")
def founder_cohort_report(actor: str = Depends(_require_admin), db: Session = Depends(get_db)):
    founders = db.query(Artist).filter(Artist.is_founder.is_(True)).all()
    standard = db.query(Artist).filter(Artist.is_founder.is_(False)).all()

    founder_ids = [a.id for a in founders]
    standard_ids = [a.id for a in standard]

    founder_claims = db.query(Claim).filter(Claim.artist_id.in_(founder_ids)).all() if founder_ids else []
    standard_claims = db.query(Claim).filter(Claim.artist_id.in_(standard_ids)).all() if standard_ids else []

    founder_recovered = [float(c.recovered_amount or 0.0) for c in founder_claims if c.recovered_amount is not None]
    standard_recovered = [float(c.recovered_amount or 0.0) for c in standard_claims if c.recovered_amount is not None]
    founder_fees = [float(c.contingency_fee or 0.0) for c in founder_claims]

    cohort = founder_status_payload(db)
    report = {
        "total_founders_activated": len(founders),
        "slots_remaining": cohort["slots_remaining"],
        "average_recovery_amount": {
            "founder": round(sum(founder_recovered) / max(1, len(founder_recovered)), 2),
            "standard": round(sum(standard_recovered) / max(1, len(standard_recovered)), 2),
        },
        "total_platform_fees_collected_from_founder_cohort": round(sum(founder_fees), 2),
    }
    _log(db, actor, "report", "founder_cohort", report)
    return report


@router.post("/artists/{artist_id}/founder/assign")
def assign_founder_manually(
    artist_id: str,
    payload: FounderAssignRequest,
    actor: str = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    cfg = get_or_create_platform_config(db, for_update=True)
    if artist.is_founder and artist.founder_slot_number is not None:
        _log(db, actor, "update", "founder_assign", {"artist_id": artist_id, "noop": "already_founder"})
        return {
            "artist_id": artist_id,
            "is_founder": True,
            "founder_slot_number": artist.founder_slot_number,
            "contingency_fee_percent": float(artist.contingency_fee_percent or cfg.founder_fee_percent),
        }

    if int(cfg.founder_slots_filled) >= int(cfg.founder_cohort_limit):
        raise HTTPException(status_code=409, detail="Founder cohort is full. Increase cohort limit before assigning.")

    cfg.founder_slots_filled = int(cfg.founder_slots_filled) + 1
    artist.is_founder = True
    artist.founder_slot_number = int(cfg.founder_slots_filled)
    artist.founder_locked_at = artist.founder_locked_at or datetime.now(timezone.utc)
    artist.contingency_fee_percent = min(float(payload.contingency_fee_percent or cfg.founder_fee_percent), float(cfg.founder_fee_percent))

    db.commit()
    _log(
        db,
        actor,
        "update",
        "founder_assign",
        {
            "artist_id": artist_id,
            "slot": artist.founder_slot_number,
            "reason": payload.reason,
        },
    )
    return {
        "artist_id": artist_id,
        "is_founder": True,
        "founder_slot_number": artist.founder_slot_number,
        "contingency_fee_percent": float(artist.contingency_fee_percent or 0.0),
        "slots_filled": int(cfg.founder_slots_filled),
        "slots_total": int(cfg.founder_cohort_limit),
    }


@router.put("/founder/cohort-limit")
def update_founder_cohort_limit(
    payload: FounderCohortLimitUpdateRequest,
    actor: str = Depends(_require_admin),
    db: Session = Depends(get_db),
):
    cfg = get_or_create_platform_config(db, for_update=True)
    current = int(cfg.founder_cohort_limit)
    if payload.founder_cohort_limit < current:
        raise HTTPException(status_code=400, detail="Founder cohort limit can only be increased.")

    cfg.founder_cohort_limit = int(payload.founder_cohort_limit)
    db.commit()
    _log(
        db,
        actor,
        "update",
        "founder_cohort_limit",
        {"previous": current, "current": int(cfg.founder_cohort_limit)},
    )
    return {
        "founder_cohort_limit": int(cfg.founder_cohort_limit),
        "founder_slots_filled": int(cfg.founder_slots_filled),
        "slots_remaining": max(0, int(cfg.founder_cohort_limit) - int(cfg.founder_slots_filled)),
        "cohort_open": int(cfg.founder_slots_filled) < int(cfg.founder_cohort_limit),
    }
