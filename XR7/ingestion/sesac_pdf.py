"""Parser for SESAC's "Quarterly Royalty Statement" PDF format.

These are the per-quarter statement PDFs a SESAC affiliate downloads
from the SESAC member portal. SESAC doesn't publish a CSV equivalent
with the same line-item detail; the PDF is what artists have.

Layout summary (verified against statements 2023-Q1 → 2025-Q4 for
affiliate 422303):

    NASHVILLE • NEW YORK • LOS ANGELES • LONDON
    35 MUSIC SQUARE EAST, NASHVILLE, TN 37203
    615-320-0055 WWW.SESAC.COM
    QUARTERLY Royalty Statement: <YYYY>/<Q>
    Page <N> of <M>
    Affiliate Name: <NAME>  Dist. Period: <Month> <Year> - <Month> <Year>
    Affiliate #: <ID>       Dist. Date: <Month Day, Year>

Sections (each in its own all-caps block, on its own line):

    CABLE TV
    MONITORED RADIO         (broadcast radio)
    SATELLITE RADIO
    GENERAL/LIVE
    DIGITAL MEDIA           (streaming + interactive)
    BACKGROUND MUSIC (SERVICES)
    INTERNATIONAL
    SUMMARY OF EARNINGS     (final-page totals, not data)

Body rows come in two distinct shapes.

(1) TV / Radio / Satellite — TWO physical lines per logical row:

      <PRODUCTION_TITLE> <SOURCE> <DAY_PART> [<AIR_DATE> <EPISODE>] [<OCCUR> <STATIONS>]
      <SONG#> <SONG_TITLE> <SHARE%> <USE> <DURATION> $<AMOUNT>

    where USE is 1-3 letters from SESAC's legend (F, BG, J, P, OT, CT, ST, L)
    and DURATION is M:SS or MM:SS.

(2) DIGITAL MEDIA / INTERNATIONAL — ONE line per row:

      <SONG#> <SONG_TITLE> <SHARE%> <SOURCE_NAME> $<AMOUNT>

We anchor row detection on the SONG# at start + $AMOUNT at end. The
production-side line for shape (1) is captured as context for the
event/payment but isn't strictly required — we tolerate cases where the
PDF text extractor merges or reorders the two lines.

Output mirrors the BMI/ASCAP parsers so downstream rules + dispute
template routing work without per-payer branches.
"""

from __future__ import annotations

import io
import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Iterable

logger = logging.getLogger(__name__)


# Header field regexes.
_HEADER_STATEMENT_RE = re.compile(
    r"QUARTERLY Royalty Statement:\s*(?P<year>\d{4})/(?P<quarter>[1-4])"
)
_HEADER_AFFILIATE_NAME_RE = re.compile(
    r"Affiliate Name:\s*([A-Z][A-Z'\-\.\s]+?)(?=\s{2,}|\s+Dist\.|\n|$)"
)
_HEADER_AFFILIATE_ID_RE = re.compile(r"Affiliate\s*#:\s*(\d+)")
_HEADER_DIST_DATE_RE = re.compile(
    r"Dist\.\s*Date:\s*([A-Z][a-z]+\s+\d{1,2},\s*\d{4})"
)
_HEADER_PERIOD_RE = re.compile(
    r"Dist\.\s*Period:\s*([A-Z][a-z]+)\s+(\d{4})\s*-\s*([A-Z][a-z]+)\s+(\d{4})"
)

# Detection fingerprints.
_SESAC_FINGERPRINT_DOMAIN = re.compile(r"WWW\.SESAC\.COM", re.IGNORECASE)
_SESAC_FINGERPRINT_STATEMENT = re.compile(
    r"QUARTERLY Royalty Statement", re.IGNORECASE
)

# Canonical section headers — match exactly (line is just the section name).
_SECTION_HEADERS = (
    "CABLE TV",
    "MONITORED RADIO",
    "SATELLITE RADIO",
    "GENERAL/LIVE",
    "DIGITAL MEDIA",
    "BACKGROUND MUSIC SERVICES",
    "BACKGROUND MUSIC",
    "INTERNATIONAL",
)

# Lines that look like a section header but are end-of-statement noise.
_END_OF_DATA_HEADERS = ("SUMMARY OF EARNINGS", "LEGEND")

# Two-line TV/Radio row shape — the song-side line is the anchor:
#   <song#> <song_title> <share%> <use_code> <m:ss> $<amount>
# song# is 4-10 digits (we've seen 1025491 and 729692698 in real data).
_USE_CODES = "F|BG|J|P|OT|CT|ST|L"
_TWOLINE_SONG_RE = re.compile(
    r"^(?P<song_id>\d{4,10})\s+"
    r"(?P<song_title>.+?)\s+"
    r"(?P<share>\d{1,3}(?:\.\d{1,3})?)\s+"
    r"(?P<use>(?:" + _USE_CODES + r")\b)\s+"
    r"(?P<duration>\d{1,2}:\d{2})\s+"
    r"\$(?P<amount>-?\(?[\d,]+\.\d{2,8}\)?)\s*$"
)

# Single-line row used by domestic non-Cable sections. The trailer
# between share% and $amount has different shapes per section:
#   DIGITAL MEDIA:       <source>                 (e.g. "AMAZON MUSIC FREE")
#   SATELLITE RADIO:     <source>                 (e.g. "SIRIUS XM")
#   GENERAL/LIVE:        <source>                 (e.g. "Live Performance")
#   BACKGROUND MUSIC:    <source>                 (e.g. "MUS")
#   MONITORED RADIO:     <artist> <source>        (e.g. "DYLAN SCOTT")
# Rather than enumerate every shape, capture the whole middle as `trailer`
# and let the caller decide whether to subdivide it.
_ONELINE_ROW_RE = re.compile(
    r"^(?P<song_id>\d{4,10})\s+"
    r"(?P<song_title>.+?)\s+"
    r"(?P<share>\d{1,3}(?:\.\d{1,3})?)\s+"
    r"(?P<trailer>\S.*?\S)\s+"
    r"\$(?P<amount>-?\(?[\d,]+\.\d{2,8}\)?)\s*$"
)
# INTERNATIONAL row shape — starts with COUNTRY + SOCIETY before song#:
#   AUSTRALIA APRA 789250 CABLE & SATELLITE RETRANSMISS Audio-Visual Carriers $0.0089
# Country can be multi-word (UNITED KINGDOM). Society follows.
_INTERNATIONAL_ROW_RE = re.compile(
    r"^(?P<prefix>[A-Z][A-Z ]+?)\s+"
    r"(?P<song_id>\d{4,10})\s+"
    r"(?P<song_title>.+?)\s+"
    r"(?P<medium>\S.*?\S)\s+"
    r"\$(?P<amount>-?\(?[\d,]+\.\d{2,8}\)?)\s*$"
)

# Lines we skip outright (column headers, page footers, totals, address lines).
_SKIP_PATTERNS = (
    re.compile(r"^NASHVILLE\s*•"),
    re.compile(r"^35 MUSIC SQUARE"),
    re.compile(r"^\d{3}-\d{3}-\d{4}"),
    re.compile(r"^Page \d+ of \d+", re.IGNORECASE),
    re.compile(r"^Affiliate\b"),
    re.compile(r"^Production Title\b"),
    re.compile(r"^Song #\b"),
    re.compile(r"\bSUBTOTAL:\s*\$"),
    re.compile(r"^Total Earnings:"),
    re.compile(r"^Earnings Paid:"),
    re.compile(r"^F=Feature\b"),  # LEGEND row
    re.compile(r"^\s*$"),
)


_MONTH_NUM = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}


@dataclass
class SesacPdfParseResult:
    affiliate_id: str | None = None
    affiliate_name: str | None = None
    statement_year: int | None = None
    statement_quarter: int | None = None
    distribution_date: date | None = None
    period_start: date | None = None
    period_end: date | None = None
    rows: list[dict] = field(default_factory=list)
    skipped_lines: int = 0
    sections_seen: list[str] = field(default_factory=list)


def is_sesac_pdf(pdf_bytes: bytes) -> bool:
    """Return True if these bytes look like a SESAC Quarterly Royalty Statement.

    Reads up to the first 3 pages of extracted text so the SESAC domain
    line (page 1) plus the "Quarterly Royalty Statement" header (page 1
    or 2) are both available.
    """
    try:
        import pdfplumber  # noqa: PLC0415

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if not pdf.pages:
                return False
            head_parts = []
            for page in pdf.pages[:3]:
                head_parts.append(page.extract_text() or "")
            head = "\n".join(head_parts)
    except Exception:  # noqa: BLE001
        return False
    return bool(
        _SESAC_FINGERPRINT_DOMAIN.search(head)
        and _SESAC_FINGERPRINT_STATEMENT.search(head)
        and "Affiliate #:" in head
    )


def _parse_amount(s: str) -> float:
    """`1,234.56` / `(0.12)` → float (negative for parens)."""
    s = s.replace(",", "").strip()
    if s.startswith("(") and s.endswith(")"):
        return -float(s[1:-1])
    return float(s)


def _parse_distribution_date(s: str) -> date | None:
    try:
        return datetime.strptime(s.strip(), "%B %d, %Y").date()
    except ValueError:
        return None


def _quarter_bounds(year: int, quarter: int) -> tuple[date, date]:
    start_month = (quarter - 1) * 3 + 1
    end_month = start_month + 2
    last_day = {3: 31, 6: 30, 9: 30, 12: 31}[end_month]
    return date(year, start_month, 1), date(year, end_month, last_day)


def _detect_section(line: str) -> str | None:
    s = line.strip()
    if s in _SECTION_HEADERS:
        return s
    return None


def _is_end_of_data(line: str) -> bool:
    return line.strip() in _END_OF_DATA_HEADERS


def _looks_like_data_line(stripped: str) -> bool:
    """Cheap pre-check: starts with a song# (4-10 digits) and contains '$'."""
    return bool(re.match(r"^\d{4,10}\s", stripped)) and "$" in stripped


def parse_sesac_pdf_bytes(pdf_bytes: bytes) -> SesacPdfParseResult:
    """Parse SESAC Quarterly Royalty Statement PDF bytes into structured rows."""
    import pdfplumber  # noqa: PLC0415

    result = SesacPdfParseResult()
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    full_text = "\n".join(text_parts)

    # Header fields.
    if m := _HEADER_STATEMENT_RE.search(full_text):
        result.statement_year = int(m.group("year"))
        result.statement_quarter = int(m.group("quarter"))
        result.period_start, result.period_end = _quarter_bounds(
            result.statement_year, result.statement_quarter
        )
    if m := _HEADER_AFFILIATE_ID_RE.search(full_text):
        result.affiliate_id = m.group(1)
    if m := _HEADER_AFFILIATE_NAME_RE.search(full_text):
        result.affiliate_name = m.group(1).strip()
    if m := _HEADER_DIST_DATE_RE.search(full_text):
        result.distribution_date = _parse_distribution_date(m.group(1))
    # Dist. Period is informational — quarter bounds already give us
    # start/end. Parse it only if the statement code didn't.
    if result.period_start is None:
        if m := _HEADER_PERIOD_RE.search(full_text):
            try:
                sm = _MONTH_NUM[m.group(1)]
                sy = int(m.group(2))
                em = _MONTH_NUM[m.group(3)]
                ey = int(m.group(4))
                # Use first/last day of month.
                last_day = {3: 31, 6: 30, 9: 30, 12: 31}.get(em, 30)
                result.period_start = date(sy, sm, 1)
                result.period_end = date(ey, em, last_day)
            except (KeyError, ValueError):
                pass

    # Walk lines, tracking section context. For the two-line TV/Radio
    # rows, the production-side line is captured as `production_context`
    # so the song-side line that follows can use it as event metadata.
    current_section: str | None = None
    production_context: str | None = None
    in_data_section = False

    for line in full_text.splitlines():
        # End-of-data markers: stop emitting rows.
        if _is_end_of_data(line):
            in_data_section = False
            production_context = None
            continue

        # New section header.
        sec = _detect_section(line)
        if sec is not None:
            current_section = sec
            in_data_section = True
            production_context = None
            if sec not in result.sections_seen:
                result.sections_seen.append(sec)
            continue

        if not in_data_section:
            continue

        if any(p.search(line) for p in _SKIP_PATTERNS):
            production_context = None
            continue

        stripped = line.strip()

        # INTERNATIONAL rows start with COUNTRY (letters) not song# —
        # the digit-prefix precheck doesn't apply. Try the dedicated
        # regex before falling through.
        if current_section == "INTERNATIONAL":
            m = _INTERNATIONAL_ROW_RE.match(stripped)
            if m is None:
                # Probably a column header continuation or page footer;
                # skip silently.
                continue
            try:
                amount = _parse_amount(m.group("amount"))
            except ValueError:
                result.skipped_lines += 1
                continue
            prefix_tokens = m.group("prefix").split()
            country = " ".join(prefix_tokens[:-1]) if len(prefix_tokens) > 1 else prefix_tokens[0]
            society = prefix_tokens[-1] if len(prefix_tokens) > 1 else ""
            subsection = (
                f"{country} / {society} / {m.group('medium').strip()}"
                if society
                else f"{country} / {m.group('medium').strip()}"
            )
            result.rows.append(
                {
                    "section": current_section,
                    "subsection": subsection,
                    "song_id": m.group("song_id"),
                    "song_title": " ".join(m.group("song_title").split()),
                    "share_pct": None,
                    "use_code": None,
                    "duration": None,
                    "plays": 1,
                    "royalty_amt": amount,
                    "production_context": None,
                }
            )
            continue

        if not _looks_like_data_line(stripped):
            # Not a data line in a data section — probably the
            # production-side line preceding a Cable TV song-line.
            # Stash it as context for the next song row.
            if stripped:
                production_context = stripped
            continue

        # Cable TV uses the two-line shape (production-line above,
        # song-line with USE code + duration here). Every other section
        # uses the one-line shape with a variable trailer.
        if current_section == "CABLE TV":
            m = _TWOLINE_SONG_RE.match(stripped)
            if m is not None:
                try:
                    amount = _parse_amount(m.group("amount"))
                    share = float(m.group("share"))
                except ValueError:
                    result.skipped_lines += 1
                    continue
                result.rows.append(
                    {
                        "section": current_section,
                        "subsection": None,
                        "song_id": m.group("song_id"),
                        "song_title": " ".join(m.group("song_title").split()),
                        "share_pct": share,
                        "use_code": m.group("use"),
                        "duration": m.group("duration"),
                        "plays": 1,
                        "royalty_amt": amount,
                        "production_context": production_context,
                    }
                )
                production_context = None
                continue
            # CABLE TV rows that don't match — also try one-line in case
            # SESAC ever emits a degenerate row, but log skip otherwise.
            result.skipped_lines += 1
            continue

        # Domestic single-line: MONITORED RADIO, SATELLITE RADIO,
        # GENERAL/LIVE, BACKGROUND MUSIC SERVICES, DIGITAL MEDIA.
        m = _ONELINE_ROW_RE.match(stripped)
        if m is None:
            result.skipped_lines += 1
            continue
        try:
            amount = _parse_amount(m.group("amount"))
            share = float(m.group("share"))
        except ValueError:
            result.skipped_lines += 1
            continue
        result.rows.append(
            {
                "section": current_section,
                "subsection": m.group("trailer").strip(),
                "song_id": m.group("song_id"),
                "song_title": " ".join(m.group("song_title").split()),
                "share_pct": share,
                "use_code": None,
                "duration": None,
                "plays": 1,
                "royalty_amt": amount,
                "production_context": None,
            }
        )
        continue

    return result


def sesac_pdf_to_events_and_payments(
    pdf_bytes: bytes, artist_id: str
) -> tuple[list[dict], list[dict], list[str]]:
    """Convert a SESAC PDF's bytes into Event + Payment dicts ready for
    `_save_events` / `_save_payments`.

    Returns ``(events, payments, errors)``. Empty events+payments with
    a non-empty errors list signals "we tried but found nothing usable."
    """
    errors: list[str] = []
    try:
        result = parse_sesac_pdf_bytes(pdf_bytes)
    except Exception as exc:  # noqa: BLE001
        return [], [], [f"SESAC PDF parse failed: {exc}"]

    if not result.rows:
        errors.append("No data rows extracted from SESAC PDF")
        return [], [], errors

    events: list[dict] = []
    payments: list[dict] = []
    distribution_dt = (
        datetime.combine(result.distribution_date, datetime.min.time(), tzinfo=timezone.utc)
        if result.distribution_date
        else datetime.now(timezone.utc)
    )
    period_mid_dt = distribution_dt
    if result.period_start and result.period_end:
        midpoint = result.period_start + (result.period_end - result.period_start) / 2
        period_mid_dt = datetime.combine(
            midpoint, datetime.min.time(), tzinfo=timezone.utc
        )

    for r in result.rows:
        section = r["section"]
        subsection = r.get("subsection")
        platform = (
            f"SESAC / {section} / {subsection}" if subsection else f"SESAC / {section}"
        )
        territory = "INT" if section == "INTERNATIONAL" else "US"
        royalty = float(r["royalty_amt"])
        plays = int(r["plays"])
        unit_value = round(royalty / plays, 8) if plays > 0 else 0.0

        events.append(
            {
                "event_type": "STREAM",
                "artist_id": artist_id,
                "platform": platform,
                "territory": territory,
                "timestamp": period_mid_dt,
                "quantity": plays,
                "unit_value": unit_value,
                "currency": "USD",
                "work_title": r["song_title"],
                "share_pct": r.get("share_pct"),
            }
        )
        # Stable per-row reference for dedup-on-reupload. Includes section,
        # song_id, and a row-position fallback so identical-amount rows
        # within a section (e.g. ACCURADIO plays of the same song) don't
        # collide. Append the index to the ref so dedup is row-stable.
        period_key = (
            result.period_start.isoformat() if result.period_start else "unknown"
        )
        ref_idx = len(payments)  # monotonic per artist within this statement
        payments.append(
            {
                "payment_type": "ROYALTY",
                "artist_id": artist_id,
                "amount": round(royalty, 6),
                "currency": "USD",
                "source": platform,
                "period_start": result.period_start,
                "period_end": result.period_end,
                "received_at": distribution_dt,
                "reference_id": (
                    f"sesac-pdf:{r['song_id']}:{period_key}:{section}:"
                    f"{subsection or 'na'}:{ref_idx}"
                ),
                "payer_account_id": result.affiliate_id,
                "payer_ip_number": None,  # SESAC statements don't carry IPI
                "payer_work_id": r["song_id"],
            }
        )

    return events, payments, errors


__all__ = (
    "SesacPdfParseResult",
    "is_sesac_pdf",
    "parse_sesac_pdf_bytes",
    "sesac_pdf_to_events_and_payments",
)


def _all() -> Iterable[str]:
    return __all__
