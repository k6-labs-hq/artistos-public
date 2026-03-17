"""
Statute-of-Limitations (SOL) Tracker for XR7 Engine 2.

Artists have a finite window to file claims for unpaid royalties and other
music-industry obligations.  Missing that window means permanently losing the
right to recover those funds.

This module:
- Defines SOL windows per anomaly category and territory.
- Classifies each anomaly as URGENT (< 90 days left), AT_RISK (90–180 days),
  or OK (> 180 days remaining) — or EXPIRED if the window has already passed.
- Returns a prioritised list so artists and their representatives can act on the
  most time-sensitive issues first.

Default windows are based on common US/EU music-industry practice:
  - US copyright / mechanical royalties: 3 years (17 U.S.C. § 507(b))
  - UK / EU performing rights: 6 years
  - Touring / live performance disputes: 2 years

All windows are configurable — pass a custom ``sol_windows`` dict to override.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from XR7.recovery.sol_calculator import SOL_DISCLAIMER, calculate_sol


# ---------------------------------------------------------------------------
# Default SOL windows (in days) per category × territory
# ---------------------------------------------------------------------------

# Structure: {category: {territory_or_"DEFAULT": days}}
# "DEFAULT" is used when no territory-specific window exists.
DEFAULT_SOL_WINDOWS: dict[str, dict[str, int]] = {
    "ROYALTY": {
        "DEFAULT": 1095,   # 3 years — US Copyright Act § 507(b)
        "GB": 2190,        # 6 years — UK Limitation Act 1980
        "EU": 2190,        # 6 years — common EU civil limitation period
    },
    "PLATFORM": {
        "DEFAULT": 1095,   # 3 years
        "GB": 2190,
        "EU": 2190,
    },
    "TOURING": {
        "DEFAULT": 730,    # 2 years — typical contractual dispute window
        "GB": 2190,
        "EU": 1095,
    },
    "MERCH": {
        "DEFAULT": 1095,
        "GB": 2190,
        "EU": 1095,
    },
    "SYNC": {
        "DEFAULT": 1095,
        "GB": 2190,
        "EU": 1095,
    },
    "BRAND": {
        "DEFAULT": 730,
        "GB": 2190,
        "EU": 1095,
    },
    "GRANT": {
        "DEFAULT": 1095,
        "GB": 2190,
        "EU": 2190,
    },
}

# SOL status thresholds (days remaining)
_URGENT_THRESHOLD = 90
_AT_RISK_THRESHOLD = 180


# ---------------------------------------------------------------------------
# SOL status enum (string values so they serialise cleanly in API responses)
# ---------------------------------------------------------------------------

class SOLStatus:
    EXPIRED = "EXPIRED"       # Window has already passed — claim may be time-barred
    URGENT = "URGENT"         # < 90 days remaining
    AT_RISK = "AT_RISK"       # 90–180 days remaining
    OK = "OK"                 # > 180 days remaining
    UNKNOWN = "UNKNOWN"       # Cannot determine (missing created_at)


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _sol_window_days(
    category: str,
    territory: str | None,
    sol_windows: dict[str, dict[str, int]],
) -> int:
    """Return the applicable SOL window in days for a given category/territory."""
    cat_windows = sol_windows.get(category.upper(), {})
    if territory:
        # Try exact match, then 2-char country code prefix
        for key in (territory.upper(), territory.upper()[:2]):
            if key in cat_windows:
                return cat_windows[key]
    return cat_windows.get("DEFAULT", 1095)


def _days_remaining(created_at: datetime, sol_days: int, reference_dt: datetime) -> int:
    """Return days remaining in the SOL window (negative = expired)."""
    deadline = created_at + timedelta(days=sol_days)
    # Make both timezone-aware for comparison
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    if reference_dt.tzinfo is None:
        reference_dt = reference_dt.replace(tzinfo=timezone.utc)
    return (deadline - reference_dt).days


def _classify_status(days_left: int) -> str:
    if days_left < 0:
        return SOLStatus.EXPIRED
    if days_left <= _URGENT_THRESHOLD:
        return SOLStatus.URGENT
    if days_left <= _AT_RISK_THRESHOLD:
        return SOLStatus.AT_RISK
    return SOLStatus.OK


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_anomalies(
    anomalies: list[dict],
    sol_windows: dict[str, dict[str, int]] | None = None,
    reference_dt: datetime | None = None,
) -> list[dict]:
    """
    Attach SOL metadata to each anomaly dict and return a sorted list.

    Parameters
    ----------
    anomalies:
        List of anomaly dicts.  Each dict should contain at least
        ``category``, and ideally ``territory`` and ``created_at``
        (ISO string or datetime).
    sol_windows:
        Override the default SOL windows.  Uses ``DEFAULT_SOL_WINDOWS`` if
        omitted.
    reference_dt:
        The "current" datetime used to compute days remaining.  Defaults to
        ``datetime.now(timezone.utc)``.

    Returns
    -------
    List of dicts, each original anomaly dict augmented with:
    - ``sol_status``: ``"EXPIRED"`` | ``"URGENT"`` | ``"AT_RISK"`` | ``"OK"`` | ``"UNKNOWN"``
    - ``sol_days_remaining``: int (negative = expired, None if unknown)
    - ``sol_deadline``: ISO date string of the filing deadline (or None)
    - ``sol_window_days``: the applicable window used

    Sorted by ``sol_days_remaining`` ascending (most urgent first; expired first).
    """
    windows = sol_windows or DEFAULT_SOL_WINDOWS
    ref = reference_dt or datetime.now(timezone.utc)

    results: list[dict] = []
    for a in anomalies:
        if a.get("governing_law_state") or a.get("contract_type"):
            sol = calculate_sol(
                governing_law_state=a.get("governing_law_state"),
                contract_type=a.get("contract_type"),
                infringement_date=a.get("infringement_date") or a.get("time_window_end"),
                discovery_date=a.get("discovery_date") or a.get("created_at"),
                as_of=ref,
            )
            enriched = {
                **a,
                "sol_status": sol.get("sol_status") or SOLStatus.UNKNOWN,
                "sol_days_remaining": sol.get("sol_days_remaining"),
                "sol_deadline": sol.get("sol_deadline").date().isoformat() if sol.get("sol_deadline") else None,
                "sol_window_days": int((sol.get("sol_window_years") or 0) * 365),
                "sol_citation_source": sol.get("sol_citation_source"),
                "legal_disclaimer": SOL_DISCLAIMER,
            }
            results.append(enriched)
            continue

        category = str(a.get("category", "ROYALTY"))
        territory = a.get("territory")

        sol_days = _sol_window_days(category, territory, windows)
        deadline_str = None
        days_left = None
        status = SOLStatus.UNKNOWN

        raw_created = a.get("created_at")
        if raw_created is not None:
            if isinstance(raw_created, str):
                try:
                    created_at = datetime.fromisoformat(raw_created)
                except ValueError:
                    created_at = None
            elif isinstance(raw_created, datetime):
                created_at = raw_created
            else:
                created_at = None

            if created_at is not None:
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                deadline = created_at + timedelta(days=sol_days)
                days_left = _days_remaining(created_at, sol_days, ref)
                status = _classify_status(days_left)
                deadline_str = deadline.date().isoformat()

        enriched = {
            **a,
            "sol_status": status,
            "sol_days_remaining": days_left,
            "sol_deadline": deadline_str,
            "sol_window_days": sol_days,
        }
        results.append(enriched)

    # Sort: EXPIRED first (most negative days), then by days ascending
    return sorted(
        results,
        key=lambda x: (x["sol_days_remaining"] is None, x["sol_days_remaining"] or 0),
    )


def get_urgent_anomalies(
    anomalies: list[dict],
    sol_windows: dict[str, dict[str, int]] | None = None,
    reference_dt: datetime | None = None,
) -> list[dict]:
    """
    Return only anomalies whose SOL status is EXPIRED, URGENT, or AT_RISK.

    Useful for surfacing the subset of anomalies that require immediate action.
    """
    classified = classify_anomalies(anomalies, sol_windows=sol_windows, reference_dt=reference_dt)
    return [a for a in classified if a["sol_status"] in (SOLStatus.EXPIRED, SOLStatus.URGENT, SOLStatus.AT_RISK)]


def sol_summary(
    anomalies: list[dict],
    sol_windows: dict[str, dict[str, int]] | None = None,
    reference_dt: datetime | None = None,
) -> dict:
    """
    Return a high-level summary of SOL exposure across all anomalies.

    Returns
    -------
    Dict with counts per SOL status and a list of the most urgent anomaly IDs.
    """
    classified = classify_anomalies(anomalies, sol_windows=sol_windows, reference_dt=reference_dt)
    counts: dict[str, int] = {
        SOLStatus.EXPIRED: 0,
        SOLStatus.URGENT: 0,
        SOLStatus.AT_RISK: 0,
        SOLStatus.OK: 0,
        SOLStatus.UNKNOWN: 0,
    }
    for a in classified:
        counts[a["sol_status"]] = counts.get(a["sol_status"], 0) + 1

    urgent = [
        a.get("id") or a.get("subtype", "unknown")
        for a in classified
        if a["sol_status"] in (SOLStatus.EXPIRED, SOLStatus.URGENT)
    ]

    return {
        "total_anomalies": len(classified),
        "counts_by_status": counts,
        "urgent_anomaly_ids": urgent,
        "action_required": counts[SOLStatus.EXPIRED] + counts[SOLStatus.URGENT] > 0,
    }
