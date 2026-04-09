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
from XR7.ingestion.connectors.file_backfill import load_statement_rows

_PLATFORM_ENV_VARS = {
    "YouTube": ("YOUTUBE_API_KEY",),
    "TikTok": ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET"),
    "Instagram": ("INSTAGRAM_APP_ID", "INSTAGRAM_APP_SECRET"),
}


class PlatformConnector(BaseConnector):
    """
    Connector for a content/social platform (YouTube, TikTok, Instagram).

    ``connect()`` checks whether the required credential environment variables
    are set. ``fetch_historical()`` and ``fetch_recent()`` use statement-file
    backfill when configured and otherwise return an empty result.
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
            self.config.get(v.lower()) or os.environ.get(v, "") for v in self._required_env_vars()
        )

    def fetch_historical(
        self, artist_id: str, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        rows = load_statement_rows(
            config=self.config,
            source_name=self.platform_name,
            env_name=f"{self.platform_name.upper().replace(' ', '_')}_STATEMENT_FILES",
            artist_id=artist_id,
            start=start_date,
            end=end_date,
        )
        return rows

    def fetch_recent(self, artist_id: str, since: datetime) -> list[dict]:
        return self.fetch_historical(artist_id, since, datetime.now(tz=since.tzinfo))

    def normalize(self, raw_data: list[dict]) -> list[dict]:
        normalized = []
        for record in raw_data:
            normalized.append(
                {
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
                }
            )
        return normalized
