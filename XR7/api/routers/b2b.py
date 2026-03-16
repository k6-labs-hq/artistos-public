from __future__ import annotations

import os
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["b2b"])


def _require_org_key(x_org_key: str = Header(default="", alias="X-Org-Key")) -> None:
    expected = os.environ.get("XR7_ORG_KEY", "")
    if not expected or not x_org_key or x_org_key != expected:
        raise HTTPException(status_code=401, detail="Invalid org key")


class BulkOnboardRequest(BaseModel):
    artists: list[dict]


@router.get("/b2b/org/{org_id}/dashboard")
def b2b_dashboard(org_id: str, _: None = Header(default=None, alias="X-Org-Key")):
    _require_org_key(_)
    return {
        "org_id": org_id,
        "portfolio": {
            "artists": 42,
            "aggregate_recoverable": 840000.0,
            "anonymized_metrics": True,
        },
    }


@router.get("/org/{org_id}/portfolio")
def org_portfolio(org_id: str, _: None = Header(default=None, alias="X-Org-Key")):
    _require_org_key(_)
    return {
        "org_id": org_id,
        "anonymized": True,
        "metrics": {"leakage_discovered": 1400000.0, "claims_active": 128},
    }


@router.post("/b2b/org/{org_id}/artists/bulk-onboard")
def bulk_onboard(org_id: str, payload: BulkOnboardRequest, _: None = Header(default=None, alias="X-Org-Key")):
    _require_org_key(_)
    return {"org_id": org_id, "onboarded": len(payload.artists), "white_label": True}
