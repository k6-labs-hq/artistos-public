"""XR7 Advisor Copilot: natural-language catalog + recovery Q&A for VIPs.

Endpoints:
  POST /artists/{artist_id}/copilot/query   – ask the XR7 Advisor
  POST /artists/{artist_id}/copilot/feedback – thumbs up/down on a response
  GET  /artists/{artist_id}/copilot/history  – recent query history
  GET  /artists/{artist_id}/weekly-brief     – latest AI weekly brief
  POST /artists/{artist_id}/weekly-brief/generate – trigger brief generation
"""
from __future__ import annotations

import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.vip import (
    CopilotQueryRequest,
    CopilotQueryResponse,
    CopilotQuerySchema,
    WeeklyBriefSchema,
)
from XR7.services.vip_service import VipService

router = APIRouter(tags=["copilot"])

# ---------------------------------------------------------------------------
# Guard helper (shared pattern)
# ---------------------------------------------------------------------------

def _require_vip(artist_id: str, db: Session) -> None:
    svc = VipService(db)
    if not svc.is_vip(artist_id):
        raise HTTPException(
            status_code=403,
            detail="Founders Circle / VIP membership required.",
        )


# ---------------------------------------------------------------------------
# Copilot LLM query builder
# ---------------------------------------------------------------------------

def _build_copilot_context(artist_id: str, db: Session) -> dict:
    """Collects catalog, recovery, and persona context for prompt injection."""
    from XR7.models.artist import Artist
    from XR7.models.claim import Claim, ClaimStatus

    ctx: dict = {}
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if artist:
        ctx["artist_name"] = artist.name
        ctx["primary_vertical"] = artist.primary_vertical
        ctx["tvfilm_role"] = artist.tvfilm_role
        ctx["status"] = artist.status

    open_claims = (
        db.query(Claim)
        .filter(Claim.artist_id == artist_id, Claim.status != ClaimStatus.RESOLVED.value)
        .count()
    )
    ctx["open_claims"] = open_claims

    from XR7.services.vip_service import VipService
    persona = VipService(db).get_persona(artist_id)
    if persona:
        ctx["detected_roles"] = persona.detected_roles
        ctx["genre_tags"] = persona.genre_tags
        ctx["notable_works"] = persona.notable_works
        ctx["bio_snippet"] = persona.bio_snippet

    return ctx


def _call_copilot_llm(query: str, context: dict) -> tuple[str, float, list[str]]:
    """
    Calls the LLM layer to answer the user query given their context.

    Returns (response_text, confidence, sources_cited).
    Uses the existing XR7 LLM infrastructure.
    """
    try:
        from XR7.llm.advisor import ask_xr7_advisor
        return ask_xr7_advisor(query, context)
    except Exception:
        # Graceful degradation: use a structured template response
        context.get("artist_name", "you")
        open_claims = context.get("open_claims", 0)
        roles = context.get("detected_roles") or []
        response = (
            f"Based on your XR7 profile, here's what I can tell you: "
            f"You currently have {open_claims} open recovery claim(s). "
        )
        if roles:
            response += f"Your detected roles include {', '.join(roles)}. "
        response += (
            "For detailed recovery analysis, check your Recovery Story timeline. "
            "For questions about specific works or earnings, your XR7 Advisor has full catalog context."
        )
        return response, 0.72, ["XR7 catalog", "recovery ledger"]


# ---------------------------------------------------------------------------
# Copilot endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/artists/{artist_id}/copilot/query",
    response_model=CopilotQueryResponse,
    summary="Ask the personalized XR7 Advisor copilot",
)
def copilot_query(
    artist_id: str,
    body: CopilotQueryRequest,
    db: Session = Depends(get_db),
) -> CopilotQueryResponse:
    _require_vip(artist_id, db)

    context: dict = {}
    if body.include_catalog_context or body.include_recovery_context:
        context = _build_copilot_context(artist_id, db)

    t0 = time.monotonic()
    response_text, confidence, sources = _call_copilot_llm(body.query, context)
    latency_ms = int((time.monotonic() - t0) * 1000)

    # Action suggestions based on context
    action_suggestions: list[str] = []
    if context.get("open_claims", 0) > 0:
        action_suggestions.append("Review open claims in your Recovery Story timeline")
    if context.get("primary_vertical") == "tv_film":
        action_suggestions.append("Upload your latest residuals statement for TV/Film gap analysis")
    action_suggestions.append("Schedule your monthly 1:1 strategy call via your Concierge Inbox")

    svc = VipService(db)
    query_record = svc.record_copilot_query(
        artist_id,
        body.query,
        response_text,
        context_snapshot=context,
        confidence=confidence,
        sources_cited=sources,
        latency_ms=latency_ms,
    )

    return CopilotQueryResponse(
        query_id=query_record.id,
        response=response_text,
        confidence=confidence,
        sources_cited=sources,
        action_suggestions=action_suggestions,
        latency_ms=latency_ms,
    )


class CopilotFeedbackRequest(BaseModel):
    query_id: str
    thumbs_up: bool


class CopilotFeedbackResponse(BaseModel):
    success: bool


@router.post(
    "/artists/{artist_id}/copilot/feedback",
    response_model=CopilotFeedbackResponse,
    summary="Submit thumbs up/down feedback on a copilot response",
)
def copilot_feedback(
    artist_id: str,
    body: CopilotFeedbackRequest,
    db: Session = Depends(get_db),
) -> CopilotFeedbackResponse:
    _require_vip(artist_id, db)
    svc = VipService(db)
    try:
        svc.feedback_copilot(body.query_id, artist_id, body.thumbs_up)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return CopilotFeedbackResponse(success=True)


@router.get(
    "/artists/{artist_id}/copilot/history",
    response_model=list[CopilotQuerySchema],
    summary="Get recent copilot query history",
)
def copilot_history(
    artist_id: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[CopilotQuerySchema]:
    _require_vip(artist_id, db)
    from XR7.models.vip import CopilotQuery
    rows = (
        db.query(CopilotQuery)
        .filter(CopilotQuery.artist_id == artist_id)
        .order_by(CopilotQuery.created_at.desc())
        .limit(limit)
        .all()
    )
    return [CopilotQuerySchema.model_validate(r) for r in rows]


# ---------------------------------------------------------------------------
# Weekly brief endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/artists/{artist_id}/weekly-brief",
    response_model=Optional[WeeklyBriefSchema],
    summary="Get the latest AI-generated weekly brief",
)
def get_weekly_brief(
    artist_id: str,
    db: Session = Depends(get_db),
) -> Optional[WeeklyBriefSchema]:
    _require_vip(artist_id, db)
    from XR7.models.vip import WeeklyBrief
    brief = (
        db.query(WeeklyBrief)
        .filter(WeeklyBrief.artist_id == artist_id)
        .order_by(WeeklyBrief.created_at.desc())
        .first()
    )
    if not brief:
        return None
    return WeeklyBriefSchema.model_validate(brief)


class GenerateBriefResponse(BaseModel):
    job_id: str
    brief_week: str
    status: str


@router.post(
    "/artists/{artist_id}/weekly-brief/generate",
    response_model=GenerateBriefResponse,
    summary="Trigger on-demand weekly brief generation",
)
def generate_weekly_brief(
    artist_id: str,
    db: Session = Depends(get_db),
) -> GenerateBriefResponse:
    _require_vip(artist_id, db)
    from datetime import date

    from XR7.tasks.vip_tasks import generate_weekly_brief_task

    brief_week = date.today().strftime("%G-W%V")  # ISO week
    task = generate_weekly_brief_task.delay(artist_id, brief_week)
    return GenerateBriefResponse(
        job_id=task.id,
        brief_week=brief_week,
        status="generating",
    )
