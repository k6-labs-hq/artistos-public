"""Tests for the SESAC Quarterly Royalty Statement PDF parser.

We don't ship a SESAC PDF as a fixture (real artist data). These tests
exercise the regex shapes and section detection against synthetic text
matching layouts verified against affiliate 422303's 2023-Q1 → 2025-Q4
statements.
"""

from __future__ import annotations

import pytest

from XR7.ingestion.sesac_pdf import (
    _INTERNATIONAL_ROW_RE,
    _ONELINE_ROW_RE,
    _TWOLINE_SONG_RE,
    _detect_section,
    _parse_amount,
)


class TestSectionDetection:
    @pytest.mark.parametrize(
        "header",
        [
            "CABLE TV",
            "MONITORED RADIO",
            "SATELLITE RADIO",
            "GENERAL/LIVE",
            "DIGITAL MEDIA",
            "BACKGROUND MUSIC SERVICES",
            "BACKGROUND MUSIC",
            "INTERNATIONAL",
        ],
    )
    def test_canonical_sections(self, header):
        assert _detect_section(header) == header

    def test_non_section_returns_none(self):
        for noise in (
            "NASHVILLE • NEW YORK • LOS ANGELES • LONDON",
            "QUARTERLY Royalty Statement: 2025/2",
            "Affiliate Name: MATTHEW JAMES ALDERMAN",
            "NOBODY (LOVE YOU LIKE I DO) CMT DAY",  # production-side line
            "",
        ):
            assert _detect_section(noise) is None


class TestCableTVRow:
    def test_basic_song_line(self):
        # Two-line shape; the song-side line is what we anchor on.
        line = "58449125 NOBODY (LOVE YOU LIKE I DO) 16.67 F 05:00 $0.1539"
        m = _TWOLINE_SONG_RE.match(line)
        assert m is not None
        assert m.group("song_id") == "58449125"
        assert m.group("song_title") == "NOBODY (LOVE YOU LIKE I DO)"
        assert m.group("share") == "16.67"
        assert m.group("use") == "F"
        assert m.group("duration") == "05:00"
        assert m.group("amount") == "0.1539"

    def test_duration_with_short_seconds(self):
        # `03:13` — 3-minute, 13-second duration.
        line = "694119643 TRUTH ABOUT YOU 16.66 F 03:13 $3.0120"
        m = _TWOLINE_SONG_RE.match(line)
        assert m is not None
        assert m.group("duration") == "03:13"


class TestOneLineRow:
    def test_digital_media_row(self):
        line = "58449125 NOBODY (LOVE YOU LIKE I DO) 16.67 ACCURADIO $0.0514"
        m = _ONELINE_ROW_RE.match(line)
        assert m is not None
        assert m.group("song_id") == "58449125"
        assert m.group("song_title") == "NOBODY (LOVE YOU LIKE I DO)"
        assert m.group("share") == "16.67"
        assert m.group("trailer") == "ACCURADIO"
        assert m.group("amount") == "0.0514"

    def test_monitored_radio_with_artist_and_source(self):
        # Trailer is "<ARTIST> <SOURCE>" — captured as one string.
        line = "712730224 CAN'T HAVE MINE 12.5 DYLAN SCOTT $1,123.3900"
        m = _ONELINE_ROW_RE.match(line)
        assert m is not None
        assert m.group("song_id") == "712730224"
        assert m.group("song_title") == "CAN'T HAVE MINE"
        assert m.group("share") == "12.5"
        assert m.group("trailer") == "DYLAN SCOTT"
        assert m.group("amount") == "1,123.3900"

    def test_amount_with_comma(self):
        line = "712730224 CAN'T HAVE MINE 12.5 DYLAN SCOTT $1,057.5900"
        m = _ONELINE_ROW_RE.match(line)
        assert m is not None
        assert _parse_amount(m.group("amount")) == pytest.approx(1057.59)

    def test_share_with_no_decimal(self):
        # e.g. 25 not 25.0
        line = "10617430 LIKES ON A PHOTO 25 SOMETHING ELSE $0.0100"
        m = _ONELINE_ROW_RE.match(line)
        assert m is not None
        assert m.group("share") == "25"


class TestInternationalRow:
    # The INTERNATIONAL row title vs. medium split is inherently ambiguous
    # from PDF text extraction (no column boundaries). We tolerate any
    # title/medium split that captures the song_id and amount correctly —
    # totals come out right even when the cosmetic split is off.
    def test_basic_intl_row_captures_anchors(self):
        line = "AUSTRALIA APRA 789250 CABLE & SATELLITE RETRANSMISS Audio-Visual Carriers $0.0089"
        m = _INTERNATIONAL_ROW_RE.match(line)
        assert m is not None
        assert m.group("prefix") == "AUSTRALIA APRA"
        assert m.group("song_id") == "789250"
        assert m.group("amount") == "0.0089"

    def test_general_medium_row_captures_anchors(self):
        line = "AUSTRALIA APRA 59809001 ADDITIONAL FOREIGN REVENUE General $2.9895"
        m = _INTERNATIONAL_ROW_RE.match(line)
        assert m is not None
        assert m.group("song_id") == "59809001"
        assert m.group("amount") == "2.9895"


class TestParseAmount:
    def test_simple(self):
        assert _parse_amount("0.0514") == pytest.approx(0.0514)

    def test_comma_grouping(self):
        assert _parse_amount("1,123.3900") == pytest.approx(1123.39)

    def test_parens_negative(self):
        assert _parse_amount("(0.50)") == -0.50
