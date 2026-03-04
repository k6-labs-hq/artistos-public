# Platform Connectors: connects to YouTube Content ID, TikTok Creator, Instagram, etc.
# These platforms provide ad revenue and content usage data; this stub simulates the interface.
from datetime import datetime

from arcos7.ingestion.connectors.base import BaseConnector


class PlatformConnector(BaseConnector):
    def __init__(self, config: dict, platform_name: str = "YouTube"):
        super().__init__(config)
        self.platform_name = platform_name

    def connect(self) -> bool:
        return True

    def fetch_historical(self, artist_id: str, start_date: datetime, end_date: datetime) -> list[dict]:
        return []

    def fetch_recent(self, artist_id: str, since: datetime) -> list[dict]:
        return []

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
