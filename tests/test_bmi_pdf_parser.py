"""BMI Royalty Statement PDF parser tests.

Live-PDF tests (against Tolliver's corpus at
``/home/jason/Downloads/6/tolliver/BMI Statements``) are skipped when
that directory is absent (CI / fresh checkouts) and run when present
(local dev with the real test corpus on hand).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from XR7.ingestion.bmi_pdf import (
    _decode_period,
    _parse_amount,
    bmi_pdf_to_events_and_payments,
    is_bmi_pdf,
    parse_bmi_pdf_bytes,
)


def test_parse_amount_basic():
    assert _parse_amount("$1,234.56") == 1234.56
    assert _parse_amount("$0.00") == 0.0
    assert _parse_amount("$0.42") == 0.42


def test_parse_amount_negative_parens():
    """Negative amounts on adjustment rows render as `$(0.12)`."""
    assert _parse_amount("$(0.12)") == -0.12
    assert _parse_amount("$(1,234.56)") == -1234.56


def test_decode_period_q3_2025():
    start, end = _decode_period("20253")
    assert start == date(2025, 7, 1)
    assert end == date(2025, 9, 30)


def test_decode_period_q4_2024():
    start, end = _decode_period("20244")
    assert start == date(2024, 10, 1)
    assert end == date(2024, 12, 31)


def test_decode_period_invalid():
    assert _decode_period("20255") == (None, None)  # quarter 5
    assert _decode_period("191ST") == (None, None)  # international code
    assert _decode_period("") == (None, None)


# ── Live-PDF tests ────────────────────────────────────────────────────────
# These run when Tolliver's corpus is on disk; otherwise skipped so they
# don't break CI. The corpus has 39 unique BMI Royalty Statement PDFs
# spanning 2015 Q4 to 2025 Q3, account 885077.

_CORPUS = Path("/home/jason/Downloads/6/tolliver/BMI Statements/BMI Statements")
_CORPUS_AVAILABLE = _CORPUS.is_dir()


@pytest.mark.skipif(not _CORPUS_AVAILABLE, reason="Tolliver BMI corpus not present")
def test_parses_2025_q3_statement():
    """Most recent statement format (2025 Q3, post-Creative-Office layout change)."""
    pdf = (_CORPUS / "royalty_885077_20253.pdf").read_bytes()
    result = parse_bmi_pdf_bytes(pdf)
    assert result.account_no == "000885077"
    assert result.ip_no == "00437.26.71.50"
    assert result.period_year == 2025
    assert result.period_quarter == 3
    assert result.distribution_date == date(2026, 2, 19)
    assert len(result.rows) > 100  # 364 in this statement at last check
    # Sanity: rows have all the required fields populated.
    sample = result.rows[0]
    for field in (
        "title",
        "work_no",
        "wh",
        "use_count",
        "period",
        "percent",
        "current_activity",
        "royalty_amt",
        "section",
    ):
        assert field in sample, f"missing {field}"


@pytest.mark.skipif(not _CORPUS_AVAILABLE, reason="Tolliver BMI corpus not present")
def test_parses_2015_q4_statement():
    """Oldest statement in the corpus — verifies the legacy
    Writer/Publisher Relations Office layout still parses."""
    pdf = (_CORPUS / "royalty_885077_20154.pdf").read_bytes()
    result = parse_bmi_pdf_bytes(pdf)
    assert result.account_no == "000885077"
    assert result.period_year == 2015
    assert result.period_quarter == 4
    assert len(result.rows) > 50


@pytest.mark.skipif(not _CORPUS_AVAILABLE, reason="Tolliver BMI corpus not present")
def test_is_bmi_pdf_recognises_full_corpus():
    """Every PDF in Tolliver's corpus must be recognised by the dispatcher
    detector. The Tolliver covers use the abbreviated `ACCT NO:` header,
    so a stricter `ACCOUNT NO:`-only check would silently route the
    entire corpus into the unsupported-PDF branch."""
    pdfs = sorted(_CORPUS.glob("royalty_885077_*.pdf"))
    missed = [p.name for p in pdfs if not is_bmi_pdf(p.read_bytes())]
    assert not missed, f"is_bmi_pdf rejected {len(missed)} BMI PDFs: {missed[:5]}"


@pytest.mark.skipif(not _CORPUS_AVAILABLE, reason="Tolliver BMI corpus not present")
def test_full_corpus_no_failures():
    """Every PDF in Tolliver's corpus should parse without throwing,
    and produce at least one row."""
    pdfs = sorted(_CORPUS.glob("royalty_885077_*.pdf"))
    assert len(pdfs) >= 30, "Expected the full Tolliver corpus to be on disk"
    failed: list[tuple[str, str]] = []
    for path in pdfs:
        try:
            data = path.read_bytes()
            r = parse_bmi_pdf_bytes(data)
            if not r.rows:
                failed.append((path.name, "no rows"))
        except Exception as exc:  # noqa: BLE001
            failed.append((path.name, str(exc)))
    assert not failed, f"{len(failed)} PDFs failed: {failed[:5]}"


@pytest.mark.skipif(not _CORPUS_AVAILABLE, reason="Tolliver BMI corpus not present")
def test_to_events_and_payments_shape():
    """Output dicts are shaped for the existing `_save_events` /
    `_save_payments` helpers — same key set as the bmi_real CSV path."""
    pdf = (_CORPUS / "royalty_885077_20253.pdf").read_bytes()
    events, payments, errors = bmi_pdf_to_events_and_payments(pdf, artist_id="art_test")
    assert errors == []
    assert len(events) == len(payments)
    assert len(events) > 0

    e = events[0]
    assert e["event_type"] == "STREAM"
    assert e["artist_id"] == "art_test"
    assert e["platform"].startswith("BMI / ")
    assert e["currency"] == "USD"
    assert e["quantity"] >= 1
    assert isinstance(e["work_title"], str)

    p = payments[0]
    assert p["payment_type"] == "ROYALTY"
    assert p["artist_id"] == "art_test"
    assert p["currency"] == "USD"
    assert p["source"].startswith("BMI / ")
    assert p["payer_account_id"] == "000885077"
    assert p["payer_ip_number"] == "00437.26.71.50"
    assert p["payer_work_id"]  # populated for every row
    # reference_id is stable per (work, period, source) — re-uploads dedup.
    assert p["reference_id"].startswith("bmi-pdf:")
