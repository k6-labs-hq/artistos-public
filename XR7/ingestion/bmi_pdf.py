"""Parser for BMI's "Royalty Statement" PDF format.

These are the print-friendly statements an affiliate can download from
BMI Online Services. The 28-column CSV export from the same portal is
the higher-quality input (parsed by `_parse_bmi_real` in
``statement_parser``); this PDF parser is the fallback for affiliates
who only have the PDFs on hand.

Layout summary (verified against statements 2015 Q4 → 2025 Q3 for
account 885077):

    Account No: 000XXXXXXX  IP No: NN.NNNN.NNNN.NN
    U.S. Performance Period: NTH QUARTER YYYY
    Distribution Date: <Month Day, Year>  International: NNN ACCOUNTING

Body sections (one or more per statement):

    U.S. Performances - Commercial Radio
        TITLE  WORK_NO  WH  USE_COUNT  PERIOD  PCT%  $CURR  $HIT_BONUS  $STD_BONUS  $ROYALTY

    U.S. Performances - Internet Audio
        SOURCE_LABEL (e.g. SPOTIFY PREM, PANDORA, APPLE FAMILY)
        TITLE  WORK_NO  WH  USE_COUNT  PERIOD  PCT%  $CURR  $BONUS  $ROYALTY
        ...
        SOURCE_LABEL Total  $X.XX

    U.S. Performances - Other Sources
        (mixed shapes — variable additional column "Source")

    International Performances - Audio / Audiovisual
        Per-society blocks, similar shape to Internet Audio

We extract one Payment per data row plus one synthetic STREAM Event
keyed off USE_COUNT so downstream rate analysis has something to chew
on.

Output shape mirrors what `_parse_bmi_real` produces so the same
downstream rules + payer_office routing work.
"""

from __future__ import annotations

import io
import logging
import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Iterable

logger = logging.getLogger(__name__)


# Header field regexes — robust to whitespace variation and the
# "Account No:" / "IP No:" being on the same line.
_HEADER_ACCOUNT_RE = re.compile(r"Account No:\s*(\d{6,})")
_HEADER_IP_RE = re.compile(r"IP No:\s*([\d.]+)")
_HEADER_PERIOD_RE = re.compile(
    r"U\.S\.\s*Performance\s*Period:\s*(\d+)(?:ST|ND|RD|TH)\s*QUARTER\s*(\d{4})",
    re.IGNORECASE,
)
_HEADER_DIST_DATE_RE = re.compile(r"Distribution Date:\s*([A-Za-z]+\s+\d+,\s*\d{4})")

# Section headers we recognise. Anything else is treated as informational.
_SECTION_HEADERS: tuple[tuple[str, str], ...] = (
    ("U.S. Performances - Commercial Radio", "US_RADIO"),
    ("U.S. Performances - Internet Audio", "US_INTERNET"),
    ("U.S. Performances - Other Sources", "US_OTHER"),
    ("International Performances - Audio", "INTL_AUDIO"),
    ("International Performances - Audiovisual", "INTL_AV"),
)

# A data row's right-edge: percent, then two-to-four currency values.
# Currency values can be `$X.XX`, `$X,XXX.XX`, or `$(X.XX)` for negatives.
_AMOUNT = r"\$\(?[\d,]+\.\d{2}\)?"

# Internet Audio / International / Other Sources: 3 currency values
# (Current Activity, Bonus, Royalty Amt).
_ROW_RE_3AMT = re.compile(
    r"^(?P<title>.+?)\s+"
    r"(?P<work_no>\d{6,9})\s+"
    r"(?P<wh>[A-Z]{1,3})\s+"
    r"(?P<use_count>[\d,]+)\s+"
    r"(?P<period>\d{5})\s+"
    r"(?P<percent>[\d.]+)%\s+"
    r"(?P<curr>" + _AMOUNT + r")\s+"
    r"(?P<bonus>" + _AMOUNT + r")\s+"
    r"(?P<royalty>" + _AMOUNT + r")$"
)

# Commercial Radio: 4 currency values (Current Activity, Hit Song
# Bonus, Standards Bonus, Royalty Amt).
_ROW_RE_4AMT = re.compile(
    r"^(?P<title>.+?)\s+"
    r"(?P<work_no>\d{6,9})\s+"
    r"(?P<wh>[A-Z]{1,3})\s+"
    r"(?P<use_count>[\d,]+)\s+"
    r"(?P<period>\d{5})\s+"
    r"(?P<percent>[\d.]+)%\s+"
    r"(?P<curr>" + _AMOUNT + r")\s+"
    r"(?P<hit>" + _AMOUNT + r")\s+"
    r"(?P<std>" + _AMOUNT + r")\s+"
    r"(?P<royalty>" + _AMOUNT + r")$"
)

# Source sub-header (e.g. "SPOTIFY PREM", "PANDORA", "AMAZON UNLTD",
# "GROOVE MUSIC", "AMZ UNLTD FREE"). Uppercase letters / digits /
# spaces / & / -. NOT followed by digits (that'd be a data row's title).
# Excludes section totals like "AMAZON UNLTD Total $7.85".
_SOURCE_HEADER_RE = re.compile(r"^(?P<source>[A-Z0-9][A-Z0-9 &\-/]+?)$")

# Lines we always skip — totals, footers, page headers, informational.
_SKIP_PATTERNS = (
    re.compile(r"^.+\s+Total\s+\$.*"),  # "AMAZON UNLTD Total $7.85"
    re.compile(r"^U\.S\. Performance.*Total\s+\$.*"),  # "Internet Audio Grand Total..."
    re.compile(r"^International Performances.*Total"),
    re.compile(r"^Royalty Statement Page \d+"),
    re.compile(r"^Affiliate:\s+", re.IGNORECASE),
    re.compile(r"^Account No:", re.IGNORECASE),
    re.compile(r"^Distribution Date:", re.IGNORECASE),
    re.compile(r"^U\.S\. Performance Period:", re.IGNORECASE),
    re.compile(r"^(New York|Los Angeles|Atlanta|Nashville|London|Austin|Miami)\s"),
    re.compile(r"Writer/Publisher Relations|Creative Office", re.IGNORECASE),
    re.compile(r"^[\d,.\s]+$"),  # all-numeric noise
    re.compile(r"^Source\s*$", re.IGNORECASE),
    re.compile(r"^Title\s+Work", re.IGNORECASE),  # column header continuation
    re.compile(r"^\s*$"),
)


@dataclass
class BmiPdfParseResult:
    account_no: str | None = None
    ip_no: str | None = None
    period_quarter: int | None = None  # 1-4
    period_year: int | None = None
    distribution_date: date | None = None
    rows: list[dict] = field(default_factory=list)
    skipped_lines: int = 0
    sections_seen: list[str] = field(default_factory=list)


def _parse_amount(s: str) -> float:
    """Parse `$1,234.56` / `$(0.12)` / `$0.00` → float (negative for parens)."""
    s = s.replace("$", "").replace(",", "").strip()
    if s.startswith("(") and s.endswith(")"):
        return -float(s[1:-1])
    return float(s)


def _decode_period(period_5: str) -> tuple[date, date] | tuple[None, None]:
    """``20162`` → (2016-04-01, 2016-06-30). Same encoding as bmi_real CSV."""
    if len(period_5) != 5 or not period_5.isdigit():
        return None, None
    year, q = int(period_5[:4]), int(period_5[4])
    if not 1 <= q <= 4:
        return None, None
    start_month = (q - 1) * 3 + 1
    end_month = start_month + 2
    last_day = (date(year, end_month + 1, 1) if end_month < 12 else date(year + 1, 1, 1))
    last_day = (
        last_day.replace(day=last_day.day - 1) if last_day.day > 1 else last_day  # noqa: PLR2004
    )
    # Simpler last-day calc:
    import calendar  # noqa: PLC0415

    return date(year, start_month, 1), date(year, end_month, calendar.monthrange(year, end_month)[1])


def _parse_distribution_date(s: str) -> date | None:
    try:
        return datetime.strptime(s.strip(), "%B %d, %Y").date()
    except ValueError:
        return None


def _is_skip_line(line: str) -> bool:
    return any(p.match(line) for p in _SKIP_PATTERNS)


def _detect_section(line: str) -> str | None:
    for header_text, key in _SECTION_HEADERS:
        if header_text in line:
            return key
    return None


def parse_bmi_pdf_bytes(pdf_bytes: bytes) -> BmiPdfParseResult:
    """Parse BMI Royalty Statement PDF bytes into structured rows."""
    # Defer pdfplumber import so the module load doesn't pay the cost
    # for non-PDF parses.
    import pdfplumber  # noqa: PLC0415

    result = BmiPdfParseResult()
    full_text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            full_text_parts.append(page.extract_text() or "")
    text = "\n".join(full_text_parts)

    if m := _HEADER_ACCOUNT_RE.search(text):
        result.account_no = m.group(1)
    if m := _HEADER_IP_RE.search(text):
        result.ip_no = m.group(1)
    if m := _HEADER_PERIOD_RE.search(text):
        result.period_quarter = int(m.group(1))
        result.period_year = int(m.group(2))
    if m := _HEADER_DIST_DATE_RE.search(text):
        result.distribution_date = _parse_distribution_date(m.group(1))

    current_section: str | None = None
    current_source: str | None = None  # for Internet Audio / International (sub-headers)

    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        # Section detection — switches state, doesn't consume a row.
        new_section = _detect_section(line)
        if new_section is not None:
            current_section = new_section
            current_source = None
            if new_section not in result.sections_seen:
                result.sections_seen.append(new_section)
            continue

        # Skip noise.
        if _is_skip_line(line):
            result.skipped_lines += 1
            continue

        # Try to match as a data row. Commercial Radio uses 4-amount form;
        # Internet/Intl/Other use 3-amount. Try the wider match first
        # (4-amount) so a 3-amount line doesn't accidentally consume a
        # 4-amount line's currency as the title.
        match4 = _ROW_RE_4AMT.match(line)
        match3 = _ROW_RE_3AMT.match(line) if match4 is None else None

        if match4:
            period_start, period_end = _decode_period(match4.group("period"))
            result.rows.append(
                {
                    "section": current_section or "UNKNOWN",
                    "source": current_source or current_section or "UNKNOWN",
                    "title": match4.group("title").strip(),
                    "work_no": match4.group("work_no"),
                    "wh": match4.group("wh"),
                    "use_count": int(match4.group("use_count").replace(",", "")),
                    "period": match4.group("period"),
                    "period_start": period_start,
                    "period_end": period_end,
                    "percent": float(match4.group("percent")),
                    "current_activity": _parse_amount(match4.group("curr")),
                    "hit_song_bonus": _parse_amount(match4.group("hit")),
                    "standards_bonus": _parse_amount(match4.group("std")),
                    "bonus": 0.0,
                    "royalty_amt": _parse_amount(match4.group("royalty")),
                }
            )
        elif match3:
            period_start, period_end = _decode_period(match3.group("period"))
            result.rows.append(
                {
                    "section": current_section or "UNKNOWN",
                    "source": current_source or current_section or "UNKNOWN",
                    "title": match3.group("title").strip(),
                    "work_no": match3.group("work_no"),
                    "wh": match3.group("wh"),
                    "use_count": int(match3.group("use_count").replace(",", "")),
                    "period": match3.group("period"),
                    "period_start": period_start,
                    "period_end": period_end,
                    "percent": float(match3.group("percent")),
                    "current_activity": _parse_amount(match3.group("curr")),
                    "hit_song_bonus": 0.0,
                    "standards_bonus": 0.0,
                    "bonus": _parse_amount(match3.group("bonus")),
                    "royalty_amt": _parse_amount(match3.group("royalty")),
                }
            )
        else:
            # Source sub-header (e.g. "SPOTIFY PREM"). Store and continue.
            sm = _SOURCE_HEADER_RE.match(line)
            if (
                sm
                and current_section in {"US_INTERNET", "US_OTHER", "INTL_AUDIO", "INTL_AV"}
                and not any(c.islower() for c in line)
                and len(line.split()) <= 5
                and not any(ch.isdigit() for ch in line)
            ):
                current_source = sm.group("source").strip()
            else:
                result.skipped_lines += 1

    return result


def is_bmi_pdf(pdf_bytes: bytes) -> bool:
    """Heuristic: does this look like a BMI Royalty Statement PDF?

    Used by the dispatcher to route .pdf uploads to this parser. Cheap
    text extraction on the first page checking for the BMI cover-page
    layout: a `ROYALTY STATEMENT` header plus a member account marker
    (`ACCT NO:` / `ACCOUNT NO:`). The Tolliver corpus uses the
    abbreviated `ACCT NO:` form, so we accept either.
    """
    try:
        import pdfplumber  # noqa: PLC0415

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            if not pdf.pages:
                return False
            head = (pdf.pages[0].extract_text() or "")[:1500].upper()
        has_account = "ACCT NO:" in head or "ACCOUNT NO:" in head
        has_marker = "BMI" in head or "ROYALTY STATEMENT" in head
        return has_account and has_marker
    except Exception:  # noqa: BLE001
        return False


def bmi_pdf_to_events_and_payments(
    pdf_bytes: bytes, artist_id: str
) -> tuple[list[dict], list[dict], list[str]]:
    """Convert a BMI PDF's bytes into Event + Payment dicts ready for
    `_save_events` / `_save_payments`.

    Returns ``(events, payments, errors)``. Empty events+payments with
    a non-empty errors list signals "we tried but found nothing usable."
    """
    errors: list[str] = []
    try:
        result = parse_bmi_pdf_bytes(pdf_bytes)
    except Exception as exc:  # noqa: BLE001
        return [], [], [f"BMI PDF parse failed: {exc}"]

    if not result.rows:
        errors.append("No data rows extracted from BMI PDF")
        return [], [], errors

    events: list[dict] = []
    payments: list[dict] = []
    distribution_dt = (
        datetime.combine(result.distribution_date, datetime.min.time(), tzinfo=timezone.utc)
        if result.distribution_date
        else datetime.now(timezone.utc)
    )

    for r in result.rows:
        # Event = one synthetic STREAM event per data row keyed off use_count.
        events.append(
            {
                "event_type": "STREAM",
                "artist_id": artist_id,
                "platform": f"BMI / {r['source']}",
                "territory": "US" if (r["section"] or "").startswith("US_") else "INT",
                "timestamp": distribution_dt,
                "quantity": r["use_count"],
                "unit_value": (
                    round(r["royalty_amt"] / r["use_count"], 6) if r["use_count"] > 0 else 0.0
                ),
                "currency": "USD",
                "work_title": r["title"],
            }
        )
        # Payment = one ROYALTY payment per data row.
        payments.append(
            {
                "payment_type": "ROYALTY",
                "artist_id": artist_id,
                "amount": round(r["royalty_amt"], 6),
                "currency": "USD",
                "source": f"BMI / {r['source']}",
                "period_start": r["period_start"],
                "period_end": r["period_end"],
                "received_at": distribution_dt,
                # Stable per-row reference: artist + work + period + source.
                # Prevents dup-on-reupload of the same PDF.
                "reference_id": f"bmi-pdf:{r['work_no']}:{r['period']}:{r['source']}",
                "payer_account_id": result.account_no,
                "payer_ip_number": result.ip_no,
                "payer_work_id": r["work_no"],
            }
        )

    return events, payments, errors


__all__ = (
    "BmiPdfParseResult",
    "bmi_pdf_to_events_and_payments",
    "is_bmi_pdf",
    "parse_bmi_pdf_bytes",
)


# Re-export for convenience from any caller importing this module
def _all() -> Iterable[str]:
    return __all__
