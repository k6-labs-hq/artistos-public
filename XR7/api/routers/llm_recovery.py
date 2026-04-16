from __future__ import annotations

import asyncio
import importlib
import json
from collections import defaultdict, deque
from datetime import datetime, timezone
from functools import wraps
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.api.authz import artist_or_404 as _artist_or_404
from XR7.api.authz import authorize_team_access as _authorize_team_access
from XR7.llm.claim_drafter import claim_drafter
from XR7.models.anomaly import Anomaly, AnomalySchema
from XR7.models.base import get_db
from XR7.models.claim import Claim, ClaimSchema
from XR7.models.ml_feedback import MLFeedbackEvent, MLFeedbackType
from XR7.models.team_access import TeamRole
from XR7.tasks.pipeline import (
    llm_generate_advice_task,
    llm_generate_demand_letter_task,
    llm_generate_negotiation_script_task,
)
from xr7_common.logging import get_logger
from xr7_common.settings import settings

try:
    redis = importlib.import_module("redis.asyncio")
except Exception:  # pragma: no cover - optional dependency
    redis = None


logger = get_logger(__name__)
router = APIRouter(tags=["Recovery Intelligence (LLM)"])


_RATE_WINDOWS: dict[str, deque[float]] = defaultdict(deque)
_RATE_LOCK = asyncio.Lock()


def rate_limit_2026(limit: int = 30, window_seconds: int = 60):
    """Simple async in-process rate limiter for 2026 API endpoints."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            actor_email = kwargs.get("x_actor_email") or "anonymous"
            key = f"{func.__name__}:{str(actor_email).strip().lower()}"
            now = datetime.now(timezone.utc).timestamp()
            cutoff = now - window_seconds

            async with _RATE_LOCK:
                window = _RATE_WINDOWS[key]
                while window and window[0] < cutoff:
                    window.popleft()
                if len(window) >= limit:
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                window.append(now)
            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def _redis_client():
    if redis is None:
        return None
    try:
        return redis.from_url(settings.redis_url, decode_responses=True)
    except Exception:
        logger.exception("Redis client init failed")
        return None


_MEMORY_HISTORY: dict[str, list[dict[str, str]]] = {}


async def _load_history(artist_id: str) -> list[dict[str, str]]:
    client = await _redis_client()
    key = f"xr7:llm:history:{artist_id}"
    if client is None:
        return list(_MEMORY_HISTORY.get(key, []))

    try:
        raw = await client.get(key)
        if not raw:
            return []
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, list) else []
    except Exception:
        logger.exception("Failed to load advice history from Redis")
        return []


async def _store_history(artist_id: str, history: list[dict[str, str]]) -> None:
    client = await _redis_client()
    key = f"xr7:llm:history:{artist_id}"
    trimmed = history[-20:]
    if client is None:
        _MEMORY_HISTORY[key] = trimmed
        return

    try:
        await client.set(key, json.dumps(trimmed), ex=7 * 24 * 3600)
    except Exception:
        logger.exception("Failed to persist advice history in Redis")


class DemandLetterRequest(BaseModel):
    claim_id: str | None = None
    anomaly: dict = Field(default_factory=dict)
    evidence: dict = Field(default_factory=dict)


class DemandLetterResponse(BaseModel):
    artist_id: str
    claim_id: str | None = None
    markdown: str
    evidence_zip_link: str | None = None


class NegotiationScriptRequest(BaseModel):
    claim: dict = Field(default_factory=dict)


class NegotiationScriptResponse(BaseModel):
    artist_id: str
    claim_id: str | None = None
    script: dict[str, Any]


class AdviceRequest(BaseModel):
    artist_dashboard: dict = Field(default_factory=dict)
    user_message: str | None = None


class AdviceResponse(BaseModel):
    artist_id: str
    response: str
    conversation_history: list[dict[str, str]]


@router.post("/artists/{artist_id}/llm/demand-letter", response_model=DemandLetterResponse)
@rate_limit_2026(limit=20, window_seconds=60)
async def llm_demand_letter(
    artist_id: str,
    payload: DemandLetterRequest,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    # Check if LLM provider is available
    if not claim_drafter.is_available:
        raise HTTPException(
            status_code=503, detail="LLM service unavailable - API key not configured"
        )

    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )

    anomaly_data = payload.anomaly
    evidence_data = payload.evidence
    claim: Claim | None = None

    if payload.claim_id:
        claim = (
            db.query(Claim)
            .filter(Claim.id == payload.claim_id, Claim.artist_id == artist_id)
            .first()
        )
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        if not anomaly_data:
            row = db.query(Anomaly).filter(Anomaly.id == claim.anomaly_id).first()
            anomaly_data = AnomalySchema.model_validate(row).model_dump(mode="json") if row else {}
        if not evidence_data:
            evidence_data = claim.evidence or {}

    markdown = await claim_drafter.async_generate_demand_letter(
        anomaly_data, evidence_data, artist_id
    )

    if claim is not None:
        claim.evidence = claim.evidence or {}
        claim.evidence.setdefault("llm_outputs", {})
        claim.evidence["llm_outputs"]["demand_letter_markdown"] = markdown
        claim.evidence["llm_outputs"]["demand_letter_generated_at"] = datetime.now(
            timezone.utc
        ).isoformat()
        db.commit()
        llm_generate_demand_letter_task.delay(claim.id, anomaly_data, evidence_data, artist_id)

    evidence_zip_link = (
        f"/claims/{payload.claim_id}/evidence/export?format=zip" if payload.claim_id else None
    )
    return DemandLetterResponse(
        artist_id=artist_id,
        claim_id=payload.claim_id,
        markdown=markdown,
        evidence_zip_link=evidence_zip_link,
    )


@router.post(
    "/artists/{artist_id}/llm/negotiation-script", response_model=NegotiationScriptResponse
)
@rate_limit_2026(limit=25, window_seconds=60)
async def llm_negotiation_script(
    artist_id: str,
    payload: NegotiationScriptRequest,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    # Check if LLM provider is available
    if not claim_drafter.is_available:
        raise HTTPException(
            status_code=503, detail="LLM service unavailable - API key not configured"
        )

    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )

    claim_payload = payload.claim
    claim_id = claim_payload.get("id") if isinstance(claim_payload, dict) else None
    if claim_id:
        claim = db.query(Claim).filter(Claim.id == claim_id, Claim.artist_id == artist_id).first()
        if claim:
            claim_payload = ClaimSchema.model_validate(claim).model_dump(mode="json")

    script = await claim_drafter.async_generate_negotiation_script(claim_payload)

    if claim_id:
        row = db.query(Claim).filter(Claim.id == claim_id, Claim.artist_id == artist_id).first()
        if row:
            row.evidence = row.evidence or {}
            row.evidence.setdefault("llm_outputs", {})
            row.evidence["llm_outputs"]["negotiation_script"] = script
            row.evidence["llm_outputs"]["negotiation_script_generated_at"] = datetime.now(
                timezone.utc
            ).isoformat()
            db.commit()
            llm_generate_negotiation_script_task.delay(claim_id, claim_payload)

    return NegotiationScriptResponse(artist_id=artist_id, claim_id=claim_id, script=script)


@router.post("/artists/{artist_id}/llm/advice", response_model=AdviceResponse)
@rate_limit_2026(limit=40, window_seconds=60)
async def llm_personalized_advice(
    artist_id: str,
    payload: AdviceRequest,
    db: Session = Depends(get_db),
    x_actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
    x_actor_role: str | None = Header(default=None, alias="X-Actor-Role"),
):
    # Check if LLM provider is available
    if not claim_drafter.is_available:
        raise HTTPException(
            status_code=503, detail="LLM service unavailable - API key not configured"
        )

    _artist_or_404(artist_id, db)
    _authorize_team_access(
        artist_id,
        db,
        {TeamRole.ARTIST, TeamRole.MANAGER, TeamRole.ATTORNEY},
        actor_email=x_actor_email,
        actor_role=x_actor_role,
    )

    history = await _load_history(artist_id)
    if payload.user_message:
        history.append({"role": "user", "content": payload.user_message})

    dashboard_with_history = {
        **payload.artist_dashboard,
        "conversation_history": history[-10:],
    }
    advice = await claim_drafter.async_generate_personalized_advice(dashboard_with_history)

    history.append({"role": "assistant", "content": advice})
    await _store_history(artist_id, history)

    event = MLFeedbackEvent(
        artist_id=artist_id,
        feedback_type=MLFeedbackType.RECOVERY_RESULT.value,
        source_type="llm_advice",
        source_id=None,
        payload={
            "conversation_history": history[-10:],
            "advice": advice,
        },
        outcome="ADVICE_GENERATED",
    )
    db.add(event)
    db.commit()

    llm_generate_advice_task.delay(artist_id, payload.artist_dashboard, history[-10:])

    return AdviceResponse(artist_id=artist_id, response=advice, conversation_history=history[-10:])
