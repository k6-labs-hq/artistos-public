# Distributor Connectors: connects to small-label / indie-distributor APIs
#
# NOTE: Most small distributors (Amuse, United Masters, ONErpm, Stem, LANDR,
# Ditto Music, ReverbNation, Bandcamp) do not offer public royalty-data APIs
# for third-party access.  Until formal data-partnership agreements are in
# place, the primary ingestion path is the statement CSV upload:
#
#   POST /artists/{id}/statements/upload
#
# Artists can download their royalty statement CSVs from each distributor's
# dashboard and upload them directly — the parser auto-detects the format.
# This connector class provides a consistent credential-check interface that
# mirrors ``PROConnector`` and ``DSPConnector``.  When an API becomes
# available, implement ``fetch_historical()`` and ``fetch_recent()`` here.
#
# Required environment variables (set when the API is available):
#   AMUSE_API_KEY
#   UNITEDMASTERS_API_KEY
#   ONERPM_API_KEY
#   STEM_CLIENT_ID, STEM_CLIENT_SECRET
#   LANDR_API_KEY
#   DITTO_API_KEY
#   REVERBNATION_API_KEY
#   BANDCAMP_CLIENT_ID, BANDCAMP_CLIENT_SECRET
import os
from datetime import datetime

from XR7.ingestion.connectors.base import BaseConnector
from XR7.ingestion.connectors.file_backfill import load_statement_rows

# Maps distributor name → required credential environment variables
_DISTRIBUTOR_ENV_VARS: dict[str, tuple[str, ...]] = {
    "Amuse":          ("AMUSE_API_KEY",),
    "United Masters": ("UNITEDMASTERS_API_KEY",),
    "ONErpm":         ("ONERPM_API_KEY",),
    "Stem":           ("STEM_CLIENT_ID", "STEM_CLIENT_SECRET"),
    "LANDR":          ("LANDR_API_KEY",),
    "Ditto Music":    ("DITTO_API_KEY",),
    "ReverbNation":   ("REVERBNATION_API_KEY",),
    "Bandcamp":       ("BANDCAMP_CLIENT_ID", "BANDCAMP_CLIENT_SECRET"),
    # Legacy / large distributors that also use CSV as primary path
    "DistroKid":      ("DISTROKID_USERNAME", "DISTROKID_PASSWORD"),
    "TuneCore":       ("TUNECORE_API_KEY",),
    "CD Baby":        ("CDBABY_API_KEY",),
}


class DistributorConnector(BaseConnector):
    """
    Connector for a music distributor (small-label / indie-distributor).

    ``connect()`` checks whether the required API credential environment
    variables are set.  ``fetch_historical()`` and ``fetch_recent()`` raise
    ``NotImplementedError`` — use the statement CSV upload workflow until a
    real API integration is built.

    Parameters
    ----------
    config:
        Optional dict of explicit credentials (overrides env-var lookup).
    distributor_name:
        Name of the distributor, e.g. ``"Amuse"``, ``"ONErpm"`` (must match
        a key in ``_DISTRIBUTOR_ENV_VARS``).
    """

    def __init__(self, config: dict, distributor_name: str = "Amuse"):
        super().__init__(config)
        self.distributor_name = distributor_name

    def _required_env_vars(self) -> tuple[str, ...]:
        # All known distributors have explicit entries in _DISTRIBUTOR_ENV_VARS.
        # The fallback is a reasonable convention for unknown names: spaces and
        # hyphens are replaced with underscores and the result is uppercased,
        # e.g. "My Label" → "MY_LABEL_API_KEY".  Distributor names should be
        # plain ASCII strings (no special characters) when using the fallback.
        return _DISTRIBUTOR_ENV_VARS.get(
            self.distributor_name,
            (f"{self.distributor_name.upper().replace(' ', '_')}_API_KEY",),
        )

    def connect(self) -> bool:
        """
        Return ``True`` if all required credential environment variables are
        set, ``False`` otherwise.  Does NOT make a real network call.
        """
        return all(
            self.config.get(v.lower()) or os.environ.get(v, "")
            for v in self._required_env_vars()
        )

    def fetch_historical(
        self,
        artist_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict]:
        rows = load_statement_rows(
            config=self.config,
            source_name=self.distributor_name,
            env_name=f"{self.distributor_name.upper().replace(' ', '_')}_STATEMENT_FILES",
            artist_id=artist_id,
            start=start_date,
            end=end_date,
        )
        if rows:
            return rows
        raise NotImplementedError(
            f"{self.distributor_name} API integration is not yet configured and no statement backfill files "
            f"were provided. Required env vars for API mode: {', '.join(self._required_env_vars())}. "
            f"For file mode, provide config['statement_files'] or "
            f"{self.distributor_name.upper().replace(' ', '_')}_STATEMENT_FILES. "
            f"You can always upload files through POST /artists/{{artist_id}}/statements/upload."
        )

    def fetch_recent(self, artist_id: str, since: datetime) -> list[dict]:
        return self.fetch_historical(artist_id, since, datetime.now(tz=since.tzinfo))

    def normalize(self, raw_data: list[dict]) -> list[dict]:
        normalized = []
        for record in raw_data:
            normalized.append({
                "source": self.distributor_name,
                "event_type": "STREAM",
                "artist_id": record.get("artist_id"),
                "work_id": record.get("work_id"),
                "quantity": record.get("streams", record.get("quantity", 0)),
                "unit_value": record.get("rate", record.get("unit_value", 0.004)),
                "currency": record.get("currency", "USD"),
                "territory": record.get("country", record.get("territory")),
                "timestamp": record.get("timestamp"),
                "platform": self.distributor_name,
            })
        return normalized

    @classmethod
    def supported_distributors(cls) -> list[str]:
        """Return the list of explicitly supported distributor names."""
        return list(_DISTRIBUTOR_ENV_VARS.keys())
