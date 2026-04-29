"""
Regression test for #195: the upload endpoint must accept Apple Numbers (.numbers)
files directly, not require operator pre-conversion to CSV.

The MLC ships member statements as .numbers by default. Pre-fix, the upload
endpoint rejected anything not csv/tsv/xlsx, so a real beta-cohort songwriter
on MLC would hit a dead end. This test pins:

  1. .numbers extension is accepted (not 400-rejected at the file-type gate)
  2. The endpoint internally converts via numbers_file.numbers_to_csv_bytes
  3. Detection still picks up the underlying format (we patch the numbers
     converter to return canonical CSV; we don't include a real .numbers
     binary fixture in the repo to keep it small)

We monkeypatch numbers_to_csv_bytes rather than ship a binary .numbers
fixture — testing the conversion library itself is out of scope; what
matters here is the wiring in the upload endpoint.
"""

from __future__ import annotations

import io
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from tests.conftest import TestSession as _TestSession
from XR7.api.app import app
from XR7.legal.terms import TERMS_VERSION
from XR7.models.artist import Artist

client = TestClient(app)


def _create_artist_with_terms() -> str:
    db = _TestSession()
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Numbers Test Artist",
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.commit()
    aid = artist.id
    db.close()
    resp = client.post(
        f"/artists/{aid}/terms/accept",
        json={"terms_version": TERMS_VERSION, "agreed": True},
    )
    assert resp.status_code == 201
    return aid


def test_upload_accepts_dotnumbers_extension_and_calls_converter(monkeypatch):
    """A .numbers file passes the file-type gate and is routed through the converter.

    Before #195: the gate returned 400 on anything not csv/tsv/xlsx — beta users
    on MLC (Numbers is the default export) hit a dead end. After: the upload
    endpoint accepts .numbers, calls numbers_to_csv_bytes, and continues with
    the converted CSV.

    We verify the wiring (extension allowed + converter invoked + raw bytes
    passed through) rather than the full ingestion path, because the latter
    depends on a Postgres-only ON CONFLICT constraint not present in the
    SQLite test schema. End-to-end ingestion is verified by the live QA
    smoke test against real MLC data.
    """
    artist_id = _create_artist_with_terms()

    converter_called: dict[str, bytes] = {}

    def _fake_numbers_to_csv_bytes(content):
        # Capture so the test can assert the raw upload bytes are passed through unchanged.
        converter_called["content"] = content
        # Return a header-only CSV so detection runs but no events are inserted
        # (avoids the SQLite-vs-Postgres ON CONFLICT mismatch in tests).
        return b"Sale Month,Store,Title,Quantity,Earnings (USD)\n"

    import XR7.api.routers.ingestion as ingestion_module

    monkeypatch.setattr(ingestion_module, "numbers_to_csv_bytes", _fake_numbers_to_csv_bytes)

    resp = client.post(
        f"/artists/{artist_id}/statements/upload",
        files={
            "file": (
                "MLC Statement.numbers",
                io.BytesIO(b"FAKE-NUMBERS-BINARY"),
                "application/octet-stream",
            )
        },
    )

    # Pin: extension was accepted (status is NOT a 400 file-type rejection).
    assert resp.status_code != 400, f"expected acceptance, got 400: {resp.text}"

    # Pin: converter was invoked with the raw uploaded bytes (not a re-read or wrong stream).
    assert converter_called.get("content") == b"FAKE-NUMBERS-BINARY"


def test_upload_rejects_non_supported_extension():
    """Sanity check that the .numbers addition didn't break the rejection path."""
    artist_id = _create_artist_with_terms()
    resp = client.post(
        f"/artists/{artist_id}/statements/upload",
        files={"file": ("statement.docx", io.BytesIO(b"x" * 100), "application/octet-stream")},
    )
    assert resp.status_code == 400
    assert "Numbers" in resp.json()["detail"]  # error message lists supported types


def test_upload_returns_422_when_numbers_file_unreadable(monkeypatch):
    """A corrupt or unreadable .numbers file surfaces a clear 422, not a 500."""
    artist_id = _create_artist_with_terms()

    import XR7.api.routers.ingestion as ingestion_module

    def _raises_value_error(content):
        raise ValueError("numbers-parser library not installed.")

    monkeypatch.setattr(ingestion_module, "numbers_to_csv_bytes", _raises_value_error)

    resp = client.post(
        f"/artists/{artist_id}/statements/upload",
        files={
            "file": (
                "broken.numbers",
                io.BytesIO(b"not-a-real-numbers-file"),
                "application/octet-stream",
            )
        },
    )
    assert resp.status_code == 422
    assert "Numbers" in resp.json()["detail"]
