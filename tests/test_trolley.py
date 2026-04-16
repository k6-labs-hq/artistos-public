from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient


from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.trolley_transaction import TrolleyTransaction, TrolleyTxnStatus, TrolleyTxnType

client = TestClient(app)


@pytest.fixture()
def db():
    session = _TestSession()
    yield session
    session.close()


def _mk_artist(db, *, verified: bool = True) -> Artist:
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Trolley Test Artist",
        email="artist@example.com",
        country_code="US",
        trolley_recipient_id="tr_123",
        payout_account_status="verified" if verified else "pending",
        tax_form_status="verified" if verified else "pending",
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.commit()
    db.refresh(artist)
    return artist


def _mk_claim(
    db, artist_id: str, *, status: ClaimStatus = ClaimStatus.FUNDS_RECEIVED, net: float = 900.0
) -> Claim:
    now = datetime.now(timezone.utc)
    claim = Claim(
        id=str(uuid.uuid4()),
        artist_id=artist_id,
        anomaly_id=str(uuid.uuid4()),
        claim_type="ROYALTY",
        status=status,
        recovered_amount=1000.0,
        currency="USD",
        platform_fee_percent=12.0,
        platform_fee_amount=120.0,
        contingency_fee=120.0,
        artist_net_amount=net,
        created_at=now,
        updated_at=now,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


@pytest.mark.integration
def test_manual_remittance_endpoint_updates_claim_and_creates_transaction(db):
    artist = _mk_artist(db, verified=False)
    claim = _mk_claim(db, artist.id, status=ClaimStatus.ACCEPTED, net=0.0)

    resp = client.post(
        f"/artists/{artist.id}/claims/{claim.id}/manual-remittance",
        json={
            "gross_amount": 1200.0,
            "remittance_method": "wire",
            "received_date": datetime.now(timezone.utc).isoformat(),
            "reference_number": "WIRE-123",
        },
    )
    assert resp.status_code == 200

    db.refresh(claim)
    assert claim.status == ClaimStatus.FUNDS_RECEIVED
    assert claim.platform_fee_amount == pytest.approx(144.0)
    assert claim.artist_net_amount == pytest.approx(1056.0)

    txn = (
        db.query(TrolleyTransaction)
        .filter(
            TrolleyTransaction.claim_id == claim.id,
            TrolleyTransaction.type == TrolleyTxnType.REMITTANCE,
        )
        .first()
    )
    assert txn is not None
    assert txn.status == TrolleyTxnStatus.PAID
    assert txn.gross_amount == pytest.approx(1200.0)


@pytest.mark.integration
def test_disburse_endpoint_rejects_existing_external_payment(db, monkeypatch):
    artist = _mk_artist(db)
    claim = _mk_claim(db, artist.id)

    class _DummyClient:
        def get_payments_by_external_id(self, external_id: str):
            assert external_id == claim.id
            return {"payments": [{"id": "pay_existing"}]}

        def create_payment(self, payload):  # pragma: no cover
            raise AssertionError("create_payment should not be called when payment already exists")

    monkeypatch.setattr("XR7.billing.engine.TrolleyClient.from_env", lambda: _DummyClient())

    resp = client.post(f"/claims/{claim.id}/disburse")
    assert resp.status_code == 400
    assert "already exists" in resp.json()["detail"]


@pytest.mark.integration
def test_disburse_endpoint_success_creates_processing_transaction(db, monkeypatch):
    artist = _mk_artist(db)
    claim = _mk_claim(db, artist.id)

    class _DummyClient:
        def get_payments_by_external_id(self, external_id: str):
            return {"payments": []}

        def create_payment(self, payload):
            assert payload["externalId"] == claim.id
            return {"payment": {"id": "pay_new_1", "status": "processing"}}

    monkeypatch.setattr("XR7.billing.engine.TrolleyClient.from_env", lambda: _DummyClient())

    resp = client.post(f"/claims/{claim.id}/disburse")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "PROCESSING"
    assert body["trolley_payment_id"] == "pay_new_1"

    db.refresh(claim)
    assert claim.trolley_payment_id == "pay_new_1"
    assert claim.trolley_payment_status == "PROCESSING"


@pytest.mark.integration
def test_trolley_webhook_marks_claim_paid_and_updates_transaction(db, monkeypatch):
    monkeypatch.setenv("TROLLEY_SECRET_KEY", "wh_secret")

    artist = _mk_artist(db)
    claim = _mk_claim(db, artist.id)

    tx = TrolleyTransaction(
        id=str(uuid.uuid4()),
        artist_id=artist.id,
        claim_id=claim.id,
        type=TrolleyTxnType.DISBURSEMENT,
        status=TrolleyTxnStatus.PROCESSING,
        net_amount=900.0,
        source_currency="USD",
        external_id=claim.id,
        trolley_payment_id="pay_old",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(tx)
    db.commit()

    payload = {
        "type": "payment.paid",
        "payment": {
            "id": "pay_paid_1",
            "externalId": claim.id,
            "exchangeRate": 1.0,
            "targetAmount": 900.0,
            "targetCurrency": "USD",
        },
    }
    body = json.dumps(payload).encode("utf-8")
    sig = hmac.new(b"wh_secret", body, hashlib.sha256).hexdigest()

    resp = client.post(
        "/webhooks/trolley",
        content=body,
        headers={"x-trolley-signature": sig, "Content-Type": "application/json"},
    )
    assert resp.status_code == 200

    db.refresh(claim)
    db.refresh(tx)
    assert claim.status == ClaimStatus.PAID
    assert claim.trolley_payment_id == "pay_paid_1"
    assert tx.status == TrolleyTxnStatus.PAID
