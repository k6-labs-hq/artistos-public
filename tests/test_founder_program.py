from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.legal.terms import TERMS_VERSION
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.platform_config import PlatformConfig
from XR7.services.founder_program import process_founder_termination

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


def test_process_founder_termination_releases_slot_and_sets_standard_fee():
    db = _TestSession()
    try:
        cfg = db.query(PlatformConfig).filter(PlatformConfig.id == 1).first()
        if cfg is None:
            cfg = PlatformConfig(id=1)
            db.add(cfg)
        cfg.founder_cohort_limit = 2500
        cfg.founder_slots_filled = 120
        cfg.standard_contingency_fee_percent = 17.5

        artist = Artist(
            id=str(uuid.uuid4()),
            name="Founder Termination Test",
            email="terminate@test.artist",
            is_founder=True,
            founder_slot_number=120,
            founder_locked_at=datetime.now(timezone.utc),
            contingency_fee_percent=12.0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(artist)
        db.commit()

        result = process_founder_termination(
            db,
            artist=artist,
            reason="artist_requested_termination",
        )

        db.refresh(artist)
        assert result.artist_id == artist.id
        assert result.slot_released is True
        assert result.previous_fee_percent == 12.0
        assert result.effective_fee_percent == 17.5
        assert result.slots_filled == 119
        assert result.refund_due_total == 0.0

        assert artist.is_founder is False
        assert artist.founder_slot_number is None
        assert float(artist.contingency_fee_percent or 0.0) == 17.5
    finally:
        db.close()


def test_process_founder_termination_reprices_claims_and_calculates_refund_due():
    db = _TestSession()
    try:
        cfg = db.query(PlatformConfig).filter(PlatformConfig.id == 1).first()
        if cfg is None:
            cfg = PlatformConfig(id=1)
            db.add(cfg)
        cfg.founder_cohort_limit = 2500
        cfg.founder_slots_filled = 20
        cfg.standard_contingency_fee_percent = 17.5

        artist = Artist(
            id=str(uuid.uuid4()),
            name="Founder Fee Change Test",
            email="fees@test.artist",
            is_founder=True,
            founder_slot_number=20,
            founder_locked_at=datetime.now(timezone.utc),
            contingency_fee_percent=12.0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(artist)

        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            category=AnomalyCategory.ROYALTY,
            subtype="MISSING_PAYMENT",
            severity=AnomalySeverity.HIGH,
        )
        db.add(anomaly)
        db.flush()

        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="royalty_recovery",
            status=ClaimStatus.PAID,
            recovered_amount=1000.0,
            platform_fee_percent=12.0,
            platform_fee_amount=120.0,
            contingency_fee=120.0,
            artist_net_amount=880.0,
            currency="USD",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(claim)
        db.commit()

        # Fee policy changes down to 10% => refund due is 20.00
        result = process_founder_termination(
            db,
            artist=artist,
            reason="fee_policy_change",
            effective_fee_percent=10.0,
        )

        db.refresh(claim)
        assert result.claims_repriced == 1
        assert result.refund_due_total == 20.0
        assert float(claim.platform_fee_amount or 0.0) == 100.0
        assert float(claim.contingency_fee or 0.0) == 100.0
        assert float(claim.artist_net_amount or 0.0) == 900.0
        assert float(claim.platform_fee_percent or 0.0) == 10.0
    finally:
        db.close()


def test_founders_circle_rate_lock_prevents_fee_changes():
    """P0: Verify that contingency_fee_percent is immutable after founder_locked_at is set.

    Business Requirement: Founders Circle (2,500 artist cap) members receive a lifetime
    rate lock guarantee. Once locked, the rate cannot be changed by anyone - not admins,
    not the artist, not system processes.

    This test ensures the @validates decorator on Artist.contingency_fee_percent enforces
    this immutability at the ORM level, preventing rate manipulation that would violate
    the explicit contract promise to Founders Circle members.

    Compliance: SOC 2 CC6.1 - Logical access controls (immutable financial terms)
    Regulatory citation: 17 CFR § 270.22c-2 (anti-manipulation of fee schedules)
    """
    db = _TestSession()
    try:
        # Create a Founders Circle member with locked rate
        artist = Artist(
            id=str(uuid.uuid4()),
            name="Founder Rate Lock Test",
            email="ratelock@test.artist",
            is_founder=True,
            founder_slot_number=42,
            founder_locked_at=datetime.now(timezone.utc),
            contingency_fee_percent=12.0,  # Locked at 12%
            created_at=datetime.now(timezone.utc),
        )
        db.add(artist)
        db.commit()
        db.refresh(artist)

        # Verify initial state
        assert artist.is_founder is True
        assert artist.founder_locked_at is not None
        assert artist.contingency_fee_percent == 12.0

        # TEST 1: Attempt to change rate - should raise ValueError
        try:
            artist.contingency_fee_percent = 15.0
            db.flush()
            assert False, "Expected ValueError when changing locked rate"
        except ValueError as e:
            # Expected error
            assert "Cannot modify contingency_fee_percent for Founders Circle member" in str(e)
            assert "Rate locked at 12.0%" in str(e)
            assert "lifetime rate guarantee" in str(e)
            db.rollback()

        # TEST 2: Setting the SAME value should succeed (idempotent operation)
        artist.contingency_fee_percent = 12.0
        db.flush()  # Should not raise
        db.commit()
        db.refresh(artist)
        assert artist.contingency_fee_percent == 12.0

        # TEST 3: Non-locked artist can change rate freely
        non_founder = Artist(
            id=str(uuid.uuid4()),
            name="Non-Founder Test",
            email="nonfounder@test.artist",
            is_founder=False,
            founder_locked_at=None,  # No lock
            contingency_fee_percent=17.5,
            created_at=datetime.now(timezone.utc),
        )
        db.add(non_founder)
        db.commit()

        # This should succeed - no lock, so rate can change
        non_founder.contingency_fee_percent = 18.0
        db.flush()
        db.commit()
        db.refresh(non_founder)
        assert non_founder.contingency_fee_percent == 18.0

    finally:
        db.close()
