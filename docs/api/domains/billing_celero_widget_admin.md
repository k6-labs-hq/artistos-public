# Billing, Celero, Widget, Admin Domain

## Billing
- GET /artists/{artist_id}/billing
- GET /artists/{artist_id}/invoices

## Celero MoR
- POST /artists/{artist_id}/celero/register
- GET /artists/{artist_id}/celero/status
- POST /artists/{artist_id}/celero/charge
- POST /artists/{artist_id}/celero/disburse
- POST /celero/webhook

## Widget
- POST /widget/register
- POST /widget/verify
- POST /widget/estimate
- POST /widget/claim
- GET /widget/leads

## Admin + Review Queue
- /admin/* endpoints for operations visibility
- /review-queue/* endpoints for analyst decisions and threshold checks
