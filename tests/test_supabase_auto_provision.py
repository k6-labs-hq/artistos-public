"""
First-time sign-in via /auth/supabase/exchange auto-provisions an Artist row.

Background: closed-beta UX means a new user signs into Supabase, gets a JWT,
posts it to /auth/supabase/exchange, and gets back an XR7 token. Before this
behavior, the exchange endpoint returned 403 if the Supabase user wasn't
already linked to an Artist row — meaning beta operators had to manually
create the row in the DB. Now the row is auto-provisioned.

These tests pin that contract.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.models.artist import Artist

client = TestClient(app)


# ── Test JWT issuance helpers (HS256 path; matches what verify_supabase_jwt accepts) ──


@pytest.fixture(autouse=True)
def _hs256_supabase_env(monkeypatch):
    """Configure the Supabase verifier for HS256 with a known shared secret.

    In production the new artistos-dev project uses ES256/JWKS; for these
    unit tests we use HS256 with a local secret because mocking JWKS fetch
    on every test is heavier than the test value justifies.
    """
    monkeypatch.setenv("SUPABASE_URL", "https://testproj.supabase.co")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "test-secret-for-auto-provision")
    monkeypatch.setenv("SUPABASE_JWT_AUDIENCE", "authenticated")


@pytest.fixture(autouse=True)
def _clear_jwks_cache():
    from XR7.auth import supabase as sb

    sb._jwk_client.cache_clear()
    yield
    sb._jwk_client.cache_clear()


def _issue_supabase_token(
    *, sub: str, email: str | None = None, artist_name: str | None = None
) -> str:
    """Issue an HS256 token shaped like a real Supabase access token."""
    claims: dict = {
        "sub": sub,
        "aud": "authenticated",
        "iss": "https://testproj.supabase.co/auth/v1",
        "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
    }
    if email:
        claims["email"] = email
    if artist_name:
        claims["user_metadata"] = {"artist_name": artist_name}
    return pyjwt.encode(claims, "test-secret-for-auto-provision", algorithm="HS256")


# ── Tests ──────────────────────────────────────────────────────────────────


def _count_artists_for(supabase_uid: str) -> int:
    db = _TestSession()
    try:
        return db.query(Artist).filter(Artist.supabase_user_id == supabase_uid).count()
    finally:
        db.close()


def test_first_signin_creates_artist_row():
    """A Supabase user with no existing Artist gets one created on first exchange."""
    supabase_uid = str(uuid.uuid4())
    assert _count_artists_for(supabase_uid) == 0

    token = _issue_supabase_token(
        sub=supabase_uid,
        email="firsttime@example.com",
        artist_name="Firsttime Artist",
    )
    resp = client.post(
        "/auth/supabase/exchange",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

    # Artist row exists, keyed by supabase_user_id
    db = _TestSession()
    try:
        artist = db.query(Artist).filter(Artist.supabase_user_id == supabase_uid).first()
        assert artist is not None
        assert artist.email == "firsttime@example.com"
        assert artist.name == "Firsttime Artist"  # used user_metadata.artist_name
        assert artist.country_code == "US"
    finally:
        db.close()


def test_second_signin_reuses_existing_artist():
    """Subsequent sign-ins find the row and don't create duplicates."""
    supabase_uid = str(uuid.uuid4())
    token = _issue_supabase_token(sub=supabase_uid, email="repeat@example.com")

    # First exchange — creates
    resp1 = client.post(
        "/auth/supabase/exchange",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp1.status_code == 200
    assert _count_artists_for(supabase_uid) == 1

    # Second exchange — must find the existing row, not create a second one
    resp2 = client.post(
        "/auth/supabase/exchange",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp2.status_code == 200
    assert _count_artists_for(supabase_uid) == 1


def test_name_falls_back_to_email_local_part_when_no_metadata():
    """If user_metadata.artist_name is missing, use the email local-part."""
    supabase_uid = str(uuid.uuid4())
    token = _issue_supabase_token(sub=supabase_uid, email="someone@artistmail.io")

    resp = client.post(
        "/auth/supabase/exchange",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    db = _TestSession()
    try:
        artist = db.query(Artist).filter(Artist.supabase_user_id == supabase_uid).first()
        assert artist.name == "someone"
    finally:
        db.close()


def test_existing_artist_matched_by_email_gets_supabase_uid_backfilled():
    """Pre-existing Artist with matching email gets its supabase_user_id set on first sign-in."""
    supabase_uid = str(uuid.uuid4())
    email = "preonboarded@example.com"

    # Pre-seed an Artist with email but no supabase_user_id (admin-onboarded path)
    db = _TestSession()
    artist_id = str(uuid.uuid4())
    db.add(
        Artist(
            id=artist_id,
            name="Pre-onboarded",
            email=email,
            supabase_user_id=None,
            country_code="US",
            created_at=datetime.now(timezone.utc),
        )
    )
    db.commit()
    db.close()

    token = _issue_supabase_token(sub=supabase_uid, email=email)
    resp = client.post(
        "/auth/supabase/exchange",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    # The pre-existing artist now has supabase_user_id set, no new row created
    db = _TestSession()
    try:
        rows = db.query(Artist).filter(Artist.email == email).all()
        assert len(rows) == 1
        assert rows[0].id == artist_id
        assert rows[0].supabase_user_id == supabase_uid
    finally:
        db.close()


def test_token_without_sub_rejected_at_401_not_provisioned():
    """A token missing sub doesn't get an Artist row silently."""
    # An HS256 token without 'sub' — verify_supabase_jwt rejects it at 401
    bogus = pyjwt.encode(
        {"aud": "authenticated"},
        "test-secret-for-auto-provision",
        algorithm="HS256",
    )
    resp = client.post(
        "/auth/supabase/exchange",
        headers={"Authorization": f"Bearer {bogus}"},
    )
    assert resp.status_code == 401
