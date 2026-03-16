from __future__ import annotations

from typing import Any


def register_push_token(artist_id: str, token: str, platform: str) -> dict[str, Any]:
    return {"artist_id": artist_id, "token": token, "platform": platform, "registered": True}


def voice_balance_query(artist_id: str, question: str, dashboard_payload: dict[str, Any]) -> dict[str, Any]:
    balance = (dashboard_payload.get("balance_still_pursuing") or {}).get("balance_still_pursuing")
    response = f"Current balance still pursuing is ${float(balance or 0.0):,.2f}."
    return {"artist_id": artist_id, "question": question, "response": response}
