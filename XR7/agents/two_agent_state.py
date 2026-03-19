from __future__ import annotations

from typing import Any, TypedDict

from XR7.agents.state import XR7State, add_trace_event, initial_state, update_onboarding_progress


class TwoAgentHandoff(TypedDict, total=False):
    handoff_id: str
    artist_id: str
    from_agent: str
    to_agent: str
    readiness_score: float
    readiness_threshold: float
    catalog_profile: dict[str, Any]
    public_profile: dict[str, Any]
    onboarding_progress: dict[str, Any]
    contract_terms: dict[str, Any]
    rights_conflicts: list[dict[str, Any]]
    release_timeline: list[dict[str, Any]]
    persona_profile: dict[str, Any]
    tvfilm_preparation: dict[str, Any]
    timestamp: str


class TwoAgentState(XR7State, total=False):
    artist_status: str
    readiness_threshold: float
    handoff_trigger: str | None
    active_agent: str
    handoff: TwoAgentHandoff
    handoff_history: list[TwoAgentHandoff]
    orchestrator_decision: str
    prepared_state: dict[str, Any]
    recovery_execution_state: dict[str, Any]
    tvfilm_mode: bool
    workflow_phase: str


def bootstrap_state(artist_id: str, run_id: str | None = None, *, readiness_threshold: float = 85.0) -> TwoAgentState:
    state: TwoAgentState = dict(initial_state(artist_id, run_id))
    state.update(
        {
            "artist_status": "preparing",
            "readiness_threshold": float(readiness_threshold),
            "handoff_trigger": None,
            "active_agent": "onboarding_preparation",
            "handoff": {},
            "handoff_history": [],
            "orchestrator_decision": "pending",
            "prepared_state": {},
            "recovery_execution_state": {},
            "tvfilm_mode": False,
            "workflow_phase": "onboarding_preparation",
        }
    )
    return state


__all__ = [
    "TwoAgentHandoff",
    "TwoAgentState",
    "add_trace_event",
    "bootstrap_state",
    "update_onboarding_progress",
]
