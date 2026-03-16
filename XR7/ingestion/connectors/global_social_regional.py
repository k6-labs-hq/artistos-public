from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from XR7.ingestion.connectors.base import IngestionConnector


class GlobalSocialRegionalConnector(IngestionConnector):
    name = "global_social_regional"

    def __init__(self, config: dict | None = None):
        super().__init__(config=config or {})
        self.simulated = os.environ.get("XR7_GLOBAL_SOCIAL_SIMULATED", "1").strip().lower() in {"1", "true", "yes"}

    def connect(self) -> bool:
        return True

    def fetch_historical(self, artist_id: str, start_date: datetime, end_date: datetime) -> list[dict[str, Any]]:
        return []

    def fetch_recent(self, artist_id: str, since: datetime) -> list[dict[str, Any]]:
        return []

    def normalize(self, raw_data: list[dict]) -> list[dict]:
        return raw_data

    async def oauth_flow(self, artist_id: str, platform: str) -> str:
        return f"https://auth.example.com/{platform}/oauth?artist_id={artist_id}"

    async def fetch_usage_and_ugc(self, artist_id: str, platform: str) -> list[dict[str, Any]]:
        return [
            {
                "artist_id": artist_id,
                "platform": platform,
                "source_type": "social",
                "source_name": platform,
                "record_type": "UGC",
                "event_type": "UNREPORTED_USE",
                "amount": 0.0,
                "currency": "USD",
                "work_id": f"{platform}-work-1",
                "metadata_json": "{\"mode\":\"simulated\"}",
                "detected_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

    async def scan_ugc_opportunities(self, artist_id: str) -> list[dict[str, Any]]:
        return [
            {"platform": "youtube", "title": "Viral vlog sync", "estimated_recoverable": 4200.0},
            {"platform": "tiktok", "title": "Dance trend usage", "estimated_recoverable": 5100.0},
            {"platform": "soundcloud", "title": "Unofficial remix repost cluster", "estimated_recoverable": 2300.0},
        ]

    def generate_csv_export_instructions(self, platform: str) -> dict[str, Any]:
        return {
            "platform": platform,
            "steps": [
                f"Open {platform.title()} creator dashboard",
                "Go to analytics/reports export",
                "Download CSV with date, title, views, and revenue columns",
                "Upload to POST /artists/{id}/statements/upload",
            ],
            "screenshot_placeholders": ["step1.png", "step2.png", "step3.png"],
        }
