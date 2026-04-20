# XR7 Microservices Migration Plan

**Version:** 1.0
**Date:** April 2026
**Scope:** Full strategy for evolving XR7 from a structured monolith to a domain-aligned microservices architecture.
**Principle:** The monolith is well-structured. Migration extracts services one at a time — never a "big bang." Zero downtime is non-negotiable.

---

## Table of Contents

1. [Microservice Map](#1-microservice-map)
2. [Service Responsibilities, APIs, and Data Contracts](#2-service-responsibilities-apis-and-data-contracts)
3. [Extraction Strategy](#3-extraction-strategy)
4. [Migration Sequence (Zero Downtime)](#4-migration-sequence-zero-downtime)
5. [Communication Patterns](#5-communication-patterns)
6. [Service Discovery Strategy](#6-service-discovery-strategy)
7. [Database-per-Service Rules](#7-database-per-service-rules)
8. [Authentication, Authorization & Secrets](#8-authentication-authorization--secrets)
9. [Rollback Strategy](#9-rollback-strategy)
10. [Cost, Complexity & Risk Analysis](#10-cost-complexity--risk-analysis)
11. [Migration Timeline](#11-migration-timeline)
12. [Risk Assessment](#12-risk-assessment)
13. [Microservices Readiness Checklist](#13-microservices-readiness-checklist)

---

## 1. Microservice Map

The XR7 monolith already has clean layer separation. Each service below corresponds to an existing XR7 module, meaning extraction is domain-aligned refactoring — not a rewrite.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        XR7 API Gateway                              │
│           (single ingress point; routes to services below)          │
└──────────┬──────────┬──────────┬──────────┬─────────────────────────┘
           │          │          │          │
    ┌──────▼──┐ ┌─────▼──┐ ┌────▼────┐ ┌───▼───────┐
    │Ingestion│ │Normal- │ │Matching │ │ Recovery  │
    │Service  │ │ization │ │Service  │ │ Service   │
    │         │ │Service  │ │         │ │           │
    └──────┬──┘ └─────┬──┘ └────┬────┘ └───┬───────┘
           │          │         │           │
    ┌──────▼──────────▼─────────▼───────────▼───────┐
    │              Event Bus (Redis Streams / Kafka) │
    └──────────────────────────────────────────────┘
           │          │         │           │
    ┌──────▼──┐ ┌─────▼──┐ ┌────▼────┐ ┌───▼───────┐
    │Reporting│ │Claims  │ │ML/Score │ │  Shared   │
    │Service  │ │Service │ │Service  │ │  Service  │
    └─────────┘ └────────┘ └─────────┘ └───────────┘
```

### Service Catalogue

| Service | Current XR7 Module | Team Owner |
|---------|-------------------|------------|
| **xr7-ingestion** | `XR7/ingestion/` | Data Engineering |
| **xr7-normalization** | `XR7/fingerprinting/` + `shared/utils/` normalization | Data Engineering |
| **xr7-matching** | `XR7/services/reconciliation*` + `XR7/core/workflow/` | Royalties Engineering |
| **xr7-recovery** | `XR7/recovery/` + `XR7/core/claims_state_machine.py` | Recovery Engineering |
| **xr7-reporting** | `XR7/api/routers/` reporting paths + `XR7/services/` reporting | Product Engineering |
| **xr7-claims** | `XR7/api/routers/claims.py` + claims services | Recovery Engineering |
| **xr7-ml** | `XR7/ml/` | Data Science |
| **xr7-identity** | `XR7/api/routers/auth.py` + user/tenant management | Platform Engineering |
| **xr7-gateway** | New (API Gateway / BFF) | Platform Engineering |
| **xr7-shared** | `shared/utils/` + `xr7_common/` (library, not a service) | All teams |

---

## 2. Service Responsibilities, APIs, and Data Contracts

### 2.1 xr7-ingestion

**Responsibility:** Receive, parse, validate, and persist raw DSP/PRO statements. Emit normalized `StatementIngested` events.

**Inbound API (REST):**
```
POST /ingest               — Accept raw file (CSV/ZIP/DDEX XML/JSON)
GET  /ingest/{job_id}      — Job status polling
POST /ingest/webhook       — DSP push delivery (Spotify, etc.)
```

**Outbound events (published to Event Bus):**
```json
{
  "event": "StatementIngested",
  "version": "1",
  "payload": {
    "artist_id": "usr_abc",
    "dsp": "spotify",
    "period_from": "2024-01-01",
    "period_to": "2024-01-31",
    "row_count": 4500,
    "ingestion_id": "ing_abc"
  }
}
```

**Database:** PostgreSQL — `ingestion_jobs`, `raw_statement_rows` tables (ingestion schema).
**Storage:** S3/GCS for raw file archival.

---

### 2.2 xr7-normalization

**Responsibility:** Consume `StatementIngested` events. Normalize field names (work_title, isrc, iswc, party_id), de-duplicate rows, resolve ISRC/ISWC via the fingerprint registry. Emit `StatementNormalized` events.

**Inbound events (consumed):**
- `StatementIngested`

**Outbound events (published):**
```json
{
  "event": "StatementNormalized",
  "version": "1",
  "payload": {
    "ingestion_id": "ing_abc",
    "normalized_row_count": 4498,
    "duplicate_count": 2,
    "normalization_id": "norm_abc"
  }
}
```

**Inbound API (REST — for ad-hoc lookups):**
```
GET /normalize/fingerprint/{isrc}   — ISRC resolution
GET /normalize/work/{iswc}          — Work metadata lookup
POST /normalize/batch               — Batch normalize a list of rows
```

**Database:** PostgreSQL — `normalized_rows`, `fingerprint_registry` tables (normalization schema).

---

### 2.3 xr7-matching

**Responsibility:** Consume `StatementNormalized` events. Compare actual royalties against expected rates. Produce variance rows. Emit `ReconciliationComplete` events.

**Inbound events (consumed):**
- `StatementNormalized`

**Outbound events (published):**
```json
{
  "event": "ReconciliationComplete",
  "version": "1",
  "payload": {
    "artist_id": "usr_abc",
    "period_from": "2024-01-01",
    "period_to": "2024-01-31",
    "variance_rows": 12,
    "total_delta_usd": 1250.00,
    "reconciliation_id": "rec_abc"
  }
}
```

**Inbound API (REST):**
```
POST /reconcile              — Trigger manual reconciliation
GET  /reconcile/{rec_id}     — Get reconciliation results
GET  /reconcile/{rec_id}/variance-rows  — Paginated variance rows
```

**Database:** PostgreSQL — `reconciliation_runs`, `variance_rows`, `expected_rates` tables (matching schema).

---

### 2.4 xr7-recovery

**Responsibility:** Manage the full lifecycle of recovery claims. Consume `ReconciliationComplete` events. Own the claims state machine. Generate and seal evidence packets. Interface with Trolley for disbursements.

**Inbound events (consumed):**
- `ReconciliationComplete`
- `EvidenceVerified` (from xr7-ml)

**Outbound events (published):**
```json
{
  "event": "ClaimStateChanged",
  "version": "1",
  "payload": {
    "claim_id": "clm_abc",
    "from_state": "EVIDENCE_READY",
    "to_state": "SUBMITTED",
    "actor": "usr_abc"
  }
}
```

**Inbound API (REST):**
```
POST /claims                     — Create draft claim
GET  /claims/{id}                — Get claim
POST /claims/{id}/advance        — State transition
POST /claims/{id}/evidence       — Generate evidence
GET  /claims/{id}/evidence       — Get signed evidence packet
POST /claims/{id}/evidence/export — Export evidence packet
```

**Database:** PostgreSQL — `claims`, `evidence_packets`, `claim_events` tables (recovery schema).

---

### 2.5 xr7-reporting

**Responsibility:** Serve read-optimized earnings summaries, history, forecasts, and dashboards. Consumes events to update a read-model (CQRS read side). No writes to domain data.

**Inbound events (consumed):**
- `StatementNormalized`
- `ReconciliationComplete`
- `ClaimStateChanged`

**Inbound API (REST — all GETs):**
```
GET /artists/{id}/earnings
GET /artists/{id}/earnings/history
GET /artists/{id}/earnings/forecast
GET /artists/{id}/statements
GET /artists/{id}/dashboard
GET /stats/platform
```

**Database:** PostgreSQL read replica + optional columnar store (TimescaleDB or DuckDB for analytics).

---

### 2.6 xr7-ml

**Responsibility:** Anomaly detection, earnings forecasting, ML model serving. Operates asynchronously. Consumes reconciliation events, produces scored outputs.

**Inbound events (consumed):**
- `ReconciliationComplete`
- `StatementNormalized`

**Outbound events (published):**
```json
{
  "event": "AnomalyDetected",
  "version": "1",
  "payload": {
    "artist_id": "usr_abc",
    "anomaly_type": "underpayment_spike",
    "confidence": 0.94,
    "affected_isrcs": ["USRC12345678"],
    "period": "2024-01"
  }
}
```

**Inbound API (REST):**
```
POST /ml/forecast             — Earnings forecast
POST /ml/anomaly/score        — Score a set of variance rows
GET  /ml/model/status         — Model health + last training timestamp
```

---

### 2.7 xr7-identity

**Responsibility:** Authentication, JWT issuance, user management, tenant management, RBAC. The single source of truth for identity.

**Inbound API (REST):**
```
POST /auth/login/artist
POST /auth/login/admin
GET  /auth/me
POST /auth/token/refresh
GET  /tenants/{id}
POST /tenants
```

**Database:** PostgreSQL — `users`, `tenants`, `roles`, `permissions` (identity schema).
**No event publishing** — identity is synchronously queried by the gateway for token validation.

---

### 2.8 xr7-gateway

**Responsibility:** Single ingress point. Validates JWTs (by calling xr7-identity token introspection or verifying JWT signature locally with cached public key). Routes requests to internal services. Rate limiting. Request tracing.

**Does NOT own any business logic.**
**Implements:** rate limiting, auth header injection downstream, correlation ID injection, circuit breakers.

---

## 3. Extraction Strategy

### The Strangler Fig Pattern

Each service is extracted using the **Strangler Fig** pattern:

```
Phase A: Run alongside monolith (shadow mode)
    ↓ New service receives copied events; responses are not used yet
Phase B: Dual-write (monolith writes to its DB + publishes events to the new service)
    ↓ Service builds its own data model from events
Phase C: Read from new service (canary: 5% → 25% → 100%)
    ↓ Verify parity; roll back if divergence detected
Phase D: Disable monolith code path
    ↓ Remove from monolith; update gateway routing
```

### Anti-corruption Layer

During extraction, the service must not inherit monolith's internal schemas. Create a translation layer at the boundary:

```python
# xr7-ingestion/translate.py
# Translates monolith StatementRow to ingestion service's domain model
def from_monolith_row(row: dict) -> IngestionRow:
    return IngestionRow(
        isrc=row.get("isrc") or row.get("track_isrc"),  # handles old field names
        work_title=row.get("work_title") or row.get("track_title"),
        ...
    )
```

### Database Extraction (Expand-Contract)

1. **Expand**: Add the service's tables to the shared DB under a new schema (`ingestion.*`, `matching.*`).
2. **Synchronize**: Dual-write to both old and new tables for one sprint.
3. **Contract**: Remove the old tables once the new service is fully live.

---

## 4. Migration Sequence (Zero Downtime)

### Preconditions Before Starting

- [ ] All domain boundaries are enforced (`check_domain_boundaries.py` passes)
- [ ] Test coverage ≥ 80% on all modules to be extracted
- [ ] Distributed tracing is operational (correlation IDs in all logs)
- [ ] Feature flags system is operational (`docs/feature_flags_configuration.md`)
- [ ] Event bus (Redis Streams or Kafka) is provisioned

---

### Sprint 1–2: Infrastructure Groundwork

1. Provision API Gateway (Kong, AWS API Gateway, or Envoy + custom)
2. Configure Redis Streams or Kafka for the Event Bus
3. Stand up Kubernetes namespaces: `xr7-ingestion`, `xr7-identity`, etc.
4. Deploy distributed tracing (Jaeger/Tempo)
5. Establish the service mesh (Linkerd or Istio, optional but recommended)

### Sprint 3–4: Extract xr7-identity (Lowest Risk, Highest Value)

Identity has no upstream dependencies. Extracting it first enables JWT validation in the gateway.

1. Deploy xr7-identity as a standalone FastAPI service
2. Dual-write: monolith writes to both `users` table AND the new identity service DB
3. Flip gateway to verify tokens via xr7-identity public key
4. Remove auth code from monolith after 2-week soak period
5. **Rollback:** Feature flag → revert to monolith JWT verification in ≤ 5 minutes

### Sprint 5–6: Extract xr7-ingestion

1. Deploy xr7-ingestion with its own DB schema
2. Monolith continues processing; xr7-ingestion receives copies of inbound files (shadow mode)
3. Compare outputs for 1 sprint — validate parity
4. Route 10% of ingestion traffic to xr7-ingestion via gateway
5. Scale to 100% after 2 weeks of parity
6. Publish `StatementIngested` events for downstream consumers

### Sprint 7–8: Extract xr7-normalization

- Depends on: xr7-ingestion `StatementIngested` events
- Extract `XR7/fingerprinting/` and normalization logic
- Validate: normalized output matches monolith's normalization (A/B comparison in shadow mode)

### Sprint 9–10: Extract xr7-matching

- Depends on: xr7-normalization `StatementNormalized` events
- Extract `XR7/core/workflow/`, `XR7/core/scoring/`, reconciliation services
- Dual-run: compare variance rows from monolith vs. new service
- Zero-downtime: monolith stays hot during canary rollout

### Sprint 11–12: Extract xr7-ml

- Depends on: `ReconciliationComplete` events from xr7-matching
- Deploy as a separate Python service (GPU-optional for model serving)
- ML service consumes events asynchronously — no user-facing latency impact

### Sprint 13–14: Extract xr7-recovery

- Depends on: xr7-matching, xr7-ml
- Most complex extraction — claims state machine must be fully tested before extraction
- Deploy claims DB schema migration ahead of service extraction (Expand-Contract)

### Sprint 15–16: Extract xr7-reporting

- CQRS read model: subscribe to all domain events and build read tables
- Replace all `GET /artists/{id}/earnings*` endpoints with xr7-reporting backend
- Monolith endpoints remain as fallback behind feature flag

### Sprint 17–18: Decommission Monolith

- All traffic routed through gateway to microservices
- Monolith kept in "cold standby" for 2 sprints (off, but deployable in <10 min if needed)
- Final decommission after 2 sprints of zero rollback events

---

## 5. Communication Patterns

### Decision Matrix

| Pattern | Use When | Services Using It |
|---------|----------|------------------|
| **REST (sync)** | User-facing read/write operations; requires immediate response | Gateway → all services, identity validation |
| **gRPC** | Inter-service calls where latency matters (hot path); strong schema needed | matching → recovery (variance row delivery) |
| **Redis Streams / Kafka (async events)** | Domain events that multiple consumers need; decoupling required | ingestion → normalization → matching → recovery → reporting |
| **Webhook callbacks** | External DSP push delivery; Trolley payment events | ingestion (inbound), recovery (Trolley outbound) |

### Event Schema Versioning

All events must include a `version` field. Consumers must handle both v1 and v2 during upgrades:

```json
{
  "event": "StatementIngested",
  "version": "2",
  "schema_url": "https://schemas.xr7.artistos.io/events/StatementIngested/v2.json",
  "payload": { ... }
}
```

Use an **Avro/Protobuf schema registry** (Confluent or Apicurio) to enforce schema compatibility.

### gRPC Service Definitions (hot paths)

```protobuf
// matching.proto
service MatchingService {
  rpc GetVarianceRows (VarianceRowsRequest) returns (stream VarianceRow);
  rpc TriggerReconciliation (ReconcileRequest) returns (ReconcileResponse);
}

message VarianceRow {
  string isrc = 1;
  string work_title = 2;
  double expected_usd = 3;
  double actual_usd = 4;
  double delta_usd = 5;
  string period = 6;
}
```

---

## 6. Service Discovery Strategy

### Kubernetes-Native (Recommended)

Use **Kubernetes Services + CoreDNS** for service discovery within the cluster:

```
xr7-ingestion.xr7-ingestion.svc.cluster.local:8080
xr7-identity.xr7-identity.svc.cluster.local:8080
```

The API Gateway resolves service names via environment variables + DNS:

```yaml
# gateway config
upstream_ingestion:
  url: http://xr7-ingestion.xr7-ingestion.svc.cluster.local
upstream_matching:
  url: http://xr7-matching.xr7-matching.svc.cluster.local
```

### External Service Registry (if multi-cluster)

For multi-region deployments (Phase 19 Enterprise), use **Consul** or **AWS Cloud Map** as a service registry with health-check-based routing.

### Health Checks

Every service exposes:
```
GET /healthz     — Liveness probe
GET /readyz      — Readiness probe (checks DB + Redis connectivity)
```

---

## 7. Database-per-Service Rules

### The Rule

Each microservice owns exactly one PostgreSQL schema. **No service reads another service's schema directly.**

```
PostgreSQL cluster
├── identity schema   (xr7-identity owns)
├── ingestion schema  (xr7-ingestion owns)
├── normalization schema (xr7-normalization owns)
├── matching schema   (xr7-matching owns)
├── recovery schema   (xr7-recovery owns)
└── reporting schema  (xr7-reporting owns — read model)
```

During transition, all schemas may live in a single PostgreSQL cluster (pragmatic). As load grows, each schema can migrate to its own cluster with no application changes.

### Cross-Service Data Access Rules

| Need | Approved Pattern | Forbidden Pattern |
|------|-----------------|-------------------|
| Service A needs a `work_title` from Service B | Publish event; B subscribes | A queries B's DB directly |
| Service A needs real-time data from B | Synchronous REST/gRPC call to B's API | A reads B's tables |
| Reporting needs data from all services | Subscribe to all domain events; build own read model | Cross-schema JOIN queries |

### Data Consistency

Accept **eventual consistency** for inter-service data. The reporting read model may lag events by milliseconds. The recovery service must not rely on "current state" from ingestion — it uses its own claims state machine.

**Saga pattern** for distributed transactions (e.g., advance approval + payout):

```
1. recovery-service: reserve advance (state: PENDING)
2. → event: AdvanceReserved
3. identity-service: validate artist
4. → event: ArtistValidated
5. trolley-integration: initiate payout
6. → event: PayoutInitiated
7. recovery-service: confirm advance (state: DISBURSED)

Compensating transactions if any step fails:
→ recovery-service: release reservation (state: FAILED)
```

---

## 8. Authentication, Authorization & Secrets

### JWT Flow in Microservices

```
Client → Gateway → [validate JWT signature with xr7-identity public key]
                 → [inject X-Tenant-Id, X-User-Id, X-Role headers]
                 → Route to downstream service
                 → Downstream service reads X-* headers (trusts gateway)
```

**Gateway is the only** service that touches the raw `Authorization` header. Downstream services trust `X-Tenant-Id` injected by the gateway. This means:
- Downstream services are NOT publicly accessible — only reachable via gateway or internal network
- Service-to-service calls use mTLS (service mesh) + `X-Service-Identity` header

### Service-to-Service Auth

```yaml
# Kubernetes ServiceAccount + SPIFFE/SPIRE for mTLS
# Each pod gets a SVID (SPIFFE Verifiable Identity Document)
# Services verify peer identity before accepting calls
```

### Secrets Management

| Secret type | Storage | Rotation |
|-------------|---------|----------|
| DB passwords | HashiCorp Vault or AWS Secrets Manager | 90 days |
| JWT signing keys (RS256) | Vault PKI secrets engine | 90 days |
| API keys (Spotify, Apple, etc.) | Vault KV v2 | Manual / on revocation |
| Celery broker URL | Kubernetes Secret (encrypted at rest) | 90 days |
| HMAC evidence signing key | Vault KV v2 | 90 days |

**Vault agent sidecar injection** in Kubernetes: secrets are injected as environment variables or files into pods at startup — never baked into Docker images.

### RBAC

Each service has its own permission checks:

| Role | ingestion | matching | recovery | admin |
|------|-----------|----------|----------|-------|
| `artist` | read own | read own | read/write own | — |
| `analyst` | read all | read all | read all + approve | — |
| `admin` | full | full | full | full |
| `service` | internal only | internal only | internal only | — |

---

## 9. Rollback Strategy

### Three-Level Rollback

**Level 1 — Feature flag (< 5 minutes)**

Every extraction is behind a feature flag. If xr7-ingestion behaves incorrectly, flip the flag to route 100% back to the monolith:

```bash
# Instant rollback — no redeployment needed
curl -X PATCH https://feature-flags/flags/use_ingestion_service \
  -d '{"enabled": false}'
```

**Level 2 — Kubernetes rollout undo (< 10 minutes)**

```bash
kubectl rollout undo deployment/xr7-ingestion -n xr7-ingestion
```

**Level 3 — Database rollback (< 30 minutes)**

If a service's DB migration caused data corruption:

```bash
# Every Alembic migration has a working downgrade()
alembic downgrade -1 --config services/xr7-ingestion/alembic.ini
```

### Circuit Breaker

The gateway implements circuit breakers (Hystrix-style or envoy circuit breaker):

```yaml
# If xr7-ingestion returns 5xx for > 10% of requests in 60s window:
# → Circuit opens: all requests route back to monolith fallback
# → Alert sent to ops Slack channel
circuit_breaker:
  window_seconds: 60
  threshold: 10%
  fallback: monolith
```

### Data Divergence Detection

During dual-write phase, run a nightly reconciliation job that compares:
- Monolith DB output vs. microservice DB output
- Fail if more than 0.01% row divergence
- Emit a `DataDivergenceDetected` alert to halt migration

---

## 10. Cost, Complexity & Risk Analysis

### Cost Impact

| Category | Monolith | Microservices | Delta |
|----------|----------|--------------|-------|
| Compute (K8s pods) | 2–4 pods | 10–16 pods | +40–60% |
| DB connections | 1 pool | 8–10 pools | Slight increase (managed via PgBouncer) |
| Observability tooling | Basic | Tracing + service mesh | +$500–2,000/mo |
| Engineering overhead | Low | Medium (distributed systems expertise required) | Requires hiring or training |
| Deployment complexity | Low | High | Mitigated by CI/CD automation |

### Complexity Threshold

Microservices are NOT the right choice if:
- Team is < 8 engineers
- Average service has < 10 deployments/month
- The monolith has no performance bottlenecks

XR7 crosses the threshold when:
- Ingestion and ML need to scale independently (ingestion spikes during statement drops; ML is GPU-bound)
- Enterprise customers require data residency isolation (services in different regions)
- Team grows beyond 12 engineers working on the same codebase

### Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Data divergence during dual-write | Medium | High | Automated nightly comparison + 0.01% threshold |
| Network latency (sync calls replacing function calls) | High | Medium | gRPC for hot paths; async events for cold paths |
| Distributed transaction failures | Low | High | Saga pattern + compensating transactions |
| Team knowledge gap (distributed systems) | High | Medium | Training + hired platform engineer before Sprint 1 |
| Event ordering issues | Medium | Medium | Kafka partitioning by `artist_id`; use sequence numbers |
| Service mesh operational overhead | Medium | Low | Start without mesh; add Linkerd in Sprint 5+ |

---

## 11. Migration Timeline

```
2026 Q2  Sprints 1–2   Infrastructure groundwork (K8s, Event Bus, Gateway, Tracing)
2026 Q2  Sprints 3–4   Extract xr7-identity
2026 Q3  Sprints 5–6   Extract xr7-ingestion
2026 Q3  Sprints 7–8   Extract xr7-normalization
2026 Q3  Sprints 9–10  Extract xr7-matching
2026 Q4  Sprints 11–12 Extract xr7-ml
2026 Q4  Sprints 13–14 Extract xr7-recovery
2027 Q1  Sprints 15–16 Extract xr7-reporting
2027 Q1  Sprints 17–18 Decommission monolith
```

Total: ~18 months at 2-week sprints. Monolith remains fully operational throughout.

---

## 12. Risk Assessment

### Overall Migration Risk: **MEDIUM**

Rationale: XR7's monolith already has clean domain separation enforced by CI scripts. The module boundaries are mature. Primary risks are operational (distributed tracing, event ordering, team expertise) not architectural.

| Phase | Risk Level | Key Risk |
|-------|-----------|----------|
| Infrastructure (Sprints 1–2) | LOW | Vendor choice lock-in for event bus |
| Identity extraction (Sprints 3–4) | LOW | Token validation downtime |
| Ingestion extraction (Sprints 5–6) | MEDIUM | Data loss during file hand-off |
| Normalization (Sprints 7–8) | MEDIUM | Fingerprint registry parity |
| Matching (Sprints 9–10) | HIGH | Variance row calculation parity — any divergence means wrong claims |
| ML (Sprints 11–12) | LOW | Async; no user-facing path |
| Recovery (Sprints 13–14) | HIGH | Claims state machine — any bug creates legal/financial liability |
| Reporting (Sprints 15–16) | LOW | Read-only; no data mutation |
| Decommission (Sprints 17–18) | LOW | Monolith in cold standby |

**Highest risk:** Matching and Recovery services must have 100% test coverage and 4 weeks of dual-run parity before any traffic is routed to the new services.

---

## 13. Microservices Readiness Checklist

### Infrastructure Readiness

- [ ] Kubernetes cluster operational with multi-namespace isolation
- [ ] API Gateway deployed and routing 100% of XR7 traffic
- [ ] Event bus (Redis Streams or Kafka) operational with replication factor ≥ 2
- [ ] Distributed tracing (Jaeger/Tempo) collecting traces from all services
- [ ] Centralized logging (ELK/Loki) draining from all pods
- [ ] Vault or equivalent secrets manager operational
- [ ] PgBouncer or RDS Proxy managing DB connection pools
- [ ] Feature flags system operational (each extraction behind a flag)

### Code Readiness (per service to extract)

- [ ] Module has ≥ 80% test coverage in the monolith
- [ ] Module has zero imports from modules it should not know about (domain boundary checks pass)
- [ ] All external contracts (event shapes, API shapes) are documented in `docs/api/`
- [ ] Pydantic models are defined for all inbound/outbound data
- [ ] Migration scripts for the service's DB schema are complete and tested

### Operational Readiness (per service)

- [ ] `GET /healthz` and `GET /readyz` endpoints implemented
- [ ] Prometheus metrics exposed on `/metrics`
- [ ] Structured JSON logs with `correlation_id`, `tenant_id`, `service` fields
- [ ] Circuit breaker configured in gateway for this service
- [ ] Rollback runbook written and tested
- [ ] Alerting rules for error rate > 1%, p99 latency > 500ms
- [ ] Data divergence comparison job running during dual-write phase
- [ ] Load test completed (p99 latency within SLA at 2× expected peak)

### Team Readiness

- [ ] On-call rotation updated to include new service
- [ ] Runbook written in `docs/incident_response_runbook_index.md`
- [ ] Deployment pipeline (GitHub Actions) covers the new service
- [ ] Engineers trained on distributed systems debugging (correlation IDs, event replay)
