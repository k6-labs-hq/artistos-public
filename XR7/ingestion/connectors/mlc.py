import os
from datetime import datetime

import httpx

from XR7.ingestion.connectors.base import BaseConnector


class MLCConnector(BaseConnector):
    """
    Feed connector for Mechanical Licensing Collective (MLC) royalty data.

    This connector fetches mechanical royalty records from an HTTP JSON feed.
    The exact endpoint can vary by account/setup, so it is configurable via
    ``config`` and environment variables.

    Environment variables
    ---------------------
    - ``MLC_API_KEY``
    - ``MLC_API_BASE_URL`` (optional; default: ``https://api.themlc.com``)
    """

    def __init__(self, config: dict, http_client: httpx.Client | None = None):
        super().__init__(config)
        self.api_key = config.get("api_key") or os.environ.get("MLC_API_KEY", "")
        self.base_url = (
            config.get("base_url")
            or os.environ.get("MLC_API_BASE_URL")
            or "https://api.themlc.com"
        ).rstrip("/")
        self.royalties_endpoint = config.get("royalties_endpoint", "/v1/royalties")
        self.timeout_seconds = float(config.get("timeout_seconds", 15.0))
        self._http_client = http_client

    def connect(self) -> bool:
        """
        Return ``True`` when required credentials are configured.

        This method validates local configuration only and does not perform
        a network call.
        """
        return bool(self.api_key and self.base_url)

    def fetch_historical(self, artist_id: str, start_date: datetime, end_date: datetime) -> list[dict]:
        if not self.connect():
            raise RuntimeError(
                "MLC connector is missing credentials. Set MLC_API_KEY "
                "(and optionally MLC_API_BASE_URL)."
            )
        params = {
            "artist_id": artist_id,
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
        }
        return self._fetch_entries(params)

    def fetch_recent(self, artist_id: str, since: datetime) -> list[dict]:
        if not self.connect():
            raise RuntimeError(
                "MLC connector is missing credentials. Set MLC_API_KEY "
                "(and optionally MLC_API_BASE_URL)."
            )
        params = {
            "artist_id": artist_id,
            "since": since.date().isoformat(),
        }
        return self._fetch_entries(params)

    def _fetch_entries(self, params: dict[str, str]) -> list[dict]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        url = f"{self.base_url}{self.royalties_endpoint}"

        if self._http_client is not None:
            response = self._http_client.get(url, params=params, headers=headers)
        else:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.get(url, params=params, headers=headers)

        if response.status_code >= 400:
            raise RuntimeError(
                f"MLC feed request failed ({response.status_code}): {response.text[:300]}"
            )

        payload = response.json()
        rows = self._extract_rows(payload)
        for row in rows:
            row.setdefault("source", "MLC")
            row.setdefault("artist_id", params.get("artist_id"))
        return rows

    @staticmethod
    def _extract_rows(payload: object) -> list[dict]:
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        if isinstance(payload, dict):
            for key in ("data", "results", "records", "items", "royalties"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [row for row in value if isinstance(row, dict)]
        return []

    @staticmethod
    def _to_float(value: object, default: float = 0.0) -> float:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.replace("$", "").replace(",", "").strip()
            if cleaned == "":
                return default
            try:
                return float(cleaned)
            except ValueError:
                return default
        return default

    @staticmethod
    def _to_int(value: object, default: int = 0) -> int:
        if value is None:
            return default
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            cleaned = value.replace(",", "").strip()
            if cleaned == "":
                return default
            try:
                return int(float(cleaned))
            except ValueError:
                return default
        return default

    def normalize(self, raw_data: list[dict]) -> list[dict]:
        normalized = []
        for record in raw_data:
            quantity = self._to_int(
                record.get("quantity", record.get("units", record.get("streams", 0))),
                default=0,
            )
            amount = self._to_float(
                record.get("amount", record.get("royalty_amount", record.get("total", 0.0))),
                default=0.0,
            )
            unit_value = self._to_float(record.get("unit_value", record.get("rate")), default=0.0)
            if unit_value == 0.0 and quantity > 0:
                unit_value = amount / quantity

            normalized.append({
                "source": "MLC",
                "event_type": record.get("event_type", "MECHANICAL"),
                "artist_id": record.get("artist_id"),
                "work_id": record.get("work_id", record.get("iswc", record.get("isrc"))),
                "quantity": quantity,
                "unit_value": unit_value,
                "currency": record.get("currency", "USD"),
                "territory": record.get("territory", record.get("country")),
                "timestamp": record.get("timestamp", record.get("statement_date")),
                "platform": "MLC",
            })
        return normalized
