from __future__ import annotations

import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.claim import Claim
from XR7.recovery.deadline_risk_engine import evaluate_deadline_risk
from XR7.models.anomaly import Anomaly
from XR7.models.contract import Contract
from XR7.models.payment import Payment
from XR7.services.branding import branding_metadata, get_branding_profile

router = APIRouter(prefix="/workspace", tags=["workspace"])


def _require_workspace_role(
    x_workspace_key: str = Header(default="", alias="X-Workspace-Key"),
    x_workspace_role: str = Header(default="", alias="X-Workspace-Role"),
) -> str:
    expected = os.environ.get("WORKSPACE_API_KEY", "")
    if expected and not hmac.compare_digest(x_workspace_key, expected):
        raise HTTPException(status_code=401, detail="Invalid workspace key")

    role = x_workspace_role.strip().lower()
    if role not in {"manager", "attorney", "enterprise"}:
        raise HTTPException(status_code=403, detail="Workspace role must be manager, attorney, or enterprise")
    return role


@router.get("/overview")
def workspace_overview(role: str = Depends(_require_workspace_role), db: Session = Depends(get_db)):
    artists = db.query(Artist).count()
    claims = db.query(Claim).count()
    anomalies = db.query(Anomaly).count()
    open_claims = db.query(Claim).filter(Claim.status.notin_(["PAID", "CLOSED"]))
    return {
        "role": role,
        "branding": branding_metadata(get_branding_profile(None, None)),
        "artists": artists,
        "claims": claims,
        "anomalies": anomalies,
        "open_claims": open_claims.count(),
    }


@router.get("/artists")
def workspace_artists(role: str = Depends(_require_workspace_role), db: Session = Depends(get_db)):
    rows = db.query(Artist).order_by(Artist.created_at.desc()).limit(500).all()
    return {
        "role": role,
        "branding": branding_metadata(get_branding_profile(None, None)),
        "artists": [
            {
                "id": r.id,
                "name": r.name,
                "email": r.email,
                "status": str(r.status),
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
    }


@router.get("/claims")
def workspace_claims(role: str = Depends(_require_workspace_role), db: Session = Depends(get_db)):
    rows = db.query(Claim).order_by(Claim.updated_at.desc()).limit(1000).all()
    return {
        "role": role,
        "branding": branding_metadata(get_branding_profile(None, None)),
        "claims": [
            {
                "id": c.id,
                "artist_id": c.artist_id,
                "status": str(c.status),
                "claim_type": c.claim_type,
                "recovered_amount": float(c.recovered_amount or 0.0),
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in rows
        ],
    }


@router.get("/deadlines")
def workspace_deadlines(role: str = Depends(_require_workspace_role), db: Session = Depends(get_db)):
    artists = db.query(Artist).all()
    out = []
    for artist in artists:
        anomalies = db.query(Anomaly).filter(Anomaly.artist_id == artist.id).all()
        claims = db.query(Claim).filter(Claim.artist_id == artist.id).all()
        contracts = db.query(Contract).filter(Contract.artist_id == artist.id).all()
        payments = db.query(Payment).filter(Payment.artist_id == artist.id).all()
        risk = evaluate_deadline_risk(
            anomalies=[
                {
                    "id": a.id,
                    "category": str(a.category),
                    "subtype": a.subtype,
                    "territory": a.territory,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                    "estimated_recoverable": float(a.estimated_recoverable or 0.0),
                }
                for a in anomalies
            ],
            claims=[
                {
                    "id": c.id,
                    "status": str(c.status),
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in claims
            ],
            contracts=[{"id": c.id, "terms": c.terms or {}, "territory": c.territory} for c in contracts],
            payments=[{"id": p.id, "amount": p.amount} for p in payments],
        )
        out.append({"artist_id": artist.id, "artist_name": artist.name, **risk})

    return {
        "role": role,
        "branding": branding_metadata(get_branding_profile(None, None)),
        "deadlines": out,
    }
