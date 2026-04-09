from __future__ import annotations

import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from XR7.celery_app import celery_app
from xr7_common.logging import get_logger

logger = get_logger(__name__)


class UGCUsageMonitor:
    """Monitor UGC platforms for usage opportunities."""

    def __init__(self):
        self.youtube_key = os.environ.get("YOUTUBE_API_KEY", "")
        self.tiktok_key = os.environ.get("TIKTOK_API_KEY", "")
        self.simulated = not (self.youtube_key or self.tiktok_key)

    async def scan_for_uses(self, artist_id: str, days_back: int = 30) -> list[dict[str, Any]]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
        if self.simulated:
            return [
                {
                    "use_id": f"yt-{artist_id}-viral-1",
                    "platform": "youtube",
                    "title": "Fan vlog using chorus hook",
                    "url": "https://example.com/youtube/use-1",
                    "views": 950000,
                    "engagement_rate": 0.062,
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                    "cutoff": cutoff.isoformat(),
                },
                {
                    "use_id": f"tt-{artist_id}-viral-2",
                    "platform": "tiktok",
                    "title": "Dance trend with unreleased stem",
                    "url": "https://example.com/tiktok/use-2",
                    "views": 1800000,
                    "engagement_rate": 0.084,
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                    "cutoff": cutoff.isoformat(),
                },
            ]
        return []

    def calculate_lost_sync_value(self, use: dict[str, Any]) -> float:
        views = float(use.get("views") or 0.0)
        engagement = float(use.get("engagement_rate") or 0.0)
        base = views * 0.0012
        multiplier = 1.0 + min(0.5, engagement)
        return round(base * multiplier, 2)

    def generate_ugc_claim_packet(self, use: dict[str, Any]) -> dict[str, Any]:
        value = self.calculate_lost_sync_value(use)
        payload = {
            "ugc_use": use,
            "estimated_recoverable": value,
            "evidence_links": [use.get("url")],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        payload["packet_hash"] = hashlib.sha256(str(payload).encode("utf-8")).hexdigest()
        return payload


@celery_app.task(name="xr7.pipeline.scan_ugc_daily", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 2})
def scan_ugc_daily(self, artist_id: str) -> dict:  # noqa: ANN001
    monitor = UGCUsageMonitor()
    uses = __import__("asyncio").run(monitor.scan_for_uses(artist_id, days_back=30))
    packets = [monitor.generate_ugc_claim_packet(u) for u in uses]
    logger.info("UGC scan complete", extra={"artist_id": artist_id, "detected": len(uses)})
    return {"artist_id": artist_id, "detected_uses": uses, "packets": packets}
