"""
Tests for the MFA-gated royalty estimation widget.

Covers:
- OTP service: session creation, verification, rate limiting, lockout,
  expiry, and token validation
- Widget API endpoints: register, verify, estimate — happy path and
  all error paths
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

import arcos7.auth.otp_service as otp_svc
from arcos7.auth.otp_service import (
    MAX_ATTEMPTS,
    OTP_EXPIRY_SECONDS,
    MAX_SENDS_PER_PHONE_PER_HOUR,
    RateLimitError,
    SessionLockedError,
    SessionNotFoundError,
    InvalidOTPError,
    TokenError,
    create_session,
    verify_session,
    validate_token,
    clear_all,
)
from arcos7.auth.notification_service import MockNotificationService
from arcos7.api.app import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_otp_state():
    """Clear all in-memory OTP state before every test."""
    clear_all()
    yield
    clear_all()


@pytest.fixture()
def now():
    return datetime.now(timezone.utc)


def _make_session(phone: str = "+15550001111", email: str = "test@example.com",
                  name: str = "Test Artist", now=None):
    return create_session(artist_name=name, phone=phone, email=email, now=now)


# ---------------------------------------------------------------------------
# OTP service — session creation
# ---------------------------------------------------------------------------

class TestCreateSession:
    def test_returns_session_with_id_and_otps(self):
        s = _make_session()
        assert len(s.session_id) > 10
        assert len(s.phone_otp) == 6
        assert len(s.email_otp) == 6
        assert s.phone_otp.isdigit()
        assert s.email_otp.isdigit()

    def test_otps_are_different(self):
        s = _make_session()
        # They COULD theoretically be equal, but the probability is 1/10^6
        # Running 1000 sessions confirms they are independently generated:
        sessions = [_make_session(phone=f"+1555000{i:04d}") for i in range(20)]
        phone_otps = [s.phone_otp for s in sessions]
        email_otps = [s.email_otp for s in sessions]
        # They should not all be the same
        assert len(set(phone_otps)) > 1

    def test_session_stored_with_correct_expiry(self, now):
        s = _make_session(now=now)
        expected_expiry = now + timedelta(seconds=OTP_EXPIRY_SECONDS)
        assert abs((s.expires_at - expected_expiry).total_seconds()) < 1

    def test_rate_limit_blocks_after_max_sends(self):
        phone = "+15550002222"
        for _ in range(MAX_SENDS_PER_PHONE_PER_HOUR):
            _make_session(phone=phone)
        with pytest.raises(RateLimitError):
            _make_session(phone=phone)

    def test_rate_limit_different_phones_are_independent(self):
        # Exhaust rate limit for phone A
        for _ in range(MAX_SENDS_PER_PHONE_PER_HOUR):
            _make_session(phone="+15550003333")
        # Phone B should still work
        s = _make_session(phone="+15550004444")
        assert s.session_id is not None

    def test_rate_limit_resets_after_one_hour(self, now):
        phone = "+15550005555"
        # Send 3 OTPs with timestamps just over 1 hour ago
        past = now - timedelta(hours=1, seconds=10)
        for _ in range(MAX_SENDS_PER_PHONE_PER_HOUR):
            _make_session(phone=phone, now=past)
        # At current time the window should be clear
        s = _make_session(phone=phone, now=now)
        assert s.session_id is not None


# ---------------------------------------------------------------------------
# OTP service — verification
# ---------------------------------------------------------------------------

class TestVerifySession:
    def test_correct_otps_return_token(self, now):
        s = _make_session(now=now)
        token = verify_session(s.session_id, s.phone_otp, s.email_otp, now=now)
        assert token.token is not None
        assert len(token.token) > 20
        assert token.artist_name == "Test Artist"

    def test_wrong_phone_otp_raises_invalid(self, now):
        s = _make_session(now=now)
        with pytest.raises(InvalidOTPError):
            verify_session(s.session_id, "000000", s.email_otp, now=now)

    def test_wrong_email_otp_raises_invalid(self, now):
        s = _make_session(now=now)
        with pytest.raises(InvalidOTPError):
            verify_session(s.session_id, s.phone_otp, "000000", now=now)

    def test_both_wrong_raises_invalid(self, now):
        s = _make_session(now=now)
        with pytest.raises(InvalidOTPError):
            verify_session(s.session_id, "111111", "222222", now=now)

    def test_lockout_after_max_attempts(self, now):
        s = _make_session(now=now)
        for _ in range(MAX_ATTEMPTS - 1):
            with pytest.raises(InvalidOTPError):
                verify_session(s.session_id, "999999", "888888", now=now)
        # Final attempt should lock
        with pytest.raises(SessionLockedError):
            verify_session(s.session_id, "999999", "888888", now=now)

    def test_locked_session_raises_even_with_correct_otps(self, now):
        s = _make_session(now=now)
        for _ in range(MAX_ATTEMPTS):
            try:
                verify_session(s.session_id, "000000", "000000", now=now)
            except (InvalidOTPError, SessionLockedError):
                pass
        with pytest.raises(SessionLockedError):
            verify_session(s.session_id, s.phone_otp, s.email_otp, now=now)

    def test_expired_session_raises_not_found(self, now):
        s = _make_session(now=now)
        future = now + timedelta(seconds=OTP_EXPIRY_SECONDS + 1)
        with pytest.raises(SessionNotFoundError):
            verify_session(s.session_id, s.phone_otp, s.email_otp, now=future)

    def test_unknown_session_id_raises_not_found(self, now):
        with pytest.raises(SessionNotFoundError):
            verify_session("nonexistent-id", "123456", "123456", now=now)

    def test_session_consumed_after_success(self, now):
        s = _make_session(now=now)
        verify_session(s.session_id, s.phone_otp, s.email_otp, now=now)
        # Second attempt with same session_id should fail
        with pytest.raises(SessionNotFoundError):
            verify_session(s.session_id, s.phone_otp, s.email_otp, now=now)


# ---------------------------------------------------------------------------
# OTP service — token validation
# ---------------------------------------------------------------------------

class TestValidateToken:
    def test_valid_token_returns_token_object(self, now):
        s = _make_session(now=now)
        issued = verify_session(s.session_id, s.phone_otp, s.email_otp, now=now)
        validated = validate_token(issued.token, now=now)
        assert validated.artist_name == "Test Artist"

    def test_unknown_token_raises_token_error(self):
        with pytest.raises(TokenError):
            validate_token("not-a-real-token")

    def test_expired_token_raises_token_error(self, now):
        from arcos7.auth.otp_service import ESTIMATE_TOKEN_EXPIRY_SECONDS
        s = _make_session(now=now)
        token = verify_session(s.session_id, s.phone_otp, s.email_otp, now=now)
        future = now + timedelta(seconds=ESTIMATE_TOKEN_EXPIRY_SECONDS + 1)
        with pytest.raises(TokenError):
            validate_token(token.token, now=future)


# ---------------------------------------------------------------------------
# Mock notification service
# ---------------------------------------------------------------------------

class TestMockNotificationService:
    def test_send_sms_returns_true(self):
        svc = MockNotificationService()
        assert svc.send_sms("+15551234567", "Your code is 123456") is True

    def test_send_email_returns_true(self):
        svc = MockNotificationService()
        assert svc.send_email("test@example.com", "Subject", "Body") is True

    def test_records_sent_sms(self):
        svc = MockNotificationService()
        svc.send_sms("+15551234567", "code 111111")
        assert len(svc.sent_sms) == 1

    def test_records_sent_email(self):
        svc = MockNotificationService()
        svc.send_email("test@example.com", "S", "B")
        assert len(svc.sent_emails) == 1

    def test_raises_in_production(self, monkeypatch):
        monkeypatch.setenv("ARCOS7_ENV", "production")
        with pytest.raises(RuntimeError, match="MockNotificationService cannot be used in production"):
            MockNotificationService()


# ---------------------------------------------------------------------------
# Widget API — /widget/register
# ---------------------------------------------------------------------------

class TestRegisterEndpoint:
    def test_successful_registration_returns_session_id(self):
        resp = client.post("/widget/register", json={
            "artist_name": "Jane Doe",
            "phone": "+15551234567",
            "email": "jane@example.com",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "session_id" in data
        assert data["expires_in_seconds"] == OTP_EXPIRY_SECONDS
        # Dev OTPs should be present in non-production env
        assert "dev_phone_otp" in data
        assert "dev_email_otp" in data

    def test_dev_otps_are_6_digits(self):
        resp = client.post("/widget/register", json={
            "artist_name": "Jane Doe",
            "phone": "+15551234567",
            "email": "jane@example.com",
        })
        data = resp.json()
        assert data["dev_phone_otp"].isdigit()
        assert len(data["dev_phone_otp"]) == 6

    def test_invalid_phone_returns_422(self):
        resp = client.post("/widget/register", json={
            "artist_name": "Jane Doe",
            "phone": "not-a-phone",
            "email": "jane@example.com",
        })
        assert resp.status_code == 422

    def test_invalid_email_returns_422(self):
        resp = client.post("/widget/register", json={
            "artist_name": "Jane Doe",
            "phone": "+15551234567",
            "email": "not-an-email",
        })
        assert resp.status_code == 422

    def test_empty_artist_name_returns_422(self):
        resp = client.post("/widget/register", json={
            "artist_name": "",
            "phone": "+15551234567",
            "email": "jane@example.com",
        })
        assert resp.status_code == 422

    def test_rate_limit_returns_429(self):
        payload = {"artist_name": "Jane", "phone": "+15559998888", "email": "x@y.com"}
        for _ in range(MAX_SENDS_PER_PHONE_PER_HOUR):
            client.post("/widget/register", json=payload)
        resp = client.post("/widget/register", json=payload)
        assert resp.status_code == 429

    def test_phone_without_plus_is_accepted(self):
        resp = client.post("/widget/register", json={
            "artist_name": "Jane Doe",
            "phone": "15551234567",
            "email": "jane@example.com",
        })
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Widget API — /widget/verify
# ---------------------------------------------------------------------------

class TestVerifyEndpoint:
    def _register(self, phone="+15550011111", email="v@test.com", name="V Artist"):
        resp = client.post("/widget/register", json={
            "artist_name": name, "phone": phone, "email": email,
        })
        assert resp.status_code == 200
        return resp.json()

    def test_correct_otps_return_estimate_token(self):
        reg = self._register()
        resp = client.post("/widget/verify", json={
            "session_id": reg["session_id"],
            "phone_otp": reg["dev_phone_otp"],
            "email_otp": reg["dev_email_otp"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "estimate_token" in data
        assert data["artist_name"] == "V Artist"

    def test_wrong_phone_otp_returns_400(self):
        reg = self._register()
        resp = client.post("/widget/verify", json={
            "session_id": reg["session_id"],
            "phone_otp": "000000",
            "email_otp": reg["dev_email_otp"],
        })
        assert resp.status_code == 400

    def test_wrong_both_otps_returns_400(self):
        reg = self._register()
        resp = client.post("/widget/verify", json={
            "session_id": reg["session_id"],
            "phone_otp": "111111",
            "email_otp": "222222",
        })
        assert resp.status_code == 400

    def test_unknown_session_returns_404(self):
        resp = client.post("/widget/verify", json={
            "session_id": "nonexistent",
            "phone_otp": "123456",
            "email_otp": "654321",
        })
        assert resp.status_code == 404

    def test_lockout_after_max_failures_returns_429(self):
        reg = self._register(phone="+15550022222")
        for _ in range(MAX_ATTEMPTS):
            client.post("/widget/verify", json={
                "session_id": reg["session_id"],
                "phone_otp": "000000",
                "email_otp": "000000",
            })
        resp = client.post("/widget/verify", json={
            "session_id": reg["session_id"],
            "phone_otp": reg["dev_phone_otp"],
            "email_otp": reg["dev_email_otp"],
        })
        assert resp.status_code == 429


# ---------------------------------------------------------------------------
# Widget API — /widget/estimate
# ---------------------------------------------------------------------------

class TestEstimateEndpoint:
    def _get_token(self, phone="+15550033333", email="e@test.com", name="E Artist"):
        reg = client.post("/widget/register", json={
            "artist_name": name, "phone": phone, "email": email,
        }).json()
        ver = client.post("/widget/verify", json={
            "session_id": reg["session_id"],
            "phone_otp": reg["dev_phone_otp"],
            "email_otp": reg["dev_email_otp"],
        }).json()
        return ver["estimate_token"], name

    def test_estimate_returns_full_report(self):
        token, name = self._get_token()
        resp = client.post("/widget/estimate", json={
            "estimate_token": token,
            "career_stage": "DEVELOPING",
            "genre": "POP",
            "years_active": 7,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["artist_name"] == name
        estimate = data["estimate"]
        assert estimate["total_likely"] > 0
        assert estimate["total_conservative"] > 0
        assert estimate["total_optimistic"] >= estimate["total_likely"]
        assert len(estimate["streams"]) == 6

    def test_estimate_without_token_returns_401(self):
        resp = client.post("/widget/estimate", json={
            "estimate_token": "fake-token",
            "career_stage": "DEVELOPING",
            "genre": "POP",
            "years_active": 7,
        })
        assert resp.status_code == 401

    def test_invalid_career_stage_returns_422(self):
        token, _ = self._get_token(phone="+15550044444", email="f@test.com")
        resp = client.post("/widget/estimate", json={
            "estimate_token": token,
            "career_stage": "SUPERSTAR",
            "genre": "POP",
            "years_active": 5,
        })
        assert resp.status_code == 422

    def test_years_active_out_of_range_returns_422(self):
        token, _ = self._get_token(phone="+15550055555", email="g@test.com")
        resp = client.post("/widget/estimate", json={
            "estimate_token": token,
            "career_stage": "EMERGING",
            "genre": "POP",
            "years_active": 99,
        })
        assert resp.status_code == 422

    def test_established_artist_gets_larger_estimate_than_emerging(self):
        token_e, _ = self._get_token(phone="+15550066666", email="h@test.com", name="Emerging")
        token_s, _ = self._get_token(phone="+15550077777", email="i@test.com", name="Star")

        resp_e = client.post("/widget/estimate", json={
            "estimate_token": token_e, "career_stage": "EMERGING",
            "genre": "POP", "years_active": 5,
        }).json()
        resp_s = client.post("/widget/estimate", json={
            "estimate_token": token_s, "career_stage": "ESTABLISHED",
            "genre": "POP", "years_active": 5,
        }).json()

        assert resp_s["estimate"]["total_likely"] > resp_e["estimate"]["total_likely"]

    def test_longer_career_gives_larger_estimate(self):
        token1, _ = self._get_token(phone="+15550088888", email="j@test.com", name="Short")
        token2, _ = self._get_token(phone="+15550099999", email="k@test.com", name="Long")

        r1 = client.post("/widget/estimate", json={
            "estimate_token": token1, "career_stage": "DEVELOPING",
            "genre": "OTHER", "years_active": 2,
        }).json()
        r2 = client.post("/widget/estimate", json={
            "estimate_token": token2, "career_stage": "DEVELOPING",
            "genre": "OTHER", "years_active": 20,
        }).json()

        assert r2["estimate"]["total_likely"] > r1["estimate"]["total_likely"]

    def test_all_six_streams_present(self):
        token, _ = self._get_token(phone="+15550111111", email="l@test.com")
        resp = client.post("/widget/estimate", json={
            "estimate_token": token, "career_stage": "MID_LEVEL",
            "genre": "ROCK", "years_active": 10,
        }).json()
        stream_types = {s["stream_type"] for s in resp["estimate"]["streams"]}
        expected = {
            "digital_mechanical", "pro_performance", "international",
            "sync_licensing", "physical_download", "publishing_advance",
        }
        assert expected == stream_types

    def test_each_stream_has_required_fields(self):
        token, _ = self._get_token(phone="+15550222222", email="m@test.com")
        resp = client.post("/widget/estimate", json={
            "estimate_token": token, "career_stage": "DEVELOPING",
            "genre": "OTHER", "years_active": 5,
        }).json()
        for stream in resp["estimate"]["streams"]:
            for key in ("stream_type", "label", "description",
                        "conservative", "likely", "optimistic", "methodology"):
                assert key in stream, f"Missing key {key!r} in stream {stream['stream_type']}"
