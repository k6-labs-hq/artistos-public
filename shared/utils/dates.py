"""shared.utils.dates – date/datetime helpers used across XR7 modules.

Consolidates the private ``_ensure_utc`` copied verbatim into ≥ 8 module
files, the ``_period_key`` / ``_quarter_label`` helpers duplicated in at
least 2 modules, and supplements the existing ``XR7.utils.datetime_utils``
(which is kept for backward-compat).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal


def ensure_utc(
    dt: datetime | None,
    *,
    fallback_to_now: bool = True,
) -> datetime | None:
    """Return *dt* normalised to UTC.

    * If *dt* is already timezone-aware it is converted to UTC.
    * If *dt* is naive it is assumed to already be UTC and ``tzinfo`` is
      attached without conversion.
    * If *dt* is ``None`` and *fallback_to_now* is ``True`` (the default),
      ``datetime.now(timezone.utc)`` is returned.
    * If *dt* is ``None`` and *fallback_to_now* is ``False``, ``None`` is
      returned.

    Replaces the private ``_ensure_utc`` that was copy-pasted into:
      - ``XR7/modules/contract_drift_monitor.py``
      - ``XR7/modules/catalog_value_appraiser.py``
      - ``XR7/modules/royalty_dna_profile.py``
      - ``XR7/modules/ghost_catalog_detector.py``
      - ``XR7/modules/earnings_time_machine.py``
      - ``XR7/modules/black_box_countdown.py``
      - ``XR7/modules/recovery_credit_score.py``
      - ``XR7/modules/payer_health_score.py``
    """
    if dt is None:
        return datetime.now(timezone.utc) if fallback_to_now else None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


Granularity = Literal["month", "quarter", "year"]


def period_key(dt: datetime, granularity: Granularity = "month") -> str:
    """Return a sortable string label for the period that contains *dt*.

    Examples::

        period_key(dt, "month")   -> "2025-03"
        period_key(dt, "quarter") -> "2025-Q1"
        period_key(dt, "year")    -> "2025"

    Replaces the private ``_quarter_label`` in ``contract_drift_monitor`` and
    the ``_period_key`` helper in ``earnings_time_machine``.
    """
    if granularity == "month":
        return dt.strftime("%Y-%m")
    if granularity == "quarter":
        q = (dt.month - 1) // 3 + 1
        return f"{dt.year}-Q{q}"
    return str(dt.year)
