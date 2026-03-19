"""XR7 Advisor: personalized copilot LLM interface for VIP members.

Provides `ask_xr7_advisor(query, context)` which:
1. Builds a system prompt embedding the artist's catalog + recovery context
2. Calls the LLM (OpenAI / xAI / fallback) with the user's natural-language query
3. Returns (response_text, confidence, sources_cited)

Used by the /artists/{id}/copilot/query endpoint.
"""
from __future__ import annotations

import importlib
import json
import os
from typing import Any

from xr7_common.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Optional LangChain imports
# ---------------------------------------------------------------------------

try:
    _lc_messages = importlib.import_module("langchain_core.messages")
    HumanMessage = getattr(_lc_messages, "HumanMessage")
    SystemMessage = getattr(_lc_messages, "SystemMessage")
except Exception:
    HumanMessage = None
    SystemMessage = None

try:
    _lc_openai = importlib.import_module("langchain_openai")
    ChatOpenAI = getattr(_lc_openai, "ChatOpenAI")
except Exception:
    ChatOpenAI = None

try:
    _lc_xai = importlib.import_module("langchain_xai")
    ChatXAI = getattr(_lc_xai, "ChatXAI")
except Exception:
    ChatXAI = None

# ---------------------------------------------------------------------------
# System prompt template
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT_TEMPLATE = """\
You are the XR7 Advisor — a concierge-grade, deeply personalized AI strategist \
for elite music and TV/Film rights professionals.

You have full context about this artist:
{context_json}

Your role:
• Answer questions about their catalog, earnings, recovery claims, and strategies \
with precision and care.
• Identify leakage patterns, negotiation leverage, and proactive recovery actions.
• Reference real data points from the context when available — never hallucinate specifics.
• Speak in a concise, high-trust, professional tone suited to top-tier creators.
• For complex legal or financial decisions, recommend they consult their assigned analyst.

Today's date: {today}
"""


def _build_system_prompt(context: dict[str, Any]) -> str:
    from datetime import date

    context_json = json.dumps(context, indent=2, default=str)
    return _SYSTEM_PROMPT_TEMPLATE.format(
        context_json=context_json,
        today=date.today().isoformat(),
    )


def _get_llm() -> Any:
    """Return the best available LLM client, in priority order."""
    xai_key = os.getenv("XAI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if xai_key and ChatXAI is not None:
        try:
            return ChatXAI(api_key=xai_key, model="grok-3", temperature=0.3)
        except Exception:
            logger.warning("Failed to init ChatXAI, falling back to OpenAI")

    if openai_key and ChatOpenAI is not None:
        try:
            return ChatOpenAI(api_key=openai_key, model="gpt-4o", temperature=0.3)
        except Exception:
            logger.warning("Failed to init ChatOpenAI")

    return None


def ask_xr7_advisor(
    query: str,
    context: dict[str, Any],
) -> tuple[str, float, list[str]]:
    """
    Main entry point for the XR7 Advisor copilot.

    Returns:
        (response_text, confidence_score, sources_cited)
    """
    llm = _get_llm()
    if llm is None or HumanMessage is None or SystemMessage is None:
        # No LLM available — return a structured fallback
        return _fallback_response(query, context)

    system_prompt = _build_system_prompt(context)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query),
    ]

    try:
        response = llm.invoke(messages)
        response_text = getattr(response, "content", str(response)).strip()
        # Derive a confidence proxy from response length and context richness
        ctx_fields = sum(1 for v in context.values() if v)
        confidence = min(0.95, 0.60 + ctx_fields * 0.04)
        sources = _extract_sources(context)
        return response_text, round(confidence, 2), sources
    except Exception as exc:
        logger.warning("XR7 Advisor LLM call failed, using fallback", exc_info=exc)
        return _fallback_response(query, context)


def _fallback_response(query: str, context: dict[str, Any]) -> tuple[str, float, list[str]]:
    """Structured, context-aware fallback when no LLM is available."""
    artist_name = context.get("artist_name", "")
    open_claims = context.get("open_claims", 0)
    roles = context.get("detected_roles") or []
    vertical = context.get("primary_vertical", "music")
    notable_works = context.get("notable_works") or []

    parts = []
    if artist_name:
        parts.append(f"Based on your XR7 profile, {artist_name}:")
    if open_claims:
        parts.append(
            f"• You have {open_claims} active recovery claim(s). "
            "Prioritise reviewing these in your Recovery Story timeline."
        )
    if roles:
        parts.append(f"• Your detected roles: {', '.join(roles)}.")
    if vertical == "tv_film":
        parts.append(
            "• As a TV/Film creator, ensure your residuals statements are uploaded "
            "and your guild registrations are current."
        )
    if notable_works:
        parts.append(
            f"• Notable works in your catalog include: {', '.join(str(w) for w in notable_works[:3])}."
        )
    parts.append(
        "For detailed answers, schedule your monthly strategy call via your Concierge Inbox."
    )

    return " ".join(parts), 0.70, _extract_sources(context)


def _extract_sources(context: dict[str, Any]) -> list[str]:
    sources = []
    if context.get("open_claims") is not None:
        sources.append("XR7 recovery ledger")
    if context.get("detected_roles"):
        sources.append("persona enrichment")
    if context.get("notable_works"):
        sources.append("catalog graph")
    if context.get("bio_snippet"):
        sources.append("public profile data")
    return sources
