"""Data Residency Enforcement Service.

Provides:
  - get_policy(org_id, db) — fetch policy row for an org
  - assert_region_allowed(org_id, target_region, db) — raises HTTP 451
    if target_region violates the org's policy
  - assert_ai_allowed(org_id, db) — raises HTTP 451 if LLM cross-region
    processing is forbidden
"""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from XR7.models.data_residency import DataRegion, DataResidencyPolicy


def get_policy(org_id: str, db: Session) -> DataResidencyPolicy | None:
    return (
        db.query(DataResidencyPolicy)
        .filter(
            DataResidencyPolicy.org_id == org_id,
            DataResidencyPolicy.active == True,  # noqa: E712
        )
        .first()
    )


def _permitted_set(policy: DataResidencyPolicy) -> set[str]:
    regions = {policy.primary_region}
    if policy.permitted_regions:
        for r in policy.permitted_regions.split(","):
            r = r.strip()
            if r:
                regions.add(r)
    return regions


def assert_region_allowed(org_id: str, target_region: str, db: Session) -> None:
    """Raise HTTP 451 if target_region is not in the org's permitted set."""
    policy = get_policy(org_id, db)
    if policy is None:
        return  # no policy = no restriction
    if policy.primary_region == DataRegion.GLOBAL:
        return
    permitted = _permitted_set(policy)
    if target_region not in permitted:
        raise HTTPException(
            status_code=451,
            detail=(
                f"Data residency policy for org '{org_id}' prohibits storage in "
                f"region '{target_region}'. Permitted: {sorted(permitted)}"
            ),
        )


def assert_ai_allowed(org_id: str, db: Session) -> None:
    """Raise HTTP 451 if cross-region AI processing is forbidden for this org."""
    policy = get_policy(org_id, db)
    if policy is None:
        return
    if not policy.allow_cross_region_ai:
        raise HTTPException(
            status_code=451,
            detail=(
                f"Data residency policy for org '{org_id}' prohibits cross-region "
                "AI/LLM processing."
            ),
        )
