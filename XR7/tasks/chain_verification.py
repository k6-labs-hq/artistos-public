"""Scheduled chain integrity verification tasks for evidence audit ledger.

SOC 2 CC7.2 Compliance: System monitoring must detect unauthorized data modifications.
This module implements continuous monitoring of the SHA-256 hash-chained audit ledger
to detect tampering, bit rot, or database compromise before evidence is used in legal proceedings.

Regulatory basis: Attorney trust requires proactive verification, not just reactive
verification on read. If tampering is detected during attorney evidence export, forensic
recovery of "when it happened" is impossible without scheduled verification history.

Architecture: Tenant-scoped verification jobs run daily. Each tenant's evidence chain
is verified independently. Verification failures trigger P0 alerts and block evidence serving.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import distinct, select
from sqlalchemy.orm import Session

from XR7.celery_app import celery_app
from XR7.core.integrity.evidence_crypto import verify_packet_integrity
from XR7.models.base import get_db
from XR7.models.claim import Claim
from xr7_common.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(
    name="xr7.chain_verification.verify_all_tenants",
    bind=True,
    max_retries=0,
    time_limit=3600,
)
def verify_all_tenants_chain_integrity_task(
    self, db: Session | None = None
) -> dict[str, int]:  # noqa: ANN001
    """Verify evidence chain integrity for all tenants with active claims.

    SOC 2 CC7.2: Daily per-tenant verification job detecting unauthorized modifications.

    Args:
        db: Optional database session (for testing). If None, uses get_db().

    Returns:
        dict with keys: tenants_checked, packets_verified, tampering_detected_count

    Alerts:
        - P0 alert fired for each tampering detection event
        - Alert includes: artist_id, claim_id, failed checks, packet hash, chain hash
        - Runbook: docs/operations/runbooks/chain-integrity-failure.md
    """
    logger.info(
        "chain_verification_sweep_starting",
        extra={
            "task_id": self.request.id if hasattr(self, "request") else "manual",
            "started_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    # Use provided session for testing, or get production session
    if db is None:
        db = next(get_db())
        should_close = True
    else:
        should_close = False

    try:
        # Get all unique artist_ids with claims that have evidence packets
        artist_ids = (
            db.execute(
                select(distinct(Claim.artist_id)).where(
                    Claim.evidence.isnot(None), Claim.deleted_at.is_(None)
                )
            )
            .scalars()
            .all()
        )

        tenants_checked = len(artist_ids)
        packets_verified = 0
        tampering_detected_count = 0

        for artist_id in artist_ids:
            result = verify_tenant_chain_integrity(db, artist_id)
            packets_verified += result["packets_verified"]
            tampering_detected_count += result["tampering_detected_count"]

            if result["tampering_detected_count"] > 0:
                logger.error(
                    "chain_verification_tenant_tampering_detected",
                    extra={
                        "artist_id": artist_id,
                        "packets_verified": result["packets_verified"],
                        "tampering_count": result["tampering_detected_count"],
                        "severity": "P0",
                        "security_event": "scheduled_chain_verification_failure",
                        "runbook": "docs/operations/runbooks/chain-integrity-failure.md",
                    },
                )

        logger.info(
            "chain_verification_sweep_completed",
            extra={
                "task_id": self.request.id if hasattr(self, "request") else "manual",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "tenants_checked": tenants_checked,
                "packets_verified": packets_verified,
                "tampering_detected_count": tampering_detected_count,
            },
        )

        return {
            "tenants_checked": tenants_checked,
            "packets_verified": packets_verified,
            "tampering_detected_count": tampering_detected_count,
        }

    finally:
        if should_close:
            db.close()


def verify_tenant_chain_integrity(db: Session, artist_id: str) -> dict[str, int]:
    """Verify all evidence packets for a single tenant.

    Args:
        db: Database session
        artist_id: Tenant identifier

    Returns:
        dict with keys: packets_verified, tampering_detected_count
    """
    claims = (
        db.query(Claim)
        .filter(
            Claim.artist_id == artist_id,
            Claim.evidence.isnot(None),
            Claim.deleted_at.is_(None),
        )
        .all()
    )

    packets_verified = 0
    tampering_detected_count = 0

    for claim in claims:
        if not isinstance(claim.evidence, dict):
            continue

        verification = verify_packet_integrity(claim.evidence)
        packets_verified += 1

        if not verification.get("valid"):
            tampering_detected_count += 1

            logger.error(
                "scheduled_chain_verification_tampering_detected",
                extra={
                    "claim_id": claim.id,
                    "artist_id": artist_id,
                    "checks": verification.get("checks"),
                    "packet_hash": verification.get("packet_hash"),
                    "prior_packet_hash": verification.get("prior_packet_hash"),
                    "chain_hash": verification.get("chain_hash"),
                    "signature_mode": verification.get("signature_mode"),
                    "severity": "P0",
                    "security_event": "scheduled_verification_failure",
                    "impact": "Evidence packet cannot be served to attorney until integrity restored",
                    "runbook": "docs/operations/runbooks/chain-integrity-failure.md",
                },
            )

    return {
        "packets_verified": packets_verified,
        "tampering_detected_count": tampering_detected_count,
    }
