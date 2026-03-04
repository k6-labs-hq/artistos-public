"""
Royalty Statement CSV Parser for ARCOS7 Engine 2.

Artists download royalty statements from distributors and PROs as CSV files
and upload them via ``POST /artists/{id}/statements/upload``.  This module
detects the statement format from the column headers and normalises every row
into a (events, payments) pair ready for database insertion.

Supported formats
-----------------
- **DistroKid** — ``Month``, ``Store``, ``Country``, ``Title``, ``ISRC``,
  ``Quantity``, ``Earnings`` (and variants)
- **TuneCore** — ``Sale Month``, ``Store``, ``Country``, ``Title``, ``ISRC``,
  ``Quantity``, ``Net Revenue``
- **CD Baby** — ``Store``, ``Country``, ``Sale Date``, ``Title``, ``ISRC``,
  ``Quantity``, ``Total Earnings``
- **ASCAP** — ``Work Title``, ``ISWC``, ``Performance Date``, ``Source``,
  ``Royalty``
- **BMI** — ``Title``, ``ISWC``, ``Date``, ``Payer``, ``Revenue``
- **Spotify for Artists** — ``Date``, ``Country``, ``Track Name``, ``ISRC``,
  ``Streams``, ``Stream Revenue``
- **Generic** — Any CSV with recognisable date, source/platform, quantity,
  and amount columns (fallback).

Output format
-------------
Each normalised *event* dict maps to the :class:`~arcos7.models.event.Event`
ORM model::

    {
        "event_type": "STREAM",          # EventType enum value
        "artist_id":  "<uuid>",
        "platform":   "Spotify",
        "territory":  "US",
        "timestamp":  datetime(...),
        "quantity":   12345,
        "unit_value": 0.00415,           # royalty per unit
        "currency":   "USD",
        "work_title": "Song Name",       # not stored in Event; used for Work matching
        "isrc":       "USRC17607839",    # not stored in Event; used for Work matching
    }

Each normalised *payment* dict maps to :class:`~arcos7.models.payment.Payment`::

    {
        "payment_type": "ROYALTY",
        "artist_id":    "<uuid>",
        "amount":       42.17,
        "currency":     "USD",
        "source":       "DistroKid / Spotify",
        "period_start": date(2023, 1, 1),
        "period_end":   date(2023, 1, 31),
        "reference_id": "<row_hash>",
    }
"""

from __future__ import annotations

import csv
import hashlib
import io
import logging
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------

_FORMATS = {
    "distrokid": {
        "required": {"month", "store", "title", "quantity", "earnings"},
        "aliases": {"earnings": "earnings", "isrc": "isrc", "country": "country"},
    },
    "tunecore": {
        "required": {"sale month", "store", "title", "quantity", "net revenue"},
        "aliases": {"net revenue": "amount", "isrc": "isrc", "country": "country"},
    },
    "cdbaby": {
        "required": {"store", "title", "quantity", "total earnings"},
        "aliases": {"total earnings": "amount", "sale date": "date", "isrc": "isrc"},
    },
    "ascap": {
        "required": {"work title", "performance date", "royalty"},
        "aliases": {"work title": "title", "performance date": "date", "royalty": "amount"},
    },
    "bmi": {
        "required": {"title", "date", "payer", "revenue"},
        "aliases": {"revenue": "amount", "payer": "source"},
    },
    "spotify": {
        "required": {"track name", "streams", "stream revenue"},
        "aliases": {"track name": "title", "stream revenue": "amount", "streams": "quantity"},
    },
}

# Columns that indicate the generic fallback
_GENERIC_DATE_COLS = {
    "date", "timestamp", "period", "month", "sale date", "sale month",
    "performance date", "report date",
}
_GENERIC_AMOUNT_COLS = {
    "amount", "royalty", "revenue", "earnings", "net revenue",
    "total earnings", "stream revenue", "net",
}
_GENERIC_QUANTITY_COLS = {
    "quantity", "streams", "plays", "units", "impressions", "views",
}
_GENERIC_SOURCE_COLS = {
    "source", "platform", "store", "distributor", "payer", "channel",
}
_GENERIC_TERRITORY_COLS = {
    "country", "territory", "region",
}


def _normalise_header(h: str) -> str:
    return h.strip().lower().replace("_", " ").replace("-", " ")


def detect_format(headers: list[str]) -> str:
    """
    Return the statement format name based on the CSV column headers.

    Returns one of ``"distrokid"``, ``"tunecore"``, ``"cdbaby"``,
    ``"ascap"``, ``"bmi"``, ``"spotify"``, or ``"generic"``.
    """
    normalised = {_normalise_header(h) for h in headers}
    for fmt_name, spec in _FORMATS.items():
        required = spec["required"]
        if required.issubset(normalised):
            return fmt_name
    return "generic"


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

_DATE_FMTS = [
    "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d",
    "%B %Y", "%b %Y", "%m-%Y", "%Y-%m",
    "%m/%Y", "%d-%b-%Y", "%b-%Y",
]


def _parse_date(value: str) -> datetime | None:
    """Try several common date formats and return a UTC datetime or None."""
    value = value.strip()
    for fmt in _DATE_FMTS:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _month_end(dt: datetime) -> date:
    """Return the last day of the month for a given datetime."""
    import calendar
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    return date(dt.year, dt.month, last_day)


# ---------------------------------------------------------------------------
# Currency / amount helpers
# ---------------------------------------------------------------------------

def _parse_amount(value: str) -> float | None:
    """Strip currency symbols and parse a float, returning None on failure."""
    cleaned = value.strip().replace("$", "").replace("€", "").replace("£", "").replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_int(value: str) -> int:
    """Parse an integer quantity, returning 0 on failure."""
    try:
        return max(0, int(str(value).strip().replace(",", "")))
    except (ValueError, TypeError):
        return 0


def _row_hash(row: dict, fmt: str) -> str:
    """Stable SHA-256 hash of a row dict for de-duplication."""
    key = f"{fmt}|" + "|".join(f"{k}={v}" for k, v in sorted(row.items()))
    return hashlib.sha256(key.encode()).hexdigest()[:24]


# ---------------------------------------------------------------------------
# Parse result
# ---------------------------------------------------------------------------

@dataclass
class ParseResult:
    """Result of parsing a statement CSV."""

    format_detected: str
    row_count: int
    events: list[dict] = field(default_factory=list)
    payments: list[dict] = field(default_factory=list)
    skipped_rows: int = 0
    errors: list[str] = field(default_factory=list)

    def to_summary(self) -> dict:
        return {
            "format_detected": self.format_detected,
            "row_count": self.row_count,
            "events_parsed": len(self.events),
            "payments_parsed": len(self.payments),
            "skipped_rows": self.skipped_rows,
            "errors": self.errors[:10],  # cap to first 10 for API response
        }


# ---------------------------------------------------------------------------
# Format-specific parsers
# ---------------------------------------------------------------------------

def _col(row: dict[str, str], *names: str) -> str:
    """Return the first non-empty value from a list of possible column names."""
    lrow = {k.strip().lower(): v for k, v in row.items()}
    for name in names:
        val = lrow.get(name.lower(), "").strip()
        if val:
            return val
    return ""


def _parse_distrokid(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "month", "sale month", "date")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "quantity"))
    amount_str = _col(row, "earnings", "net", "amount")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    store = _col(row, "store", "platform", "source") or "DistroKid"
    country = _col(row, "country", "territory") or "US"
    title = _col(row, "title", "track name", "song")
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"

    unit_value = (amount / quantity) if quantity > 0 else 0.0

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": store,
        "territory": country.upper()[:2] if country else None,
        "timestamp": dt,
        "quantity": quantity,
        "unit_value": round(unit_value, 8),
        "currency": currency,
        "work_title": title,
        "isrc": isrc,
    }
    payment = {
        "payment_type": "ROYALTY",
        "artist_id": artist_id,
        "amount": round(amount, 6),
        "currency": currency,
        "source": f"DistroKid / {store}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "distrokid"),
    }
    return event, payment


def _parse_tunecore(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "sale month", "month", "date")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "quantity"))
    amount_str = _col(row, "net revenue", "amount", "earnings")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    store = _col(row, "store", "platform") or "TuneCore"
    country = _col(row, "country", "territory") or "US"
    title = _col(row, "title", "track name", "song")
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"

    unit_value = (amount / quantity) if quantity > 0 else 0.0

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": store,
        "territory": country.upper()[:2] if country else None,
        "timestamp": dt,
        "quantity": quantity,
        "unit_value": round(unit_value, 8),
        "currency": currency,
        "work_title": title,
        "isrc": isrc,
    }
    payment = {
        "payment_type": "ROYALTY",
        "artist_id": artist_id,
        "amount": round(amount, 6),
        "currency": currency,
        "source": f"TuneCore / {store}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "tunecore"),
    }
    return event, payment


def _parse_cdbaby(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "sale date", "date", "month")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "quantity"))
    amount_str = _col(row, "total earnings", "royalty", "amount")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    store = _col(row, "store", "platform") or "CD Baby"
    country = _col(row, "country", "territory") or "US"
    title = _col(row, "title", "track name", "song")
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"

    unit_value = (amount / quantity) if quantity > 0 else 0.0

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": store,
        "territory": country.upper()[:2] if country else None,
        "timestamp": dt,
        "quantity": quantity,
        "unit_value": round(unit_value, 8),
        "currency": currency,
        "work_title": title,
        "isrc": isrc,
    }
    payment = {
        "payment_type": "ROYALTY",
        "artist_id": artist_id,
        "amount": round(amount, 6),
        "currency": currency,
        "source": f"CD Baby / {store}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "cdbaby"),
    }
    return event, payment


def _parse_ascap(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "performance date", "date")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    amount_str = _col(row, "royalty", "amount", "revenue")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    source = _col(row, "source", "usage type", "platform") or "ASCAP"
    title = _col(row, "work title", "title", "song")
    currency = _col(row, "currency") or "USD"

    # ASCAP records are per-performance; quantity = 1 performance
    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": f"ASCAP / {source}",
        "territory": "US",
        "timestamp": dt,
        "quantity": 1,
        "unit_value": round(amount, 6),
        "currency": currency,
        "work_title": title,
        "isrc": _col(row, "isrc"),
    }
    payment = {
        "payment_type": "ROYALTY",
        "artist_id": artist_id,
        "amount": round(amount, 6),
        "currency": currency,
        "source": f"ASCAP / {source}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "ascap"),
    }
    return event, payment


def _parse_bmi(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "date", "period", "month")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    amount_str = _col(row, "revenue", "amount", "royalty")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    source = _col(row, "payer", "source", "platform") or "BMI"
    title = _col(row, "title", "work title", "song")
    currency = _col(row, "currency") or "USD"

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": f"BMI / {source}",
        "territory": "US",
        "timestamp": dt,
        "quantity": 1,
        "unit_value": round(amount, 6),
        "currency": currency,
        "work_title": title,
        "isrc": _col(row, "isrc"),
    }
    payment = {
        "payment_type": "ROYALTY",
        "artist_id": artist_id,
        "amount": round(amount, 6),
        "currency": currency,
        "source": f"BMI / {source}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "bmi"),
    }
    return event, payment


def _parse_spotify(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "date", "month")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "streams", "plays", "quantity"))
    amount_str = _col(row, "stream revenue", "amount", "revenue")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    country = _col(row, "country", "territory") or "US"
    title = _col(row, "track name", "title", "song")
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"

    unit_value = (amount / quantity) if quantity > 0 else 0.0

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": "Spotify",
        "territory": country.upper()[:2] if country else None,
        "timestamp": dt,
        "quantity": quantity,
        "unit_value": round(unit_value, 8),
        "currency": currency,
        "work_title": title,
        "isrc": isrc,
    }
    payment = {
        "payment_type": "ROYALTY",
        "artist_id": artist_id,
        "amount": round(amount, 6),
        "currency": currency,
        "source": "Spotify",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "spotify"),
    }
    return event, payment


def _parse_generic(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    lrow = {_normalise_header(k): v.strip() for k, v in row.items()}

    # Find date column
    raw_date = ""
    for col in _GENERIC_DATE_COLS:
        raw_date = lrow.get(col, "")
        if raw_date:
            break
    dt = _parse_date(raw_date) if raw_date else datetime.now(timezone.utc)
    if dt is None:
        dt = datetime.now(timezone.utc)

    # Find amount column
    amount_str = ""
    for col in _GENERIC_AMOUNT_COLS:
        amount_str = lrow.get(col, "")
        if amount_str:
            break
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    # Find quantity column
    quantity_str = ""
    for col in _GENERIC_QUANTITY_COLS:
        quantity_str = lrow.get(col, "")
        if quantity_str:
            break
    quantity = _parse_int(quantity_str) if quantity_str else 1

    # Find source/platform
    source = ""
    for col in _GENERIC_SOURCE_COLS:
        source = lrow.get(col, "")
        if source:
            break
    source = source or "Unknown"

    # Find territory
    territory = ""
    for col in _GENERIC_TERRITORY_COLS:
        territory = lrow.get(col, "")
        if territory:
            break

    title = lrow.get("title", lrow.get("track name", lrow.get("song", lrow.get("work title", ""))))
    isrc = lrow.get("isrc", "")
    currency = lrow.get("currency", "USD")

    unit_value = (amount / quantity) if quantity > 0 else 0.0

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": source,
        "territory": territory.upper()[:2] if territory else None,
        "timestamp": dt,
        "quantity": quantity,
        "unit_value": round(unit_value, 8),
        "currency": currency,
        "work_title": title,
        "isrc": isrc,
    }
    payment = {
        "payment_type": "ROYALTY",
        "artist_id": artist_id,
        "amount": round(amount, 6),
        "currency": currency,
        "source": source,
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "generic"),
    }
    return event, payment


_FORMAT_PARSERS = {
    "distrokid": _parse_distrokid,
    "tunecore": _parse_tunecore,
    "cdbaby": _parse_cdbaby,
    "ascap": _parse_ascap,
    "bmi": _parse_bmi,
    "spotify": _parse_spotify,
    "generic": _parse_generic,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_csv(content: bytes, artist_id: str, encoding: str = "utf-8-sig") -> ParseResult:
    """
    Parse a royalty statement CSV file and return normalised events and payments.

    Parameters
    ----------
    content:
        Raw bytes of the uploaded CSV file.
    artist_id:
        The artist's UUID — injected into every parsed row.
    encoding:
        File encoding.  ``"utf-8-sig"`` strips the byte-order mark that
        Microsoft Excel adds to CSV exports.

    Returns
    -------
    :class:`ParseResult` with ``events``, ``payments``, and a summary.
    """
    try:
        text = content.decode(encoding)
    except UnicodeDecodeError:
        # Fallback to latin-1 which accepts any byte value
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        return ParseResult(
            format_detected="unknown",
            row_count=0,
            errors=["CSV file has no header row or is empty."],
        )

    headers = list(reader.fieldnames)
    fmt = detect_format(headers)
    parser = _FORMAT_PARSERS[fmt]

    events: list[dict] = []
    payments: list[dict] = []
    skipped = 0
    errors: list[str] = []
    rows = list(reader)

    for i, row in enumerate(rows, start=2):
        try:
            event, payment = parser(row, artist_id)
        except Exception as exc:  # noqa: BLE001
            skipped += 1
            errors.append(f"Row {i}: {exc}")
            continue

        if event is None or payment is None:
            skipped += 1
            continue

        # Skip rows with zero amounts — these are informational totals
        if payment["amount"] == 0.0 and event["quantity"] == 0:
            skipped += 1
            continue

        events.append(event)
        payments.append(payment)

    if not events and not errors and rows:
        errors.append(
            f"No parseable rows found for format '{fmt}'.  "
            "Ensure the file has the expected column headers.  "
            "See the API documentation for supported formats."
        )

    return ParseResult(
        format_detected=fmt,
        row_count=len(rows),
        events=events,
        payments=payments,
        skipped_rows=skipped,
        errors=errors,
    )
