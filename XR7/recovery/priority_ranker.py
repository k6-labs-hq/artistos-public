"""
Recovery Priority Ranker for XR7 Engine 2.

Given a set of open anomalies and in-flight claims, this module scores each
item and returns a prioritised action queue so artists and their representatives
can focus on the highest-ROI recovery actions first.

Scoring formula
---------------
    priority_score = (estimated_recoverable × confidence_score × urgency_factor)
                     / (1 + age_decay_factor)

Where:
- ``estimated_recoverable`` — the dollar amount at stake (from the anomaly).
  Defaults to a category-specific average if not set.
- ``confidence_score`` — model/rule confidence [0, 1].
- ``urgency_factor`` — elevated by SOL status (EXPIRED=5, URGENT=3, AT_RISK=2, OK=1).
- ``age_decay_factor`` — items older than ``_AGE_DECAY_DAYS`` get a small penalty
  to favour recently-detected issues (prevent stale items dominating forever).

The score is normalised to [0, 100] across the returned list so it is easy to
display as a percentage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# How many days before age decay kicks in
_AGE_DECAY_DAYS = 365

# Age decay coefficient: penalty per year of age beyond _AGE_DECAY_DAYS
_AGE_DECAY_COEFFICIENT = 0.1

# Urgency multipliers by SOL status
_SOL_URGENCY: dict[str, float] = {
    "EXPIRED": 5.0,
    "URGENT": 3.0,
    "AT_RISK": 2.0,
    "OK": 1.0,
    "UNKNOWN": 1.0,
}

# Default estimated recoverable values by anomaly category (USD)
# Used when an anomaly has no explicit ``estimated_recoverable`` field.
_DEFAULT_RECOVERABLE: dict[str, float] = {
    "ROYALTY": 500.0,
    "PLATFORM": 250.0,
    "TOURING": 1500.0,
    "MERCH": 300.0,
    "SYNC": 2000.0,
    "BRAND": 800.0,
    "GRANT": 1000.0,
}

_GLOBAL_DEFAULT_RECOVERABLE = 500.0


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

class ActionType:
    INVESTIGATE_ANOMALY = "INVESTIGATE_ANOMALY"
    FILE_CLAIM = "FILE_CLAIM"
    ADVANCE_CLAIM = "ADVANCE_CLAIM"
    REQUEST_AUDIT = "REQUEST_AUDIT"


@dataclass
class PriorityItem:
    """A single scored item in the priority queue."""

    item_id: str
    item_type: str                    # "ANOMALY" or "CLAIM"
    action: str                       # see ActionType
    artist_id: str
    category: str
    subtype: str
    priority_score: float             # raw score (before normalisation)
    priority_rank: int = 0            # 1 = highest priority
    normalised_score: float = 0.0     # [0, 100]
    estimated_recoverable: float = 0.0
    confidence_score: float = 0.0
    sol_status: str = "UNKNOWN"
    sol_days_remaining: int | None = None
    description: str = ""
    claim_status: str | None = None

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "item_type": self.item_type,
            "action": self.action,
            "artist_id": self.artist_id,
            "category": self.category,
            "subtype": self.subtype,
            "priority_rank": self.priority_rank,
            "normalised_score": round(self.normalised_score, 1),
            "estimated_recoverable": round(self.estimated_recoverable, 2),
            "confidence_score": round(self.confidence_score, 4),
            "sol_status": self.sol_status,
            "sol_days_remaining": self.sol_days_remaining,
            "description": self.description,
            "claim_status": self.claim_status,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_datetime(val: Any) -> datetime | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(str(val))
    except (ValueError, TypeError):
        return None


def _age_factor(created_at: datetime | None, reference_dt: datetime) -> float:
    """
    Return a decay factor > 0 that penalises very old items.
    Factor = 0.0 for items younger than _AGE_DECAY_DAYS.
    """
    if created_at is None:
        return 0.0
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    age_days = (reference_dt - created_at).days
    if age_days <= _AGE_DECAY_DAYS:
        return 0.0
    excess_years = (age_days - _AGE_DECAY_DAYS) / 365.0
    return _AGE_DECAY_COEFFICIENT * excess_years


def _score_item(
    estimated_recoverable: float,
    confidence: float,
    sol_status: str,
    created_at: datetime | None,
    reference_dt: datetime,
    threshold_adjustment: float = 1.0,
    effort_adjustment: float = 1.0,
) -> float:
    urgency = _SOL_URGENCY.get(sol_status, 1.0)
    decay = _age_factor(created_at, reference_dt)
    adjusted_recoverable = estimated_recoverable / max(threshold_adjustment, 1e-6)
    raw = (adjusted_recoverable * confidence * urgency) / (1.0 + decay)
    raw = raw / max(effort_adjustment, 1e-6)
    return max(raw, 0.0)


def _normalise(scores: list[float]) -> list[float]:
    """Normalise a list of scores to [0, 100]."""
    if not scores:
        return []
    max_score = max(scores)
    if max_score == 0.0:
        return [0.0] * len(scores)
    return [min((s / max_score) * 100.0, 100.0) for s in scores]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def rank_anomalies(
    anomalies: list[dict],
    reference_dt: datetime | None = None,
) -> list[PriorityItem]:
    """
    Score and rank a list of anomaly dicts.

    Parameters
    ----------
    anomalies:
        List of anomaly dicts, each with at minimum ``id``, ``artist_id``,
        ``category``, ``subtype``, and optionally ``estimated_recoverable``,
        ``confidence_score``, ``created_at``, ``sol_status``,
        ``sol_days_remaining``, and ``description``.
    reference_dt:
        "Now" for age calculations.  Defaults to ``datetime.now(timezone.utc)``.

    Returns
    -------
    List of :class:`PriorityItem` sorted by priority_score descending.
    """
    ref = reference_dt or datetime.now(timezone.utc)
    items: list[PriorityItem] = []

    for a in anomalies:
        category = str(a.get("category", "ROYALTY"))
        recoverable = float(
            a.get("estimated_recoverable")
            or _DEFAULT_RECOVERABLE.get(category.upper(), _GLOBAL_DEFAULT_RECOVERABLE)
        )
        confidence = float(a.get("confidence_score", 0.5) or 0.5)
        sol_status = str(a.get("sol_status", "UNKNOWN"))
        created_at = _parse_datetime(a.get("created_at"))
        threshold_adjustment = float(a.get("threshold_adjustment", 1.0) or 1.0)
        effort_adjustment = float(a.get("effort_adjustment", 1.0) or 1.0)

        score = _score_item(
            recoverable,
            confidence,
            sol_status,
            created_at,
            ref,
            threshold_adjustment=threshold_adjustment,
            effort_adjustment=effort_adjustment,
        )

        items.append(
            PriorityItem(
                item_id=str(a.get("id", "")),
                item_type="ANOMALY",
                action=ActionType.FILE_CLAIM,
                artist_id=str(a.get("artist_id", "")),
                category=category,
                subtype=str(a.get("subtype", "")),
                priority_score=score,
                estimated_recoverable=recoverable,
                confidence_score=confidence,
                sol_status=sol_status,
                sol_days_remaining=a.get("sol_days_remaining"),
                description=str(a.get("description", "")),
            )
        )

    # Normalise and rank
    raw_scores = [it.priority_score for it in items]
    normalised = _normalise(raw_scores)
    sorted_items = sorted(
        zip(items, normalised), key=lambda x: x[1], reverse=True
    )
    for rank, (item, norm) in enumerate(sorted_items, start=1):
        item.priority_rank = rank
        item.normalised_score = norm

    return [item for item, _ in sorted_items]


def rank_claims(
    claims: list[dict],
    reference_dt: datetime | None = None,
) -> list[PriorityItem]:
    """
    Score and rank in-flight claims to help prioritise follow-up actions.

    Parameters
    ----------
    claims:
        List of claim dicts with at minimum ``id``, ``artist_id``,
        ``claim_type``, ``status``, and optionally ``estimated_recoverable``
        (or derived from the anomaly), ``confidence_score``,
        ``created_at``, ``sol_status``, and ``sol_days_remaining``.

    Returns
    -------
    List of :class:`PriorityItem` sorted by priority descending.
    """
    ref = reference_dt or datetime.now(timezone.utc)
    items: list[PriorityItem] = []

    for c in claims:
        claim_type = str(c.get("claim_type", "ROYALTY"))
        category = str(c.get("category", claim_type))
        recoverable = float(
            c.get("estimated_recoverable")
            or _DEFAULT_RECOVERABLE.get(category.upper(), _GLOBAL_DEFAULT_RECOVERABLE)
        )
        confidence = float(c.get("confidence_score", 0.7) or 0.7)
        sol_status = str(c.get("sol_status", "UNKNOWN"))
        created_at = _parse_datetime(c.get("created_at"))
        threshold_adjustment = float(c.get("threshold_adjustment", 1.0) or 1.0)
        effort_adjustment = float(c.get("effort_adjustment", 1.0) or 1.0)

        score = _score_item(
            recoverable,
            confidence,
            sol_status,
            created_at,
            ref,
            threshold_adjustment=threshold_adjustment,
            effort_adjustment=effort_adjustment,
        )

        items.append(
            PriorityItem(
                item_id=str(c.get("id", "")),
                item_type="CLAIM",
                action=ActionType.ADVANCE_CLAIM,
                artist_id=str(c.get("artist_id", "")),
                category=category,
                subtype=str(c.get("claim_type", "")),
                priority_score=score,
                estimated_recoverable=recoverable,
                confidence_score=confidence,
                sol_status=sol_status,
                sol_days_remaining=c.get("sol_days_remaining"),
                description=str(c.get("description", "")),
                claim_status=str(c.get("status", "")),
            )
        )

    raw_scores = [it.priority_score for it in items]
    normalised = _normalise(raw_scores)
    sorted_items = sorted(
        zip(items, normalised), key=lambda x: x[1], reverse=True
    )
    for rank, (item, norm) in enumerate(sorted_items, start=1):
        item.priority_rank = rank
        item.normalised_score = norm

    return [item for item, _ in sorted_items]


def build_action_queue(
    anomalies: list[dict],
    claims: list[dict],
    reference_dt: datetime | None = None,
) -> list[dict]:
    """
    Merge ranked anomalies and ranked claims into a single unified priority queue.

    The unified queue can be surfaced as the artist's "to-do list" — each item
    has a clear recommended action, a priority rank, and an estimated recovery value.

    Parameters
    ----------
    anomalies:
        Open anomaly dicts (already classified with SOL metadata if available).
    claims:
        In-flight claim dicts.
    reference_dt:
        "Now" for age calculations.

    Returns
    -------
    List of action queue item dicts, sorted by priority (highest first).
    """
    ref = reference_dt or datetime.now(timezone.utc)
    ranked_anomalies = rank_anomalies(anomalies, reference_dt=ref)
    ranked_claims = rank_claims(claims, reference_dt=ref)

    all_items = [a.to_dict() for a in ranked_anomalies] + [c.to_dict() for c in ranked_claims]

    # Re-sort the merged list by normalised_score descending and reassign ranks
    all_items.sort(key=lambda x: x["normalised_score"], reverse=True)
    for rank, item in enumerate(all_items, start=1):
        item["priority_rank"] = rank

    return all_items
