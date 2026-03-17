from __future__ import annotations

import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from XR7.models.admin_audit_log import AdminAuditLog, AdminAuditLogSchema
from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist, ArtistSchema
from XR7.models.base import get_db
from XR7.models.celero_transaction import CeleroTransaction, CeleroTransactionSchema
from XR7.models.claim import Claim, ClaimSchema
from XR7.models.review_queue import ReviewItem, ReviewItemSchema
from XR7.recovery.sol_calculator import SOL_DISCLAIMER, calculate_sol

router = APIRouter(prefix="/admin", tags=["admin"])


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
    return _paginated_response([ArtistSchema.model_validate(r).model_dump() for r in rows], total, limit, offset)


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
    query = db.query(CeleroTransaction)
    if status:
        query = query.filter(CeleroTransaction.status == status)
    if tx_type:
        query = query.filter(CeleroTransaction.type == tx_type)
    if artist_id:
        query = query.filter(CeleroTransaction.artist_id == artist_id)

    total = query.count()
    rows = query.order_by(CeleroTransaction.updated_at.desc()).offset(offset).limit(limit).all()
    _log(db, actor, "list", "transactions", {"total": total, "status": status, "tx_type": tx_type, "artist_id": artist_id})
    return _paginated_response([CeleroTransactionSchema.model_validate(r).model_dump() for r in rows], total, limit, offset)


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
    snapshot = {
        "artists": db.query(func.count(Artist.id)).scalar() or 0,
        "claims": db.query(func.count(Claim.id)).scalar() or 0,
        "anomalies": db.query(func.count(Anomaly.id)).scalar() or 0,
        "transactions": db.query(func.count(CeleroTransaction.id)).scalar() or 0,
        "review_queue_open": db.query(func.count(ReviewItem.id)).filter(ReviewItem.status == "OPEN").scalar() or 0,
    }
    _log(db, actor, "overview", "admin", snapshot)
    return snapshot
