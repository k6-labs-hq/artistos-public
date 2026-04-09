from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.identity_match import (
    ArtistIdentityMatch,
    ArtistIdentityMatchAudit,
    IdentityConfidenceBand,
    IdentityDecisionStatus,
)
from XR7.models.statement import Statement
from XR7.models.work import Work


@dataclass(frozen=True)
class IdentityMatchResult:
    score: float
    band: IdentityConfidenceBand
    decision_status: IdentityDecisionStatus
    reason: str
    score_breakdown: dict[str, float]


def _norm(value: str | None) -> str:
    return str(value or "").strip().lower()


def _string_similarity(a: str | None, b: str | None) -> float:
    aa = _norm(a)
    bb = _norm(b)
    if not aa or not bb:
        return 0.0
    if aa == bb:
        return 1.0
    return float(SequenceMatcher(None, aa, bb).ratio())


def _set_overlap(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    intersect = len(left.intersection(right))
    denom = max(len(left), len(right))
    return float(intersect) / float(denom)


def _band_for_score(score: float) -> tuple[IdentityConfidenceBand, IdentityDecisionStatus, str]:
    if score >= 0.90:
        return (
            IdentityConfidenceBand.AUTO_ACCEPT,
            IdentityDecisionStatus.AUTO_ACCEPTED,
            "Auto-accepted identity match (>=0.90 confidence).",
        )
    if score >= 0.70:
        return (
            IdentityConfidenceBand.SOFT_CONFIRM,
            IdentityDecisionStatus.PENDING_SOFT_CONFIRM,
            "Soft confirmation required (0.70-0.89 confidence).",
        )
    return (
        IdentityConfidenceBand.REQUIRE_CONFIRMATION,
        IdentityDecisionStatus.PENDING_EXPLICIT_CONFIRM,
        "Explicit confirmation required (<0.70 confidence).",
    )


def _hash_chain(prev_hash: str | None, payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    raw = f"{prev_hash or 'GENESIS'}:{blob}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _artist_aliases(artist: Artist) -> set[str]:
    aliases = {_norm(artist.name)}
    for s in list(artist.stage_names or []):
        if s:
            aliases.add(_norm(str(s)))
    return {a for a in aliases if a}


def compute_identity_match(artist: Artist, statement_signals: dict[str, Any], works: list[Work]) -> IdentityMatchResult:
    stage_name_candidate = _norm(statement_signals.get("artist_name"))
    artist_aliases = _artist_aliases(artist)

    stage_score = 0.0
    if stage_name_candidate:
        stage_score = max(_string_similarity(alias, stage_name_candidate) for alias in artist_aliases) if artist_aliases else 0.0

    ipi_candidate = _norm(statement_signals.get("pro_writer_id"))
    ipi_known = _norm(artist.ipi_number)
    ipi_score = 1.0 if (ipi_candidate and ipi_known and ipi_candidate == ipi_known) else 0.0

    distributor_aliases = {_norm(v) for v in list(statement_signals.get("distributor_list") or []) if _norm(v)}
    artist_distributor_aliases = {_norm(v) for v in list(artist.stage_names or []) if _norm(v)}
    distributor_score = _set_overlap(distributor_aliases, artist_distributor_aliases)

    statement_isrcs = {_norm(v) for v in list(statement_signals.get("isrcs") or []) if _norm(v)}
    statement_iswcs = {_norm(v) for v in list(statement_signals.get("iswcs") or []) if _norm(v)}
    statement_upcs = {_norm(v) for v in list(statement_signals.get("upcs") or []) if _norm(v)}

    catalog_isrcs = {_norm(w.isrc) for w in works if _norm(w.isrc)}
    catalog_iswcs = {_norm(w.iswc) for w in works if _norm(w.iswc)}

    isrc_score = _set_overlap(statement_isrcs, catalog_isrcs)
    iswc_score = _set_overlap(statement_iswcs, catalog_iswcs)
    # UPC is currently sourced from statement metadata and used as consistency signal.
    upc_score = 1.0 if statement_upcs else 0.0

    score_breakdown = {
        "stage_name": stage_score,
        "pro_writer_id": ipi_score,
        "distributor_alias": distributor_score,
        "isrc": isrc_score,
        "iswc": iswc_score,
        "upc": upc_score,
    }

    score = (
        (stage_score * 0.35)
        + (ipi_score * 0.20)
        + (distributor_score * 0.15)
        + (isrc_score * 0.15)
        + (iswc_score * 0.10)
        + (upc_score * 0.05)
    )
    score = round(min(max(score, 0.0), 1.0), 4)

    band, decision_status, reason = _band_for_score(score)
    return IdentityMatchResult(
        score=score,
        band=band,
        decision_status=decision_status,
        reason=reason,
        score_breakdown=score_breakdown,
    )


def persist_identity_match(
    db: Session,
    artist: Artist,
    statement: Statement | None,
    statement_signals: dict[str, Any],
) -> ArtistIdentityMatch:
    works = db.query(Work).filter(Work.artist_id == artist.id).all()
    result = compute_identity_match(artist, statement_signals, works)

    prior = (
        db.query(ArtistIdentityMatch)
        .filter(ArtistIdentityMatch.artist_id == artist.id)
        .order_by(ArtistIdentityMatch.created_at.desc())
        .first()
    )

    payload = {
        "artist_id": artist.id,
        "statement_id": statement.id if statement else None,
        "score": result.score,
        "band": result.band.value,
        "decision_status": result.decision_status.value,
        "signals": statement_signals,
        "score_breakdown": result.score_breakdown,
    }
    chain_hash = _hash_chain(prior.chain_hash if prior else None, payload)

    record = ArtistIdentityMatch(
        artist_id=artist.id,
        statement_id=statement.id if statement else None,
        confidence_score=result.score,
        confidence_band=result.band,
        decision_status=result.decision_status,
        decision_reason=result.reason,
        decision_actor="system:auto_match",
        decision_at=datetime.now(timezone.utc) if result.decision_status == IdentityDecisionStatus.AUTO_ACCEPTED else None,
        matched_profile=statement_signals,
        score_breakdown=result.score_breakdown,
        chain_hash=chain_hash,
    )
    db.add(record)
    db.flush()

    audit_payload = {
        "event": "identity_match_computed",
        "decision_status": record.decision_status,
        "confidence_band": record.confidence_band,
        "confidence_score": record.confidence_score,
    }
    audit_hash = _hash_chain(None, audit_payload)
    db.add(
        ArtistIdentityMatchAudit(
            match_id=record.id,
            action="AUTO_MATCH",
            actor="system:auto_match",
            payload=audit_payload,
            chain_hash=audit_hash,
        )
    )
    db.commit()
    db.refresh(record)
    return record


def apply_identity_decision(
    db: Session,
    match: ArtistIdentityMatch,
    decision: IdentityDecisionStatus,
    actor: str,
    reason: str,
) -> ArtistIdentityMatch:
    if decision not in {IdentityDecisionStatus.CONFIRMED, IdentityDecisionStatus.REJECTED}:
        raise ValueError("Decision must be CONFIRMED or REJECTED")

    match.decision_status = decision
    match.decision_actor = actor
    match.decision_reason = reason
    match.decision_at = datetime.now(timezone.utc)

    prior_audit = (
        db.query(ArtistIdentityMatchAudit)
        .filter(ArtistIdentityMatchAudit.match_id == match.id)
        .order_by(ArtistIdentityMatchAudit.created_at.desc())
        .first()
    )
    payload = {
        "decision": decision.value,
        "reason": reason,
        "match_id": match.id,
    }
    chain_hash = _hash_chain(prior_audit.chain_hash if prior_audit else None, payload)
    db.add(
        ArtistIdentityMatchAudit(
            match_id=match.id,
            action="DECISION",
            actor=actor,
            payload=payload,
            chain_hash=chain_hash,
        )
    )

    db.commit()
    db.refresh(match)
    return match
