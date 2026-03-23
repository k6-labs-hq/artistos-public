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


# ---------------------------------------------------------------------------
# PARTNER-301 — Portfolio and legal export authorization matrix
# ---------------------------------------------------------------------------

def test_portfolio_export_blocks_unknown_role(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get("/management/org-1/portfolio/export", headers=_headers("viewer"))
    assert resp.status_code == 403


def test_portfolio_export_blocks_missing_role(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get("/management/org-1/portfolio/export", headers=_headers(None))
    assert resp.status_code == 403


def test_portfolio_export_blocks_wrong_key(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get(
        "/management/org-1/portfolio/export",
        headers=_headers("org_admin", key="wrong"),
    )
    assert resp.status_code == 401


def test_portfolio_export_allows_org_admin(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get("/management/org-1/portfolio/export", headers=_headers("org_admin"))
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    lines = resp.text.strip().splitlines()
    assert lines[0].startswith("artist_id")


def test_portfolio_export_allows_org_analyst(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get("/management/org-1/portfolio/export", headers=_headers("org_analyst"))
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]


def test_portfolio_export_allows_publisher_admin(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get("/management/org-1/portfolio/export", headers=_headers("publisher_admin"))
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]


def test_legal_export_blocks_org_analyst(monkeypatch):
    """org_analyst may export portfolio but NOT the attorney legal packet."""
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get("/management/org-1/legal/export", headers=_headers("org_analyst"))
    assert resp.status_code == 403


def test_legal_export_allows_attorney(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get("/management/org-1/legal/export", headers=_headers("attorney"))
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    lines = resp.text.strip().splitlines()
    assert lines[0].startswith("claim_id")


def test_legal_export_allows_org_admin(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get("/management/org-1/legal/export", headers=_headers("org_admin"))
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]


def test_legal_export_content_disposition(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    resp = client.get("/management/org-1/legal/export", headers=_headers("attorney"))
    assert resp.status_code == 200
    cd = resp.headers.get("content-disposition", "")
    assert "attachment" in cd
    assert "legal_packets_org-1" in cd
