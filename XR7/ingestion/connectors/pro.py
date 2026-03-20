# PRO Connectors: connects to ASCAP, BMI, SESAC, GMR, SOCAN, PRS, GEMA APIs
#
# NOTE: PRO APIs (ASCAP, BMI, SESAC, etc.) are not publicly available.
# Access requires a formal data-partnership agreement with each organisation.
# Until those agreements are in place, use the statement upload workflow:
#   POST /artists/{id}/statements/upload
# Artists can download their royalty statement CSVs from each PRO portal and
# upload them directly — this gives equivalent data coverage.
#
# Required environment variables when a real PRO API is available:
#   ASCAP_API_KEY, BMI_API_KEY, SESAC_API_KEY, GMR_API_KEY,
#   SOCAN_API_KEY, PRS_API_KEY, GEMA_API_KEY
import os
from datetime import datetime

from XR7.ingestion.connectors.base import BaseConnector
from XR7.ingestion.connectors.file_backfill import load_statement_rows


class PROConnector(BaseConnector):
    """
    Connector for a Performing Rights Organisation (PRO).

    ``connect()`` checks whether the required API key environment variable is
    set. ``fetch_historical()`` and ``fetch_recent()`` use statement-file
    backfill when configured and otherwise return an empty result.
    """

    def __init__(self, config: dict, pro_name: str = "ASCAP"):
        super().__init__(config)
        self.pro_name = pro_name

    def _env_key(self) -> str:
        """Return the environment variable name expected for this PRO's API key."""
        return f"{self.pro_name.upper().replace(' ', '_')}_API_KEY"

    def connect(self) -> bool:
        """
        Return ``True`` if the API key environment variable is set,
        ``False`` otherwise.  Does NOT make a real network call.
        """
        api_key = self.config.get("api_key") or os.environ.get(self._env_key(), "")
        return bool(api_key)

    def fetch_historical(self, artist_id: str, start_date: datetime, end_date: datetime) -> list[dict]:
        rows = load_statement_rows(
            config=self.config,
            source_name=self.pro_name,
            env_name=f"{self.pro_name.upper().replace(' ', '_')}_STATEMENT_FILES",
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
            normalized.append({
                "source": self.pro_name,
                "event_type": "STREAM",
                "artist_id": record.get("artist_id"),
                "work_id": record.get("work_id"),
                "quantity": record.get("quantity", 0),
                "unit_value": record.get("unit_value", 0.0),
                "currency": record.get("currency", "USD"),
                "territory": record.get("territory"),
                "timestamp": record.get("timestamp"),
                "platform": self.pro_name,
            })
        return normalized
