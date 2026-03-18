from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.legal.terms import TERMS_VERSION
from XR7.models.artist import Artist
from XR7.models.platform_config import PlatformConfig
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


def _create_artist(name: str = "Founder Test Artist") -> str:
    db = _TestSession()
    artist = Artist(
        id=str(uuid.uuid4()),
        name=name,
        email=f"{uuid.uuid4().hex[:8]}@artist.test",
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.commit()
    artist_id = artist.id
    db.close()
    return artist_id


def _accept_terms(artist_id: str) -> None:
    resp = client.post(
        f"/artists/{artist_id}/terms/accept",
        json={"terms_version": TERMS_VERSION, "agreed": True},
    )
    assert resp.status_code in {200, 201}


def _upload_statement(artist_id: str) -> None:
    csv_bytes = b"Month,Store,Country,Title,ISRC,Quantity,Earnings\n2024-01,Spotify,US,Song,USAAA1234567,100,1.00\n"
    resp = client.post(
        f"/artists/{artist_id}/statements/upload",
        files={"file": ("statement.csv", io.BytesIO(csv_bytes), "text/csv")},
    )
    assert resp.status_code == 201


def test_founder_slot_assigned_on_first_activation():
    db = _TestSession()
    cfg = db.query(PlatformConfig).filter(PlatformConfig.id == 1).first()
    if cfg is None:
        cfg = PlatformConfig(id=1)
        db.add(cfg)
    cfg.founder_cohort_limit = 2500
    cfg.founder_slots_filled = 0
    cfg.standard_contingency_fee_percent = 17.5
    db.commit()
    db.close()

    artist_id = _create_artist("Founder Candidate")
    _accept_terms(artist_id)
    _upload_statement(artist_id)

    artist_resp = client.get(f"/artists/{artist_id}")
    assert artist_resp.status_code == 200
    artist = artist_resp.json()

    assert artist["status"] == "ACTIVE"
    assert artist["is_founder"] is True
    assert artist["founder_slot_number"] is not None
    assert artist["founder_locked_at"] is not None
    assert float(artist["contingency_fee_percent"]) == 12.0

    founder_status = client.get("/config/founder-status")
    assert founder_status.status_code == 200
    body = founder_status.json()
    assert body["slots_total"] == 2500
    assert body["slots_filled"] >= 1
    assert body["founder_fee_percent"] == 12
    assert body["cohort_open"] is True


def test_non_founder_assignment_when_cohort_full_uses_configured_standard_fee():
    db = _TestSession()
    cfg = db.query(PlatformConfig).filter(PlatformConfig.id == 1).first()
    if cfg is None:
        cfg = PlatformConfig(id=1)
        db.add(cfg)
    cfg.founder_cohort_limit = 1
    cfg.founder_slots_filled = 1
    cfg.standard_contingency_fee_percent = 17.5
    db.commit()
    db.close()

    artist_id = _create_artist("Post Founder Artist")
    _accept_terms(artist_id)
    _upload_statement(artist_id)

    artist_resp = client.get(f"/artists/{artist_id}")
    assert artist_resp.status_code == 200
    artist = artist_resp.json()

    assert artist["status"] == "ACTIVE"
    assert artist["is_founder"] is False
    assert artist["founder_slot_number"] is None
    assert float(artist["contingency_fee_percent"]) == 17.5


def test_admin_can_only_increase_founder_cohort_limit(monkeypatch):
    monkeypatch.setenv("ADMIN_API_KEY", "admin-secret")

    db = _TestSession()
    cfg = db.query(PlatformConfig).filter(PlatformConfig.id == 1).first()
    if cfg is None:
        cfg = PlatformConfig(id=1)
        db.add(cfg)
    cfg.founder_cohort_limit = 2500
    db.commit()
    db.close()

    down_resp = client.put(
        "/admin/founder/cohort-limit",
        headers={"X-Admin-Key": "admin-secret", "X-Admin-Actor": "ops@xr7.test"},
        json={"founder_cohort_limit": 2000},
    )
    assert down_resp.status_code == 400

    up_resp = client.put(
        "/admin/founder/cohort-limit",
        headers={"X-Admin-Key": "admin-secret", "X-Admin-Actor": "ops@xr7.test"},
        json={"founder_cohort_limit": 2600},
    )
    assert up_resp.status_code == 200
    assert up_resp.json()["founder_cohort_limit"] == 2600
