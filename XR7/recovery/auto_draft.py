"""Auto-draft + auto-promote claims from detected anomalies.

Wired into the post-detection pipeline so every persisted anomaly with
enough evidence becomes a Claim row the operator can preview and file
from `/ops`. Without this the dashboard surfaced anomalies but the
filing queue stayed empty — operators had no way to walk an anomaly
through the recovery pipeline.

Auto-promotion is conservative: a claim only advances IDENTIFIED →
PREPARED automatically when we can resolve the payer and the recoverable
clears a small floor. The /ops Advance button is the manual escape hatch
for the cases this helper can't handle.

See PR thread for the design — earlier ingestion-time auto-draft fired
only for the first anomaly per artist on the single-file upload path,
which made batch BMI PDF uploads silently no-op.
"""

from __future__ import annotations

import json

from sqlalchemy.orm import Session

from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.recovery.orchestrator import ClaimsOrchestrator
from XR7.recovery.payer_config import PAYER_CONFIGS
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# Minimum estimated_recoverable below which we don't auto-promote a claim
# to PREPARED. Below $1 the claim isn't worth filing — operator can still
# advance it manually from /ops if they disagree.
_AUTO_PROMOTE_RECOVERABLE_FLOOR = 1.0


def resolve_payer_for_anomaly(
    anomaly: Anomaly, artist: Artist | None
) -> str | None:
    """Pick a canonical payer id for an anomaly.

    Resolution order:
      1. ``feature_snapshot.evidence.worst_payer`` — the rule itself
         identified a payer (e.g. high-retroactive-ratio rule).
      2. ``artist.pro_affiliations`` when there's exactly one — the artist
         only receives statements from one payer, so the gap must be
         against them.
      3. None — operator must set the payer manually from /ops.

    The conservative single-affiliation gate matters: an artist with
    BMI + ASCAP could have a missing-payment gap in either, and guessing
    sends our dispute to the wrong door. Better to leave the claim as
    IDENTIFIED until a human picks.
    """
    if anomaly.feature_snapshot:
        try:
            parsed = json.loads(anomaly.feature_snapshot)
            worst_payer = (parsed.get("evidence") or {}).get("worst_payer")
            if isinstance(worst_payer, str) and worst_payer.strip():
                normalised = worst_payer.strip().upper()
                if normalised in PAYER_CONFIGS:
                    return normalised
        except (TypeError, ValueError):
            pass

    if artist is not None:
        affiliations = [
            p.strip().upper()
            for p in (artist.pro_affiliations or [])
            if isinstance(p, str) and p.strip()
        ]
        known = [p for p in affiliations if p in PAYER_CONFIGS]
        if len(known) == 1:
            return known[0]

    return None


def auto_draft_and_promote(
    db: Session, anomaly: Anomaly
) -> Claim | None:
    """Ensure a Claim exists for ``anomaly`` and promote when filable.

    Idempotent — safe to call repeatedly. If a Claim already exists for
    the anomaly_id we leave it alone (operator may have advanced it
    further; we don't want to overwrite their state).

    Returns the Claim row (created or pre-existing) or None when we
    decline to draft (no payer resolvable, recoverable too low).
    """
    existing = (
        db.query(Claim)
        .filter(Claim.anomaly_id == anomaly.id, Claim.deleted_at.is_(None))
        .first()
    )
    if existing is not None:
        return existing

    artist = db.query(Artist).filter(Artist.id == anomaly.artist_id).first()
    payer = resolve_payer_for_anomaly(anomaly, artist)
    recoverable = float(anomaly.estimated_recoverable or 0.0)

    if recoverable < _AUTO_PROMOTE_RECOVERABLE_FLOOR:
        # Skip the draft entirely — sub-dollar gaps aren't worth a claim
        # row (and clutter /ops). Operator can re-trigger detection if a
        # later upload pushes the figure above the floor.
        return None

    orchestrator = ClaimsOrchestrator(db)
    try:
        claim = orchestrator.create_claim(
            anomaly_id=anomaly.id,
            claim_type="AUTO_DRAFT",
            payer_name=payer,
        )
    except Exception:  # noqa: BLE001
        logger.exception(
            "auto-draft create_claim failed",
            extra={"anomaly_id": anomaly.id, "artist_id": anomaly.artist_id},
        )
        return None

    # Auto-promote IDENTIFIED → PREPARED only when we have the payer
    # the dispute pipeline needs. Without payer_name, file-via-email
    # 409s — promoting prematurely would hand the operator a row they
    # can click but not actually send.
    if payer:
        try:
            orchestrator.advance_claim(claim.id)
            db.refresh(claim)
        except Exception:  # noqa: BLE001
            logger.exception(
                "auto-draft advance_claim failed",
                extra={"claim_id": claim.id, "anomaly_id": anomaly.id},
            )

    return claim
