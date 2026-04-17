# DSP Connectors: connects to Spotify, Apple Music, Amazon Music, Tidal, Deezer, etc.
#
# NOTE: DSPs do not provide direct royalty-data APIs to artists.  Royalty data
# flows through distributors (DistroKid, TuneCore, CD Baby, etc.) or aggregators.
# Use the statement upload workflow to ingest distributor CSV exports:
#   POST /artists/{id}/statements/upload
#
# Spotify's Web API provides catalogue/popularity data but NOT per-stream royalties.
# For royalty data, artists must use Spotify for Artists dashboard exports.
#
# Required environment variables for future Spotify Web API integration:
#   SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
import os
from datetime import datetime

from XR7.ingestion.connectors.base import BaseConnector
from XR7.ingestion.connectors.circuit_breaker import CircuitBreaker
from XR7.ingestion.connectors.file_backfill import load_statement_rows

_DSP_ENV_VARS = {
    "Spotify": ("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET"),
    "Apple Music": ("APPLE_KEY_ID", "APPLE_TEAM_ID"),
    "Amazon Music": ("AMAZON_CLIENT_ID", "AMAZON_CLIENT_SECRET"),
    "Tidal": ("TIDAL_CLIENT_ID", "TIDAL_CLIENT_SECRET"),
    "Deezer": ("DEEZER_APP_ID", "DEEZER_APP_SECRET"),
}


class DSPConnector(BaseConnector):
    """
    Connector for a Digital Streaming Platform (DSP).

    ``connect()`` checks whether the required credential environment variables
    are set. ``fetch_historical()`` and ``fetch_recent()`` use statement-file
    backfill when configured and otherwise return an empty result.
    """

    def __init__(self, config: dict, dsp_name: str = "Spotify"):
        super().__init__(config)
        self.dsp_name = dsp_name
        self._breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=60)

    def _required_env_vars(self) -> tuple[str, ...]:
        return _DSP_ENV_VARS.get(
            self.dsp_name, (f"{self.dsp_name.upper().replace(' ', '_')}_API_KEY",)
        )

    def connect(self) -> bool:
        """
        Return ``True`` if all required credential environment variables are set,
        ``False`` otherwise.  Does NOT make a real network call.
        """
        def _check() -> bool:
            env_vars = self._required_env_vars()
            return all(self.config.get(v.lower()) or os.environ.get(v, "") for v in env_vars)

        return self._breaker.run(_check, operation_name=f"{self.dsp_name}.connect")

    def fetch_historical(
        self, artist_id: str, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        def _fetch() -> list[dict]:
            return load_statement_rows(
                config=self.config,
                source_name=self.dsp_name,
                env_name=f"{self.dsp_name.upper().replace(' ', '_')}_STATEMENT_FILES",
                artist_id=artist_id,
                start=start_date,
                end=end_date,
            )

        return self._breaker.run(_fetch, operation_name=f"{self.dsp_name}.fetch_historical")

    def fetch_recent(self, artist_id: str, since: datetime) -> list[dict]:
        return self.fetch_historical(artist_id, since, datetime.now(tz=since.tzinfo))

    def normalize(self, raw_data: list[dict]) -> list[dict]:
        normalized = []
        for record in raw_data:
            normalized.append(
                {
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
                }
            )
        return normalized
