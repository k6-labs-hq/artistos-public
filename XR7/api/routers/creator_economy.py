"""Pillar 4 — Creator-economy ingestion + anomaly detection endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.anomaly.rules.creator_economy import detect_creator_anomalies
from XR7.api.routers.auth import require_artist_access
from XR7.ingestion.creator_parsers import CREATOR_PARSERS, parse_creator_platform
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["creator_economy"])

_SUPPORTED_PLATFORMS = sorted(CREATOR_PARSERS.keys())


class CreatorIngestRequest(BaseModel):
    platform: str
    rows: list[dict[str, Any]]


@router.post("/artists/{artist_id}/creator/ingest")
def ingest_creator_data(
    artist_id: str,
    payload: CreatorIngestRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """Parse and anomaly-scan creator-economy platform data.

    Accepts raw export rows from YouTube Studio, TikTok, Instagram Reels,
    Twitch, Patreon, or Shopify. Returns parsed events and detected anomalies.
    """
    if payload.platform not in CREATOR_PARSERS:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported platform '{payload.platform}'. "
            f"Supported: {_SUPPORTED_PLATFORMS}",
        )

    events = parse_creator_platform(payload.platform, payload.rows)
    anomalies = detect_creator_anomalies(events, artist_id)

    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "platform": payload.platform,
            "events_parsed": len(events),
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies,
            "events": events,
        },
    )


@router.get("/artists/{artist_id}/creator/platforms")
def list_creator_platforms(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> dict:
    """List all supported creator-economy platforms."""
    return inject_branding_metadata(
        db,
        {
            "artist_id": artist_id,
            "supported_platforms": _SUPPORTED_PLATFORMS,
        },
    )
