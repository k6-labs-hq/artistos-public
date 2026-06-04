"""Parser for ASCAP's "Writer Domestic Distribution" PDF format.

These are the quarterly statement PDFs an ASCAP member can download from
the ASCAP Member Access portal. Unlike BMI's PDF, ASCAP doesn't publish a
CSV equivalent with the same line-item detail — the PDF is often the only
form an artist has.

Layout summary (verified against statements 2018→2025 for member 990227565):

    Writer Domestic Distribution For:
    Member Name: <FIRST LAST>
    Member ID: <DIGITS>
    IPI #: <DIGITS>
    <Month> <Year>                                      ← distribution period
    Royalty Total $<X.XX>
    ...
    Advice #: <DIGITS>  Date : <MM-DD-YYYY>             ← distribution date

    Page 2+:
    <Period Start> to <Period End> Performances        ← performance period
    Survey Year <YYYY>

    Per-page section headers (the performance category):
    Performing Right > ASCAP > USA
    <CATEGORY NAME>                                     ← e.g. "Cable TV - Blanket"

    For Internet (and similar) sub-categorized sections, the layout is:
    Internet: Audio & Music Videos - <DSP NAME>         ← e.g. "- NAPSTER"

Body rows come in two main shapes depending on category:

    TV / Radio (with Series, Network, Duration columns):
      LINE# SERIES_TEXT...    TITLE  WORK_ID  CA%  SHARE%  NET  C/S  PART  PLAYS  TYPE  HH:MM:SS  PREM  TOTAL  $AMT

    Internet / Satellite (no series/duration):
      LINE# TITLE  WORK_ID  CA%  SHARE%  C/S  PLAYS  TYPE  [MUSIC_USER]  PREM  TOTAL  $AMT

We anchor the row regex on three reliable elements: the line number at the
start, an 8-9 digit Work ID partway through, and a `$<dollars>.<cents>`
amount at the end. Everything between line# and Work ID becomes the title
blob (which sometimes carries series/episode noise for TV — accepted for
now; refinement deferred).

We extract one synthetic STREAM Event per line plus one ROYALTY Payment,
matching the BMI parser's shape so downstream rules + payer_office
routing work without per-payer branches.
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
_HEADER_MEMBER_NAME_RE = re.compile(r"Member Name:\s*([A-Z][A-Z'\-\.\s]+?)(?=\s{2,}|\s+Member ID|\n|$)")
_HEADER_MEMBER_ID_RE = re.compile(r"Member ID:\s*(\d+)")
_HEADER_IPI_RE = re.compile(r"IPI\s*#:\s*(\d+)")
_HEADER_DIST_DATE_RE = re.compile(r"Date\s*:\s*(\d{2}-\d{2}-\d{4})")
_HEADER_PERIOD_RE = re.compile(
    r"([A-Z][a-z]+)\s+(\d{1,2}),\s*(\d{4})\s+to\s+([A-Z][a-z]+)\s+(\d{1,2}),\s*(\d{4})\s+Performances"
)
_HEADER_CREDIT_VALUE_RE = re.compile(r"Credit Value\s*=\s*\$(\d+\.\d+)")

# Detection signature: the title block on page 1. We require BOTH the
# ASCAP corporate name AND the "Writer Domestic Distribution" subtitle.
# International Performance Statements look identical structurally (same
# member header, same "American Society of..." line) but the body is a
# per-country / per-licensor table with no work IDs / play counts, so a
# different parser would be needed. For now we reject them with a clear
# error rather than producing empty/garbage rows.
_ASCAP_FINGERPRINT_CORP = re.compile(
    r"American Society of Composers,\s*Authors and Publishers", re.IGNORECASE
)
_ASCAP_FINGERPRINT_DOMESTIC = re.compile(
    r"Writer Domestic Distribution", re.IGNORECASE
)
_ASCAP_FINGERPRINT_INTERNATIONAL = re.compile(
    r"International Performance Statement", re.IGNORECASE
)

# Section header detection. Performance categories appear as their own
# lines beneath "Performing Right > ASCAP > USA". List is the set of
# canonical category names observed in real statements; a free-form
# "Internet: Audio & Music Videos - <DSP>" pattern is handled separately
# so we capture the DSP name.
_CATEGORY_NAMES = (
    "ABC, CBS, NBC Network TV",
    "FOX, CW, MY Network TV",
    "Univision",
    "Local TV - Blanket",
    "Local TV - Per Program",
    "Cable TV - Blanket",
    "Cable TV - Per Program",
    "PBS",
    "Broadcast and Satellite Radio",
    "Radio - Includes Commercial, NPR and College",
    "Internet",
    "Additional Categories",
    "Symphonic Concerts",
    "Recitals",
    "Educational Concerts",
    "Satellite Radio",
)
_INTERNET_SUBSECTION_RE = re.compile(
    r"^Internet:\s*Audio\s*&\s*Music\s*Videos\s*-\s*(.+?)\s*(?:\(continued\))?\s*$"
)
_GENERIC_DASH_SUBSECTION_RE = re.compile(
    r"^(Cable TV|Local TV|Satellite Radio|Broadcast and Satellite Radio|Additional Categories)\s*-\s*(.+?)\s*$"
)
# "Additional Categories: <sub>" header variants — e.g.
# "Additional Categories: Background/Foreground - AMI ENTERTAINMENT".
_ADDITIONAL_COLON_RE = re.compile(
    r"^Additional Categories:\s*(.+?)\s*(?:\(continued\))?\s*$"
)

# Line-item row regex. Anchors:
#   - LINE#: 6-digit zero-padded counter at start
#   - WORK_ID: 8-9 digit ASCAP work identifier
#   - $AMOUNT: the final dollar value
# Title is greedy match up to (and excluding) the Work ID. Middle text
# (percentages, network codes, play counts, duration, credits) is ignored
# here and reconstructed only as needed.
# Standard row: two decimal credit columns (Premium + Total) before $amt.
# Used by TV, Radio, Internet, Satellite — anything in the main detail tables.
_ROW_RE = re.compile(
    r"^(?P<line_no>\d{6})\s+"
    r"(?P<title_blob>.+?)\s+"
    r"(?P<work_id>\d{8,9})\s+"
    r"(?P<rest>.+?)\s+"
    r"(?P<premium>-?[\d,]+\.\d{1,8})\s+"
    r"(?P<total_credits>-?[\d,]+\.\d{1,8})\s+"
    r"\$(?P<amount>-?\(?[\d,]+\.\d{2,8}\)?)\s*$"
)
# "Additional Categories" row: only ONE Credits column before $amt.
# Shape: LINE# MUSIC_USER TITLE WORK_ID PCT% PCT% C/S PLAYS TYPE CREDITS $AMT.
_ROW_RE_ONE_CREDIT = re.compile(
    r"^(?P<line_no>\d{6})\s+"
    r"(?P<title_blob>.+?)\s+"
    r"(?P<work_id>\d{8,9})\s+"
    r"(?P<rest>.+?)\s+"
    r"(?P<total_credits>-?[\d,]+\.\d{1,8})\s+"
    r"\$(?P<amount>-?\(?[\d,]+\.\d{2,8}\)?)\s*$"
)

# Lines we skip outright (totals, page footers, column headers).
_SKIP_PATTERNS = (
    re.compile(r"^Total for\b", re.IGNORECASE),
    re.compile(r"^Line\b"),
    re.compile(r"^#\s+Series"),
    re.compile(r"^\d{8}\s+\d+$"),  # page footer "<advice#> <page#>"
    re.compile(r"^Performing Right\b"),
    re.compile(r"^Music User Summary"),
    re.compile(r"^Performance Category:"),
    re.compile(r"^Performance Categories"),
    re.compile(r"^Member Name\b"),
    re.compile(r"^Survey Year"),
    re.compile(r"^Credit Value"),
    re.compile(r"^\s*$"),
)


@dataclass
class AscapPdfParseResult:
    member_id: str | None = None
    ipi_number: str | None = None
    member_name: str | None = None
    distribution_date: date | None = None
    period_start: date | None = None
    period_end: date | None = None
    credit_value: float | None = None
    rows: list[dict] = field(default_factory=list)
    skipped_lines: int = 0
    categories_seen: list[str] = field(default_factory=list)


def is_ascap_pdf(pdf_bytes: bytes) -> bool:
    """Return True if these bytes look like an ASCAP Writer Domestic
    Distribution PDF — the variant this parser handles.

    Reads the first ~3 pages of extracted text (covers cover page +
    summary header so the "Writer Domestic Distribution" subtitle is
    seen even if the cover doesn't carry it).

    Excludes International Performance Statements explicitly — they're
    ASCAP-issued but have a per-country/per-licensor body that this
    parser can't read.
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
    if not _ASCAP_FINGERPRINT_CORP.search(head):
        return False
    if "Member ID:" not in head:
        return False
    if _ASCAP_FINGERPRINT_INTERNATIONAL.search(head):
        return False
    return bool(_ASCAP_FINGERPRINT_DOMESTIC.search(head))


def is_ascap_international_pdf(pdf_bytes: bytes) -> bool:
    """Cheap check used by the dispatcher to give a clearer error message
    when an artist uploads an ASCAP International Performance Statement
    instead of the Domestic Distribution PDF we can parse today.
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
        _ASCAP_FINGERPRINT_CORP.search(head)
        and _ASCAP_FINGERPRINT_INTERNATIONAL.search(head)
    )


def _parse_amount(s: str) -> float:
    """`1,234.56` / `(0.12)` → float (negative for parens)."""
    s = s.replace(",", "").strip()
    if s.startswith("(") and s.endswith(")"):
        return -float(s[1:-1])
    return float(s)


def _parse_distribution_date(s: str) -> date | None:
    try:
        return datetime.strptime(s.strip(), "%m-%d-%Y").date()
    except ValueError:
        return None


_MONTH_NUM = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}


def _detect_category(line: str) -> str | None:
    """Return the canonical category for a line that's a section header.

    Rejects lines containing `$` so the Statement Summary on page 4
    (which has lines like "Local TV - Blanket $18.63 - $18.63")
    doesn't pollute the category state for the actual data pages.
    """
    stripped = line.strip()
    if "$" in stripped:
        return None
    if m := _INTERNET_SUBSECTION_RE.match(stripped):
        return f"Internet: {m.group(1).strip()}"
    if m := _ADDITIONAL_COLON_RE.match(stripped):
        return f"Additional Categories: {m.group(1).strip()}"
    if m := _GENERIC_DASH_SUBSECTION_RE.match(stripped):
        return f"{m.group(1)} - {m.group(2).strip()}"
    # Exact match against the canonical category list.
    for name in _CATEGORY_NAMES:
        if stripped == name:
            return name
    return None


def parse_ascap_pdf_bytes(pdf_bytes: bytes) -> AscapPdfParseResult:
    """Parse ASCAP Writer Distribution PDF bytes into structured rows."""
    import pdfplumber  # noqa: PLC0415

    result = AscapPdfParseResult()
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")
    full_text = "\n".join(text_parts)

    # Header fields.
    if m := _HEADER_MEMBER_ID_RE.search(full_text):
        result.member_id = m.group(1)
    if m := _HEADER_IPI_RE.search(full_text):
        result.ipi_number = m.group(1)
    if m := _HEADER_MEMBER_NAME_RE.search(full_text):
        result.member_name = m.group(1).strip()
    if m := _HEADER_DIST_DATE_RE.search(full_text):
        result.distribution_date = _parse_distribution_date(m.group(1))
    if m := _HEADER_PERIOD_RE.search(full_text):
        try:
            sm = _MONTH_NUM[m.group(1)]
            sd, sy = int(m.group(2)), int(m.group(3))
            em = _MONTH_NUM[m.group(4)]
            ed, ey = int(m.group(5)), int(m.group(6))
            result.period_start = date(sy, sm, sd)
            result.period_end = date(ey, em, ed)
        except (KeyError, ValueError):
            pass
    if m := _HEADER_CREDIT_VALUE_RE.search(full_text):
        try:
            result.credit_value = float(m.group(1))
        except ValueError:
            pass

    # Walk lines, tracking:
    #   - current performance category (e.g. "Internet: SPOTIFY")
    #   - section mode: "YOUR" (Jerry's portion) vs "ALLOCATED" (publishers'
    #     shares of Jerry's works). ASCAP statements repeat the same line
    #     items in both sections — once at full value under YOUR, once
    #     per-recipient under ALLOCATED. Pulling rows from both double-
    #     counts. Default YOUR; switch on the page-header markers.
    current_category: str | None = None
    section_mode = "YOUR"
    for line in full_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("YOUR ROYALTIES"):
            section_mode = "YOUR"
            continue
        if stripped.startswith("ALLOCATED ROYALTIES"):
            section_mode = "ALLOCATED"
            continue

        # Update the current category on header lines.
        cat = _detect_category(line)
        if cat is not None:
            current_category = cat
            if cat not in result.categories_seen:
                result.categories_seen.append(cat)
            continue

        # Skip allocated-section rows entirely — they aren't Jerry's money.
        if section_mode != "YOUR":
            continue

        # Skip non-data lines.
        if any(p.match(line) for p in _SKIP_PATTERNS):
            continue

        # Try matching a data row. Most tables have Premium + Total credit
        # columns; "Additional Categories" has only Total. Try two-credit
        # form first (more specific), fall back to one-credit.
        m = _ROW_RE.match(stripped)
        if m is None:
            m = _ROW_RE_ONE_CREDIT.match(stripped)
            if m is None:
                continue
            has_premium = False
        else:
            has_premium = True

        try:
            amount = _parse_amount(m.group("amount"))
            premium_credits = (
                float(m.group("premium").replace(",", "")) if has_premium else 0.0
            )
            total_credits = float(m.group("total_credits").replace(",", ""))
            work_id = m.group("work_id")
            # Title cleanup: collapse whitespace; for TV rows the blob
            # may include series text — accepted for now (rule code
            # uses title matching, not exact equality).
            title = " ".join(m.group("title_blob").split())
            # Plays count is in the `rest` middle text, always followed
            # by a 1-3 letter "Perf. Type" code (F, FB, BG, M, P, FD,
            # NF, etc.). Row shapes seen:
            #   TV:        ... C P 2 F 00:03:44 ...
            #   Internet:  ... C 5 F ...
            #   Satellite: ... C 244 FB SIRIRS ...
            #   Radio:     ... C 11,670 FD Radio - Country ...
            # Radio rows can carry comma-separated play counts ("11,670")
            # and a trailing "Music User Genre" string ("Radio - Country").
            # The reliable anchor is `<plays_with_optional_commas> <1-3
            # uppercase letters>` — take the LAST such match in `rest`.
            rest = m.group("rest")
            plays_matches = re.findall(
                r"\b(\d{1,3}(?:,\d{3})*|\d+)\s+([A-Z]{1,3})\b", rest
            )
            if plays_matches:
                plays = int(plays_matches[-1][0].replace(",", ""))
            else:
                plays = 1
        except (ValueError, IndexError):
            result.skipped_lines += 1
            continue

        result.rows.append(
            {
                "line_no": m.group("line_no"),
                "title": title,
                "work_id": work_id,
                "category": current_category or "Uncategorized",
                "plays": plays,
                "premium_credits": premium_credits,
                "total_credits": total_credits,
                "royalty_amt": amount,
            }
        )

    return result


def ascap_pdf_to_events_and_payments(
    pdf_bytes: bytes, artist_id: str
) -> tuple[list[dict], list[dict], list[str]]:
    """Convert an ASCAP PDF's bytes into Event + Payment dicts ready for
    `_save_events` / `_save_payments`.

    Returns ``(events, payments, errors)``. Empty events+payments with
    a non-empty errors list signals "we tried but found nothing usable."
    """
    errors: list[str] = []
    try:
        result = parse_ascap_pdf_bytes(pdf_bytes)
    except Exception as exc:  # noqa: BLE001
        return [], [], [f"ASCAP PDF parse failed: {exc}"]

    if not result.rows:
        errors.append("No data rows extracted from ASCAP PDF")
        return [], [], errors

    events: list[dict] = []
    payments: list[dict] = []
    distribution_dt = (
        datetime.combine(result.distribution_date, datetime.min.time(), tzinfo=timezone.utc)
        if result.distribution_date
        else datetime.now(timezone.utc)
    )
    # Bucket events by the performance period midpoint when available.
    # Without it (e.g. summary-only statements), fall back to the
    # distribution timestamp so timeline math still works.
    period_mid_dt = distribution_dt
    if result.period_start and result.period_end:
        midpoint = result.period_start + (result.period_end - result.period_start) / 2
        period_mid_dt = datetime.combine(
            midpoint, datetime.min.time(), tzinfo=timezone.utc
        )

    for r in result.rows:
        plays = max(int(r["plays"]), 0)
        royalty = float(r["royalty_amt"])
        unit_value = round(royalty / plays, 8) if plays > 0 else 0.0
        platform = f"ASCAP / {r['category']}"

        events.append(
            {
                "event_type": "STREAM",
                "artist_id": artist_id,
                "platform": platform,
                "territory": "US",
                "timestamp": period_mid_dt,
                "quantity": plays,
                "unit_value": unit_value,
                "currency": "USD",
                "work_title": r["title"],
            }
        )
        # Stable reference: artist + work + period + category + line. Lets
        # re-upload of the same statement dedup cleanly. Including line_no
        # disambiguates cases where the same work appears multiple times
        # in the same category (different networks / DSP variants).
        period_key = (
            result.period_start.isoformat() if result.period_start else "unknown"
        )
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
                    f"ascap-pdf:{r['work_id']}:{period_key}:"
                    f"{r['category']}:{r['line_no']}"
                ),
                "payer_account_id": result.member_id,
                "payer_ip_number": result.ipi_number,
                "payer_work_id": r["work_id"],
            }
        )

    return events, payments, errors


__all__ = (
    "AscapPdfParseResult",
    "ascap_pdf_to_events_and_payments",
    "is_ascap_international_pdf",
    "is_ascap_pdf",
    "parse_ascap_pdf_bytes",
)


def _all() -> Iterable[str]:
    return __all__
