from __future__ import annotations

from XR7.services.hubspot_client import HubSpotClient


def test_hubspot_client_disabled_without_config(monkeypatch):
    monkeypatch.setenv("HUBSPOT_ENABLED", "0")
    c = HubSpotClient()
    assert c.enabled is False


def test_hubspot_request_returns_disabled_when_not_enabled(monkeypatch):
    monkeypatch.setenv("HUBSPOT_ENABLED", "0")
    c = HubSpotClient()
    result = c.upsert_contact(email="a@example.com", name="A", properties={"source": "test"})
    assert result.get("disabled") is True
    assert result.get("ok") is False
