from __future__ import annotations

from fastapi.testclient import TestClient

from XR7.api.app import app


client = TestClient(app)


def _headers(role: str | None = None, *, key: str = "org-secret") -> dict[str, str]:
    h = {"X-Org-Key": key, "X-Org-Actor": "partner@xr7.test"}
    if role is not None:
        h["X-Org-Role"] = role
    return h


def test_b2b_dashboard_requires_valid_key(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get("/b2b/org/org-1/dashboard", headers=_headers("publisher_admin", key="wrong"))
    assert resp.status_code == 401


def test_b2b_dashboard_requires_role(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get("/b2b/org/org-1/dashboard", headers=_headers(None))
    assert resp.status_code == 403


def test_b2b_dashboard_allows_viewer(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get("/b2b/org/org-1/dashboard", headers=_headers("viewer"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "viewer"
    assert data["actor"] == "partner@xr7.test"


def test_bulk_onboard_blocks_viewer(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.post(
        "/b2b/org/org-1/artists/bulk-onboard",
        headers=_headers("viewer"),
        json={"artists": [{"name": "A"}]},
    )
    assert resp.status_code == 403


def test_bulk_onboard_allows_manager(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.post(
        "/b2b/org/org-1/artists/bulk-onboard",
        headers=_headers("manager"),
        json={"artists": [{"name": "A"}, {"name": "B"}]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["onboarded"] == 2
    assert data["role"] == "manager"
