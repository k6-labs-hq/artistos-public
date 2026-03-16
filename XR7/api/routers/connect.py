from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from XR7.ingestion.connectors.global_social_regional import GlobalSocialRegionalConnector
from XR7.models.base import get_db
from XR7.services.branding import inject_branding_metadata

router = APIRouter(tags=["connect"])


@router.post("/artists/{artist_id}/connect/global-social")
async def connect_global_social(artist_id: str, platform: str, db: Session = Depends(get_db)):
    conn = GlobalSocialRegionalConnector()
    auth_url = await conn.oauth_flow(artist_id, platform)
    return inject_branding_metadata(
        db,
        {"artist_id": artist_id, "platform": platform, "auth_url": auth_url},
    )


@router.get("/artists/{artist_id}/connect/global-social/status")
def connect_global_social_status(artist_id: str, db: Session = Depends(get_db)):
    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "status": "ready_with_fallbacks",
        "platforms": ["youtube", "tiktok", "instagram", "soundcloud", "melon", "boomplay", "tencent", "jiosaavn"],
    })


@router.post("/artists/{artist_id}/connect/soundcloud")
async def connect_soundcloud(artist_id: str, db: Session = Depends(get_db)):
    conn = GlobalSocialRegionalConnector()
    auth_url = await conn.oauth_flow(artist_id, "soundcloud")
    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "platform": "soundcloud",
        "auth_url": auth_url,
        "status": "authorization_url_generated",
    })


@router.get("/artists/{artist_id}/connect/soundcloud/status")
def connect_soundcloud_status(artist_id: str, db: Session = Depends(get_db)):
    return inject_branding_metadata(db, {
        "artist_id": artist_id,
        "provider": "soundcloud",
        "status": "ready_with_fallbacks",
    })
