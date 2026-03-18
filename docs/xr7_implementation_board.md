# XR7 Implementation Board (Issue-Ready)

This board translates the XR7 execution epics into issue-ready work items with ownership lanes, dependencies, and sequencing.

## Priority Lanes

- Lane A: Platform Core and Data Foundation
- Lane B: Explainability and Recovery Intelligence
- Lane C: Collaboration, Mobile, and GTM Enablement

## Sprint 1 (Foundation)

1) XR7-101: Add metadata repair API endpoints and services
- Owner: Backend API
- Depends on: xr7_forensics base APIs
- Acceptance:
  - suggest/apply endpoints live
  - AI audit log row written for apply operations

2) XR7-102: Add UGC signal ingestion and opportunities APIs
- Owner: Backend Data
- Depends on: usage event schema expansion
- Acceptance:
  - ingest endpoint persists UGC fields
  - opportunities endpoint returns ranked list

3) XR7-103: Add catalog health and valuation snapshot APIs
- Owner: Backend Analytics
- Depends on: valuation tables migration
- Acceptance:
  - health endpoint returns scored components
  - valuation snapshot endpoint persists and fetches snapshots

4) XR7-104: Add forecast and simulation APIs
- Owner: Backend Analytics
- Depends on: forecast model table
- Acceptance:
  - forecast endpoint stores forecast rows
  - simulation endpoint returns scenario comparisons

5) XR7-105: Migration chain 0015-0018 rollout in staging
- Owner: Platform + Data
- Depends on: review of migration scripts
- Acceptance:
  - migrations apply cleanly in staging
  - rollback exercise documented

## Sprint 2 (Reliability and Contract Hardening)

1) XR7-201: OpenAPI and API reference regeneration for enhanced routes
2) XR7-202: SDK regeneration and smoke validation
3) XR7-203: Add endpoint idempotency support for write mutations
4) XR7-204: Add queue-backed jobs for valuation and UGC batch workflows
5) XR7-205: Add SLO dashboards and alerting for new endpoints

## Sprint 3 (Product Differentiation)

1) XR7-301: Recovery Potential Radar dashboard backend aggregation
2) XR7-302: Explain-my-gap endpoint with evidence citations
3) XR7-303: One-click fix UX integration with metadata apply API
4) XR7-304: Mobile daily brief integration
5) XR7-305: Pilot tenant launch package and scorecard tracking

## Dependency Graph

- 0015 migration -> 0016 indexes -> 0017 backfill -> 0018 constraints
- Schema availability -> service logic -> router exposure -> OpenAPI generation -> SDK generation
- API availability -> dashboard and mobile integration -> pilot rollout

## Exit Criteria for Market Readiness

- P0 APIs implemented and documented.
- Migrations and rollback validated in staging.
- OpenAPI and SDKs current.
- Pilot tenant onboarding and recovery flow validated.
- Security and observability gates satisfied.
