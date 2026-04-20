# XR7 Commercialization & Go-To-Market Technical Plan

**Version:** 1.0
**Date:** 2026-04-09
**Audience:** Engineering, Product, Revenue, GTM teams
**Principle:** Every commercial capability has a corresponding engineering deliverable. No revenue commitment is made without a technical plan to support it.

---

## Table of Contents

1. [Technical Roadmap: MVP → GA → Enterprise](#1-technical-roadmap-mvp--ga--enterprise)
2. [Feature Tier Breakdown](#2-feature-tier-breakdown)
3. [Pricing-Tier Architecture](#3-pricing-tier-architecture)
4. [Infrastructure for 100 / 1,000 / 10,000 Users](#4-infrastructure-for-100--1000--10000-users)
5. [Scaling Ingestion, Matching & Recovery](#5-scaling-ingestion-matching--recovery)
6. [Customer-Facing Dashboards, Reports & Exports](#6-customer-facing-dashboards-reports--exports)
7. [Customer Onboarding Automation](#7-customer-onboarding-automation)
8. [Customer Support Tooling, Logging & Auditability](#8-customer-support-tooling-logging--auditability)
9. [Developer Documentation & Partner API Access](#9-developer-documentation--partner-api-access)
10. [Commercial Readiness Checklist](#10-commercial-readiness-checklist)
11. [Launch Playbook](#11-launch-playbook)
12. [Technical GTM Risk Assessment](#12-technical-gtm-risk-assessment)

---

## 1. Technical Roadmap: MVP → GA → Enterprise

### 1.1 Stage Definitions

| Stage | Definition | Target date |
|-------|-----------|-------------|
| **MVP (Private Beta)** | Core pipeline functional for invited artists; manual onboarding; no self-serve | 2026 Q3 |
| **GA (General Availability)** | Self-serve signup; Core tier live; public API; full documentation | 2026 Q4 |
| **Pro Tier Launch** | Pro tier with advanced reconciliation, PRO integration, reporting exports | 2027 Q1 |
| **Enterprise GA** | White-label, SSO, dedicated tenancy, SOC 2 report available | 2027 Q2 |
| **Scale Milestone** | 1,000 active tenants; 100M+ statement rows processed/month | 2027 Q4 |

---

### 1.2 MVP Engineering Deliverables (by 2026 Q3)

| # | Deliverable | Owner | Done-when |
|---|------------|-------|-----------|
| M1 | Ingestion: Spotify + Apple Music + Amazon parsers | Ingestion team | 3 DSPs processed end-to-end |
| M2 | Matching: ISRC + title hybrid matching | Matching team | >85% match rate on test corpus |
| M3 | Anomaly detection: rate-deviation rule engine | ML team | Flags >90% of synthetic anomalies |
| M4 | Claims: DRAFT → SUBMITTED state machine | Claims team | Claim submits and returns DSP ref |
| M5 | Auth: JWT login + artist RBAC | Identity team | 401/403 enforced on all routes |
| M6 | Multi-tenancy: tenant_id isolation | Platform | Cross-tenant test suite passing |
| M7 | Artist portal: earnings dashboard (read-only) | Frontend | P95 load < 2s |
| M8 | Admin panel: analyst review queue | Frontend | Analyst can approve/reject claims |
| M9 | Evidence generation: PDF bundle | Recovery team | Legal-grade bundle generated |
| M10 | Manual onboarding script | DevOps | Onboard artist in < 30 min |

---

### 1.3 GA Engineering Deliverables (by 2026 Q4)

| # | Deliverable | Owner |
|---|------------|-------|
| G1 | Self-serve signup: email verification + Stripe setup | Identity + Billing |
| G2 | Ingestion: 18 DSP parsers complete | Ingestion |
| G3 | 8 PRO format parsers complete | Ingestion |
| G4 | Public OpenAPI documentation site (Redoc/Stoplight) | DevRel |
| G5 | Webhook delivery system (inbound + outbound) | Platform |
| G6 | Usage metering + billing event pipeline | Billing |
| G7 | Rate limiting (per-tier enforcement) | Platform |
| G8 | Status page (statuspage.io or self-hosted) | DevOps |
| G9 | Automated onboarding n8n workflow | Platform |
| G10 | Customer email notifications (ingestion complete, claim updates) | Platform |
| G11 | Export API: CSV/JSON statement + reconciliation exports | Reporting |
| G12 | Cookie consent + GDPR/CCPA flows (frontend) | Frontend |

---

### 1.4 Enterprise GA Deliverables (by 2027 Q2)

| # | Deliverable | Owner |
|---|------------|-------|
| E1 | SAML 2.0 / OIDC SSO integration | Identity |
| E2 | Custom RBAC role definitions API | Identity |
| E3 | Sub-tenant hierarchy (parent → label → artist) | Platform |
| E4 | Dedicated Kubernetes namespace per enterprise tenant | DevOps |
| E5 | Data residency: EU-West + APAC regions | Infrastructure |
| E6 | SIEM audit log export (Splunk / Elastic connector) | Platform |
| E7 | SOC 2 Type II audit completed; report available | Security |
| E8 | White-label deployment option (custom domain + branding) | Platform |
| E9 | Dedicated ML model per enterprise tenant | ML |
| E10 | SLA credits automation (breach detection + credit issuance) | Billing |

---

## 2. Feature Tier Breakdown

### Core (Free / Contingency-Only)

**Who:** Independent artists, small managers, solo songwriters
**Works limit:** 500
**Onboarding:** Self-serve
**Billing:** Contingency fee only (15–30% of recovery; no upfront cost)

| Feature | Available |
|---------|-----------|
| DSP statement import (5 DSPs) | ✅ |
| ISRC-based matching | ✅ |
| Basic anomaly detection | ✅ |
| Earnings dashboard | ✅ |
| Claim DRAFT + SUBMITTED | ✅ |
| Evidence PDF generation | ✅ |
| Email notifications | ✅ |
| API access (read-only, rate-limited) | ✅ |
| PRO reconciliation | ❌ |
| Advanced ML scoring | ❌ |
| Custom exports | ❌ |
| Webhook delivery | ❌ |
| Sub-tenants | ❌ |
| SSO | ❌ |
| SLA | Best effort |
| Support | Community + email (48h) |

---

### Pro ($299/month or enhanced contingency)

**Who:** Active managers, boutique labels, mid-size publishers (up to 5,000 works)

| Feature | Available |
|---------|-----------|
| All Core features | ✅ |
| DSP statement import (18 DSPs) | ✅ |
| Hybrid matching (ISRC + title + fingerprint) | ✅ |
| Full ML anomaly detection | ✅ |
| PRO reconciliation (ASCAP, BMI, PRS, SOCAN, GEMA) | ✅ |
| Advanced reporting dashboard | ✅ |
| CSV / JSON / Excel export | ✅ |
| Webhook delivery (10 endpoints) | ✅ |
| API access (read + write, 1,000 req/min) | ✅ |
| Multi-user (up to 10 seats) | ✅ |
| Email + Slack notifications | ✅ |
| Custom claim bundles | ✅ |
| Data retention: 3 years | ✅ |
| SLA | 99.5% (best-effort) |
| Support | Email + chat (8h) |

---

### Enterprise (Custom pricing)

**Who:** Major labels, publishers, collecting societies, distributors (unlimited works)

| Feature | Available |
|---------|-----------|
| All Pro features | ✅ |
| Unlimited works | ✅ |
| All 18 DSPs + custom parser onboarding | ✅ |
| All 11 PROs + foreign society integrations | ✅ |
| SAML 2.0 / OIDC SSO | ✅ |
| Custom RBAC role definitions | ✅ |
| Sub-tenant hierarchy | ✅ |
| Dedicated Kubernetes namespace | ✅ |
| Tenant-isolated ML model | ✅ |
| Data residency (US / EU / APAC) | ✅ |
| White-label deployment | ✅ |
| SIEM audit log integration | ✅ |
| SOC 2 Type II report | ✅ |
| Unlimited API access (dedicated gateway) | ✅ |
| Recovery advance priority underwriting | ✅ |
| Dedicated CSM + implementation engineer | ✅ |
| SLA | 99.9% contractual |
| Support | P0: 15min / P1: 1h / P2: 4h |

---

## 3. Pricing-Tier Architecture

### 3.1 Technical Differences by Tier

| Dimension | Core | Pro | Enterprise |
|-----------|------|-----|-----------|
| **Rate limiting** | 100 req/min | 1,000 req/min | Unlimited (dedicated GW) |
| **API auth** | Bearer JWT | Bearer JWT | JWT + API Key + SSO |
| **Tenant isolation** | Schema-level | Schema-level | Namespace-level (dedicated pods) |
| **ML model** | Shared global model | Shared global model | Tenant-isolated model |
| **Queue priority** | Low (best-effort) | Medium | High (dedicated queues) |
| **Ingestion concurrency** | 1 file at a time | 5 concurrent | Unlimited |
| **Reconciliation schedule** | Daily | Daily + on-demand | Real-time + on-demand |
| **Webhook retry** | N/A | 3 retries, 1h window | 10 retries, 24h window, dead-letter |
| **Export size limit** | 10,000 rows | 100,000 rows | Unlimited (streaming) |
| **Storage retention** | 1 year | 3 years | 7 years |
| **Audit log access** | None | 90 days web UI | 7 years + API + SIEM |

### 3.2 Billing Infrastructure

```
Stripe (payment processing + subscription management)
      │
      ├── Metered billing: ingestion rows processed (Pro tier)
      ├── Flat subscription: monthly platform fee (Pro/Enterprise)
      ├── Contingency billing: % of settled claims (all tiers)
      └── Usage-based: API calls over included quota (Enterprise overage)

Billing event pipeline:
  XR7 service → emit UsageEvent → billing-service → Stripe Meter API
```

---

## 4. Infrastructure for 100 / 1,000 / 10,000 Users

### 4.1 100 Active Tenants (MVP / Early Beta)

**Profile:** 100 artists, ~500 works each, 5 DSPs, monthly ingestion

**Database:** Single PostgreSQL 16 instance (32 vCPU, 128 GB RAM)
**App:** 3 pods per service × 8 services = 24 pods
**Redis:** Single Redis Sentinel cluster (16 GB)
**Storage:** S3, ~5 TB statement files
**Ingestion volume:** ~50M rows/month
**Cost estimate:** ~$3,500/month cloud infra

```
Kubernetes cluster: 3-node (16 vCPU, 64 GB each)
PostgreSQL: RDS db.r6g.4xlarge (single AZ)
Redis: ElastiCache r6g.large
S3: Standard tier
Celery workers: 10 workers
```

---

### 4.2 1,000 Active Tenants (GA / Scale)

**Profile:** 1,000 tenants, ~2,000 works average, 18 DSPs, daily ingestion

**Database:** PostgreSQL primary + 2 read replicas (r6g.8xlarge each)
**App:** 5 pods per service × 10 services = 50 pods; KEDA autoscaling to 150
**Redis:** Redis Cluster (3 shards × 2 replicas)
**Storage:** S3, ~200 TB
**Ingestion volume:** ~2B rows/month
**Cost estimate:** ~$22,000/month cloud infra

```
Kubernetes cluster: 12-node (32 vCPU, 128 GB each)
PostgreSQL: Multi-AZ, primary + 2 replicas
Redis Cluster: 3 shards
S3: Standard + Intelligent-Tiering for older data
Celery workers: 50 workers, auto-scale to 200
CDN: CloudFront for static assets + API response caching
```

---

### 4.3 10,000 Active Tenants (Enterprise Scale)

**Profile:** Mix of enterprise (large catalogs) + pro + core; global; real-time ingestion

**Architecture:** Multi-region (US-East, EU-West, APAC); read replicas per region; Kafka for event bus

**Database:** Citus (distributed PostgreSQL) or Aurora Global for write sharding
**App:** 20 pods base per service; KEDA scales to 500 per service
**Redis:** Redis Enterprise Cluster per region
**Storage:** S3, ~2 PB (Glacier for >1 year data)
**Ingestion volume:** ~50B rows/month
**Cost estimate:** ~$180,000/month cloud infra

```
Kubernetes: Multi-cluster (EKS per region), Karpenter for node provisioning
Database: Citus (coordinator + 8 workers) per region with logical replication for DR
Event bus: Kafka (MSK) replacing Redis Streams for event volume
CDN: CloudFront global with edge caching for API responses
ML: Dedicated GPU nodes (g5.4xlarge) for inference; model training on spot
```

---

## 5. Scaling Ingestion, Matching & Recovery

### 5.1 Ingestion Scaling

**Bottleneck at scale:** File parsing is CPU-bound; a 500 MB CSV takes 90s single-threaded.

**Solution: Chunked parallel parsing**
```
File upload → S3
     │
     ▼
Ingestion service: detect format, calculate chunk boundaries
     │
     ├── Spawn N Celery tasks (one per 100K rows)
     │   Each task: parse chunk → normalize → persist batch
     │
     └── Completion task: aggregate row count, emit ingestion.completed event
```

**Worker scaling:**
- Core: 1 concurrent file per tenant
- Pro: 5 concurrent files per tenant
- Enterprise: dedicated ingestion pod with unlimited concurrency

**Database writes:** Batch INSERT 1,000 rows per transaction. Never row-at-a-time inserts for statement data.

---

### 5.2 Matching Scaling

**Bottleneck at scale:** 50B rows/month = 19,000 matches/second at peak.

**Solution: Tiered matching pipeline**

```
Tier 1 — Exact ISRC lookup (Redis cache, <1ms)
     │ Miss →
Tier 2 — Normalized title + artist DB lookup (<10ms)
     │ Miss →
Tier 3 — Audio fingerprint lookup (Chromaprint index, <50ms)
     │ Miss →
Tier 4 — ML fuzzy match (BERT embedding similarity, <200ms)
     │ Miss →
Flag as "unmatched" for analyst review
```

**Cache strategy:** Top 10,000 ISRCs per DSP cached in Redis (covers ~60% of streaming volume due to Pareto distribution — 20% of songs = 80% of plays).

**Horizontal scaling:** Match workers are stateless; KEDA scales on `celery_queue_length{queue="matching"}` > 20 per pod.

---

### 5.3 Recovery Scaling

**Bottleneck at scale:** Evidence bundle generation is I/O-bound (reads from DB + S3, generates PDF).

**Solution:**
- Pre-generate evidence bundles for high-confidence anomalies (before analyst requests)
- Bundle generation runs on a dedicated queue with higher-memory workers
- Completed bundles cached in S3 with 30-day TTL; regenerated on request if expired
- For enterprise bulk filing (>100 claims in a bundle), use streaming PDF generation with progress webhook

---

## 6. Customer-Facing Dashboards, Reports & Exports

### 6.1 Artist / Core Dashboard

**Route:** `GET /dashboard/overview`

Panels:
- **Earnings summary:** Total reported vs. expected vs. recovered ($USD, current period)
- **DSP coverage:** Heatmap of which DSPs have recent statements imported
- **Active claims:** Count by state with trend arrow (vs. last period)
- **Recent activity feed:** Last 10 events (statement imported, anomaly found, claim filed)

**Performance target:** p95 < 2s; all data served from materialized views, refreshed every 4 hours.

---

### 6.2 Analyst / Pro Dashboard

Additional panels for Pro+ tiers:
- **Reconciliation quality score:** Match rate % by DSP (trend, 12 months)
- **Anomaly breakdown:** Type × DSP × severity heatmap
- **Claims aging table:** Claims by state and days open; highlight > 90 days
- **Recovery funnel:** Identified → Submitted → Under Review → Settled ($USD amounts at each stage)
- **PRO reconciliation variance:** Expected vs. received by PRO (monthly, 12-month trend)

---

### 6.3 Report Templates

| Report | Tier | Format | Trigger |
|--------|------|--------|---------|
| Earnings Statement | Core+ | PDF, CSV | Monthly auto-send |
| Royalty Reconciliation Summary | Pro+ | PDF, Excel | Quarterly auto-send |
| DSP Underpayment Analysis | Pro+ | PDF | On-demand |
| Claims Activity Report | Core+ | CSV, PDF | Monthly auto-send |
| Anomaly Detection Report | Pro+ | PDF | Weekly auto-send |
| PRO Gap Analysis | Pro+ | PDF, Excel | Quarterly |
| Annual Recovery Report | Core+ | PDF | Annual auto-send |
| Custom date range | Enterprise | CSV, JSON, Excel, Parquet | On-demand API |

### 6.4 Export API

```
GET /exports/statements?from=2025-01-01&to=2025-12-31&format=csv
GET /exports/reconciliations?dsp=spotify&format=excel
GET /exports/claims?state=SETTLED&format=json
GET /exports/earnings?period=2025-Q4&format=parquet   ← Enterprise only
```

Large exports (>100K rows) are asynchronous:
```json
POST /exports/statements?async=true
→ 202 Accepted
{
  "export_id": "exp_abc123",
  "status": "pending",
  "download_url": null
}

GET /exports/exp_abc123/status
→ 200 OK
{
  "export_id": "exp_abc123",
  "status": "ready",
  "download_url": "https://s3.../exports/exp_abc123.csv?signed=...",
  "expires_at": "2026-04-10T12:00:00Z"
}
```

---

## 7. Customer Onboarding Automation

### 7.1 Self-Serve Onboarding Flow (Core / Pro)

```
User signs up (email + password)
     │
     ▼
Email verification
     │
     ▼
Stripe checkout (card on file; $0 charge for Core)
     │
     ▼
Tenant provisioning (automated):
  1. Create tenant record (DB)
  2. Create default analyst user
  3. Provision S3 prefix
  4. Set rate limit tier in Redis
  5. Send welcome email with getting-started guide
     │
     ▼
First-time setup wizard (frontend):
  Step 1: Import first DSP statement (drag & drop)
  Step 2: Wait for ingestion & matching (~2 min)
  Step 3: Review earnings dashboard
  Step 4: Review first anomaly (if found)
  Step 5: (Optional) Connect additional DSPs
```

**Total time to first value:** < 10 minutes.

---

### 7.2 n8n Onboarding Automation Workflow

```json
Workflow: "05_customer_onboarding_automation"
Trigger: Webhook (tenant_created event from XR7 auth service)

Nodes:
  1. [Webhook] Receive tenant_created event
     {tenant_id, email, tier, created_at}

  2. [HTTP Request] POST /internal/tenants/{id}/provision
     Trigger infrastructure provisioning (S3 prefix, rate limits, DB schema)

  3. [Wait] 30 seconds (provisioning completes)

  4. [HTTP Request] GET /internal/tenants/{id}/status
     Confirm provisioning succeeded

  5. [IF] tier == "enterprise"
     TRUE → Node 6a (Enterprise path)
     FALSE → Node 6b (Self-serve path)

  6a. [HTTP Request] POST /internal/cs/assign-csm
      Assign dedicated CSM; create onboarding Asana project

  6b. [Email] Send "Welcome to XR7" email via SendGrid
      Template: welcome_self_serve_{{tier}}

  7. [HTTP Request] POST /internal/analytics/identify
     Track new tenant in Segment

  8. [Slack] Post to #new-tenants channel
     "New {{tier}} tenant: {{email}} | Works: TBD"

  9. [Wait] 3 days

  10. [HTTP Request] GET /internal/tenants/{id}/first-ingestion-status
      Check if first statement has been imported

  11. [IF] first_ingestion_complete == false
      TRUE → Send "Getting started" reminder email
      FALSE → Send "First results ready" email with dashboard link
```

---

### 7.3 Enterprise Onboarding Automation

Enterprise onboarding is semi-automated with human touchpoints:

```
Day 0: Tenant created → auto-provision enterprise namespace
Day 1: CSM assigned → Asana project created → kickoff calendar invite sent
Day 3: SSO config form sent automatically via email
Day 5 (SSO configured): Auto-test SSO login → confirm success
Day 7: Bulk catalog import enabled → API keys generated → welcome docs sent
Day 14: Ingestion health check → email report to CSM if <80% match rate
Day 30: Automated QBR prep report generated → sent to CSM
```

---

## 8. Customer Support Tooling, Logging & Auditability

### 8.1 Support Tier Matrix

| Tier | Channel | SLA | Tools |
|------|---------|-----|-------|
| Core | Email only | 48h | Help centre + email queue (Intercom) |
| Pro | Email + live chat | 8h | Intercom + admin panel access |
| Enterprise | Email + chat + phone | P0: 15min, P1: 1h | Dedicated CSM + internal support console |

### 8.2 Support Console (Internal)

A read-only internal console for support analysts at `/internal/support`:

**Tenant lookup:**
- Search by tenant_id, email, or company name
- View: tier, provisioning status, last login, total works, total claims

**Ingestion health:**
- Last 5 ingestion runs per DSP: status, row count, error count, duration

**Claims status:**
- All claims for tenant: state, amount, DSP, last action, assigned analyst

**Audit log viewer:**
- Last 200 audit events for tenant
- Filter by action type, user, date range
- Export to CSV

**Impersonation mode (admin only):**
- Support analyst can view tenant portal as that tenant (read-only, logged to audit)
- Impersonation events get a separate `impersonation` audit log type

### 8.3 Error Tracking

```
Application errors → Sentry (with tenant_id + user_id context)
     │
     ├── P0/P1 errors → PagerDuty alert
     ├── Repeated errors (>10/hour per tenant) → Slack #support-alerts
     └── New error signature → GitHub issue creation (nightly-analysis.yml)
```

### 8.4 Support Logging Requirements

Every support action is logged:
```sql
INSERT INTO audit_events (entity_type, action, user_id, tenant_id, new_value)
VALUES (
  'support_session',
  'support.impersonation.started',
  :support_analyst_user_id,
  :target_tenant_id,
  '{"reason": "Customer reported missing claims", "ticket_id": "INT-4421"}'
);
```

---

## 9. Developer Documentation & Partner API Access

### 9.1 Public Documentation Site

**Stack:** Mintlify or Redocly (OpenAPI auto-generated) + custom MDX for guides.
**URL:** `https://docs.xr7.artistos.io`

**Sections:**
- Quick Start (< 5 minutes to first API call)
- Authentication (JWT + API Keys)
- Core Concepts (Works, Recordings, Statements, Claims)
- API Reference (auto-generated from `openapi/openapi.json`)
- Guides: Import Statement, Reconcile, File Claim, Export Data
- Webhooks: Events, Signatures, Retry Behaviour
- SDKs: Python, Node.js, cURL examples
- Changelog
- Status page link

### 9.2 API Key System (Partner Access)

```python
# Partner API keys (separate from user JWTs)
# Keys are scoped to specific permissions and rate limits

class APIKey(Base):
    key_id: UUID
    tenant_id: UUID
    key_hash: str          # bcrypt hash of the actual key (never stored plaintext)
    name: str              # human label: "Production ingestion key"
    permissions: list[str] # ["statements:read", "statements:import"]
    rate_limit: int        # req/min; tier default unless overridden
    last_used_at: datetime
    expires_at: datetime   # None = non-expiring (discouraged for partner use)
    created_by: UUID
    revoked: bool
```

**Key format:** `xr7_live_<random64chars>` (prefix enables secret scanning by GitHub + GitGuardian)

### 9.3 Developer Sandbox

- URL: `https://sandbox.xr7.artistos.io`
- Sandbox contains synthetic statement data (1 year, 5 DSPs, 1,000 works, 3 PROs)
- Sandbox API keys issued at signup; never charged; never touch real DSP data
- Sandbox is automatically reset every 7 days to a known state
- All API responses include `X-Environment: sandbox` header

### 9.4 SDK Generation

SDKs auto-generated from the OpenAPI spec using `openapi-generator`:

```bash
# Python SDK
openapi-generator generate \
  -i openapi/openapi.json \
  -g python \
  -o sdk/python/ \
  --additional-properties=packageName=xr7

# Node.js SDK
openapi-generator generate \
  -i openapi/openapi.json \
  -g typescript-axios \
  -o sdk/typescript/
```

SDKs are published to PyPI (`xr7-client`) and npm (`@xr7/client`) on each API version tag.

---

## 10. Commercial Readiness Checklist

### Product & Features
- [ ] MVP feature set complete (M1–M10 from Section 1.2)
- [ ] Core, Pro, and Enterprise tiers technically differentiated and enforced in code
- [ ] Rate limiting enforced per tier (tested with integration tests)
- [ ] Billing events emitting to Stripe for metered features
- [ ] Contingency fee calculation verified against at least 5 real claim settlements
- [ ] Self-serve signup flow completes < 10 min (user-tested with 5 external users)
- [ ] First-value achieved in < 10 min for 80% of beta testers

### Infrastructure & Reliability
- [ ] 99.9% availability target achievable (load test at 2× peak load passing)
- [ ] Auto-scaling tested: scale up under ingestion burst, scale down after
- [ ] Failover tested: primary DB failover < 2 min (tested in staging)
- [ ] DR plan tested: full region restore < 1 hour (tested in staging)
- [ ] Status page live and integrated with monitoring

### Data & Compliance
- [ ] DSP parsers for top-5 DSPs (Spotify, Apple, Amazon, YouTube, Tidal) stable
- [ ] PRO parsers for ASCAP + BMI stable
- [ ] GDPR consent flows implemented (cookie banner + data subject rights API)
- [ ] SOC 2 audit initiated (for Enterprise GA timeline)
- [ ] Privacy policy and ToS reviewed by legal

### Security
- [ ] All items in `docs/security_hardening_plan.md` Section 12 verified
- [ ] Penetration test completed (external firm) before GA
- [ ] Vulnerability disclosure policy published on docs site

### Developer Experience
- [ ] Public API documentation live at docs.xr7.artistos.io
- [ ] Developer sandbox operational and auto-resetting
- [ ] Python + Node.js SDKs published to PyPI and npm
- [ ] Changelog published and maintained

### Support & Operations
- [ ] Support ticketing system (Intercom) configured with tier-based routing
- [ ] On-call rotation and escalation policy configured
- [ ] Runbooks written for all critical alert types
- [ ] SLA credits automation tested (breach → auto-credit in Stripe)

### GTM Alignment
- [ ] Pricing page live on marketing site
- [ ] Sales CRM integrated with XR7 tenant provisioning API (deal won → tenant created)
- [ ] Customer success dashboard live for CSMs
- [ ] Launch announcement prepared (blog, press release, social)

---

## 11. Launch Playbook

### T-8 Weeks: Final Beta Gate

**Engineering:**
- [ ] Beta-to-GA migration test: 50 beta tenants migrated to GA infrastructure without data loss
- [ ] Performance baseline published (p50/p95/p99 by endpoint)
- [ ] Known issues list triaged; no P0/P1 open bugs

**Product:**
- [ ] Pricing confirmed with leadership; Stripe products created
- [ ] Feature flags: GA features behind flag; flip sequentially over launch week
- [ ] Beta tenant comms: "GA is coming" email sent

---

### T-4 Weeks: Soft Launch (Invite-Only GA)

- [ ] Invite-only signup live (100 invites issued)
- [ ] Public API docs live
- [ ] Status page live
- [ ] Intercom support live
- [ ] Monitor: daily error rate review, support ticket volume

---

### T-1 Week: Launch Prep

- [ ] Capacity confirmed: load test at 10× MVP peak passing
- [ ] On-call hand-off to war-room rotation (engineering + product + support)
- [ ] Blog post + press release finalized and scheduled
- [ ] Launch email sequence scheduled in Intercom/HubSpot

---

### Launch Day (T-0)

**Hour 0:**
1. Flip feature flag: `public_signup_enabled = true`
2. Send launch email to waitlist
3. Publish blog post and press release
4. Post to social channels (LinkedIn, X, Product Hunt)
5. War room open (Zoom bridge; engineering + product + support online)

**Hour 1–4 monitoring:**
- Check: signup rate (target: >50 new accounts)
- Check: error rate (target: <0.1%)
- Check: p99 API latency (target: <500ms)
- Check: Celery queue depth (target: <100)
- Check: support ticket volume (target: < 20)

**Hour 4 decision gate:**
If any P0/P1 active → evaluate reverting `public_signup_enabled` flag
Otherwise → declare launch successful, reduce war room to on-call

---

### T+2 Weeks: Post-Launch Review

- [ ] Cohort analysis: first-week retention (users who completed first ingestion)
- [ ] Support ticket analysis: top 5 issues by volume → prioritize fixes
- [ ] Performance review: p99 latency trends post-launch
- [ ] Billing validation: Stripe events reconcile with XR7 usage logs

---

## 12. Technical GTM Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **DSP format change breaks parser** | HIGH (DSPs update formats 2–3×/year) | MEDIUM (ingestion paused for affected DSP) | Format versioning registry; alert on parse failure; parser update SLA: 48h |
| **Match rate below 85% at GA** | MEDIUM | HIGH (users don't see value without matches) | Hold GA if match rate <85% on production data; beta testing threshold enforced |
| **Stripe billing integration failure** | LOW | HIGH (no revenue collected; legal risk) | Billing integration tested with 100 transactions in staging; fallback manual billing process documented |
| **PRO data quality worse than expected** | MEDIUM | MEDIUM (reconciliation inaccurate) | Start with ASCAP/BMI only; add PROs incrementally; manual review layer for first 3 months |
| **Security vulnerability discovered post-launch** | LOW | CRITICAL | Penetration test before GA; vulnerability disclosure policy; hotfix process <4h SLA |
| **Competitor launches similar product** | MEDIUM | MEDIUM (pricing pressure) | Moat is data + ML flywheel, not features; accelerate enterprise sales pipeline |
| **Data residency requirement blocks EU deal** | HIGH (GDPR endemic in music industry) | HIGH (enterprise deals lost) | EU region must be available at Enterprise GA; not optional |
| **Celery queue depth spikes on ingestion burst** | MEDIUM | MEDIUM (delayed processing; SLA breach) | KEDA autoscaling tested at 10× peak; queue depth alert at 200 |
| **Startup metrics don't reach 1K tenants by 2027 Q4** | MEDIUM | HIGH (Series A timing) | Growth strategy must include partner-sourced tenants (labels onboarding all their artists at once) |
| **Support ticket volume overwhelms team** | MEDIUM (launch spike) | MEDIUM (CSAT drop) | Self-serve help centre + AI-powered chat deflection before GA |
