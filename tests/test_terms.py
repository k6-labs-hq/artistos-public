"""
Tests for the Artist Recovery Services Agreement (Terms & Conditions) flow.

Covers:
- GET /terms returns text, version, and sha256
- POST /artists/{id}/terms/accept happy path (201)
- POST /artists/{id}/terms/accept is idempotent (returns existing record)
- POST /artists/{id}/terms/accept rejects wrong version (409)
- POST /artists/{id}/terms/accept rejects agreed=False (422)
- POST /artists/{id}/terms/accept rejects unknown artist (404)
- GET /artists/{id}/terms/status before acceptance
- GET /artists/{id}/terms/status after acceptance
- GET /artists/{id}/terms/status unknown artist (404)
- Statement upload gate: 403 without T&C, 201 after acceptance
- require_terms_accepted helper function behaviour
- Text and hash consistency: sha256 stored equals sha256 of served text
"""

from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.legal.terms import TERMS_TEXT, TERMS_VERSION, terms_text_sha256
from XR7.models.artist import Artist
from XR7.models.terms_acceptance import TermsAcceptance

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def artist():
    """Create a fresh artist in the test DB and return its ID."""
    db = _TestSession()
    a = Artist(
        id=str(uuid.uuid4()),
        name="Terms Test Artist",
        created_at=datetime.now(timezone.utc),
    )
    db.add(a)
    db.commit()
    aid = a.id
    db.close()
    return aid


def _accept_terms(artist_id: str) -> dict:
    """Helper: accept the current T&C for an artist via the API."""
    resp = client.post(
        f"/artists/{artist_id}/terms/accept",
        json={"terms_version": TERMS_VERSION, "agreed": True},
    )
    return resp


def _csv_bytes() -> bytes:
    """Minimal DistroKid-style CSV for upload tests."""
    lines = [
        "Month,Store,Country,Title,ISRC,Quantity,Earnings",
        "2024-01,Spotify,US,Song A,USABC0000001,1000,4.20",
    ]
    return "\n".join(lines).encode("utf-8")


# ---------------------------------------------------------------------------
# GET /terms
# ---------------------------------------------------------------------------


class TestGetTerms:
    def test_returns_200(self):
        resp = client.get("/terms")
        assert resp.status_code == 200

    def test_response_has_required_keys(self):
        data = client.get("/terms").json()
        assert "version" in data
        assert "sha256" in data
        assert "text" in data

    def test_version_matches_constant(self):
        data = client.get("/terms").json()
        assert data["version"] == TERMS_VERSION

    def test_sha256_matches_text(self):
        data = client.get("/terms").json()
        import hashlib

        expected = hashlib.sha256(data["text"].encode("utf-8")).hexdigest()
        assert data["sha256"] == expected

    def test_text_contains_contingency_fee_language(self):
        data = client.get("/terms").json()
        assert "12%" in data["text"] or "twelve percent" in data["text"].lower()

    def test_text_contains_trolley_reference(self):
        data = client.get("/terms").json()
        assert "Trolley" in data["text"]

    def test_text_contains_disbursement_language(self):
        data = client.get("/terms").json()
        text_lower = data["text"].lower()
        assert "disburse" in text_lower or "deposit" in text_lower

    def test_text_contains_net_recovery_language(self):
        data = client.get("/terms").json()
        text_lower = data["text"].lower()
        assert "net recovery" in text_lower or "90%" in data["text"]

    def test_text_contains_power_of_attorney(self):
        data = client.get("/terms").json()
        assert "power of attorney" in data["text"].lower()


# ---------------------------------------------------------------------------
# POST /artists/{id}/terms/accept — happy path
# ---------------------------------------------------------------------------


class TestAcceptTerms:
    def test_accept_returns_201(self, artist):
        resp = _accept_terms(artist)
        assert resp.status_code == 201

    def test_accept_response_has_required_fields(self, artist):
        data = _accept_terms(artist).json()
        assert "id" in data
        assert "artist_id" in data
        assert "terms_version" in data
        assert "text_sha256" in data
        assert "accepted_at" in data

    def test_accept_response_artist_id_matches(self, artist):
        data = _accept_terms(artist).json()
        assert data["artist_id"] == artist

    def test_accept_response_version_matches(self, artist):
        data = _accept_terms(artist).json()
        assert data["terms_version"] == TERMS_VERSION

    def test_accept_response_sha256_correct(self, artist):
        data = _accept_terms(artist).json()
        assert data["text_sha256"] == terms_text_sha256()

    def test_accept_persisted_to_db(self, artist):
        _accept_terms(artist)
        db = _TestSession()
        record = db.query(TermsAcceptance).filter(TermsAcceptance.artist_id == artist).first()
        db.close()
        assert record is not None
        assert record.terms_version == TERMS_VERSION


# ---------------------------------------------------------------------------
# POST /artists/{id}/terms/accept — idempotency
# ---------------------------------------------------------------------------


class TestAcceptTermsIdempotent:
    def test_second_accept_returns_201(self, artist):
        r1 = _accept_terms(artist)
        r2 = _accept_terms(artist)
        # Both succeed (idempotent)
        assert r1.status_code == 201
        assert r2.status_code == 201

    def test_second_accept_returns_same_record_id(self, artist):
        d1 = _accept_terms(artist).json()
        d2 = _accept_terms(artist).json()
        assert d1["id"] == d2["id"]

    def test_no_duplicate_rows_created(self, artist):
        _accept_terms(artist)
        _accept_terms(artist)
        _accept_terms(artist)
        db = _TestSession()
        count = (
            db.query(TermsAcceptance)
            .filter(
                TermsAcceptance.artist_id == artist,
                TermsAcceptance.terms_version == TERMS_VERSION,
            )
            .count()
        )
        db.close()
        assert count == 1


# ---------------------------------------------------------------------------
# POST /artists/{id}/terms/accept — validation failures
# ---------------------------------------------------------------------------


class TestAcceptTermsValidation:
    def test_wrong_version_returns_409(self, artist):
        resp = client.post(
            f"/artists/{artist}/terms/accept",
            json={"terms_version": "1999-01-01.1", "agreed": True},
        )
        assert resp.status_code == 409

    def test_wrong_version_error_mentions_current_version(self, artist):
        resp = client.post(
            f"/artists/{artist}/terms/accept",
            json={"terms_version": "1999-01-01.1", "agreed": True},
        )
        assert TERMS_VERSION in resp.json()["detail"]

    def test_agreed_false_returns_422(self, artist):
        resp = client.post(
            f"/artists/{artist}/terms/accept",
            json={"terms_version": TERMS_VERSION, "agreed": False},
        )
        assert resp.status_code == 422

    def test_unknown_artist_returns_404(self):
        resp = client.post(
            "/artists/nonexistent-uuid/terms/accept",
            json={"terms_version": TERMS_VERSION, "agreed": True},
        )
        assert resp.status_code == 404

    def test_missing_agreed_field_returns_422(self, artist):
        resp = client.post(
            f"/artists/{artist}/terms/accept",
            json={"terms_version": TERMS_VERSION},
        )
        assert resp.status_code == 422

    def test_missing_version_field_returns_422(self, artist):
        resp = client.post(
            f"/artists/{artist}/terms/accept",
            json={"agreed": True},
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# GET /artists/{id}/terms/status
# ---------------------------------------------------------------------------


class TestTermsStatus:
    def test_status_before_acceptance(self, artist):
        resp = client.get(f"/artists/{artist}/terms/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] is False
        assert data["accepted_at"] is None
        assert data["pending_version"] == TERMS_VERSION

    def test_status_after_acceptance(self, artist):
        _accept_terms(artist)
        resp = client.get(f"/artists/{artist}/terms/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] is True
        assert data["accepted_at"] is not None
        assert data["terms_version"] == TERMS_VERSION
        assert data["pending_version"] is None

    def test_status_unknown_artist_returns_404(self):
        resp = client.get("/artists/nonexistent-uuid/terms/status")
        assert resp.status_code == 404

    def test_status_has_required_fields(self, artist):
        data = client.get(f"/artists/{artist}/terms/status").json()
        for field in (
            "artist_id",
            "accepted",
            "terms_version",
            "accepted_at",
            "text_sha256",
            "pending_version",
        ):
            assert field in data

    def test_status_artist_id_matches(self, artist):
        data = client.get(f"/artists/{artist}/terms/status").json()
        assert data["artist_id"] == artist

    def test_status_sha256_correct_after_acceptance(self, artist):
        _accept_terms(artist)
        data = client.get(f"/artists/{artist}/terms/status").json()
        assert data["text_sha256"] == terms_text_sha256()


# ---------------------------------------------------------------------------
# Statement upload gate (T&C required)
# ---------------------------------------------------------------------------


class TestStatementUploadGate:
    def _upload(self, artist_id: str) -> int:
        csv_b = _csv_bytes()
        resp = client.post(
            f"/artists/{artist_id}/statements/upload",
            files={"file": ("statement.csv", io.BytesIO(csv_b), "text/csv")},
        )
        return resp.status_code

    def test_upload_without_terms_returns_403(self):
        # Create artist without accepting T&C
        db = _TestSession()
        a = Artist(
            id=str(uuid.uuid4()),
            name="No Terms Artist",
            created_at=datetime.now(timezone.utc),
        )
        db.add(a)
        db.commit()
        aid = a.id
        db.close()
        assert self._upload(aid) == 403

    def test_upload_gate_403_detail_instructs_user(self):
        db = _TestSession()
        a = Artist(
            id=str(uuid.uuid4()),
            name="No Terms Detail Artist",
            created_at=datetime.now(timezone.utc),
        )
        db.add(a)
        db.commit()
        aid = a.id
        db.close()
        csv_b = _csv_bytes()
        resp = client.post(
            f"/artists/{aid}/statements/upload",
            files={"file": ("statement.csv", io.BytesIO(csv_b), "text/csv")},
        )
        detail = resp.json()["detail"]
        assert "GET /terms" in detail or "terms" in detail.lower()

    def test_upload_after_terms_accepted_returns_201(self):
        # Create artist
        db = _TestSession()
        a = Artist(
            id=str(uuid.uuid4()),
            name="Gated Upload Artist",
            created_at=datetime.now(timezone.utc),
        )
        db.add(a)
        db.commit()
        aid = a.id
        db.close()
        # Accept T&C
        r = _accept_terms(aid)
        assert r.status_code == 201
        # Upload should now succeed
        assert self._upload(aid) == 201


# ---------------------------------------------------------------------------
# Legal content assertions
# ---------------------------------------------------------------------------


class TestTermsLegalContent:
    """Verify that the T&C text contains legally required provisions."""

    def _text(self) -> str:
        return TERMS_TEXT

    def test_contains_governing_law(self):
        assert "California" in self._text()

    def test_contains_arbitration_clause(self):
        text_lower = self._text().lower()
        assert "arbitration" in text_lower

    def test_contains_esign_reference(self):
        text_lower = self._text().lower()
        assert "electronic" in text_lower and "signature" in text_lower

    def test_contains_limitation_of_liability(self):
        text_lower = self._text().lower()
        assert "limitation of liability" in text_lower

    def test_contains_contingency_fee_percentage(self):
        assert "12%" in self._text()

    def test_contains_net_recovery_percentage(self):
        assert "90%" in self._text()

    def test_contains_disbursement_timeline(self):
        text_lower = self._text().lower()
        assert "five" in text_lower or "5" in self._text()

    def test_version_embedded_in_text(self):
        assert TERMS_VERSION in self._text()

    def test_sha256_stable(self):
        """SHA-256 of the live text must match what terms_text_sha256() returns."""
        import hashlib

        computed = hashlib.sha256(TERMS_TEXT.encode("utf-8")).hexdigest()
        assert computed == terms_text_sha256()
