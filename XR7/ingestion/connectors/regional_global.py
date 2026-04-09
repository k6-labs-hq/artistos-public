from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from XR7.ingestion.connectors.base import IngestionConnector


class RegionalGlobalConnector(IngestionConnector):
    name = "regional_global"

    def __init__(self, config: dict | None = None):
        super().__init__(config=config or {})
        self.simulated = os.environ.get("XR7_REGIONAL_GLOBAL_SIMULATED", "1").strip().lower() in {
            "1",
            "true",
            "yes",
        }

    async def fetch_statements(
        self, artist_id: str, genre: str, territory: str
    ) -> list[dict[str, Any]]:
        return [
            {
                "artist_id": artist_id,
                "source_name": f"regional-{territory.lower()}",
                "record_type": "ROYALTY",
                "event_type": "STREAM",
                "amount": 888.0,
                "currency": "USD",
                "territory": territory,
                "metadata_json": f'{{"genre":"{genre}","mode":"simulated"}}',
                "ingested_at": datetime.now(timezone.utc).isoformat(),
            }
        ]

    async def auto_detect_genre_specific_anomalies(
        self, artist_id: str, genre: str, territory: str
    ) -> list[dict[str, Any]]:
        genre_l = genre.lower()
        if "latin" in genre_l:
            subtype = "latin_sync_drift"
        elif "k-pop" in genre_l or "kpop" in genre_l:
            subtype = "kpop_multi_territory_split"
        else:
            subtype = "regional_reporting_gap"
        return [
            {
                "artist_id": artist_id,
                "territory": territory,
                "genre": genre,
                "subtype": subtype,
                "estimated_recoverable": 1450.0,
            }
        ]
