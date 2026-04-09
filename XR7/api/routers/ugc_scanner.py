"""
YouTube / TikTok / Meta UGC Revenue Opportunity Scanner + Auto-Claim Flow.

Endpoints:
  POST /artists/{artist_id}/fetchers/ugc/scan
  POST /artists/{artist_id}/ugc/claims/{ugc_anomaly_id}/draft
  GET  /artists/{artist_id}/ugc/opportunities
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.api.routers.auth import require_artist_access
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.oauth_connector import ConnectorAccountLink
from XR7.models.ugc_opportunity import (
    UGCOpportunity,
    UGCOpportunitySchema,
    UGCOpportunityStatus,
    UGCPlatform,
)
from XR7.models.work import Work
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from xr7_common.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["ugc_scanner"])

# ---------------------------------------------------------------------------
# Mock UGC scan results  (replace with live YouTube Data API / TikTok API calls
# once OAuth tokens are available)
# ---------------------------------------------------------------------------

_MOCK_PLATFORM_VIDEOS: dict[str, list[dict[str, Any]]] = {
    "youtube": [
        {
            "video_id": "yt_mock_001",
            "video_url": "https://www.youtube.com/watch?v=yt_mock_001",
            "video_title": "Fan cover of [MATCHED WORK] — 2.3M views",
            "channel_name": "FanCoversUnofficial",
            "estimated_views": 2_300_000,
            "monetization_active": False,
            "content_id_claimed": False,
        },
        {
            "video_id": "yt_mock_002",
            "video_url": "https://www.youtube.com/watch?v=yt_mock_002",
            "video_title": "Best of [ARTIST] compilation",
            "channel_name": "TopMusicChannel",
            "estimated_views": 870_000,
            "monetization_active": False,
            "content_id_claimed": False,
        },
    ],
    "tiktok": [
        {
            "video_id": "tt_mock_001",
            "video_url": "https://www.tiktok.com/@user/video/tt_mock_001",
            "video_title": "Trending dance to [MATCHED WORK]",
            "channel_name": "@viral_dancer",
            "estimated_views": 5_200_000,
            "monetization_active": False,
            "content_id_claimed": False,
        },
    ],
    "meta": [
        {
            "video_id": "fb_mock_001",
            "video_url": "https://www.facebook.com/watch/?v=fb_mock_001",
            "video_title": "Lyric video — [MATCHED WORK] (unofficial)",
            "channel_name": "UnofficialLyrics FB",
            "estimated_views": 380_000,
            "monetization_active": False,
            "content_id_claimed": False,
        },
    ],
}

# Revenue-per-view estimates by platform (USD)
_RPV: dict[str, float] = {
    "youtube": 0.0025,   # ~$2.50 CPM avg
    "tiktok": 0.00025,   # lower monetisation share
    "meta": 0.0018,
}


def _estimate_recoverable(platform: str, views: int) -> float:
    rpv = _RPV.get(platform, 0.001)
    return round(views * rpv, 2)


# ---------------------------------------------------------------------------
# Internal scan function
# ---------------------------------------------------------------------------

def _scan_platform(
    db: Session,
    artist: Artist,
    platform: str,
    connector: ConnectorAccountLink | None,
) -> list[UGCOpportunity]:
    """
    Scan one platform for un-monetized UGC opportunities.
    Returns list of newly created UGCOpportunity rows (not yet committed).
    """
    works = db.query(Work).filter(Work.artist_id == artist.id).all()
    if not works:
        return []

    primary_work = works[0]
    mock_videos = _MOCK_PLATFORM_VIDEOS.get(platform, [])
    new_opps: list[UGCOpportunity] = []

    for vid in mock_videos:
        video_id = str(vid.get("video_id") or "")
        video_url = str(vid.get("video_url") or "")
        views = int(vid.get("estimated_views") or 0)

        # Skip if already tracked
        existing = (
            db.query(UGCOpportunity)
            .filter(
                UGCOpportunity.artist_id == artist.id,
                UGCOpportunity.video_id == video_id,
            )
            .first()
        )
        if existing:
            # Update last_scanned_at
            existing.last_scanned_at = datetime.now(timezone.utc)
            existing.estimated_views = max(existing.estimated_views, views)
            existing.estimated_recoverable = _estimate_recoverable(platform, existing.estimated_views)
            continue

        recoverable = _estimate_recoverable(platform, views)

        # Create anomaly
        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            category=AnomalyCategory.ROYALTY.value,
            subtype="ugc_opportunity",
            severity=AnomalySeverity.HIGH.value if recoverable >= 500 else AnomalySeverity.MEDIUM.value,
            estimated_recoverable=recoverable,
            confidence_score=0.78,
            description=(
                f"Un-monetized UGC match on {platform.capitalize()}: "
                f"'{vid.get('video_title', '')}' — "
                f"~{views:,} views, est. ${recoverable:,.2f} recoverable."
            ),
            status=AnomalyStatus.OPEN.value,
            urgent_flag=recoverable >= 1000,
        )
        db.add(anomaly)
        db.flush()

        title_hint = str(vid.get("video_title") or "").replace("[MATCHED WORK]", primary_work.title)

        opp = UGCOpportunity(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            platform=platform,
            video_url=video_url,
            video_id=video_id,
            video_title=title_hint,
            channel_name=str(vid.get("channel_name") or ""),
            matched_work_title=primary_work.title,
            matched_isrc=primary_work.isrc,
            estimated_views=views,
            estimated_recoverable=recoverable,
            status=UGCOpportunityStatus.DETECTED.value,
            is_monetized=bool(vid.get("monetization_active", False)),
            detected_at=datetime.now(timezone.utc),
            last_scanned_at=datetime.now(timezone.utc),
        )
        db.add(opp)
        new_opps.append(opp)

    return new_opps


# ---------------------------------------------------------------------------
# Response / request schemas
# ---------------------------------------------------------------------------


class UGCScanRequest(BaseModel):
    platforms: list[str] = Field(
        default=["youtube", "tiktok", "meta"],
        description="Platforms to scan. Defaults to all supported.",
    )


class UGCScanResponse(BaseModel):
    artist_id: str
    platforms_scanned: list[str]
    new_opportunities: int
    total_estimated_recoverable: float
    opportunities: list[UGCOpportunitySchema]
    scanned_at: datetime


class UGCClaimDraftResponse(BaseModel):
    ugc_opportunity_id: str
    anomaly_id: str | None
    platform: str
    claim_draft: dict[str, Any]
    drafted_at: datetime


class UGCOpportunityListResponse(BaseModel):
    artist_id: str
    opportunities: list[UGCOpportunitySchema]
    total: int
    total_estimated_recoverable: float


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/artists/{artist_id}/fetchers/ugc/scan",
    response_model=UGCScanResponse,
    summary="Scan connected accounts for un-monetized UGC matches",
)
def scan_ugc_opportunities(
    artist_id: str,
    body: UGCScanRequest = UGCScanRequest(),
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> UGCScanResponse:
    """
    Scans connected YouTube / TikTok / Meta accounts for unauthorized uses
    or un-monetized Content ID matches.  Creates ``ugc_opportunity`` anomalies
    for each new match found.
    """
    artist = get_artist_or_404(artist_id, db)

    _SUPPORTED = {"youtube", "tiktok", "meta", "instagram"}
    platforms = [p.lower() for p in body.platforms if p.lower() in _SUPPORTED]
    if not platforms:
        raise HTTPException(
            status_code=422,
            detail=f"No valid platforms specified. Supported: {sorted(_SUPPORTED)}",
        )

    all_new: list[UGCOpportunity] = []
    for platform in platforms:
        # Look up linked connector (may be None — we still scan with mock data)
        connector = (
            db.query(ConnectorAccountLink)
            .filter(
                ConnectorAccountLink.artist_id == artist_id,
                ConnectorAccountLink.provider == platform,
            )
            .first()
        )
        new_opps = _scan_platform(db, artist, platform, connector)
        all_new.extend(new_opps)

    db.flush()

    if all_new:
        try:
            ImmutableLedgerService(db).append(
                artist_id,
                "ugc_scan_completed",
                {
                    "platforms": platforms,
                    "new_opportunities": len(all_new),
                    "total_recoverable": sum(o.estimated_recoverable for o in all_new),
                },
            )
        except Exception:
            logger.exception("Failed to write ugc_scan ledger entry for artist %s", artist_id)

    db.commit()

    schemas = [UGCOpportunitySchema.model_validate(o) for o in all_new]
    total_recoverable = sum(float(o.estimated_recoverable) for o in all_new)

    return UGCScanResponse(
        artist_id=artist_id,
        platforms_scanned=platforms,
        new_opportunities=len(all_new),
        total_estimated_recoverable=round(total_recoverable, 2),
        opportunities=schemas,
        scanned_at=datetime.now(timezone.utc),
    )


@router.post(
    "/artists/{artist_id}/ugc/claims/{ugc_opportunity_id}/draft",
    response_model=UGCClaimDraftResponse,
    summary="Auto-draft a Content ID / DMCA claim for a UGC opportunity",
)
def draft_ugc_claim(
    artist_id: str,
    ugc_opportunity_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> UGCClaimDraftResponse:
    """
    Generates a platform-appropriate claim draft payload (Content ID asset
    claim for YouTube, DMCA-style takedown for others).  Marks the opportunity
    status as ``claim_drafted`` and logs the action.
    """
    artist = get_artist_or_404(artist_id, db)

    opp = (
        db.query(UGCOpportunity)
        .filter(
            UGCOpportunity.id == ugc_opportunity_id,
            UGCOpportunity.artist_id == artist_id,
        )
        .first()
    )
    if not opp:
        raise HTTPException(status_code=404, detail="UGC opportunity not found")

    if opp.status == UGCOpportunityStatus.MONETIZED.value:
        raise HTTPException(status_code=409, detail="Opportunity is already monetized")
    if opp.status == UGCOpportunityStatus.DISMISSED.value:
        raise HTTPException(status_code=409, detail="Opportunity has been dismissed")

    now = datetime.now(timezone.utc)
    platform = str(opp.platform)

    # ── Build platform-specific draft ──────────────────────────────────────
    if platform == UGCPlatform.YOUTUBE.value:
        claim_draft: dict[str, Any] = {
            "platform": "youtube",
            "claim_type": "content_id",
            "action": "monetize",
            "asset": {
                "title": opp.matched_work_title or "Unknown Work",
                "isrc": opp.matched_isrc,
                "artist": artist.name,
                "type": "sound_recording",
                "content_id_asset_id": opp.content_id_asset_id,
            },
            "video": {
                "video_id": opp.video_id,
                "video_url": opp.video_url,
                "video_title": opp.video_title,
                "channel": opp.channel_name,
                "estimated_views": opp.estimated_views,
            },
            "policy": "monetize",  # alternatives: "block", "track"
            "territory": "worldwide",
            "claimant": {
                "name": artist.name,
                "ipi": artist.ipi_number,
                "email": artist.email,
            },
            "submission_endpoint": "https://www.googleapis.com/youtube/partner/v1/claims",
            "notes": (
                "Submit via YouTube Content Manager or YouTube Partner API "
                f"(POST to claims endpoint). IPI: {artist.ipi_number or 'N/A'}."
            ),
            "estimated_recoverable_usd": opp.estimated_recoverable,
            "draft_generated_at": now.isoformat(),
        }
    elif platform in (UGCPlatform.TIKTOK.value, "instagram", UGCPlatform.META.value):
        claim_draft = {
            "platform": platform,
            "claim_type": "dmca_takedown",
            "action": "monetize_or_takedown",
            "rights_holder": {
                "name": artist.name,
                "ipi": artist.ipi_number,
                "email": artist.email,
                "pro": None,  # to be filled from artist PRO registration
            },
            "infringing_content": {
                "video_id": opp.video_id,
                "video_url": opp.video_url,
                "video_title": opp.video_title,
                "channel": opp.channel_name,
                "platform": platform,
            },
            "work": {
                "title": opp.matched_work_title or "Unknown Work",
                "isrc": opp.matched_isrc,
                "type": "sound_recording",
            },
            "submission_url": (
                "https://www.tiktok.com/legal/report/Copyright"
                if platform == "tiktok"
                else "https://www.facebook.com/help/contact/634636770043106"
            ),
            "estimated_recoverable_usd": opp.estimated_recoverable,
            "notes": (
                f"File a {platform.upper()} copyright claim via the platform's IP "
                "reporting portal. Use ISRC as proof of ownership if requested."
            ),
            "draft_generated_at": now.isoformat(),
        }
    else:
        claim_draft = {
            "platform": platform,
            "claim_type": "general_copyright_notice",
            "rights_holder": {"name": artist.name, "email": artist.email},
            "infringing_content": {"video_url": opp.video_url},
            "work": {"title": opp.matched_work_title, "isrc": opp.matched_isrc},
            "estimated_recoverable_usd": opp.estimated_recoverable,
            "draft_generated_at": now.isoformat(),
        }

    # Persist draft on the opportunity
    opp.claim_draft_json = json.dumps(claim_draft)
    opp.status = UGCOpportunityStatus.CLAIM_DRAFTED.value
    opp.updated_at = now

    # Log
    try:
        ImmutableLedgerService(db).append(
            artist_id,
            "ugc_claim_drafted",
            {
                "ugc_opportunity_id": ugc_opportunity_id,
                "platform": platform,
                "video_id": opp.video_id,
                "estimated_recoverable_usd": opp.estimated_recoverable,
                "claim_type": claim_draft.get("claim_type"),
            },
        )
    except Exception:
        logger.exception("Failed to write ugc_claim_drafted ledger entry for artist %s", artist_id)

    db.commit()

    return UGCClaimDraftResponse(
        ugc_opportunity_id=ugc_opportunity_id,
        anomaly_id=opp.anomaly_id,
        platform=platform,
        claim_draft=claim_draft,
        drafted_at=now,
    )


@router.get(
    "/artists/{artist_id}/ugc/opportunities",
    response_model=UGCOpportunityListResponse,
    summary="List all UGC revenue opportunities for the artist",
)
def list_ugc_opportunities(
    artist_id: str,
    platform: UGCPlatform | None = None,
    status: UGCOpportunityStatus | None = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> UGCOpportunityListResponse:
    get_artist_or_404(artist_id, db)

    q = db.query(UGCOpportunity).filter(UGCOpportunity.artist_id == artist_id)
    if platform:
        q = q.filter(UGCOpportunity.platform == platform.value)
    if status:
        q = q.filter(UGCOpportunity.status == status.value)

    rows: list[UGCOpportunity] = q.order_by(UGCOpportunity.detected_at.desc()).all()
    schemas = [UGCOpportunitySchema.model_validate(r) for r in rows]
    total_recoverable = sum(float(r.estimated_recoverable) for r in rows)

    return UGCOpportunityListResponse(
        artist_id=artist_id,
        opportunities=schemas,
        total=len(schemas),
        total_estimated_recoverable=round(total_recoverable, 2),
    )
