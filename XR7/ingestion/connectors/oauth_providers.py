from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urlencode

import httpx


@dataclass(frozen=True)
class OAuthProviderConfig:
    name: str
    authorize_url: str
    token_url: str
    client_id_env: str
    client_secret_env: str
    default_scopes: tuple[str, ...]


PROVIDER_CONFIGS: dict[str, OAuthProviderConfig] = {
    "spotify": OAuthProviderConfig(
        name="spotify",
        authorize_url="https://accounts.spotify.com/authorize",
        token_url="https://accounts.spotify.com/api/token",
        client_id_env="SPOTIFY_CLIENT_ID",
        client_secret_env="SPOTIFY_CLIENT_SECRET",
        default_scopes=("user-read-email", "user-read-private"),
    ),
    "youtube": OAuthProviderConfig(
        name="youtube",
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        client_id_env="YOUTUBE_OAUTH_CLIENT_ID",
        client_secret_env="YOUTUBE_OAUTH_CLIENT_SECRET",
        default_scopes=("https://www.googleapis.com/auth/youtube.readonly",),
    ),
    "tiktok": OAuthProviderConfig(
        name="tiktok",
        authorize_url="https://www.tiktok.com/v2/auth/authorize/",
        token_url="https://open.tiktokapis.com/v2/oauth/token/",
        client_id_env="TIKTOK_CLIENT_KEY",
        client_secret_env="TIKTOK_CLIENT_SECRET",
        default_scopes=("user.info.basic",),
    ),
}


class OAuthProviderError(RuntimeError):
    """Raised when provider-aware OAuth operations fail."""


class OAuthProviderService:
    """Provider-aware OAuth helper for authorization URL and token operations.

    If provider credentials are not configured, the service returns deterministic
    local fallback payloads so local development and tests can run without
    external API calls.
    """

    def __init__(self, provider: str):
        provider_key = provider.strip().lower()
        self.provider = provider_key
        self.config = PROVIDER_CONFIGS.get(provider_key)

    def _credentials(self) -> tuple[str | None, str | None]:
        if not self.config:
            return None, None
        return os.getenv(self.config.client_id_env), os.getenv(self.config.client_secret_env)

    def configured(self) -> bool:
        client_id, client_secret = self._credentials()
        return bool(client_id and client_secret)

    def default_scopes(self) -> list[str]:
        if not self.config:
            return []
        return list(self.config.default_scopes)

    def build_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        scopes: list[str],
        tenant_id: str,
    ) -> str:
        requested_scopes = scopes or self.default_scopes()

        if not self.config:
            q = {
                "response_type": "code",
                "client_id": "configure-provider-client-id",
                "redirect_uri": redirect_uri,
                "state": state,
                "scope": " ".join(requested_scopes),
                "tenant": tenant_id,
            }
            return f"https://auth.{self.provider}.example/oauth2/authorize?{urlencode(q)}"

        client_id, _ = self._credentials()
        q = {
            "response_type": "code",
            "client_id": client_id or "configure-provider-client-id",
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": " ".join(requested_scopes),
        }
        if self.provider == "youtube":
            q["access_type"] = "offline"
            q["include_granted_scopes"] = "true"
            q["prompt"] = "consent"
        if self.provider == "tiktok":
            q["disable_auto_auth"] = "0"
        if tenant_id:
            q["tenant"] = tenant_id
        return f"{self.config.authorize_url}?{urlencode(q)}"

    def exchange_code(
        self,
        code: str,
        redirect_uri: str,
        tenant_id: str,
        fallback_scopes: list[str],
    ) -> dict[str, Any]:
        if not self.config or not self.configured():
            # Local fallback so tests/dev do not require live provider credentials.
            return {
                "access_token": f"atk_{secrets.token_hex(16)}",
                "refresh_token": f"rtk_{secrets.token_hex(16)}",
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": " ".join(fallback_scopes),
                "tenant_id": tenant_id,
                "simulated": True,
            }

        client_id, client_secret = self._credentials()
        if not client_id or not client_secret:
            raise OAuthProviderError("OAuth provider credentials are missing")

        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        data = self._post_token(payload)
        return {
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "token_type": data.get("token_type") or "Bearer",
            "expires_in": int(data.get("expires_in") or 3600),
            "scope": data.get("scope") or " ".join(fallback_scopes),
            "tenant_id": tenant_id,
            "simulated": False,
        }

    def refresh_token(self, refresh_token: str, fallback_expires_in: int = 3600) -> dict[str, Any]:
        if not self.config or not self.configured():
            return {
                "access_token": f"atk_{secrets.token_hex(16)}",
                "refresh_token": f"rtk_{secrets.token_hex(16)}",
                "token_type": "Bearer",
                "expires_in": fallback_expires_in,
                "simulated": True,
            }

        client_id, client_secret = self._credentials()
        if not client_id or not client_secret:
            raise OAuthProviderError("OAuth provider credentials are missing")

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        data = self._post_token(payload)
        return {
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token") or refresh_token,
            "token_type": data.get("token_type") or "Bearer",
            "expires_in": int(data.get("expires_in") or fallback_expires_in),
            "simulated": False,
        }

    def _post_token(self, payload: dict[str, str]) -> dict[str, Any]:
        if not self.config:
            raise OAuthProviderError("Unsupported OAuth provider")
        try:
            with httpx.Client(timeout=12.0) as client:
                response = client.post(
                    self.config.token_url,
                    data=payload,
                    headers={"Accept": "application/json"},
                )
            response.raise_for_status()
        except Exception as exc:  # noqa: BLE001
            raise OAuthProviderError(f"Token request failed for provider '{self.provider}': {exc}") from exc

        data = response.json()
        if not isinstance(data, dict):
            raise OAuthProviderError("Token response payload is not a JSON object")
        if "access_token" not in data:
            raise OAuthProviderError("Token response missing access_token")
        return data


def parse_scope_string(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.replace(",", " ").split() if part.strip()]


def expires_at_from_seconds(seconds: int | None, *, now: datetime | None = None) -> datetime | None:
    if seconds is None:
        return None
    base = now or datetime.now(timezone.utc)
    return base + timedelta(seconds=max(0, int(seconds)))
