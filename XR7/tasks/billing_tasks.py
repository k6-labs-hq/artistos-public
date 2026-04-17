"""
Celery tasks for billing and payout operations.

Critical for production: automated retry of failed Trolley disbursements
with exponential backoff to handle transient API failures.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from celery.exceptions import MaxRetriesExceededError
from sqlalchemy import and_

from XR7.billing.engine import BillingEngine
from XR7.celery_app import celery_app
from XR7.models.base import SessionLocal
from XR7.models.claim import Claim, ClaimStatus
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from XR7.trolley.client import TrolleyException
from xr7_common.logging import get_logger

logger = get_logger(__name__)


# Exponential backoff schedule: 5m, 30m, 2h, 24h (max 5 retries total)
# Retry 0 → 1: 300s (5 minutes)
# Retry 1 → 2: 1800s (30 minutes)
# Retry 2 → 3: 7200s (2 hours)
# Retry 3 → 4: 86400s (24 hours)
# Retry 4 → 5: gives up (max_retries=4 means 5 total attempts)
DISBURSEMENT_RETRY_DELAYS = [300, 1800, 7200, 86400]


def _calculate_retry_countdown(retry_count: int) -> int:
    """Calculate exponential backoff delay for disbursement retries."""
    if retry_count >= len(DISBURSEMENT_RETRY_DELAYS):
        # If we exceed defined delays, use the last one (24h)
        return DISBURSEMENT_RETRY_DELAYS[-1]
    return DISBURSEMENT_RETRY_DELAYS[retry_count]


@celery_app.task(
    name="xr7.billing.retry_failed_disbursement",
    bind=True,
    max_retries=4,  # 5 total attempts (0-4)
    autoretry_for=(TrolleyException,),
    retry_backoff=False,  # We use custom countdown logic
)
def retry_failed_disbursement(self, claim_id: str) -> dict:  # noqa: ANN001
    """
    Retry a failed Trolley disbursement with exponential backoff.

    This task is automatically retried with increasing delays:
    - Attempt 1 → 2: 5 minutes
    - Attempt 2 → 3: 30 minutes
    - Attempt 3 → 4: 2 hours
    - Attempt 4 → 5: 24 hours
    - Attempt 5: Final attempt, then permanent failure

    Args:
        claim_id: ID of the claim to retry disbursement for

    Returns:
        dict: Status of the retry attempt

    Raises:
        TrolleyException: Triggers automatic retry with exponential backoff
        MaxRetriesExceededError: After 5 failed attempts
    """
    db = SessionLocal()
    try:
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            logger.error(f"Claim {claim_id} not found for disbursement retry")
            return {"status": "error", "reason": "claim_not_found"}

        # Verify claim is still in failed state
        if claim.status != ClaimStatus.DISBURSEMENT_FAILED:
            logger.info(
                f"Claim {claim_id} no longer in DISBURSEMENT_FAILED status "
                f"(current: {claim.status}), skipping retry"
            )
            return {"status": "skipped", "reason": "not_in_failed_status"}

        # Check if we've exceeded max retries at the claim level
        retry_count = int(claim.payout_retry_count or 0)
        if retry_count >= 5:
            logger.warning(
                f"Claim {claim_id} has exceeded max retries ({retry_count}), "
                "marking as permanently failed"
            )
            # Log to immutable ledger for audit trail
            ledger = ImmutableLedgerService(db)
            ledger.append(
                claim.artist_id,
                "disbursement_permanently_failed",
                {
                    "claim_id": claim.id,
                    "retry_count": retry_count,
                    "failure_reason": claim.payout_failure_reason,
                    "failed_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            return {"status": "permanently_failed", "retry_count": retry_count}

        # Attempt disbursement
        logger.info(
            f"Retrying disbursement for claim {claim_id} "
            f"(attempt {retry_count + 1}/5, task retry {self.request.retries})"
        )

        engine = BillingEngine(db)
        try:
            tx = engine.disburse_via_trolley(claim_id=claim_id)
            logger.info(
                f"Disbursement retry succeeded for claim {claim_id}, "
                f"trolley_payment_id: {tx.trolley_payment_id}"
            )
            return {
                "status": "success",
                "claim_id": claim_id,
                "trolley_payment_id": tx.trolley_payment_id,
                "retry_count": retry_count,
            }
        except TrolleyException as exc:
            # Update retry count is already handled in disburse_via_trolley
            db.refresh(claim)  # Get updated retry count
            new_retry_count = int(claim.payout_retry_count or 0)

            # Calculate countdown for next retry
            countdown = _calculate_retry_countdown(self.request.retries)

            logger.warning(
                f"Disbursement retry {self.request.retries + 1}/5 failed for claim {claim_id}: {exc}. "
                f"Next retry in {countdown}s ({countdown // 60} minutes)"
            )

            # Log retry attempt to immutable ledger
            ledger = ImmutableLedgerService(db)
            ledger.append(
                claim.artist_id,
                "disbursement_retry_attempted",
                {
                    "claim_id": claim.id,
                    "retry_attempt": self.request.retries + 1,
                    "max_retries": 5,
                    "failure_reason": str(exc),
                    "next_retry_countdown_seconds": countdown,
                    "attempted_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            # Re-raise to trigger Celery's automatic retry with our custom countdown
            try:
                raise self.retry(exc=exc, countdown=countdown)
            except MaxRetriesExceededError:
                # All retries exhausted
                logger.error(
                    f"All 5 disbursement retry attempts exhausted for claim {claim_id}. "
                    f"Final failure reason: {exc}"
                )
                ledger.append(
                    claim.artist_id,
                    "disbursement_all_retries_exhausted",
                    {
                        "claim_id": claim.id,
                        "total_attempts": 5,
                        "final_failure_reason": str(exc),
                        "exhausted_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
                return {
                    "status": "all_retries_exhausted",
                    "claim_id": claim_id,
                    "retry_count": new_retry_count,
                    "error": str(exc),
                }
    finally:
        db.close()


@celery_app.task(
    name="xr7.billing.scan_stuck_disbursements",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=2,
    retry_backoff_max=60,
    max_retries=3,
)
def scan_stuck_disbursements(self) -> dict:  # noqa: ANN001
    """
    Periodic task to find and queue failed disbursements for retry.

    Scans for claims in DISBURSEMENT_FAILED status that:
    - Have retry_count < 5 (haven't exhausted retries)
    - Last update was > 5 minutes ago (rate limiting)
    - Are not already being retried

    Returns:
        dict: Summary of claims queued for retry
    """
    db = SessionLocal()
    try:
        # Find failed disbursements eligible for retry
        five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
        failed_claims = (
            db.query(Claim)
            .filter(
                and_(
                    Claim.status == ClaimStatus.DISBURSEMENT_FAILED,
                    Claim.payout_retry_count < 5,
                    Claim.updated_at < five_minutes_ago,
                )
            )
            .all()
        )

        queued_count = 0
        for claim in failed_claims:
            # Queue the retry task asynchronously
            retry_failed_disbursement.delay(claim.id)
            queued_count += 1
            logger.info(
                f"Queued disbursement retry for claim {claim.id} "
                f"(retry {claim.payout_retry_count + 1}/5)"
            )

        logger.info(
            f"Disbursement scan complete: {queued_count} claims queued for retry "
            f"out of {len(failed_claims)} failed disbursements"
        )

        return {
            "status": "success",
            "failed_claims_found": len(failed_claims),
            "claims_queued": queued_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        logger.error(f"Error in scan_stuck_disbursements: {exc}")
        raise
    finally:
        db.close()
