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


class PROConnector(BaseConnector):
    """
    Connector for a Performing Rights Organisation (PRO).

    ``connect()`` checks whether the required API key environment variable is
    set.  ``fetch_historical()`` and ``fetch_recent()`` raise
    ``NotImplementedError`` until a real API integration is built — use the
    statement file upload workflow in the meantime.
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
        raise NotImplementedError(
            f"{self.pro_name} API integration is not yet configured.  "
            f"Set the '{self._env_key()}' environment variable and implement "
            f"this method with a real API client.  "
            f"Alternatively, upload statement CSV files via "
            f"POST /artists/{{artist_id}}/statements/upload."
        )

    def fetch_recent(self, artist_id: str, since: datetime) -> list[dict]:
        raise NotImplementedError(
            f"{self.pro_name} API integration is not yet configured.  "
            f"See fetch_historical() for setup instructions."
        )

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
