# XR7 - Forensic Royalty Recovery Engine (Production-Grade, Multi-Tenant SaaS)

This document is the canonical 2026-2027 master specification for XR7. It expands the baseline platform into a world-class, production-grade system for independent artists, songwriters, producers, managers, publishers, business managers, and large catalog owners.

## 1. XR7 - Vision & Killer Differentiators

- Recovery Potential Radar that prioritizes the highest-value recoveries by confidence, legal readiness, and time sensitivity.
- Leakage Funnel Storytelling that shows detected usage -> reported usage -> paid royalties -> recovered value.
- Explainable AI for every major match and gap with confidence decomposition and plain-language reasoning.
- One-Click Fix workflows for unmatched works, metadata defects, split conflicts, and registration gaps.
- Short-form UGC leakage intelligence for TikTok sounds, Instagram Reels, YouTube Shorts, remixes, reposts, and viral derivatives.
- MLC and SoundExchange recovery accelerators for unmatched work queues and black-box opportunity packets.
- Catalog Health Score with measurable sub-scores: metadata quality, split integrity, registration completeness, and platform coverage.
- Predictive leakage forecasting with territory/platform risk heatmaps and intervention recommendations.
- Catalog valuation modeling with baseline, upside, downside, and confidence intervals tied to correction actions.
- Collaborative Case Rooms with comments, mentions, attachments, decisions, and SLA-aware timelines.
- Mobile-first artist view for daily alerts, connector health, and rapid recovery approvals.
- Guided onboarding and coverage health checks to drive time-to-first-insight in days.
- Recovery Playbook exports (PDF/CSV/API) for labels, societies, legal teams, and finance stakeholders.
- Per-tenant AI tuning controls (precision vs aggressiveness) with policy guardrails and full audit trails.
- Ecosystem extensibility via webhooks, Zapier, BI connectors, and partner APIs.

## 2. Enhanced System Architecture Diagram

```text
                                  +----------------------------------+
                                  |           Client Layer            |
                                  |----------------------------------|
                                  | Artist/Manager Web App           |
                                  | Mobile Self-Service App          |
                                  | Internal Analyst Console         |
                                  | Partner/API Client Applications  |
                                  +----------------+-----------------+
                                                   |
                                                   v
+-------------------------------------------------------------------------------------+
|                           API Gateway & Edge Services                               |
|-------------------------------------------------------------------------------------|
| REST/GraphQL Gateway | BFF Layer | Webhook Gateway | WAF | Rate Limit | Request Log|
| AuthN/AuthZ (OIDC/SSO, RBAC/ABAC) | Tenant Resolver | API Key Management            |
+----------------------------+--------------------------+------------------------------+
                             |                          |
                             v                          v
+-------------------------------------------------------------------------------------+
|                              Core Domain Services                                    |
|-------------------------------------------------------------------------------------|
| API Connectors Service              | File Ingestion Service                         |
| Fingerprinting & Similarity Service | Reconciliation & Royalty Gap Engine            |
| Artist Identity Graph Service       | Catalog & Works Service                        |
| Reporting & Analytics Service       | Workflow/Case/Notification Service             |
| Admin & Configuration Service       | Mobile Self-Service API Service                |
|-------------------------------------------------------------------------------------|
| AI Metadata Cleanup & Enrichment Service                                             |
| Short-Form UGC & Social Rights Tracker                                               |
| Catalog Health & Valuation Service                                                   |
| Predictive Recovery & Simulation Engine                                              |
| Collaborative Case Workspace Service                                                 |
+----------------------------+--------------------------+------------------------------+
                             |                          |
                             v                          v
+-------------------------------------------------------------------------------------+
|                           Data, Search, Graph, and Storage                           |
|-------------------------------------------------------------------------------------|
| PostgreSQL (+RLS, pgvector) | Warehouse/Lakehouse (Snowflake/BigQuery/Delta)       |
| Object Storage (raw files, audio, evidence) | OpenSearch | Redis                    |
| Graph Store (Neo4j optional) | Credential Vault/KMS                                  |
+----------------------------+--------------------------+------------------------------+
                             |                          |
                             v                          v
+-------------------------------------------------------------------------------------+
|                                ML & Compute Layer                                    |
|-------------------------------------------------------------------------------------|
| Fingerprinting Workers (audio + short-form video) | Vector Similarity Retrieval     |
| LLM Explainability Layer (OpenAI/Grok) | Time-Series Forecast Models                |
| Feature Store | Temporal Orchestration | Serverless Burst Workers                   |
| Queue Fabric (Kafka/SQS/RabbitMQ)                                                     |
+----------------------------+--------------------------+------------------------------+
                             |
                             v
+-------------------------------------------------------------------------------------+
|                           Observability & Governance                                 |
|-------------------------------------------------------------------------------------|
| OpenTelemetry Tracing | Metrics (Prometheus/Grafana) | Centralized Structured Logs |
| Audit Logs (user/admin/AI decisions) | Data Lineage | Cost Telemetry per tenant     |
| Compliance Controls (SOC2/GDPR/CCPA support)                                         |
+-------------------------------------------------------------------------------------+

Primary data flows:
1) API ingestion -> normalized catalog and usage -> reconciliation -> cases, alerts, dashboards.
2) File ingestion -> parsing and mapping -> statements and unmatched entities -> reconciliation.
3) Fingerprinting and UGC tracking -> similarity engine -> reconciliation -> leakage alerts.
4) Identity graph enriches all matching, scoring, and reconciliation workflows.
5) Forecast and simulation consume historical outcomes -> proactive recovery guidance.
```

## 3. Upgraded Service-by-Service Breakdown

### API Connectors Service

Responsibilities:
- Integrate Spotify, Apple, Amazon, YouTube Data/Content ID, TikTok endpoints, SoundCloud, Meta Rights Manager, BMAT, Soundmouse, and partner feeds.
- Handle OAuth/token refresh, credential rotation, webhook subscriptions, and incremental sync cursors.
- Enforce rate-limit-aware scheduling, retries, backoff, circuit breakers, and dead-letter handling.

Inputs:
- Tenant connector configs, encrypted credentials, sync windows, webhook events.

Outputs:
- Normalized catalog and usage records, monetization records, raw payload archives.

Key operations:
- connect/disconnect/test connector
- incremental sync and historical backfill
- webhook receive/replay

### File Ingestion Service

Responsibilities:
- Ingest MLC/PRO/SoundExchange/international/live files across PDF/CSV/XLSX/XML/JSON.
- OCR and extraction, format detection, schema mapping, normalization, and data quality checks.
- Produce user-facing parse diagnostics and reprocessing options.

Inputs:
- Upload payloads, source templates, tenant mapping rules.

Outputs:
- Royalty statements/lines, usage events, works updates, unmatched work records.

Key operations:
- upload, preview parse, apply mapping, commit ingestion, reprocess

### Fingerprinting & Similarity Service

Responsibilities:
- Generate and compare audio and short-form video fingerprints.
- Build embeddings and run nearest-neighbor retrieval.
- Score match candidates and emit explainability features.

Inputs:
- Catalog media assets, UGC snippets, detection feeds.

Outputs:
- Candidate matches, confidence scores, linkage records, evidence artifacts.

Key operations:
- fingerprint asset, similar search, cross-platform linkage, embedding refresh

### Reconciliation & Royalty Gap Engine

Responsibilities:
- Compute expected vs actual usage and royalties by track/work/platform/territory/period.
- Detect under-reporting, unmatched records, rate anomalies, black-box candidates.
- Generate prioritized recovery opportunities and case seeds.

Inputs:
- Usage events, statements, benchmark rates, catalog state, identity graph.

Outputs:
- Gap records, confidence scores, recommendations, case artifacts.

Key operations:
- run reconciliation, evaluate gap, score recovery potential, export discrepancy packet

### Artist Identity Graph Service

Responsibilities:
- Resolve aliases, duplicates, role conflicts, and ownership relationship chains.
- Maintain graph links among artists, writers, publishers, labels, distributors, societies.

Inputs:
- Platform identities, registries, manual corrections, ML suggestions.

Outputs:
- Node/edge graph with confidence and provenance.

Key operations:
- resolve identity, merge/split nodes, relationship query, conflict explanation

### Catalog & Works Service

Responsibilities:
- Maintain canonical catalog for tracks, works, mappings, rights windows, and splits.
- Support split sheet ingestion and controlled bulk updates.

Inputs:
- API and file ingestion records, fingerprint matches, analyst edits.

Outputs:
- Ground truth catalog state and revision history.

Key operations:
- upsert tracks/works, import split sheets, apply rights windows, territory overrides

### Reporting & Analytics Service

Responsibilities:
- Power dashboard analytics, trend analysis, leakage funnels, and risk heatmaps.
- Produce exports and evidence bundles across CSV/XLSX/PDF/API.

Inputs:
- Reconciliation outputs, cases, historical outcomes, valuation models.

Outputs:
- Report artifacts, dashboard views, scheduled digests.

Key operations:
- dashboard query, generate report, export evidence bundle

### Workflow, Case Management & Notifications Service

Responsibilities:
- Manage case lifecycle, assignments, approvals, and status transitions.
- Trigger notifications to app, email, webhooks, and mobile push.

Inputs:
- Gap events, user actions, policy rules.

Outputs:
- Case updates, activity timeline events, alerts.

Key operations:
- create/update/resolve case, escalate, assign, notify

### Admin & Configuration Service

Responsibilities:
- Manage tenant branding, role policies, feature flags, and threshold rules.
- Govern automation boundaries and experiment toggles.

Inputs:
- Admin requests, policy templates, tenant settings.

Outputs:
- Versioned policy configs and audit records.

Key operations:
- configure RBAC, tune thresholds, enable feature flags, review policy diffs

### AI Metadata Cleanup & Enrichment Service (New)

Responsibilities:
- Detect metadata defects and propose deterministic plus ML-based repairs.
- Suggest likely ISRC/ISWC/IPI links and registration completion actions.

Inputs:
- Catalog metadata, ingestion errors, historical successful mappings.

Outputs:
- Repair suggestions with impact estimates and confidence explanations.

### Short-Form UGC & Social Rights Tracker (New)

Responsibilities:
- Capture and normalize short-form social usage signals and trend dynamics.
- Link weak-signal UGC detections to rights ownership opportunities.

Inputs:
- UGC platform feeds, fingerprint detections, social metadata snapshots.

Outputs:
- UGC usage events, claim recommendations, risk-ranked opportunity queues.

### Catalog Health & Valuation Service (New)

Responsibilities:
- Compute catalog health metrics and valuation snapshots.
- Quantify uplift from remediation actions and pipeline corrections.

Inputs:
- Catalog quality metrics, payout history, benchmark economics, recovery history.

Outputs:
- Health scores, valuation ranges, confidence intervals.

### Predictive Recovery & Simulation Engine (New)

Responsibilities:
- Forecast likely leakage and recoveries at 30/90/365 day horizons.
- Simulate changes in rates, territories, deal structures, and split corrections.

Inputs:
- Time-series usage and payout data, interventions, benchmark updates.

Outputs:
- Forecasts, scenarios, recommended intervention plans.

### Collaborative Case Workspace Service (New)

Responsibilities:
- Provide persistent case rooms with comments, mentions, evidence boards, and approval trails.
- Enable secure cross-stakeholder workflows.

Inputs:
- Case events, participant actions, attachment metadata.

Outputs:
- Immutable case timelines and collaboration artifacts.

### Mobile/Artist Self-Service Portal Service (New)

Responsibilities:
- Deliver artist-friendly mobile APIs for alerts, status, and quick actions.
- Support guided onboarding and platform connection flows.

Inputs:
- Tenant states, connector statuses, case alerts.

Outputs:
- Daily summaries, push notifications, progress indicators.

## 4. Enhanced Data Models

All entity families are tenant-scoped and include provenance fields.

Common required columns:
- id (UUID), tenant_id, created_at, updated_at, source_system, lineage_id, confidence_score.

Common indexing strategy:
- Composite: (tenant_id, updated_at), (tenant_id, external_source, external_id), (tenant_id, status, period_start).
- Text search: trigram/GIN on normalized titles and names.
- Vector search: pgvector index for embedding columns.

Partitioning strategy:
- usage_events and royalty_statement_lines monthly partitions on event_date or statement_period.
- Archive cold partitions to warehouse/lakehouse.

### tracks

Core fields:
- id, tenant_id, canonical_title, normalized_title, primary_artist_name, release_date, duration_seconds, isrc, upc, label_name, distributor_name.

Enhanced fields:
- metadata_quality_score, metadata_quality_grade, ai_repair_status, ai_repair_suggestions_json.
- ugc_usage_velocity_7d, ugc_usage_velocity_30d, ugc_platform_coverage_score, viral_risk_score.
- fingerprint_id, audio_embedding_vector, video_embedding_vector, fingerprint_confidence.

### works

Core fields:
- id, tenant_id, canonical_title, normalized_title, iswc, alt_titles_json.

Enhanced fields:
- writer_splits_json, publisher_splits_json, split_conflict_flag, split_conflict_reason.
- registration_status_mlc, registration_status_pro, registration_status_soundexchange.
- metadata_quality_score, registration_completeness_score, split_sheet_import_id.
- recovery_forecast_90d, recovery_forecast_365d.

### isrc_iswc_ipi_mappings

Fields:
- id, tenant_id, track_id, work_id, ipi, cae, role, mapping_source, mapping_status.
- ai_match_confidence, ai_match_explanations_json, feature_contributions_json.
- decision_source, decided_by, decided_at, lineage_id, source_row_ref.

### usage_events

Core fields:
- id, tenant_id, event_timestamp, platform, source_type, usage_type, territory.
- asset_ref, work_ref, quantity, estimated_rate, expected_royalty, reported_royalty.

UGC-specific fields:
- ugc_content_id, ugc_creator_handle_hash, ugc_format, ugc_video_duration_sec.
- remix_parent_ref, trend_cluster_id, short_form_signal_strength.

AI and anomaly fields:
- match_confidence, confidence_band, explainability_blob.
- potential_underreport_flag, black_box_risk_score, rights_conflict_flag.

### royalty_statements and royalty_statement_lines

royalty_statements fields:
- id, tenant_id, source_org, statement_period_start, statement_period_end, currency, fx_rate_snapshot.
- ingestion_job_id, parsing_confidence, source_file_ref.

royalty_statement_lines fields:
- id, statement_id, tenant_id, line_ref, track_id, work_id, usage_qty, amount_reported.
- rate_effective, territory, platform, source_lineage.
- expected_amount, gap_amount, gap_pct, gap_confidence.
- normalization_status, ai_repair_recommendation, mismatch_reason_code.

### unmatched_works

Fields:
- id, tenant_id, unresolved_title, unresolved_artist, unresolved_ids_json.
- first_seen_at, last_seen_at, usage_volume, status, linked_entity_id, case_id.
- suggested_matches_json, suggested_resolution_actions_json.
- ai_resolution_confidence, explainability_summary.
- recovery_potential_score, urgency_score, sla_due_at.

### artist_identity_graph_nodes and artist_identity_graph_edges

Node fields:
- id, tenant_id, node_type, display_name, normalized_name, external_ids_json, confidence.

Edge fields:
- id, tenant_id, from_node_id, to_node_id, relation_type, strength, evidence_refs_json, source.

Enhanced fields:
- conflict_state, reviewed_by, reviewed_at, ai_reasoning_summary.

### catalog_valuation_snapshots (new)

Fields:
- id, tenant_id, artist_id, as_of_date, baseline_value, corrected_value, upside_value.
- confidence_interval_low, confidence_interval_high, assumptions_json.

### recovery_forecasts (new)

Fields:
- id, tenant_id, scope_type, scope_id, forecast_horizon_days, forecast_amount.
- model_version, feature_snapshot_ref, confidence_interval_json.

### split_sheet_imports (new)

Fields:
- id, tenant_id, file_ref, import_status, conflicts_found.
- auto_resolved_count, manual_required_count, imported_by.

### ai_decision_audit_log (new)

Fields:
- id, tenant_id, decision_type, model_provider, model_version.
- prompt_hash, input_ref, output_ref, reviewer_id, override_flag, created_at.

## 5. Upgraded Pipeline Definitions

### API ingestion pipeline

Trigger:
- Scheduled incremental jobs, connector webhooks, manual backfill runs.

Stages:
1) Credential retrieval and scope validation.
2) Platform fetch with adaptive throttling.
3) Normalization and schema validation.
4) Idempotent upsert to catalog and usage.
5) Lineage recording, metrics emission, and reconciliation enqueue.

Failure handling:
- Exponential retries, DLQ routing, checkpointed partial commits, connector health alerts.

### File ingestion pipeline

Trigger:
- User upload via web/mobile, partner API upload, scheduled secure drop pickup.

Stages:
1) Raw file storage and checksum.
2) Format and source detection.
3) Parsing and OCR where needed.
4) Source template mapping.
5) Validation and anomaly pre-check.
6) Normalization and persistence.
7) Unmatched detection and reconciliation enqueue.

Failure handling:
- Per-file and row-level error reporting, resumable reprocessing, user remediation guidance.

### Fingerprinting pipeline

Trigger:
- New catalog media, backfill sweeps, UGC spike events.

Stages:
1) Media retrieval.
2) Audio/video fingerprint generation.
3) Embedding computation.
4) Candidate retrieval.
5) Confidence and explanation scoring.
6) Candidate persistence and reconciliation trigger.

Failure handling:
- Retry with fallback extraction profile, metadata-only fallback, DLQ for corrupted media.

### Reconciliation pipeline

Trigger:
- New usage, statement lines, mapping changes, scheduled batch windows.

Stages:
1) Context aggregation (usage, statements, catalog, identity graph).
2) Match rule application and confidence scoring.
3) Expected vs actual royalty computation.
4) Gap detection and prioritization.
5) Case creation, dashboard refresh, notification dispatch.

Failure handling:
- Idempotent run keys, chunked recompute, audit snapshots, partial replay support.

### Black box detection pipeline

Trigger:
- Monthly or quarterly scheduled execution.

Stages:
1) Aggregate long-horizon usage vs reported royalties.
2) Detect systematic under-report patterns.
3) Compute black-box potential and risk scores.
4) Generate case recommendations and reports.

Outputs:
- Black-box candidate records, risk tiering, action recommendations.

### UGC detection and fingerprint cross-check pipeline (new)

Trigger:
- Streaming social usage feeds and trend threshold events.

Stages:
1) UGC event capture and normalization.
2) Clip sampling and fingerprint extraction.
3) Cross-check against catalog vectors and known fingerprints.
4) Confidence scoring and monetization gap estimation.
5) Opportunity queue insertion and alerting.

Failure handling:
- Deferred re-scan queue for low-quality clips, confidence downgrade tagging.

### AI-driven metadata repair suggestion pipeline (new)

Trigger:
- Nightly quality sweep and post-ingestion validation failures.

Stages:
1) Detect metadata defects.
2) Generate deterministic and ML suggestions.
3) Compute expected impact and confidence.
4) Auto-apply if policy threshold met; otherwise route to manual review.
5) Record decision in AI audit log.

### Monthly catalog valuation refresh pipeline (new)

Trigger:
- Month-end close and major catalog events.

Stages:
1) Pull corrected earnings and quality metrics.
2) Run valuation model suite.
3) Produce baseline/upside/downside snapshots.
4) Publish to dashboards and exports.

### Predictive leakage forecasting pipeline (new)

Trigger:
- Weekly cadence and after significant ingestion updates.

Stages:
1) Build time-series features.
2) Forecast leakage/recovery by segment.
3) Generate recommended preventive interventions.
4) Notify stakeholders and persist forecast records.

## 6. Advanced Algorithms & AI Layer

### Metadata triangulation (explicit)

Goal:
- Combine title, artist, duration, release date, label, territory, and ID signals (ISRC/ISWC/IPI) into a composite similarity score for candidate linkage.

Process:
1) Normalize fields (unicode fold, punctuation strip, featuring/remix token normalization, locale variants).
2) Build candidate pool using blocking keys (duration tolerance, territory overlap, release window proximity).
3) Compute per-field similarities:
   - title and alternate titles
   - primary and contributing artist names
   - duration delta
   - release date distance
   - label and distributor consistency
   - ID alignment (ISRC/ISWC/IPI exact and partial)
4) Apply platform-specific heuristics (for example, short-form title truncation and localized title aliases).
5) Aggregate weighted score and emit reason codes.

Pseudo-code:

```python
def metadata_triangulation_score(obs, candidate, weights):
    t = token_similarity(norm_title(obs.title), norm_title(candidate.title))
    a = contributor_similarity(obs.artists, candidate.artists)
    d = duration_similarity(obs.duration_sec, candidate.duration_sec, tol_sec=3)
    r = date_similarity(obs.release_date, candidate.release_date)
    l = label_similarity(obs.label, candidate.label)
    i = id_consistency(obs.isrc, obs.iswc, obs.ipi, candidate)
    h = platform_heuristics(obs.platform, obs, candidate)
    c = conflict_penalty(obs, candidate)
    score = (weights.t * t + weights.a * a + weights.d * d +
             weights.r * r + weights.l * l + weights.i * i +
             weights.h * h - weights.c * c)
    return clamp01(score)
```

### Fuzzy matching with explainability (explicit)

Goal:
- Produce ranked candidate matches using lexical and embedding similarity while keeping decision traces auditable.

Process:
1) Blocking: same territory or allowed territory map, duration within tolerance, period proximity.
2) Lexical retrieval: n-gram and trigram index search on normalized title and artist fields.
3) Distance scoring: Levenshtein/Jaro-Winkler/token-set ratios.
4) Embedding retrieval: ANN search over metadata embeddings.
5) Blend lexical and embedding scores, then apply business constraints.
6) Return top-k candidates with reasons and evidence refs.

Pseudo-code:

```python
def fuzzy_match(observation, candidates):
    blocked = [c for c in candidates if pass_blocking(observation, c)]
    scored = []
    for c in blocked:
        s_lex = lexical_score(observation, c)
        s_dist = edit_distance_score(observation, c)
        s_emb = embedding_score(observation, c)
        s_rule = rules_adjustment(observation, c)
        s = clamp01(0.35*s_lex + 0.20*s_dist + 0.35*s_emb + 0.10*s_rule)
        scored.append((c.id, s, explain_signals(observation, c)))
    return sorted(scored, key=lambda x: x[1], reverse=True)[:10]
```

### Unmatched work detection and clustering (explicit)

Goal:
- Detect unresolved records, suppress low-value noise, and batch similar unresolved entities for analyst efficiency.

Process:
1) Mark as unmatched when top candidate confidence is below policy threshold.
2) Apply business gates: minimum usage volume, minimum monetary exposure, age since first seen.
3) Cluster unresolved items by embedding similarity + blocking keys (title stem, contributor set, territory).
4) Generate suggested candidates and bulk resolution actions.
5) Open or update cases with SLA priority based on potential recovery and urgency.

Policy defaults:
- high_confidence_auto_link >= 0.92
- medium_review_band in [0.70, 0.92)
- unmatched_below < 0.70

### Royalty gap detection (explicit)

Goal:
- For each work/track/platform/territory/period, compare expected royalties to reported royalties and prioritize significant deviations.

Process:
1) Assemble usage evidence, reporting lines, benchmark rates, and contract/deal modifiers.
2) Compute expected usage and expected royalties.
3) Compare to reported usage and reported royalties.
4) Compute absolute and percentage gap; suppress if below de minimis threshold.
5) Score confidence from data completeness, source reliability, and match certainty.
6) Persist gap records and trigger workflow alerts.

Pseudo-code:

```python
def royalty_gap(record):
    expected_usage = estimate_usage(record.signals)
    expected_amt = expected_usage * benchmark_rate(record.platform, record.territory, record.deal_type)
    actual_amt = record.reported_amount
    gap_amt = max(0.0, expected_amt - actual_amt)
    gap_pct = gap_amt / max(expected_amt, 1e-9)
    conf = confidence_score(record)
    flag = gap_amt >= record.min_gap_amount and gap_pct >= record.min_gap_pct
    return {
        "expected": expected_amt,
        "actual": actual_amt,
        "gap_amount": gap_amt,
        "gap_pct": gap_pct,
        "confidence": conf,
        "flag": flag,
    }
```

### Unified confidence scoring framework (explicit)

Input components:
- Metadata similarity
- Fingerprint similarity
- Identity graph strength
- Source reliability (direct API, file parser, OCR confidence tier)
- Data completeness and recency

Formula:

$$
C = w_m M + w_f F + w_g G + w_s S + w_d D
$$

Where $C \in [0,1]$ and weights are tenant-policy configurable with safe defaults.

Bands and actions:
- High: $C \ge 0.90$ -> auto-link or auto-case create per policy.
- Medium: $0.70 \le C < 0.90$ -> analyst review queue.
- Low: $C < 0.70$ -> unmatched queue with clustering and watchlist.

Explainability payload requirements:
- top_contributing_signals
- negative_signals_or_conflicts
- source_references
- model and ruleset version
- human override metadata (if any)

### AI-powered metadata normalization and repair

Process:
1) Normalize text (casefold, punctuation cleanup, locale-aware transformations, featuring/remix token handling).
2) Generate candidates using deterministic keys + fuzzy retrieval + embedding retrieval.
3) Score candidates with weighted feature signals.
4) Suggest repairs with impact and confidence.
5) Route high-confidence suggestions to auto-apply policy or analyst review.

Composite score:

$$
S = w_t T + w_a A + w_d D + w_i I + w_h H - w_c C
$$

Where:
- $T$ = title similarity
- $A$ = artist/contributor similarity
- $D$ = duration proximity
- $I$ = ID consistency (ISRC/ISWC/IPI)
- $H$ = historical linkage prior
- $C$ = conflict penalty

### Hybrid short-form audio plus video fingerprinting

Process:
1) Extract audio fingerprint and visual-temporal signal from short clips.
2) Build hybrid embedding:

$$
E_{hybrid} = \alpha E_{audio} + (1 - \alpha)E_{video}
$$

3) Retrieve nearest candidates via ANN index.
4) Re-rank with metadata and identity graph constraints.
5) Emit top-k candidates with confidence and reason codes.

### Predictive black-box scoring using time-series anomalies

Process:
1) Build features: reporting lag, usage/report divergence, seasonality, territory behavior drift.
2) Fit ensemble of gradient boosting and probabilistic forecasting models.
3) Compute risk:

$$
R = P(underreport\_pattern) \times impact\_estimate
$$

4) Classify into risk tiers and generate interventions.

### Natural-language explain-my-gap summaries

Approach:
- Retrieval-grounded LLM generation over lineage-backed evidence only.
- Structured output: summary, top drivers, confidence, recommended next actions.
- Mandatory citation of source evidence IDs and AI decision audit records.

### Auto-suggested split resolutions

Process:
1) Detect conflicts across imported split sheets, registrations, statements, and historical payouts.
2) Generate candidate resolutions ranked by legal plausibility and payout impact.
3) Require explicit approval for material split changes.
4) Record full decision lineage in audit logs.

## 7. Recommended Tech Stack 2026 Edition

Backend and API:
- FastAPI (Python) for data/ML-heavy services and orchestration APIs.
- Optional NestJS (TypeScript) for high-throughput gateway edge services.
- REST + GraphQL for client interfaces; gRPC for selected internal service links.

Orchestration and queues:
- Temporal for durable orchestration and retries.
- Kafka for event streaming.
- SQS or RabbitMQ for async jobs where queue semantics differ by workload.

Data and storage:
- PostgreSQL with row-level security and pgvector.
- Snowflake or BigQuery for analytics warehouse.
- S3/GCS/Azure Blob for raw statements, media, and evidence bundles.
- OpenSearch for fuzzy search.
- Optional Neo4j for heavy graph traversals.

ML and AI:
- Python stack with scikit-learn, XGBoost, PyTorch.
- LLM integration via OpenAI or Grok API for explainability and assistant workflows.
- Vector retrieval on pgvector initially; optional dedicated vector DB as scale grows.
- Serverless workers for bursty fingerprinting and extraction tasks.

Frontend:
- Next.js (Vercel-ready) for artist/manager and analyst web interfaces.
- React Native or Flutter for mobile app experience.

Infra and delivery:
- Kubernetes for core runtime services.
- Terraform or Pulumi for IaC.
- GitHub Actions for CI/CD with staged promotion.
- OpenTelemetry + Prometheus + Grafana + centralized logs for observability.

## 8. Enhanced Security & Compliance Model

Multi-tenant isolation:
- Tenant scoping in service layer and database row-level security.
- Optional single-tenant isolation modes for enterprise catalogs.

Credential and token handling:
- Vault/KMS backed secret storage.
- Envelope encryption for tokens and integration credentials.
- Rotation policies and short-lived credentials.

Encryption and transport:
- TLS in transit across all service boundaries.
- Encryption at rest for operational DB, warehouse, and object storage.

PII and sensitive data controls:
- Data minimization, field classification, and least-privilege access.
- Full audit logs for sensitive data access and admin actions.

Access control:
- RBAC and ABAC layered permissions.
- SSO/OIDC support for enterprise tenants.
- Just-in-time support access with mandatory audit trail.

SOC 2 Type II readiness:
- Control mapping for security, availability, and confidentiality criteria.
- Change management, incident response, backup validation, and access reviews.

AI decision auditability:
- Store model/provider/version metadata for every AI-influenced decision.
- Persist prompt hash, retrieval references, output references, human override metadata.

Data residency:
- Per-tenant region pinning and policy-configurable processing boundaries.

## 9. Scalable Deployment & Cost Strategy

Architecture style:
- Modular monolith with explicit bounded contexts at launch, evolving selected domains into microservices at scale.
- Rationale: faster delivery and lower ops burden initially, while preserving extractable service seams.

Service boundary evolution:
- First extraction targets: ingestion, fingerprinting, reconciliation, and case workflows.

Scaling:
- Horizontal autoscaling for stateless APIs.
- Queue-depth and job-age autoscaling for workers.
- Dedicated compute pools for heavy fingerprint and reconciliation workloads.

Multi-region:
- Active-active edge/API.
- Region-aware data strategy by tenant compliance and SLO tier.
- Tested failover runbooks and replication monitoring.

Resilience:
- Circuit breakers, retries, idempotency keys, DLQs, replay tooling.
- PITR for relational data, object versioning, warehouse snapshots.
- Defined RTO and RPO per service tier.

Environment strategy:
- Dev, staging, prod with synthetic or masked datasets in non-prod.
- Progressive rollout and feature flag controls.

Cost strategy and usage-based guardrails:
- Meter usage by pipeline, compute, storage, LLM tokens, and connector activity.
- Per-tenant budget alerts, soft/hard caps, and overage protection policy.
- Internal cost observability dashboards for tenant and workload profitability.

## 10. Product & UX Superpowers - The Make-It-Awesome Layer

### Recovery Potential Radar
- Portfolio-level and artist-level opportunity ranking with expected dollar recovery and confidence.
- Daily reprioritization with change detection since last sync.

### Leakage Funnel storytelling visualizations
- Visual funnel from detection to payment with stage conversion metrics and drop-off explanations.
- Heatmaps by territory/platform and trend overlays.

### One-Click Fix AI suggestions
- Suggested remediations for unmatched works, metadata defects, and split inconsistencies.
- Bulk approve with policy constraints and full auditability.

### Collaborative Case Rooms
- Threaded comments, mentions, attachments, role-based approvals, and timeline playback.
- Shared evidence boards for society submissions and legal escalation.

### Mobile app with daily leakage alerts
- Push-based alerting for high-priority opportunities and connector issues.
- Quick actions: connect platform, approve suggestion, resolve assignment.

### Guided Onboarding Wizard with coverage health score
- Stepwise setup for connectors, statements, catalog checks, and split imports.
- Dynamic health score with explicit missing coverage recommendations.

### Exportable Recovery Playbook PDFs
- Generate branded reports with evidence lineage, confidence explanation, and recommended actions.
- Export in PDF, CSV, and structured API packets.

### Webhook and Zapier integrations
- Emit events for gap creation, case transitions, connector failures, and forecast changes.
- Integrate with CRM, support systems, BI stacks, and legal workflows.

### Per-tenant AI tuning sliders
- Precision vs recall controls, auto-apply threshold controls, and review routing controls.
- Safety guardrails to prevent over-automation on high-risk financial changes.

### Explainability-first UX patterns
- Why this match and why this gap panels on all key records.
- Two-click drill-down from summary cards to raw lineage evidence.

### Recovery command center for teams
- Unified queue of actions by value, urgency, and owner.
- SLA badges, blocked-state reasons, and completion analytics.

### Simulation studio
- What-if deal/rate/territory scenarios with confidence intervals.
- Compare scenarios and export recommendation briefs.

---

## Implementation Notes

- This master spec should be used as the source document for roadmap, architecture reviews, API contracts, and delivery planning.
- Each section can be decomposed into epics and milestones for phased production rollout.
