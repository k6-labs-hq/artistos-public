from __future__ import annotations

from datetime import datetime, timezone
from operator import add
from typing import Annotated, Any, TypedDict
from uuid import uuid4


class XR7State(TypedDict, total=False):
    artist_id: str
    run_id: str
    current_step: str
    confidence_scores: dict[str, float]
    anomalies: Annotated[list[dict[str, Any]], add]
    claims: Annotated[list[dict[str, Any]], add]
    evidence_hashes: Annotated[list[str], add]
    negotiation_history: Annotated[list[dict[str, Any]], add]
    error_log: Annotated[list[str], add]
    final_payout: float | None

    artist_intent: str | None
    portal_guidance: Annotated[list[dict[str, Any]], add]
    fixed_files: Annotated[list[dict[str, Any]], add]
    upload_errors: Annotated[list[str], add]
    catalog_profile: dict[str, Any]
    distributor_sync_status: dict[str, Any]
    explanations: Annotated[list[str], add]
    expected_earnings: dict[str, Any]
    split_conflicts: Annotated[list[dict[str, Any]], add]
    split_suggestions: Annotated[list[dict[str, Any]], add]
    comfort_messages: Annotated[list[str], add]
    fast_track_claim: dict[str, Any] | None
    public_profile: dict[str, Any]
    welcome_summary: str | None
    registration_actions: Annotated[list[dict[str, Any]], add]
    rights_conflicts: Annotated[list[dict[str, Any]], add]
    ugc_opportunities: Annotated[list[dict[str, Any]], add]
    contract_terms: dict[str, Any]
    release_timeline: Annotated[list[dict[str, Any]], add]
    readiness_score: float | None
    follow_up_actions: Annotated[list[dict[str, Any]], add]
    persona_profile: dict[str, Any]
    onboarding_progress: dict[str, Any]

    agent_activity: Annotated[list[dict[str, Any]], add]
    trace: Annotated[list[dict[str, Any]], add]
    reflection_score: float
    reflection_reasoning: str
    reflection_suggestions: Annotated[list[str], add]
    next_action: str
    retry_count: int
    pending_agent: str | None


def initial_state(artist_id: str, run_id: str | None = None) -> XR7State:
    rid = run_id or str(uuid4())
    return {
        "artist_id": artist_id,
        "run_id": rid,
        "current_step": "supervisor",
        "confidence_scores": {},
        "anomalies": [],
        "claims": [],
        "evidence_hashes": [],
        "negotiation_history": [],
        "error_log": [],
        "final_payout": None,
        "artist_intent": None,
        "portal_guidance": [],
        "fixed_files": [],
        "upload_errors": [],
        "catalog_profile": {},
        "distributor_sync_status": {},
        "explanations": [],
        "expected_earnings": {},
        "split_conflicts": [],
        "split_suggestions": [],
        "comfort_messages": [],
        "fast_track_claim": None,
        "public_profile": {},
        "welcome_summary": None,
        "registration_actions": [],
        "rights_conflicts": [],
        "ugc_opportunities": [],
        "contract_terms": {},
        "release_timeline": [],
        "readiness_score": None,
        "follow_up_actions": [],
        "persona_profile": {},
        "onboarding_progress": {
            "steps_total": 10,
            "steps_completed": 0,
            "missing": [
                "terms",
                "files",
                "catalog",
                "splits",
                "portal_guidance",
            ],
        },
        "agent_activity": [],
        "trace": [],
        "reflection_score": 1.0,
        "reflection_reasoning": "",
        "reflection_suggestions": [],
        "next_action": "proceed",
        "retry_count": 0,
        "pending_agent": None,
    }


def set_confidence(state: XR7State, component: str, score: float) -> XR7State:
    merged = dict(state.get("confidence_scores") or {})
    merged[component] = round(max(0.0, min(1.0, float(score))), 4)
    return {"confidence_scores": merged}


def update_onboarding_progress(state: XR7State, *, completed_step: str | None = None) -> XR7State:
    current = dict(state.get("onboarding_progress") or {})
    missing = list(current.get("missing") or [])
    if completed_step and completed_step in missing:
        missing.remove(completed_step)
    steps_total = int(current.get("steps_total") or 10)
    steps_completed = max(0, steps_total - len(missing))
    return {
        "onboarding_progress": {
            "steps_total": steps_total,
            "steps_completed": steps_completed,
            "missing": missing,
            "completed": steps_completed >= steps_total,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    }


def add_trace_event(state: XR7State, *, node: str, event: str, payload: dict[str, Any] | None = None) -> XR7State:
    return {
        "trace": [
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "node": node,
                "event": event,
                "payload": payload or {},
            }
        ]
    }
