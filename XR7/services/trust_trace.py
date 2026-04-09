"""Pillar 1 — Trust & Transparency trace writer service."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from XR7.models.trust_trace import TrustTraceEvent
from xr7_common.logging import get_logger

logger = get_logger(__name__)

_STAGE_EXPLANATIONS: dict[str, str] = {
    "ingestion": "XR7 is reading and parsing your uploaded royalty files.",
    "identity": "XR7 is fingerprinting your artist identity across platforms.",
    "anomaly": "XR7 is scanning every revenue line for rate drift and missing payments.",
    "repair": "XR7 is correcting metadata gaps that cause unpaid royalties.",
    "forecast": "XR7 is calculating your predicted and recoverable earnings.",
    "claim": "XR7 is drafting claim packets and filing recovery actions.",
    "rights": "XR7 is checking for missing ISRC/ISWC/PRO registrations.",
    "tax": "XR7 is reviewing withholding rates for over-deduction.",
    "complete": "XR7 has finished your full analysis. Your recovery dashboard is ready.",
}


def write_trace_event(
    db: Session,
    *,
    artist_id: str,
    run_id: str,
    stage: str,
    sub_stage: str | None = None,
    confidence: float | None = None,
    eta_seconds: float | None = None,
    explanation: str | None = None,
) -> TrustTraceEvent:
    """Persist a pipeline trace step for real-time trust feed."""
    plain_explanation = explanation or _STAGE_EXPLANATIONS.get(stage, f"Processing stage: {stage}")
    event = TrustTraceEvent(
        artist_id=artist_id,
        run_id=run_id,
        stage=stage,
        sub_stage=sub_stage,
        confidence=confidence,
        eta_seconds=eta_seconds,
        explanation=plain_explanation,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    logger.info(
        "trust_trace_event",
        extra={
            "artist_id": artist_id,
            "run_id": run_id,
            "stage": stage,
            "sub_stage": sub_stage,
            "confidence": confidence,
        },
    )
    return event


def get_latest_trace(db: Session, artist_id: str, *, limit: int = 20) -> list[dict[str, Any]]:
    rows = (
        db.query(TrustTraceEvent)
        .filter(TrustTraceEvent.artist_id == artist_id)
        .order_by(TrustTraceEvent.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "run_id": r.run_id,
            "stage": r.stage,
            "sub_stage": r.sub_stage,
            "confidence": r.confidence,
            "eta_seconds": r.eta_seconds,
            "explanation": r.explanation,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reversed(rows)
    ]
