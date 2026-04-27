"""
Tests for MLC mechanical royalty distribution parser (#162).

Fixtures here are structurally accurate but synthesized — no real PII,
no real dollar amounts. Real-data validation happens out-of-band against
files held outside the repo.
"""

from __future__ import annotations

from datetime import date

from XR7.ingestion.statement_parser import detect_format, parse_csv

# ── Header line of an MLC mechanical royalty distribution CSV ────────────
# 27 columns matching the .numbers export layout.
_MLC_HEADER = (
    "Payee Name,Payee MLC Number,Payee IPI Name Number,"
    "Original Publisher Name,Original Publisher MLC Number,"
    "Original Publisher IPI Name Number,Admin Publisher MLC Number,"
    "Admin Publisher Name,Admin Publisher IPI Name Number,"
    "Usage Period Start Date,Usage Period End Date,Territory,Use Type,"
    "DSP Identifier,DSP Name,MLC Song Code,Member Song Identifier,ISWC,"
    "Work Primary Title,Work Writer List,Work Payable %,Processing Type,"
    "Number of Usages,Royalty Amount,Late Fee Amount,Interest Amount,"
    "Distributed Amount"
)


def _row(
    *,
    payee="DOE JANE",
    payee_mlc="P000XX",
    period_start="2025-01-01",
    period_end="2025-01-31",
    dsp_name="Spotify",
    title="SAMPLE TITLE",
    processing_type="regular",
    usages="1000",
    royalty_amount="0.5000",
    late_fee="0.0000",
    interest="0.0000",
    distributed="0.5000",
) -> str:
    """One CSV data row, structurally matching the real MLC format."""
    return (
        f"{payee},{payee_mlc},,{payee},{payee_mlc},,,,,"
        f"{period_start},{period_end},US,Streaming,"
        f"M0000X,{dsp_name},XXXXX0,,,"
        f"{title},{payee.upper()},100.0,{processing_type},"
        f"{usages},{royalty_amount},{late_fee},{interest},{distributed}"
    )


# ──────────────────────────────────────────────────────────────────────────
# Format detection
# ──────────────────────────────────────────────────────────────────────────


def test_detect_format_mlc():
    headers = [h.strip() for h in _MLC_HEADER.split(",") if h.strip()]
    assert detect_format(headers) == "mlc"


def test_detect_format_mlc_does_not_clash_with_other_pros():
    """Real BMI and ASCAP shouldn't be detected as MLC."""
    bmi_headers = ["Title", "ISWC", "Date", "Payer", "Revenue"]
    assert detect_format(bmi_headers) == "bmi"
    ascap_headers = ["Work Title", "ISWC", "Performance Date", "Source", "Royalty"]
    assert detect_format(ascap_headers) == "ascap"


# ──────────────────────────────────────────────────────────────────────────
# Parser end-to-end
# ──────────────────────────────────────────────────────────────────────────


def test_parse_basic_streaming_row():
    csv = _MLC_HEADER + "\n" + _row(
        dsp_name="Spotify", usages="60153", royalty_amount="20.7677",
        distributed="20.7677",
    )
    result = parse_csv(csv.encode(), artist_id="artist-1")

    assert result.format_detected == "mlc"
    assert len(result.events) == 1
    assert len(result.payments) == 1

    e = result.events[0]
    assert e["event_type"] == "STREAM"
    assert e["platform"] == "MLC / Spotify"
    assert e["territory"] == "US"
    assert e["quantity"] == 60153
    assert e["work_title"] == "SAMPLE TITLE"

    p = result.payments[0]
    assert p["payment_type"] == "ROYALTY"
    assert p["amount"] == 20.7677
    assert p["period_start"] == date(2025, 1, 1)
    assert p["period_end"] == date(2025, 1, 31)
    assert "regular" in p["source"]


def test_parse_reprocessing_row_keeps_processing_type_in_source():
    """Reprocessing rows should be distinguishable in payment.source for downstream filtering."""
    csv = _MLC_HEADER + "\n" + _row(
        processing_type="reprocessing",
        royalty_amount="0.5000", late_fee="0.0001", interest="0.0001",
        distributed="0.5002",
    )
    result = parse_csv(csv.encode(), artist_id="artist-1")
    assert "reprocessing" in result.payments[0]["source"]
    # Distributed amount is preferred over Royalty Amount alone (includes interest + late fee).
    assert result.payments[0]["amount"] == 0.5002


def test_parse_zero_distributed_skipped():
    """Zero-amount rows are noise — placeholder entries with no real money."""
    csv = _MLC_HEADER + "\n" + _row(distributed="0.0000", royalty_amount="0.0000")
    result = parse_csv(csv.encode(), artist_id="artist-1")
    assert result.events == []
    assert result.payments == []


def test_parse_multiple_dsps_aggregated_correctly():
    rows = [
        _row(dsp_name="Spotify", usages="100000", distributed="20.00"),
        _row(dsp_name="Apple Music", usages="40000", distributed="33.00"),
        _row(dsp_name="YouTube", usages="5000", distributed="3.50"),
    ]
    csv = _MLC_HEADER + "\n" + "\n".join(rows)
    result = parse_csv(csv.encode(), artist_id="artist-1")
    assert len(result.events) == 3
    assert len(result.payments) == 3
    assert sum(p["amount"] for p in result.payments) == 56.50
    platforms = sorted(e["platform"] for e in result.events)
    assert platforms == ["MLC / Apple Music", "MLC / Spotify", "MLC / YouTube"]


def test_parse_distributed_includes_interest_and_late_fee():
    """Distributed Amount = Royalty + Late Fee + Interest. We use Distributed."""
    csv = _MLC_HEADER + "\n" + _row(
        royalty_amount="1.0000", late_fee="0.0500", interest="0.0100",
        distributed="1.0600",
    )
    result = parse_csv(csv.encode(), artist_id="artist-1")
    assert result.payments[0]["amount"] == 1.06
