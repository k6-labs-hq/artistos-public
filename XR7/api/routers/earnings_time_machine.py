"""
Earnings Time Machine — API endpoints.

POST /artists/{artist_id}/earnings/time-machine
GET  /artists/{artist_id}/earnings/time-machine/result
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.api.routers.auth import get_optional_auth_payload
from XR7.models.base import get_db
from XR7.modules.earnings_time_machine import EarningsTimeMachine
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["earnings_time_machine"])


class TimeMachineRequest(BaseModel):
    granularity: str = "year"
    metadata_repair_log: list[dict] = []
    anomaly_history: list[dict] = []
    split_verification_history: list[dict] = []
    catalog_health_scores: list[dict] = []


@router.post("/artists/{artist_id}/earnings/time-machine")
def trigger_time_machine(
    artist_id: str,
    body: TimeMachineRequest,
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Trigger Earnings Time Machine analysis for this artist."""
    get_artist_or_404(artist_id, db)
    engine = EarningsTimeMachine(db)
    result = engine.run(
        artist_id=artist_id,
        granularity=body.granularity,
        metadata_repair_log=body.metadata_repair_log,
        anomaly_history=body.anomaly_history,
        split_verification_history=body.split_verification_history,
        catalog_health_scores=body.catalog_health_scores,
    )
    return inject_branding_metadata(db, result)


@router.get("/artists/{artist_id}/earnings/time-machine/result")
def get_time_machine_result(
    artist_id: str,
    granularity: str = "year",
    db: Session = Depends(get_db),
    _auth: dict | None = Depends(get_optional_auth_payload),
) -> dict[str, Any]:
    """Retrieve the latest Earnings Time Machine result."""
    get_artist_or_404(artist_id, db)
    engine = EarningsTimeMachine(db)
    result = engine.run(artist_id=artist_id, granularity=granularity)
    return inject_branding_metadata(db, result)
