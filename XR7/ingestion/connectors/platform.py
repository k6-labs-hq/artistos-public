# Platform Connectors: connects to YouTube Content ID, TikTok Creator, Instagram, etc.
#
# NOTE: YouTube Content ID requires a formal CMS partnership agreement with Google
# and is not available via a simple API key signup.  TikTok and Instagram creator
# monetisation APIs require approved developer access.
#
# Use the statement upload workflow to ingest platform CSV exports:
#   POST /artists/{id}/statements/upload
#
# Required environment variables for future platform API integrations:
#   YOUTUBE_API_KEY  (for metadata only; CMS requires OAuth2 service-account)
#   TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET
#   INSTAGRAM_APP_ID, INSTAGRAM_APP_SECRET
import os
from datetime import datetime

from XR7.ingestion.connectors.base import BaseConnector

_PLATFORM_ENV_VARS = {
    "YouTube":   ("YOUTUBE_API_KEY",),
    "TikTok":    ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET"),
    "Instagram": ("INSTAGRAM_APP_ID", "INSTAGRAM_APP_SECRET"),
}


class PlatformConnector(BaseConnector):
    """
    Connector for a content/social platform (YouTube, TikTok, Instagram).

    ``connect()`` checks whether the required credential environment variables
    are set.  ``fetch_historical()`` and ``fetch_recent()`` raise
    ``NotImplementedError`` — use platform CSV/JSON exports and the statement
    upload workflow instead.
    """

    def __init__(self, config: dict, platform_name: str = "YouTube"):
        super().__init__(config)
        self.platform_name = platform_name

    def _required_env_vars(self) -> tuple[str, ...]:
        return _PLATFORM_ENV_VARS.get(
            self.platform_name,
            (f"{self.platform_name.upper().replace(' ', '_')}_API_KEY",),
        )

    def connect(self) -> bool:
        """
        Return ``True`` if all required credential environment variables are set,
        ``False`` otherwise.  Does NOT make a real network call.
        """
        return all(
            self.config.get(v.lower()) or os.environ.get(v, "")
            for v in self._required_env_vars()
        )

    def fetch_historical(self, artist_id: str, start_date: datetime, end_date: datetime) -> list[dict]:
        raise NotImplementedError(
            f"{self.platform_name} API integration is not yet configured.  "
            f"Required env vars: {', '.join(self._required_env_vars())}.  "
            f"Alternatively, export your analytics as CSV and upload via "
            f"POST /artists/{{artist_id}}/statements/upload."
        )

    def fetch_recent(self, artist_id: str, since: datetime) -> list[dict]:
        raise NotImplementedError(
            f"{self.platform_name} API integration is not yet configured.  "
            f"See fetch_historical() for setup instructions."
        )

    def normalize(self, raw_data: list[dict]) -> list[dict]:
        normalized = []
        for record in raw_data:
            normalized.append({
                "source": self.platform_name,
                "event_type": record.get("event_type", "STREAM"),
                "artist_id": record.get("artist_id"),
                "work_id": record.get("work_id"),
                "quantity": record.get("views", record.get("quantity", 0)),
                "unit_value": record.get("cpm", record.get("unit_value", 0.0)),
                "currency": record.get("currency", "USD"),
                "territory": record.get("country", record.get("territory")),
                "timestamp": record.get("timestamp"),
                "platform": self.platform_name,
            })
        return normalized
