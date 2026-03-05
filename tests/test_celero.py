"""
Tests for the Celero Commerce merchant-of-record integration.

Covers:
- CeleroClient: credential check, status, NotImplementedError when unconfigured
- CeleroResponse: parsing, approved/declined helpers
- CeleroWebhookHandler: signature validation, event parsing, dispatch
- CeleroTransaction model: creation, schema serialisation
- Artist.celero_customer_vault_id field
- BillingEngine.charge_via_celero / disburse_via_celero
- API endpoints: register, status, charge, disburse, refund, void,
  list/get transactions, webhook receiver
- GET /health/readiness now includes merchant_of_record section
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from XR7.api.app import app
from XR7.billing.engine import BillingEngine
from XR7.celero.client import (
    CeleroClient,
    CeleroResponse,
    _parse_response,
    RESPONSE_APPROVED,
    RESPONSE_DECLINED,
    RESPONSE_ERROR,
)
from XR7.celero.webhook import (
    CeleroWebhookHandler,
    parse_event,
    validate_signature,
    EVENT_TRANSACTION_APPROVED,
    EVENT_TRANSACTION_DECLINED,
    EVENT_DISBURSEMENT_SETTLED,
    EVENT_DISBURSEMENT_FAILED,
)
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.celero_transaction import (
    CeleroTransaction,
    CeleroTxnStatus,
    CeleroTxnType,
    CeleroTransactionSchema,
)
from XR7.models.claim import Claim, ClaimStatus

# Use the shared test DB from conftest
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def db():
    session = _TestSession()
    yield session
    session.close()


@pytest.fixture()
def artist(db):
    a = Artist(
        id=str(uuid.uuid4()),
        name="Celero Test Artist",
        created_at=datetime.now(timezone.utc),
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@pytest.fixture()
def artist_with_vault(db):
    a = Artist(
        id=str(uuid.uuid4()),
        name="Vaulted Artist",
        celero_customer_vault_id="vault-abc-123",
        created_at=datetime.now(timezone.utc),
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@pytest.fixture()
def anomaly(db, artist):
    a = Anomaly(
        id=str(uuid.uuid4()),
        artist_id=artist.id,
        category=AnomalyCategory.ROYALTY,
        subtype="MISSING_PAYMENT",
        severity=AnomalySeverity.HIGH,
        confidence_score=0.9,
        status=AnomalyStatus.OPEN,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@pytest.fixture()
def paid_claim(db, artist, anomaly):
    c = Claim(
        id=str(uuid.uuid4()),
        artist_id=artist.id,
        anomaly_id=anomaly.id,
        claim_type="ROYALTY",
        status=ClaimStatus.PAID,
        recovered_amount=1000.0,
        currency="USD",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@pytest.fixture()
def celero_txn(db, artist_with_vault):
    txn = CeleroTransaction(
        id=str(uuid.uuid4()),
        artist_id=artist_with_vault.id,
        type=CeleroTxnType.CHARGE,
        amount=100.0,
        currency="USD",
        status=CeleroTxnStatus.APPROVED,
        celero_transaction_id="celero-txn-999",
        celero_customer_vault_id="vault-abc-123",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


# ---------------------------------------------------------------------------
# CeleroResponse parsing
# ---------------------------------------------------------------------------

class TestCeleroResponseParsing:
    def test_approved_response(self):
        raw = "response=1&responsetext=SUCCESS&authcode=ABC123&transactionid=7654321&response_code=100"
        r = _parse_response(raw)
        assert r.approved is True
        assert r.declined is False
        assert r.transaction_id == "7654321"
        assert r.auth_code == "ABC123"
        assert r.response_code == "100"

    def test_declined_response(self):
        raw = "response=2&responsetext=DECLINE&transactionid=111&response_code=200"
        r = _parse_response(raw)
        assert r.approved is False
        assert r.declined is True

    def test_error_response(self):
        raw = "response=3&responsetext=Error&response_code=300"
        r = _parse_response(raw)
        assert r.response == RESPONSE_ERROR
        assert r.approved is False

    def test_customer_vault_id_parsed(self):
        raw = "response=1&responsetext=Customer Added&customer_vault_id=vault-new-555"
        r = _parse_response(raw)
        assert r.customer_vault_id == "vault-new-555"

    def test_to_dict_keys(self):
        r = _parse_response("response=1&responsetext=OK&transactionid=T1&response_code=100")
        d = r.to_dict()
        assert "approved" in d
        assert "transaction_id" in d
        assert "response_code" in d
        assert "response_code_description" in d

    def test_response_code_description(self):
        r = _parse_response("response=2&responsetext=Decline&response_code=200")
        assert "declined" in r.response_code_description.lower()

    def test_empty_raw_gives_error_response(self):
        r = _parse_response("")
        assert r.response == RESPONSE_ERROR


# ---------------------------------------------------------------------------
# CeleroClient credential checks
# ---------------------------------------------------------------------------

class TestCeleroClientCredentials:
    def test_not_configured_without_env_var(self, monkeypatch):
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        c = CeleroClient()
        assert c.configured is False

    def test_configured_with_env_var(self, monkeypatch):
        monkeypatch.setenv("CELERO_SECURITY_KEY", "test-key-123")
        c = CeleroClient()
        assert c.configured is True

    def test_configured_with_constructor_arg(self):
        c = CeleroClient(security_key="direct-key")
        assert c.configured is True

    def test_charge_raises_not_implemented_when_unconfigured(self, monkeypatch):
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        c = CeleroClient()
        with pytest.raises(NotImplementedError) as exc:
            c.charge(amount=100.0, customer_vault_id="v1")
        assert "CELERO_SECURITY_KEY" in str(exc.value)
        assert "https://celerocommerce.com/developers/" in str(exc.value)

    def test_disburse_raises_not_implemented_when_unconfigured(self, monkeypatch):
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        c = CeleroClient()
        with pytest.raises(NotImplementedError):
            c.disburse(amount=900.0, customer_vault_id="v1")

    def test_add_customer_raises_not_implemented_when_unconfigured(self, monkeypatch):
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        c = CeleroClient()
        with pytest.raises(NotImplementedError):
            c.add_customer(first_name="A", last_name="B", email="a@b.com")

    def test_refund_raises_not_implemented_when_unconfigured(self, monkeypatch):
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        c = CeleroClient()
        with pytest.raises(NotImplementedError):
            c.refund(transaction_id="txn-1")

    def test_void_raises_not_implemented_when_unconfigured(self, monkeypatch):
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        c = CeleroClient()
        with pytest.raises(NotImplementedError):
            c.void(transaction_id="txn-1")

    def test_status_returns_dict(self, monkeypatch):
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        c = CeleroClient()
        s = c.status()
        assert "configured" in s
        assert "required_env_vars" in s
        assert "setup_url" in s
        assert s["configured"] is False
        assert s["status"] == "missing_credentials"

    def test_status_ready_when_configured(self, monkeypatch):
        monkeypatch.setenv("CELERO_SECURITY_KEY", "sk-live-xxx")
        c = CeleroClient()
        assert c.status()["status"] == "ready"


# ---------------------------------------------------------------------------
# Webhook signature validation
# ---------------------------------------------------------------------------

class TestWebhookSignatureValidation:
    def _sign(self, body: bytes, secret: str) -> str:
        return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    def test_valid_signature_accepted(self, monkeypatch):
        monkeypatch.setenv("CELERO_WEBHOOK_SECRET", "my-secret")
        body = b'{"event_type":"transaction.approved","transaction_id":"T1"}'
        sig = self._sign(body, "my-secret")
        assert validate_signature(body, sig) is True

    def test_invalid_signature_rejected(self, monkeypatch):
        monkeypatch.setenv("CELERO_WEBHOOK_SECRET", "my-secret")
        body = b'{"event_type":"transaction.approved","transaction_id":"T1"}'
        assert validate_signature(body, "bad-sig") is False

    def test_empty_signature_rejected(self, monkeypatch):
        monkeypatch.setenv("CELERO_WEBHOOK_SECRET", "my-secret")
        body = b"{}"
        assert validate_signature(body, "") is False

    def test_development_skips_validation_without_secret(self, monkeypatch):
        monkeypatch.delenv("CELERO_WEBHOOK_SECRET", raising=False)
        monkeypatch.setenv("XR7_ENV", "development")
        assert validate_signature(b"{}", "any-sig") is True

    def test_production_raises_without_secret(self, monkeypatch):
        monkeypatch.delenv("CELERO_WEBHOOK_SECRET", raising=False)
        monkeypatch.setenv("XR7_ENV", "production")
        with pytest.raises(ValueError) as exc:
            validate_signature(b"{}", "any-sig")
        assert "CELERO_WEBHOOK_SECRET" in str(exc.value)

    def test_case_insensitive_comparison(self, monkeypatch):
        monkeypatch.setenv("CELERO_WEBHOOK_SECRET", "secret")
        body = b"test"
        sig = self._sign(body, "secret").upper()
        assert validate_signature(body, sig) is True


# ---------------------------------------------------------------------------
# Webhook event parsing
# ---------------------------------------------------------------------------

class TestWebhookEventParsing:
    def test_parse_valid_event(self):
        body = json.dumps({
            "event_type": "transaction.approved",
            "transaction_id": "T123",
            "amount": "100.00",
        }).encode()
        event = parse_event(body)
        assert event["event_type"] == "transaction.approved"
        assert event["transaction_id"] == "T123"

    def test_parse_invalid_json_raises(self):
        with pytest.raises(ValueError, match="Invalid webhook payload"):
            parse_event(b"not-json")

    def test_parse_missing_event_type_raises(self):
        with pytest.raises(ValueError, match="missing 'event_type'"):
            parse_event(b'{"transaction_id": "T1"}')

    def test_parse_non_object_raises(self):
        with pytest.raises(ValueError):
            parse_event(b'"just a string"')


# ---------------------------------------------------------------------------
# CeleroWebhookHandler
# ---------------------------------------------------------------------------

class TestCeleroWebhookHandler:
    def _make_txn(self, db, artist_id: str, celero_txn_id: str, txn_type=CeleroTxnType.CHARGE) -> CeleroTransaction:
        txn = CeleroTransaction(
            id=str(uuid.uuid4()),
            artist_id=artist_id,
            type=txn_type,
            amount=100.0,
            currency="USD",
            status=CeleroTxnStatus.PENDING,
            celero_transaction_id=celero_txn_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(txn)
        db.commit()
        db.refresh(txn)
        return txn

    def test_approved_updates_status(self, db, artist):
        txn = self._make_txn(db, artist.id, "TXN-APPROVED-1")
        handler = CeleroWebhookHandler(db)
        result = handler.handle({
            "event_type": EVENT_TRANSACTION_APPROVED,
            "transaction_id": "TXN-APPROVED-1",
        })
        assert result["handled"] is True
        assert result["new_status"] == "APPROVED"
        db.refresh(txn)
        assert txn.status == CeleroTxnStatus.APPROVED

    def test_declined_updates_status(self, db, artist):
        txn = self._make_txn(db, artist.id, "TXN-DECLINED-1")
        handler = CeleroWebhookHandler(db)
        result = handler.handle({
            "event_type": EVENT_TRANSACTION_DECLINED,
            "transaction_id": "TXN-DECLINED-1",
        })
        assert result["handled"] is True
        assert result["new_status"] == "DECLINED"

    def test_disbursement_settled_updates_status(self, db, artist):
        txn = self._make_txn(db, artist.id, "TXN-SETTLE-1", txn_type=CeleroTxnType.DISBURSEMENT)
        handler = CeleroWebhookHandler(db)
        result = handler.handle({
            "event_type": EVENT_DISBURSEMENT_SETTLED,
            "transaction_id": "TXN-SETTLE-1",
        })
        assert result["new_status"] == "SETTLED"
        db.refresh(txn)
        assert txn.status == CeleroTxnStatus.SETTLED

    def test_unknown_transaction_id_returns_not_handled(self, db):
        handler = CeleroWebhookHandler(db)
        result = handler.handle({
            "event_type": EVENT_TRANSACTION_APPROVED,
            "transaction_id": "does-not-exist",
        })
        assert result["handled"] is False

    def test_unknown_event_type_returns_not_handled(self, db):
        handler = CeleroWebhookHandler(db)
        result = handler.handle({"event_type": "unknown.event", "transaction_id": "X"})
        assert result["handled"] is False

    def test_missing_transaction_id_returns_not_handled(self, db):
        handler = CeleroWebhookHandler(db)
        result = handler.handle({"event_type": EVENT_TRANSACTION_APPROVED})
        assert result["handled"] is False

    def test_approved_charge_advances_paid_claim_to_closed(self, db, artist, anomaly):
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="ROYALTY",
            status=ClaimStatus.PAID,
            recovered_amount=1000.0,
            currency="USD",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(claim)
        db.commit()

        txn = CeleroTransaction(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            claim_id=claim.id,
            type=CeleroTxnType.CHARGE,
            amount=100.0,
            currency="USD",
            status=CeleroTxnStatus.PENDING,
            celero_transaction_id="TXN-FEE-CLOSE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(txn)
        db.commit()

        handler = CeleroWebhookHandler(db)
        result = handler.handle({
            "event_type": EVENT_TRANSACTION_APPROVED,
            "transaction_id": "TXN-FEE-CLOSE",
        })
        assert result.get("claim_advanced_to") == "CLOSED"
        db.refresh(claim)
        assert ClaimStatus(claim.status) == ClaimStatus.CLOSED


# ---------------------------------------------------------------------------
# CeleroTransaction model
# ---------------------------------------------------------------------------

class TestCeleroTransactionModel:
    def test_create_and_persist(self, db, artist):
        txn = CeleroTransaction(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            type=CeleroTxnType.CHARGE,
            amount=150.0,
            currency="USD",
            status=CeleroTxnStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(txn)
        db.commit()
        fetched = db.query(CeleroTransaction).filter(CeleroTransaction.id == txn.id).first()
        assert fetched is not None
        assert fetched.amount == 150.0
        assert fetched.type == CeleroTxnType.CHARGE

    def test_schema_serialisation(self, celero_txn):
        schema = CeleroTransactionSchema.model_validate(celero_txn)
        assert schema.type == CeleroTxnType.CHARGE
        assert schema.status == CeleroTxnStatus.APPROVED
        assert schema.amount == 100.0


# ---------------------------------------------------------------------------
# Artist model — celero_customer_vault_id field
# ---------------------------------------------------------------------------

class TestArtistCeleroField:
    def test_default_is_none(self, artist):
        assert artist.celero_customer_vault_id is None

    def test_can_be_set(self, db, artist):
        artist.celero_customer_vault_id = "vault-xyz-789"
        db.commit()
        db.refresh(artist)
        assert artist.celero_customer_vault_id == "vault-xyz-789"

    def test_schema_includes_vault_id(self, artist_with_vault):
        from XR7.models.artist import ArtistSchema
        schema = ArtistSchema.model_validate(artist_with_vault)
        assert schema.celero_customer_vault_id == "vault-abc-123"


# ---------------------------------------------------------------------------
# BillingEngine Celero methods
# ---------------------------------------------------------------------------

class TestBillingEngineCelero:
    def test_charge_via_celero_raises_when_unconfigured(self, db, artist_with_vault, anomaly, monkeypatch):
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist_with_vault.id,
            anomaly_id=anomaly.id,
            claim_type="ROYALTY",
            status=ClaimStatus.PAID,
            recovered_amount=500.0,
            currency="USD",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(claim)
        db.commit()
        engine = BillingEngine(db)
        with pytest.raises(NotImplementedError) as exc:
            engine.charge_via_celero(
                claim_id=claim.id,
                customer_vault_id="vault-abc-123",
            )
        assert "CELERO_SECURITY_KEY" in str(exc.value)

    def test_charge_via_celero_raises_for_missing_claim(self, db, monkeypatch):
        monkeypatch.setenv("CELERO_SECURITY_KEY", "sk-test")
        engine = BillingEngine(db)
        with pytest.raises(ValueError, match="not found"):
            engine.charge_via_celero(
                claim_id="nonexistent-claim",
                customer_vault_id="v1",
            )

    def test_charge_via_celero_raises_for_no_recovered_amount(self, db, artist, anomaly, monkeypatch):
        monkeypatch.setenv("CELERO_SECURITY_KEY", "sk-test")
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="ROYALTY",
            status=ClaimStatus.PAID,
            recovered_amount=None,
            currency="USD",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(claim)
        db.commit()
        engine = BillingEngine(db)
        with pytest.raises(ValueError, match="no recovered_amount"):
            engine.charge_via_celero(claim_id=claim.id, customer_vault_id="v1")

    def test_charge_via_celero_creates_pending_txn_before_gateway(self, db, artist_with_vault, anomaly, monkeypatch):
        """
        Even when Celero responds, a PENDING transaction must be in the DB
        before the gateway call so we never lose a record.
        """
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist_with_vault.id,
            anomaly_id=anomaly.id,
            claim_type="ROYALTY",
            status=ClaimStatus.PAID,
            recovered_amount=200.0,
            currency="USD",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(claim)
        db.commit()

        engine = BillingEngine(db)
        with pytest.raises(NotImplementedError):
            engine.charge_via_celero(claim_id=claim.id, customer_vault_id="v1")

        # Pending record must exist despite the error
        pending = (
            db.query(CeleroTransaction)
            .filter(CeleroTransaction.claim_id == claim.id)
            .first()
        )
        assert pending is not None
        assert pending.status == CeleroTxnStatus.PENDING
        assert pending.amount == pytest.approx(20.0)  # 10% of 200

    def test_disburse_via_celero_raises_when_unconfigured(self, db, artist_with_vault, monkeypatch):
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        engine = BillingEngine(db)
        with pytest.raises(NotImplementedError):
            engine.disburse_via_celero(
                artist_id=artist_with_vault.id,
                claim_id=None,
                amount=900.0,
                currency="USD",
                customer_vault_id="vault-abc-123",
            )


# ---------------------------------------------------------------------------
# API: GET /health/readiness — Celero section
# ---------------------------------------------------------------------------

class TestReadinessCeleroSection:
    def test_readiness_includes_merchant_of_record(self, monkeypatch):
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        resp = client.get("/health/readiness")
        assert resp.status_code == 200
        data = resp.json()
        assert "merchant_of_record" in data
        mor = data["merchant_of_record"]
        assert mor["provider"] == "Celero Commerce"
        assert mor["gateway"] == "Celero Connect®"

    def test_readiness_shows_missing_credentials_without_key(self, monkeypatch):
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        monkeypatch.delenv("CELERO_WEBHOOK_SECRET", raising=False)
        data = client.get("/health/readiness").json()
        mor = data["merchant_of_record"]
        assert mor["api_configured"] is False
        assert mor["status"] == "missing_credentials"

    def test_readiness_shows_ready_with_key(self, monkeypatch):
        monkeypatch.setenv("CELERO_SECURITY_KEY", "sk-test")
        monkeypatch.setenv("CELERO_WEBHOOK_SECRET", "ws-secret")
        data = client.get("/health/readiness").json()
        mor = data["merchant_of_record"]
        assert mor["api_configured"] is True
        assert mor["status"] == "ready"


# ---------------------------------------------------------------------------
# API: Artist Celero endpoints
# ---------------------------------------------------------------------------

class TestArtistCeleroEndpoints:
    def test_celero_status_unknown_artist_404(self):
        resp = client.get("/artists/nonexistent/celero/status")
        assert resp.status_code == 404

    def test_celero_status_unregistered_artist(self):
        # Create artist via API
        resp = client.post("/artists/", json={"name": "Status Test Artist"})
        assert resp.status_code == 201
        aid = resp.json()["id"]
        resp = client.get(f"/artists/{aid}/celero/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["celero_registered"] is False
        assert data["celero_customer_vault_id"] is None

    def test_register_unknown_artist_404(self, monkeypatch):
        monkeypatch.setenv("CELERO_SECURITY_KEY", "sk-test")
        resp = client.post(
            "/artists/nonexistent/celero/register",
            json={"first_name": "A", "last_name": "B", "email": "a@b.com"},
        )
        assert resp.status_code == 404

    def test_register_without_celero_key_returns_503(self, monkeypatch):
        monkeypatch.delenv("CELERO_SECURITY_KEY", raising=False)
        resp = client.post("/artists/", json={"name": "Reg503 Artist"})
        aid = resp.json()["id"]
        resp = client.post(
            f"/artists/{aid}/celero/register",
            json={"first_name": "R", "last_name": "R", "email": "r@r.com"},
        )
        assert resp.status_code == 503
        assert "CELERO_SECURITY_KEY" in resp.json()["detail"]

    def test_register_mocked_success_stores_vault_id(self, monkeypatch):
        monkeypatch.setenv("CELERO_SECURITY_KEY", "sk-test")
        resp = client.post("/artists/", json={"name": "Mock Reg Artist"})
        aid = resp.json()["id"]

        mock_response = CeleroResponse(
            raw="response=1&customer_vault_id=vault-mock-001",
            response=RESPONSE_APPROVED,
            response_text="Customer Added",
            customer_vault_id="vault-mock-001",
        )
        with patch("XR7.celero.client.CeleroClient.add_customer", return_value=mock_response):
            resp = client.post(
                f"/artists/{aid}/celero/register",
                json={"first_name": "Mock", "last_name": "Artist", "email": "mock@artist.com"},
            )
        assert resp.status_code == 200
        assert resp.json()["celero_customer_vault_id"] == "vault-mock-001"

    def test_register_twice_returns_409(self, monkeypatch):
        monkeypatch.setenv("CELERO_SECURITY_KEY", "sk-test")
        resp = client.post("/artists/", json={"name": "Double Reg Artist"})
        aid = resp.json()["id"]

        mock_response = CeleroResponse(
            raw="response=1&customer_vault_id=vault-double-1",
            response=RESPONSE_APPROVED,
            response_text="Customer Added",
            customer_vault_id="vault-double-1",
        )
        with patch("XR7.celero.client.CeleroClient.add_customer", return_value=mock_response):
            client.post(
                f"/artists/{aid}/celero/register",
                json={"first_name": "D", "last_name": "R", "email": "d@r.com"},
            )
        # Second registration attempt
        with patch("XR7.celero.client.CeleroClient.add_customer", return_value=mock_response):
            resp2 = client.post(
                f"/artists/{aid}/celero/register",
                json={"first_name": "D", "last_name": "R", "email": "d@r.com"},
            )
        assert resp2.status_code == 409

    def test_charge_without_vault_returns_400(self, monkeypatch):
        monkeypatch.setenv("CELERO_SECURITY_KEY", "sk-test")
        resp = client.post("/artists/", json={"name": "No Vault Charge"})
        aid = resp.json()["id"]
        resp = client.post(f"/artists/{aid}/celero/charge", json={"claim_id": "any"})
        assert resp.status_code == 400
        assert "not registered" in resp.json()["detail"]

    def test_list_transactions_unknown_artist_404(self):
        resp = client.get("/artists/nonexistent/celero/transactions")
        assert resp.status_code == 404

    def test_list_transactions_returns_list(self):
        resp = client.post("/artists/", json={"name": "Txn List Artist"})
        aid = resp.json()["id"]
        resp = client.get(f"/artists/{aid}/celero/transactions")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_transaction_not_found_404(self):
        resp = client.post("/artists/", json={"name": "Txn 404 Artist"})
        aid = resp.json()["id"]
        resp = client.get(f"/artists/{aid}/celero/transactions/nonexistent-txn")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# API: Charge and disburse — mocked gateway
# ---------------------------------------------------------------------------

class TestChargeAndDisburseEndpoints:
    def test_charge_returns_201_on_approved(self, monkeypatch):
        monkeypatch.setenv("CELERO_SECURITY_KEY", "sk-test")
        # Create artist + vault
        resp = client.post("/artists/", json={"name": "Charge Approved Artist"})
        aid = resp.json()["id"]

        # Manually set vault ID via API mock pattern
        db = _TestSession()
        artist = db.query(Artist).filter(Artist.id == aid).first()
        artist.celero_customer_vault_id = "vault-charge-001"
        # Create anomaly and claim
        from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
        anom = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=aid,
            category=AnomalyCategory.ROYALTY,
            subtype="MISSING",
            severity=AnomalySeverity.HIGH,
            confidence_score=0.9,
            status=AnomalyStatus.OPEN,
        )
        db.add(anom)
        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=aid,
            anomaly_id=anom.id,
            claim_type="ROYALTY",
            status=ClaimStatus.PAID,
            recovered_amount=800.0,
            currency="USD",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(claim)
        db.commit()
        claim_id = claim.id
        db.close()

        mock_response = CeleroResponse(
            raw="response=1&transactionid=TXN-CHARGE-OK&authcode=AUTH1&response_code=100",
            response=RESPONSE_APPROVED,
            response_text="SUCCESS",
            transaction_id="TXN-CHARGE-OK",
            auth_code="AUTH1",
            response_code="100",
        )
        with patch("XR7.celero.client.CeleroClient.charge", return_value=mock_response):
            resp = client.post(
                f"/artists/{aid}/celero/charge",
                json={"claim_id": claim_id},
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["type"] == "CHARGE"
        assert data["status"] == "APPROVED"
        assert data["amount"] == pytest.approx(80.0)  # 10% of 800

    def test_disburse_returns_201_on_approved(self, monkeypatch):
        monkeypatch.setenv("CELERO_SECURITY_KEY", "sk-test")
        resp = client.post("/artists/", json={"name": "Disburse Test Artist"})
        aid = resp.json()["id"]
        db = _TestSession()
        artist = db.query(Artist).filter(Artist.id == aid).first()
        artist.celero_customer_vault_id = "vault-disburse-001"
        db.commit()
        db.close()

        mock_response = CeleroResponse(
            raw="response=1&transactionid=TXN-DISBURSE-OK",
            response=RESPONSE_APPROVED,
            response_text="SUCCESS",
            transaction_id="TXN-DISBURSE-OK",
        )
        with patch("XR7.celero.client.CeleroClient.disburse", return_value=mock_response):
            resp = client.post(
                f"/artists/{aid}/celero/disburse",
                json={"amount": 720.0, "currency": "USD"},
            )
        assert resp.status_code == 201
        data = resp.json()
        assert data["type"] == "DISBURSEMENT"
        assert data["amount"] == pytest.approx(720.0)

    def test_disburse_zero_amount_returns_400(self, monkeypatch):
        monkeypatch.setenv("CELERO_SECURITY_KEY", "sk-test")
        resp = client.post("/artists/", json={"name": "Zero Disburse Artist"})
        aid = resp.json()["id"]
        db = _TestSession()
        a = db.query(Artist).filter(Artist.id == aid).first()
        a.celero_customer_vault_id = "vault-zero"
        db.commit()
        db.close()
        resp = client.post(f"/artists/{aid}/celero/disburse", json={"amount": 0})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# API: Webhook receiver
# ---------------------------------------------------------------------------

class TestWebhookEndpoint:
    def _post_webhook(self, body: bytes, secret: str = "") -> httpx.Response:
        if secret:
            sig = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        else:
            sig = ""
        return client.post(
            "/celero/webhook",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Celero-Signature": sig,
            },
        )

    def test_valid_event_returns_200(self, monkeypatch):
        monkeypatch.setenv("CELERO_WEBHOOK_SECRET", "wh-secret")
        body = json.dumps({
            "event_type": "transaction.approved",
            "transaction_id": "nonexistent-for-webhook-test",
        }).encode()
        resp = self._post_webhook(body, "wh-secret")
        assert resp.status_code == 200
        assert resp.json()["received"] is True

    def test_invalid_signature_returns_401(self, monkeypatch):
        monkeypatch.setenv("CELERO_WEBHOOK_SECRET", "wh-secret")
        body = b'{"event_type":"transaction.approved","transaction_id":"X"}'
        resp = self._post_webhook(body, "wrong-secret")
        assert resp.status_code == 401

    def test_invalid_json_returns_400(self, monkeypatch):
        monkeypatch.delenv("CELERO_WEBHOOK_SECRET", raising=False)
        monkeypatch.setenv("XR7_ENV", "development")
        resp = client.post(
            "/celero/webhook",
            content=b"not-json",
            headers={"Content-Type": "application/json", "X-Celero-Signature": ""},
        )
        assert resp.status_code == 400
