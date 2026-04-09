# Ticketing Connectors: connects to Ticketmaster, AXS, SeatGeek, Eventbrite, etc.
#
# NOTE: Ticketmaster and AXS require an approved partnership/developer agreement
# for access to artist settlement and payout data.  SeatGeek and Eventbrite have
# public APIs but do not expose per-artist financial settlement data.
#
# Use the statement upload workflow to ingest settlement CSV exports:
#   POST /artists/{id}/statements/upload
#
# Required environment variables for future ticketing API integrations:
#   TICKETMASTER_API_KEY
#   AXS_API_KEY
#   SEATGEEK_CLIENT_ID, SEATGEEK_CLIENT_SECRET
#   EVENTBRITE_PRIVATE_TOKEN
import os
from datetime import datetime

from XR7.ingestion.connectors.base import BaseConnector
from XR7.ingestion.connectors.file_backfill import load_statement_rows

_TICKETING_ENV_VARS = {
    "Ticketmaster": ("TICKETMASTER_API_KEY",),
    "AXS": ("AXS_API_KEY",),
    "SeatGeek": ("SEATGEEK_CLIENT_ID", "SEATGEEK_CLIENT_SECRET"),
    "Eventbrite": ("EVENTBRITE_PRIVATE_TOKEN",),
}


class TicketingConnector(BaseConnector):
    """
    Connector for a ticketing platform (Ticketmaster, AXS, SeatGeek, Eventbrite).

    ``connect()`` checks whether the required credential environment variables
    are set. ``fetch_historical()`` and ``fetch_recent()`` use statement-file
    backfill when configured and otherwise return an empty result.
    """

    def __init__(self, config: dict, platform_name: str = "Ticketmaster"):
        super().__init__(config)
        self.platform_name = platform_name

    def _required_env_vars(self) -> tuple[str, ...]:
        return _TICKETING_ENV_VARS.get(
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
                    "event_type": "SHOW",
                    "artist_id": record.get("artist_id"),
                    "quantity": record.get("tickets_sold", record.get("quantity", 1)),
                    "unit_value": record.get("guarantee", record.get("unit_value", 0.0)),
                    "currency": record.get("currency", "USD"),
                    "territory": record.get("country", record.get("territory")),
                    "timestamp": record.get("show_date", record.get("timestamp")),
                    "platform": self.platform_name,
                }
            )
        return normalized
