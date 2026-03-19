from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import and_

from XR7.agents.onboarding_preparation_graph import run_onboarding_preparation_agent
from XR7.agents.recovery_execution_graph import run_recovery_execution_agent
from XR7.agents.two_agent_state import TwoAgentState, add_trace_event, bootstrap_state
from XR7.models.agent_handoff import AgentHandoffRecord
from XR7.models.artist import Artist, ArtistLifecycleStatus
from XR7.models.base import SessionLocal
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# Runtime stores for dashboard status and trace replay.
_RUN_STATE: dict[str, TwoAgentState] = {}
_RUN_TRACE: dict[str, list[dict[str, Any]]] = {}
_ARTIST_LATEST_RUN: dict[str, str] = {}


def _persist_handoff(run_id: str, state: TwoAgentState) -> None:
    handoff = dict(state.get("handoff") or {})
    handoff_id = str(handoff.get("handoff_id") or "")
    if not handoff_id:
        return

    db = SessionLocal()
    try:
        existing = db.query(AgentHandoffRecord).filter(AgentHandoffRecord.handoff_id == handoff_id).first()
        if existing:
            return
        row = AgentHandoffRecord(
            run_id=run_id,
            artist_id=str(state.get("artist_id") or ""),
            handoff_id=handoff_id,
            from_agent=str(handoff.get("from_agent") or "onboarding_preparation"),
            to_agent=str(handoff.get("to_agent") or "recovery_execution"),
            readiness_score=float(handoff.get("readiness_score") or 0.0),
            readiness_threshold=float(handoff.get("readiness_threshold") or 85.0),
            payload=handoff,
        )
        db.add(row)
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()
        logger.exception("Failed to persist two-agent handoff", extra={"run_id": run_id, "handoff_id": handoff_id})
    finally:
        db.close()


def _derive_artist_status_from_db(artist_id: str) -> str:
    db = SessionLocal()
    try:
        artist = db.query(Artist).filter(Artist.id == artist_id).first()
        if not artist:
            return "preparing"
        status = str(artist.status or "").upper()
        if status == ArtistLifecycleStatus.ACTIVE.value:
            return "active"
        if status == ArtistLifecycleStatus.ONBOARDED.value:
            return "ready"
        return "preparing"
    finally:
        db.close()


def _merge(base: TwoAgentState, patch: dict[str, Any]) -> TwoAgentState:
    merged: TwoAgentState = dict(base)
    for key, value in patch.items():
        if isinstance(value, list) and key in {
            "anomalies",
            "claims",
            "evidence_hashes",
            "error_log",
            "agent_activity",
            "trace",
            "handoff_history",
            "negotiation_history",
        }:
            merged[key] = list(merged.get(key) or []) + list(value)
        elif isinstance(value, dict) and key in {
            "confidence_scores",
            "handoff",
            "prepared_state",
            "recovery_execution_state",
            "catalog_profile",
            "public_profile",
            "contract_terms",
            "onboarding_progress",
        }:
            merged[key] = {**(merged.get(key) or {}), **value}
        else:
            merged[key] = value
    return merged


def _route(state: TwoAgentState) -> str:
    artist_status = str(state.get("artist_status") or "preparing").lower()
    if artist_status in {"ready", "active"}:
        return "recovery_execution"
    return "onboarding_preparation"


async def run_two_agent_orchestrator(
    artist_id: str,
    run_id: str | None = None,
    *,
    readiness_threshold: float = 85.0,
) -> TwoAgentState:
    rid = run_id or str(uuid4())
    state = bootstrap_state(artist_id, rid, readiness_threshold=readiness_threshold)
    state["artist_status"] = _derive_artist_status_from_db(artist_id)

    _RUN_STATE[rid] = state
    _ARTIST_LATEST_RUN[artist_id] = rid
    _RUN_TRACE[rid] = []

    route = _route(state)
    state = _merge(
        state,
        {
            "orchestrator_decision": f"route={route}",
            **add_trace_event(
                state,
                node="two_agent_orchestrator",
                event="route",
                payload={"artist_status": state.get("artist_status"), "route": route},
            ),
        },
    )

    if route == "onboarding_preparation":
        state = await run_onboarding_preparation_agent(state)
        if str(state.get("artist_status") or "preparing") in {"ready", "active"}:
            state = await run_recovery_execution_agent(state)
    else:
        state = await run_recovery_execution_agent(state)

    state = _merge(
        state,
        add_trace_event(
            state,
            node="two_agent_orchestrator",
            event="complete",
            payload={"artist_status": state.get("artist_status"), "active_agent": state.get("active_agent")},
        ),
    )

    _RUN_STATE[rid] = state
    _RUN_TRACE[rid] = list(state.get("trace") or [])
    _persist_handoff(rid, state)
    return state


def run_two_agent_orchestrator_sync(
    artist_id: str,
    run_id: str | None = None,
    *,
    readiness_threshold: float = 85.0,
) -> TwoAgentState:
    return asyncio.run(run_two_agent_orchestrator(artist_id, run_id, readiness_threshold=readiness_threshold))


def get_latest_artist_state(artist_id: str) -> TwoAgentState | None:
    run_id = _ARTIST_LATEST_RUN.get(artist_id)
    if not run_id:
        return None
    return _RUN_STATE.get(run_id)


def get_run_trace(artist_id: str, run_id: str) -> dict[str, Any]:
    state = _RUN_STATE.get(run_id)
    if not state or str(state.get("artist_id")) != artist_id:
        return {
            "artist_id": artist_id,
            "run_id": run_id,
            "found": False,
            "events": [],
        }
    return {
        "artist_id": artist_id,
        "run_id": run_id,
        "found": True,
        "events": _RUN_TRACE.get(run_id, []),
        "current_step": state.get("current_step"),
        "confidence_scores": state.get("confidence_scores", {}),
        "active_agent": state.get("active_agent"),
        "artist_status": state.get("artist_status"),
    }


def get_run_state_by_id(run_id: str) -> TwoAgentState | None:
    return _RUN_STATE.get(run_id)


def _serialize_handoff(row: AgentHandoffRecord) -> dict[str, Any]:
    payload = row.payload or {}
    return {
        "id": row.id,
        "run_id": row.run_id,
        "artist_id": row.artist_id,
        "handoff_id": row.handoff_id,
        "from_agent": row.from_agent,
        "to_agent": row.to_agent,
        "readiness_score": row.readiness_score,
        "readiness_threshold": row.readiness_threshold,
        "status": str(payload.get("artist_status") or payload.get("workflow_phase") or row.to_agent),
        "payload": payload,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


def query_handoffs(
    *,
    artist_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    from_agent: str | None = None,
    to_agent: str | None = None,
    status: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> dict[str, Any]:
    db = SessionLocal()
    try:
        query = db.query(AgentHandoffRecord)
        filters = []
        if artist_id:
            filters.append(AgentHandoffRecord.artist_id == artist_id)
        if from_agent:
            filters.append(AgentHandoffRecord.from_agent == from_agent)
        if to_agent:
            filters.append(AgentHandoffRecord.to_agent == to_agent)
        if since:
            filters.append(AgentHandoffRecord.created_at >= since)
        if until:
            filters.append(AgentHandoffRecord.created_at <= until)
        if filters:
            query = query.filter(and_(*filters))

        rows = query.order_by(AgentHandoffRecord.created_at.desc()).all()
        items = [_serialize_handoff(row) for row in rows]
        if status:
            desired_status = status.strip().lower()
            items = [item for item in items if str(item.get("status") or "").lower() == desired_status]

        total = len(items)
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": items[offset: offset + limit],
        }
    finally:
        db.close()


def list_handoffs_for_artist(
    artist_id: str,
    *,
    limit: int = 50,
    offset: int = 0,
    from_agent: str | None = None,
    to_agent: str | None = None,
    status: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> list[dict[str, Any]]:
    return query_handoffs(
        artist_id=artist_id,
        limit=limit,
        offset=offset,
        from_agent=from_agent,
        to_agent=to_agent,
        status=status,
        since=since,
        until=until,
    )["items"]


def list_latest_runs(limit: int = 100) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for artist_id, run_id in list(_ARTIST_LATEST_RUN.items())[:limit]:
        state = _RUN_STATE.get(run_id) or {}
        rows.append(
            {
                "artist_id": artist_id,
                "run_id": run_id,
                "active_agent": state.get("active_agent"),
                "artist_status": state.get("artist_status"),
                "current_step": state.get("current_step"),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    return rows
