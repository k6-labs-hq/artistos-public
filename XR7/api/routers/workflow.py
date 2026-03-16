from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.agents.orchestrator import get_run_trace
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata
from XR7.tasks.celery_tasks import run_artist_workflow

router = APIRouter(tags=["workflow"])


class WorkflowRunResponse(BaseModel):
    artist_id: str
    run_id: str
    status: str
    status_url: str
    branding: dict[str, Any] | None = None


@router.post("/artists/{artist_id}/workflow/run-full-autonomous", response_model=WorkflowRunResponse)
def run_full_autonomous_workflow(artist_id: str, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

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
