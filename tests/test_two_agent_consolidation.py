from __future__ import annotations

import asyncio

from tests.conftest import TestSession
from XR7.agents.onboarding_preparation_graph import run_onboarding_preparation_agent
from XR7.agents.recovery_execution_graph import run_recovery_execution_agent
from XR7.agents.two_agent_orchestrator_graph import (
    list_handoffs_for_artist,
    run_two_agent_orchestrator,
)
from XR7.agents.two_agent_state import bootstrap_state
from XR7.models.agent_handoff import AgentHandoffRecord


def test_onboarding_agent_emits_handoff_when_readiness_threshold_met(monkeypatch):
    async def _prep_node(state):
        return {
            "readiness_score": 92.0,
            "confidence_scores": {"artist_readiness_score": 0.95},
            "catalog_profile": {"work_count": 4},
            "onboarding_progress": {"completed": True},
        }

    monkeypatch.setattr(
        "XR7.agents.onboarding_preparation_graph.PREPARATION_NODE_ORDER",
        ["artist_readiness_score"],
    )
    monkeypatch.setattr(
        "XR7.agents.onboarding_preparation_graph.PREPARATION_NODE_MAP",
        {"artist_readiness_score": _prep_node},
    )

    state = bootstrap_state("artist-1", "run-1", readiness_threshold=85.0)
    state["artist_status"] = "preparing"

    out = asyncio.run(run_onboarding_preparation_agent(state))
    assert out["artist_status"] == "ready"
    assert out["handoff"]["from_agent"] == "onboarding_preparation"
    assert out["handoff"]["to_agent"] == "recovery_execution"


def test_recovery_agent_refuses_to_run_while_preparing():
    state = bootstrap_state("artist-2", "run-2")
    state["artist_status"] = "preparing"

    out = asyncio.run(run_recovery_execution_agent(state))
    assert out["orchestrator_decision"] == "skip_recovery_not_ready"


def test_recovery_agent_runs_when_artist_ready(monkeypatch):
    call_order: list[str] = []

    async def _node_a(state):
        call_order.append("node_a")
        return {"confidence_scores": {"node_a": 0.95}}

    async def _node_b(state):
        call_order.append("node_b")
        return {"confidence_scores": {"node_b": 0.95}}

    monkeypatch.setattr(
        "XR7.agents.recovery_execution_graph.RECOVERY_NODE_ORDER",
        ["node_a", "node_b"],
    )
    monkeypatch.setattr(
        "XR7.agents.recovery_execution_graph.RECOVERY_NODE_MAP",
        {"node_a": _node_a, "node_b": _node_b},
    )

    state = bootstrap_state("artist-3", "run-3")
    state["artist_status"] = "ready"

    out = asyncio.run(run_recovery_execution_agent(state))
    assert call_order == ["node_a", "node_b"]
    assert out["artist_status"] == "active"


def test_orchestrator_routes_preparing_artist_to_prep_then_recovery(monkeypatch):
    async def _prep(state):
        return {
            **state,
            "artist_status": "ready",
            "active_agent": "onboarding_preparation",
            "handoff": {"handoff_id": "h1", "from_agent": "onboarding_preparation", "to_agent": "recovery_execution"},
        }

    async def _recovery(state):
        return {**state, "artist_status": "active", "active_agent": "recovery_execution"}

    monkeypatch.setattr("XR7.agents.two_agent_orchestrator_graph._derive_artist_status_from_db", lambda artist_id: "preparing")
    monkeypatch.setattr("XR7.agents.two_agent_orchestrator_graph.run_onboarding_preparation_agent", _prep)
    monkeypatch.setattr("XR7.agents.two_agent_orchestrator_graph.run_recovery_execution_agent", _recovery)

    out = asyncio.run(run_two_agent_orchestrator("artist-4", "run-4"))
    assert out["active_agent"] == "recovery_execution"
    assert out["artist_status"] == "active"


def test_orchestrator_persists_handoff_record(monkeypatch):
    async def _prep(state):
        return {
            **state,
            "artist_status": "ready",
            "active_agent": "onboarding_preparation",
            "handoff": {
                "handoff_id": "handoff-fixed-1",
                "artist_id": "artist-5",
                "from_agent": "onboarding_preparation",
                "to_agent": "recovery_execution",
                "readiness_score": 90.0,
                "readiness_threshold": 85.0,
            },
        }

    async def _recovery(state):
        return {**state, "artist_status": "active", "active_agent": "recovery_execution"}

    monkeypatch.setattr("XR7.agents.two_agent_orchestrator_graph._derive_artist_status_from_db", lambda artist_id: "preparing")
    monkeypatch.setattr("XR7.agents.two_agent_orchestrator_graph.run_onboarding_preparation_agent", _prep)
    monkeypatch.setattr("XR7.agents.two_agent_orchestrator_graph.run_recovery_execution_agent", _recovery)
    monkeypatch.setattr("XR7.agents.two_agent_orchestrator_graph.SessionLocal", TestSession)

    asyncio.run(run_two_agent_orchestrator("artist-5", "run-5"))

    db = TestSession()
    try:
        row = db.query(AgentHandoffRecord).filter(AgentHandoffRecord.handoff_id == "handoff-fixed-1").first()
        assert row is not None
        assert row.artist_id == "artist-5"
        listed = list_handoffs_for_artist("artist-5")
        assert listed
        assert listed[0]["handoff_id"] == "handoff-fixed-1"
    finally:
        db.close()
