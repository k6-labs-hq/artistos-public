from __future__ import annotations

from typing import Any


DEFAULT_CHANNELS = {
    "spotify": ["portal", "email"],
    "distrokid": ["email"],
    "tunecore": ["portal", "email"],
    "ascap": ["portal", "email"],
    "bmi": ["portal", "email"],
    "generic": ["email", "pdf_fallback"],
}


def deliver_dispute(claim: dict[str, Any], payer_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Route dispute delivery through payer-specific channels with fallback semantics."""
    channels = DEFAULT_CHANNELS.get(str(payer_id).lower(), DEFAULT_CHANNELS["generic"])
    results = []
    for channel in channels:
        results.append({"channel": channel, "status": "sent" if channel != "api" else "queued", "detail": "simulated"})

    return {
        "claim_id": claim.get("id"),
        "payer_id": payer_id,
        "channels_attempted": channels,
        "delivery_results": results,
        "fallback_used": "pdf_fallback" in channels,
        "payload": payload or {},
    }
