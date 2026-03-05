"""
Royalty Statement CSV Parser for ARCOS7 Engine 2.

Artists download royalty statements from distributors and PROs as CSV files
and upload them via ``POST /artists/{id}/statements/upload``.  This module
detects the statement format from the column headers and normalises every row
into a (events, payments) pair ready for database insertion.

Supported formats
-----------------
Major distributors (dedicated parsers):

- **DistroKid** — ``Month``, ``Store``, ``Country``, ``Title``, ``ISRC``,
  ``Quantity``, ``Earnings`` (and variants)
- **TuneCore** — ``Sale Month``, ``Store``, ``Country``, ``Title``, ``ISRC``,
  ``Quantity``, ``Net Revenue``
- **CD Baby** — ``Store``, ``Country``, ``Sale Date``, ``Title``, ``ISRC``,
  ``Quantity``, ``Total Earnings``
- **Amuse** — ``Reporting Period``, ``Platform``, ``Country``, ``Track Title``,
  ``ISRC``, ``Streams``, ``Revenue``
- **United Masters** — ``Period``, ``Store``, ``Country/Region``, ``Track``,
  ``ISRC``, ``Units``, ``Total Revenue``
- **ONErpm** — ``Sale Date``, ``Retailer``, ``Country``, ``Track Title``,
  ``ISRC``, ``Qty``, ``Net Amount``
- **Stem** — ``Period``, ``Platform``, ``Country Code``, ``Track Name``,
  ``ISRC``, ``Streams``, ``Net Revenue``
- **LANDR** — ``Month``, ``Store``, ``Territory``, ``Track Name``, ``ISRC``,
  ``Net Quantity``, ``Net Revenue``
- **Ditto Music** — ``Month``, ``Store``, ``Country``, ``Title``, ``ISRC``,
  ``Streams``, ``Net Revenue``
- **ReverbNation** — ``Date``, ``Platform``, ``Country``, ``Song``, ``ISRC``,
  ``Streams``, ``Revenue``
- **Bandcamp** — ``Date``, ``Item Name``, ``Buyer Name``, ``Country``,
  ``Item Type``, ``Quantity``, ``Revenue``

PROs / platforms (dedicated parsers):

- **ASCAP** — ``Work Title``, ``ISWC``, ``Performance Date``, ``Source``,
  ``Royalty``
- **BMI** — ``Title``, ``ISWC``, ``Date``, ``Payer``, ``Revenue``
- **Spotify for Artists** — ``Date``, ``Country``, ``Track Name``, ``ISRC``,
  ``Streams``, ``Stream Revenue``

Fallback:

- **Generic** — Any CSV with recognisable date, source/platform, quantity,
  and amount columns (fallback for any unlisted distributor).

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
    # -----------------------------------------------------------------------
    # Major distributors
    # -----------------------------------------------------------------------
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
    # Amuse — "Reporting Period" is the unambiguous key column
    "amuse": {
        "required": {"reporting period", "track title", "streams"},
        "aliases": {},
    },
    # United Masters — "Country/Region" is the unambiguous key column
    "unitedmasters": {
        "required": {"country/region", "units", "total revenue"},
        "aliases": {},
    },
    # ONErpm — "Retailer" and "Net Amount" are the unambiguous key columns
    "onerpm": {
        "required": {"retailer", "track title", "net amount"},
        "aliases": {},
    },
    # Stem — "Country Code" (not "Country") is the unambiguous key column
    "stem": {
        "required": {"country code", "streams", "net revenue"},
        "aliases": {},
    },
    # LANDR — "Net Quantity" is the unambiguous key column
    "landr": {
        "required": {"territory", "net quantity", "net revenue"},
        "aliases": {},
    },
    # Ditto Music — "Streams" + "Net Revenue" + "Month" + "Store"
    # (distinct from DistroKid which uses "Earnings", and TuneCore which
    # uses "Sale Month")
    "ditto": {
        "required": {"month", "store", "streams", "net revenue"},
        "aliases": {},
    },
    # ReverbNation — "Song" (not "Title"/"Track Name") is the unambiguous key
    "reverbnation": {
        "required": {"song", "streams", "platform", "revenue"},
        "aliases": {},
    },
    # Bandcamp — "Item Name" and "Buyer Name" are completely unique
    "bandcamp": {
        "required": {"item name", "item type", "buyer name"},
        "aliases": {},
    },
    # -----------------------------------------------------------------------
    # PROs / platforms
    # -----------------------------------------------------------------------
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

# Human-readable descriptions for every explicitly supported format.
# Returned by ``GET /ingestion/supported-formats``.
SUPPORTED_FORMATS: dict[str, dict] = {
    "distrokid": {
        "name": "DistroKid",
        "type": "distributor",
        "key_columns": ["Month", "Store", "Country", "Title", "ISRC", "Quantity", "Earnings"],
        "description": "DistroKid royalty report CSV (download from DistroKid Bank → Reports).",
    },
    "tunecore": {
        "name": "TuneCore",
        "type": "distributor",
        "key_columns": ["Sale Month", "Store", "Country", "Title", "ISRC", "Quantity", "Net Revenue"],
        "description": "TuneCore royalty statement CSV.",
    },
    "cdbaby": {
        "name": "CD Baby",
        "type": "distributor",
        "key_columns": ["Store", "Country", "Sale Date", "Title", "ISRC", "Quantity", "Total Earnings"],
        "description": "CD Baby royalty statement CSV.",
    },
    "amuse": {
        "name": "Amuse",
        "type": "distributor",
        "key_columns": ["Reporting Period", "Platform", "Country", "Track Title", "ISRC", "Streams", "Revenue"],
        "description": "Amuse royalty report CSV.",
    },
    "unitedmasters": {
        "name": "United Masters",
        "type": "distributor",
        "key_columns": ["Period", "Store", "Country/Region", "Track", "ISRC", "Units", "Total Revenue"],
        "description": "United Masters earnings export CSV.",
    },
    "onerpm": {
        "name": "ONErpm",
        "type": "distributor",
        "key_columns": ["Sale Date", "Retailer", "Country", "Track Title", "ISRC", "Qty", "Net Amount"],
        "description": "ONErpm royalty statement CSV.",
    },
    "stem": {
        "name": "Stem",
        "type": "distributor",
        "key_columns": ["Period", "Platform", "Country Code", "Track Name", "ISRC", "Streams", "Net Revenue"],
        "description": "Stem earnings report CSV.",
    },
    "landr": {
        "name": "LANDR",
        "type": "distributor",
        "key_columns": ["Month", "Store", "Territory", "Track Name", "ISRC", "Net Quantity", "Net Revenue"],
        "description": "LANDR (formerly PUSH) royalty statement CSV.",
    },
    "ditto": {
        "name": "Ditto Music",
        "type": "distributor",
        "key_columns": ["Month", "Store", "Country", "Title", "ISRC", "Streams", "Net Revenue"],
        "description": "Ditto Music royalty statement CSV.",
    },
    "reverbnation": {
        "name": "ReverbNation",
        "type": "distributor",
        "key_columns": ["Date", "Platform", "Country", "Song", "ISRC", "Streams", "Revenue"],
        "description": "ReverbNation earnings report CSV.",
    },
    "bandcamp": {
        "name": "Bandcamp",
        "type": "distributor",
        "key_columns": ["Date", "Item Name", "Buyer Name", "Country", "Item Type", "Quantity", "Revenue"],
        "description": "Bandcamp sales CSV (download from Fan Dashboard → Sales).",
    },
    "ascap": {
        "name": "ASCAP",
        "type": "pro",
        "key_columns": ["Work Title", "ISWC", "Performance Date", "Source", "Royalty"],
        "description": "ASCAP royalty statement CSV.",
    },
    "bmi": {
        "name": "BMI",
        "type": "pro",
        "key_columns": ["Title", "ISWC", "Date", "Payer", "Revenue"],
        "description": "BMI royalty statement CSV.",
    },
    "spotify": {
        "name": "Spotify for Artists",
        "type": "dsp",
        "key_columns": ["Date", "Country", "Track Name", "ISRC", "Streams", "Stream Revenue"],
        "description": "Spotify for Artists streaming report CSV.",
    },
    "generic": {
        "name": "Generic / Other",
        "type": "generic",
        "key_columns": ["date/period", "source/store/platform", "quantity/streams", "amount/revenue/earnings"],
        "description": (
            "Automatic fallback for any distributor not listed above.  "
            "Works for any CSV that contains recognisable date, platform, "
            "quantity, and amount columns — including Songtradr, Vydia, "
            "AWAL, Symphonic, INgrooves, Believe, Kobalt, and others."
        ),
    },
}

# Columns that indicate the generic fallback
_GENERIC_DATE_COLS = {
    "date", "timestamp", "period", "month", "sale date", "sale month",
    "performance date", "report date", "reporting period",
}
_GENERIC_AMOUNT_COLS = {
    "amount", "royalty", "revenue", "earnings", "net revenue",
    "total earnings", "stream revenue", "net", "net amount",
    "total revenue", "revenue (usd)", "net revenue (usd)",
}
_GENERIC_QUANTITY_COLS = {
    "quantity", "streams", "plays", "units", "impressions", "views",
    "qty", "net quantity",
}
_GENERIC_SOURCE_COLS = {
    "source", "platform", "store", "distributor", "payer", "channel",
    "retailer",
}
_GENERIC_TERRITORY_COLS = {
    "country", "territory", "region", "country/region", "country code",
}


def _normalise_header(h: str) -> str:
    return h.strip().lower().replace("_", " ").replace("-", " ")


def _calc_unit_value(amount: float, quantity: int) -> float:
    """Return per-unit value, avoiding division by zero."""
    return amount / quantity if quantity > 0 else 0.0


def detect_format(headers: list[str]) -> str:
    """
    Return the statement format name based on the CSV column headers.

    Returns one of ``"distrokid"``, ``"tunecore"``, ``"cdbaby"``,
    ``"amuse"``, ``"unitedmasters"``, ``"onerpm"``, ``"stem"``,
    ``"landr"``, ``"ditto"``, ``"reverbnation"``, ``"bandcamp"``,
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

    unit_value = _calc_unit_value(amount, quantity)

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

    unit_value = _calc_unit_value(amount, quantity)

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

    unit_value = _calc_unit_value(amount, quantity)

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


def _parse_amuse(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "reporting period", "period", "date", "month")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "streams", "plays", "quantity"))
    amount_str = _col(row, "revenue", "revenue (usd)", "net revenue", "amount")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    platform = _col(row, "platform", "store") or "Amuse"
    country = _col(row, "country", "territory") or "US"
    title = _col(row, "track title", "title", "track name", "song")
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"
    unit_value = _calc_unit_value(amount, quantity)

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": platform,
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
        "source": f"Amuse / {platform}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "amuse"),
    }
    return event, payment


def _parse_unitedmasters(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "period", "date", "month")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "units", "streams", "quantity"))
    amount_str = _col(row, "total revenue", "net revenue", "revenue", "amount")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    store = _col(row, "store", "platform", "retailer") or "United Masters"
    country = _col(row, "country/region", "country", "territory") or "US"
    title = _col(row, "track", "track title", "title", "track name", "song")
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"
    unit_value = _calc_unit_value(amount, quantity)

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
        "source": f"United Masters / {store}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "unitedmasters"),
    }
    return event, payment


def _parse_onerpm(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "sale date", "date", "period", "month")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "qty", "quantity", "streams"))
    amount_str = _col(row, "net amount", "amount", "revenue", "net revenue")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    retailer = _col(row, "retailer", "store", "platform") or "ONErpm"
    country = _col(row, "country", "territory") or "US"
    title = _col(row, "track title", "title", "track name", "song")
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"
    unit_value = _calc_unit_value(amount, quantity)

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": retailer,
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
        "source": f"ONErpm / {retailer}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "onerpm"),
    }
    return event, payment


def _parse_stem(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "period", "date", "month")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "streams", "plays", "quantity"))
    amount_str = _col(row, "net revenue", "revenue", "amount")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    platform = _col(row, "platform", "store") or "Stem"
    country = _col(row, "country code", "country", "territory") or "US"
    title = _col(row, "track name", "track title", "title", "song")
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"
    unit_value = _calc_unit_value(amount, quantity)

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": platform,
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
        "source": f"Stem / {platform}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "stem"),
    }
    return event, payment


def _parse_landr(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "month", "period", "date")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "net quantity", "quantity", "streams"))
    amount_str = _col(row, "net revenue", "net revenue (usd)", "revenue", "amount")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    store = _col(row, "store", "platform", "retailer") or "LANDR"
    territory = _col(row, "territory", "country") or "US"
    title = _col(row, "track name", "track title", "title", "song")
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"
    unit_value = _calc_unit_value(amount, quantity)

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": store,
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
        "source": f"LANDR / {store}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "landr"),
    }
    return event, payment


def _parse_ditto(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "month", "period", "date")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "streams", "plays", "quantity"))
    amount_str = _col(row, "net revenue", "revenue", "amount")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    store = _col(row, "store", "platform") or "Ditto Music"
    country = _col(row, "country", "territory") or "US"
    title = _col(row, "title", "track name", "track title", "song")
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"
    unit_value = _calc_unit_value(amount, quantity)

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
        "source": f"Ditto Music / {store}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "ditto"),
    }
    return event, payment


def _parse_reverbnation(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "date", "period", "month")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "streams", "plays", "quantity"))
    amount_str = _col(row, "revenue", "net revenue", "amount")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    platform = _col(row, "platform", "store") or "ReverbNation"
    country = _col(row, "country", "territory") or "US"
    title = _col(row, "song", "title", "track name", "track title")
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"
    unit_value = _calc_unit_value(amount, quantity)

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": platform,
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
        "source": f"ReverbNation / {platform}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "reverbnation"),
    }
    return event, payment


def _parse_bandcamp(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "date", "period", "month")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "quantity", "qty", "units"))
    amount_str = _col(row, "revenue", "net", "amount")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    country = _col(row, "country", "territory") or "US"
    title = _col(row, "item name", "title", "track name", "song")
    item_type = _col(row, "item type", "type") or "track"
    currency = _col(row, "currency") or "USD"
    unit_value = _calc_unit_value(amount, quantity)

    event = {
        "event_type": "SALE",
        "artist_id": artist_id,
        "platform": "Bandcamp",
        "territory": country.upper()[:2] if country else None,
        "timestamp": dt,
        "quantity": quantity,
        "unit_value": round(unit_value, 8),
        "currency": currency,
        "work_title": title,
        "isrc": _col(row, "isrc"),
    }
    payment = {
        "payment_type": "ROYALTY",
        "artist_id": artist_id,
        "amount": round(amount, 6),
        "currency": currency,
        "source": f"Bandcamp / {item_type}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "bandcamp"),
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

    unit_value = _calc_unit_value(amount, quantity)

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

    unit_value = _calc_unit_value(amount, quantity)

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
    "amuse": _parse_amuse,
    "unitedmasters": _parse_unitedmasters,
    "onerpm": _parse_onerpm,
    "stem": _parse_stem,
    "landr": _parse_landr,
    "ditto": _parse_ditto,
    "reverbnation": _parse_reverbnation,
    "bandcamp": _parse_bandcamp,
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
