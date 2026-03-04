# DSP Connectors: connects to Spotify, Apple Music, Amazon Music, Tidal, Deezer, etc.
# Each DSP provides streaming data reports; this stub simulates the interface.
from datetime import datetime

from arcos7.ingestion.connectors.base import BaseConnector


class DSPConnector(BaseConnector):
    def __init__(self, config: dict, dsp_name: str = "Spotify"):
        super().__init__(config)
        self.dsp_name = dsp_name

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
                "source": self.dsp_name,
                "event_type": "STREAM",
                "artist_id": record.get("artist_id"),
                "work_id": record.get("work_id"),
                "quantity": record.get("streams", record.get("quantity", 0)),
                "unit_value": record.get("rate", record.get("unit_value", 0.004)),
                "currency": record.get("currency", "USD"),
                "territory": record.get("country", record.get("territory")),
                "timestamp": record.get("timestamp"),
                "platform": self.dsp_name,
            })
        return normalized
