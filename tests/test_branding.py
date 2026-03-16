from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from XR7.api.app import app


client = TestClient(app)


def _headers(role: str = "org_admin", key: str = "org-secret") -> dict[str, str]:
    return {
        "X-Org-Key": key,
        "X-Org-Role": role,
        "X-Org-Actor": "branding@test.xr7",
    }


def _assert_branding_schema(payload: dict) -> None:
    assert "branding" in payload
    branding = payload["branding"]
    assert isinstance(branding, dict)
    assert "name" in branding
    assert "logo_url" in branding
    assert "primary_color" in branding
    assert "support_email" in branding
    assert "white_label_enabled" in branding


def test_branding_profile_crud(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    org_id = f"org-brand-{uuid.uuid4().hex[:8]}"

    create_resp = client.post(
        f"/branding/{org_id}",
        json={
            "display_name": "Northstar Rights",
            "logo_url": "https://cdn.example.com/logo.svg",
            "primary_color": "#003366",
            "secondary_color": "#005599",
            "accent_color": "#E67E22",
            "dashboard_header_text": "Northstar Command Center",
            "dashboard_footer_text": "Northstar Confidential",
            "support_email": "help@northstar.test",
            "support_phone": "+1-555-0123",
            "legal_disclaimer": "Northstar legal terms apply.",
            "custom_domain": "app.northstar.test",
            "white_label_enabled": True,
        },
    )
    assert create_resp.status_code == 200
    assert create_resp.json()["profile"]["display_name"] == "Northstar Rights"

    get_resp = client.get(f"/branding/{org_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["branding"]["name"] == "Northstar Rights"

    patch_resp = client.patch(
        f"/branding/{org_id}",
        json={"support_email": "support@northstar.test"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["profile"]["support_email"] == "support@northstar.test"


def test_ui_shell_renders_branded_placeholders():
    org_id = f"org-shell-{uuid.uuid4().hex[:8]}"
    client.patch(
        f"/branding/{org_id}",
        json={
            "display_name": "Helix Music Group",
            "support_email": "support@helix.test",
            "white_label_enabled": True,
        },
    )
    resp = client.get(f"/ui/shell?org_id={org_id}")
    assert resp.status_code == 200
    body = resp.text
    assert "Helix Music Group" in body
    assert "support@helix.test" in body


def test_artist_dashboard_includes_branding_metadata():
    create_artist = client.post(
        "/artists/",
        json={
            "name": "Branded Artist",
            "role": "org:org-dashboard-brand",
        },
    )
    assert create_artist.status_code == 201
    artist_id = create_artist.json()["id"]

    client.patch(
        "/branding/org-dashboard-brand",
        json={
            "display_name": "Summit Label",
            "support_email": "ops@summit.test",
            "white_label_enabled": True,
        },
    )

    dashboard_resp = client.get(f"/artists/{artist_id}/dashboard")
    assert dashboard_resp.status_code == 200
    payload = dashboard_resp.json()
    _assert_branding_schema(payload)
    assert payload["branding"]["name"] == "Summit Label"


def test_management_dashboard_exposes_branding(monkeypatch):
    monkeypatch.setenv("XR7_ORG_KEY", "org-secret")
    org_id = f"org-mgmt-{uuid.uuid4().hex[:8]}"
    client.patch(
        f"/branding/{org_id}",
        json={
            "display_name": "Keystone Partners",
            "white_label_enabled": True,
            "support_email": "contact@keystone.test",
            "legal_disclaimer": "Keystone legal disclosure.",
        },
    )
    resp = client.get(f"/management/{org_id}/dashboard", headers=_headers())
    assert resp.status_code == 200
    data = resp.json()
    _assert_branding_schema(data)
    assert data["branding"]["name"] == "Keystone Partners"
    assert data["dashboard_title"] == "Keystone Partners Dashboard"


def test_additional_dashboard_like_endpoints_include_branding():
    create_artist = client.post(
        "/artists/",
        json={
            "name": "Brand Surface Artist",
            "role": "org:org-surface-brand",
        },
    )
    assert create_artist.status_code == 201
    artist_id = create_artist.json()["id"]

    client.patch(
        "/branding/org-surface-brand",
        json={
            "display_name": "Atlas Rights",
            "white_label_enabled": True,
        },
    )

    flow = client.get(f"/artists/{artist_id}/dashboard/flow")
    assert flow.status_code == 200
    _assert_branding_schema(flow.json())
    assert flow.json()["branding"]["name"] == "Atlas Rights"

    benchmarks = client.get(f"/artists/{artist_id}/benchmarks")
    assert benchmarks.status_code == 200
    _assert_branding_schema(benchmarks.json())
    assert benchmarks.json()["branding"]["name"] == "Atlas Rights"

    export_guidance = client.get(f"/artists/{artist_id}/dashboard/export-guidance")
    assert export_guidance.status_code == 200
    _assert_branding_schema(export_guidance.json())
    assert export_guidance.json()["branding"]["name"] == "Atlas Rights"

    permissions = client.get(f"/artists/{artist_id}/connect/permissions-dashboard")
    assert permissions.status_code == 200
    _assert_branding_schema(permissions.json())
    assert permissions.json()["branding"]["name"] == "Atlas Rights"

    benchmark = client.get(f"/artists/{artist_id}/recovery/rate-benchmark")
    assert benchmark.status_code == 200
    _assert_branding_schema(benchmark.json())
    assert benchmark.json()["branding"]["name"] == "Atlas Rights"

    digest = client.get(f"/artists/{artist_id}/digest/weekly")
    assert digest.status_code == 200
    _assert_branding_schema(digest.json())
    assert digest.json()["branding"]["name"] == "Atlas Rights"


def test_branding_schema_on_representative_endpoints():
    create_artist = client.post(
        "/artists/",
        json={
            "name": "Schema Coverage Artist",
            "role": "org:org-schema-brand",
        },
    )
    assert create_artist.status_code == 201
    artist_id = create_artist.json()["id"]

    patch = client.patch(
        "/branding/org-schema-brand",
        json={
            "display_name": "Schema Label",
            "white_label_enabled": True,
        },
    )
    assert patch.status_code == 200

    responses = [
        client.get(f"/artists/{artist_id}/workflow/runs/unknown-run"),
        client.get(f"/artists/{artist_id}/connect/global-social/status"),
        client.get(f"/artists/{artist_id}/terms/status"),
        client.get(f"/artists/{artist_id}/connect/regional-global/status"),
        client.get(f"/artists/{artist_id}/agent-trace/unknown-run"),
    ]
    for resp in responses:
        assert resp.status_code == 200
        _assert_branding_schema(resp.json())