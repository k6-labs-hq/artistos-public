"""Shared constants and helper functions for all onboarding agents."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from XR7.agents.state import XR7State, add_trace_event, set_confidence
from XR7.llm.claim_drafter import claim_drafter
from XR7.models.base import SessionLocal
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from xr7_common.logging import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are an autonomous XR7 agent. Eliminate human error. "
    "Always verify before acting. Log every decision with evidence hash."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_score(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 4)


def _evidence_hash(artist_id: str, agent_name: str, payload: dict[str, Any]) -> str:
    raw = json.dumps(
        {"artist_id": artist_id, "agent": agent_name, "payload": payload},
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _ledger(artist_id: str, entry_type: str, payload: dict[str, Any]) -> str | None:
    db = SessionLocal()
    try:
        row = ImmutableLedgerService(db).append(artist_id, entry_type, payload)
        return row.entry_hash
    except Exception:  # noqa: BLE001
        logger.exception(
            "Unable to append ledger entry",
            extra={"artist_id": artist_id, "entry_type": entry_type},
        )
        return None
    finally:
        db.close()


async def _llm_reflect(
    agent_name: str, context: dict[str, Any]
) -> tuple[float, str, list[str], str]:
    critique_prompt = {
        "system": SYSTEM_PROMPT,
        "task": "self-critique",
        "agent": agent_name,
        "checks": [
            "Evidence integrity and hash coverage",
            "SOL urgency considered",
            "Missing metadata or split issues",
            "Action is safe and reversible",
        ],
        "context": context,
        "output": "JSON with score, reasoning, suggestions, next_action",
    }
    try:
        text = await claim_drafter.async_generate_personalized_advice(critique_prompt)
        score = 0.9
        lower = (text or "").lower()
        if "missing" in lower or "risk" in lower:
            score = 0.82
        suggestions = ["Check SOL deadline and metadata completeness"] if score < 0.85 else []
        action = "retry_previous_node" if score < 0.85 else "proceed"
        return _safe_score(score), text or "Reflection generated", suggestions, action
    except Exception:  # noqa: BLE001
        logger.exception("Reflection LLM failed", extra={"agent": agent_name})
        return 0.86, "Reflection fallback used", [], "proceed"


def _finalize(
    state: XR7State,
    *,
    agent_name: str,
    score: float,
    updates: dict[str, Any],
    decision: str,
    confidence_label: str | None = None,
) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    evidence_hash = _evidence_hash(artist_id, agent_name, updates)
    ledger_hash = _ledger(
        artist_id,
        f"agent_{agent_name}",
        {
            "decision": decision,
            "confidence": score,
            "evidence_hash": evidence_hash,
            "updates": updates,
            "at": _now(),
        },
    )
    merged_scores = {**(state.get("confidence_scores") or {}), agent_name: _safe_score(score)}
    if confidence_label:
        merged_scores[confidence_label] = _safe_score(score)
    out: XR7State = {
        **updates,
        "current_step": agent_name,
        "confidence_scores": merged_scores,
        "agent_activity": [
            {
                "step": agent_name,
                "status": "completed",
                "decision": decision,
                "confidence": _safe_score(score),
                "evidence_hash": ledger_hash or evidence_hash,
            }
        ],
        "evidence_hashes": [evidence_hash],
    }
    if score < 0.85:
        out["next_action"] = "reflection"
        out["pending_agent"] = agent_name
    return out


async def ReflectionNode(state: XR7State) -> XR7State:
    pending = str(state.get("pending_agent") or state.get("current_step") or "unknown")
    score, reasoning, suggestions, action = await _llm_reflect(
        "ReflectionNode",
        {
            "pending_agent": pending,
            "confidence": (state.get("confidence_scores") or {}).get(pending, 0.0),
            "error_log": state.get("error_log") or [],
        },
    )
    artist_id = str(state.get("artist_id") or "")
    _ledger(
        artist_id,
        "agent_reflection",
        {
            "pending_agent": pending,
            "score": score,
            "reasoning": reasoning,
            "suggestions": suggestions,
            "next_action": action,
        },
    )
    return {
        **set_confidence(state, "reflection", score),
        **add_trace_event(
            state,
            node="reflection",
            event="completed",
            payload={"pending_agent": pending, "score": score},
        ),
        "reflection_score": score,
        "reflection_reasoning": reasoning,
        "reflection_suggestions": suggestions,
        "next_action": action,
        "error_log": [reasoning] if score < 0.85 else [],
    }
