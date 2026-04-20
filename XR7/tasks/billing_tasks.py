"""Billing task functions for Celery workers."""

# Retry schedule: 5min, 30min, 2hr, 24hr
DISBURSEMENT_RETRY_DELAYS = [300, 1800, 7200, 86400]


def _calculate_retry_countdown(attempt: int) -> int:
    """Calculate retry countdown based on attempt number using exponential backoff.
    
    Args:
        attempt: Retry attempt number (0-indexed)
        
    Returns:
        Delay in seconds before next retry
    """
    return DISBURSEMENT_RETRY_DELAYS[min(attempt, len(DISBURSEMENT_RETRY_DELAYS) - 1)]


def retry_failed_disbursement(disbursement_id: str) -> None:
    """Retry a failed disbursement.
    
    Args:
        disbursement_id: ID of disbursement to retry
    """
    pass


def scan_stuck_disbursements() -> None:
    """Scan for and retry stuck disbursements."""
    pass
