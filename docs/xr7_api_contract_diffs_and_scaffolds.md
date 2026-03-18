# XR7 API Contract Diffs and Endpoint Scaffolds

This document maps contract-level changes required to implement the enhanced XR7 platform on top of existing endpoints.

## Baseline Existing XR7 Forensics Endpoints

Current endpoints are implemented in XR7 API router and include:
- credentials upsert
- pipeline runs (api-ingestion, file-ingestion, fingerprinting, reconciliation, black-box)
- queue dispatch variants
- reconciliation gap report

## Contract Design Principles

- Tenant-safe by default with tenant_id request fields and server-side access checks.
- Idempotent mutation routes using Idempotency-Key header for write APIs.
- Explainability-first responses for matching, reconciliation, and prediction outputs.
- Consistent envelope for async work: job_id, task_id, status, retry_policy, links.
- Versioned schema evolution with backward-compatible additions.

## New API Groups and Endpoints

## A) Metadata Cleanup and Enrichment

1) POST /artists/{artist_id}/xr7/metadata/repair/suggest
- Purpose: Generate deterministic + AI suggestions for metadata cleanup.
- Request:
  - tenant_id: string
  - scope: catalog | statements | unmatched
  - max_items: int
- Response:
  - suggestions: array of suggestion objects
  - quality_score_before: float
  - projected_quality_score_after: float

2) POST /artists/{artist_id}/xr7/metadata/repair/apply
- Purpose: Apply approved suggestions (single or bulk).
- Request:
  - tenant_id: string
  - suggestion_ids: array[string]
  - dry_run: bool
- Response:
  - applied_count: int
  - skipped_count: int
  - audit_refs: array[string]

## B) UGC and Social Rights Tracking

1) POST /artists/{artist_id}/xr7/ugc/signals/ingest
- Purpose: Ingest short-form usage signals from partner or internal collectors.
- Request:
  - tenant_id: string
  - platform: string
  - signals: array[UGCSignalInput]
- Response:
  - accepted: int
  - rejected: int
  - ingestion_ref: string

2) GET /artists/{artist_id}/xr7/ugc/opportunities
- Purpose: Return ranked UGC leakage opportunities.
- Query:
  - tenant_id, min_confidence, min_estimated_value, status
- Response:
  - opportunities: array[UGCOpportunity]

## C) Explainability and Case Intelligence

1) GET /artists/{artist_id}/xr7/reconciliation/gaps/{gap_id}/explain
- Purpose: Explain why a specific gap is flagged.
- Response:
  - summary: string
  - top_drivers: array[Driver]
  - confidence_breakdown: object
  - source_refs: array[string]

2) POST /artists/{artist_id}/xr7/cases/from-gap/{gap_id}
- Purpose: Create case and evidence packet from gap.
- Request:
  - tenant_id: string
  - priority: low|medium|high|critical
- Response:
  - case_id: string
  - packet_id: string

## D) Catalog Health, Valuation, and Forecasting

1) GET /artists/{artist_id}/xr7/catalog/health
- Response:
  - score: float
  - components: object
  - top_actions: array[string]

2) GET /artists/{artist_id}/xr7/valuation/snapshot
- Query: tenant_id, as_of
- Response:
  - baseline_value, corrected_value, upside_value
  - confidence_interval
  - assumptions

3) POST /artists/{artist_id}/xr7/forecast/recovery
- Request:
  - tenant_id
  - horizon_days: 30|90|365
  - scenario_overrides: object
- Response:
  - forecast_amount
  - confidence_interval
  - recommended_actions

4) POST /artists/{artist_id}/xr7/simulations/what-if
- Request:
  - tenant_id
  - scenarios: array[ScenarioInput]
- Response:
  - scenarios: array[ScenarioResult]

## E) Collaboration and Mobile

1) POST /artists/{artist_id}/xr7/case-rooms
- Create collaborative room scoped to case.

2) POST /artists/{artist_id}/xr7/case-rooms/{room_id}/comments
- Add comment with optional mentions and attachments.

3) GET /artists/{artist_id}/xr7/mobile/daily-brief
- Return mobile digest cards and quick actions.

4) POST /artists/{artist_id}/xr7/onboarding/steps/{step_key}/complete
- Mark guided onboarding step as complete.

## Request and Response Schema Additions

New request models:
- MetadataRepairSuggestRequest
- MetadataRepairApplyRequest
- UGCSignalIngestRequest
- ForecastRequest
- SimulationRequest
- CreateCaseFromGapRequest
- CaseRoomCommentRequest

New response models:
- MetadataRepairSuggestion
- ExplainGapResponse
- UGCOpportunity
- CatalogHealthResponse
- ValuationSnapshotResponse
- ForecastResponse
- SimulationResponse
- CaseRoomResponse
- MobileDailyBriefResponse

Common response envelope (recommended):
- request_id: string
- tenant_id: string
- status: string
- data: object
- warnings: array[string]

## Error Model and Status Codes

Standard error payload:
- code: string
- message: string
- detail: object
- request_id: string

Core status code contracts:
- 200: success read or synchronous mutation success
- 202: async accepted with job metadata
- 400: validation error
- 401/403: auth/authorization error
- 404: resource not found
- 409: conflict (idempotency, version mismatch)
- 422: semantic validation failure
- 429: rate limit throttled
- 500: internal error with trace reference

## Endpoint Scaffold Mapping to Current Router Layout

Recommended file additions:
- XR7/api/routers/xr7_metadata.py
- XR7/api/routers/xr7_ugc.py
- XR7/api/routers/xr7_valuation.py
- XR7/api/routers/xr7_collaboration.py

Recommended service additions:
- XR7/services/xr7_metadata_service.py
- XR7/services/xr7_ugc_service.py
- XR7/services/xr7_valuation_service.py
- XR7/services/xr7_case_rooms_service.py

Recommended task additions:
- XR7/tasks/xr7_ugc_pipeline.py
- XR7/tasks/xr7_valuation_pipeline.py
- XR7/tasks/xr7_forecast_pipeline.py

## OpenAPI Build-Out Plan

Phase 1:
- Add request and response schemas.
- Add endpoint docs with examples and error responses.

Phase 2:
- Add tags and operation IDs.
- Add auth and rate-limit headers to endpoint specs.

Phase 3:
- Generate and validate SDK updates.
- Publish contract changelog and migration notes.

## Backward Compatibility and Versioning

- Avoid breaking existing payloads; only additive fields on existing models.
- Introduce API version header for future breaking changes.
- Add deprecation metadata for old routes before retirement.

## Market-Ready API Quality Gates

- 100 percent endpoint auth coverage validated.
- 100 percent mutation endpoints support idempotency keys.
- 100 percent automated decisions include explainability payload links.
- Public API examples available for top 20 workflows.
- SDK smoke tests pass for Python and TypeScript clients.
