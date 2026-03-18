# XR7 Database Migration Rollout Plan (Alembic-Aligned)

This document defines a production-safe migration strategy for enhanced XR7 data models and scale requirements.

## Current Baseline

Existing XR7 forensic migration establishes core entities including tracks, works, mappings, usage events, statements, unmatched works, identity graph, and connector credentials.

## Migration Goals

- Add support for UGC usage signals and explainability persistence.
- Add valuation snapshots, forecasting records, split-sheet imports, and AI audit trails.
- Improve query performance for high-volume multi-tenant workloads.
- Maintain backwards compatibility and low-risk rollout posture.

## Alembic Conventions to Preserve

- Revision naming pattern: YYYYMMDD_NNNN_descriptive_name.
- Guard table creation with existence checks for idempotency.
- Use additive migrations first; avoid destructive changes in same release cycle.
- Keep downgrade support where technically practical.

## Phase 1 - Additive Schema Expansion

Proposed revision:
- 20260317_0015_xr7_growth_models.py

Add columns to existing tables:

1) xr7_tracks
- metadata_quality_score FLOAT default 0
- metadata_quality_grade VARCHAR nullable
- ai_repair_status VARCHAR default 'not_evaluated'
- ugc_usage_velocity_7d FLOAT default 0
- ugc_usage_velocity_30d FLOAT default 0
- ugc_platform_coverage_score FLOAT default 0
- viral_risk_score FLOAT default 0

2) xr7_works
- registration_completeness_score FLOAT default 0
- split_conflict_flag BOOLEAN default false
- split_conflict_reason VARCHAR nullable
- recovery_forecast_90d FLOAT default 0
- recovery_forecast_365d FLOAT default 0

3) xr7_usage_events
- ugc_content_id VARCHAR nullable
- ugc_format VARCHAR nullable
- ugc_video_duration_sec INTEGER nullable
- remix_parent_ref VARCHAR nullable
- trend_cluster_id VARCHAR nullable
- short_form_signal_strength FLOAT default 0
- black_box_risk_score FLOAT default 0
- explainability_json TEXT default '{}'

4) xr7_unmatched_works
- suggested_matches_json TEXT default '[]'
- suggested_resolution_actions_json TEXT default '[]'
- ai_resolution_confidence FLOAT default 0
- recovery_potential_score FLOAT default 0
- urgency_score FLOAT default 0
- sla_due_at DATETIME nullable

New tables:

1) xr7_catalog_valuation_snapshots
- id, tenant_id, artist_id, as_of_date
- baseline_value, corrected_value, upside_value
- confidence_interval_low, confidence_interval_high
- assumptions_json, created_at

2) xr7_recovery_forecasts
- id, tenant_id, artist_id, scope_type, scope_id
- forecast_horizon_days, forecast_amount
- confidence_interval_json, model_version
- feature_snapshot_ref, created_at

3) xr7_split_sheet_imports
- id, tenant_id, artist_id, file_ref
- import_status, conflicts_found
- auto_resolved_count, manual_required_count
- imported_by, created_at

4) xr7_ai_decision_audit_log
- id, tenant_id, artist_id, decision_type
- model_provider, model_version
- prompt_hash, input_ref, output_ref
- reviewer_id, override_flag, created_at

## Phase 2 - Indexing and Partition Preparation

Proposed revision:
- 20260317_0016_xr7_performance_indexes.py

Indexes:
- Composite index on xr7_usage_events(tenant_id, artist_id, event_timestamp).
- Composite index on xr7_usage_events(tenant_id, platform, territory, event_timestamp).
- Composite index on xr7_royalty_statement_lines(statement_id, row_index).
- Composite index on xr7_unmatched_works(tenant_id, artist_id, status, updated_at).
- Composite index on xr7_catalog_valuation_snapshots(tenant_id, artist_id, as_of_date).

Optional platform-dependent indexes:
- Trigram index on normalized title fields for fuzzy lookup.
- JSON path indexes for high-frequency metadata keys.

Partition readiness:
- Introduce event-month derivation in writes.
- Create partitioning plan for usage events by month in PostgreSQL production environments.

## Phase 3 - Data Backfill and Consistency

Proposed revision:
- 20260317_0017_xr7_backfill_defaults.py

Backfill actions:
- Initialize newly added numeric scores with deterministic defaults.
- Compute initial metadata quality score from available metadata_json completeness.
- Set ai_repair_status for historical rows to not_evaluated.
- Initialize explainability_json where null.

Consistency checks:
- No null tenant_id in scoped tables.
- No orphaned foreign keys in mappings, usage, and statement lines.
- Unique constraints validated for connector credentials and identity nodes.

## Phase 4 - Controlled Deprecation and Cleanup

Proposed revision:
- 20260317_0018_xr7_cleanup_and_constraints.py

Actions:
- Add stricter constraints after successful backfill and observability checks.
- Add CHECK constraints for confidence and score ranges in [0,1] where applicable.
- Mark legacy columns as deprecated in docs before any future removal.

## Rollout Strategy

Environment sequence:
1) Local development migration dry run.
2) CI ephemeral DB migration test with seed datasets.
3) Staging migration with production-like volume sample.
4) Production canary by tenant cohort.
5) Full rollout with monitoring and rollback guardrails.

Operational safeguards:
- Apply migrations in maintenance windows for index-heavy revisions.
- Use feature flags to gate read/write paths to new columns and tables.
- Keep old and new computation paths in parallel until validation passes.

## Rollback Strategy

- Rollback code path first via feature flags.
- For additive schema releases, keep columns/tables in place and disable new writes.
- Use Alembic downgrade only when operationally safe and data loss risk is acceptable.
- Maintain backup snapshots before each production migration wave.

## Verification Queries and Checks

Post-migration checks:
- Table existence and row counts.
- Index existence and query plan improvements.
- Constraint validation.
- Latency regression checks on top reconciliation and dashboard queries.

Functional checks:
- Ingestion writes to new UGC fields when provided.
- Reconciliation includes explainability fields in outputs.
- Forecast and valuation endpoints can persist and retrieve records.

## Market-Readiness Data Gates

- Data quality score coverage available for at least 95 percent of active catalog records.
- Explainability payload persisted for at least 99 percent of new scored decisions.
- Forecast and valuation jobs complete within SLA windows for pilot tenants.
- Zero tenant data leakage incidents in pre-launch and launch windows.

## Required Companion Changes

- SQLAlchemy model updates for new columns and entities.
- Pydantic schema updates for API payloads and responses.
- OpenAPI schema updates.
- Dashboard query updates and materialized view refresh logic.
- Monitoring and alert rule updates for new jobs and data paths.
