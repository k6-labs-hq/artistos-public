from __future__ import annotations

import csv
import io
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly
from XR7.models.base import get_db
from XR7.models.claim import Claim
from XR7.services.branding import branding_metadata, get_branding_profile, org_help_articles
from XR7.services.org_dashboard_service import OrgDashboardService

router = APIRouter(tags=["b2b"])

_ORG_ROLES = {
    "publisher_admin",
    "publisher_analyst",
    "manager",
    "attorney",
    "label_ops",
    "viewer",
    "org_admin",
    "org_analyst",
    "org_manager",
    "xr7_operator",
    "xr7_engineer",
}


def _require_org_key(x_org_key: str = Header(default="", alias="X-Org-Key")) -> None:
    expected = os.environ.get("XR7_ORG_KEY", "")
    if not expected or not x_org_key or x_org_key != expected:
        raise HTTPException(status_code=401, detail="Invalid org key")


def _require_org_access(
    *,
    x_org_key: str,
    x_org_role: str,
    allowed_roles: set[str],
) -> str:
    _require_org_key(x_org_key)
    role = (x_org_role or "").strip().lower()
    if role not in _ORG_ROLES:
        raise HTTPException(status_code=403, detail="Invalid or missing org role")
    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Org role not permitted for this operation")
    return role


class BulkOnboardRequest(BaseModel):
    artists: list[dict]


@router.get("/b2b/org/{org_id}/dashboard")
def b2b_dashboard(
    org_id: str,
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
):
    role = _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles={"publisher_admin", "publisher_analyst", "manager", "label_ops", "attorney", "viewer"},
    )
    brand = get_branding_profile(db=None, org_id=org_id)
    return {
        "org_id": org_id,
        "actor": x_org_actor or None,
        "role": role,
        "branding": branding_metadata(brand),
        "portfolio": {
            "artists": 42,
            "aggregate_recoverable": 840000.0,
            "anonymized_metrics": True,
        },
    }


@router.get("/org/{org_id}/portfolio")
def org_portfolio(
    org_id: str,
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
):
    role = _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles={"publisher_admin", "publisher_analyst", "manager", "label_ops", "attorney", "viewer"},
    )
    brand = get_branding_profile(db=None, org_id=org_id)
    return {
        "org_id": org_id,
        "actor": x_org_actor or None,
        "role": role,
        "branding": branding_metadata(brand),
        "anonymized": True,
        "metrics": {"leakage_discovered": 1400000.0, "claims_active": 128},
    }


@router.post("/b2b/org/{org_id}/artists/bulk-onboard")
def bulk_onboard(
    org_id: str,
    payload: BulkOnboardRequest,
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
):
    role = _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles={"publisher_admin", "manager", "label_ops"},
    )
    brand = get_branding_profile(db=None, org_id=org_id)
    return {
        "org_id": org_id,
        "actor": x_org_actor or None,
        "role": role,
        "branding": branding_metadata(brand),
        "onboarded": len(payload.artists),
        "white_label": True,
    }


@router.get("/management/{org_id}/dashboard")
def management_dashboard(
    org_id: str,
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
    db: Session = Depends(get_db),
):
    role = _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles={"org_admin", "org_analyst", "org_manager", "publisher_admin", "publisher_analyst"},
    )
    payload = OrgDashboardService(db).management_dashboard(org_id)
    brand = get_branding_profile(db, org_id)
    if bool(brand.get("white_label_enabled")):
        payload["dashboard_title"] = f"{brand.get('display_name')} Dashboard"
        payload["support"] = {
            "support_email": brand.get("support_email"),
            "support_phone": brand.get("support_phone"),
        }
        payload["legal_disclaimer"] = brand.get("legal_disclaimer")
        payload["help_articles"] = org_help_articles(db, org_id)
    payload["branding"] = branding_metadata(brand)
    return {
        **payload,
        "actor": x_org_actor or None,
        "role": role,
    }


@router.get("/management/{org_id}/dashboard/v2")
def management_dashboard_v2(
    org_id: str,
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
    db: Session = Depends(get_db),
):
    role = _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles={"org_admin", "org_analyst", "org_manager", "publisher_admin", "publisher_analyst"},
    )

    service = OrgDashboardService(db)
    payload = service.management_dashboard(org_id)
    artists = service.scoped_artists_for_org(org_id)
    scoped = service._collect_artist_scoped_rows(artists)

    anomalies = scoped["anomalies"]
    claims = scoped["claims"]

    critical_anomalies = [a for a in anomalies if str(a.severity) == "CRITICAL"]
    now = datetime.now(timezone.utc)
    sol_sensitive_claims = []
    for c in claims:
        if c.sol_deadline is None:
            continue
        deadline = c.sol_deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        if (deadline - now).days <= 60:
            sol_sensitive_claims.append(c)

    payload["v2"] = {
        "portfolio_cohorts": {
            "artists_total": len(artists),
            "critical_anomaly_artists": len({str(a.artist_id) for a in critical_anomalies}),
            "sol_sensitive_claim_artists": len({str(c.artist_id) for c in sol_sensitive_claims}),
        },
        "execution": {
            "critical_anomalies": len(critical_anomalies),
            "sol_sensitive_claims": len(sol_sensitive_claims),
            "claims_in_review": sum(1 for c in claims if str(c.status) == "IN_REVIEW"),
            "claims_paid": sum(1 for c in claims if str(c.status) == "PAID"),
        },
        "operator_actions": [
            "Escalate critical anomaly clusters to legal review.",
            "Resolve SOL-sensitive claims this sprint.",
            "Prioritize unresolved metadata backlog for top-value catalogs.",
        ],
    }

    brand = get_branding_profile(db, org_id)
    payload["branding"] = branding_metadata(brand)
    return {
        **payload,
        "actor": x_org_actor or None,
        "role": role,
    }


@router.get("/management/{org_id}/artists/{artist_id}")
def management_artist_drilldown(
    org_id: str,
    artist_id: str,
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
    db: Session = Depends(get_db),
):
    role = _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles={"org_admin", "org_analyst", "org_manager", "publisher_admin", "publisher_analyst"},
    )
    try:
        payload = OrgDashboardService(db).management_artist_detail(org_id, artist_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    brand = get_branding_profile(db, org_id)
    payload["branding"] = branding_metadata(brand)
    return {
        **payload,
        "actor": x_org_actor or None,
        "role": role,
    }


@router.get("/management/{org_id}/catalog")
def management_catalog_drilldown(
    org_id: str,
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
    db: Session = Depends(get_db),
):
    role = _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles={"org_admin", "org_analyst", "org_manager", "publisher_admin", "publisher_analyst"},
    )
    payload = OrgDashboardService(db).management_catalog(org_id)
    payload["branding"] = branding_metadata(get_branding_profile(db, org_id))
    return {
        **payload,
        "actor": x_org_actor or None,
        "role": role,
    }


@router.get("/management/{org_id}/anomalies")
def management_anomalies_drilldown(
    org_id: str,
    severity: str | None = Query(default=None),
    status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=250),
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
    db: Session = Depends(get_db),
):
    role = _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles={"org_admin", "org_analyst", "org_manager", "publisher_admin", "publisher_analyst"},
    )
    payload = OrgDashboardService(db).management_anomalies(
        org_id,
        severity=severity,
        status=status,
        category=category,
        limit=limit,
    )
    payload["branding"] = branding_metadata(get_branding_profile(db, org_id))
    return {
        **payload,
        "actor": x_org_actor or None,
        "role": role,
    }


@router.get("/management/{org_id}/claims")
def management_claims_drilldown(
    org_id: str,
    status: str | None = Query(default=None),
    sol_window_days: int = Query(default=30, ge=1, le=365),
    limit: int = Query(default=100, ge=1, le=250),
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
    db: Session = Depends(get_db),
):
    role = _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles={"org_admin", "org_analyst", "org_manager", "publisher_admin", "publisher_analyst"},
    )
    payload = OrgDashboardService(db).management_claims(
        org_id,
        status=status,
        sol_window_days=sol_window_days,
        limit=limit,
    )
    payload["branding"] = branding_metadata(get_branding_profile(db, org_id))
    return {
        **payload,
        "actor": x_org_actor or None,
        "role": role,
    }


@router.get("/management/{org_id}/forecast")
def management_forecast(
    org_id: str,
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
    db: Session = Depends(get_db),
):
    role = _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles={"org_admin", "org_analyst", "org_manager", "publisher_admin", "publisher_analyst"},
    )
    payload = OrgDashboardService(db).management_forecast(org_id)
    payload["branding"] = branding_metadata(get_branding_profile(db, org_id))
    return {
        **payload,
        "actor": x_org_actor or None,
        "role": role,
    }


@router.get("/xr7/operator/dashboard")
def xr7_operator_dashboard(
    org_id: str | None = Query(default=None),
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
    db: Session = Depends(get_db),
):
    role = _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles={"xr7_operator", "xr7_engineer"},
    )
    payload = OrgDashboardService(db).operator_dashboard()
    payload["branding"] = branding_metadata(get_branding_profile(db, org_id))
    return {
        **payload,
        "actor": x_org_actor or None,
        "role": role,
    }


# ---------------------------------------------------------------------------
# PARTNER-301 — Portfolio scoped export endpoints
# ---------------------------------------------------------------------------

# Roles that may export the full portfolio summary (CSV).
_EXPORT_ROLES: set[str] = {"org_admin", "publisher_admin", "org_analyst", "publisher_analyst"}

# Roles that may export legal/attorney packet summaries (CSV).
_LEGAL_EXPORT_ROLES: set[str] = {"attorney", "org_admin", "publisher_admin"}


@router.get("/management/{org_id}/portfolio/export")
def export_portfolio_csv(
    org_id: str,
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
    db: Session = Depends(get_db),
):
    """
    Export a CSV summary of the org's portfolio.

    Scoped to artists that belong to *this org only* via
    ``OrgDashboardService.scoped_artists_for_org()``.

    Allowed roles: org_admin, publisher_admin, org_analyst, publisher_analyst.
    """
    _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles=_EXPORT_ROLES,
    )

    service = OrgDashboardService(db)
    artists = service.scoped_artists_for_org(org_id)
    artist_ids = [a.id for a in artists]

    # Aggregate per-artist anomaly and claim counts.
    anomaly_counts: dict[str, int] = {}
    recoverable_totals: dict[str, float] = {}
    for a in (
        db.query(Anomaly.artist_id, Anomaly.estimated_recoverable)
        .filter(Anomaly.artist_id.in_(artist_ids))
        .all()
        if artist_ids
        else []
    ):
        anomaly_counts[a.artist_id] = anomaly_counts.get(a.artist_id, 0) + 1
        recoverable_totals[a.artist_id] = (
            recoverable_totals.get(a.artist_id, 0.0) + float(a.estimated_recoverable or 0.0)
        )

    claim_counts: dict[str, int] = {}
    for c in (
        db.query(Claim.artist_id)
        .filter(Claim.artist_id.in_(artist_ids))
        .all()
        if artist_ids
        else []
    ):
        claim_counts[c.artist_id] = claim_counts.get(c.artist_id, 0) + 1

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([
        "artist_id",
        "artist_name",
        "total_anomalies",
        "total_estimated_recoverable_usd",
        "total_claims",
        "export_org_id",
        "exported_at",
    ])
    exported_at = datetime.now(timezone.utc).isoformat()
    for artist in artists:
        writer.writerow([
            artist.id,
            artist.name or "",
            anomaly_counts.get(artist.id, 0),
            round(recoverable_totals.get(artist.id, 0.0), 2),
            claim_counts.get(artist.id, 0),
            org_id,
            exported_at,
        ])

    return StreamingResponse(
        io.BytesIO(out.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="portfolio_{org_id}.csv"',
            "X-Partner-Scope": org_id,
        },
    )


@router.get("/management/{org_id}/legal/export")
def export_legal_packets_csv(
    org_id: str,
    x_org_key: str = Header(default="", alias="X-Org-Key"),
    x_org_role: str = Header(default="", alias="X-Org-Role"),
    x_org_actor: str = Header(default="", alias="X-Org-Actor"),
    db: Session = Depends(get_db),
):
    """
    Export a CSV of active claims with SOL risk metadata for legal/attorney review.

    Scoped to the org's artists.  Allowed roles: attorney, org_admin, publisher_admin.
    """
    _require_org_access(
        x_org_key=x_org_key,
        x_org_role=x_org_role,
        allowed_roles=_LEGAL_EXPORT_ROLES,
    )

    service = OrgDashboardService(db)
    artists = service.scoped_artists_for_org(org_id)
    artist_ids = [a.id for a in artists]

    claims = (
        db.query(Claim)
        .filter(Claim.artist_id.in_(artist_ids))
        .order_by(Claim.sol_deadline.asc().nullslast())
        .all()
        if artist_ids
        else []
    )

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow([
        "claim_id",
        "artist_id",
        "status",
        "recovered_amount",
        "sol_deadline",
        "governing_law_state",
        "contract_type",
        "attorney_review_required",
        "export_org_id",
        "exported_at",
    ])
    exported_at = datetime.now(timezone.utc).isoformat()
    for claim in claims:
        writer.writerow([
            claim.id,
            claim.artist_id,
            str(claim.status.value if hasattr(claim.status, "value") else claim.status),
            round(float(claim.recovered_amount or 0.0), 2),
            claim.sol_deadline.isoformat() if claim.sol_deadline else "",
            claim.governing_law_state or "",
            claim.contract_type or "",
            claim.attorney_review_required,
            org_id,
            exported_at,
        ])

    return StreamingResponse(
        io.BytesIO(out.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="legal_packets_{org_id}.csv"',
            "X-Partner-Scope": org_id,
        },
    )
