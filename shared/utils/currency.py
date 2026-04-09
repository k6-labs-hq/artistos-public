"""shared.utils.currency – currency code coercion.

Replaces the inline ``str(row.get("currency") or "USD")`` pattern that
appears in at least 9 call-sites across ingestion, pipeline, and LLM layers.
"""

from __future__ import annotations

# ISO 4217 codes that the platform currently handles.
_KNOWN_CURRENCIES: frozenset[str] = frozenset(
    {
        "USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF",
        "SEK", "NOK", "DKK", "NZD", "HKD", "SGD", "MXN",
        "BRL", "ZAR", "INR", "KRW", "CNY",
    }
)

_FALLBACK = "USD"


def coerce_currency(value: object, *, fallback: str = _FALLBACK) -> str:
    """Return a normalised, upper-cased ISO 4217 currency code.

    * ``None`` / empty / whitespace → *fallback* (default ``"USD"``)
    * Unknown codes are uppercased and returned as-is (lenient; the model
      layer enforces referential integrity).

    Replaces ``str(row.get("currency") or "USD")`` in:
      - ``XR7/services/xr7_pipelines.py``
      - ``XR7/services/xr7_ugc_service.py``
      - ``XR7/ingestion/creator_parsers.py`` (×6)
      - ``XR7/llm/claim_drafter.py``
    """
    if not value:
        return fallback
    code = str(value).strip().upper()
    return code if code else fallback
