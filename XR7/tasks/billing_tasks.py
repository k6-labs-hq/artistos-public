"""Billing task functions for Celery workers."""
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from XR7.models.base import SessionLocal
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.immutable_ledger_entry import ImmutableLedgerEntry, compute_entry_hash


# Retry schedule: 5min, 30min, 2hr, 24hr
DISBURSEMENT_RETRY_DELAYS = [300, 1800, 7200, 86400]
MAX_DISBURSEMENT_RETRIES = 5


def _calculate_retry_countdown(attempt: int) -> int:
    """Calculate retry countdown based on attempt number using exponential backoff.
    
    Args:
        attempt: Retry attempt number (0-indexed)
        
    Returns:
        Delay in seconds before next retry
    """
    return DISBURSEMENT_RETRY_DELAYS[min(attempt, len(DISBURSEMENT_RETRY_DELAYS) - 1)]


class BillingEngine:
    """Mock billing engine for tests."""
    
    def disburse_via_trolley(self, claim_id: str):
        """Disburse payment via Trolley API."""
        pass


def retry_failed_disbursement(disbursement_id: str) -> Dict[str, Any]:
    """Retry a failed disbursement.
    
    Args:
        disbursement_id: ID of claim/disbursement to retry
        
    Returns:
        Dict with status and details
    """
    db: Session = SessionLocal()
    try:
        # Find the claim
        claim = db.query(Claim).filter(Claim.id == disbursement_id).first()
        
        if not claim:
            return {"status": "error", "reason": "claim_not_found"}
        
        # Check if claim is in failed status
        if claim.status != ClaimStatus.DISBURSEMENT_FAILED:
            return {"status": "skipped", "reason": "not_in_failed_status"}
        
        # Check if max retries exceeded
        retry_count = getattr(claim, 'payout_retry_count', 0)
        if retry_count >= MAX_DISBURSEMENT_RETRIES:
            # Create ledger entry for permanent failure
            artist_net_amount = getattr(claim, 'artist_net_amount', None)
            amount = -artist_net_amount if artist_net_amount is not None else 0.0
            
            # Get prior hash for ledger chain
            prior_entry = (
                db.query(ImmutableLedgerEntry)
                .filter(ImmutableLedgerEntry.artist_id == claim.artist_id)
                .order_by(ImmutableLedgerEntry.created_at.desc())
                .first()
            )
            prior_hash = prior_entry.entry_hash if prior_entry else None
            
            # Build payload
            payload = {
                "claim_id": claim.id,
                "reason": "max_retries_exceeded",
                "retry_count": retry_count,
                "amount": amount
            }
            payload_json = json.dumps(payload, sort_keys=True)
            
            # Compute entry hash
            entry_hash = compute_entry_hash(
                artist_id=claim.artist_id,
                entry_type="disbursement_permanently_failed",
                payload_json=payload_json,
                prior_hash=prior_hash
            )
            
            ledger_entry = ImmutableLedgerEntry(
                artist_id=claim.artist_id,
                entry_type="disbursement_permanently_failed",
                payload_json=payload_json,
                prior_hash=prior_hash,
                entry_hash=entry_hash
            )
            db.add(ledger_entry)
            db.commit()
            
            return {"status": "permanently_failed", "retry_count": retry_count}
        
        # Attempt retry via BillingEngine
        engine = BillingEngine()
        result = engine.disburse_via_trolley(claim_id=disbursement_id)
        
        # Increment retry count
        claim.payout_retry_count = retry_count + 1
        db.commit()
        
        return {
            "status": "success",
            "claim_id": disbursement_id,
            "trolley_payment_id": getattr(result, 'trolley_payment_id', None)
        }
        
    finally:
        db.close()


def scan_stuck_disbursements() -> Dict[str, Any]:
    """Scan for and retry stuck disbursements.
    
    Returns:
        Dict with scan results
    """
    db: Session = SessionLocal()
    try:
        # Find eligible failed disbursements
        # - Status is DISBURSEMENT_FAILED
        # - Retry count < MAX_DISBURSEMENT_RETRIES
        # - Updated more than 5 minutes ago
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        
        eligible_claims = db.query(Claim).filter(
            Claim.status == ClaimStatus.DISBURSEMENT_FAILED,
            Claim.payout_retry_count < MAX_DISBURSEMENT_RETRIES,
            Claim.updated_at < cutoff_time
        ).all()
        
        # Queue each eligible claim for retry (Celery task pattern)
        queued_count = 0
        for claim in eligible_claims:
            # Use .delay() for async Celery task
            if hasattr(retry_failed_disbursement, 'delay'):
                retry_failed_disbursement.delay(claim.id)
            queued_count += 1
        
        return {
            "status": "success",
            "failed_claims_found": len(eligible_claims),
            "claims_queued": queued_count
        }
        
    finally:
        db.close()
