"""Data Residency Policy API.

Endpoints:
  PUT  /admin/orgs/{org_id}/data-residency    – upsert policy
  GET  /admin/orgs/{org_id}/data-residency    – get current policy
  POST /admin/orgs/{org_id}/data-residency/check – test if a region is permitted
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.data_residency import (
    DataResidencyPolicy,
    DataResidencyPolicySchema,
    DataResidencyPolicyUpsert,
)
from XR7.services.branding import inject_branding_metadata
from XR7.services.data_residency_service import assert_region_allowed, get_policy

router = APIRouter(prefix="/admin/orgs", tags=["data-residency"])

_ADMIN_HEADER = "X-Admin-Key"
_EXPECTED_KEY = "admin-secret"


def _require_admin(x_admin_key: str = Header(alias=_ADMIN_HEADER)):
    if x_admin_key != _EXPECTED_KEY:
        raise HTTPException(status_code=403, detail="Admin key required")


@router.put(
    "/{org_id}/data-residency",
    response_model=DataResidencyPolicySchema,
    summary="Upsert data residency policy for an org",
    dependencies=[Depends(_require_admin)],
)
def upsert_policy(
    org_id: str,
    body: DataResidencyPolicyUpsert,
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    db: Session = Depends(get_db),
) -> DataResidencyPolicy:
    policy = db.query(DataResidencyPolicy).filter(DataResidencyPolicy.org_id == org_id).first()
    if not policy:
        policy = DataResidencyPolicy(org_id=org_id, created_by=x_actor_email)
        db.add(policy)
    policy.primary_region = body.primary_region
    policy.permitted_regions = body.permitted_regions
    policy.allow_cross_region_ai = body.allow_cross_region_ai
    policy.audit_log_region_locked = body.audit_log_region_locked
    policy.active = True
    db.commit()
    db.refresh(policy)
    return policy


@router.get(
    "/{org_id}/data-residency",
    response_model=DataResidencyPolicySchema,
    summary="Get data residency policy for an org",
    dependencies=[Depends(_require_admin)],
)
def get_org_policy(org_id: str, db: Session = Depends(get_db)) -> DataResidencyPolicy:
    policy = get_policy(org_id, db)
    if not policy:
        raise HTTPException(status_code=404, detail="No residency policy found for org")
    return policy


@router.post(
    "/{org_id}/data-residency/check",
    summary="Check whether a storage region is permitted",
)
def check_region(org_id: str, body: dict, db: Session = Depends(get_db)) -> dict:
    """Returns {allowed: bool} — useful for pre-flight checks before writes."""
    region = (body or {}).get("target_region") or (body or {}).get("region")
    if not region:
        raise HTTPException(status_code=422, detail="target_region is required")
    try:
        assert_region_allowed(org_id, region, db)
        return inject_branding_metadata(db, {"allowed": True, "org_id": org_id, "region": region})
    except HTTPException as exc:
        return inject_branding_metadata(
            db,
            {"allowed": False, "org_id": org_id, "region": region, "reason": exc.detail},
        )
