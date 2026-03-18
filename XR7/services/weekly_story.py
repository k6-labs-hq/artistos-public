"""Pillar 6 — Weekly Earnings Story generator + message feed writer."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.artist_message import ArtistMessage, MessageCategory
from xr7_common.logging import get_logger

logger = get_logger(__name__)


def generate_weekly_story(
    db: Session,
    artist_id: str,
    *,
    total_recovered: float,
    total_recoverable: float,
    new_anomalies: int,
    claims_progressed: int,
    deposits: list[dict[str, Any]],
    currency: str = "USD",
) -> ArtistMessage:
    """Generate a plain-language weekly earnings story and persist it."""
    deposit_lines: list[str] = []
    for dep in deposits[:3]:
        amt = dep.get("amount", 0.0)
        payer = dep.get("payer", "a payer")
        deposit_lines.append(f"• ${amt:,.2f} from {payer}")

    deposit_section = (
        "Your recent deposits:\n" + "\n".join(deposit_lines)
        if deposit_lines
        else "No new deposits this week."
    )

    body = (
        f"Here is your XR7 weekly recovery summary.\n\n"
        f"📈 Total recovered to date: ${total_recovered:,.2f} {currency}\n"
        f"🔍 Estimated still recoverable: ${total_recoverable:,.2f} {currency}\n"
        f"🚨 New anomalies detected this week: {new_anomalies}\n"
        f"⚖️ Claims that progressed this week: {claims_progressed}\n\n"
        f"{deposit_section}\n\n"
        f"XR7 is working autonomously on your behalf — no action needed unless "
        f"a formal approval is required."
    )

    message = ArtistMessage(
        artist_id=artist_id,
        category=MessageCategory.WEEKLY_STORY,
        subject="Your XR7 Weekly Recovery Story",
        body=body,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    logger.info("weekly_story_generated", extra={"artist_id": artist_id})
    return message


def push_message(
    db: Session,
    artist_id: str,
    *,
    body: str,
    category: MessageCategory = MessageCategory.SYSTEM,
    subject: str | None = None,
) -> ArtistMessage:
    """Push any message onto the artist's feed."""
    message = ArtistMessage(
        artist_id=artist_id,
        category=category,
        subject=subject,
        body=body,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_message_feed(
    db: Session,
    artist_id: str,
    *,
    limit: int = 50,
    unread_only: bool = False,
) -> list[dict[str, Any]]:
    query = db.query(ArtistMessage).filter(ArtistMessage.artist_id == artist_id)
    if unread_only:
        query = query.filter(ArtistMessage.is_read.is_(False))
    rows = query.order_by(ArtistMessage.created_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "category": r.category,
            "subject": r.subject,
            "body": r.body,
            "is_read": r.is_read,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
