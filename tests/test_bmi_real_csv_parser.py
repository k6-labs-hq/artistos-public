"""
Tests for the real BMI Royalty Distribution Statement parser (#160).

Fixtures here are structurally accurate but synthesized — no real PII,
no real dollar amounts. Real-data validation happens out-of-band against
files held outside the repo.
"""

from __future__ import annotations

from datetime import date

from XR7.ingestion.statement_parser import (
    _decode_bmi_period,
    detect_format,
    parse_csv,
)

# ── Header line of a real BMI Royalty Distribution Statement CSV ─────────
# 28 columns including a trailing empty for BMI's CSV export quirk.
_BMI_REAL_HEADER = (
    "PERIOD,W OR P,PARTICIPANT NAME,PARTICIPANT #,IP #,TITLE NAME,TITLE #,"
    "PERF SOURCE,COUNTRY OF PERFORMANCE,SHOW NAME,EPISODE NAME,SHOW #,"
    "USE CODE,TIMING,PARTICIPANT %,PERF COUNT,BONUS LEVEL,ROYALTY AMOUNT,"
    "WITHHOLD,PERF PERIOD,CURRENT ACTIVITY AMT,"
    "HITS SONG OR TV NET SUPER USAGE BONUS,STANDARDS OR TV NET THEME BONUS,"
    "FOREIGN SOCIETY ADJUSTMENT,COMPANY CODE,COMPANY NAME,PERF DATE,"
)


def _row(
    *,
    period="20253",
    w_or_p="W",
    participant="DOE JANE",
    title="SAMPLE TITLE",
    perf_source="SPOTIFY PREM",
    country="UNITED STATES",
    perf_count="100",
    royalty="1.50",
) -> str:
    """One CSV data row, structurally matching the real format."""
    return (
        f"{period},{w_or_p},{participant},9999999,00000000000,{title},42424242,"
        f"{perf_source},{country},,,0,FF,000:00,100.00,{perf_count},,{royalty},,"
        f"{period},{royalty},0.00,0.00,,0,BMI,,"
    )


# ──────────────────────────────────────────────────────────────────────────
# Period decoder
# ──────────────────────────────────────────────────────────────────────────


def test_decode_bmi_period_q3_2025():
    start, end = _decode_bmi_period("20253")
    assert start == date(2025, 7, 1)
    assert end == date(2025, 9, 30)


def test_decode_bmi_period_q1_2025():
    start, end = _decode_bmi_period("20251")
    assert start == date(2025, 1, 1)
    assert end == date(2025, 3, 31)


def test_decode_bmi_period_q4_2024():
    start, end = _decode_bmi_period("20244")
    assert start == date(2024, 10, 1)
    assert end == date(2024, 12, 31)


def test_decode_bmi_period_invalid():
    assert _decode_bmi_period("20255") == (None, None)  # quarter 5 invalid
    assert _decode_bmi_period("191ST") == (None, None)  # international code
    assert _decode_bmi_period("") == (None, None)
    assert _decode_bmi_period("2025") == (None, None)


# ──────────────────────────────────────────────────────────────────────────
# Format detection
# ──────────────────────────────────────────────────────────────────────────


def test_detect_format_bmi_real():
    headers = [h.strip() for h in _BMI_REAL_HEADER.split(",") if h.strip()]
    assert detect_format(headers) == "bmi_real"


def test_detect_format_synthetic_bmi_still_detected():
    """Make sure the new bmi_real format doesn't capture the simpler synthetic shape."""
    headers = ["Title", "ISWC", "Date", "Payer", "Revenue"]
    assert detect_format(headers) == "bmi"


# ──────────────────────────────────────────────────────────────────────────
# Parser end-to-end
# ──────────────────────────────────────────────────────────────────────────


def test_parse_writer_streaming_row():
    csv = (
        _BMI_REAL_HEADER
        + "\n"
        + _row(perf_source="SPOTIFY PREM", perf_count="1234", royalty="2.50")
    )
    result = parse_csv(csv.encode(), artist_id="artist-1")

    assert result.format_detected == "bmi_real"
    assert len(result.events) == 1
    assert len(result.payments) == 1

    e = result.events[0]
    assert e["event_type"] == "STREAM"
    assert e["platform"] == "BMI / SPOTIFY PREM"
    assert e["territory"] == "US"
    assert e["quantity"] == 1234
    assert e["work_title"] == "SAMPLE TITLE"

    p = result.payments[0]
    assert p["payment_type"] == "ROYALTY"
    assert p["amount"] == 2.50
    assert p["period_start"] == date(2025, 7, 1)
    assert p["period_end"] == date(2025, 9, 30)
    assert p["source"] == "BMI / SPOTIFY PREM"
    # Per-row payer identifiers — required for dispute submissions per
    # docs/runbooks/bmi-dispute-attorney-brief.md.
    assert p["payer_account_id"] == "9999999"
    assert p["payer_ip_number"] == "00000000000"
    assert p["payer_work_id"] == "42424242"


def test_parse_radio_row_keeps_source_in_platform():
    """All BMI rows emit STREAM (EventType enum doesn't include PERFORMANCE).
    The platform field carries the source distinction."""
    csv = _BMI_REAL_HEADER + "\n" + _row(perf_source="RADIO", royalty="0.06")
    result = parse_csv(csv.encode(), artist_id="artist-1")
    assert result.events[0]["event_type"] == "STREAM"
    assert result.events[0]["platform"] == "BMI / RADIO"


def test_parse_publisher_row_skipped():
    """W OR P = P (publisher) rows are skipped in this MVP-stage parser."""
    csv = _BMI_REAL_HEADER + "\n" + _row(w_or_p="P", royalty="5.00")
    result = parse_csv(csv.encode(), artist_id="artist-1")
    assert result.events == []
    assert result.payments == []


def test_parse_zero_royalty_skipped():
    """Rows with $0.00 royalty are noise (foreign-society adjustments mostly)."""
    csv = _BMI_REAL_HEADER + "\n" + _row(royalty="0.00")
    result = parse_csv(csv.encode(), artist_id="artist-1")
    assert result.events == []
    assert result.payments == []


def test_parse_international_country_mapped():
    """Full country names map to ISO codes; unknown countries pass through truncated."""
    csv = _BMI_REAL_HEADER + "\n" + _row(country="UNITED KINGDOM", royalty="0.50")
    result = parse_csv(csv.encode(), artist_id="artist-1")
    assert result.events[0]["territory"] == "GB"


def test_parse_multiple_rows_aggregate():
    """Several rows produce matching event/payment counts."""
    rows = [
        _row(title="TRACK A", perf_source="SPOTIFY PREM", royalty="1.00"),
        _row(title="TRACK B", perf_source="APPLE FAMILY", royalty="0.50"),
        _row(title="TRACK C", perf_source="RADIO", royalty="0.10"),
    ]
    csv = _BMI_REAL_HEADER + "\n" + "\n".join(rows)
    result = parse_csv(csv.encode(), artist_id="artist-1")
    assert len(result.events) == 3
    assert len(result.payments) == 3
    assert sum(p["amount"] for p in result.payments) == 1.60
