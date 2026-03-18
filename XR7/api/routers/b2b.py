from __future__ import annotations

import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.services.org_dashboard_service import OrgDashboardService
from XR7.services.branding import branding_metadata, get_branding_profile, org_help_articles

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
