from __future__ import annotations

import asyncio
import uuid

from fastapi.testclient import TestClient

from XR7.agents import orchestrator
from XR7.agents.onboarding_agents import ArtistIntentInterpreterAgent, ReflectionNode
from XR7.agents.state import initial_state
from XR7.api.app import app
from XR7.models.artist import Artist
from tests.conftest import TestSession


def _create_artist() -> str:
    db = TestSession()
    try:
        artist = Artist(id=str(uuid.uuid4()), name="Orchestra Test Artist", email="orch@example.com")
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


def test_dashboard_exposes_orchestra_fields(monkeypatch):
    artist_id = _create_artist()
    sample_state = {
        "artist_id": artist_id,
        "run_id": "run-123",
        "current_step": "first_claim_fast_track",
        "confidence_scores": {"first_claim_fast_track": 0.93},
        "onboarding_progress": {"steps_total": 10, "steps_completed": 9, "missing": ["splits"]},
        "comfort_messages": ["XR7 is handling setup while you stay focused on music."],
        "portal_guidance": [{"provider": "ASCAP", "portal_url": "https://member.ascap.com"}],
        "fast_track_claim": {"claim_id": "c-1", "estimated_recoverable": 3200.0},
        "expected_earnings": {"quarterly_expected": 12000.0},
        "public_profile": {"followers": {"spotify": 1000}},
        "readiness_score": 88.0,
        "ugc_opportunities": [{"platform": "tiktok", "estimated_recoverable": 500.0}],
        "catalog_profile": {"work_count": 4},
        "split_conflicts": [],
        "registration_actions": [],
        "follow_up_actions": [],
        "agent_activity": [{"step": "first_claim_fast_track", "status": "completed"}],
    }
    monkeypatch.setattr("XR7.api.routers.dashboard.get_latest_artist_state", lambda aid: sample_state if aid == artist_id else None)

    client = TestClient(app)
    response = client.get(f"/artists/{artist_id}/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert payload["agent_orchestra_status"]["current_step"] == "first_claim_fast_track"
    assert payload["agent_orchestra_status"]["trace_url"] == f"/artists/{artist_id}/agent-trace/run-123"
    assert payload["onboarding_progress"]["steps_completed"] == 9
    assert payload["expected_earnings"]["quarterly_expected"] == 12000.0


def test_supervisor_routing_prefers_onboarding_then_recovery():
    state = initial_state("artist-1", "run-1")
    nxt = orchestrator._supervisor_next(state)
    assert nxt == "artist_intent_interpreter"

    state["onboarding_progress"] = {"completed": True}
    nxt2 = orchestrator._supervisor_next(state)
    assert nxt2 == "detection_agent"


def test_artist_intent_interpreter_requests_clarification_for_unclear_message():
    state = initial_state("artist-2")
    state["persona_profile"] = {"last_message": "help", "last_ui_action": ""}
    result = asyncio.run(ArtistIntentInterpreterAgent(state))
    assert result["artist_intent"] == "clarify"
    assert "dashboard_prompt" in result


def test_reflection_node_sets_retry_or_proceed():
    state = initial_state("artist-3")
    state["pending_agent"] = "smart_upload_fixer"
    state["confidence_scores"] = {"smart_upload_fixer": 0.8}
    out = asyncio.run(ReflectionNode(state))
    assert out["reflection_score"] >= 0.0
    assert out["next_action"] in {
        "proceed",
        "retry_previous_node",
        "escalate_to_human",
        "escalate_to_escalation_agent",
    }


def test_orchestrator_trace_endpoint_unknown_run_returns_not_found_shape():
    client = TestClient(app)
    response = client.get("/artists/artist-x/agent-trace/run-x")
    assert response.status_code == 200
    payload = response.json()
    assert payload["found"] is False
    assert payload["events"] == []


def test_fallback_execute_retries_pending_agent_when_reflection_requests_retry(monkeypatch):
    calls: list[str] = []

    async def _pending(state):
        calls.append("pending")
        return {
            "current_step": "smart_upload_fixer",
            "confidence_scores": {"smart_upload_fixer": 0.5},
            "next_action": "reflection",
            "pending_agent": "smart_upload_fixer",
        }

    async def _reflection(state):
        calls.append("reflection")
        return {
            "current_step": "reflection",
            "next_action": "retry_previous_node",
            "pending_agent": "smart_upload_fixer",
            "confidence_scores": {"reflection": 0.95},
        }

    monkeypatch.setattr(orchestrator, "AGENTS", {"smart_upload_fixer": _pending, "reflection": _reflection})
    monkeypatch.setattr(orchestrator, "RECOVERY_ORDER", ["smart_upload_fixer"])
    monkeypatch.setattr(orchestrator, "REFLECTION_AFTER", set())

    state = initial_state("artist-retry", "run-retry")
    state["onboarding_progress"] = {"completed": True}

    result = asyncio.run(orchestrator._fallback_execute(state))
    assert calls[:3] == ["pending", "reflection", "pending"]
    assert result["current_step"] == "smart_upload_fixer"


def test_fallback_execute_stops_on_reflection_human_review(monkeypatch):
    async def _pending(state):
        return {
            "current_step": "smart_upload_fixer",
            "next_action": "reflection",
            "pending_agent": "smart_upload_fixer",
            "confidence_scores": {"smart_upload_fixer": 0.4},
        }

    async def _reflection(state):
        return {
            "current_step": "reflection",
            "next_action": "human_review",
            "pending_agent": "smart_upload_fixer",
            "confidence_scores": {"reflection": 0.7},
        }

    monkeypatch.setattr(orchestrator, "AGENTS", {"smart_upload_fixer": _pending, "reflection": _reflection})
    monkeypatch.setattr(orchestrator, "RECOVERY_ORDER", ["smart_upload_fixer"])
    monkeypatch.setattr(orchestrator, "REFLECTION_AFTER", set())

    state = initial_state("artist-escalate", "run-escalate")
    state["onboarding_progress"] = {"completed": True}
    result = asyncio.run(orchestrator._fallback_execute(state))
    assert result["next_action"] == "human_review"


def test_run_xr7_recovery_orchestra_falls_back_when_graph_throws(monkeypatch):
    class _BrokenGraph:
        async def astream_events(self, state, config=None, version="v2"):
            raise RuntimeError("boom")
            yield  # pragma: no cover

    async def _fake_fallback(state):
        return {**state, "current_step": "fallback_done", "confidence_scores": {"fallback": 1.0}}

    monkeypatch.setattr(orchestrator, "xr7_recovery_orchestra", _BrokenGraph())
    monkeypatch.setattr(orchestrator, "_fallback_execute", _fake_fallback)

    out = asyncio.run(orchestrator.run_xr7_recovery_orchestra("artist-fallback", "run-fallback"))
    assert out["current_step"] == "fallback_done"
    assert orchestrator.get_latest_artist_state("artist-fallback") is not None
