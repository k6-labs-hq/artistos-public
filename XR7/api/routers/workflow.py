from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.agents.orchestrator import get_run_trace, query_handoffs
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.api.deps import get_artist_or_404
from XR7.services.branding import inject_branding_metadata
from XR7.tasks.celery_tasks import run_artist_workflow

router = APIRouter(tags=["workflow"])


class WorkflowRunResponse(BaseModel):
    artist_id: str
    run_id: str
    status: str
    status_url: str
    branding: dict[str, Any] | None = None


class AgentHandoffResponse(BaseModel):
    id: str
    run_id: str
    artist_id: str
    handoff_id: str
    from_agent: str
    to_agent: str
    readiness_score: float
    readiness_threshold: float
    status: str
    payload: dict[str, Any]
    created_at: str | None = None


class AgentHandoffListResponse(BaseModel):
    artist_id: str
    total: int
    limit: int
    offset: int
    handoffs: list[AgentHandoffResponse]
    branding: dict[str, Any] | None = None


@router.post("/artists/{artist_id}/workflow/run-full-autonomous", response_model=WorkflowRunResponse)
def run_full_autonomous_workflow(artist_id: str, db: Session = Depends(get_db)):
    artist = get_artist_or_404(artist_id, db)

    run_id = str(uuid4())
    run_artist_workflow.delay(artist_id, run_id)
    payload = inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "run_id": run_id,
            "status": "queued",
            "status_url": f"/artists/{artist_id}/agent-trace/{run_id}",
        },
    )
    return WorkflowRunResponse(**payload)


@router.get("/artists/{artist_id}/workflow/runs/{run_id}")
def workflow_run_status(artist_id: str, run_id: str, db: Session = Depends(get_db)):
    trace = get_run_trace(artist_id, run_id)
    if not trace.get("found"):
        return inject_branding_metadata(db, {
            "artist_id": artist_id,
            "run_id": run_id,
            "status": "queued_or_unknown",
            "current_step": None,
            "event_count": 0,
        })
    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "run_id": run_id,
        "status": "running_or_complete",
        "current_step": trace.get("current_step"),
        "event_count": len(trace.get("events") or []),
        "confidence_scores": trace.get("confidence_scores") or {},
    })


@router.get("/artists/{artist_id}/workflow/handoffs", response_model=AgentHandoffListResponse)
def workflow_handoffs(
    artist_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    from_agent: str | None = Query(default=None),
    to_agent: str | None = Query(default=None),
    status: str | None = Query(default=None),
    since: datetime | None = Query(default=None),
    until: datetime | None = Query(default=None),
    db: Session = Depends(get_db),
):
    artist = get_artist_or_404(artist_id, db)

    handoff_result = query_handoffs(
        artist_id=artist_id,
        limit=limit,
        offset=offset,
        from_agent=from_agent,
        to_agent=to_agent,
        status=status,
        since=since,
        until=until,
    )
    payload = inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "total": handoff_result["total"],
            "limit": limit,
            "offset": offset,
            "handoffs": handoff_result["items"],
        },
    )
    return AgentHandoffListResponse(**payload)
