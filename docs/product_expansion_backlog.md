# Product Expansion Backlog

This backlog translates market-driven feature priorities into phased, execution-ready work.

## Prioritization Principles

- Underpayments are widespread; detection-to-recovery velocity matters most.
- Artists choose products that provide transparency and visible progress.
- API partnerships move slowly; workflows must deliver value without them.
- Evidence quality directly impacts legal outcomes and trust.

## Phase 1: High Priority (Quick Wins and Core Experience)

### 1) Mobile/responsive dashboard expansion

Goal:
Deliver a production-grade responsive frontend for `/dashboard/ui` across mobile, tablet, and desktop.

Scope:
- Responsive layout and navigation for all dashboard sections.
- Mobile-first cards for leakage, in pursuit, deposits, deadlines, and activity feed.
- Performance budget for low-bandwidth usage.

Acceptance signals:
- No horizontal scrolling at 360px viewport width.
- Core dashboard actions remain reachable within 2 taps from home view.
- Lighthouse mobile performance score >= 80 on staging baseline.

### 2) Key event notifications (email/SMS)

Goal:
Notify users in near real-time for high-value events.

Scope:
- Notification templates and triggers for:
  - anomaly detected
  - urgent SOL deadline
  - claim status advanced
  - deposit settled
- Per-artist channel preferences and quiet hours.
- Delivery status logging and retry policy.

Acceptance signals:
- Trigger-to-send latency p95 < 60 seconds for queued notifications.
- Delivery events persisted for auditability.
- Users can disable specific notification categories.

### 3) Bulk upload and batch processing

Goal:
Enable ingestion of multi-year statement history efficiently.

Scope:
- Multi-file upload endpoint and job model.
- Idempotency keys and duplicate detection.
- Progress endpoint with per-file parse status.

Acceptance signals:
- Batch of 100 CSV files processes without API timeout.
- Failed files do not block successful files in same batch.
- Users can retry only failed files.

### 4) Visual charts and confidence bands

Goal:
Add visual analytics directly to dashboard UX.

Scope:
- Earnings trend chart with forecast and confidence intervals.
- Leakage by category over time.
- Recoverable vs recovered trajectory chart.

Acceptance signals:
- Charts render on both desktop and mobile breakpoints.
- Time filters (30d, 90d, 12m, all) update within p95 < 500ms for cached queries.
- Confidence intervals include clear legend/tooltips.

### 5) Exportable reports (PDF/CSV)

Goal:
Allow artists/managers/attorneys to export audit-ready summaries.

Scope:
- CSV export for machine-readable metrics.
- PDF export for board/legal sharing.
- Export sections:
  - total leakage
  - recovered vs potential
  - claim pipeline
  - catalog health breakdown

Acceptance signals:
- Exports include generation timestamp and artist scope.
- PDF output remains readable for 1-page and multi-page cases.
- CSV schema versioning included in metadata.

### 6) Contract ingestion improvements (OCR + clause highlighting)

Goal:
Improve extraction quality from scanned agreements and surface actionable clauses.

Scope:
- OCR fallback path for image-heavy/scanned PDFs.
- Clause highlighting for rate, recoupment, and audit-right language.
- Confidence scores and low-confidence warnings for manual review.

Acceptance signals:
- OCR path succeeds on representative scanned contracts in test corpus.
- Highlighted clauses map to text spans in extracted output.
- Endpoint returns per-clause confidence and review flag.

## Phase 2: Competitive Differentiation

### 7) Semi-automated pull fallbacks

- Add secure OAuth connectors where platform terms permit.
- Provide guided browser-assisted import for unsupported portals.
- Preserve strict credential isolation and token rotation.

### 8) Collaborative role-based access

- Introduce roles: `artist`, `manager`, `attorney`.
- Add permission matrix and scoped record visibility.
- Add access audit log for sensitive actions.

### 9) Benchmark comparisons

- Build anonymized cohorts by catalog profile.
- Return percentile insights for rates/recovery performance.
- Enforce minimum cohort size to prevent re-identification.

### 10) Success stories and trust metrics

- Publish aggregate metrics: total recovered, average uplift, median cycle time.
- Auto-refresh public stats from approved, privacy-safe aggregates.

### 11) Self-service claim templates

- Pre-filled dispute letters/emails by anomaly subtype.
- Include evidence references and amount calculations.
- Export to PDF or copy-ready email body.

### 12) International currency and tax handling

- Normalize non-USD statements with dated FX rates.
- Add baseline withholding tax estimator by country/treaty profile.
- Display gross, withheld, net, and confidence notes.

## Phase 3: Strategic

### 13) API partnership program

- Prioritize one major PRO/distributor integration pilot.
- Define partnership readiness package (security, compliance, usage evidence).
- Build adapter layer so future partners plug in with minimal rework.

### 14) Immutable lineage extension

- Optional append-only anchoring for packet and chain hashes.
- Keep existing hashing/signature pipeline as default path.

### 15) Predictive recovery scoring

- Model total recoverable value per artist using catalog and historical outcomes.
- Expose explainability factors in response payload.

### 16) Community and education layer

- In-app playbooks for statement retrieval and dispute literacy.
- Contextual education for SOL urgency and common leakage patterns.

### 17) White-label B2B offering

- Multi-tenant controls, branding, and client-level reporting.
- Portfolio views across multiple artists per organization.

### 18) Audit-rights workflow automation

- Generate formal audit demand letters from templates.
- Track response windows, objections, and escalation stages.

## Suggested Delivery Sequence (Next 2 Quarters)

Quarter 1:
- Mobile dashboard
- Key event notifications
- Bulk upload and batch ingestion
- Dashboard charts

Quarter 2:
- Exportable reports
- OCR + clause highlighting
- Role-based access
- Claim templates

## Dependencies and Risks

- Notification deliverability depends on provider setup and sender reputation.
- OCR quality varies by scan quality and legal document formatting.
- Benchmarking requires enough data volume for privacy-safe cohorting.
- OAuth/portal automation is constrained by each platform's policy terms.

## Tracking Recommendation

Track each backlog item with:
- owner
- milestone
- API/frontend status
- test coverage
- launch gate criteria
