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

import httpx
import pytest
from fastapi.testclient import TestClient

from XR7.ingestion.statement_parser import detect_format, parse_csv, SUPPORTED_FORMATS
from XR7.ingestion.connectors.pro import PROConnector
from XR7.ingestion.connectors.dsp import DSPConnector
from XR7.ingestion.connectors.platform import PlatformConnector
from XR7.ingestion.connectors.ticketing import TicketingConnector
from XR7.ingestion.connectors.mlc import MLCConnector
from XR7.ingestion.connectors.international_pro import (
    APRAAMCOSConnector,
    JASRACConnector,
    KOMCAConnector,
    SACEMConnector,
)
from XR7.models.base import Base, get_db
from XR7.models.artist import Artist
from XR7.models.event import Event
from XR7.models.payment import Payment
from XR7.models.statement import Statement
from XR7.api.app import app

# Use the shared test DB defined in conftest.py
from tests.conftest import TestSession as _TestSession

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def artist_id():
    """Create an artist in the test DB, accept the current T&C, and return the ID."""
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

    # Accept the current T&C so statement upload tests can proceed.
    from XR7.legal.terms import TERMS_VERSION
    resp = client.post(
        f"/artists/{aid}/terms/accept",
        json={"terms_version": TERMS_VERSION, "agreed": True},
    )
    assert resp.status_code == 201, f"T&C accept failed: {resp.json()}"

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

    def test_mlc_connect_false_without_key(self, monkeypatch):
        monkeypatch.delenv("MLC_API_KEY", raising=False)
        c = MLCConnector(config={})
        assert c.connect() is False

    def test_mlc_connect_true_with_env_key(self, monkeypatch):
        monkeypatch.setenv("MLC_API_KEY", "mlc-key")
        c = MLCConnector(config={})
        assert c.connect() is True

    def test_mlc_fetch_historical_returns_rows(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["artist_id"] == "artist-1"
            return httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "artist_id": "artist-1",
                            "work_id": "work-1",
                            "quantity": "1000",
                            "amount": "12.50",
                            "statement_date": "2025-01-15",
                            "territory": "US",
                        }
                    ]
                },
            )

        transport = httpx.MockTransport(handler)
        client = httpx.Client(transport=transport)
        connector = MLCConnector(
            config={"api_key": "k", "base_url": "https://example.test"},
            http_client=client,
        )
        rows = connector.fetch_historical(
            "artist-1",
            datetime(2025, 1, 1, tzinfo=timezone.utc),
            datetime(2025, 1, 31, tzinfo=timezone.utc),
        )
        assert len(rows) == 1
        assert rows[0]["source"] == "MLC"

    def test_mlc_normalize_calculates_unit_value(self):
        connector = MLCConnector(config={"api_key": "k"})
        normalized = connector.normalize([
            {
                "artist_id": "artist-1",
                "work_id": "work-1",
                "quantity": "1000",
                "amount": "12.50",
                "currency": "USD",
                "statement_date": "2025-01-15",
                "country": "US",
            }
        ])
        assert len(normalized) == 1
        row = normalized[0]
        assert row["event_type"] == "MECHANICAL"
        assert row["quantity"] == 1000
        assert abs(row["unit_value"] - 0.0125) < 1e-9
        assert row["platform"] == "MLC"

    def test_apra_amcos_connect_true_with_env_key(self, monkeypatch):
        monkeypatch.setenv("APRA_AMCOS_API_KEY", "apra-key")
        c = APRAAMCOSConnector(config={})
        assert c.connect() is True

    def test_jasrac_connect_false_without_key(self, monkeypatch):
        monkeypatch.delenv("JASRAC_API_KEY", raising=False)
        c = JASRACConnector(config={})
        assert c.connect() is False

    def test_komca_fetch_recent_returns_rows(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["artist_id"] == "artist-9"
            return httpx.Response(
                200,
                json={
                    "records": [
                        {
                            "artist_id": "artist-9",
                            "work_id": "work-k",
                            "performances": "200",
                            "royalty_amount": "3.50",
                            "statement_date": "2025-02-01",
                            "country": "KR",
                        }
                    ]
                },
            )

        transport = httpx.MockTransport(handler)
        client = httpx.Client(transport=transport)
        connector = KOMCAConnector(
            config={"api_key": "k", "base_url": "https://example.test"},
            http_client=client,
        )
        rows = connector.fetch_recent("artist-9", datetime(2025, 2, 1, tzinfo=timezone.utc))
        assert len(rows) == 1
        assert rows[0]["source"] == "KOMCA"

    def test_sacem_normalize_defaults_to_performance(self):
        connector = SACEMConnector(config={"api_key": "k"})
        normalized = connector.normalize([
            {
                "artist_id": "artist-2",
                "iswc": "T-111.222.333-4",
                "quantity": "50",
                "amount": "9.00",
                "country": "FR",
                "statement_date": "2025-01-10",
            }
        ])
        assert normalized[0]["event_type"] == "PERFORMANCE"
        assert normalized[0]["platform"] == "SACEM"
        assert normalized[0]["quantity"] == 50


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

    def test_connect_sources_include_international_pros(self, artist_id):
        sources = client.post(f"/artists/{artist_id}/connect").json()["sources"]
        names = [s["source"] for s in sources]
        assert "APRA AMCOS" in names
        assert "JASRAC" in names
        assert "KOMCA" in names
        assert "SACEM" in names


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
        assert "international_pros" in data["connectors"]
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

    def test_international_pros_present_in_readiness(self):
        data = client.get("/health/readiness").json()
        names = [p["name"] for p in data["connectors"]["international_pros"]]
        assert "APRA AMCOS" in names
        assert "JASRAC" in names
        assert "KOMCA" in names
        assert "SACEM" in names

    def test_distributors_section_present(self):
        data = client.get("/health/readiness").json()
        assert "distributors" in data["connectors"]
        assert isinstance(data["connectors"]["distributors"], list)
        assert len(data["connectors"]["distributors"]) > 0

    def test_distributors_include_known_names(self):
        data = client.get("/health/readiness").json()
        names = [d["name"] for d in data["connectors"]["distributors"]]
        assert "Amuse" in names
        assert "United Masters" in names
        assert "ONErpm" in names
        assert "DistroKid" in names
        assert "TuneCore" in names
        assert "CD Baby" in names

    def test_mechanical_connector_section_present(self):
        data = client.get("/health/readiness").json()
        assert "mechanical" in data["connectors"]
        assert isinstance(data["connectors"]["mechanical"], list)
        assert len(data["connectors"]["mechanical"]) == 1

    def test_mechanical_connector_defaults_to_missing_credentials(self, monkeypatch):
        monkeypatch.delenv("MLC_API_KEY", raising=False)
        data = client.get("/health/readiness").json()
        mlc = data["connectors"]["mechanical"][0]
        assert mlc["name"] == "MLC"
        assert mlc["configured"] is False
        assert mlc["status"] == "missing_credentials"


# ---------------------------------------------------------------------------
# GET /ingestion/supported-formats
# ---------------------------------------------------------------------------

class TestSupportedFormatsEndpoint:
    def test_returns_200(self):
        resp = client.get("/ingestion/supported-formats")
        assert resp.status_code == 200

    def test_response_has_required_keys(self):
        data = client.get("/ingestion/supported-formats").json()
        assert "total_explicit_formats" in data
        assert "formats" in data
        assert "by_type" in data
        assert "upload_endpoint" in data

    def test_total_explicit_formats_is_positive(self):
        data = client.get("/ingestion/supported-formats").json()
        # Explicit formats = all SUPPORTED_FORMATS entries except "generic"
        expected = len([k for k in SUPPORTED_FORMATS if k != "generic"])
        assert data["total_explicit_formats"] == expected

    def test_formats_includes_all_distributors(self):
        formats = client.get("/ingestion/supported-formats").json()["formats"]
        for fmt in ("distrokid", "tunecore", "cdbaby", "amuse", "unitedmasters",
                    "onerpm", "stem", "landr", "ditto", "reverbnation", "bandcamp"):
            assert fmt in formats, f"Missing format: {fmt}"

    def test_formats_includes_pros(self):
        formats = client.get("/ingestion/supported-formats").json()["formats"]
        assert "ascap" in formats
        assert "bmi" in formats

    def test_formats_includes_generic(self):
        formats = client.get("/ingestion/supported-formats").json()["formats"]
        assert "generic" in formats

    def test_each_format_has_required_fields(self):
        formats = client.get("/ingestion/supported-formats").json()["formats"]
        for fmt_key, fmt_data in formats.items():
            assert "name" in fmt_data, f"{fmt_key} missing 'name'"
            assert "type" in fmt_data, f"{fmt_key} missing 'type'"
            assert "key_columns" in fmt_data, f"{fmt_key} missing 'key_columns'"
            assert "description" in fmt_data, f"{fmt_key} missing 'description'"

    def test_by_type_groups_correctly(self):
        data = client.get("/ingestion/supported-formats").json()
        # Derive expected counts directly from the SUPPORTED_FORMATS constant
        expected_distributors = sum(1 for v in SUPPORTED_FORMATS.values() if v["type"] == "distributor")
        expected_pros = sum(1 for v in SUPPORTED_FORMATS.values() if v["type"] == "pro")
        expected_dsps = sum(1 for v in SUPPORTED_FORMATS.values() if v["type"] == "dsp")
        expected_generic = sum(1 for v in SUPPORTED_FORMATS.values() if v["type"] == "generic")
        assert len(data["by_type"]["distributors"]) == expected_distributors
        assert len(data["by_type"]["pros"]) == expected_pros
        assert len(data["by_type"]["dsps"]) == expected_dsps
        assert len(data["by_type"]["generic"]) == expected_generic

    def test_upload_endpoint_field(self):
        data = client.get("/ingestion/supported-formats").json()
        assert "statements/upload" in data["upload_endpoint"]

    def test_generic_description_mentions_other_distributors(self):
        data = client.get("/ingestion/supported-formats").json()
        generic_desc = data["formats"]["generic"]["description"]
        # Should mention the generic fallback coverage
        assert "generic" in generic_desc.lower() or "fallback" in generic_desc.lower() or "other" in generic_desc.lower()


# ---------------------------------------------------------------------------
# New distributor format detection
# ---------------------------------------------------------------------------

class TestDetectFormatNewDistributors:
    def test_detects_amuse(self):
        assert detect_format(
            ["Reporting Period", "Platform", "Country", "Track Title", "ISRC", "Streams", "Revenue"]
        ) == "amuse"

    def test_detects_amuse_case_insensitive(self):
        assert detect_format(
            ["REPORTING PERIOD", "PLATFORM", "COUNTRY", "TRACK TITLE", "ISRC", "STREAMS", "REVENUE"]
        ) == "amuse"

    def test_detects_unitedmasters(self):
        assert detect_format(
            ["Period", "Store", "Country/Region", "Album", "Track", "ISRC", "Units", "Total Revenue"]
        ) == "unitedmasters"

    def test_detects_onerpm(self):
        assert detect_format(
            ["Sale Date", "Retailer", "Country", "Track Title", "ISRC", "UPC", "Qty", "Net Amount"]
        ) == "onerpm"

    def test_detects_stem(self):
        assert detect_format(
            ["Period", "Platform", "Country Code", "Track Name", "ISRC", "Streams", "Net Revenue"]
        ) == "stem"

    def test_detects_landr(self):
        assert detect_format(
            ["Month", "Store", "Territory", "Track Name", "ISRC", "Net Quantity", "Net Revenue"]
        ) == "landr"

    def test_detects_ditto(self):
        assert detect_format(
            ["Month", "Store", "Country", "Title", "ISRC", "Streams", "Net Revenue"]
        ) == "ditto"

    def test_detects_reverbnation(self):
        assert detect_format(
            ["Date", "Platform", "Country", "Song", "ISRC", "Streams", "Revenue"]
        ) == "reverbnation"

    def test_detects_bandcamp(self):
        assert detect_format(
            ["Date", "Item Name", "Buyer Name", "Country", "Item Type", "Quantity", "Revenue"]
        ) == "bandcamp"

    # Ensure new formats don't accidentally match existing ones
    def test_ditto_not_confused_with_distrokid(self):
        # DistroKid uses "Earnings", Ditto uses "Net Revenue" + "Streams"
        assert detect_format(
            ["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"]
        ) == "distrokid"

    def test_ditto_not_confused_with_tunecore(self):
        # TuneCore uses "Sale Month" not "Month"
        assert detect_format(
            ["Sale Month", "Store", "Country", "Title", "ISRC", "Quantity", "Net Revenue"]
        ) == "tunecore"

    def test_stem_not_confused_with_ditto(self):
        # Stem uses "Country Code" not "Country"
        assert detect_format(
            ["Period", "Platform", "Country Code", "Track Name", "ISRC", "Streams", "Net Revenue"]
        ) == "stem"

    def test_landr_not_confused_with_ditto(self):
        # LANDR has "Net Quantity" and "Territory" which Ditto doesn't
        assert detect_format(
            ["Month", "Store", "Territory", "Track Name", "ISRC", "Net Quantity", "Net Revenue"]
        ) == "landr"


# ---------------------------------------------------------------------------
# New distributor CSV parsers
# ---------------------------------------------------------------------------

class TestAmuseParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Reporting Period", "Platform", "Country", "Artist", "Track Title", "ISRC", "Streams", "Revenue"],
            [["2024-01", "Spotify", "US", "Test Artist", "My Song", "USABC1234567", "5000", "20.50"]],
        )

    def test_detects_correct_format(self):
        assert parse_csv(self._csv(), "a1").format_detected == "amuse"

    def test_parses_amount(self):
        result = parse_csv(self._csv(), "a1")
        assert len(result.payments) == 1
        assert result.payments[0]["amount"] == pytest.approx(20.50, abs=0.001)

    def test_source_contains_amuse(self):
        result = parse_csv(self._csv(), "a1")
        assert "Amuse" in result.payments[0]["source"]

    def test_parses_streams(self):
        result = parse_csv(self._csv(), "a1")
        assert result.events[0]["quantity"] == 5000

    def test_parses_isrc(self):
        result = parse_csv(self._csv(), "a1")
        assert result.events[0]["isrc"] == "USABC1234567"


class TestUnitedMastersParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Period", "Store", "Country/Region", "Album", "Track", "ISRC", "UPC", "Units", "Total Revenue"],
            [["2024-02", "Apple Music", "US", "My Album", "My Track", "USDEF1234567", "123456789", "1200", "4.80"]],
        )

    def test_detects_correct_format(self):
        assert parse_csv(self._csv(), "u1").format_detected == "unitedmasters"

    def test_parses_amount(self):
        result = parse_csv(self._csv(), "u1")
        assert result.payments[0]["amount"] == pytest.approx(4.80, abs=0.001)

    def test_source_contains_united_masters(self):
        result = parse_csv(self._csv(), "u1")
        assert "United Masters" in result.payments[0]["source"]

    def test_parses_units(self):
        result = parse_csv(self._csv(), "u1")
        assert result.events[0]["quantity"] == 1200


class TestONErpmParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Sale Date", "Retailer", "Country", "Track Title", "ISRC", "UPC", "Qty", "Net Amount"],
            [["2024-03-15", "Amazon Music", "US", "My Track", "USGHI1234567", "987654321", "800", "3.20"]],
        )

    def test_detects_correct_format(self):
        assert parse_csv(self._csv(), "o1").format_detected == "onerpm"

    def test_parses_amount(self):
        result = parse_csv(self._csv(), "o1")
        assert result.payments[0]["amount"] == pytest.approx(3.20, abs=0.001)

    def test_source_contains_onerpm(self):
        result = parse_csv(self._csv(), "o1")
        assert "ONErpm" in result.payments[0]["source"]

    def test_parses_qty(self):
        result = parse_csv(self._csv(), "o1")
        assert result.events[0]["quantity"] == 800


class TestStemParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Period", "Platform", "Country Code", "Track Name", "ISRC", "Streams", "Net Revenue"],
            [["2024-04", "Spotify", "GB", "My Track", "USJKL1234567", "3500", "14.00"]],
        )

    def test_detects_correct_format(self):
        assert parse_csv(self._csv(), "s1").format_detected == "stem"

    def test_parses_amount(self):
        result = parse_csv(self._csv(), "s1")
        assert result.payments[0]["amount"] == pytest.approx(14.00, abs=0.001)

    def test_source_contains_stem(self):
        result = parse_csv(self._csv(), "s1")
        assert "Stem" in result.payments[0]["source"]

    def test_territory_from_country_code(self):
        result = parse_csv(self._csv(), "s1")
        assert result.events[0]["territory"] == "GB"


class TestLANDRParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Month", "Store", "Territory", "Track Name", "ISRC", "Net Quantity", "Net Revenue"],
            [["2024-05", "Deezer", "FR", "My Track", "USMNO1234567", "600", "2.40"]],
        )

    def test_detects_correct_format(self):
        assert parse_csv(self._csv(), "l1").format_detected == "landr"

    def test_parses_amount(self):
        result = parse_csv(self._csv(), "l1")
        assert result.payments[0]["amount"] == pytest.approx(2.40, abs=0.001)

    def test_source_contains_landr(self):
        result = parse_csv(self._csv(), "l1")
        assert "LANDR" in result.payments[0]["source"]

    def test_parses_net_quantity(self):
        result = parse_csv(self._csv(), "l1")
        assert result.events[0]["quantity"] == 600


class TestDittoParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Month", "Store", "Country", "Title", "ISRC", "Streams", "Net Revenue"],
            [["2024-06", "Tidal", "CA", "My Song", "USPQR1234567", "900", "3.60"]],
        )

    def test_detects_correct_format(self):
        assert parse_csv(self._csv(), "d1").format_detected == "ditto"

    def test_parses_amount(self):
        result = parse_csv(self._csv(), "d1")
        assert result.payments[0]["amount"] == pytest.approx(3.60, abs=0.001)

    def test_source_contains_ditto(self):
        result = parse_csv(self._csv(), "d1")
        assert "Ditto" in result.payments[0]["source"]

    def test_parses_streams(self):
        result = parse_csv(self._csv(), "d1")
        assert result.events[0]["quantity"] == 900


class TestReverbNationParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Date", "Platform", "Country", "Song", "ISRC", "Streams", "Revenue"],
            [["2024-07-01", "YouTube", "US", "My Song", "USSTU1234567", "2000", "8.00"]],
        )

    def test_detects_correct_format(self):
        assert parse_csv(self._csv(), "r1").format_detected == "reverbnation"

    def test_parses_amount(self):
        result = parse_csv(self._csv(), "r1")
        assert result.payments[0]["amount"] == pytest.approx(8.00, abs=0.001)

    def test_source_contains_reverbnation(self):
        result = parse_csv(self._csv(), "r1")
        assert "ReverbNation" in result.payments[0]["source"]

    def test_title_from_song_column(self):
        result = parse_csv(self._csv(), "r1")
        assert result.events[0]["work_title"] == "My Song"


class TestBandcampParser:
    def _csv(self) -> bytes:
        return _csv(
            ["Date", "Item Name", "Buyer Name", "Country", "Item Type", "SKU", "Quantity", "Price Per Item", "Revenue"],
            [["2024-08-15", "My Album", "John Doe", "US", "album", "SKU-001", "1", "10.00", "9.00"]],
        )

    def test_detects_correct_format(self):
        assert parse_csv(self._csv(), "b1").format_detected == "bandcamp"

    def test_parses_revenue(self):
        result = parse_csv(self._csv(), "b1")
        assert result.payments[0]["amount"] == pytest.approx(9.00, abs=0.001)

    def test_source_contains_bandcamp(self):
        result = parse_csv(self._csv(), "b1")
        assert "Bandcamp" in result.payments[0]["source"]

    def test_event_type_is_sale(self):
        result = parse_csv(self._csv(), "b1")
        assert result.events[0]["event_type"] == "SALE"

    def test_title_from_item_name(self):
        result = parse_csv(self._csv(), "b1")
        assert result.events[0]["work_title"] == "My Album"


# ---------------------------------------------------------------------------
# DistributorConnector
# ---------------------------------------------------------------------------

class TestDistributorConnector:
    def test_connect_false_without_key(self, monkeypatch):
        monkeypatch.delenv("AMUSE_API_KEY", raising=False)
        from XR7.ingestion.connectors.distributor import DistributorConnector
        c = DistributorConnector(config={}, distributor_name="Amuse")
        assert c.connect() is False

    def test_connect_true_with_env_key(self, monkeypatch):
        monkeypatch.setenv("AMUSE_API_KEY", "test-amuse-key")
        from XR7.ingestion.connectors.distributor import DistributorConnector
        c = DistributorConnector(config={}, distributor_name="Amuse")
        assert c.connect() is True

    def test_onerpm_connect_false_without_key(self, monkeypatch):
        monkeypatch.delenv("ONERPM_API_KEY", raising=False)
        from XR7.ingestion.connectors.distributor import DistributorConnector
        c = DistributorConnector(config={}, distributor_name="ONErpm")
        assert c.connect() is False

    def test_fetch_historical_raises_not_implemented(self, monkeypatch):
        monkeypatch.delenv("AMUSE_API_KEY", raising=False)
        from XR7.ingestion.connectors.distributor import DistributorConnector
        c = DistributorConnector(config={}, distributor_name="Amuse")
        with pytest.raises(NotImplementedError) as exc:
            c.fetch_historical("artist-1", datetime.now(timezone.utc), datetime.now(timezone.utc))
        assert "Amuse" in str(exc.value)
        assert "statements/upload" in str(exc.value)

    def test_supported_distributors_includes_all(self):
        from XR7.ingestion.connectors.distributor import DistributorConnector
        names = DistributorConnector.supported_distributors()
        for expected in ("Amuse", "United Masters", "ONErpm", "Stem", "LANDR",
                         "Ditto Music", "ReverbNation", "Bandcamp",
                         "DistroKid", "TuneCore", "CD Baby"):
            assert expected in names, f"Missing distributor: {expected}"

    def test_normalize_returns_list(self):
        from XR7.ingestion.connectors.distributor import DistributorConnector
        c = DistributorConnector(config={}, distributor_name="Stem")
        raw = [{"streams": 1000, "currency": "USD", "country": "US"}]
        result = c.normalize(raw)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["platform"] == "Stem"

