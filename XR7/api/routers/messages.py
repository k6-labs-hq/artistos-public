"""Pillar 6 — Natural-language business manager: chat, message feed, weekly story."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.api.routers.auth import require_artist_access
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata
from XR7.services.weekly_story import get_message_feed, push_message, generate_weekly_story
from XR7.models.artist_message import MessageCategory

router = APIRouter(tags=["messages"])


class ChatRequest(BaseModel):
    message: str


class WeeklyStoryRequest(BaseModel):
    total_recovered: float = 0.0
    total_recoverable: float = 0.0
    new_anomalies: int = 0
    claims_progressed: int = 0
    deposits: list[dict] = []
    currency: str = "USD"


@router.get("/artists/{artist_id}/messages/feed")
def get_feed(
    artist_id: str,
    limit: int = 50,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """Return the artist's message feed (onboarding, comfort, claim, SOL, deposit, weekly story)."""
    messages = get_message_feed(db, artist_id, limit=limit, unread_only=unread_only)
    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "count": len(messages),
        "messages": messages,
    })


@router.post("/artists/{artist_id}/messages/chat")
def business_manager_chat(
    artist_id: str,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """Natural-language business manager.

    Accepts a question like "Why was my YouTube lower?" and returns a
    plain-English answer grounded in this artist's anomaly + earnings data.
    """
    q = payload.message.strip().lower()

    # Route to domain-specific answer generators
    if any(k in q for k in ("youtube", "tiktok", "spotify", "apple", "platform", "lower", "why")):
        answer = _explain_platform_variance(db, artist_id, q)
    elif any(k in q for k in ("claim", "recovery", "owed", "missing")):
        answer = _explain_claims(db, artist_id)
    elif any(k in q for k in ("advance", "cash", "liquidity")):
        answer = _explain_advance(db, artist_id)
    elif any(k in q for k in ("rights", "isrc", "iswc", "pro", "registration")):
        answer = _explain_rights(db, artist_id)
    else:
        answer = (
            "XR7 is actively monitoring your royalty streams across all platforms. "
            "Ask me about a specific platform, your claims status, or your recovery forecast "
            "and I'll give you a grounded answer from your live data."
        )

    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "question": payload.message,
        "answer": answer,
    })


@router.post("/artists/{artist_id}/messages/weekly-story")
def create_weekly_story(
    artist_id: str,
    payload: WeeklyStoryRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """Generate and persist a weekly earnings story for the artist."""
    msg = generate_weekly_story(
        db,
        artist_id,
        total_recovered=payload.total_recovered,
        total_recoverable=payload.total_recoverable,
        new_anomalies=payload.new_anomalies,
        claims_progressed=payload.claims_progressed,
        deposits=payload.deposits,
        currency=payload.currency,
    )
    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "message_id": msg.id,
        "story": msg.body,
    })


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _explain_platform_variance(db: Session, artist_id: str, question: str) -> str:
    """Look up open anomalies matching the question and return a plain-English explanation."""
    try:
        from XR7.models.anomaly import Anomaly
        anomalies = (
            db.query(Anomaly)
            .filter(Anomaly.artist_id == artist_id)
            .order_by(Anomaly.created_at.desc())
            .limit(5)
            .all()
        )
        if not anomalies:
            return (
                "XR7 has not yet detected anomalies on this account. "
                "Upload your latest statements to trigger a fresh scan."
            )
        summaries = "; ".join(
            f"{a.subtype} in {a.territory or 'global'} ({a.created_at.date().isoformat() if a.created_at else 'recent'})"
            for a in anomalies
        )
        return (
            f"XR7 detected the following recent issues that may explain lower earnings: "
            f"{summaries}. Each anomaly has a drafted recovery action in your Claims tab."
        )
    except Exception:  # noqa: BLE001
        return "Unable to retrieve anomaly data at this time."


def _explain_claims(db: Session, artist_id: str) -> str:
    try:
        from XR7.models.claim import Claim, ClaimStatus
        open_claims = (
            db.query(Claim)
            .filter(
                Claim.artist_id == artist_id,
                Claim.status.notin_([ClaimStatus.PAID, ClaimStatus.CLOSED]),
            )
            .count()
        )
        return (
            f"You have {open_claims} open recovery claim(s) in progress. "
            "XR7 is autonomously chasing each one. "
            "You will be notified when funds are confirmed or a formal approval is required."
        )
    except Exception:  # noqa: BLE001
        return "Unable to retrieve claims data at this time."


def _explain_advance(db: Session, artist_id: str) -> str:
    return (
        "XR7 can offer you a cash advance based on your predicted recovery earnings. "
        "Visit the Advance tab or POST to /artists/{id}/advance/offer with your forecast to check eligibility."
    )


def _explain_rights(db: Session, artist_id: str) -> str:
    try:
        from XR7.models.rights_scan import RightsScanResult
        count = (
            db.query(RightsScanResult)
            .filter(
                RightsScanResult.artist_id == artist_id,
                RightsScanResult.submission_status == "pending",
            )
            .count()
        )
        if count:
            return (
                f"XR7 found {count} pending rights registration gap(s) in your catalog. "
                "These include missing ISRC, ISWC, or foreign PRO registrations. "
                "Visit the Rights tab to review and submit packets."
            )
        return "No pending rights registration gaps detected in your catalog at this time."
    except Exception:  # noqa: BLE001
        return "Unable to retrieve rights data at this time."
