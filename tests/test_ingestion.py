"""
Tests for the statement parser and ingestion endpoints.

Covers:
- format detection for all supported CSV formats
- parsing DistroKid, TuneCore, CD Baby, ASCAP, BMI, Spotify, generic CSVs
- edge cases: empty file, no amounts, zero-quantity rows, unknown format
- upload endpoint: happy path, duplicate detection, wrong file type
- connector credential validation (PROConnector, DSPConnector, etc.)
- POST /artists/{id}/connect credential status response
- GET /health/readiness connector inventory
"""

from __future__ import annotations

import io
import os
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from arcos7.ingestion.statement_parser import detect_format, parse_csv
from arcos7.ingestion.connectors.pro import PROConnector
from arcos7.ingestion.connectors.dsp import DSPConnector
from arcos7.ingestion.connectors.platform import PlatformConnector
from arcos7.ingestion.connectors.ticketing import TicketingConnector
from arcos7.models.base import Base, get_db
from arcos7.models.artist import Artist
from arcos7.models.event import Event
from arcos7.models.payment import Payment
from arcos7.models.statement import Statement
from arcos7.api.app import app

# Use the shared test DB defined in conftest.py
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def artist_id():
    """Create an artist in the test DB and return its ID."""
    db = _TestSession()
    artist = Artist(
        id=str(uuid.uuid4()),
        name="Test Artist",
        created_at=datetime.now(timezone.utc),
    )
    db.add(artist)
    db.commit()
    aid = artist.id
    db.close()
    return aid


# ---------------------------------------------------------------------------
# CSV helper
# ---------------------------------------------------------------------------

def _csv(headers: list[str], rows: list[list[str]]) -> bytes:
    lines = [",".join(headers)]
    for row in rows:
        lines.append(",".join(str(c) for c in row))
    return "\n".join(lines).encode("utf-8")


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------

class TestDetectFormat:
    def test_detects_distrokid(self):
        assert detect_format(["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"]) == "distrokid"

    def test_detects_tunecore(self):
        assert detect_format(["Sale Month", "Store", "Country", "Title", "ISRC", "Quantity", "Net Revenue"]) == "tunecore"

    def test_detects_cdbaby(self):
        assert detect_format(["Store", "Country", "Sale Date", "Title", "ISRC", "Quantity", "Total Earnings"]) == "cdbaby"

    def test_detects_ascap(self):
        assert detect_format(["Work Title", "ISWC", "Performance Date", "Source", "Royalty"]) == "ascap"

    def test_detects_bmi(self):
        assert detect_format(["Title", "ISWC", "Date", "Payer", "Revenue"]) == "bmi"

    def test_detects_spotify(self):
        assert detect_format(["Date", "Country", "Track Name", "ISRC", "Streams", "Stream Revenue"]) == "spotify"

    def test_falls_back_to_generic(self):
        assert detect_format(["date", "source", "amount", "quantity"]) == "generic"

    def test_case_insensitive(self):
        # Headers are normalised to lowercase before matching
        assert detect_format(["MONTH", "STORE", "COUNTRY", "TITLE", "ISRC", "QUANTITY", "EARNINGS"]) == "distrokid"


# ---------------------------------------------------------------------------
# DistroKid parser
# ---------------------------------------------------------------------------

class TestDistroKidParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"],
            [
                ["2023-06", "Spotify", "US", "My Song", "USABC1234567", "15000", "62.50"],
                ["2023-06", "Apple Music", "GB", "My Song", "USABC1234567", "3000", "18.75"],
            ],
        )

    def test_detects_correct_format(self):
        result = parse_csv(self._csv(), "artist-1")
        assert result.format_detected == "distrokid"

    def test_parses_two_rows(self):
        result = parse_csv(self._csv(), "artist-1")
        assert result.row_count == 2
        assert len(result.events) == 2
        assert len(result.payments) == 2

    def test_event_fields(self):
        result = parse_csv(self._csv(), "artist-1")
        e = result.events[0]
        assert e["event_type"] == "STREAM"
        assert e["platform"] == "Spotify"
        assert e["territory"] == "US"
        assert e["quantity"] == 15000
        assert abs(e["unit_value"] - 62.50 / 15000) < 1e-6

    def test_payment_fields(self):
        result = parse_csv(self._csv(), "artist-1")
        p = result.payments[0]
        assert abs(p["amount"] - 62.50) < 0.01
        assert p["currency"] == "USD"
        assert "DistroKid" in p["source"]

    def test_no_errors(self):
        result = parse_csv(self._csv(), "artist-1")
        assert result.errors == []


# ---------------------------------------------------------------------------
# TuneCore parser
# ---------------------------------------------------------------------------

class TestTuneCoreParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Sale Month", "Store", "Country", "Title", "ISRC", "Quantity", "Net Revenue"],
            [["2023-07", "Spotify", "CA", "Another Song", "CADEF9876543", "5000", "21.00"]],
        )

    def test_detects_correct_format(self):
        assert parse_csv(self._csv(), "x").format_detected == "tunecore"

    def test_parses_row(self):
        result = parse_csv(self._csv(), "x")
        assert len(result.events) == 1
        assert result.events[0]["platform"] == "Spotify"
        assert result.events[0]["territory"] == "CA"
        assert abs(result.payments[0]["amount"] - 21.00) < 0.01


# ---------------------------------------------------------------------------
# CD Baby parser
# ---------------------------------------------------------------------------

class TestCDBabyParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Store", "Country", "Sale Date", "Title", "ISRC", "Quantity", "Total Earnings"],
            [["Spotify", "AU", "2022-03-15", "Old Song", "AUGHI5554321", "800", "3.52"]],
        )

    def test_detects_correct_format(self):
        assert parse_csv(self._csv(), "x").format_detected == "cdbaby"

    def test_parses_amount(self):
        result = parse_csv(self._csv(), "x")
        assert abs(result.payments[0]["amount"] - 3.52) < 0.01


# ---------------------------------------------------------------------------
# ASCAP parser
# ---------------------------------------------------------------------------

class TestASCAPParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Work Title", "ISWC", "Performance Date", "Source", "Royalty"],
            [["My Ballad", "T-123456789", "2023-01-15", "Digital", "12.40"]],
        )

    def test_detects_ascap(self):
        assert parse_csv(self._csv(), "x").format_detected == "ascap"

    def test_territory_defaults_to_us(self):
        result = parse_csv(self._csv(), "x")
        assert result.events[0]["territory"] == "US"

    def test_source_contains_ascap(self):
        result = parse_csv(self._csv(), "x")
        assert "ASCAP" in result.payments[0]["source"]


# ---------------------------------------------------------------------------
# BMI parser
# ---------------------------------------------------------------------------

class TestBMIParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Title", "ISWC", "Date", "Payer", "Revenue"],
            [["Rock Track", "T-987654321", "2022-06-01", "Spotify", "8.75"]],
        )

    def test_detects_bmi(self):
        assert parse_csv(self._csv(), "x").format_detected == "bmi"

    def test_parses_payer_as_source(self):
        result = parse_csv(self._csv(), "x")
        assert "Spotify" in result.payments[0]["source"]


# ---------------------------------------------------------------------------
# Spotify format parser
# ---------------------------------------------------------------------------

class TestSpotifyParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Date", "Country", "Track Name", "ISRC", "Streams", "Stream Revenue"],
            [["2023-05", "US", "Hit Song", "USXYZ0001234", "20000", "84.00"]],
        )

    def test_detects_spotify(self):
        assert parse_csv(self._csv(), "x").format_detected == "spotify"

    def test_platform_is_spotify(self):
        result = parse_csv(self._csv(), "x")
        assert result.events[0]["platform"] == "Spotify"

    def test_quantity_parsed(self):
        result = parse_csv(self._csv(), "x")
        assert result.events[0]["quantity"] == 20000


# ---------------------------------------------------------------------------
# Generic fallback parser
# ---------------------------------------------------------------------------

class TestGenericParser:
    def _csv(self) -> bytes:
        return _csv(
            ["date", "source", "quantity", "amount", "currency", "country"],
            [["2023-08-01", "Some Platform", "1000", "4.20", "EUR", "DE"]],
        )

    def test_detects_generic(self):
        assert parse_csv(self._csv(), "x").format_detected == "generic"

    def test_parses_territory(self):
        result = parse_csv(self._csv(), "x")
        assert result.events[0]["territory"] == "DE"

    def test_parses_currency(self):
        result = parse_csv(self._csv(), "x")
        assert result.payments[0]["currency"] == "EUR"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestParserEdgeCases:
    def test_empty_file_returns_error(self):
        result = parse_csv(b"", "x")
        assert len(result.errors) > 0

    def test_header_only_file(self):
        result = parse_csv(b"Month,Store,Earnings\n", "x")
        # 0 data rows, no events
        assert len(result.events) == 0

    def test_zero_amount_rows_skipped(self):
        csv_bytes = _csv(
            ["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"],
            [
                ["2023-01", "Spotify", "US", "Song", "ISRC1", "0", "0.00"],
                ["2023-01", "Apple", "US", "Song", "ISRC1", "100", "0.41"],
            ],
        )
        result = parse_csv(csv_bytes, "x")
        # Only the non-zero row should be included
        assert len(result.events) == 1
        assert result.skipped_rows == 1

    def test_bom_stripped_from_headers(self):
        # Excel adds a UTF-8 BOM to CSV exports
        csv_bytes = b"\xef\xbb\xbfMonth,Store,Country,Title,ISRC,Quantity,Earnings\n2023-01,Spotify,US,Song,ISRC,500,2.00\n"
        result = parse_csv(csv_bytes, "x")
        assert result.format_detected == "distrokid"
        assert len(result.events) == 1

    def test_dollar_sign_in_amount_handled(self):
        csv_bytes = _csv(
            ["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"],
            [["2023-01", "Spotify", "US", "Song", "ISRC", "500", "$2.00"]],
        )
        result = parse_csv(csv_bytes, "x")
        assert abs(result.payments[0]["amount"] - 2.00) < 0.01

    def test_comma_in_number_handled(self):
        # Use a properly quoted CSV so the comma inside "1,000" is preserved
        csv_bytes = b'Month,Store,Country,Title,ISRC,Quantity,Earnings\n2023-01,Spotify,US,Song,ISRC,"1,000",4.20\n'
        result = parse_csv(csv_bytes, "x")
        assert result.events[0]["quantity"] == 1000


# ---------------------------------------------------------------------------
# Upload endpoint
# ---------------------------------------------------------------------------

class TestUploadEndpoint:
    def _upload(self, artist_id: str, csv_bytes: bytes, filename: str = "statement.csv"):
        return client.post(
            f"/artists/{artist_id}/statements/upload",
            files={"file": (filename, io.BytesIO(csv_bytes), "text/csv")},
        )

    def test_successful_upload_returns_201(self, artist_id):
        csv_bytes = _csv(
            ["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"],
            [["2023-06", "Spotify", "US", "Song A", "USABC1111111", "5000", "21.00"]],
        )
        resp = self._upload(artist_id, csv_bytes)
        assert resp.status_code == 201

    def test_response_contains_statement_id(self, artist_id):
        csv_bytes = _csv(
            ["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"],
            [["2023-06", "Spotify", "US", "Song B", "USABC2222222", "3000", "12.60"]],
        )
        data = self._upload(artist_id, csv_bytes).json()
        assert "id" in data
        assert data["artist_id"] == artist_id

    def test_events_and_payments_persisted(self, artist_id):
        csv_bytes = _csv(
            ["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"],
            [
                ["2023-06", "Spotify", "US", "Song C", "USABC3333333", "4000", "16.80"],
                ["2023-06", "Apple Music", "GB", "Song C", "USABC3333333", "1000", "6.20"],
            ],
        )
        data = self._upload(artist_id, csv_bytes).json()
        assert data["events_created"] == 2
        assert data["payments_created"] == 2

    def test_duplicate_upload_returns_409(self, artist_id):
        csv_bytes = _csv(
            ["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"],
            [["2023-07", "Spotify", "US", "Dup Song", "USDUP1111111", "1000", "4.20"]],
        )
        r1 = self._upload(artist_id, csv_bytes)
        r2 = self._upload(artist_id, csv_bytes)
        assert r1.status_code == 201
        assert r2.status_code == 409
        assert "already been uploaded" in r2.json()["detail"]

    def test_non_csv_file_returns_400(self, artist_id):
        resp = client.post(
            f"/artists/{artist_id}/statements/upload",
            files={"file": ("report.pdf", io.BytesIO(b"%PDF"), "application/pdf")},
        )
        assert resp.status_code == 400

    def test_empty_file_returns_400(self, artist_id):
        resp = client.post(
            f"/artists/{artist_id}/statements/upload",
            files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")},
        )
        assert resp.status_code == 400

    def test_unknown_artist_returns_404(self):
        csv_bytes = _csv(
            ["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"],
            [["2023-06", "Spotify", "US", "Song", "ISRC1", "1000", "4.20"]],
        )
        resp = self._upload("nonexistent-id", csv_bytes)
        assert resp.status_code == 404

    def test_format_detected_recorded(self, artist_id):
        csv_bytes = _csv(
            ["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"],
            [["2023-08", "Tidal", "US", "DK Song", "USDK1111111", "2000", "8.40"]],
        )
        data = self._upload(artist_id, csv_bytes).json()
        assert data["format_detected"] == "distrokid"


# ---------------------------------------------------------------------------
# List statements endpoint
# ---------------------------------------------------------------------------

class TestListStatements:
    def test_list_returns_uploaded_statements(self, artist_id):
        csv_bytes = _csv(
            ["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"],
            [["2023-09", "Spotify", "US", "Listed Song", "USLST111111", "500", "2.10"]],
        )
        client.post(
            f"/artists/{artist_id}/statements/upload",
            files={"file": ("list_test.csv", io.BytesIO(csv_bytes), "text/csv")},
        )
        resp = client.get(f"/artists/{artist_id}/statements")
        assert resp.status_code == 200
        statements = resp.json()
        assert isinstance(statements, list)
        assert len(statements) >= 1

    def test_list_unknown_artist_returns_404(self):
        resp = client.get("/artists/nonexistent-uuid/statements")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Connector credential validation
# ---------------------------------------------------------------------------

class TestConnectorCredentials:
    def test_pro_connect_returns_false_without_key(self, monkeypatch):
        monkeypatch.delenv("ASCAP_API_KEY", raising=False)
        c = PROConnector(config={}, pro_name="ASCAP")
        assert c.connect() is False

    def test_pro_connect_returns_true_with_env_key(self, monkeypatch):
        monkeypatch.setenv("ASCAP_API_KEY", "test-key-123")
        c = PROConnector(config={}, pro_name="ASCAP")
        assert c.connect() is True

    def test_pro_connect_returns_true_with_config_key(self):
        c = PROConnector(config={"api_key": "from-config"}, pro_name="BMI")
        assert c.connect() is True

    def test_pro_fetch_historical_raises_not_implemented(self, monkeypatch):
        monkeypatch.delenv("ASCAP_API_KEY", raising=False)
        c = PROConnector(config={}, pro_name="ASCAP")
        with pytest.raises(NotImplementedError) as exc:
            c.fetch_historical("artist-1", datetime.now(timezone.utc), datetime.now(timezone.utc))
        assert "ASCAP" in str(exc.value)
        assert "statements/upload" in str(exc.value)

    def test_dsp_connect_false_without_creds(self, monkeypatch):
        monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)
        monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)
        c = DSPConnector(config={}, dsp_name="Spotify")
        assert c.connect() is False

    def test_dsp_connect_true_with_creds(self, monkeypatch):
        monkeypatch.setenv("SPOTIFY_CLIENT_ID", "cid")
        monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "csecret")
        c = DSPConnector(config={}, dsp_name="Spotify")
        assert c.connect() is True

    def test_dsp_fetch_historical_raises_not_implemented(self, monkeypatch):
        monkeypatch.delenv("SPOTIFY_CLIENT_ID", raising=False)
        monkeypatch.delenv("SPOTIFY_CLIENT_SECRET", raising=False)
        c = DSPConnector(config={}, dsp_name="Spotify")
        with pytest.raises(NotImplementedError):
            c.fetch_historical("a", datetime.now(timezone.utc), datetime.now(timezone.utc))

    def test_platform_connect_false_without_key(self, monkeypatch):
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        c = PlatformConnector(config={}, platform_name="YouTube")
        assert c.connect() is False

    def test_ticketing_connect_false_without_key(self, monkeypatch):
        monkeypatch.delenv("TICKETMASTER_API_KEY", raising=False)
        c = TicketingConnector(config={}, platform_name="Ticketmaster")
        assert c.connect() is False

    def test_ticketing_connect_true_with_key(self, monkeypatch):
        monkeypatch.setenv("TICKETMASTER_API_KEY", "tm-key")
        c = TicketingConnector(config={}, platform_name="Ticketmaster")
        assert c.connect() is True


# ---------------------------------------------------------------------------
# POST /artists/{id}/connect
# ---------------------------------------------------------------------------

class TestConnectEndpoint:
    def test_returns_200(self, artist_id, monkeypatch):
        # Ensure all env vars are absent so we get the 'no_connectors_configured' status
        for var in ("ASCAP_API_KEY", "BMI_API_KEY", "SESAC_API_KEY",
                    "SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET"):
            monkeypatch.delenv(var, raising=False)
        resp = client.post(f"/artists/{artist_id}/connect")
        assert resp.status_code == 200

    def test_returns_sources_list(self, artist_id):
        resp = client.post(f"/artists/{artist_id}/connect")
        data = resp.json()
        assert "sources" in data
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) > 0

    def test_sources_have_required_fields(self, artist_id):
        resp = client.post(f"/artists/{artist_id}/connect")
        for source in resp.json()["sources"]:
            assert "source" in source
            assert "configured" in source
            assert "status" in source

    def test_returns_next_steps(self, artist_id):
        resp = client.post(f"/artists/{artist_id}/connect")
        assert "next_steps" in resp.json()

    def test_unknown_artist_returns_404(self):
        resp = client.post("/artists/nonexistent-id/connect")
        assert resp.status_code == 404

    def test_configured_count_increases_with_env_var(self, artist_id, monkeypatch):
        monkeypatch.setenv("ASCAP_API_KEY", "set-for-test")
        resp = client.post(f"/artists/{artist_id}/connect").json()
        assert resp["configured_sources"] >= 1


# ---------------------------------------------------------------------------
# GET /health/readiness
# ---------------------------------------------------------------------------

class TestReadinessEndpoint:
    def test_returns_200(self):
        resp = client.get("/health/readiness")
        assert resp.status_code == 200

    def test_ready_is_true(self):
        data = client.get("/health/readiness").json()
        assert data["ready"] is True

    def test_core_platform_is_ready(self):
        data = client.get("/health/readiness").json()
        assert data["core"]["database"] == "ready"
        assert data["core"]["api"] == "ready"
        assert data["core"]["widget"] == "ready"
        assert data["core"]["statement_upload"] == "ready"

    def test_connectors_section_present(self):
        data = client.get("/health/readiness").json()
        assert "connectors" in data
        assert "pros" in data["connectors"]
        assert "dsps" in data["connectors"]
        assert "ticketing" in data["connectors"]

    def test_missing_creds_shows_missing_credentials(self, monkeypatch):
        for var in ("ASCAP_API_KEY", "BMI_API_KEY"):
            monkeypatch.delenv(var, raising=False)
        data = client.get("/health/readiness").json()
        ascap = next(c for c in data["connectors"]["pros"] if c["name"] == "ASCAP")
        assert ascap["status"] == "missing_credentials"
        assert ascap["configured"] is False

    def test_note_field_present(self):
        data = client.get("/health/readiness").json()
        assert "note" in data
        assert "statements/upload" in data["note"]
