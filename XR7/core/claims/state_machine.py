"""
Claim state-machine rules and category mappings.

Pure module: imports only from XR7.models.claim (an enum, no DB connection).
Safe to call from n8n, LangGraph nodes, or unit tests without a session.
"""
from __future__ import annotations

from XR7.models.claim import ClaimStatus

# ---------------------------------------------------------------------------
# State-transition table
# ---------------------------------------------------------------------------

#: Legal forward transitions in the claims lifecycle.
TRANSITIONS: dict[ClaimStatus, ClaimStatus] = {
    ClaimStatus.IDENTIFIED: ClaimStatus.PREPARED,
    # SUBMITTED is kept as an explicit intermediate state for compatibility
    # with existing dashboard and recovery workflows.
    ClaimStatus.PREPARED:  ClaimStatus.SUBMITTED,
    ClaimStatus.SUBMITTED: ClaimStatus.FILED,
    ClaimStatus.FILED:     ClaimStatus.IN_REVIEW,
    ClaimStatus.IN_REVIEW: ClaimStatus.ACCEPTED,
    ClaimStatus.ACCEPTED:  ClaimStatus.PAID,
    ClaimStatus.PAID:      ClaimStatus.CLOSED,
}

# ---------------------------------------------------------------------------
# Category → contract-type mapping
# ---------------------------------------------------------------------------

_CATEGORY_TO_CONTRACT_TYPE: dict[str, str] = {
    "ROYALTY":  "LABEL",
    "TOURING":  "TOURING",
    "MERCH":    "MERCH",
    "SYNC":     "SYNC",
    "PLATFORM": "LABEL",
    "BRAND":    "BRAND",
    "GRANT":    "GRANT",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def next_status(current: ClaimStatus) -> ClaimStatus:
    """Return the next legal status for *current*, or raise ``ValueError``."""
    result = TRANSITIONS.get(current)
    if result is None:
        raise ValueError(f"No forward transition defined for status: {current!r}")
    return result


def contract_type_for_category(category: str | None) -> str | None:
    """Map an anomaly category string to its relevant contract type.

    Returns ``None`` when *category* is ``None`` or unmapped, signalling that
    all contract types should be included in the evidence packet.
    """
    if category is None:
        return None
    return _CATEGORY_TO_CONTRACT_TYPE.get(str(category))
