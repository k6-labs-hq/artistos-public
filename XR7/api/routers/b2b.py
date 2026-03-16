from __future__ import annotations

import os
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["b2b"])

_ORG_ROLES = {
    "publisher_admin",
    "publisher_analyst",
    "manager",
    "attorney",
    "label_ops",
    "viewer",
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
    return {
        "org_id": org_id,
        "actor": x_org_actor or None,
        "role": role,
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
    return {
        "org_id": org_id,
        "actor": x_org_actor or None,
        "role": role,
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
    return {
        "org_id": org_id,
        "actor": x_org_actor or None,
        "role": role,
        "onboarded": len(payload.artists),
        "white_label": True,
    }
