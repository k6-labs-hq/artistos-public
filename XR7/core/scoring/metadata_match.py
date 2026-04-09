"""
Pure metadata-matching and confidence-scoring functions.

No DB, no ORM imports.  All inputs are plain Python primitives, making these
functions callable from n8n HTTP steps, LangGraph nodes, or unit tests without
any infrastructure setup.
"""

from __future__ import annotations

import math
from difflib import SequenceMatcher

# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------


def normalize_text(text: str | None) -> str:
    """Lowercase, keep only alphanumeric + spaces, collapse whitespace."""
    if not text:
        return ""
    cleaned = "".join(ch.lower() if ch.isalnum() or ch.isspace() else " " for ch in text)
    return " ".join(cleaned.split())


def text_similarity(a: str | None, b: str | None) -> float:
    """SequenceMatcher ratio of two normalised strings; returns 0.0 if either is empty."""
    aa = normalize_text(a)
    bb = normalize_text(b)
    if not aa or not bb:
        return 0.0
    return float(SequenceMatcher(None, aa, bb).ratio())


# ---------------------------------------------------------------------------
# Composite scoring
# ---------------------------------------------------------------------------


def metadata_triangulation_score(
    *,
    title_a: str | None,
    title_b: str | None,
    artist_a: str | None,
    artist_b: str | None,
    duration_ms_a: int | None,
    duration_ms_b: int | None,
    id_match: bool,
    context_match: bool,
) -> float:
    """Weighted composite match score in [0.0, 1.0].

    Weights
    -------
    - Title similarity:    35 %
    - Artist similarity:   20 %
    - Duration similarity: 15 %  (0.5 when either duration is absent)
    - ID match:            20 %
    - Context match:       10 %
    """
    title_score = text_similarity(title_a, title_b)
    artist_score = text_similarity(artist_a, artist_b)

    if duration_ms_a is None or duration_ms_b is None or duration_ms_a <= 0 or duration_ms_b <= 0:
        duration_score = 0.5
    else:
        delta = abs(duration_ms_a - duration_ms_b)
        duration_score = math.exp(-((delta / 1500.0) ** 2))

    score = (
        0.35 * title_score
        + 0.2 * artist_score
        + 0.15 * duration_score
        + 0.2 * (1.0 if id_match else 0.0)
        + 0.1 * (1.0 if context_match else 0.0)
    )
    return max(0.0, min(1.0, score))


def confidence_score(
    metadata_score: float,
    fingerprint_score: float,
    history_score: float,
    contract_score: float,
    conflict_penalty: float,
) -> float:
    """Logistic confidence score combining multiple evidence signals.

    Parameters correspond to the XR7 evidence pipeline stages; each is
    expected in the natural range for that signal (typically [0, 1]).
    Returns a probability in (0, 1).
    """
    linear = (
        1.6 * metadata_score
        + 1.8 * fingerprint_score
        + 0.8 * history_score
        + 0.9 * contract_score
        - 1.2 * conflict_penalty
    )
    return 1.0 / (1.0 + math.exp(-linear))
