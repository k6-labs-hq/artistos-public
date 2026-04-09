"""
Pure row-transform helpers for the XR7 variance-detection and universal-event
pipeline steps.

No ORM objects are imported.  All functions accept plain Python primitives so
they can be driven by n8n, LangGraph, or unit tests without a DB session.
"""

from __future__ import annotations

from typing import Any

#: Multiplier applied to reported payout to produce the expected payout.
#: Set to 1.2 (i.e. 20% above reported) as the baseline for variance detection.
EXPECTED_PAYOUT_UPLIFT: float = 1.2


def event_to_variance_row(quantity: float, unit_value: float) -> dict[str, Any]:
    """Build a variance-detection input row from raw event values.

    Parameters
    ----------
    quantity:
        Number of streams / plays / units.
    unit_value:
        Per-unit amount (in the event's native currency).

    Returns a dict compatible with ``VarianceDetectionService.run()``.
    """
    payout = quantity * unit_value
    return {
        "streams": quantity,
        "payout": payout,
        "expected_payout": payout * EXPECTED_PAYOUT_UPLIFT,
        "has_registration": True,
        "reported_usage": quantity,
    }


def event_to_universal_row(
    *,
    artist_id: str,
    source_name: str,
    event_type: str,
    amount: float,
    quantity: float,
    unit_value: float,
    currency: str = "USD",
    territory: str | None = None,
    event_id: str | None = None,
) -> dict[str, Any]:
    """Build a universal-event row ready for ``UniversalEventService.persist_many()``.

    All parameters are plain primitives — extract them from your ORM objects
    before calling this function so the core module stays DB-free.
    """
    return {
        "artist_id": artist_id,
        "source_type": "event",
        "source_name": source_name,
        "record_type": "EVENT",
        "event_type": event_type,
        "amount": amount,
        "quantity": quantity,
        "unit_value": unit_value,
        "currency": currency,
        "territory": territory,
        "work_id": None,
        "work_title": None,
        "isrc": None,
        "metadata": {"event_id": event_id},
    }
