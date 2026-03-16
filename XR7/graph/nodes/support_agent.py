from __future__ import annotations

from typing import Any


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:  # noqa: BLE001
        return default


def _find_top_payer(dashboard: dict[str, Any]) -> dict[str, Any] | None:
    payers = dashboard.get("payers_owing") or []
    if not isinstance(payers, list) or not payers:
        return None
    sorted_rows = sorted(payers, key=lambda r: _as_float((r or {}).get("recoverable_estimate"), 0.0), reverse=True)
    return sorted_rows[0] if sorted_rows else None


def _build_recommendation(dashboard: dict[str, Any]) -> str:
    deadlines = dashboard.get("deadlines") or {}
    urgent = int(deadlines.get("urgent_count") or 0)
    top_payer = _find_top_payer(dashboard)
    if urgent > 0:
        return "You have urgent SOL deadlines. Prioritize those claims before lower-value disputes."
    if top_payer:
        payer_name = str(top_payer.get("payer_name") or "top payer")
        est = _as_float(top_payer.get("recoverable_estimate"), 0.0)
        return f"Your highest recoverable payer is {payer_name} (${est:,.2f}). Focus there first for fastest impact."
    queue = dashboard.get("priority_actions") or {}
    open_items = int(queue.get("total_open_items") or 0)
    if open_items > 0:
        return f"You have {open_items} open priority actions. Start from the top-ranked item to maximize recoverable value."
    return "Upload the latest statements and run readiness checks so we can identify new recoverable anomalies."


def _term_explanations() -> dict[str, str]:
    return {
        "missing_mechanical": "MISSING_MECHANICAL means the statement indicates usage but no matching mechanical royalty payment was found.",
        "catalog health": "Catalog health is a composite score combining metadata quality, payout regularity, anomaly density, and recovery outcomes.",
        "sol": "SOL is the statute-of-limitations window. Once it expires, legal recovery options may be significantly reduced.",
        "friction": "Friction level estimates negotiation effort and relationship sensitivity with a payer. High friction usually needs tighter evidence and analyst review.",
        "calibration": "Calibration reflects how closely model confidence matches actual claim outcomes. Better calibration means better prioritization confidence.",
        "leakage": "Leakage is recoverable revenue that should have been paid but was not correctly paid based on source data and contract logic.",
    }


async def ArtistSupportAgent(state: dict[str, Any]) -> dict[str, Any]:
    message = str(state.get("support_user_message") or "").strip()
    dashboard = dict(state.get("dashboard_context") or {})
    thread_id = str(state.get("support_thread_id") or "")

    lowered = message.lower()
    explanations = _term_explanations()

    response = "I can help with dashboard questions, anomaly explanations, and safe actions like summaries and readiness checks."
    confidence = 0.8
    quick_replies = [
        "Show my top payers",
        "Explain this anomaly",
        "Generate my weekly digest now",
        "Run catalog readiness check",
    ]

    destructive_markers = ["create claim", "charge", "disburse", "delete", "void", "skip payer", "close claim"]
    if any(token in lowered for token in destructive_markers):
        response = (
            "I can only run safe read-only or low-risk actions in chat. "
            "For destructive actions, please use the dedicated endpoint with explicit confirmation."
        )
        confidence = 0.93
    else:
        matched = False
        for key, text in explanations.items():
            if key in lowered:
                response = text
                confidence = 0.9
                matched = True
                break

        if not matched and ("top payer" in lowered or "show my payers" in lowered or "payer" in lowered):
            top = _find_top_payer(dashboard)
            if top:
                response = (
                    f"Top payer: {top.get('payer_name')} ({top.get('payer_type')}) with "
                    f"${_as_float(top.get('recoverable_estimate'), 0.0):,.2f} estimated recoverable "
                    f"across {int(top.get('claim_count') or 0)} claims."
                )
                confidence = 0.88
            else:
                response = "No payer breakdown is available yet. Upload statements or sync new data to generate payer insights."
                confidence = 0.72
            matched = True

        if not matched and ("missing_mechanical" in lowered or "anomaly" in lowered):
            response = (
                "Anomaly categories represent specific revenue mismatches. For MISSING_MECHANICAL, "
                "we detected missing mechanical payouts for usage that appears in source reporting."
            )
            confidence = 0.86
            matched = True

        if not matched and ("what should i do" in lowered or "next step" in lowered or "should i" in lowered):
            response = _build_recommendation(dashboard)
            confidence = 0.84
            matched = True

        if not matched:
            response = (
                "I can answer this with current dashboard context, but confidence is limited. "
                "If you want, I can escalate this to a human analyst review."
            )
            confidence = 0.68

    needs_human = confidence < 0.75
    support_messages = list(state.get("support_messages") or [])
    support_messages.append(
        {
            "role": "assistant",
            "content": response,
            "confidence": confidence,
            "thread_id": thread_id,
            "needs_human_escalation": needs_human,
        }
    )

    return {
        "current_step": "artist_support",
        "support_messages": support_messages,
        "support_response": response,
        "support_confidence": round(confidence, 4),
        "support_suggested_replies": quick_replies,
        "support_escalation_recommended": needs_human,
        "next_action": "human_review" if needs_human else "proceed",
        "confidence_scores": {**(state.get("confidence_scores") or {}), "artist_support": round(confidence, 4)},
    }
