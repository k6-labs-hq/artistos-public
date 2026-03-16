# Anomalies, Claims, and Recovery Domain

## Anomaly Endpoints
- GET /artists/{artist_id}/anomalies
- GET /anomalies/{anomaly_id}
- POST /artists/{artist_id}/anomalies/detect

## Claim Endpoints
- GET /artists/{artist_id}/claims
- GET /claims/{claim_id}
- POST /claims/{claim_id}/advance
- POST /claims/{claim_id}/evidence
- GET /claims/{claim_id}/evidence/export
- GET /claims/{claim_id}/evidence/verify
- POST /claims/{claim_id}/reconcile

## Recovery Endpoints
- GET /artists/{artist_id}/recovery/sol-status
- GET /artists/{artist_id}/recovery/rate-benchmark
- GET /artists/{artist_id}/recovery/audit-eligibility
- GET /artists/{artist_id}/recovery/recoupment
- GET /artists/{artist_id}/recovery/priority-queue

## Evidence Lifecycle
Detection -> claim draft -> evidence generation -> verification -> submission/escalation.
