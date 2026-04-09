"""shared.utils.numbers – numeric coercion and rounding helpers.

Consolidates:
  - ``_safe_float`` duplicated across ``enterprise_historical_analysis``,
    ``tvfilm_vertical``, ``tvfilm_compensation_engine``,
    ``founder_program``, and ``org_dashboard_service`` (as ``_to_float``).
  - The ``round(x, 2)`` pattern for monetary values used in > 25 spots.
"""

from __future__ import annotations

from typing import Any

# Sentinel strings that represent "no value" when a number field is read
# from user-supplied CSV / spreadsheet data.
_EMPTY_TOKENS: frozenset[str] = frozenset({"", "-", "N/A", "na", "None", "n/a"})


def safe_float(value: Any, *, default: float = 0.0) -> float:
    """Coerce *value* to ``float``, stripping common formatting artefacts.

    Handles:
    * ``None``              → *default*
    * ``""`` / ``"-"`` / ``"N/A"`` / ``"na"`` / ``"None"`` → *default*
    * Leading ``$`` / embedded ``,``  (e.g. ``"$1,234.56"``) → stripped
    * Anything that still cannot be parsed → *default*

    Replaces ``_safe_float`` in ``tvfilm_vertical``, ``tvfilm_compensation_engine``,
    and ``enterprise_historical_analysis``, and ``_to_float`` in
    ``org_dashboard_service``.

    ``founder_program._safe_float`` returned ``None`` for unparseable input;
    callers there should pass ``default=None`` and annotate accordingly, or
    handle ``None`` themselves.
    """
    if value is None:
        return default
    text = str(value).strip().replace(",", "").replace("$", "")
    if text in _EMPTY_TOKENS:
        return default
    try:
        return float(text)
    except ValueError:
        return default


def money_round(value: float) -> float:
    """Round a monetary value to two decimal places (bank / display rounding).

    A named wrapper around ``round(value, 2)`` that makes intent explicit
    and can be swapped for ``Decimal`` rounding in the future without
    touching every call-site.
    """
    return round(value, 2)
