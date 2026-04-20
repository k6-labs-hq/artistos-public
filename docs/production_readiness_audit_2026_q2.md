# ArtistOS Production Readiness Audit — 2026 Q2

## Audit Date
April 19, 2026

## Executive Summary
This audit reviews a production-grade SaaS platform for artist royalty recovery with extensive backend, frontend, SDK, infrastructure, and ML capabilities. Based on completed work, this document identifies **missing but expected** features for enterprise buyers, CTOs, auditors, and compliance teams.

---

## ✅ Already Completed (Context)
- Health checks, readiness probes, dependency checks
- Queue-depth HPA scaling for Celery
- Smoke tests between staging/prod
- SQLAlchemy pool configuration
- File upload validation and malware scanning
- Idempotency middleware
- Redis caching for heavy dashboard queries
- Outbound webhook system
- Bulk insert ingestion
- Tenant isolation middleware
- Backup + disaster recovery automation
- Circuit breaker patterns for external APIs
- Migration rollback testing
- Email template system
- API versioning middleware
- Full-text search
- CSV/PDF export
- RBAC expansion
- Scheduled report generation
- API docs enhancements
- Mobile-responsive UI
- Feature flags
- Onboarding validation checkpoints
- Query performance monitoring
- WebSocket dashboard updates
- Internationalization
- Pre-commit hooks + editorconfig
- Environment variable documentation
- Database indexing
- Refund + chargeback logic
- Payment retry logic
- Request body size limits
- Dependency health checks
- Claim status validation
- Immutable audit logs
- Currency validation
- Graceful Celery shutdown
- Query timeouts
- Rate limiting
- Billing invariant checks
- Pydantic schema validation
- Unique constraints
- Frontend 404 fallback
- VIP/Founder program logic
- Trolley API circuit breaker
- Immutable soft-delete
- Claim amount invariant checks
- Unified statement normalizer
- GDPR data export/erase endpoints
- Trivy filesystem security scanning

---

## 🔴 Missing Production-Critical Tasks

### Security & Compliance

1. **SEC-001: Security Headers Middleware**
   - Priority: CRITICAL
   - HSTS, CSP, X-Frame-Options, X-Content-Type-Options headers not implemented
   - Documented in security_hardening_plan.md but not wired into app.py as middleware
   - Risk: Clickjacking, XSS, MITM attacks

2. **SEC-002: Encryption at Rest for PII**
   - Priority: CRITICAL
   - Database-level encryption for sensitive fields (email, SSN, bank details)
   - Required for SOC 2, GDPR, PCI compliance
   - Current: PostgreSQL encryption not enforced

3. **SEC-003: Secret Rotation Automation**
   - Priority: HIGH
   - JWT signing key rotation (90-day policy documented but not automated)
   - Database credential rotation (Vault dynamic secrets not configured)
   - API key rotation workflow missing

4. **SEC-004: Container Image Vulnerability Scanning**
   - Priority: HIGH
   - Trivy/Snyk scanning for Docker images in CI/CD pipeline
   - Current: Filesystem scan exists, container scan missing
   - Required for enterprise security audits

5. **SEC-005: API Key Rotation Endpoint**
   - Priority: MEDIUM
   - Allow users to regenerate API keys on-demand
   - Audit log for all key rotation events

6. **SEC-006: Session Management Hardening**
   - Priority: MEDIUM
   - Concurrent session limits per user
   - Session invalidation on password change
   - Device fingerprinting for anomaly detection

7. **SEC-007: SQL Injection Prevention Audit**
   - Priority: HIGH
   - Systematic review of all raw SQL queries
   - Add sqlfluff linting to CI for SQL validation
   - Currently: SQLAlchemy ORM used but raw SQL exists in some query patterns

8. **SEC-008: Secrets Scanning in Git History**
   - Priority: MEDIUM
   - GitGuardian or TruffleHog in pre-commit and CI
   - Currently: No automated secret leak detection

9. **SEC-009: PII Anonymization for Non-Production**
   - Priority: MEDIUM
   - Production DB dumps must anonymize PII before staging/dev restore
   - Faker-based anonymization script for artist names, emails, addresses

10. **SEC-010: SOC 2 Type II Documentation**
    - Priority: HIGH (Enterprise SSP requirement)
    - Complete control narratives for security, availability, confidentiality
    - Penetration test schedule (annual)
    - Vendor risk assessment process

---

### Infrastructure & Reliability

11. **INFRA-001: Distributed Tracing Implementation**
    - Priority: CRITICAL
    - OpenTelemetry instrumentation exists in docs but not wired into app.py
    - FastAPI, SQLAlchemy, Redis, Celery tracing not enabled
    - Required for production debugging and SLO tracking

12. **INFRA-002: Multi-Region Deployment**
    - Priority: MEDIUM (Enterprise feature)
    - Active-active or active-passive failover architecture
    - Data residency middleware exists but not deployed to multiple regions

13. **INFRA-003: Database Read Replicas**
    - Priority: HIGH
    - Read-heavy dashboard queries offload to replicas
    - Connection pool routing for primary (writes) vs replica (reads)

14. **INFRA-004: Connection Pool Monitoring**
    - Priority: MEDIUM
    - SQLAlchemy pool exhaustion alerts
    - Prometheus metrics for active/idle connections

15. **INFRA-005: Disaster Recovery Runbooks**
    - Priority: HIGH
    - Region failover procedure (step-by-step)
    - Database restore SLA validation (tested quarterly)
    - Backup encryption verification

16. **INFRA-006: Chaos Engineering Tests**
    - Priority: MEDIUM
    - Monthly chaos game days (kill pods, inject latency, network partitions)
    - LitmusChaos or Chaos Mesh for Kubernetes

17. **INFRA-007: Service Mesh (Optional)**
    - Priority: LOW (Nice-to-have for microservices)
    - Istio or Linkerd for mTLS, traffic management, observability
    - Current: Microservices migration plan exists but not executed

18. **INFRA-008: Load Balancer Health Check Tuning**
    - Priority: MEDIUM
    - Readiness vs liveness probe differentiation
    - Graceful shutdown testing (30s drain period)

19. **INFRA-009: Zero-Downtime Deployment Validation**
    - Priority: HIGH
    - Blue-green or canary deployment strategy
    - Smoke tests run against new deployment before traffic shift

20. **INFRA-010: Database Backup Encryption**
    - Priority: HIGH (Compliance)
    - RDS encrypted backups enabled
    - Backup restore drill (quarterly)

---

### Observability & Monitoring

21. **OBS-001: Error Budget Tracking**
    - Priority: HIGH
    - Define error budgets per service (99.9% = 43.2 min/month)
    - Prometheus alerting when budget 50% consumed
    - Burn rate alerts for rapid error budget depletion

22. **OBS-002: SLI/SLO Dashboard**
    - Priority: HIGH
    - Grafana dashboard showing:
      - API latency p50/p95/p99
      - Error rate (4xx/5xx)
      - Availability (uptime percentage)
      - Ingestion throughput

23. **OBS-003: Distributed Tracing UI**
    - Priority: MEDIUM
    - Jaeger or Tempo UI for trace visualization
    - Currently: OTel collector not deployed

24. **OBS-004: Log Aggregation & Retention**
    - Priority: HIGH
    - Centralized logging (Loki, CloudWatch Logs, or Datadog)
    - 90-day retention policy with archival to S3
    - Log sampling for high-volume endpoints

25. **OBS-005: Cost Monitoring Dashboard**
    - Priority: MEDIUM
    - AWS Cost Explorer or custom Prometheus metrics
    - Budget alerts per service/environment
    - Cost attribution by tenant

26. **OBS-006: Performance Regression Testing**
    - Priority: MEDIUM
    - Automated load tests in CI (Locust, k6, or Gatling)
    - Performance budget gates (p95 latency must not regress >10%)

27. **OBS-007: Business KPI Metrics**
    - Priority: MEDIUM
    - Artists onboarded/day
    - Claims submitted/recovered
    - Revenue protected (aggregate)
    - Publish to Prometheus for dashboards

28. **OBS-008: Dead Letter Queue Monitoring**
    - Priority: MEDIUM
    - Celery task failure visibility
    - Webhook retry DLQ monitoring
    - Alerts when DLQ depth > threshold

29. **OBS-009: API Latency Percentile Tracking**
    - Priority: HIGH
    - Per-endpoint latency histograms (not just p95)
    - Slowest queries dashboard (APM-style)

30. **OBS-010: Custom Alert Escalation Policy**
    - Priority: MEDIUM
    - PagerDuty or Opsgenie integration
    - On-call rotation schedule
    - Alert severity tiers (P0/P1/P2/P3)

---

### API & Integration

31. **API-001: API Deprecation Strategy**
    - Priority: HIGH
    - `Sunset` and `Deprecation` headers for deprecated endpoints
    - 6-month deprecation notice policy documented
    - SDK version compatibility matrix

32. **API-002: Webhook Retry Dead Letter Queue**
    - Priority: MEDIUM
    - Exponential backoff with max 5 retries
    - DLQ for permanently failed webhooks
    - Admin console for manual retry

33. **API-003: API Rate Limit Headers**
    - Priority: MEDIUM
    - `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers
    - Currently: Rate limiting exists but headers missing

34. **API-004: OpenAPI Schema Validation Middleware**
    - Priority: MEDIUM
    - Validate requests/responses against OpenAPI spec at runtime
    - Prevent schema drift

35. **API-005: SDK Versioning & Deprecation Notices**
    - Priority: MEDIUM
    - SDK changelog with breaking changes highlighted
    - Deprecation warnings in SDK code comments
    - Migration guides for major version bumps

36. **API-006: Batch API Endpoints**
    - Priority: LOW (Nice-to-have)
    - Bulk operations: batch create claims, batch upload statements
    - Reduce N+1 request patterns for integrations

37. **API-007: API Usage Analytics**
    - Priority: MEDIUM
    - Per-tenant API usage dashboard
    - Endpoint popularity ranking
    - Integration partner usage tracking

38. **API-008: Third-Party Integration Testing**
    - Priority: MEDIUM
    - Mock servers for DSP APIs (Spotify, Apple Music)
    - Contract tests for external dependencies

39. **API-009: OAuth2 Scope Management**
    - Priority: MEDIUM
    - Granular scopes for read-only vs write access
    - Scope validation on every protected endpoint

40. **API-010: GraphQL API Layer (Optional)**
    - Priority: LOW
    - Strawberry or Graphene for GraphQL over REST
    - For complex frontend queries with nested relationships

---

### Data Model & Database

41. **DB-001: Soft Delete Consistency Audit**
    - Priority: HIGH
    - Ensure all models with `deleted_at` respect soft delete in queries
    - Automated test: verify no hard deletes on production tables

42. **DB-002: Foreign Key Cascade Review**
    - Priority: HIGH
    - Audit all FK constraints for correct ON DELETE behavior
    - Prevent accidental cascade deletes of critical data

43. **DB-003: Data Retention Policies**
    - Priority: HIGH (GDPR compliance)
    - Auto-delete anonymized records after N years
    - Archive old claims/statements to cold storage (S3)

44. **DB-004: Database Partitioning Strategy**
    - Priority: MEDIUM
    - Partition large tables by time (statements, events)
    - Improve query performance and backup speed

45. **DB-005: Materialized Views for Reporting**
    - Priority: MEDIUM
    - Pre-aggregate dashboard metrics (earnings, anomalies)
    - Refresh strategy (hourly or incremental)

46. **DB-006: Database Query EXPLAIN Plan Review**
    - Priority: HIGH
    - Quarterly review of slowest queries (pgBadger)
    - Add missing indexes based on production query patterns

47. **DB-007: Time-Series Data Optimization**
    - Priority: MEDIUM
    - Consider TimescaleDB extension for time-series events
    - Improve compression and query speed for royalty events

48. **DB-008: Data Migration Testing Suite**
    - Priority: HIGH
    - Automated rollback tests for Alembic migrations
    - Pre-production migration dry-run on anonymized data

49. **DB-009: Historical Data Archival**
    - Priority: MEDIUM
    - Archive statements/events older than 3 years to S3
    - Keep only metadata in primary DB

50. **DB-010: Connection Retry Logic**
    - Priority: HIGH
    - Exponential backoff for DB connection failures
    - Circuit breaker for database unavailability

---

### Frontend & UX

51. **FE-001: Accessibility (WCAG 2.1 AA)**
    - Priority: HIGH (Legal compliance)
    - Screen reader compatibility
    - Keyboard navigation for all interactive elements
    - Color contrast ratios validated

52. **FE-002: Performance Budgets**
    - Priority: MEDIUM
    - Lighthouse CI in GitHub Actions
    - Fail build if performance score < 80

53. **FE-003: Error Boundary Implementation**
    - Priority: MEDIUM
    - React error boundaries for graceful fallback
    - Error reporting to Sentry or similar

54. **FE-004: Offline Mode / PWA**
    - Priority: LOW (Nice-to-have)
    - Service worker for offline caching
    - Progressive Web App manifest

55. **FE-005: Analytics Integration**
    - Priority: MEDIUM
    - Google Analytics or Mixpanel for user behavior tracking
    - Conversion funnel analysis (signup → onboarding → first claim)

56. **FE-006: A/B Testing Framework**
    - Priority: LOW
    - LaunchDarkly or Optimizely for experiments
    - Feature flag integration for gradual rollouts

57. **FE-007: User Session Replay**
    - Priority: LOW (Support tool)
    - FullStory or LogRocket for debugging user issues

58. **FE-008: Client-Side Error Tracking**
    - Priority: HIGH
    - Sentry SDK for JavaScript error reporting
    - Source maps uploaded for production debugging

59. **FE-009: Dark Mode Support**
    - Priority: LOW (UX enhancement)
    - CSS variables for light/dark themes

60. **FE-010: Keyboard Navigation Compliance**
    - Priority: HIGH (Accessibility)
    - Tab order validation
    - Focus indicators for all controls

---

### DevOps & CI/CD

61. **DEVOPS-001: Deployment Rollback Automation**
    - Priority: HIGH
    - One-click rollback to previous Docker image
    - Automated health check after rollback

62. **DEVOPS-002: Canary Deployment Strategy**
    - Priority: MEDIUM
    - Deploy to 5% of traffic first, monitor, then 100%
    - Flagger or Argo Rollouts for progressive delivery

63. **DEVOPS-003: Blue-Green Deployment**
    - Priority: MEDIUM
    - Zero-downtime deployments with instant rollback
    - Kubernetes namespaces or AWS ECS task definitions

64. **DEVOPS-004: Database Migration Safety Checks**
    - Priority: HIGH
    - Pre-flight checks: validate migration on staging first
    - Automated rollback script for failed migrations

65. **DEVOPS-005: Dependency Vulnerability Scanning**
    - Priority: HIGH
    - Dependabot or Snyk for Python/Node.js dependencies
    - Auto-merge security patches for low-risk updates

66. **DEVOPS-006: Infrastructure as Code Tests**
    - Priority: MEDIUM
    - Terraform validate + plan in CI
    - Terratest for integration testing

67. **DEVOPS-007: Terraform Drift Detection**
    - Priority: MEDIUM
    - Daily `terraform plan` to detect manual changes
    - Alerts on drift from source of truth

68. **DEVOPS-008: Build Artifact Signing**
    - Priority: MEDIUM (Supply chain security)
    - Sigstore/cosign for Docker image signing
    - SLSA provenance attestation

69. **DEVOPS-009: Staging Environment Parity**
    - Priority: HIGH
    - Staging mirrors production config (same DB version, resource limits)
    - Automated smoke tests on every staging deploy

70. **DEVOPS-010: Post-Deploy Smoke Tests**
    - Priority: HIGH
    - Automated E2E tests run after production deployment
    - Fail = instant rollback

---

### SDK & Developer Experience

71. **SDK-001: SDK Code Examples Library**
    - Priority: MEDIUM
    - Python/TypeScript code snippets for common use cases
    - Hosted on docs site with runnable samples

72. **SDK-002: Postman/Insomnia Collections**
    - Priority: MEDIUM
    - Pre-configured API collection for manual testing
    - Published to Postman Public Workspace

73. **SDK-003: API Changelog**
    - Priority: HIGH
    - Keep changelog.md in sync with OpenAPI version bumps
    - Link from SDK docs to changelog

74. **SDK-004: SDK Deprecation Notices**
    - Priority: MEDIUM
    - Deprecated methods log warnings
    - Migration guides linked in error messages

75. **SDK-005: Developer Sandbox Environment**
    - Priority: MEDIUM
    - Free tier with rate limits for testing
    - Separate sandbox.artistos.io subdomain

76. **SDK-006: API Playground/Console**
    - Priority: LOW (Nice-to-have)
    - Interactive API explorer (Swagger UI or custom)

77. **SDK-007: Webhook Testing Tools**
    - Priority: MEDIUM
    - Webhook.site integration or mock server
    - Webhook signature validation examples

78. **SDK-008: CLI Tool for Common Operations**
    - Priority: LOW
    - `xr7 cli upload-statement`, `xr7 cli list-claims`
    - Useful for integrations and scripts

79. **SDK-009: Local Development Docker Compose**
    - Priority: HIGH
    - One-command local stack (API, DB, Redis, Celery)
    - Currently: Makefile targets exist but not complete

80. **SDK-010: SDK Error Code Documentation**
    - Priority: MEDIUM
    - Enum of error codes with descriptions
    - Troubleshooting guide for common errors

---

### Compliance & Legal

81. **COMP-001: Terms of Service Acceptance Tracking**
    - Priority: HIGH
    - Log which version of ToS user accepted
    - Re-prompt on major ToS updates

82. **COMP-002: GDPR Consent Management**
    - Priority: HIGH (EU compliance)
    - Cookie consent banner
    - Granular consent preferences (analytics, marketing)

83. **COMP-003: Data Processing Agreements (DPAs)**
    - Priority: HIGH (B2B requirement)
    - DPA template for enterprise customers
    - Subprocessor list published

84. **COMP-004: Privacy Policy Versioning**
    - Priority: MEDIUM
    - Version control for privacy policy changes
    - Notify users of material changes

85. **COMP-005: Cookie Consent Management**
    - Priority: MEDIUM (GDPR)
    - OneTrust or Cookiebot integration
    - Respect Do Not Track headers

86. **COMP-006: Data Breach Notification System**
    - Priority: HIGH (Legal requirement)
    - 72-hour notification workflow for GDPR
    - Automated email to affected users

87. **COMP-007: Compliance Audit Logging**
    - Priority: HIGH
    - Immutable logs for all PII access
    - Retention: 7 years for financial data

88. **COMP-008: Right to Be Forgotten Implementation**
    - Priority: HIGH (GDPR)
    - Full data deletion across all systems (DB, backups, logs)
    - 30-day retention for audit trail

89. **COMP-009: Data Portability API**
    - Priority: MEDIUM (GDPR)
    - Export user data in machine-readable format (JSON)
    - Currently: Export endpoint exists but not comprehensive

90. **COMP-010: Regulatory Reporting Exports**
    - Priority: MEDIUM
    - Financial reporting exports for auditors (SOX compliance)
    - Transaction logs for regulatory review

---

### Business Logic & Domain

91. **BIZ-001: Fraud Detection System**
    - Priority: HIGH
    - Anomaly detection beyond royalty discrepancies
    - Flag suspicious login patterns, duplicate accounts

92. **BIZ-002: Duplicate Payment Prevention**
    - Priority: CRITICAL
    - Idempotency keys for payment operations
    - Currently: Idempotency middleware exists for API but not payments

93. **BIZ-003: Account Hierarchy (Organizations)**
    - Priority: MEDIUM (Enterprise feature)
    - Multi-artist management under single org
    - Team access exists but not full org hierarchy

94. **BIZ-004: Custom Contract Terms**
    - Priority: MEDIUM
    - Allow non-standard contingency fees per artist
    - Currently: 12% hardcoded in billing engine

95. **BIZ-005: Bulk Operations Audit Trail**
    - Priority: MEDIUM
    - Log all bulk CSV uploads with diff before/after
    - Roll back bulk ingestion if anomalies detected

96. **BIZ-006: Revenue Recognition Logic**
    - Priority: HIGH (Financial compliance)
    - Accrual accounting for contingency fees
    - Deferred revenue handling for advances

97. **BIZ-007: Tax Calculation Integration**
    - Priority: MEDIUM (US compliance)
    - TaxJar or Avalara for sales tax
    - Currently: Currency validation exists but no tax logic

98. **BIZ-008: Multi-Currency Support Expansion**
    - Priority: MEDIUM
    - Support for EUR, GBP, JPY, AUD beyond USD
    - Exchange rate API integration

99. **BIZ-009: Settlement Reconciliation**
    - Priority: HIGH
    - Match Trolley payouts to claim records
    - Alert on settlement discrepancies

100. **BIZ-010: Payment Method Verification**
     - Priority: MEDIUM
     - Micro-deposit verification for bank accounts
     - PayPal/Venmo integration for faster payouts

---

## Implementation Priority Matrix

### Tier 1: Launch Blockers (Complete Before GA)
- SEC-001: Security Headers Middleware
- SEC-002: Encryption at Rest for PII
- INFRA-001: Distributed Tracing
- OBS-001: Error Budget Tracking
- OBS-002: SLI/SLO Dashboard
- API-001: API Deprecation Strategy
- DB-001: Soft Delete Consistency Audit
- DB-002: Foreign Key Cascade Review
- FE-001: Accessibility (WCAG 2.1 AA)
- DEVOPS-001: Deployment Rollback Automation
- COMP-001: Terms of Service Acceptance Tracking
- COMP-002: GDPR Consent Management
- BIZ-002: Duplicate Payment Prevention

### Tier 2: Enterprise Requirements (Q3 2026)
- SEC-004: Container Image Scanning
- SEC-010: SOC 2 Type II Documentation
- INFRA-003: Database Read Replicas
- INFRA-005: Disaster Recovery Runbooks
- OBS-006: Performance Regression Testing
- API-002: Webhook Retry DLQ
- DB-003: Data Retention Policies
- FE-008: Client-Side Error Tracking
- DEVOPS-005: Dependency Vulnerability Scanning
- COMP-008: Right to Be Forgotten
- BIZ-006: Revenue Recognition Logic
- BIZ-009: Settlement Reconciliation

### Tier 3: Competitive Differentiators (Q4 2026)
- INFRA-002: Multi-Region Deployment
- INFRA-006: Chaos Engineering
- OBS-005: Cost Monitoring
- API-006: Batch API Endpoints
- DB-004: Database Partitioning
- FE-004: Offline Mode / PWA
- DEVOPS-002: Canary Deployments
- SDK-005: Developer Sandbox
- BIZ-003: Account Hierarchy
- BIZ-007: Tax Calculation Integration

---

## Execution Plan

### Sprint 6 (Current): Foundation Hardening
**Week 1-2:**
1. Implement security headers middleware (SEC-001)
2. Wire distributed tracing into app.py (INFRA-001)
3. Add container image scanning to CI (SEC-004)
4. Create API deprecation headers utility (API-001)
5. Add performance regression tests to CI (OBS-006)

**Week 3-4:**
6. SLI/SLO dashboard (Grafana + Prometheus) (OBS-002)
7. Error budget tracking alerts (OBS-001)
8. Soft delete audit script (DB-001)
9. Foreign key cascade review (DB-002)
10. Data retention policy implementation (DB-003)

### Sprint 7: Compliance & Security
1. Encryption at rest for PII fields (SEC-002)
2. GDPR consent management UI (COMP-002)
3. ToS acceptance tracking (COMP-001)
4. Right to be forgotten automation (COMP-008)
5. Privacy policy versioning (COMP-004)

### Sprint 8: Reliability & Observability
1. Database read replicas (INFRA-003)
2. Disaster recovery runbooks + quarterly drill (INFRA-005)
3. Log aggregation infrastructure (OBS-004)
4. Cost monitoring dashboard (OBS-005)
5. Dead letter queue monitoring (OBS-008)

---

## Acceptance Criteria

A task is considered **production-ready** when:
- [ ] Implementation complete with unit + integration tests
- [ ] Documentation updated (handbook, runbook, or README)
- [ ] Monitoring/alerting configured (if applicable)
- [ ] Security review passed (if security-related)
- [ ] Performance impact validated (no regressions)
- [ ] Rolled out to staging and validated for 1 week
- [ ] Runbook updated with rollback procedure
- [ ] CTO/security team sign-off (for Tier 1 items)

---

## Next Steps

1. Review this audit with engineering lead and CTO
2. Socialize Tier 1 tasks with product team
3. Break down epics into GitHub issues with labels:
   - `production-critical`
   - `enterprise-ssp`
   - `compliance`
   - `security`
   - `observability`
   - `developer-experience`
4. Begin Sprint 6 execution with Tier 1 tasks
5. Schedule quarterly audit reviews

---

## Sign-Off

- **Engineering Lead:** ___________ Date: __________
- **CTO:** ___________ Date: __________
- **Security Lead:** ___________ Date: __________
- **Compliance Officer:** ___________ Date: __________
