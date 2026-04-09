from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from XR7.ingestion.connectors.base import IngestionConnector
from xr7_common.logging import get_logger

logger = get_logger(__name__)


class SoundExchangeMLCConnector(IngestionConnector):
    name = "soundexchange_mlc"

    def __init__(self, config: dict | None = None):
        super().__init__(config=config or {})
        self.soundexchange_key = os.environ.get("SOUNDEXCHANGE_API_KEY", "")
        self.mlc_key = os.environ.get("MLC_API_KEY", "")
        self.simulated = not (self.soundexchange_key and self.mlc_key)

    async def fetch_royalty_statements(
        self, artist_id: str, years_back: int = 10
    ) -> list[dict[str, Any]]:
        if self.simulated:
            return [
                {
                    "artist_id": artist_id,
                    "source_type": "mlc",
                    "source_name": "MLC",
                    "record_type": "ROYALTY",
                    "event_type": "MECHANICAL",
                    "amount": 1234.56,
                    "currency": "USD",
                    "work_id": "work-mlc-1",
                    "statement_period": f"{datetime.now(timezone.utc).year - 1}",
                    "metadata_json": '{"mode":"simulated"}',
                }
            ]
        return []

    async def detect_unreported_uses(self, catalog_isrcs: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "type": "unreported_soundexchange_use",
                "isrc": isrc,
                "estimated_recoverable": 320.0,
            }
            for isrc in catalog_isrcs[:5]
        ]

    async def auto_reconcile_with_existing_statements(
        self, uploaded_csvs: list[dict[str, Any]]
    ) -> dict[str, Any]:
        return {
            "rows_checked": len(uploaded_csvs),
            "matched": max(0, len(uploaded_csvs) - 1),
            "mode": "simulated",
        }
