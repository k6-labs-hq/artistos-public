from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Callable

from XR7.ingestion.metadata_sources.models import ResolvedWork

Resolver = Callable[[str], list[ResolvedWork]]


@dataclass(frozen=True)
class StatementLine:
    isrc: str | None
    work_title: str | None = None
    iswc: str | None = None
    payee_name: str | None = None
    amount: float = 0.0


@dataclass(frozen=True)
class MetadataFinding:
    # ISRC_UNRESOLVED | STATEMENT_MISSING_ISWC | ISWC_MISMATCH | NO_ISWC_ANYWHERE | PAYEE_NOT_CREDITED
    code: str
    severity: str  # review | high
    isrc: str | None
    message: str
    amount_at_stake: float
    evidence_url: str | None = None
    source: str | None = None


def _iswc_norm(value: str | None) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def _name_match(a: str, b: str) -> float:
    return SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()


def reconcile_statement_lines(
    lines: list[StatementLine], resolver: Resolver, payee_threshold: float = 0.8
) -> list[MetadataFinding]:
    """Compare statement identifiers against externally resolved metadata.

    Findings are leads for human/agent review, not proof of unpaid money:
    external sources are incomplete, and a mismatch can be the source's error.
    """
    findings: list[MetadataFinding] = []
    cache: dict[str, list[ResolvedWork]] = {}

    for line in lines:
        if not line.isrc:
            continue
        if line.isrc not in cache:
            cache[line.isrc] = resolver(line.isrc)
        works = cache[line.isrc]

        if not works:
            findings.append(
                MetadataFinding(
                    "ISRC_UNRESOLVED",
                    "review",
                    line.isrc,
                    "ISRC not linked to any work in the external source; recording-to-work link may be missing.",
                    line.amount,
                )
            )
            continue

        known_iswcs = {_iswc_norm(i): w for w in works for i in w.iswcs}
        stmt_iswc = _iswc_norm(line.iswc)
        first = works[0]

        if not known_iswcs:
            findings.append(
                MetadataFinding(
                    "NO_ISWC_ANYWHERE",
                    "review",
                    line.isrc,
                    f"Work '{first.work_title}' resolved but no ISWC is published for it.",
                    line.amount,
                    first.source_url,
                    first.source,
                )
            )
        elif not stmt_iswc:
            iswc = next(iter(known_iswcs))
            findings.append(
                MetadataFinding(
                    "STATEMENT_MISSING_ISWC",
                    "review",
                    line.isrc,
                    f"Statement line has no ISWC; source lists {iswc}.",
                    line.amount,
                    known_iswcs[iswc].source_url,
                    first.source,
                )
            )
        elif stmt_iswc not in known_iswcs:
            findings.append(
                MetadataFinding(
                    "ISWC_MISMATCH",
                    "high",
                    line.isrc,
                    f"Statement ISWC {line.iswc} differs from source ISWC(s) {sorted(known_iswcs)}.",
                    line.amount,
                    first.source_url,
                    first.source,
                )
            )

        if line.payee_name:
            writers = [c.name for w in works for c in w.contributors]
            if writers and max(_name_match(line.payee_name, n) for n in writers) < payee_threshold:
                findings.append(
                    MetadataFinding(
                        "PAYEE_NOT_CREDITED",
                        "review",
                        line.isrc,
                        f"Payee '{line.payee_name}' is not among credited writers {sorted(set(writers))}.",
                        line.amount,
                        first.source_url,
                        first.source,
                    )
                )
    return findings
