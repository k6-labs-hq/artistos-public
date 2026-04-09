# XR7 Enterprise Edition Architecture

**Version:** 1.0  
**Audience:** Enterprise sales, solutions architects, CTO-level buyers, technical evaluators  
**Scope:** XR7 Enterprise features, architecture, compliance posture, and commercial differentiation  
**Compliance targets:** SOC 2 Type II, ISO 27001, GDPR, CCPA, MMA 2018

---

## Table of Contents

1. [Enterprise vs. Core Feature Comparison](#1-enterprise-vs-core-feature-comparison)
2. [Multi-Tenant Enterprise Architecture](#2-multi-tenant-enterprise-architecture)
3. [SOC 2 & ISO 27001 Aligned Controls](#3-soc-2--iso-27001-aligned-controls)
4. [High Availability & Failover](#4-high-availability--failover)
5. [Horizontal Scaling Architecture](#5-horizontal-scaling-architecture)
6. [Enterprise SSO (SAML 2.0 & OIDC)](#6-enterprise-sso-saml-20--oidc)
7. [Role-Based Access Control (RBAC)](#7-role-based-access-control-rbac)
8. [Audit Logging](#8-audit-logging)
9. [Data Residency](#9-data-residency)
10. [Enterprise SLAs](#10-enterprise-slas)
11. [Enterprise Onboarding Workflow](#11-enterprise-onboarding-workflow)
12. [Enterprise Architecture Diagram](#12-enterprise-architecture-diagram)
13. ["Why XR7 Enterprise Wins" Narrative](#13-why-xr7-enterprise-wins-narrative)

---

## 1. Enterprise vs. Core Feature Comparison

| Feature | Core (Indie/Artist) | Enterprise |
|---------|-------------------|------------|
| **Artists / works supported** | Up to 500 works | Unlimited |
| **DSPs supported** | 18 DSPs | 18 DSPs + custom integrations |
| **PROs supported** | 11 PROs | 11 PROs + bespoke foreign societies |
| **Ingestion frequency** | Daily | Real-time + daily + on-demand |
| **API access** | Public API (rate-limited) | Dedicated API gateway; no shared rate limits |
| **White-label deployment** | No | Yes — full white label with custom domain |
| **Data residency** | US-West (shared) | US, EU, APAC — your choice |
| **SSO** | Username/password + MFA | SAML 2.0 + OIDC + custom IdP integration |
| **RBAC** | Artist / Analyst / Admin | Custom role definitions; attribute-based policies |
| **Multi-entity tenancy** | Single catalog | Sub-tenants: labels, imprints, individual artists all isolated |
| **Audit log export** | 90-day web UI | 7-year retention; SIEM integration; custom export |
| **SLA** | 99.5% availability (best effort) | 99.9% availability (contractual, with credits) |
| **Support** | Community + email (48h) | Dedicated CSM; 4-hour response; 24/7 P0 hotline |
| **Recovery advance** | Standard | Priority underwriting + custom contingency terms |
| **Compliance reports** | None | SOC 2 Type II report; ISO 27001 certificate |
| **Custom ML models** | Shared model | Tenant-isolated models trained on client data |
| **Onboarding** | Self-serve | Dedicated implementation engineer; 90-day program |
| **Contract term** | Month-to-month | Multi-year with volume pricing |
| **Pricing model** | Contingency (15–30%) | Contingency + platform license + volume discounts |

---

## 2. Multi-Tenant Enterprise Architecture

### 2.1 Tenancy Model

XR7 Enterprise uses a **silo-pod** model for enterprise customers: a dedicated namespace in the shared Kubernetes cluster, with isolated database schema, isolated Redis keyspace, and isolated S3 bucket prefix.

For the largest enterprise customers (>500K works), an option for **dedicated cluster deployment** is available.

```
┌── XR7 Enterprise Cluster ────────────────────────────────────────────────────────────┐
│                                                                                        │
│  ┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐  │
│  │  Enterprise Pod: UMPG                │  │  Enterprise Pod: Sony Music           │  │
│  │  ┌────────────────────────────────┐  │  │  ┌────────────────────────────────┐  │  │
│  │  │ Namespace: xr7-umpg            │  │  │  │ Namespace: xr7-sony            │  │  │
│  │  │ DB Schema: umpg                │  │  │  │ DB Schema: sony                │  │  │
│  │  │ Redis DB: 3                    │  │  │  │ Redis DB: 5                    │  │  │
│  │  │ S3 prefix: /umpg/              │  │  │  │ S3 prefix: /sony/              │  │  │
│  │  │ ML model: umpg-v12             │  │  │  │ ML model: sony-v7              │  │  │
│  │  └────────────────────────────────┘  │  │  └────────────────────────────────┘  │  │
│  └──────────────────────────────────────┘  └──────────────────────────────────────┘  │
│                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│  │  Shared Infrastructure                                                            │ │
│  │  API Gateway (Istio) │ Prometheus │ Grafana │ Vault │ PostgreSQL (per-schema)     │ │
│  └──────────────────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Sub-Tenant Hierarchy

Enterprise customers often manage multiple entities (a major label with sub-labels, a publisher with multiple catalogs):

```
Enterprise Tenant: Universal Music Publishing Group (UMPG)
├── Sub-tenant: Interscope Records
│   ├── Artist: Drake
│   ├── Artist: Lady Gaga
│   └── Artist: Billie Eilish
├── Sub-tenant: Republic Records
│   ├── Artist: Taylor Swift
│   └── Artist: The Weeknd
└── Sub-tenant: UMPG Direct (publishing, not recordings)
    └── Works: 50,000 owned compositions
```

Each sub-tenant inherits the parent tenant's SSO and RBAC configuration but has its own data isolation.

### 2.3 Database Isolation

```sql
-- Enterprise uses PostgreSQL schemas for isolation
-- All xr7-umpg data lives in the 'umpg' schema
SET search_path TO umpg, public;

-- Cross-schema queries explicitly denied by application layer
-- A request authenticated to 'umpg' can NEVER issue queries against 'sony' schema
```

---

## 3. SOC 2 & ISO 27001 Aligned Controls

### 3.1 SOC 2 Trust Service Criteria

| TSC | Control | XR7 Implementation |
|-----|---------|-------------------|
| **CC6.1** | Logical access controls | JWT RBAC, tenant isolation, mTLS |
| **CC6.2** | Authentication | MFA enforced for admin roles; SSO via SAML/OIDC |
| **CC6.3** | Removed access | User deprovisioning API; SSO group sync; immediate token revocation |
| **CC6.6** | Intrusion detection | WAF + anomaly detection on API traffic; Falco for runtime security |
| **CC7.1** | System monitoring | Prometheus/Grafana; PagerDuty alerting; error budget tracking |
| **CC7.2** | Incident response | Documented in `docs/security_hardening_plan.md` Section 11 |
| **CC8.1** | Change management | Git-gated; PRs with 2 approvals; protected branches |
| **A1.2** | Capacity management | KEDA autoscaling; load testing before each release |
| **C1.1** | Confidentiality | Encryption at rest + in transit; PII masking in logs |
| **PI1.1** | Processing integrity | SHA-256 file hashing; HMAC-sealed evidence bundles |

### 3.2 ISO 27001 Annex A Mapping

| Annex A | Domain | XR7 Control |
|---------|--------|-------------|
| A.9 | Access control | RBAC + SAML/OIDC SSO; Vault for secrets |
| A.10 | Cryptography | TLS 1.3; AES-256; RS256 JWT; column encryption for PII |
| A.12 | Operations security | CI/CD pipelines; change management; backup/restore tested |
| A.13 | Communications security | mTLS; network policies; CORS; firewall rules |
| A.14 | System acquisition / development | Secure SDLC; security in CI/CD; code review checklist |
| A.16 | Incident management | P0/P1/P2/P3 response procedures; post-mortem culture |
| A.17 | Business continuity | Multi-AZ; DR in `docs/disaster_recovery_backup_strategy.md` |
| A.18 | Compliance | GDPR data mapping; CCPA notices; audit log retention |

---

## 4. High Availability & Failover

### 4.1 Multi-AZ Deployment

```
Region: us-east-1 (primary)
├── AZ us-east-1a:  2 app pods, 1 DB primary, 1 Redis primary
├── AZ us-east-1b:  2 app pods, 1 DB replica (hot standby), 1 Redis replica
└── AZ us-east-1c:  2 app pods, 1 DB replica (async), 1 Redis replica

Region: eu-west-1 (EU data-residency tenants)
├── AZ eu-west-1a:  2 app pods, 1 DB primary, 1 Redis primary
└── AZ eu-west-1b:  2 app pods, 1 DB replica, 1 Redis replica
```

### 4.2 Failover Procedures

**PostgreSQL failover:**
- Tool: Patroni (automatic leader election)
- Failover time: < 30 seconds (automated)
- RTO for DB failure: < 2 minutes
- RPO: < 5 seconds (synchronous replica in same region)

**Application failover:**
- Kubernetes ReplicaSet ensures minimum 3 pods
- Pod disruption budget: no more than 1 pod unavailable during maintenance
- Rolling deployment: Kubernetes rolling update with 0-downtime

**Redis failover:**
- Redis Sentinel (or Redis Cluster for enterprise tier)
- Automatic leader election: < 15 seconds
- No data loss for write-acknowledged data (AOF persistence)

### 4.3 Disaster Recovery

Full DR plan documented at `docs/disaster_recovery_backup_strategy.md`.

**RTO / RPO targets for Enterprise:**
| Scenario | RTO | RPO |
|----------|-----|-----|
| Single pod failure | < 30s | 0 |
| Availability zone failure | < 5 min | < 1 min |
| Full region failure | < 1 hour | < 15 min |
| Data corruption | < 4 hours | < 24 hours |

---

## 5. Horizontal Scaling Architecture

### 5.1 Stateless Application Layer

All XR7 microservices are stateless — no local state. Session data in Redis. File uploads directly to S3. This allows horizontal scaling by adding pods without any coordination.

### 5.2 KEDA Autoscaling

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: xr7-matching-scaler
spec:
  scaleTargetRef:
    name: xr7-matching
  minReplicaCount: 2
  maxReplicaCount: 50
  triggers:
    - type: prometheus
      metadata:
        serverAddress: http://prometheus:9090
        metricName: celery_queue_length
        query: celery_queue_length{queue="matching"}
        threshold: "20"   # scale up when queue depth > 20 per pod
```

### 5.3 Read Replicas for Reporting

Reporting queries (high-cardinality reconciliation aggregations) route to read replicas:
```python
# SQLAlchemy routing: reporting sessions use replica
class ReplicaSession(Session):
    bind = replica_engine
```

### 5.4 Capacity Benchmarks

| Load | Pods | Throughput | p99 Latency |
|------|------|-----------|------------|
| Baseline | 2 per service | 50 req/s | 120ms |
| Medium | 5 per service | 250 req/s | 180ms |
| Peak (ingestion burst) | 20 matching pods | 1,200 matches/s | 280ms |
| Theoretical max | 50 pods | 6,000 matches/s | <500ms |

---

## 6. Enterprise SSO (SAML 2.0 & OIDC)

### 6.1 SSO Architecture

```
Enterprise User
      │
      ▼
[Enterprise IdP]  ← SAML 2.0 or OIDC Provider
  (Okta, Azure AD, PingFederate, Google Workspace)
      │
      │  SAML Assertion / ID Token
      ▼
[XR7 SSO Adapter]
  • Validates assertion / token
  • Maps IdP groups → XR7 roles
  • Issues XR7 JWT
  • Logs auth event to audit_events
      │
      ▼
[XR7 Application]
```

### 6.2 SAML 2.0 Configuration

XR7 acts as the **Service Provider (SP)**:
```xml
<!-- XR7 SP Metadata exposed at: /auth/saml/metadata -->
<EntityDescriptor entityID="https://xr7.artistos.io/auth/saml">
  <SPSSODescriptor AuthnRequestsSigned="true" WantAssertionsSigned="true">
    <AssertionConsumerService
      Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
      Location="https://xr7.artistos.io/auth/saml/acs"
      index="0"/>
    <SingleLogoutService
      Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
      Location="https://xr7.artistos.io/auth/saml/logout"/>
  </SPSSODescriptor>
</EntityDescriptor>
```

**Required SAML Attributes:**
- `email` — maps to XR7 user email
- `name` — maps to XR7 user display name
- `groups` — maps to XR7 role (configurable mapping per enterprise tenant)

### 6.3 OIDC Configuration

```python
# Enterprise tenant OIDC configuration (stored in Vault, per-tenant)
OIDC_CONFIG = {
    "client_id": "xr7-enterprise-client",
    "discovery_url": "https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration",
    "scope": "openid email profile groups",
    "group_claim": "groups",   # Azure AD group IDs → XR7 roles
    "group_mapping": {
        "royalty-analysts": "analyst",
        "catalog-admins": "admin",
        "artist-portal": "artist",
    }
}
```

### 6.4 JIT Provisioning

If an SSO user authenticates for the first time:
1. XR7 creates a new user record automatically (Just-In-Time provisioning)
2. Role is assigned from the IdP group mapping
3. Welcome email sent to the new user
4. Audit log entry created: `user.created.sso`

---

## 7. Role-Based Access Control (RBAC)

### 7.1 Enterprise RBAC Model

Enterprise customers can define **custom roles** with fine-grained permissions:

```json
{
  "role": "royalty_analyst_read_only",
  "description": "Can view all reconciliation data but cannot file or modify claims",
  "permissions": [
    "statements:read",
    "reconciliations:read",
    "anomalies:read",
    "claims:read",
    "evidence:read"
  ],
  "denied": [
    "claims:write",
    "claims:submit",
    "users:manage",
    "settings:write"
  ]
}
```

### 7.2 Permission Taxonomy

| Resource | Actions |
|---------|---------|
| `statements` | `read`, `import`, `delete` |
| `reconciliations` | `read`, `run`, `approve`, `delete` |
| `anomalies` | `read`, `acknowledge`, `escalate` |
| `claims` | `read`, `create`, `update`, `submit`, `withdraw`, `delete` |
| `evidence` | `read`, `generate`, `seal`, `download` |
| `recoveries` | `read`, `advance`, `settle` |
| `artists` | `read`, `create`, `update`, `delete` |
| `users` | `read`, `create`, `update`, `delete`, `manage_roles` |
| `settings` | `read`, `write` |
| `audit_logs` | `read`, `export` |
| `reports` | `read`, `generate`, `schedule` |

### 7.3 Attribute-Based Policies (ABAC)

For the most complex enterprise requirements, XR7 supports attribute-based conditions:

```python
# Example: An analyst can only access claims for artists they are assigned to
@require_permission("claims:read", condition=lambda user, claim: claim.assigned_analyst == user.id)
async def get_claim(claim_id: str, user: User = Depends(current_user)):
    ...
```

---

## 8. Audit Logging

### 8.1 Enterprise Audit Log Features

Enterprise customers receive enhanced audit log capabilities beyond the standard offering:

| Feature | Core | Enterprise |
|---------|------|-----------|
| Retention | 90 days web UI | 7 years; queryable for 1 year, archived for 6 |
| Export format | CSV via web UI | CSV, JSON, NDJSON; S3 sync; API |
| SIEM integration | No | Yes — Splunk, Elastic, Sumologic connectors |
| Real-time streaming | No | Yes — Kafka / Kinesis stream |
| Immutability guarantee | DB constraints | Write-once S3 bucket (S3 Object Lock) |
| Field-level change history | No | Yes — old_value / new_value on every update |

### 8.2 SIEM Integration

```yaml
# Fluent Bit configuration for Splunk HEC
[OUTPUT]
    Name        splunk
    Match       audit.*
    Host        ${SPLUNK_HEC_HOST}
    Port        8088
    Splunk_Token ${SPLUNK_HEC_TOKEN}
    TLS         On
    TLS.Verify  On
```

### 8.3 Audit Report Templates

Pre-built audit report templates for compliance reviews:

- **"Monthly access review"** — All user login events; failed login attempts; role changes
- **"Claims integrity report"** — All claim state transitions with author and timestamp
- **"Data access by user"** — Every query with row counts; for compliance investigations
- **"Admin actions log"** — All privileged operations over a date range

---

## 9. Data Residency

### 9.1 Available Regions

| Region | Cloud Provider | Covers |
|--------|---------------|--------|
| **US-West** | AWS us-west-2 | US-based tenants; default |
| **US-East** | AWS us-east-1 | US financial tenants; secondary |
| **EU-West** | AWS eu-west-1 (Ireland) | EU GDPR-scoped tenants |
| **EU-Central** | AWS eu-central-1 (Frankfurt) | German-law tenants (GEMA, GVL) |
| **APAC** | AWS ap-southeast-1 (Singapore) | APAC-based rightholders |

### 9.2 Data Residency Guarantees

When an enterprise customer selects a region:
1. All statement files stored in S3 in that region
2. All database data stored in PostgreSQL in that region
3. No data replication to other regions
4. Kafka/Redis in the same region
5. Application servers in the same region (not cross-region calls for primary data paths)
6. Documented in enterprise contract addendum

### 9.3 GDPR Compliance

- Data Processing Agreement (DPA) available for EU tenants
- Data Subject Access Request (DSAR) API: `GET /gdpr/subject-data?email=...` returns all data for a data subject
- Right to Erasure: `DELETE /gdpr/erase?email=...` pseudonymizes all PII for a subject; claim data retained for legal obligation
- Data map maintained in `docs/data_retention_privacy_compliance.md`

---

## 10. Enterprise SLAs

### 10.1 Availability SLA

| Tier | Availability | Monthly downtime budget | Credits |
|------|-------------|------------------------|---------|
| Enterprise Standard | 99.9% | 43.2 min/month | 10% monthly fee per 0.1% breach |
| Enterprise Premium | 99.95% | 21.6 min/month | 15% monthly fee per 0.05% breach |
| Dedicated (isolated cluster) | 99.99% | 4.3 min/month | 25% monthly fee per breach |

### 10.2 Support SLA

| Priority | Description | Response time | Resolution target |
|----------|------------|--------------|------------------|
| **P0** | System-wide outage; data inaccessible | 15 minutes | 2 hours |
| **P1** | Major feature failure; claims filing blocked | 1 hour | 8 hours |
| **P2** | Performance degradation; non-critical failure | 4 hours | 24 hours |
| **P3** | Questions; minor issues; feature requests | 8 hours | Best effort |

### 10.3 Data SLA

- **Statement ingestion:** Files uploaded before 23:59 UTC processed by 08:00 UTC next day (99.5% target)
- **Reconciliation freshness:** Reconciliation data reflects statements within 4 hours of ingestion (99.0% target)
- **Evidence generation:** Evidence bundles generated within 30 seconds of request (99.5% target)

---

## 11. Enterprise Onboarding Workflow

### Phase 1: Technical Kickoff (Days 1–5)

- Assign dedicated implementation engineer
- Collect: DSP statement samples (last 3 periods), PRO membership details, catalog export (works + recordings)
- Provision enterprise tenant: namespace, schema, credentials
- Configure SSO (SAML/OIDC) with client's IdP
- Set data residency region

### Phase 2: Data Onboarding (Days 6–30)

- Ingest historical statements (up to 3 years of history)
- Import catalog (works, recordings, parties) via bulk API
- Configure custom DSP parsers if non-standard formats
- Initial reconciliation run on historical data
- Analyst review: verify match quality; tune ML confidence threshold

### Phase 3: Pilot Claims (Days 31–60)

- Identify top 10 recovery opportunities from historical data
- File pilot claims in "review" mode (no live submission until approved)
- Analyst + client reviews: validate accuracy of identified underpayments
- Client approves first live submissions

### Phase 4: Steady State (Days 61–90)

- Configure automated ingestion schedule
- Set up n8n workflows for regular reconciliation cycles
- Configure alerting and dashboard access for client team
- Train client analysts on XR7 platform
- Conduct first quarterly business review (QBR)

### Post-Onboarding: Ongoing

- Monthly QBR with Customer Success Manager
- Quarterly security review + SOC 2 report delivery
- Annual contract renewal + pricing review

---

## 12. Enterprise Architecture Diagram

```mermaid
graph TB
    subgraph "Enterprise Customers"
        UMPG[UMPG (Major Publisher)]
        Sony[Sony Music]
        Indie[Independent Label]
    end

    subgraph "XR7 Enterprise Gateway"
        WAF[WAF / DDoS Protection]
        LB[Global Load Balancer]
        GW[API Gateway\nIstio Ingress]
    end

    subgraph "Identity Layer"
        SSO[SSO Adapter\nSAML 2.0 / OIDC]
        VAULT[HashiCorp Vault\nSecrets + PKI]
        IDP1[Okta\nUMPG IdP]
        IDP2[Azure AD\nSony IdP]
    end

    subgraph "Enterprise Pod: UMPG (us-east-1)"
        NS_UMPG[Namespace: xr7-umpg]
        DB_UMPG[(PostgreSQL\nSchema: umpg\nReplica x2)]
        REDIS_UMPG[(Redis Sentinel\numpg keyspace)]
        S3_UMPG[(S3: /umpg/\nSSE-KMS)]
        ML_UMPG[ML Worker\numpg-model-v12]
    end

    subgraph "Enterprise Pod: Sony (eu-west-1)"
        NS_SONY[Namespace: xr7-sony]
        DB_SONY[(PostgreSQL\nSchema: sony\nGDPR Region)]
        REDIS_SONY[(Redis Sentinel\nsony keyspace)]
        S3_SONY[(S3 EU: /sony/\nGDPR Compliant)]
    end

    subgraph "Shared Infrastructure"
        PROM[Prometheus]
        GRAFANA[Grafana]
        JAEGER[Jaeger Tracing]
        LOKI[Loki Logs]
        PAGER[PagerDuty]
    end

    subgraph "Audit & Compliance"
        AUDIT_DB[(Audit Events DB\nWrite-Once)]
        SIEM[SIEM Integration\nSplunk / Elastic]
        COLD[(S3 Cold Storage\n7-Year Retention)]
    end

    UMPG -->|SAML SSO| IDP1
    Sony -->|OIDC| IDP2
    IDP1 -->|Assertion| SSO
    IDP2 -->|ID Token| SSO
    SSO --> GW

    UMPG -->|API Requests| WAF
    Sony -->|API Requests| WAF
    Indie -->|API Requests| WAF
    WAF --> LB --> GW

    GW -->|Routes by tenant| NS_UMPG
    GW -->|Routes by tenant| NS_SONY

    NS_UMPG --> DB_UMPG
    NS_UMPG --> REDIS_UMPG
    NS_UMPG --> S3_UMPG
    NS_UMPG --> ML_UMPG

    NS_SONY --> DB_SONY
    NS_SONY --> REDIS_SONY
    NS_SONY --> S3_SONY

    GW --> VAULT
    NS_UMPG --> VAULT
    NS_SONY --> VAULT

    NS_UMPG --> AUDIT_DB
    NS_SONY --> AUDIT_DB
    AUDIT_DB --> SIEM
    AUDIT_DB --> COLD

    NS_UMPG --> PROM
    NS_SONY --> PROM
    PROM --> GRAFANA
    PROM --> PAGER
    NS_UMPG --> JAEGER
    NS_SONY --> JAEGER
```

---

## 13. "Why XR7 Enterprise Wins" Narrative

**XR7 Enterprise is not a bigger version of the artist portal. It is a completely different system designed for organizations running catalogs at institutional scale.**

A major label or publishing administrator has unique problems that no artist-focused tool can solve:

**Problem 1: Catalog scale.** UMPG administers over 3 million compositions. Reconciling 3 million works against 18 DSPs, 11 PROs, and dozens of foreign societies is not an analyst problem — it is a data engineering problem. XR7's event-driven pipeline processes at 1,200 match operations per second and scales horizontally to any catalog size.

**Problem 2: Organizational complexity.** A major label isn't a single entity. It's dozens of labels, imprints, and sub-publishers, each with their own rights, analysts, and reporting requirements. XR7's sub-tenant hierarchy reflects this reality: UMPG's Republic Records team sees only Republic's catalog; Interscope sees only Interscope's. Parent-level reporting aggregates everything.

**Problem 3: Compliance burden.** Publishing administrators are subject to fiduciary duties to their clients (artists). They need to demonstrate, on demand, that every royalty calculation was correct and every recovery opportunity was pursued. XR7's 7-year immutable audit trail, field-level change history, and pre-built compliance reports transform a multi-week audit into a one-click export.

**Problem 4: Security requirements.** Enterprise contracts routinely require SOC 2 Type II certification, GDPR data processing agreements, data residency controls, and SSO. XR7 Enterprise ships with all of this — not as add-ons, but as core design decisions in the architecture.

**Problem 5: Integration into existing infrastructure.** An enterprise doesn't want a new portal; they want their analysts to use their existing Okta workspace, their existing Splunk SIEM, their existing Tableau dashboards. XR7 Enterprise fits into what they already have, not the other way around.

**The result:** Publishing administrators who deploy XR7 Enterprise process their full catalog reconciliation in hours rather than quarters, recover royalties their teams would never have found manually, satisfy compliance obligations without custom engineering, and integrate into their existing enterprise workflows on day one.

**XR7 Enterprise wins because it was architecturally designed for enterprise from the start — not retrofitted.**
