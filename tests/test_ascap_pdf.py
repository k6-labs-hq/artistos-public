"""Tests for the ASCAP Writer Domestic Distribution PDF parser.

We don't ship a real ASCAP PDF as a fixture — they're large and contain
real artist data. Instead these tests exercise the parser's internals
(row regex, category detection, number formats) against synthetic
text that matches the layout we verified against Jerry Flowers' 2018-2025
statements.
"""

from __future__ import annotations

import pytest

from XR7.ingestion.ascap_pdf import (
    _ROW_RE,
    _ROW_RE_ONE_CREDIT,
    _detect_category,
)


class TestCategoryDetection:
    def test_canonical_category(self):
        assert _detect_category("ABC, CBS, NBC Network TV") == "ABC, CBS, NBC Network TV"

    def test_internet_subsection(self):
        assert (
            _detect_category("Internet: Audio & Music Videos - NAPSTER")
            == "Internet: NAPSTER"
        )

    def test_internet_subsection_with_continued_marker(self):
        # ASCAP wraps long category sections across pages, marking the
        # second page with "(continued)" — same logical category.
        assert (
            _detect_category("Internet: Audio & Music Videos - Pandora (continued)")
            == "Internet: Pandora"
        )

    def test_additional_categories_colon_form(self):
        assert (
            _detect_category("Additional Categories: Background/Foreground - AMI ENTERTAINMENT")
            == "Additional Categories: Background/Foreground - AMI ENTERTAINMENT"
        )

    def test_satellite_radio_dash_form(self):
        assert (
            _detect_category("Satellite Radio - SIRIRS")
            == "Satellite Radio - SIRIRS"
        )

    def test_summary_line_with_dollars_rejected(self):
        # The Statement Summary on page 4 has lines like:
        #   "Local TV - Blanket $18.63 - $18.63"
        # — these must NOT be picked up as category headers.
        assert _detect_category("Local TV - Blanket $18.63 - $18.63") is None

    def test_non_matching_line_returns_none(self):
        assert _detect_category("Member Name JERRY ALLEN FLOWERS") is None
        assert _detect_category("") is None


class TestRowRegex:
    def test_internet_simple_row(self):
        # `... C 5 F 0.00000 0.00192 $0.01862`
        line = "000001 CHASING AFTER YOU 887805267 100.00% 24.96% C 5 F 0.00000 0.00192 $0.01862"
        m = _ROW_RE.match(line)
        assert m is not None
        assert m.group("line_no") == "000001"
        assert m.group("title_blob") == "CHASING AFTER YOU"
        assert m.group("work_id") == "887805267"
        assert m.group("amount") == "0.01862"

    def test_tv_row_with_duration(self):
        line = (
            "000001 JIMMY KIMMEL LIVE MONICA CHUCK TAYLORS 924018722 100.00% 12.50% "
            "ABC C P 2 F 00:03:44 1.59546 60.68636 $588.65762"
        )
        m = _ROW_RE.match(line)
        assert m is not None
        assert m.group("work_id") == "924018722"
        assert m.group("amount") == "588.65762"

    def test_radio_row_with_commas_in_plays_and_credits(self):
        # The high-plays / high-credits case — without comma tolerance
        # in premium/total credits, this single $17,650 row was lost.
        line = (
            "000023 OUTSKIRTS 917992658 100.00% 12.50% C 55,177 FD Radio - Country "
            "1,335.71548 1,819.66804 $17,650.73678"
        )
        m = _ROW_RE.match(line)
        assert m is not None
        assert m.group("work_id") == "917992658"
        assert m.group("premium") == "1,335.71548"
        assert m.group("total_credits") == "1,819.66804"
        assert m.group("amount") == "17,650.73678"

    def test_additional_categories_one_credit_row(self):
        line = "000001 AMI ENTERTAINMENT A LITTLE MORE SUMMERTIME 890969395 100.00% 16.67% C 518 F 0.05145 $0.49907"
        # Should NOT match the two-credit regex (only one decimal before $).
        assert _ROW_RE.match(line) is None
        # Should match the one-credit regex.
        m = _ROW_RE_ONE_CREDIT.match(line)
        assert m is not None
        assert m.group("work_id") == "890969395"
        assert m.group("total_credits") == "0.05145"
        assert m.group("amount") == "0.49907"

    def test_non_data_lines_dont_match(self):
        for noise in (
            "Performing Right > ASCAP > USA",
            "Line CA Share # of Perf. Premium Total Royalty",
            "# Title Work ID % % C/S Plays Type Credits Credits Amount",
            "Total for Satellite Radio - SIRIRS: 21.46497 $208.20982",
            "Member Name Member ID IPI #",
            "JERRY ALLEN FLOWERS 990227565 515685244",
            "38743981 6",  # page footer
            "",
        ):
            assert _ROW_RE.match(noise) is None, f"matched: {noise!r}"
            assert _ROW_RE_ONE_CREDIT.match(noise) is None, f"matched: {noise!r}"


class TestParseAmount:
    def test_parens_negative(self):
        from XR7.ingestion.ascap_pdf import _parse_amount

        assert _parse_amount("(0.12)") == -0.12

    def test_comma_grouping(self):
        from XR7.ingestion.ascap_pdf import _parse_amount

        assert _parse_amount("17,650.73678") == pytest.approx(17650.73678)


class TestPlaysExtraction:
    """The plays count lives inside the `rest` middle text, always followed
    by a 1-3 letter perf-type code. Verify the extraction across the row
    shapes we know about."""

    @staticmethod
    def _extract_plays(rest: str) -> int:
        import re

        plays_matches = re.findall(
            r"\b(\d{1,3}(?:,\d{3})*|\d+)\s+([A-Z]{1,3})\b", rest
        )
        return int(plays_matches[-1][0].replace(",", "")) if plays_matches else 1

    def test_tv_row_skips_duration_digits(self):
        # `2 F 00:03:44` — duration is HH:MM:SS, plays is 2.
        # The naive "last integer" approach grabbed 44 here.
        rest = "100.00% 12.50% ABC C P 2 F 00:03:44"
        # Strip duration before extract (mimics the parser flow).
        import re

        rest = re.sub(r"\b\d{1,2}:\d{2}:\d{2}\b", " ", rest)
        assert self._extract_plays(rest) == 2

    def test_internet_row(self):
        # `100.00% 12.50% C 64 F` → 64 plays
        rest = "100.00% 12.50% C 64 F"
        assert self._extract_plays(rest) == 64

    def test_radio_row_with_comma_plays(self):
        # The 11,670-play row that the comma-blind regex missed.
        rest = "100.00% 12.50% C 11,670 FD Radio - Country"
        assert self._extract_plays(rest) == 11670

    def test_satellite_row_with_music_user_trailer(self):
        # `244 FB SIRIRS` — perf type FB, plays 244, then music_user.
        rest = "100.00% 12.50% C 244 FB SIRIRS"
        assert self._extract_plays(rest) == 244
