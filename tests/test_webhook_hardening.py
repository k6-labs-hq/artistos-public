"""
Test outbound webhook retry hardening and signature verification.
"""

from __future__ import annotations

import json
import uuid
from unittest.mock import MagicMock, patch

import pytest

from tests.conftest import TestSession
from XR7.models.artist import Artist
from XR7.models.webhook_event import WebhookEvent, WebhookEventStatus
from XR7.services.webhook_delivery import OutboundWebhookService


class TestWebhookHardening:
    @pytest.fixture
    def setup_artist(self):
        """Create test artist."""
        db = TestSession()
        try:
            artist_id = str(uuid.uuid4())
            artist = Artist(id=artist_id, name="Test Artist", email=f"artist_{artist_id[:8]}@test.com")
            db.add(artist)
            db.commit()
            return artist_id
        finally:
            db.close()

    def test_hmac_signature_generation(self, setup_artist):
        """Verify webhook payloads are signed with HMAC-SHA256."""
        db = TestSession()
        try:
            artist_id = setup_artist
            service = OutboundWebhookService(db, secret="test-secret-key")

            payload_dict = {"event": "claim.created", "artist_id": artist_id}
            raw_payload = json.dumps(payload_dict, default=str, sort_keys=True)
            signature = service._sign(raw_payload)

            # Signature should be hex string
            assert isinstance(signature, str)
            assert len(signature) == 64  # SHA-256 hex is 64 chars

            # Verify signature is deterministic
            signature2 = service._sign(raw_payload)
            assert signature == signature2

        finally:
            db.close()

    def test_signature_verification_rejects_tampered_payload(self, setup_artist):
        """Verify that modified payloads fail signature verification."""
        db = TestSession()
        try:
            artist_id = setup_artist
            service = OutboundWebhookService(db, secret="test-secret-key")

            original_payload_dict = {"event": "claim.created", "artist_id": artist_id, "amount": 1000}
            original_payload = json.dumps(original_payload_dict, default=str, sort_keys=True)
            signature = service._sign(original_payload)

            # Tamper with payload
            tampered_payload_dict = {"event": "claim.created", "artist_id": artist_id, "amount": 9999}
            tampered_payload = json.dumps(tampered_payload_dict, default=str, sort_keys=True)
            tampered_signature = service._sign(tampered_payload)

            # Signatures should be different
            assert signature != tampered_signature

        finally:
            db.close()

    @patch("httpx.Client")
    def test_delivery_includes_signature_header(self, mock_client_class, setup_artist):
        """Verify that webhook delivery includes X-XR7-Signature header."""
        db = TestSession()
        try:
            artist_id = setup_artist

            # Mock successful HTTP response
            mock_response = MagicMock()
            mock_response.status_code = 200

            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post = MagicMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            # Queue and deliver event
            service = OutboundWebhookService(db, secret="test-secret", endpoint="https://example.com/webhook")
            event = service.queue_event(
                event_type="claim.created",
                payload={"claim_id": "test-123", "artist_id": artist_id},
            )

            result = service.deliver_event(event)

            assert result is True
            assert event.status == WebhookEventStatus.PROCESSED

            # Verify that httpx.Client.post was called with signature header
            assert mock_client.post.called
            call_args = mock_client.post.call_args
            headers = call_args.kwargs.get("headers", {})
            assert "X-XR7-Signature" in headers
            assert "X-XR7-Event-Type" in headers
            assert headers["X-XR7-Event-Type"] == "claim.created"

        finally:
            db.close()

    @patch("httpx.Client")
    def test_delivery_retries_on_failure(self, mock_client_class, setup_artist):
        """Verify that failed deliveries are marked for retry."""
        db = TestSession()
        try:
            artist_id = setup_artist

            # Mock failed HTTP response
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock(side_effect=Exception("Connection timeout"))

            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.post = MagicMock(return_value=mock_response)
            mock_client_class.return_value = mock_client

            # Queue and deliver event
            service = OutboundWebhookService(db, secret="test-secret", endpoint="https://example.com/webhook")
            event = service.queue_event(
                event_type="claim.created",
                payload={"claim_id": "test-123", "artist_id": artist_id},
            )

            result = service.deliver_event(event)

            assert result is False
            assert event.status == WebhookEventStatus.FAILED
            assert event.attempts == 1
            assert "Connection timeout" in event.processing_error

        finally:
            db.close()

    def test_celery_task_configuration(self):
        """Verify Celery task has correct retry configuration."""
        from XR7.tasks.webhooks import deliver_webhook_event

        # Check task configuration
        assert deliver_webhook_event.autoretry_for == (Exception,)
        assert deliver_webhook_event.retry_backoff is True
        assert deliver_webhook_event.retry_kwargs["max_retries"] == 5

        # Verify exponential backoff default (Celery uses 2^n formula by default)
        # With retry_backoff=True and no custom retry_backoff_max, Celery will use:
        # Retry 1: 2^1 = 2s
        # Retry 2: 2^2 = 4s
        # Retry 3: 2^3 = 8s
        # Retry 4: 2^4 = 16s
        # Retry 5: 2^5 = 32s
