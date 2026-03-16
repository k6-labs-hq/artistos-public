from __future__ import annotations

from fastapi import APIRouter

from XR7.ingestion.connectors.global_social_regional import GlobalSocialRegionalConnector

router = APIRouter(tags=["connect"])


@router.post("/artists/{artist_id}/connect/global-social")
async def connect_global_social(artist_id: str, platform: str):
    conn = GlobalSocialRegionalConnector()
    auth_url = await conn.oauth_flow(artist_id, platform)
    return {"artist_id": artist_id, "platform": platform, "auth_url": auth_url}


@router.get("/artists/{artist_id}/connect/global-social/status")
def connect_global_social_status(artist_id: str):
    return {
        "artist_id": artist_id,
        "status": "ready_with_fallbacks",
        "platforms": ["youtube", "tiktok", "instagram", "melon", "boomplay", "tencent", "jiosaavn"],
    }
