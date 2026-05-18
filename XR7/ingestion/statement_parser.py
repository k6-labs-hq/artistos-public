"""
Royalty Statement CSV Parser for XR7 Engine 2.

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
Each normalised *event* dict maps to the :class:`~XR7.models.event.Event`
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

Each normalised *payment* dict maps to :class:`~XR7.models.payment.Payment`::

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
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

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
        # Modern TuneCore "Music Sales" export columns. Detection requires
        # the unambiguous-to-TuneCore column names (Sales Period + TC Song
        # ID + Total Earned), with the legacy "Sale Month" form kept as a
        # secondary detection path for older exports.
        "required": {"sales period", "tc song id", "total earned"},
        "aliases": {"total earned": "amount", "optional isrc": "isrc", "country of sale": "country"},
    },
    "tunecore_legacy": {
        # Older TuneCore exports we still want to detect. Kept separate so
        # the dispatcher can route both to _parse_tunecore.
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
    "bmi_real": {
        # BMI's real Royalty Distribution Statement CSV (28-col writer/publisher
        # export from the BMI member portal). Distinct from the simplified
        # 'bmi' format above which is the synthetic test fixture shape.
        "required": {"period", "title name", "perf source", "royalty amount", "perf count"},
        "aliases": {
            "title name": "title",
            "royalty amount": "amount",
            "perf source": "source",
            "perf count": "quantity",
        },
    },
    "mlc": {
        # The MLC mechanical royalty distribution. Native export is Apple
        # Numbers (.numbers); also available as CSV from the member portal.
        "required": {
            "payee mlc number",
            "mlc song code",
            "distributed amount",
            "processing type",
            "number of usages",
        },
        "aliases": {
            "distributed amount": "amount",
            "number of usages": "quantity",
            "dsp name": "source",
            "work primary title": "title",
        },
    },
    "spotify": {
        "required": {"track name", "streams", "stream revenue"},
        "aliases": {"track name": "title", "stream revenue": "amount", "streams": "quantity"},
    },
    "soundcloud": {
        "required": {"track title", "plays", "revenue"},
        "aliases": {},
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
        "key_columns": [
            "Sale Month",
            "Store",
            "Country",
            "Title",
            "ISRC",
            "Quantity",
            "Net Revenue",
        ],
        "description": "TuneCore royalty statement CSV.",
    },
    "cdbaby": {
        "name": "CD Baby",
        "type": "distributor",
        "key_columns": [
            "Store",
            "Country",
            "Sale Date",
            "Title",
            "ISRC",
            "Quantity",
            "Total Earnings",
        ],
        "description": "CD Baby royalty statement CSV.",
    },
    "amuse": {
        "name": "Amuse",
        "type": "distributor",
        "key_columns": [
            "Reporting Period",
            "Platform",
            "Country",
            "Track Title",
            "ISRC",
            "Streams",
            "Revenue",
        ],
        "description": "Amuse royalty report CSV.",
    },
    "unitedmasters": {
        "name": "United Masters",
        "type": "distributor",
        "key_columns": [
            "Period",
            "Store",
            "Country/Region",
            "Track",
            "ISRC",
            "Units",
            "Total Revenue",
        ],
        "description": "United Masters earnings export CSV.",
    },
    "onerpm": {
        "name": "ONErpm",
        "type": "distributor",
        "key_columns": [
            "Sale Date",
            "Retailer",
            "Country",
            "Track Title",
            "ISRC",
            "Qty",
            "Net Amount",
        ],
        "description": "ONErpm royalty statement CSV.",
    },
    "stem": {
        "name": "Stem",
        "type": "distributor",
        "key_columns": [
            "Period",
            "Platform",
            "Country Code",
            "Track Name",
            "ISRC",
            "Streams",
            "Net Revenue",
        ],
        "description": "Stem earnings report CSV.",
    },
    "landr": {
        "name": "LANDR",
        "type": "distributor",
        "key_columns": [
            "Month",
            "Store",
            "Territory",
            "Track Name",
            "ISRC",
            "Net Quantity",
            "Net Revenue",
        ],
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
        "key_columns": [
            "Date",
            "Item Name",
            "Buyer Name",
            "Country",
            "Item Type",
            "Quantity",
            "Revenue",
        ],
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
        "description": "BMI royalty statement CSV (simplified test fixture shape).",
    },
    "bmi_real": {
        "name": "BMI (Royalty Distribution Statement)",
        "type": "pro",
        "key_columns": [
            "PERIOD",
            "W OR P",
            "PARTICIPANT NAME",
            "TITLE NAME",
            "PERF SOURCE",
            "PERF COUNT",
            "ROYALTY AMOUNT",
        ],
        "description": (
            "BMI's real 28-column Royalty Distribution Statement CSV "
            "(downloaded from BMI member portal). Period encoded as YYYYQ "
            "(e.g. 20253 = Q3 2025). Currently parses writer rows only; "
            "publisher rows (W OR P = P) are skipped."
        ),
    },
    "mlc": {
        "name": "The MLC (mechanical royalties)",
        "type": "pro",
        "key_columns": [
            "Payee Name",
            "Payee MLC Number",
            "Usage Period Start Date",
            "Usage Period End Date",
            "DSP Name",
            "Work Primary Title",
            "ISWC",
            "Processing Type",
            "Number of Usages",
            "Royalty Amount",
            "Late Fee Amount",
            "Interest Amount",
            "Distributed Amount",
        ],
        "description": (
            "The Mechanical Licensing Collective mechanical royalty distribution. "
            "Native export is Apple Numbers (.numbers); also available as CSV. "
            "Use parse_mlc_numbers_file() for .numbers; CSV flows through the "
            "standard parse_csv() path."
        ),
    },
    "spotify": {
        "name": "Spotify for Artists",
        "type": "dsp",
        "key_columns": ["Date", "Country", "Track Name", "ISRC", "Streams", "Stream Revenue"],
        "description": "Spotify for Artists streaming report CSV.",
    },
    "soundcloud": {
        "name": "SoundCloud",
        "type": "dsp",
        "key_columns": [
            "Date",
            "Track Title",
            "SoundCloud Track ID",
            "Plays",
            "Revenue",
            "ISRC",
            "Release Date",
            "Waveform Duration",
        ],
        "description": (
            "SoundCloud monetization exports (CSV/TSV/XLSX). Also supports fallback header variants "
            "like stream count/listener count with net payout columns."
        ),
    },
    "generic": {
        "name": "Generic / Other",
        "type": "generic",
        "key_columns": [
            "date/period",
            "source/store/platform",
            "quantity/streams",
            "amount/revenue/earnings",
        ],
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
    "date",
    "timestamp",
    "period",
    "month",
    "sale date",
    "sale month",
    "performance date",
    "report date",
    "reporting period",
}
_GENERIC_AMOUNT_COLS = {
    "amount",
    "royalty",
    "revenue",
    "earnings",
    "net revenue",
    "total earnings",
    "stream revenue",
    "net",
    "net amount",
    "total revenue",
    "revenue (usd)",
    "net revenue (usd)",
}
_GENERIC_QUANTITY_COLS = {
    "quantity",
    "streams",
    "plays",
    "units",
    "impressions",
    "views",
    "qty",
    "net quantity",
}
_GENERIC_SOURCE_COLS = {
    "source",
    "platform",
    "store",
    "distributor",
    "payer",
    "channel",
    "retailer",
}
_GENERIC_TERRITORY_COLS = {
    "country",
    "territory",
    "region",
    "country/region",
    "country code",
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

    # SoundCloud exports vary, but usually include explicit provider metadata.
    if (
        any("soundcloud" in h for h in normalised)
        and ("plays" in normalised or "stream count" in normalised or "streams" in normalised)
        and ("revenue" in normalised or "net payout" in normalised or "earnings" in normalised)
    ):
        return "soundcloud"

    # Variant with no explicit provider key but with SoundCloud-specific metadata fields.
    if ("waveform duration" in normalised or "soundcloud track id" in normalised) and (
        "plays" in normalised or "stream count" in normalised or "streams" in normalised
    ):
        return "soundcloud"

    # DistroKid: accept both legacy ("Month" + "Earnings") and modern
    # ("Sale Month" + "Earnings (USD)") header conventions. Modern statements
    # (downloaded from DistroKid Bank → Reports as of 2026) use the latter
    # and would otherwise fall through to the generic parser. Checked before
    # the generic loop because TuneCore also has "sale month" + the constant
    # columns; the differentiator is "earnings*" vs "net revenue".
    if (
        {"store", "title", "quantity"}.issubset(normalised)
        and (normalised & {"month", "sale month"})
        and any(h == "earnings" or h.startswith("earnings ") for h in normalised)
    ):
        return "distrokid"

    for fmt_name, spec in _FORMATS.items():
        required = spec["required"]
        if required.issubset(normalised):
            return fmt_name
    return "generic"


# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

_DATE_FMTS = [
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%Y/%m/%d",
    "%B %Y",
    "%b %Y",
    "%m-%Y",
    "%Y-%m",
    "%m/%Y",
    "%d-%b-%Y",
    "%b-%Y",
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


@dataclass(frozen=True)
class _DistributorCols:
    """
    Column-name alternatives and fixed defaults for one distributor format.

    Each tuple is tried left-to-right by ``_col()``; the first non-empty
    value wins.  ``source_label`` is the human-readable prefix written into
    ``payment["source"]`` (e.g. ``"DistroKid"`` → ``"DistroKid / Spotify"``).
    """

    date: tuple[str, ...]
    quantity: tuple[str, ...]
    amount: tuple[str, ...]
    platform: tuple[str, ...]
    territory: tuple[str, ...]
    title: tuple[str, ...]
    default_platform: str
    source_label: str
    fmt_key: str
    event_type: str = "STREAM"


# One entry per supported distributor.  PROs (ASCAP/BMI), DSPs (Spotify/
# SoundCloud), and Bandcamp keep dedicated parsers below because their
# field semantics differ materially (fixed territory, per-performance
# quantity, item-type source label, etc.).
_DISTRIBUTOR_COLS: dict[str, _DistributorCols] = {
    "distrokid": _DistributorCols(
        date=("month", "sale month", "date"),
        quantity=("quantity",),
        amount=("earnings", "earnings (usd)", "net", "amount"),
        platform=("store", "platform", "source"),
        territory=("country", "country of sale", "territory"),
        title=("title", "track name", "song"),
        default_platform="DistroKid",
        source_label="DistroKid",
        fmt_key="distrokid",
    ),
    "tunecore": _DistributorCols(
        # Modern TuneCore "Music Sales" export has these column names. The
        # legacy aliases ("sale month", "net revenue", etc.) stay for older
        # exports we may still see. Real header sample (2024 export):
        #   "Sales Period","Posted Date","Store Name","Country Of Sale",
        #   "Artist","Release Type","Release Title","Song Title","Label",
        #   "UPC","Optional UPC","TC Song ID","Optional ISRC","Sales Type",
        #   "# Units Sold","Per Unit Price","Net Sales","Net Sales Currency",
        #   "Exchange Rate","Total Earned","Currency","Commission",
        #   "Youtube Video ID","Youtube Policy Type"
        date=("sales period", "sale month", "month", "date"),
        quantity=("# units sold", "units sold", "quantity"),
        amount=("total earned", "net revenue", "net sales", "amount", "earnings"),
        platform=("store name", "store", "platform"),
        territory=("country of sale", "country", "territory"),
        title=("song title", "release title", "title", "track name", "song"),
        default_platform="TuneCore",
        source_label="TuneCore",
        fmt_key="tunecore",
    ),
    # Alias entry so the format dispatcher can route "tunecore_legacy" detections
    # (older exports — see _FORMATS) to the same tunecore parser.
    "tunecore_legacy": _DistributorCols(
        date=("sale month", "month", "date"),
        quantity=("quantity",),
        amount=("net revenue", "amount", "earnings"),
        platform=("store", "platform"),
        territory=("country", "territory"),
        title=("title", "track name", "song"),
        default_platform="TuneCore",
        source_label="TuneCore",
        fmt_key="tunecore_legacy",
    ),
    "cdbaby": _DistributorCols(
        date=("sale date", "date", "month"),
        quantity=("quantity",),
        amount=("total earnings", "royalty", "amount"),
        platform=("store", "platform"),
        territory=("country", "territory"),
        title=("title", "track name", "song"),
        default_platform="CD Baby",
        source_label="CD Baby",
        fmt_key="cdbaby",
    ),
    "amuse": _DistributorCols(
        date=("reporting period", "period", "date", "month"),
        quantity=("streams", "plays", "quantity"),
        amount=("revenue", "revenue (usd)", "net revenue", "amount"),
        platform=("platform", "store"),
        territory=("country", "territory"),
        title=("track title", "title", "track name", "song"),
        default_platform="Amuse",
        source_label="Amuse",
        fmt_key="amuse",
    ),
    "unitedmasters": _DistributorCols(
        date=("period", "date", "month"),
        quantity=("units", "streams", "quantity"),
        amount=("total revenue", "net revenue", "revenue", "amount"),
        platform=("store", "platform", "retailer"),
        territory=("country/region", "country", "territory"),
        title=("track", "track title", "title", "track name", "song"),
        default_platform="United Masters",
        source_label="United Masters",
        fmt_key="unitedmasters",
    ),
    "onerpm": _DistributorCols(
        date=("sale date", "date", "period", "month"),
        quantity=("qty", "quantity", "streams"),
        amount=("net amount", "amount", "revenue", "net revenue"),
        platform=("retailer", "store", "platform"),
        territory=("country", "territory"),
        title=("track title", "title", "track name", "song"),
        default_platform="ONErpm",
        source_label="ONErpm",
        fmt_key="onerpm",
    ),
    "stem": _DistributorCols(
        date=("period", "date", "month"),
        quantity=("streams", "plays", "quantity"),
        amount=("net revenue", "revenue", "amount"),
        platform=("platform", "store"),
        territory=("country code", "country", "territory"),
        title=("track name", "track title", "title", "song"),
        default_platform="Stem",
        source_label="Stem",
        fmt_key="stem",
    ),
    "landr": _DistributorCols(
        date=("month", "period", "date"),
        quantity=("net quantity", "quantity", "streams"),
        amount=("net revenue", "net revenue (usd)", "revenue", "amount"),
        platform=("store", "platform", "retailer"),
        territory=("territory", "country"),
        title=("track name", "track title", "title", "song"),
        default_platform="LANDR",
        source_label="LANDR",
        fmt_key="landr",
    ),
    "ditto": _DistributorCols(
        date=("month", "period", "date"),
        quantity=("streams", "plays", "quantity"),
        amount=("net revenue", "revenue", "amount"),
        platform=("store", "platform"),
        territory=("country", "territory"),
        title=("title", "track name", "track title", "song"),
        default_platform="Ditto Music",
        source_label="Ditto Music",
        fmt_key="ditto",
    ),
    "reverbnation": _DistributorCols(
        date=("date", "period", "month"),
        quantity=("streams", "plays", "quantity"),
        amount=("revenue", "net revenue", "amount"),
        platform=("platform", "store"),
        territory=("country", "territory"),
        title=("song", "title", "track name", "track title"),
        default_platform="ReverbNation",
        source_label="ReverbNation",
        fmt_key="reverbnation",
    ),
}


def _parse_distributor_row(
    spec: _DistributorCols,
    row: dict,
    artist_id: str,
) -> tuple[dict | None, dict | None]:
    """
    Generic distributor parser driven by a ``_DistributorCols`` config.

    All 10 mainstream distributor formats share the same shape:
    (date, quantity, amount, platform, territory, title, ISRC, currency).
    Only the column name alternatives and defaults differ.
    """
    dt = _parse_date(_col(row, *spec.date)) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, *spec.quantity))
    amount = _parse_amount(_col(row, *spec.amount))
    if amount is None:
        return None, None

    platform = _col(row, *spec.platform) or spec.default_platform
    territory = _col(row, *spec.territory) or "US"
    title = _col(row, *spec.title)
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"
    unit_value = _calc_unit_value(amount, quantity)

    event = {
        "event_type": spec.event_type,
        "artist_id": artist_id,
        "platform": platform,
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
        "source": f"{spec.source_label} / {platform}",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, spec.fmt_key),
    }
    return event, payment


# Thin wrappers so that _FORMAT_PARSERS entries remain plain callables.
# Each delegates to _parse_distributor_row with the frozen column spec.


def _parse_distrokid(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    return _parse_distributor_row(_DISTRIBUTOR_COLS["distrokid"], row, artist_id)


def _parse_tunecore(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    return _parse_distributor_row(_DISTRIBUTOR_COLS["tunecore"], row, artist_id)


def _parse_cdbaby(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    return _parse_distributor_row(_DISTRIBUTOR_COLS["cdbaby"], row, artist_id)


def _parse_amuse(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    return _parse_distributor_row(_DISTRIBUTOR_COLS["amuse"], row, artist_id)


def _parse_unitedmasters(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    return _parse_distributor_row(_DISTRIBUTOR_COLS["unitedmasters"], row, artist_id)


def _parse_onerpm(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    return _parse_distributor_row(_DISTRIBUTOR_COLS["onerpm"], row, artist_id)


def _parse_stem(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    return _parse_distributor_row(_DISTRIBUTOR_COLS["stem"], row, artist_id)


def _parse_landr(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    return _parse_distributor_row(_DISTRIBUTOR_COLS["landr"], row, artist_id)


def _parse_ditto(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    return _parse_distributor_row(_DISTRIBUTOR_COLS["ditto"], row, artist_id)


def _parse_reverbnation(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    return _parse_distributor_row(_DISTRIBUTOR_COLS["reverbnation"], row, artist_id)


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


# ── BMI real-format helpers (28-col Royalty Distribution Statement) ─────────


def _decode_bmi_period(value: str) -> tuple[date | None, date | None]:
    """Decode BMI's ``YYYYQ`` period encoding.

    Examples: ``"20253"`` → (2025-07-01, 2025-09-30), ``"20251"`` → Q1 2025.
    Returns ``(None, None)`` for unparseable values (international accounting
    periods like ``191ST`` show in the PDF but not in the CSV; if they ever
    do appear, the row's amount is still captured but without a period).
    """
    raw = (value or "").strip()
    if len(raw) != 5 or not raw.isdigit():
        return None, None
    year = int(raw[:4])
    quarter = int(raw[4])
    if quarter < 1 or quarter > 4:
        return None, None
    start_month = (quarter - 1) * 3 + 1
    period_start = date(year, start_month, 1)
    end_month = start_month + 2
    last_day = _month_end(datetime(year, end_month, 1, tzinfo=timezone.utc))
    return period_start, last_day


_BMI_COUNTRY_TO_ISO = {
    "UNITED STATES": "US",
    "CANADA": "CA",
    "UNITED KINGDOM": "GB",
    "AUSTRALIA": "AU",
    "GERMANY": "DE",
    "FRANCE": "FR",
    "NETHERLANDS": "NL",
    "SWEDEN": "SE",
    "NORWAY": "NO",
    "DENMARK": "DK",
    "FINLAND": "FI",
    "JAPAN": "JP",
    "BRAZIL": "BR",
    "MEXICO": "MX",
    "ITALY": "IT",
    "SPAIN": "ES",
    "BELGIUM": "BE",
    "AUSTRIA": "AT",
    "SWITZERLAND": "CH",
    "IRELAND": "IE",
    "NEW ZEALAND": "NZ",
}


def _bmi_country_to_iso(country: str) -> str:
    """Map BMI's full-country-name to ISO 3166-1 alpha-2; default US."""
    raw = (country or "").strip().upper()
    return _BMI_COUNTRY_TO_ISO.get(raw, raw[:2] if len(raw) >= 2 else "US")


def _parse_bmi_real(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    """Parse one row of BMI's real 28-column Royalty Distribution Statement.

    Skips publisher rows (``W OR P == 'P'``) since this MVP-stage parser
    focuses on writer royalties; publisher rows are typically a separate
    distribution to a separate IPI.
    """
    w_or_p = _col(row, "w or p").strip().upper()
    if w_or_p and w_or_p != "W":
        return None, None

    amount_str = _col(row, "royalty amount", "current activity amt")
    amount = _parse_amount(amount_str)
    if amount is None or amount == 0:
        return None, None

    period_start, period_end = _decode_bmi_period(_col(row, "period"))

    perf_source = _col(row, "perf source") or "UNKNOWN"
    title = _col(row, "title name", "title") or "UNKNOWN"
    country = _col(row, "country of performance")
    perf_count = _parse_int(_col(row, "perf count")) or 1

    # Prefer explicit perf_date when present; fall back to period start.
    raw_perf_date = _col(row, "perf date")
    dt = _parse_date(raw_perf_date)
    if dt is None:
        dt = (
            datetime(period_start.year, period_start.month, period_start.day, tzinfo=timezone.utc)
            if period_start
            else datetime.now(timezone.utc)
        )

    # All BMI rows are unit-of-consumption that earned royalty — emit STREAM.
    # The platform field ("BMI / RADIO", "BMI / SPOTIFY PREM", "BMI / TIKTOK")
    # carries the source distinction. EventType.PERFORMANCE doesn't exist in
    # the schema; broadening the enum is a separate-PR conversation.
    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": f"BMI / {perf_source}",
        "territory": _bmi_country_to_iso(country),
        "timestamp": dt,
        "quantity": perf_count,
        "unit_value": round(amount / max(perf_count, 1), 6),
        "currency": "USD",
        "work_title": title,
    }
    # received_at marks when the artist actually got paid. Without this the
    # "stream month missing payment" rule false-positives on multi-period
    # ingestion (it would see all payments as arriving in one month).
    received_at = (
        datetime(period_end.year, period_end.month, period_end.day, tzinfo=timezone.utc)
        if period_end
        else dt
    )
    payment = {
        "payment_type": "ROYALTY",
        "artist_id": artist_id,
        "amount": round(amount, 6),
        "currency": "USD",
        "source": f"BMI / {perf_source}",
        "period_start": period_start,
        "period_end": period_end,
        "received_at": received_at,
        "reference_id": _row_hash(row, "bmi_real"),
        # BMI's per-row identifiers — required on dispute submissions, so
        # we denormalize them onto Payment at ingestion rather than asking
        # the artist to look them up later. See
        # docs/runbooks/bmi-dispute-attorney-brief.md §3.5 for context.
        "payer_account_id": _col(row, "participant #", "participant#") or None,
        "payer_ip_number": _col(row, "ip #", "ip#") or None,
        "payer_work_id": _col(row, "title #", "title#") or None,
    }
    return event, payment


# ── MLC (Mechanical Licensing Collective) parser ────────────────────────────


def _parse_mlc(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    """Parse one row of an MLC mechanical royalty distribution.

    All MLC rows are US-territory mechanical streaming income. We tag them
    as STREAM events with payment_type=ROYALTY but include processing_type
    in the source label so downstream filtering can distinguish ``regular``
    current-period payments from ``reprocessing`` retroactive catch-ups
    (an important signal — high reprocessing % suggests more uncollected
    royalties exist).
    """
    # Distributed Amount = Royalty Amount + Late Fee Amount + Interest Amount.
    # Use Distributed for the payment ledger (total received), and prefer it
    # over Royalty Amount alone since the late fee + interest are real
    # received income too.
    distributed = _parse_amount(_col(row, "distributed amount"))
    royalty = _parse_amount(_col(row, "royalty amount"))
    amount = distributed if distributed is not None else royalty
    if amount is None or amount == 0:
        return None, None

    quantity = _parse_int(_col(row, "number of usages")) or 1
    title = _col(row, "work primary title", "title") or "UNKNOWN"
    dsp_name = _col(row, "dsp name", "source") or "UNKNOWN"
    territory = _col(row, "territory") or "US"
    processing_type = _col(row, "processing type") or "regular"

    period_start_str = _col(row, "usage period start date")
    period_end_str = _col(row, "usage period end date")
    period_start = _parse_date(period_start_str)
    period_end = _parse_date(period_end_str)
    period_start_d = period_start.date() if period_start else None
    period_end_d = period_end.date() if period_end else None

    # Use period_start as the event timestamp; if missing, fall back to
    # ingestion time so downstream queries don't break.
    dt = period_start or datetime.now(timezone.utc)

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": f"MLC / {dsp_name}",
        "territory": territory,
        "timestamp": dt,
        "quantity": quantity,
        "unit_value": round(amount / max(quantity, 1), 6),
        "currency": "USD",
        "work_title": title,
        "isrc": _col(row, "isrc"),
    }
    # MLC distributes monthly so received_at ≈ period_end + a few weeks.
    # Use period_end as a sensible proxy — keeps multi-period analysis honest.
    received_at = period_end if period_end else dt
    payment = {
        "payment_type": "ROYALTY",
        "artist_id": artist_id,
        "amount": round(amount, 6),
        "currency": "USD",
        # Include processing_type in source so anomaly detection can detect
        # high reprocessing ratios per artist.
        "source": f"MLC / {dsp_name} / {processing_type}",
        "period_start": period_start_d,
        "period_end": period_end_d,
        "received_at": received_at,
        "reference_id": _row_hash(row, "mlc"),
        # MLC's per-row identifiers — captured for dispute-packet rendering.
        # See docs/runbooks/mlc-dispute-attorney-brief.md.
        "payer_account_id": _col(row, "payee mlc number") or None,
        "payer_work_id": _col(row, "mlc song code") or None,
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


def _parse_soundcloud(row: dict, artist_id: str) -> tuple[dict | None, dict | None]:
    raw_date = _col(row, "date", "report date", "period", "month")
    dt = _parse_date(raw_date) or datetime.now(timezone.utc)
    quantity = _parse_int(_col(row, "plays", "stream count", "streams", "listener count"))
    amount_str = _col(row, "revenue", "net payout", "earnings", "amount", "net revenue")
    amount = _parse_amount(amount_str)
    if amount is None:
        return None, None

    country = _col(row, "country", "territory", "region") or "US"
    title = _col(row, "track title", "title", "track name", "song")
    isrc = _col(row, "isrc")
    currency = _col(row, "currency") or "USD"
    release_date = _col(row, "release date")
    duration = _col(row, "waveform duration", "duration")
    sc_track_id = _col(row, "soundcloud track id", "track id")
    label = _col(row, "label", "label name")
    artist_name = _col(row, "artist", "artist name")

    unit_value = _calc_unit_value(amount, quantity)

    event = {
        "event_type": "STREAM",
        "artist_id": artist_id,
        "platform": "SoundCloud",
        "territory": country.upper()[:2] if country else None,
        "timestamp": dt,
        "quantity": quantity,
        "unit_value": round(unit_value, 8),
        "currency": currency,
        "work_title": title,
        "isrc": isrc,
        "soundcloud_track_id": sc_track_id,
        "release_date": release_date,
        "waveform_duration": duration,
        "artist_metadata": artist_name,
        "label_metadata": label,
    }
    payment = {
        "payment_type": "ROYALTY",
        "artist_id": artist_id,
        "amount": round(amount, 6),
        "currency": currency,
        "source": "SoundCloud",
        "period_start": date(dt.year, dt.month, 1),
        "period_end": _month_end(dt),
        "reference_id": _row_hash(row, "soundcloud"),
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


_FORMAT_PARSERS: dict[str, Any] = {
    # Distributor formats — handled by the unified config-driven parser.
    fmt: (lambda spec: lambda row, artist_id: _parse_distributor_row(spec, row, artist_id))(
        _DISTRIBUTOR_COLS[fmt]
    )
    for fmt in _DISTRIBUTOR_COLS
}
# PRO / DSP formats with non-standard field semantics keep dedicated parsers.
_FORMAT_PARSERS.update(
    {
        "bandcamp": _parse_bandcamp,  # SALE event, item_type source label
        "ascap": _parse_ascap,  # per-performance, fixed territory US
        "bmi": _parse_bmi,  # per-performance, fixed territory US
        "bmi_real": _parse_bmi_real,  # 28-col BMI Royalty Distribution Statement
        "mlc": _parse_mlc,  # The MLC mechanical royalty distribution
        "spotify": _parse_spotify,  # stream revenue column name
        "soundcloud": _parse_soundcloud,  # extra SC-specific metadata fields
        "generic": _parse_generic,  # column-sniffing fallback
    }
)


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
        # Fallback to latin-1, which accepts any byte value.
        text = content.decode("latin-1")

    # newline="" is required so the csv module — not StringIO — handles
    # line endings. Without it, a file with classic-Mac CR-only endings
    # (some Excel/Numbers exports produce these) raises csv.Error:
    # "new-line character seen in unquoted field".
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if reader.fieldnames is None:
        return ParseResult(
            format_detected="unknown",
            row_count=0,
            errors=["CSV file has no header row or is empty."],
        )

    try:
        rows = list(reader)
    except csv.Error as exc:
        return ParseResult(
            format_detected="unknown",
            row_count=0,
            errors=[f"CSV file could not be parsed: {exc}"],
        )
    return _parse_table_rows(rows, list(reader.fieldnames), artist_id)


def _parse_table_rows(
    rows: list[dict[str, str]], headers: list[str], artist_id: str
) -> ParseResult:
    fmt = detect_format(headers)
    parser = _FORMAT_PARSERS[fmt]

    events: list[dict] = []
    payments: list[dict] = []
    skipped = 0
    errors: list[str] = []

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

        if payment["amount"] == 0.0 and event["quantity"] == 0:
            skipped += 1
            continue

        events.append(event)
        payments.append(payment)

    if not events and not errors and rows:
        errors.append(
            f"No parseable rows found for format '{fmt}'. Ensure the file has the expected column headers."
        )

    return ParseResult(
        format_detected=fmt,
        row_count=len(rows),
        events=events,
        payments=payments,
        skipped_rows=skipped,
        errors=errors,
    )


def parse_delimited(
    content: bytes, artist_id: str, *, delimiter: str = ",", encoding: str = "utf-8-sig"
) -> ParseResult:
    try:
        text = content.decode(encoding)
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    # newline="" — see parse_csv. TSV exports with CR-only line endings
    # (the Tolliver DistroKid .tsv is one) otherwise raise csv.Error.
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter=delimiter)
    if reader.fieldnames is None:
        return ParseResult(
            format_detected="unknown",
            row_count=0,
            errors=["Delimited file has no header row or is empty."],
        )

    try:
        rows = list(reader)
    except csv.Error as exc:
        return ParseResult(
            format_detected="unknown",
            row_count=0,
            errors=[f"Delimited file could not be parsed: {exc}"],
        )
    return _parse_table_rows(rows, list(reader.fieldnames), artist_id)


def parse_xlsx(content: bytes, artist_id: str) -> ParseResult:
    try:
        wb = load_workbook(io.BytesIO(content), data_only=True, read_only=True)
    except Exception as exc:  # noqa: BLE001
        return ParseResult(
            format_detected="unknown", row_count=0, errors=[f"Unable to open XLSX file: {exc}"]
        )

    if not wb.worksheets:
        return ParseResult(
            format_detected="unknown", row_count=0, errors=["XLSX file has no worksheets."]
        )

    ws = wb.worksheets[0]
    iterator = ws.iter_rows(values_only=True)
    try:
        header_row = next(iterator)
    except StopIteration:
        return ParseResult(format_detected="unknown", row_count=0, errors=["XLSX file is empty."])

    headers = [str(cell).strip() if cell is not None else "" for cell in header_row]
    if not any(headers):
        return ParseResult(
            format_detected="unknown", row_count=0, errors=["XLSX header row is empty."]
        )

    rows: list[dict[str, str]] = []
    for cells in iterator:
        row: dict[str, str] = {}
        has_data = False
        for idx, header in enumerate(headers):
            if not header:
                continue
            raw = cells[idx] if idx < len(cells) else None
            val = "" if raw is None else str(raw)
            if val.strip():
                has_data = True
            row[header] = val
        if has_data:
            rows.append(row)

    return _parse_table_rows(rows, headers, artist_id)


def parse_statement_file(
    content: bytes, artist_id: str, *, filename: str = "statement.csv", encoding: str = "utf-8-sig"
) -> ParseResult:
    ext = Path(filename.lower()).suffix
    if ext == ".csv":
        return parse_csv(content, artist_id, encoding=encoding)
    if ext == ".tsv":
        return parse_delimited(content, artist_id, delimiter="\t", encoding=encoding)
    if ext == ".xlsx":
        return parse_xlsx(content, artist_id)
    return ParseResult(
        format_detected="unknown",
        row_count=0,
        errors=[f"Unsupported statement extension '{ext}'. Supported: .csv, .tsv, .xlsx"],
    )
