# Production Deployment Guide

This guide covers production deployment standards for XR7 services and data pipelines.

## Environments

- Development: local and shared dev stack.
- Staging: production-like topology, masked data only.
- Production: multi-tenant workload with region-aware controls.

## Deployment Strategy

- Use progressive delivery with staged promotion (dev -> staging -> prod).
- Use feature flags to gate new API and data model behaviors.
- Use canary release by tenant cohorts for high-impact changes.

## Pre-Deployment Checklist

- Migration scripts reviewed and tested in staging.
- API contracts and SDKs regenerated where applicable.
- SLO dashboards and alerts validated.
- Rollback strategy documented for app and schema changes.
- Security checks and dependency scans passing.

## Runtime Reliability Controls

- Idempotency on all ingestion and reconciliation write workflows.
- Queue retry policies with DLQ and replay tooling.
- Circuit breakers for external connector dependencies.
- Autoscaling policies based on queue depth and request latency.

## Data and Migration Safety

- Run additive schema migrations before enabling new write paths.
- Backfill data in controlled batches with metrics and audit logs.
- Validate post-migration counts and query performance.
- Snapshot backups before major migration waves.

## Security and Compliance Controls

- Enforce tenant isolation and least-privilege access.
- Encrypt in transit and at rest.
- Log privileged access and AI-influenced decisions.
- Maintain evidence for SOC2 controls and operational reviews.

## Incident Response and Rollback

- Define severity model and escalation matrix.
- For application regressions: rollback deployment and disable feature flags.
- For schema issues: stop new writes, use fallback paths, execute recovery playbook.
- Run post-incident review with remediation tracking.

## Market Readiness Launch Gates

- Product readiness: key workflows validated end-to-end.
- Reliability readiness: SLOs met and alerting tuned.
- Security readiness: no unresolved critical vulnerabilities.
- Data readiness: reconciliation quality and explainability coverage targets met.
- GTM readiness: support runbooks and launch collateral complete.

## Companion References

- docs/xr7_master_specification_2026_2027.md
- docs/xr7_execution_epics_and_tickets.md
- docs/xr7_database_migration_rollout_plan.md
