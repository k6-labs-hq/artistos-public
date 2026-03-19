from __future__ import annotations

import asyncio
import os
from typing import Any

from XR7.agents.recovery_execution_graph import run_recovery_execution_agent
from XR7.agents.two_agent_orchestrator_graph import (
    get_latest_artist_state as _get_latest_artist_state,
    get_run_state_by_id,
    get_run_trace,
    list_handoffs_for_artist,
    query_handoffs,
    run_two_agent_orchestrator,
    run_two_agent_orchestrator_sync,
)
from XR7.agents.two_agent_state import TwoAgentState, bootstrap_state
from XR7.graph.nodes.support_agent import ArtistSupportAgent


def _readiness_threshold() -> float:
    raw = os.environ.get("XR7_ONBOARDING_READINESS_THRESHOLD", "85")
    try:
        return float(raw)
    except Exception:  # noqa: BLE001
        return 85.0


def _supervisor_next(state: dict[str, Any]) -> str:
    artist_status = str(state.get("artist_status") or "preparing").lower()
    if artist_status in {"ready", "active"}:
        return "recovery_execution"
    return "onboarding_preparation"


async def run_xr7_recovery_orchestra(artist_id: str, run_id: str | None = None) -> TwoAgentState:
    return await run_two_agent_orchestrator(
        artist_id,
        run_id,
        readiness_threshold=_readiness_threshold(),
    )


def run_xr7_recovery_orchestra_sync(artist_id: str, run_id: str | None = None) -> TwoAgentState:
    return run_two_agent_orchestrator_sync(
        artist_id,
        run_id,
        readiness_threshold=_readiness_threshold(),
    )


async def run_export_prep_pipeline(artist_id: str, run_id: str | None = None) -> TwoAgentState:
    rid = run_id or ""
    state = get_run_state_by_id(rid) if rid else None
    if not state:
        state = bootstrap_state(artist_id, run_id, readiness_threshold=_readiness_threshold())
    state = dict(state)
    state["artist_status"] = "ready"
    state["export_requested"] = True
    state["active_agent"] = "recovery_execution"
    state["workflow_phase"] = "recovery_execution"
    return await run_recovery_execution_agent(state)


def run_export_prep_pipeline_sync(artist_id: str, run_id: str | None = None) -> TwoAgentState:
    return asyncio.run(run_export_prep_pipeline(artist_id, run_id))


async def run_tvfilm_vertical_orchestra(artist_id: str, run_id: str | None = None) -> TwoAgentState:
    rid = run_id or ""
    state = get_run_state_by_id(rid) if rid else None
    if not state:
        state = bootstrap_state(artist_id, run_id, readiness_threshold=_readiness_threshold())
    state = dict(state)
    state["artist_status"] = "active"
    state["tvfilm_mode"] = True
    state["active_agent"] = "recovery_execution"
    state["workflow_phase"] = "recovery_execution"
    return await run_recovery_execution_agent(state)


def run_tvfilm_vertical_orchestra_sync(artist_id: str, run_id: str | None = None) -> TwoAgentState:
    return asyncio.run(run_tvfilm_vertical_orchestra(artist_id, run_id))


async def run_support_agent_turn(
    artist_id: str,
    *,
    message: str,
    thread_id: str,
    dashboard_context: dict[str, Any] | None = None,
) -> TwoAgentState:
    state: TwoAgentState = bootstrap_state(artist_id)
    state.update(
        {
            "support_mode": True,
            "support_thread_id": thread_id,
            "support_user_message": message,
            "dashboard_context": dashboard_context or {},
            "current_step": "support_request",
        }
    )
    patch = await ArtistSupportAgent(state)
    out = dict(state)
    out.update(patch)
    return out


def run_support_agent_turn_sync(
    artist_id: str,
    *,
    message: str,
    thread_id: str,
    dashboard_context: dict[str, Any] | None = None,
) -> TwoAgentState:
    return asyncio.run(
        run_support_agent_turn(
            artist_id,
            message=message,
            thread_id=thread_id,
            dashboard_context=dashboard_context,
        )
    )


def get_latest_artist_state(artist_id: str) -> TwoAgentState | None:
    return _get_latest_artist_state(artist_id)


__all__ = [
    "_supervisor_next",
    "get_latest_artist_state",
    "get_run_trace",
    "list_handoffs_for_artist",
    "query_handoffs",
    "run_export_prep_pipeline",
    "run_export_prep_pipeline_sync",
    "run_support_agent_turn",
    "run_support_agent_turn_sync",
    "run_tvfilm_vertical_orchestra",
    "run_tvfilm_vertical_orchestra_sync",
    "run_xr7_recovery_orchestra",
    "run_xr7_recovery_orchestra_sync",
]
