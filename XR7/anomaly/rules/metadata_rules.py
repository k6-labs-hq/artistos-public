from __future__ import annotations

import logging
from typing import Callable

from XR7.ingestion.metadata_sources.models import ResolvedWork
from XR7.ingestion.metadata_sources.musicbrainz import normalize_isrc
from XR7.ingestion.metadata_sources.reconcile import StatementLine, reconcile_statement_lines

logger = logging.getLogger(__name__)

Resolver = Callable[[str], list[ResolvedWork]]

# Confidence is deliberately modest: external registries are incomplete, so every
# finding here is a lead to verify, never a quantified recovery. estimated_recoverable
# stays 0.0; the dollars on the affected work are reported as evidence only.
_CONFIDENCE = {
    "ISWC_MISMATCH": 0.70,
    "INVALID_ISRC_FORMAT": 0.80,
    "STATEMENT_MISSING_ISWC": 0.55,
    "PAYEE_NOT_CREDITED": 0.50,
    "ISRC_UNRESOLVED": 0.45,
    "NO_ISWC_ANYWHERE": 0.40,
}


def run_metadata_rules(
    artist_id: str,
    works: list[dict],
    events: list[dict],
    resolver: Resolver,
    max_lookups: int = 25,
    payee_name: str | None = None,
) -> list[dict]:
    """Cross-check catalog identifiers (ISRC/ISWC) against an external metadata source.

    ``works``: dicts with ``id``, ``title``, ``isrc``, ``iswc``.
    ``events``: dicts with ``work_id``, ``quantity``, ``unit_value`` (used for $ at stake).
    Lookups are capped at ``max_lookups`` distinct ISRCs, highest-earning first, because
    the source is rate limited (1 req/s). Lookup failures skip that work; they never raise.
    """
    earned: dict[str, float] = {}
    for e in events:
        wid = e.get("work_id")
        if wid:
            earned[wid] = earned.get(wid, 0.0) + float(e.get("quantity") or 0.0) * float(
                e.get("unit_value") or 0.0
            )

    findings: list[dict] = []
    candidates: list[tuple[dict, str]] = []
    for w in works:
        raw = (w.get("isrc") or "").strip()
        if not raw:
            continue
        code = normalize_isrc(raw)
        if code is None:
            findings.append(
                _finding(
                    artist_id, w, "INVALID_ISRC_FORMAT", "review", raw,
                    f"Catalog ISRC {raw!r} is not a valid ISRC; DSPs and societies cannot match it.",
                    earned.get(w["id"], 0.0), None, None,
                )
            )
            continue
        candidates.append((w, code))

    candidates.sort(key=lambda wc: earned.get(wc[0]["id"], 0.0), reverse=True)

    resolved: dict[str, list[ResolvedWork]] = {}
    for _, code in candidates[:max_lookups]:
        if code in resolved:
            continue
        try:
            resolved[code] = resolver(code)
        except Exception as exc:  # network/source failure must not break the audit
            logger.warning("metadata_lookup_failed", extra={"isrc": code, "error": str(exc)})

    for w, code in candidates:
        if code not in resolved:
            continue
        line = StatementLine(
            isrc=code,
            work_title=w.get("title"),
            iswc=w.get("iswc"),
            payee_name=payee_name,
            amount=round(earned.get(w["id"], 0.0), 2),
        )
        for f in reconcile_statement_lines([line], resolved.__getitem__):
            findings.append(
                _finding(
                    artist_id, w, f.code, f.severity, code, f.message,
                    f.amount_at_stake, f.evidence_url, f.source,
                )
            )
    return findings


def _finding(
    artist_id: str,
    work: dict,
    code: str,
    severity: str,
    isrc: str,
    message: str,
    amount: float,
    evidence_url: str | None,
    source: str | None,
) -> dict:
    return {
        "artist_id": artist_id,
        "category": "ROYALTY",
        "subtype": f"METADATA_{code}",
        "severity": "HIGH" if severity == "high" else "MEDIUM",
        "expected_amount": 0.0,
        "actual_amount": round(amount, 2),
        "estimated_recoverable": 0.0,
        "confidence_score": _CONFIDENCE.get(code, 0.4),
        "status": "OPEN",
        "description": message,
        "rule_id": f"METADATA_{code}",
        "rule_name": f"Metadata check: {code}",
        "identity_key": f"{work['id']}:{code}",
        "evidence": {
            "work_id": work["id"],
            "work_title": work.get("title"),
            "isrc": isrc,
            "catalog_iswc": work.get("iswc"),
            "earnings_on_work": round(amount, 2),
            "source": source,
            "source_url": evidence_url,
            "note": (
                "Lead from public metadata, not proof of unpaid royalties. Verify against "
                "the PRO/MLC work registration before filing a claim."
            ),
        },
    }
