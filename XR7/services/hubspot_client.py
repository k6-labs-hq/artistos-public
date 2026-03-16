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
                    extra={
                        "method": method,
                        "path": path,
                        "status": status,
                        "response": payload_text[:1000],
                        "payload_keys": sorted((payload or {}).keys()),
                    },
                )
                return {"ok": False, "status": status, "error": payload_text}
            except Exception as exc:  # noqa: BLE001
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.error("HubSpot request exception", extra={"method": method, "path": path, "error": str(exc)})
                return {"ok": False, "error": str(exc)}

        return {"ok": False, "error": "request_failed"}

    def _search_object(self, object_type: str, filters: list[dict[str, Any]], *, limit: int = 1) -> dict:
        payload = {
            "filterGroups": [{"filters": filters}],
            "limit": limit,
            "properties": ["email", "firstname", "lastname", "name", "dealname", "xr7_artist_id"],
        }
        return self._request("POST", f"/crm/v3/objects/{object_type}/search", payload)

    def _create_object(self, object_type: str, properties: dict[str, Any]) -> dict:
        return self._request("POST", f"/crm/v3/objects/{object_type}", {"properties": properties})

    def _update_object(self, object_type: str, object_id: str, properties: dict[str, Any]) -> dict:
        return self._request("PATCH", f"/crm/v3/objects/{object_type}/{object_id}", {"properties": properties})

    def _search_first_id(self, object_type: str, filters: list[dict[str, Any]]) -> str | None:
        result = self._search_object(object_type, filters)
        if not result.get("ok"):
            return None
        rows = ((result.get("data") or {}).get("results") or [])
        if not rows:
            return None
        row_id = rows[0].get("id")
        return str(row_id) if row_id else None

    def upsert_contact(self, *, email: str | None, name: str | None, properties: dict[str, Any]) -> dict:
        props = dict(properties)
        if email:
            props["email"] = email
        if name:
            props.setdefault("firstname", name)

        contact_id: str | None = None
        if email:
            contact_id = self._search_first_id(
                "contacts",
                [{"propertyName": "email", "operator": "EQ", "value": email}],
            )

        if not contact_id and props.get("xr7_artist_id"):
            contact_id = self._search_first_id(
                "contacts",
                [{"propertyName": "xr7_artist_id", "operator": "EQ", "value": str(props["xr7_artist_id"])}],
            )

        if contact_id:
            updated = self._update_object("contacts", contact_id, props)
            updated["object_id"] = contact_id
            updated["upsert_action"] = "updated"
            return updated

        created = self._create_object("contacts", props)
        created_id = ((created.get("data") or {}).get("id")) if created.get("ok") else None
        if created_id:
            created["object_id"] = str(created_id)
        created["upsert_action"] = "created"
        return created

    def upsert_company(self, *, name: str, properties: dict[str, Any]) -> dict:
        props = dict(properties)
        props["name"] = name

        company_id = self._search_first_id(
            "companies",
            [{"propertyName": "name", "operator": "EQ", "value": name}],
        )
        if not company_id and props.get("xr7_artist_id"):
            company_id = self._search_first_id(
                "companies",
                [{"propertyName": "xr7_artist_id", "operator": "EQ", "value": str(props["xr7_artist_id"])}],
            )

        if company_id:
            updated = self._update_object("companies", company_id, props)
            updated["object_id"] = company_id
            updated["upsert_action"] = "updated"
            return updated

        created = self._create_object("companies", props)
        created_id = ((created.get("data") or {}).get("id")) if created.get("ok") else None
        if created_id:
            created["object_id"] = str(created_id)
        created["upsert_action"] = "created"
        return created

    def upsert_deal(self, *, artist_id: str, properties: dict[str, Any]) -> dict:
        props = dict(properties)
        props.setdefault("xr7_artist_id", artist_id)

        deal_id = self._search_first_id(
            "deals",
            [{"propertyName": "xr7_artist_id", "operator": "EQ", "value": artist_id}],
        )
        if not deal_id and props.get("dealname"):
            deal_id = self._search_first_id(
                "deals",
                [{"propertyName": "dealname", "operator": "EQ", "value": str(props["dealname"])}],
            )

        if deal_id:
            updated = self._update_object("deals", deal_id, props)
            updated["object_id"] = deal_id
            updated["upsert_action"] = "updated"
            return updated

        created = self._create_object("deals", props)
        created_id = ((created.get("data") or {}).get("id")) if created.get("ok") else None
        if created_id:
            created["object_id"] = str(created_id)
        created["upsert_action"] = "created"
        return created

    def link_company_to_deal(self, *, company_id: str, deal_id: str) -> dict:
        path = f"/crm/v3/objects/deals/{deal_id}/associations/companies/{company_id}/5"
        return self._request("PUT", path, payload={})

    def link_contact_to_deal(self, *, contact_id: str, deal_id: str) -> dict:
        path = f"/crm/v3/objects/deals/{deal_id}/associations/contacts/{contact_id}/3"
        return self._request("PUT", path, payload={})
