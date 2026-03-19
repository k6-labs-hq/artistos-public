"""Tests for private XR7 invite system."""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from XR7.api.app import app
from XR7.models import (
    Invite,
    InviteChannel,
    InviteEvent,
    InviteRole,
    InviteStatus,
    SessionLocal,
)
from XR7.services.invite_service import InviteService
from XR7.services.invite_token_service import invite_token_generator, InviteTokenGenerator
from XR7.services.invite_messaging_service import InviteMessagingService


client = TestClient(app)


@pytest.fixture
def db():
    """Create a test database session."""
    db = SessionLocal()
    yield db
    db.close()


class TestInviteTokenGenerator:
    """Test invite token generation and validation."""

    def test_generate_token(self):
        """Test basic token generation."""
        generator = InviteTokenGenerator()
        token = generator.generate(
            invite_id="test-123",
            recipient_name="Jane Smith",
            recipient_email="jane@example.com",
            is_vip=False,
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_validate_token(self):
        """Test token validation."""
        generator = InviteTokenGenerator()
        token = generator.generate(
            invite_id="test-456",
            recipient_name="John Doe",
            is_vip=True,
        )

        payload = generator.validate(token)
        assert payload["invite_id"] == "test-456"
        assert payload["recipient_name"] == "John Doe"
        assert payload["is_vip"] is True

    def test_token_expiration(self):
        """Test that expired tokens are rejected."""
        generator = InviteTokenGenerator()
        token = generator.generate(
            invite_id="test-expired",
            recipient_name="Creator",
            expiration_hours=-1,  # Already expired
        )

        # Should raise InvalidTokenError
        import jwt
        with pytest.raises(jwt.InvalidTokenError):
            generator.validate(token)

    def test_invalid_token_signature(self):
        """Test that tampered tokens are rejected."""
        generator = InviteTokenGenerator()
        token = generator.generate(
            invite_id="test-tamper",
            recipient_name="Creator",
        )

        # Tamper with token
        tampered = token[:-10] + "corrupted!!"

        import jwt
        with pytest.raises(jwt.InvalidTokenError):
            generator.validate(tampered)

    def test_is_valid_without_exception(self):
        """Test is_valid method returns boolean."""
        generator = InviteTokenGenerator()
        token = generator.generate(
            invite_id="test-bool",
            recipient_name="Creator",
        )

        assert generator.is_valid(token) is True
        assert generator.is_valid("invalid-token") is False


class TestInviteService:
    """Test core invite service."""

    def test_create_invite(self, db: Session):
        """Test creating an invite."""
        service = InviteService(db)

        invite, token = service.create_invite(
            recipient_name="Jane Smith",
            recipient_email="jane@example.com",
            channel=InviteChannel.EMAIL,
            role=InviteRole.ARTIST,
            is_vip=False,
        )

        assert invite.id is not None
        assert invite.recipient_name == "Jane Smith"
        assert invite.recipient_email == "jane@example.com"
        assert invite.status == InviteStatus.PENDING
        assert token is not None

        # Check event was recorded
        events = db.query(InviteEvent).filter(
            InviteEvent.invite_id == invite.id
        ).all()
        assert len(events) > 0
        assert events[0].event_type == "created"

    def test_send_invite(self, db: Session):
        """Test marking invite as sent."""
        service = InviteService(db)

        invite, _ = service.create_invite(
            recipient_name="Creator",
            channel=InviteChannel.EMAIL,
        )

        invite = service.send_invite(invite.id)
        assert invite.status == InviteStatus.SENT
        assert invite.sent_at is not None

    def test_validate_invite(self, db: Session):
        """Test invite token validation."""
        service = InviteService(db)

        invite, token = service.create_invite(
            recipient_name="Jane Smith",
            channel=InviteChannel.EMAIL,
        )

        service.send_invite(invite.id)

        # Validate
        validation = service.validate_invite(token)
        assert validation["is_valid"] is True
        assert validation["invite_id"] == invite.id
        assert validation["recipient_name"] == "Jane Smith"

    def test_open_invite(self, db: Session):
        """Test recording invite link open."""
        service = InviteService(db)

        invite, token = service.create_invite(
            recipient_name="Creator",
        )
        service.send_invite(invite.id)

        invite = service.open_invite(token, ip_address="192.168.1.1")
        assert invite.status == InviteStatus.OPENED
        assert invite.opened_at is not None

    def test_redeem_invite(self, db: Session):
        """Test redeeming an invite and marking as single-use."""
        service = InviteService(db)

        invite, token = service.create_invite(
            recipient_name="Jane Smith",
        )
        service.send_invite(invite.id)
        service.open_invite(token)

        # Redeem
        redeemed = service.redeem_invite(token, artist_id="artist-123")
        assert redeemed.status == InviteStatus.REDEEMED
        assert redeemed.redeemed_at is not None
        assert redeemed.redeemed_by_artist_id == "artist-123"
        assert redeemed.is_single_use_consumed is True

        # Try to redeem again - should fail
        with pytest.raises(ValueError):
            service.redeem_invite(token, artist_id="artist-456")

    def test_invite_expiration(self, db: Session):
        """Test that expired invites cannot be redeemed."""
        service = InviteService(db)

        # Create invite with 1-hour expiration, but manually set to expired
        invite, token = service.create_invite(
            recipient_name="Creator",
        )

        # Manually expire the token
        invite.token_expiration = datetime.now(timezone.utc) - timedelta(hours=1)
        db.commit()

        # Try to validate - should fail
        validation = service.validate_invite(token)
        assert validation["is_valid"] is False
        assert "expired" in validation["error"].lower()

    def test_revoke_invite(self, db: Session):
        """Test revoking an invite."""
        service = InviteService(db)

        invite, _ = service.create_invite(recipient_name="Creator")

        revoked = service.revoke_invite(invite.id, reason="Test revocation")
        assert revoked.status == InviteStatus.REVOKED

    def test_list_invites(self, db: Session):
        """Test listing invites with filters."""
        service = InviteService(db)

        # Create multiple invites
        for i in range(5):
            service.create_invite(
                recipient_name=f"Creator {i}",
                campaign="test_campaign" if i < 3 else "other",
            )

        # List all
        invites, total = service.list_invites()
        assert total >= 5

        # List by campaign
        invites, total = service.list_invites(campaign="test_campaign")
        assert total >= 3

        # List by status
        invites, total = service.list_invites(status=InviteStatus.PENDING)
        assert total >= 5

    def test_get_analytics(self, db: Session):
        """Test analytics calculation."""
        service = InviteService(db)

        # Create and process multiple invites
        for i in range(5):
            invite, token = service.create_invite(
                recipient_name=f"Creator {i}",
                campaign="test_campaign",
                role=InviteRole.ARTIST,
            )
            service.send_invite(invite.id)
            if i < 3:
                service.open_invite(token)
            if i < 2:
                service.redeem_invite(token, artist_id=f"artist-{i}")

        analytics = service.get_analytics(campaign="test_campaign")

        assert analytics["invites_created"] >= 5
        assert analytics["invites_sent"] >= 5
        assert analytics["invites_opened"] >= 3
        assert analytics["invites_redeemed"] >= 2
        assert "open_rate_percent" in analytics
        assert "redemption_rate_percent" in analytics
        assert "role_distribution" in analytics


class TestInviteAPI:
    """Test API endpoints."""

    def test_generate_invite_endpoint(self):
        """Test POST /invites/generate endpoint."""
        response = client.post(
            "/invites/generate",
            json={
                "recipient_name": "Jane Smith",
                "recipient_email": "jane@example.com",
                "channel": "email",
                "role": "artist",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["recipient_name"] == "Jane Smith"
        assert data["invite_token"] is not None
        assert data["status"] == "sent"

    def test_validate_invite_endpoint(self):
        """Test POST /invites/validate endpoint."""
        # First generate an invite
        gen_response = client.post(
            "/invites/generate",
            json={
                "recipient_name": "Test Creator",
                "channel": "email",
            },
        )
        token = gen_response.json()["invite_token"]

        # Then validate it
        response = client.post(
            "/invites/validate",
            json={"invite_token": token},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["recipient_name"] == "Test Creator"

    def test_validate_invalid_token(self):
        """Test validation with invalid token."""
        response = client.post(
            "/invites/validate",
            json={"invite_token": "invalid-token-xyz"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert "error" in data

    def test_list_invites_endpoint(self):
        """Test GET /invites/ endpoint."""
        response = client.get("/invites/")

        assert response.status_code == 200
        data = response.json()
        assert "invites" in data
        assert "total" in data
        assert isinstance(data["invites"], list)

    def test_analytics_endpoint(self):
        """Test GET /invites/analytics/summary endpoint."""
        response = client.get("/invites/analytics/summary?days=30")

        assert response.status_code == 200
        data = response.json()
        assert "invites_created" in data
        assert "invites_sent" in data
        assert "invites_opened" in data
        assert "open_rate_percent" in data

    def test_quick_generate_endpoint(self):
        """Test dashboard quick generate endpoint."""
        response = client.post(
            "/invites/dashboard/quick-generate",
            json={
                "recipient_name": "Amy Wong",
                "recipient_email": "amy@example.com",
                "role": "artist",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "invite_link" in data
        assert "/onboarding/invite/" in data["invite_link"]

    def test_email_trigger_endpoint(self):
        """Test email-triggered invite endpoint."""
        response = client.post(
            "/invites/email-trigger",
            json={
                "sender_email": "inquiry@creator.com",
                "sender_name": "Creative Artist",
                "message_body": "I need analysis help",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "/onboarding/invite/" in data["invite_link"]


class TestInviteMessagingTemplates:
    """Test message templates."""

    def test_email_invitation_template(self):
        """Test email invitation template."""
        template = InviteMessagingService.get_email_invitation(
            recipient_name="Jane Smith",
            invite_link="https://xr7.app/invite/abc123",
        )

        assert "subject" in template
        assert "Jane Smith" in template["subject"]
        assert "body_text" in template
        assert "body_html" in template
        assert "Jane Smith" in template["body_text"]
        assert "https://xr7.app/invite/abc123" in template["body_text"]

    def test_email_with_custom_message(self):
        """Test email template with custom message."""
        template = InviteMessagingService.get_email_invitation(
            recipient_name="Creator",
            invite_link="https://xr7.app/invite/xyz",
            custom_message="VIP Early Access",
        )

        assert "VIP Early Access" in template["body_text"]

    def test_instagram_dm_template(self):
        """Test Instagram DM template."""
        message = InviteMessagingService.get_instagram_dm(
            recipient_name="Jane",
            invite_link="https://xr7.app/invite/abc123",
        )

        assert isinstance(message, str)
        assert "Jane" in message
        assert "https://xr7.app/invite/abc123" in message

    def test_sms_template(self):
        """Test SMS template."""
        message = InviteMessagingService.get_sms(
            recipient_name="Creator",
            invite_link="https://xr7.app/invite/short",
        )

        assert isinstance(message, str)
        assert len(message) <= 160  # SMS limit
        assert "https://xr7.app/invite/short" in message

    def test_message_by_channel(self):
        """Test get_message_by_channel method."""
        link = "https://xr7.app/invite/abc123"

        email = InviteMessagingService.get_message_by_channel(
            InviteChannel.EMAIL,
            "Jane",
            link,
        )
        assert isinstance(email, dict)
        assert "subject" in email

        instagram = InviteMessagingService.get_message_by_channel(
            InviteChannel.INSTAGRAM_DM,
            "Jane",
            link,
        )
        assert isinstance(instagram, str)

        sms = InviteMessagingService.get_message_by_channel(
            InviteChannel.SMS,
            "Jane",
            link,
        )
        assert isinstance(sms, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
