from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx


@dataclass(frozen=True)
class XR7ProviderConfig:
    provider: str
    base_url: str
    catalog_path: str | None
    usage_path: str | None
    monetization_path: str | None
    performance_path: str | None
    fingerprint_path: str | None
    max_rps: float


PROVIDER_CONFIGS: dict[str, XR7ProviderConfig] = {
    "spotify": XR7ProviderConfig(
        provider="spotify",
        base_url="https://api.spotify.com/v1",
        catalog_path="/me/tracks",
        usage_path="/me/player/recently-played",
        monetization_path=None,
        performance_path=None,
        fingerprint_path=None,
        max_rps=4.0,
    ),
    "apple_music": XR7ProviderConfig(
        provider="apple_music",
        base_url="https://api.music.apple.com/v1",
        catalog_path="/catalog/us/songs",
        usage_path=None,
        monetization_path=None,
        performance_path=None,
        fingerprint_path=None,
        max_rps=2.0,
    ),
    "amazon_music": XR7ProviderConfig(
        provider="amazon_music",
        base_url="https://api.amazonmusic.com/v1",
        catalog_path="/catalog/tracks",
        usage_path="/analytics/usage",
        monetization_path="/analytics/royalties",
        performance_path="/analytics/performance",
        fingerprint_path=None,
        max_rps=2.0,
    ),
    "youtube": XR7ProviderConfig(
        provider="youtube",
        base_url="https://www.googleapis.com/youtube/v3",
        catalog_path="/videos",
        usage_path="/search",
        monetization_path=None,
        performance_path="/videos",
        fingerprint_path=None,
        max_rps=8.0,
    ),
    "tiktok": XR7ProviderConfig(
        provider="tiktok",
        base_url="https://open.tiktokapis.com/v2",
        catalog_path="/music/track/list/",
        usage_path="/research/video/query/",
        monetization_path=None,
        performance_path="/research/video/query/",
        fingerprint_path=None,
        max_rps=1.0,
    ),
    "soundcloud": XR7ProviderConfig(
        provider="soundcloud",
        base_url="https://api.soundcloud.com",
        catalog_path="/me/tracks",
        usage_path="/me/activities",
        monetization_path=None,
        performance_path="/me/insights",
        fingerprint_path=None,
        max_rps=3.0,
    ),
    "meta_rights_manager": XR7ProviderConfig(
        provider="meta_rights_manager",
        base_url="https://graph.facebook.com/v20.0",
        catalog_path="/me/owned_media",
        usage_path="/me/owned_media",
        monetization_path="/me/insights",
        performance_path="/me/insights",
        fingerprint_path="/me/owned_media",
        max_rps=5.0,
    ),
    "bmat": XR7ProviderConfig(
        provider="bmat",
        base_url="https://api.bmat.com/v1",
        catalog_path="/catalog/assets",
        usage_path="/detections",
        monetization_path=None,
        performance_path="/detections",
        fingerprint_path="/fingerprints",
        max_rps=2.0,
    ),
    "soundmouse": XR7ProviderConfig(
        provider="soundmouse",
        base_url="https://api.soundmouse.com/v1",
        catalog_path="/works",
        usage_path="/performances",
        monetization_path=None,
        performance_path="/performances",
        fingerprint_path="/matches",
        max_rps=2.0,
    ),
}


class XR7APIClientError(RuntimeError):
    pass


class XR7RateLimitScheduler:
    def __init__(self):
        self._next_allowed: dict[str, datetime] = {}

    def wait_if_needed(self, provider: str, max_rps: float) -> None:
        now = datetime.now(timezone.utc)
        next_allowed = self._next_allowed.get(provider)
        if next_allowed and next_allowed > now:
            sleep_seconds = (next_allowed - now).total_seconds()
            if sleep_seconds > 0:
                time.sleep(sleep_seconds)
        interval = 1.0 / max(max_rps, 0.1)
        self._next_allowed[provider] = datetime.now(timezone.utc) + timedelta(seconds=interval)


class XR7PlatformAPIClient:
    def __init__(self, provider: str, token: str, timeout_seconds: float = 20.0):
        provider_key = provider.strip().lower()
        cfg = PROVIDER_CONFIGS.get(provider_key)
        if not cfg:
            raise XR7APIClientError(f"unsupported provider '{provider}'")
        self.provider = provider_key
        self.config = cfg
        self.token = token
        self.timeout_seconds = timeout_seconds

    def fetch_all(
        self,
        scheduler: XR7RateLimitScheduler,
        *,
        since: datetime | None,
        until: datetime | None,
    ) -> dict[str, list[dict[str, Any]]]:
        return {
            "catalog": self._fetch_optional(
                self.config.catalog_path, scheduler, since=since, until=until
            ),
            "usage": self._fetch_optional(
                self.config.usage_path, scheduler, since=since, until=until
            ),
            "monetization": self._fetch_optional(
                self.config.monetization_path, scheduler, since=since, until=until
            ),
            "performance": self._fetch_optional(
                self.config.performance_path, scheduler, since=since, until=until
            ),
            "fingerprints": self._fetch_optional(
                self.config.fingerprint_path, scheduler, since=since, until=until
            ),
        }

    def _fetch_optional(
        self,
        path: str | None,
        scheduler: XR7RateLimitScheduler,
        *,
        since: datetime | None,
        until: datetime | None,
    ) -> list[dict[str, Any]]:
        if not path:
            return []
        payload = self._request_json(path, scheduler, since=since, until=until)
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        if isinstance(payload, dict):
            for key in ("items", "data", "results", "rows"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [row for row in value if isinstance(row, dict)]
            return [payload]
        return []

    def _request_json(
        self,
        path: str,
        scheduler: XR7RateLimitScheduler,
        *,
        since: datetime | None,
        until: datetime | None,
    ) -> Any:
        params: dict[str, str] = {}
        if since is not None:
            params["since"] = since.isoformat()
        if until is not None:
            params["until"] = until.isoformat()

        url = f"{self.config.base_url}{path}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

        last_error: Exception | None = None
        for attempt in range(1, 4):
            scheduler.wait_if_needed(self.provider, self.config.max_rps)
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    resp = client.get(url, headers=headers, params=params)
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", "1") or "1")
                    time.sleep(max(1, retry_after))
                    continue
                if 500 <= resp.status_code < 600:
                    time.sleep(2 ** (attempt - 1))
                    continue
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                time.sleep(2 ** (attempt - 1))

        raise XR7APIClientError(f"request failed for {self.provider}{path}: {last_error}")
