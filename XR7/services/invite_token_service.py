"""Invite token generation and validation service."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt

from xr7_common.settings import settings


class InviteTokenGenerator:
    """Generate and validate cryptographically signed invite tokens."""

    # Default token expiration: 72 hours
    DEFAULT_EXPIRATION_HOURS = 72

    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        """Initialize with JWT secret and algorithm.

        Args:
            secret_key: JWT secret key (defaults to XR7_JWT_SECRET from env)
            algorithm: JWT algorithm (HS256, RS256, etc.)
        """
        self.secret_key = secret_key or settings.jwt_secret
        self.algorithm = algorithm

    def generate(
        self,
        invite_id: str,
        recipient_name: str,
        recipient_email: Optional[str] = None,
        is_vip: bool = False,
        referring_agent_id: Optional[str] = None,
        campaign: Optional[str] = None,
        expiration_hours: int = DEFAULT_EXPIRATION_HOURS,
    ) -> str:
        """Generate a signed invite token.

        Args:
            invite_id: Unique invite record ID
            recipient_name: Name of the invitee (no sex assumptions)
            recipient_email: Email address (optional)
            is_vip: VIP flag for priority features
            referring_agent_id: ID of referring agent
            campaign: Campaign identifier
            expiration_hours: Token lifetime in hours

        Returns:
            JWT token string suitable for embedding in invite link

        Raises:
            ValueError: If required fields are missing
        """
        if not invite_id:
            raise ValueError("invite_id is required")
        if not recipient_name:
            raise ValueError("recipient_name is required")

        now = datetime.now(timezone.utc)
        exp = now + timedelta(hours=expiration_hours)

        payload = {
            "invite_id": invite_id,
            "recipient_name": recipient_name,
            "recipient_email": recipient_email or "",
            "is_vip": is_vip,
            "referring_agent_id": referring_agent_id or "",
            "campaign": campaign or "",
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def validate(self, token: str) -> dict[str, Any]:
        """Validate and decode an invite token.

        Args:
            token: JWT token string

        Returns:
            Decoded payload dict if valid

        Raises:
            jwt.InvalidTokenError: If token is invalid, expired, or tampered
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError as exc:
            raise jwt.InvalidTokenError("Invite token has expired") from exc
        except jwt.InvalidSignatureError as exc:
            raise jwt.InvalidTokenError("Invalid invite token signature") from exc
        except jwt.DecodeError as exc:
            raise jwt.InvalidTokenError("Failed to decode invite token") from exc

    def is_valid(self, token: str) -> bool:
        """Quick check if token is valid (no exception raised).

        Args:
            token: JWT token string

        Returns:
            True if token is valid, False otherwise
        """
        try:
            self.validate(token)
            return True
        except jwt.InvalidTokenError:
            return False


# Global singleton
invite_token_generator = InviteTokenGenerator()
