# Authentication and Authorization

XR7 uses header-based access controls for operational and privileged endpoints.

## Header Patterns
- X-Admin-Key: admin console endpoints.
- Analyst API keys + analyst identity headers for review queue workflows.
- Team/member scoped headers for artist-collaboration routes.

## Sensitive Endpoint Guidance
Apply strict auth checks for:
- payout/disbursement operations
- escalation decisions and legal packets
- review queue decisions
- admin-wide listings and audit logs

## Webhook Security
Celero webhook endpoint should be protected with configured webhook secret validation and signature checks.

## Operational Recommendation
- Rotate API keys regularly.
- Keep keys in environment variables or secure secret stores.
- Enable immutable ledger logging for all privileged actions.
