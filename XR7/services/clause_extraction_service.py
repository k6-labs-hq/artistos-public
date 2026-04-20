"""Contract clause extraction and highlighting service.

Feature #6: Contract ingestion improvements (OCR + clause highlighting)

Extracts and highlights actionable clauses from music contracts:
- Rate clauses (royalty percentages, streaming rates)
- Recoupment terms (advance recoupment, expense allocation)
- Audit rights (inspection rights, lookback periods)

Returns confidence scores and low-confidence warnings for manual review.
"""

from __future__ import annotations

import re
from typing import TypedDict


class ClauseMatch(TypedDict):
    """Represents a single clause match in the contract text."""

    clause_type: str  # "rate", "recoupment", "audit_right"
    text: str  # The matched text span
    start_pos: int  # Character position in original text
    end_pos: int  # Character position in original text
    confidence: float  # 0.0 to 1.0
    metadata: dict  # Additional context (e.g., extracted percentage)


# Regex patterns for contract clause detection
# These patterns target common music industry contract language

RATE_PATTERNS = [
    # "15% of net receipts", "20 percent royalty", "50/50 split"
    (
        r"(\d+(?:\.\d+)?)\s*(?:%|percent|pct)\s+(?:of\s+)?(?:net\s+)?(?:receipts?|revenues?|streaming|mechanicals?|performance)",
        0.85,
    ),
    (r"(\d+/\d+)\s+split", 0.90),
    (r"royalty\s+rate\s+of\s+(\d+(?:\.\d+)?)\s*(?:%|percent)", 0.95),
]

RECOUPMENT_PATTERNS = [
    # "recoupable advance", "recoup from royalties", "unrecouped balance"
    (r"recoupable\s+advance(?:\s+of\s+\$?[\d,]+)?", 0.90),
    (r"recoup(?:ed|able|ment)?\s+(?:from|against)\s+(?:artist\s+)?royalt(?:y|ies)", 0.85),
    (r"unrecouped\s+balance", 0.90),
    (r"advance\s+shall\s+be\s+recouped", 0.85),
]

AUDIT_RIGHT_PATTERNS = [
    # "audit rights", "inspect books and records", "once per year"
    (r"audit\s+rights?", 0.85),
    (r"inspect\s+(?:the\s+)?books?\s+and\s+records?", 0.80),
    (r"(?:once|twice|two\s+times?)\s+per\s+(?:year|calendar\s+year|twelve-month\s+period)", 0.75),
    (r"accountant\s+may\s+inspect", 0.75),
    (r"right\s+to\s+examine\s+records?", 0.80),
]


def extract_clauses(text: str) -> list[ClauseMatch]:
    """
    Extract and highlight actionable clauses from contract text.

    Searches for:
    - Rate clauses (royalty percentages, splits)
    - Recoupment terms (advance recoupment language)
    - Audit rights (inspection rights, frequency)

    Args:
        text: Contract text (from PDF extraction or OCR)

    Returns:
        List of ClauseMatch dicts with type, text, position, and confidence

    Example:
        >>> text = "Artist shall receive 15% of net streaming revenues."
        >>> clauses = extract_clauses(text)
        >>> clauses[0]["clause_type"]
        'rate'
        >>> clauses[0]["confidence"]
        0.85
    """
    matches: list[ClauseMatch] = []

    # Search for rate clauses
    for pattern, confidence in RATE_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            # Extract surrounding context (up to 100 chars before/after)
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end]

            matches.append(
                {
                    "clause_type": "rate",
                    "text": context,
                    "start_pos": match.start(),
                    "end_pos": match.end(),
                    "confidence": confidence,
                    "metadata": {
                        "matched_value": match.group(0),
                        "pattern": pattern,
                    },
                }
            )

    # Search for recoupment clauses
    for pattern, confidence in RECOUPMENT_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end]

            matches.append(
                {
                    "clause_type": "recoupment",
                    "text": context,
                    "start_pos": match.start(),
                    "end_pos": match.end(),
                    "confidence": confidence,
                    "metadata": {
                        "matched_value": match.group(0),
                        "pattern": pattern,
                    },
                }
            )

    # Search for audit right clauses
    for pattern, confidence in AUDIT_RIGHT_PATTERNS:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end]

            matches.append(
                {
                    "clause_type": "audit_right",
                    "text": context,
                    "start_pos": match.start(),
                    "end_pos": match.end(),
                    "confidence": confidence,
                    "metadata": {
                        "matched_value": match.group(0),
                        "pattern": pattern,
                    },
                }
            )

    # Sort by position in document
    matches.sort(key=lambda m: m["start_pos"])

    # Deduplicate overlapping matches (keep highest confidence)
    deduped: list[ClauseMatch] = []
    for match in matches:
        # Check if this match overlaps with any previous match
        overlaps = False
        for prev in deduped:
            if match["start_pos"] <= prev["end_pos"] and match["end_pos"] >= prev["start_pos"]:
                # Overlaps - keep higher confidence match
                if match["confidence"] > prev["confidence"]:
                    deduped.remove(prev)
                    deduped.append(match)
                overlaps = True
                break

        if not overlaps:
            deduped.append(match)

    return deduped


def flag_low_confidence_review(clauses: list[ClauseMatch], threshold: float = 0.80) -> list[str]:
    """
    Generate review warnings for low-confidence clause extractions.

    Args:
        clauses: List of extracted clauses
        threshold: Confidence threshold below which to flag for review (default: 0.80)

    Returns:
        List of warning messages for manual review

    Example:
        >>> warnings = flag_low_confidence_review(clauses, threshold=0.85)
        >>> if warnings:
        ...     print(f"Manual review needed: {len(warnings)} low-confidence clauses")
    """
    warnings = []

    for clause in clauses:
        if clause["confidence"] < threshold:
            warnings.append(
                f"Low confidence ({clause['confidence']:.2f}) on {clause['clause_type']} clause "
                f"at position {clause['start_pos']}: '{clause['metadata']['matched_value']}'"
            )

    return warnings
