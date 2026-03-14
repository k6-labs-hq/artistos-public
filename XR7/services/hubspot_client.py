from __future__ import annotations

import json
import time
from typing import Any
from urllib import error, request

from xr7_common.logging import get_logger
from xr7_common.settings import settings

logger = get_logger(__name__)


class HubSpotClient:
    """Lightweight HubSpot CRM client with retries and graceful failure semantics."""

    def __init__(self) -> None:
        self.enabled = bool(settings.hubspot_enabled and (settings.hubspot_private_app_token or settings.hubspot_api_key))
        self.base_url = settings.hubspot_base_url.rstrip("/")
        self._token = settings.hubspot_private_app_token
        self._api_key = settings.hubspot_api_key

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _url(self, path: str) -> str:
        url = f"{self.base_url}{path}"
        if self._api_key and not self._token:
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}hapikey={self._api_key}"
        return url

    def _request(self, method: str, path: str, payload: dict | None = None, retries: int = 3) -> dict:
        if not self.enabled:
            return {"ok": False, "disabled": True}

        body = json.dumps(payload or {}).encode("utf-8")
        url = self._url(path)

        for attempt in range(retries):
            req = request.Request(url=url, method=method.upper(), headers=self._headers(), data=body)
            try:
                with request.urlopen(req, timeout=10) as resp:  # noqa: S310
                    raw = resp.read().decode("utf-8")
                    return {"ok": True, "status": resp.status, "data": json.loads(raw) if raw else {}}
            except error.HTTPError as exc:
                status = int(exc.code or 0)
                payload_text = exc.read().decode("utf-8", errors="ignore") if hasattr(exc, "read") else ""
                if status in {429, 500, 502, 503, 504} and attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.error(
                    "HubSpot request failed",
                    extra={"method": method, "path": path, "status": status, "response": payload_text[:1000]},
                )
                return {"ok": False, "status": status, "error": payload_text}
            except Exception as exc:  # noqa: BLE001
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.error("HubSpot request exception", extra={"method": method, "path": path, "error": str(exc)})
                return {"ok": False, "error": str(exc)}

        return {"ok": False, "error": "request_failed"}

    def upsert_contact(self, *, email: str | None, name: str | None, properties: dict[str, Any]) -> dict:
        props = dict(properties)
        if email:
            props["email"] = email
        if name:
            props["firstname"] = name
        return self._request("POST", "/crm/v3/objects/contacts", {"properties": props})

    def upsert_deal(self, *, artist_id: str, properties: dict[str, Any]) -> dict:
        props = dict(properties)
        props.setdefault("artist_id", artist_id)
        return self._request("POST", "/crm/v3/objects/deals", {"properties": props})

    def link_contact_to_deal(self, *, contact_id: str, deal_id: str) -> dict:
        path = f"/crm/v3/objects/deals/{deal_id}/associations/contacts/{contact_id}/3"
        return self._request("PUT", path, payload={})
