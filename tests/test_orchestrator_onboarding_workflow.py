from __future__ import annotations

import asyncio
import uuid

from fastapi.testclient import TestClient

from XR7.agents import orchestrator
from XR7.agents.two_agent_orchestrator_graph import get_run_trace
from XR7.api.app import app
from XR7.models.agent_handoff import AgentHandoffRecord
from XR7.models.artist import Artist
from tests.conftest import TestSession


def _create_artist(status: str = "NEW") -> str:
    db = TestSession()
    try:
        artist = Artist(
            id=str(uuid.uuid4()),
            name="Orchestra Test Artist",
            email="orch@example.com",
            status=status,
        )
        db.add(artist)
        db.commit()
        return artist.id
    finally:
        db.close()


def test_workflow_endpoint_queues_autonomous_run(monkeypatch):
    artist_id = _create_artist()
    queued: list[tuple[str, str]] = []

    class _DelayProxy:
        def delay(self, aid: str, rid: str):
            queued.append((aid, rid))

    monkeypatch.setattr("XR7.api.routers.workflow.run_artist_workflow", _DelayProxy())

    client = TestClient(app)
    response = client.post(f"/artists/{artist_id}/workflow/run-full-autonomous")
    assert response.status_code == 200
    payload = response.json()
    assert payload["artist_id"] == artist_id
    assert payload["status"] == "queued"
    assert payload["run_id"]
    assert payload["status_url"].endswith(payload["run_id"])
    assert len(queued) == 1
    assert queued[0][0] == artist_id


def test_supervisor_routes_by_artist_status():
    assert orchestrator._supervisor_next({"artist_status": "preparing"}) == "onboarding_preparation"
    assert orchestrator._supervisor_next({"artist_status": "ready"}) == "recovery_execution"
    assert orchestrator._supervisor_next({"artist_status": "active"}) == "recovery_execution"


def test_two_agent_trace_unknown_run_shape():
    out = get_run_trace("artist-x", "run-x")
    assert out["found"] is False
    assert out["events"] == []


def test_run_orchestrator_for_preparing_artist_transitions_to_agent_execution(monkeypatch):
    artist_id = _create_artist(status="NEW")

    async def _prep(state):
        return {**state, "artist_status": "ready", "active_agent": "onboarding_preparation"}

    async def _recovery(state):
        return {**state, "artist_status": "active", "active_agent": "recovery_execution", "workflow_phase": "recovery_execution"}

    monkeypatch.setattr("XR7.agents.two_agent_orchestrator_graph.run_onboarding_preparation_agent", _prep)
    monkeypatch.setattr("XR7.agents.two_agent_orchestrator_graph.run_recovery_execution_agent", _recovery)

    out = asyncio.run(orchestrator.run_xr7_recovery_orchestra(artist_id, "run-prep"))
    assert out["artist_id"] == artist_id
    assert out["active_agent"] in {"onboarding_preparation", "recovery_execution"}
    assert out["workflow_phase"] in {"onboarding_preparation", "recovery_execution"}


def test_run_export_pipeline_forces_recovery_execution_path(monkeypatch):
    artist_id = _create_artist(status="ONBOARDED")

    async def _recovery(state):
        return {**state, "artist_status": "active", "active_agent": "recovery_execution"}

    monkeypatch.setattr("XR7.agents.orchestrator.run_recovery_execution_agent", _recovery)

    out = asyncio.run(orchestrator.run_export_prep_pipeline(artist_id, "run-export"))
    assert out["artist_status"] in {"ready", "active"}
    assert out["active_agent"] == "recovery_execution"


def test_run_tvfilm_vertical_orchestra_sets_tvfilm_mode(monkeypatch):
    artist_id = _create_artist(status="ACTIVE")

    async def _recovery(state):
        return {**state, "artist_status": "active", "active_agent": "recovery_execution", "tvfilm_mode": True}

    monkeypatch.setattr("XR7.agents.orchestrator.run_recovery_execution_agent", _recovery)

    out = asyncio.run(orchestrator.run_tvfilm_vertical_orchestra(artist_id, "run-tvfilm"))
    assert out["artist_status"] == "active"
    assert out.get("tvfilm_mode") is True


def test_support_agent_turn_sync_returns_message_shape():
    artist_id = _create_artist(status="ACTIVE")
    out = orchestrator.run_support_agent_turn_sync(
        artist_id,
        message="What should I do next?",
        thread_id="thread-1",
        dashboard_context={"deadlines": {"urgent_count": 1}},
    )
    assert out["current_step"] == "artist_support"
    assert isinstance(out.get("support_response") or "", str)


def test_workflow_handoffs_endpoint_returns_records(monkeypatch):
    artist_id = _create_artist(status="ACTIVE")
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        "XR7.api.routers.workflow.query_handoffs",
        lambda **kwargs: captured.update(kwargs) or {
            "total": 1,
            "items": [
                {
                    "id": "row-1",
                    "run_id": "run-handoff-1",
                    "artist_id": kwargs["artist_id"],
                    "handoff_id": "handoff-endpoint-1",
                    "from_agent": "onboarding_preparation",
                    "to_agent": "recovery_execution",
                    "readiness_score": 91.0,
                    "readiness_threshold": 85.0,
                    "status": "active",
                    "payload": {"artist_id": kwargs["artist_id"], "handoff_id": "handoff-endpoint-1"},
                    "created_at": None,
                }
            ] if kwargs["artist_id"] == artist_id else [],
        },
    )

    client = TestClient(app)
    response = client.get(
        f"/artists/{artist_id}/workflow/handoffs?limit=5&offset=10&status=active&from_agent=onboarding_preparation"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["artist_id"] == artist_id
    assert payload["total"] == 1
    assert payload["limit"] == 5
    assert payload["offset"] == 10
    assert payload["handoffs"][0]["handoff_id"] == "handoff-endpoint-1"
    assert captured == {
        "artist_id": artist_id,
        "limit": 5,
        "offset": 10,
        "from_agent": "onboarding_preparation",
        "to_agent": None,
        "status": "active",
        "since": None,
        "until": None,
    }


def test_dashboard_exposes_handoff_status(monkeypatch):
    artist_id = _create_artist(status="ACTIVE")
    sample_state = {
        "artist_id": artist_id,
        "run_id": "run-123",
        "current_step": "recovery_execution",
        "confidence_scores": {"recovery_execution": 0.93},
        "onboarding_progress": {"steps_total": 10, "steps_completed": 10, "missing": []},
        "comfort_messages": [],
        "portal_guidance": [],
        "fast_track_claim": None,
        "expected_earnings": {},
        "public_profile": {},
        "readiness_score": 91.0,
        "ugc_opportunities": [],
        "catalog_profile": {},
        "split_conflicts": [],
        "registration_actions": [],
        "follow_up_actions": [],
        "agent_activity": [],
    }
    monkeypatch.setattr("XR7.api.routers.dashboard.get_latest_artist_state", lambda aid: sample_state if aid == artist_id else None)
    monkeypatch.setattr(
        "XR7.api.routers.dashboard.list_handoffs_for_artist",
        lambda aid, limit=1: [{"handoff_id": "handoff-dashboard-1", "artist_id": artist_id}] if aid == artist_id else [],
    )

    client = TestClient(app)
    response = client.get(f"/artists/{artist_id}/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert payload["agent_handoff_status"]["latest_handoff"]["handoff_id"] == "handoff-dashboard-1"
    assert payload["agent_handoff_status"]["handoff_history_url"].endswith("/workflow/handoffs")


def test_admin_handoffs_endpoint_returns_paginated_results(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "admin-secret")
    artist_id = _create_artist(status="ACTIVE")
    monkeypatch.setattr(
        "XR7.api.routers.admin_console.query_handoffs",
        lambda **kwargs: {
            "total": 1,
            "limit": kwargs["limit"],
            "offset": kwargs["offset"],
            "items": [
                {
                    "id": "row-admin-1",
                    "run_id": "run-admin-1",
                    "artist_id": artist_id,
                    "handoff_id": "handoff-admin-1",
                    "from_agent": "onboarding_preparation",
                    "to_agent": "recovery_execution",
                    "readiness_score": 88.0,
                    "readiness_threshold": 85.0,
                    "status": "active",
                    "payload": {"artist_status": "active"},
                    "created_at": None,
                }
            ],
        },
    )

    client = TestClient(app)
    response = client.get(
        f"/admin/workflow/handoffs?artist_id={artist_id}&status=active&limit=10&offset=0",
        headers={"X-Admin-Key": "admin-secret", "X-Admin-Actor": "ops-user@xr7.test"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["limit"] == 10
    assert payload["offset"] == 0
    assert payload["items"][0]["handoff_id"] == "handoff-admin-1"
    assert payload["items"][0]["artist_id"] == artist_id
