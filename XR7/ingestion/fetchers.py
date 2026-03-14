from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

from XR7.ingestion.universal_schema import to_universal_royalty_event


@dataclass
class FetchBundle:
    historical_statements: list[dict[str, Any]]
    catalog_metadata: list[dict[str, Any]]
    registrations: list[dict[str, Any]]
    usage_data: list[dict[str, Any]]
    normalized_events: list[dict[str, Any]]


class BaseDataFetcher:
    source_type = "generic"
    source_name = "generic"

    api_base_env = ""
    api_key_env = ""

    def _configured(self) -> bool:
        if not self.api_base_env or not self.api_key_env:
            return False
        return bool(os.getenv(self.api_base_env) and os.getenv(self.api_key_env))

    def _fetch_json(self, path: str) -> list[dict[str, Any]]:
        if not self._configured():
            return []
        base = os.getenv(self.api_base_env, "").rstrip("/")
        api_key = os.getenv(self.api_key_env, "")
        if not base or not api_key:
            return []
        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(f"{base}/{path.lstrip('/')}", headers={"Authorization": f"Bearer {api_key}"})
            resp.raise_for_status()
            payload = resp.json()
            if isinstance(payload, list):
                return payload
            if isinstance(payload, dict) and isinstance(payload.get("items"), list):
                return payload["items"]
        except Exception:  # noqa: BLE001
            return []
        return []

    def pull_historical_statements(self, artist_id: str, start: datetime | None = None, end: datetime | None = None) -> list[dict[str, Any]]:
        return [
            {
                "artist_id": artist_id,
                "source": self.source_name,
                "period": f"{(start.isoformat() if start else 'all')}-{(end.isoformat() if end else 'latest')}",
                "amount": 0.0,
                "quantity": 0,
            }
        ]

    def pull_catalog_metadata(self, artist_id: str) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": self.source_name, "work_title": "Unknown Work"}]

    def pull_registrations(self, artist_id: str) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": self.source_name, "registration_id": "pending"}]

    def pull_usage_data(self, artist_id: str, since: datetime | None = None) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": self.source_name, "usage_count": 0, "since": since.isoformat() if since else None}]

    def normalize_to_universal_schema(
        self,
        artist_id: str,
        historical_statements: list[dict[str, Any]],
        usage_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for idx, row in enumerate(historical_statements):
            events.append(
                to_universal_royalty_event(
                    artist_id=artist_id,
                    source_type=self.source_type,
                    source_name=self.source_name,
                    record_type="STATEMENT",
                    event_type="ROYALTY_EVENT",
                    amount=float(row.get("amount", 0.0)),
                    quantity=float(row.get("quantity", 0.0)),
                    source_ref=f"statement-{idx}",
                    metadata=row,
                )
            )
        for idx, row in enumerate(usage_data):
            events.append(
                to_universal_royalty_event(
                    artist_id=artist_id,
                    source_type=self.source_type,
                    source_name=self.source_name,
                    record_type="USAGE",
                    event_type="USAGE_EVENT",
                    amount=0.0,
                    quantity=float(row.get("usage_count", 0.0)),
                    source_ref=f"usage-{idx}",
                    metadata=row,
                )
            )
        return events

    def fetch_all(self, artist_id: str, start: datetime | None = None, end: datetime | None = None) -> FetchBundle:
        historical = self.pull_historical_statements(artist_id, start=start, end=end)
        catalog = self.pull_catalog_metadata(artist_id)
        registrations = self.pull_registrations(artist_id)
        usage = self.pull_usage_data(artist_id, since=start)
        normalized = self.normalize_to_universal_schema(artist_id, historical, usage)
        return FetchBundle(
            historical_statements=historical,
            catalog_metadata=catalog,
            registrations=registrations,
            usage_data=usage,
            normalized_events=normalized,
        )


class DistributorFetcher(BaseDataFetcher):
    source_type = "distributor"
    source_name = "distributor"
    api_base_env = "DISTRIBUTOR_API_BASE_URL"
    api_key_env = "DISTRIBUTOR_API_KEY"

    def pull_historical_statements(self, artist_id: str, start: datetime | None = None, end: datetime | None = None) -> list[dict[str, Any]]:
        live = self._fetch_json(f"artists/{artist_id}/statements")
        if live:
            return live
        return [
            {
                "artist_id": artist_id,
                "source": "distrokid",
                "period": "2024-01",
                "amount": 152.44,
                "quantity": 40432,
                "platform": "Spotify",
            }
        ]

    def pull_catalog_metadata(self, artist_id: str) -> list[dict[str, Any]]:
        live = self._fetch_json(f"artists/{artist_id}/catalog")
        if live:
            return live
        return [{"artist_id": artist_id, "source": "distrokid", "work_title": "Demo Track", "isrc": "USXXX1234567"}]

    def pull_registrations(self, artist_id: str) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "distributor", "registration_id": "dist-reg-1", "work_id": "work-1"}]

    def pull_usage_data(self, artist_id: str, since: datetime | None = None) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "distributor", "usage_count": 40432, "since": since.isoformat() if since else None}]


class PROFetcher(BaseDataFetcher):
    source_type = "pro"
    source_name = "pro"
    api_base_env = "PRO_API_BASE_URL"
    api_key_env = "PRO_API_KEY"

    def pull_historical_statements(self, artist_id: str, start: datetime | None = None, end: datetime | None = None) -> list[dict[str, Any]]:
        live = self._fetch_json(f"artists/{artist_id}/royalties")
        if live:
            return live
        return [{"artist_id": artist_id, "source": "ascap", "period": "2024-Q1", "amount": 88.10, "quantity": 1200}]

    def pull_catalog_metadata(self, artist_id: str) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "pro", "work_title": "Demo Track", "ipi": "00012345678"}]

    def pull_registrations(self, artist_id: str) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "pro", "registration_id": "iswc:T-000.000.001-0", "work_id": "work-1"}]

    def pull_usage_data(self, artist_id: str, since: datetime | None = None) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "pro", "usage_count": 1200, "since": since.isoformat() if since else None}]


class MLCFetcher(BaseDataFetcher):
    source_type = "mlc"
    source_name = "mlc"
    api_base_env = "MLC_API_BASE_URL"
    api_key_env = "MLC_API_KEY"

    def pull_historical_statements(self, artist_id: str, start: datetime | None = None, end: datetime | None = None) -> list[dict[str, Any]]:
        live = self._fetch_json(f"artists/{artist_id}/mechanicals")
        if live:
            return live
        return [{"artist_id": artist_id, "source": "mlc", "period": "2024-01", "amount": 44.91, "quantity": 6400}]

    def pull_catalog_metadata(self, artist_id: str) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "mlc", "work_title": "Mechanical Demo", "isrc": "USYYY1234567"}]

    def pull_registrations(self, artist_id: str) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "mlc", "registration_id": "mlc-reg-1", "work_id": "work-2"}]

    def pull_usage_data(self, artist_id: str, since: datetime | None = None) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "mlc", "usage_count": 6400, "since": since.isoformat() if since else None}]


class YouTubeContentIDFetcher(BaseDataFetcher):
    source_type = "platform"
    source_name = "youtube_content_id"
    api_base_env = "YOUTUBE_CONTENT_ID_API_BASE_URL"
    api_key_env = "YOUTUBE_API_KEY"

    def pull_historical_statements(self, artist_id: str, start: datetime | None = None, end: datetime | None = None) -> list[dict[str, Any]]:
        live = self._fetch_json(f"artists/{artist_id}/claims")
        if live:
            return live
        return [{"artist_id": artist_id, "source": "youtube_content_id", "period": "2024-01", "amount": 31.22, "quantity": 8700}]

    def pull_catalog_metadata(self, artist_id: str) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "youtube", "work_title": "UGC Demo", "asset_id": "yt-asset-1"}]

    def pull_registrations(self, artist_id: str) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "youtube", "registration_id": "content-id-asset-1", "work_id": "work-3"}]

    def pull_usage_data(self, artist_id: str, since: datetime | None = None) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "platform", "usage_count": 8700, "since": since.isoformat() if since else None}]


class SocialPlatformUsageFetcher(BaseDataFetcher):
    source_type = "social"
    source_name = "social_platform"
    api_base_env = "SOCIAL_PLATFORM_API_BASE_URL"
    api_key_env = "SOCIAL_PLATFORM_API_KEY"

    def pull_historical_statements(self, artist_id: str, start: datetime | None = None, end: datetime | None = None) -> list[dict[str, Any]]:
        live = self._fetch_json(f"artists/{artist_id}/social/earnings")
        if live:
            return live
        return [{"artist_id": artist_id, "source": "tiktok", "period": "2024-01", "amount": 11.02, "quantity": 5300}]

    def pull_catalog_metadata(self, artist_id: str) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "social", "work_title": "Shortform Snippet", "clip_id": "clip-1"}]

    def pull_registrations(self, artist_id: str) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "social", "registration_id": "social-reg-1", "work_id": "work-4"}]

    def pull_usage_data(self, artist_id: str, since: datetime | None = None) -> list[dict[str, Any]]:
        return [{"artist_id": artist_id, "source": "platform", "usage_count": 5300, "since": since.isoformat() if since else None}]


def get_fetcher(integration: str) -> BaseDataFetcher:
    key = integration.strip().lower()
    mapping: dict[str, BaseDataFetcher] = {
        "distributor": DistributorFetcher(),
        "pro": PROFetcher(),
        "mlc": MLCFetcher(),
        "youtube": YouTubeContentIDFetcher(),
        "youtube_content_id": YouTubeContentIDFetcher(),
        "social": SocialPlatformUsageFetcher(),
    }
    if key not in mapping:
        raise ValueError(f"Unsupported integration '{integration}'")
    return mapping[key]
