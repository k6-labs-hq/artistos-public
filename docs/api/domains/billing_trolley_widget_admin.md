# Billing, Trolley, Widget, Admin Domain

## Billing
- GET /artists/{artist_id}/billing
- GET /artists/{artist_id}/invoices

## Trolley Payouts
- POST /artists/{artist_id}/trolley/recipient
- GET /artists/{artist_id}/trolley/widget-url
- GET /artists/{artist_id}/trolley/status
- POST /claims/{claim_id}/remittance
- POST /claims/{claim_id}/disburse
- POST /webhooks/trolley

## Widget
- POST /widget/register
- POST /widget/verify
- POST /widget/estimate
- POST /widget/claim
- GET /widget/leads

## Admin + Review Queue
- /admin/* endpoints for operations visibility
- /review-queue/* endpoints for analyst decisions and threshold checks
