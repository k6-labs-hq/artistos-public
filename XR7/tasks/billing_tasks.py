DISBURSEMENT_RETRY_DELAYS = [60, 300, 900]
def _calculate_retry_countdown(attempt):
    return DISBURSEMENT_RETRY_DELAYS[min(attempt, len(DISBURSEMENT_RETRY_DELAYS) - 1)]
def retry_failed_disbursement(disbursement_id):
    pass
def scan_stuck_disbursements():
    pass
