from __future__ import annotations

from XR7.services.statement_signal_extractor import extract_statement_signals


def test_extract_statement_signals_identity_and_catalog_fields():
    csv_data = (
        "Artist Name,Email,Distributor Account ID,IPI,Store,Track Name,ISRC,ISWC,UPC,Label,Publisher\n"
        "Nova Artist,nova@example.com,dist-123,ipi-999,Spotify,Midnight Tape,USAAA1234567,T-123.456.789-0,123456789012,Orbit Label,Orbit Publishing\n"
    ).encode("utf-8")

    signals = extract_statement_signals(csv_data, "statement.csv", format_detected="distrokid")

    assert signals["artist_name"] == "Nova Artist"
    assert signals["email"] == "nova@example.com"
    assert signals["distributor_account_id"] == "dist-123"
    assert signals["pro_writer_id"] == "ipi-999"
    assert "Spotify" in signals["distributor_list"]
    assert "Midnight Tape" in signals["catalog_titles"]
    assert "USAAA1234567" in signals["isrcs"]
    assert "T-123.456.789-0" in signals["iswcs"]
    assert "123456789012" in signals["upcs"]
