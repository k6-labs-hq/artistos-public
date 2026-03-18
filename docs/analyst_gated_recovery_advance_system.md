# Analyst-Gated Recovery Advance System

This document describes the internal two-step approval workflow for recovery advances.

## Overview

The system introduces four internal tables:

- `advance_opportunities`: machine-generated candidates created from high-confidence open anomaly/claim signals.
- `advance_approvals`: immutable analyst and executive decisions.
- `advance_offers`: artist-visible offers created only after final approval.
- `advance_recovery_packets`: failed-advance legal/evidence packets with chain-of-custody and signer requirements.

## Workflow

1. Nightly ensemble scoring (`xr7.pipeline.nightly_advance_ensemble`) evaluates open high-confidence anomalies.
2. Candidates enter analyst queue (`QUEUED_ANALYST`).
3. Analyst approves or rejects.
4. Approved items enter executive queue (`QUEUED_EXEC`).
5. Executive approves or rejects.
6. Only executive-approved opportunities can be published as artist-visible offers.
7. Artists can view and accept only published offers.
8. Failed offers can be escalated into legal recovery packets with immutable ledger anchoring.

## Fee and Risk Controls

- Global contingency baseline is now 12%.
- Offer amount cap: min(60% of predicted recovery, 75,000).
- Fee bands are score-based.
- Effective fee hard cap: contingency + advance fee must not exceed 24%.
- No double-dipping: no new offer is published if an unrepaid accepted/disbursed advance already exists.

## API Surface

- `POST /admin/advances/run-nightly-eval`
- `GET /admin/advances/queue/analyst`
- `POST /admin/advances/opportunities/{opportunity_id}/analyst-decision`
- `GET /admin/advances/queue/executive`
- `POST /admin/advances/opportunities/{opportunity_id}/executive-decision`
- `POST /admin/advances/opportunities/{opportunity_id}/publish-offer`
- `POST /admin/advances/offers/{offer_id}/failed-recovery-packet`
- `GET /artists/{artist_id}/advance/offers`
- `POST /artists/{artist_id}/advance/offers/{offer_id}/accept`
