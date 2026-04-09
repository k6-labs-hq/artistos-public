"""
Pure confidence-band classification.

No DB, no imports from XR7 models/services.  Call this from n8n, LangGraph
nodes, unit tests, or any other context without a SQLAlchemy session.
"""
from __future__ import annotations

#: Threshold above which an anomaly is considered high-confidence.
HIGH: float = 0.90

#: Threshold above which an anomaly is considered medium-confidence.
MEDIUM: float = 0.70


def classify_band(confidence: float) -> str:
    """Map a confidence score in [0, 1] to a routing band.

    Returns
    -------
    ``"high"``   — confidence >= 0.90  → auto-case creation eligible
    ``"medium"`` — confidence >= 0.70  → analyst review queue
    ``"low"``    — confidence <  0.70  → watchlist / unmatched queue
    """
    if confidence >= HIGH:
        return "high"
    if confidence >= MEDIUM:
        return "medium"
    return "low"
