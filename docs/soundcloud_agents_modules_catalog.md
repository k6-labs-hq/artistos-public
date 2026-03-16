# SoundCloud Agents and Modules Catalog

Implementation-ready catalog aligned to XR7 Engine 2 orchestration and ingestion architecture.

## 1) SoundCloud Statement Ingestor
- Purpose: Parse SoundCloud statement files and normalize to XR7 events/payments.
- Input: CSV/TSV/XLSX statement bytes + artist_id.
- Output: ParseResult with events, payments, format_detected.
- State fields: format_detected, row_count, skipped_rows, parser_errors.
- Integration: XR7 ingestion parser and upload router.
- Value: Enables production ingestion without manual remapping.
- Required endpoints/tasks: POST /artists/{id}/statements/upload.

## 2) SoundCloud Format Detector
- Purpose: Identify SoundCloud exports from variant headers.
- Input: Header row list.
- Output: soundcloud format key.
- State fields: parser_header_signature.
- Integration: detect_format in statement parser.
- Value: Minimizes ingestion failures from export variations.
- Required endpoints/tasks: Parser pipeline.

## 3) Multi-Format Statement Dispatcher
- Purpose: Route upload to CSV/TSV/XLSX parser by extension.
- Input: file bytes + filename.
- Output: ParseResult.
- State fields: file_extension, parse_path.
- Integration: parse_statement_file + upload endpoints.
- Value: Removes CSV-only ingestion bottleneck.
- Required endpoints/tasks: upload + upload-batch.

## 4) SoundCloud OAuth Provider Adapter
- Purpose: Provide provider metadata for OAuth URL/token flow.
- Input: provider key soundcloud.
- Output: authorization and token config payload.
- State fields: oauth_provider, oauth_scopes.
- Integration: oauth_providers registry.
- Value: Enables secure account-linking parity with existing providers.
- Required endpoints/tasks: OAuth session creation/exchange.

## 5) SoundCloud Connection Router
- Purpose: Dedicated API connect/status endpoints for SoundCloud.
- Input: artist_id.
- Output: auth URL payload + status payload.
- State fields: provider_status, auth_url.
- Integration: connect router.
- Value: Explicit UX path for SoundCloud linking.
- Required endpoints/tasks: POST/GET /artists/{id}/connect/soundcloud*.

## 6) SoundCloud Partner Provider Contract
- Purpose: Register SoundCloud in partner provider status path.
- Input: provider=soundcloud.
- Output: provider readiness payload.
- State fields: credentials_configured, endpoint_configured.
- Integration: partner_ecosystem.
- Value: Reuses generic provider connect/status APIs.
- Required endpoints/tasks: /artists/{id}/connect/{provider}.

## 7) SoundCloud Upload Trigger Task
- Purpose: Fire follow-up workflow after SoundCloud statement ingest.
- Input: artist_id + statement_id.
- Output: queued workflow trigger metadata.
- State fields: trigger_type, statement_id.
- Integration: celery_tasks + ingestion router.
- Value: Ensures immediate post-ingestion orchestration.
- Required endpoints/tasks: xr7.workflow.on_soundcloud_statement_upload.

## 8) SoundCloud UGC Opportunity Scanner
- Purpose: Surface SoundCloud-specific remix/repost opportunities.
- Input: artist_id.
- Output: opportunity list.
- State fields: ugc_candidates, estimated_recoverable.
- Integration: global_social_regional connector.
- Value: Adds social leakage opportunities to recovery pipeline.
- Required endpoints/tasks: global social fetch/scan jobs.

## 9) SoundCloud Metadata Sync Agent
- Purpose: Sync track metadata (ISRC, title, release date, duration).
- Input: connected account + artist catalog.
- Output: normalized metadata deltas.
- State fields: metadata_sync_status, last_sync_at.
- Integration: ingestion + catalog services.
- Value: Improves attribution and anomaly quality.
- Required endpoints/tasks: scheduled metadata sync task.

## 10) SoundCloud Earnings Reconstruction Agent
- Purpose: Reconstruct expected royalties from usage and rate baselines.
- Input: SoundCloud usage rows + contract/rate assumptions.
- Output: expected earnings vector + variance breakdown.
- State fields: expected_vs_reported, confidence_score.
- Integration: earnings/recovery intelligence modules.
- Value: Quantifies missing payout exposure.
- Required endpoints/tasks: reconstruction endpoints/jobs.

## 11) SoundCloud Anomaly Classifier
- Purpose: Categorize anomalies for SoundCloud-specific leakage modes.
- Input: reconstructed vs reported royalty records.
- Output: anomaly records with subtype and severity.
- State fields: anomaly_subtype, severity, recoverable_estimate.
- Integration: anomaly engine/model.
- Value: Better prioritization and playbook matching.
- Required endpoints/tasks: anomaly detection run.

## 12) SoundCloud Claim Strategy Agent
- Purpose: Choose optimal claim path (platform dispute, legal, payer outreach).
- Input: anomaly profile + evidence quality + SOL context.
- Output: recommended claim strategy.
- State fields: recommended_path, priority_score.
- Integration: recovery playbook generator.
- Value: Faster and more defensible recovery actions.
- Required endpoints/tasks: playbook endpoints.

## 13) SoundCloud Evidence Packet Builder
- Purpose: Build evidence templates for SoundCloud claims.
- Input: anomaly, usage proof, statement lineage.
- Output: structured evidence packet.
- State fields: evidence_hash, packet_version.
- Integration: evidence export/verification pipeline.
- Value: Improves dispute acceptance rates.
- Required endpoints/tasks: claim evidence export/verify.

## 14) SoundCloud Catalog Adjacency Agent
- Purpose: Detect near-duplicate tracks/remix adjacency for claim expansion.
- Input: catalog + SoundCloud metadata graph.
- Output: adjacency edges and related-risk clusters.
- State fields: adjacency_nodes, adjacency_edges.
- Integration: graph and catalog modules.
- Value: Finds under-claimed related usage.
- Required endpoints/tasks: catalog graph build/audit.

## 15) SoundCloud Rights Drift Monitor
- Purpose: Detect rights owner mismatch drift over time.
- Input: periodic metadata snapshots.
- Output: drift alerts.
- State fields: owner_drift_events, drift_confidence.
- Integration: onboarding + integrity checks.
- Value: Prevents payout leakage from stale ownership data.
- Required endpoints/tasks: periodic sync and integrity checks.

## 16) SoundCloud Workflow Router Hook
- Purpose: Route SoundCloud signals into orchestration steps.
- Input: trigger events and current run state.
- Output: next-step routing decision.
- State fields: current_step, route_reason.
- Integration: workflow/orchestrator router.
- Value: Keeps SoundCloud recovery autonomous and deterministic.
- Required endpoints/tasks: workflow run tasks.

## 17) SoundCloud Confidence Calibrator
- Purpose: Calibrate model confidence for SoundCloud anomaly predictions.
- Input: predicted vs confirmed outcomes.
- Output: calibration metrics and threshold updates.
- State fields: calibration_bucket, calibration_error.
- Integration: intelligence calibration endpoints.
- Value: Reduces false positives and wasted ops cycles.
- Required endpoints/tasks: calibration jobs.

## 18) SoundCloud Dashboard Adapter
- Purpose: Add SoundCloud slices to dashboard totals and charts.
- Input: artist anomaly/payment/event aggregates.
- Output: dashboard fields and chart series.
- State fields: soundcloud_leakage_total, soundcloud_recovered_total.
- Integration: dashboard/earnings serializers.
- Value: User-visible recovery progress by platform.
- Required endpoints/tasks: dashboard endpoints.

## 19) SoundCloud Beat Scheduler
- Purpose: Schedule periodic SoundCloud healthcheck/sync scans.
- Input: schedule definitions + active linked accounts.
- Output: enqueued scan/sync tasks.
- State fields: last_run_at, next_run_at.
- Integration: celery beat and task registry.
- Value: Continuous detection without manual intervention.
- Required endpoints/tasks: scheduled celery tasks.

## 20) SoundCloud Workflow Audit Logger
- Purpose: Persist immutable trace entries for SoundCloud decisions/actions.
- Input: workflow decisions and transitions.
- Output: immutable ledger records.
- State fields: ledger_entry_type, workflow_run_id.
- Integration: immutable ledger service.
- Value: End-to-end forensics and legal defensibility.
- Required endpoints/tasks: workflow completion hooks.

## 21) SoundCloud Retry and DLQ Handler
- Purpose: Resilient retry policy for connector/task failures.
- Input: failed SoundCloud jobs.
- Output: retry/dead-letter status entries.
- State fields: retry_count, dlq_reason.
- Integration: connector retry queue contracts.
- Value: Production reliability under API volatility.
- Required endpoints/tasks: connector queues + status APIs.

## 22) SoundCloud Outcome Feedback Loop Agent
- Purpose: Learn from claim outcomes to refine scoring and routing.
- Input: claim result labels and amounts recovered.
- Output: updated strategy priors.
- State fields: outcome_label, uplift_delta.
- Integration: intelligence feedback endpoints.
- Value: Compounding improvement of recovery performance.
- Required endpoints/tasks: feedback ingestion tasks.
