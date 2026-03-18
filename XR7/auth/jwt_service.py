from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any


class JWTValidationError(ValueError):
    pass


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(raw: str) -> bytes:
    padded = raw + "=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


class JWTService:
    def __init__(self) -> None:
        self.secret = os.getenv("XR7_JWT_SECRET", "xr7-dev-jwt-secret-change-me").encode("utf-8")
        self.issuer = os.getenv("XR7_JWT_ISSUER", "xr7-engine")
        self.audience = os.getenv("XR7_JWT_AUDIENCE", "xr7-clients")
        self.access_ttl_minutes = int(os.getenv("XR7_JWT_ACCESS_TTL_MINUTES", "60"))

    def issue_token(self, subject: str, role: str, extra: dict[str, Any] | None = None) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": subject,
            "role": role,
            "iss": self.issuer,
            "aud": self.audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self.access_ttl_minutes)).timestamp()),
        }
        if extra:
            payload.update(extra)

        header = {"alg": "HS256", "typ": "JWT"}
        signing_input = f"{_b64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))}.{_b64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))}"
        signature = hmac.new(self.secret, signing_input.encode("ascii"), hashlib.sha256).digest()
        return f"{signing_input}.{_b64url_encode(signature)}"

    def verify_token(self, token: str) -> dict[str, Any]:
        try:
            head_b64, payload_b64, sig_b64 = token.split(".")
        except ValueError as exc:
            raise JWTValidationError("Malformed token") from exc

        signing_input = f"{head_b64}.{payload_b64}"
        expected_sig = hmac.new(self.secret, signing_input.encode("ascii"), hashlib.sha256).digest()
        provided_sig = _b64url_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, provided_sig):
            raise JWTValidationError("Invalid signature")

        header = json.loads(_b64url_decode(head_b64).decode("utf-8"))
        if header.get("alg") != "HS256":
            raise JWTValidationError("Unsupported JWT algorithm")

        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))

        now_ts = int(datetime.now(timezone.utc).timestamp())
        if int(payload.get("exp", 0)) < now_ts:
            raise JWTValidationError("Token expired")
        if payload.get("iss") != self.issuer:
            raise JWTValidationError("Invalid token issuer")
        if payload.get("aud") != self.audience:
            raise JWTValidationError("Invalid token audience")
        if not payload.get("sub"):
            raise JWTValidationError("Token subject missing")
        if not payload.get("role"):
            raise JWTValidationError("Token role missing")

        return payload


jwt_service = JWTService()
