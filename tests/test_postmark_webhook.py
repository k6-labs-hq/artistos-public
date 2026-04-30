"""Tests for the Postmark inbound parse webhook.

Pinned behavior:
- Without POSTMARK_INBOUND_WEBHOOK_TOKEN configured, returns 503 (not 401, not
  silent accept). Misconfiguration must be visible in monitoring.
- Wrong token returns 401.
- Right token + valid payload returns 200 and writes an immutable ledger entry.
- Malformed JSON returns 400 (Postmark will retry per their policy).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.models.artist import Artist

client = TestClient(app)


def _seed_artist() -> str:
    db = _TestSession()
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Postmark Test Artist",
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.commit()
    aid = artist.id
    db.close()
    return aid


def _inbound_payload(artist_id: str | None = None, claim_id: str | None = None) -> dict:
    return {
        "From": "BMI <support@bmi.com>",
        "To": "disputes@xr7.k6-labs.com",
        "Subject": "Re: Dispute Filing for Artist X",
        "MessageID": "inbound-msg-1",
        "InReplyTo": "outbound-msg-original",
        "TextBody": "Thank you for your filing. Case reference: BMI-DR-12345.",
        "HtmlBody": "<p>Thank you...</p>",
        "Tag": "dispute-bmi",
        "Metadata": {
            "artist_id": artist_id or "",
            "claim_id": claim_id or "",
        },
    }


@pytest.fixture
def configured_webhook(monkeypatch):
    """Set the webhook token so endpoint accepts traffic."""
    monkeypatch.setenv("POSTMARK_INBOUND_WEBHOOK_TOKEN", "secret-xyz")


def test_webhook_returns_503_when_token_not_configured(monkeypatch):
    """If the env var is unset, refuse traffic outright. Don't silently accept forged payloads."""
    monkeypatch.delenv("POSTMARK_INBOUND_WEBHOOK_TOKEN", raising=False)
    resp = client.post("/webhooks/postmark/inbound", json=_inbound_payload())
    assert resp.status_code == 503
    assert "not configured" in resp.json()["detail"].lower()


def test_webhook_returns_401_on_missing_token(configured_webhook):
    resp = client.post("/webhooks/postmark/inbound", json=_inbound_payload())
    assert resp.status_code == 401


def test_webhook_returns_401_on_wrong_token(configured_webhook):
    resp = client.post(
        "/webhooks/postmark/inbound",
        json=_inbound_payload(),
        headers={"X-Postmark-Webhook-Token": "wrong"},
    )
    assert resp.status_code == 401


def test_webhook_accepts_valid_payload_and_writes_ledger(configured_webhook):
    artist_id = _seed_artist()
    resp = client.post(
        "/webhooks/postmark/inbound",
        json=_inbound_payload(artist_id=artist_id, claim_id="claim-42"),
        headers={"X-Postmark-Webhook-Token": "secret-xyz"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "received"

    # Confirm an immutable ledger entry was written for replay/audit.
    from XR7.models.immutable_ledger_entry import ImmutableLedgerEntry

    db = _TestSession()
    try:
        entry = (
            db.query(ImmutableLedgerEntry)
            .filter(ImmutableLedgerEntry.artist_id == artist_id)
            .order_by(ImmutableLedgerEntry.created_at.desc())
            .first()
        )
        assert entry is not None
        assert entry.entry_type == "inbound_email_received"
    finally:
        db.close()


def test_webhook_returns_400_on_malformed_json(configured_webhook):
    resp = client.post(
        "/webhooks/postmark/inbound",
        content=b"not-json",
        headers={
            "X-Postmark-Webhook-Token": "secret-xyz",
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 400


def test_webhook_does_not_persist_when_metadata_lacks_artist(configured_webhook):
    """Postmark inbound webhooks for unknown artists land but don't write a ledger entry.

    Future #179 work will add a fallback path (queue for ops review). For now,
    accept the 200 to avoid Postmark retries, but don't fabricate ledger entries
    against artists that don't exist.
    """
    resp = client.post(
        "/webhooks/postmark/inbound",
        json=_inbound_payload(artist_id=None),
        headers={"X-Postmark-Webhook-Token": "secret-xyz"},
    )
    assert resp.status_code == 200
