# XR7 Monitoring & Observability Handbook

**Version:** 1.0
**Stack:** Prometheus + Grafana + Loki + Jaeger + OpenTelemetry + PagerDuty
**Scope:** Application, infrastructure, domain business metrics, data-quality drift, n8n workflows
**Principle:** Every alert must be actionable. No alert fires without a documented response action.

---

## Table of Contents

1. [Observability Philosophy](#1-observability-philosophy)
2. [Structured Logging Strategy](#2-structured-logging-strategy)
3. [Metrics Strategy](#3-metrics-strategy)
4. [Distributed Tracing](#4-distributed-tracing)
5. [Dashboards](#5-dashboards)
6. [Alerting Rules & Thresholds](#6-alerting-rules--thresholds)
7. [SLO / SLI Definitions](#7-slo--sli-definitions)
8. [Error Budgets](#8-error-budgets)
9. [n8n Workflow Monitoring](#9-n8n-workflow-monitoring)
10. [Data-Quality Drift Monitoring](#10-data-quality-drift-monitoring)
11. [Production Readiness Checklist](#11-production-readiness-checklist)

---

## 1. Observability Philosophy

XR7 uses the **three pillars of observability** — logs, metrics, and traces — as complementary signals. No single pillar is sufficient alone:

| Pillar | Answers | Tool |
|--------|---------|------|
| **Logs** | "What happened?" — event-level narrative | Loki + Grafana |
| **Metrics** | "How is the system behaving?" — aggregated signals over time | Prometheus + Grafana |
| **Traces** | "Why is this request slow?" — request-level performance breakdown | Jaeger + OpenTelemetry |

The **fourth pillar** for XR7 is **domain-level business metrics** — because a technically healthy system can still be failing its users if match rates are dropping or claim state transitions are stalling.

---

## 2. Structured Logging Strategy

### 2.1 Log Format

Every log line is JSON-structured for machine parsing:

```json
{
  "timestamp": "2026-04-01T12:34:56.789Z",
  "level": "INFO",
  "service": "xr7-matching",
  "request_id": "a3c7e19d-...",
  "trace_id": "4bf92f3577b34da6",
  "span_id": "00f067aa0ba902b7",
  "tenant_id": "f8e12a3b-...",
  "user_id": "d9f12c4e-...",
  "action": "match.completed",
  "entity_type": "recording",
  "entity_id": "7adb12c...",
  "duration_ms": 142,
  "result": "matched",
  "confidence": 0.97,
  "message": "Recording matched to work via ISRC"
}
```

### 2.2 Correlation IDs

Every inbound request receives a `request_id` (UUID v4) at the API gateway. This `request_id` propagates through all downstream service calls and is included in every log line.

For async operations (Celery tasks, n8n workflows), a `correlation_id` is generated at task creation and carried through all task events.

```python
# middleware/correlation.py
class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        ctx_request_id.set(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

### 2.3 Log Levels in Production

| Level | When to use |
|-------|-------------|
| `ERROR` | Unexpected failure requiring human attention |
| `WARNING` | Recoverable issue; no immediate action required but notable |
| `INFO` | Normal operational events (match completed, claim submitted, ingestion finished) |
| `DEBUG` | Disabled in production; enabled per-request via `X-Debug: true` header (admin only) |

### 2.4 PII Masking

```python
MASKED_FIELDS = {"password", "access_token", "refresh_token", "card_number"}

def sanitize_log_record(record: dict) -> dict:
    return {
        k: "***REDACTED***" if k in MASKED_FIELDS else v
        for k, v in record.items()
    }
```

Artist names and earnings values are **not** in application logs — only in the encrypted audit log.

---

## 3. Metrics Strategy

### 3.1 Service-Level Metrics (all services)

```prometheus
# Request rate
http_requests_total{service, method, path, status_code, tenant_id}

# Latency histogram (target: p99 < 500ms)
http_request_duration_seconds{service, method, path, status_code}

# Error rate (target: < 0.1% for 2xx paths)
http_errors_total{service, method, path, status_code, error_type}

# Active connections
http_active_connections{service}
```

### 3.2 Domain-Level Metrics

```prometheus
# Ingestion
ingestion_files_processed_total{dsp, format, status}       # success/failure/skipped
ingestion_rows_processed_total{dsp, record_type}
ingestion_file_size_bytes{dsp}                              # histogram

# Matching
match_attempts_total{dsp, method}                          # method: isrc/fingerprint/title/hybrid
match_outcomes_total{dsp, outcome}                         # matched/unmatched/ambiguous
match_confidence_score{dsp}                                # histogram (0–1)
match_duration_seconds{dsp}                               # histogram

# Reconciliation
reconciliation_runs_total{tenant_id, status}
reconciliation_variance_amount_usd{tenant_id}              # gauge: current open variance
reconciliation_anomalies_detected_total{anomaly_type}

# Claims
claims_total{state, payer}                                 # gauge: current distribution
claims_state_transitions_total{from_state, to_state, payer}
claims_amount_usd{state}                                   # gauge: amount in each state
claims_age_days{state}                                     # histogram: age of claims by state

# Recovery
recovery_advances_total{status}
recovery_amount_disbursed_usd                              # counter: total disbursed
```

### 3.3 Business-Level Metrics

```prometheus
# Daily active tenants
active_tenants_total                                       # gauge: tenants with activity today

# Revenue intelligence
identified_underpayments_usd_total                         # counter: total ever identified
recovered_amount_usd_total                                 # counter: total ever recovered
recovery_rate                                              # gauge: recovered / identified

# Platform health
statement_import_lag_hours{dsp}                            # gauge: hours since last import
oldest_open_claim_days                                     # gauge: days since oldest open claim was filed
```

---

## 4. Distributed Tracing

### 4.1 OpenTelemetry Configuration

```python
# tracing.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor

def configure_tracing():
    provider = TracerProvider()
    exporter = JaegerExporter(
        agent_host_name=settings.jaeger_host,
        agent_port=6831,
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
    RedisInstrumentor().instrument()
    CeleryInstrumentor().instrument()
```

### 4.2 Critical Paths to Trace

| Trace name | Start | End | SLO |
|-----------|-------|-----|-----|
| `ingestion.file.process` | File uploaded | All rows persisted | p99 < 60s for 100MB |
| `match.recording.resolve` | Statement row received | Match outcome recorded | p99 < 200ms |
| `reconciliation.run` | Run triggered | Report generated | p99 < 5min |
| `evidence.generate` | Evidence requested | Bundle sealed | p99 < 30s |
| `claim.submit` | Claim submit | DSP confirmation | p99 < 10s |
| `auth.token` | Login request | JWT issued | p99 < 300ms |

### 4.3 Span Enrichment

Every trace span includes:
- `tenant_id` — for per-tenant latency analysis
- `entity_type` / `entity_id` — for debugging specific records
- `dsp` — for DSP-specific performance analysis

---

## 5. Dashboards

### 5.1 Operational Dashboard: "XR7 System Health"

**Panels:**
- Request rate by service (requests/sec, 15m window)
- Error rate by service (% 5xx, 15m window) — RED if >0.5%
- p99 latency per service — YELLOW >200ms, RED >500ms
- DB connection pool usage — YELLOW >70%, RED >90%
- Redis memory usage — YELLOW >70%, RED >85%
- Celery queue depth by queue — YELLOW >100, RED >500
- Active pod count per service

### 5.2 Domain Dashboard: "Ingestion & Matching Pipeline"

**Panels:**
- Files ingested today by DSP
- Rows processed / hour (time series)
- Match rate by DSP (% matched) — YELLOW <85%, RED <70%
- Match confidence distribution (histogram)
- Unmatched row count (gauge, rolling 7 days)
- Ingestion lag by DSP (hours since last successful import)
- Parsers: success rate per DSP×format

### 5.3 Domain Dashboard: "Reconciliation & Anomalies"

**Panels:**
- Reconciliation runs this week / month
- Anomalies detected by type (bar chart)
- Total variance identified ($USD) — time series
- Anomaly resolution rate (gauge: % resolved within 30 days)
- ML anomaly model health: prediction rate, drift score

### 5.4 Domain Dashboard: "Claims & Recovery"

**Panels:**
- Claims by state (donut chart: DRAFT / SUBMITTED / UNDER_REVIEW / SETTLED / DISPUTED / CLOSED)
- Claims filed this week by DSP
- Average time-in-state per claim state (heatmap)
- Total amounts: identified / submitted / settled ($USD)
- Claims aging: claims open > 90 days (alert if >20)
- Recovery advances disbursed this month

### 5.5 Business Executive Dashboard

**Panels:**
- Total underpayments identified to date (large counter)
- Total recovered to date (large counter)
- Recovery rate (gauge: recovered / identified)
- Monthly new claims filed (bar chart, 12 months)
- Monthly amount recovered (area chart, 12 months)
- Active tenants (gauge)
- DSP coverage map (world map by territory)

---

## 6. Alerting Rules & Thresholds

### 6.1 Infrastructure Alerts

```yaml
# Prometheus alert rules
groups:
  - name: xr7-infrastructure
    rules:
      - alert: HighErrorRate
        expr: rate(http_errors_total[5m]) / rate(http_requests_total[5m]) > 0.01
        for: 5m
        severity: critical
        annotations:
          summary: "Error rate {{ $value | humanizePercentage }} on {{ $labels.service }}"
          runbook: "docs/runbooks/high-error-rate.md"

      - alert: HighLatencyP99
        expr: histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) > 1.0
        for: 10m
        severity: warning
        annotations:
          summary: "p99 latency {{ $value }}s on {{ $labels.service }}"

      - alert: DatabaseConnectionPoolNearCapacity
        expr: db_connection_pool_used / db_connection_pool_max > 0.85
        for: 5m
        severity: critical

      - alert: CeleryQueueDepthHigh
        expr: celery_queue_length{queue="ingestion"} > 200
        for: 10m
        severity: warning
```

### 6.2 Domain Alerts

```yaml
      - alert: MatchRateCriticallyLow
        expr: sum(rate(match_outcomes_total{outcome="matched"}[1h])) /
              sum(rate(match_attempts_total[1h])) < 0.7
        for: 30m
        severity: critical
        annotations:
          summary: "Match rate dropped to {{ $value | humanizePercentage }}"
          runbook: "docs/runbooks/low-match-rate.md"

      - alert: IngestionStaleDSP
        expr: time() - ingestion_last_success_timestamp > 86400
        for: 1m
        severity: warning
        annotations:
          summary: "No successful ingestion from {{ $labels.dsp }} in 24h"

      - alert: ClaimsAging
        expr: count(claim_age_days{state="SUBMITTED"} > 90) > 10
        for: 1h
        severity: warning
        annotations:
          summary: "{{ $value }} claims submitted > 90 days ago without resolution"

      - alert: DataQualityDriftDetected
        expr: data_quality_drift_score > 0.15
        for: 15m
        severity: warning
        annotations:
          summary: "Data quality drift {{ $value }} on {{ $labels.dsp }}"
```

### 6.3 Alert Routing

| Severity | Channel | On-call required | Response time |
|----------|---------|-----------------|--------------|
| `critical` | PagerDuty (wake-up) | Yes | < 15 min |
| `warning` | Slack `#alerts-warning` | No (business hours) | < 4 hours |
| `info` | Slack `#alerts-info` | No | Next business day |

---

## 7. SLO / SLI Definitions

### 7.1 User-Facing SLOs

| SLO | SLI measurement | Target |
|-----|----------------|--------|
| **API availability** | % of minutes with ≥ 1 successful request per 5-min window | 99.9% (8.7h downtime/year) |
| **API latency** | % of requests completing in < 500ms | 99.0% |
| **Ingestion reliability** | % of uploaded files fully processed within 2 hours | 99.5% |
| **Match quality** | % of statement rows assigned a match outcome within 1 hour | 99.0% |
| **Claim submission** | % of submitted claims reaching DSP without error | 99.5% |

### 7.2 Internal SLOs

| SLO | Target |
|-----|--------|
| Reconciliation run completion (< 5 min per 10K rows) | 99.0% |
| Evidence bundle generation (< 30s per claim) | 99.0% |
| ML scoring (< 100ms per recording lookup) | 99.5% |
| JWT issuance latency (< 300ms) | 99.9% |

---

## 8. Error Budgets

### 8.1 Error Budget Calculation

For API availability SLO of 99.9%:
- Monthly error budget = 0.1% × 43,200 minutes = **43.2 minutes/month**
- Weekly budget = ~10 minutes

### 8.2 Error Budget Policy

| Budget remaining | Policy |
|-----------------|--------|
| > 50% | Normal development; new features can ship |
| 25–50% | Elevated caution; tech lead reviews all changes |
| < 25% | Development freeze; reliability work only |
| 0% (exhausted) | Post-mortem required; no new features until budget partially replenishes (next 7 days) |

### 8.3 Error Budget Dashboard Panel

The Executive Dashboard includes a live "remaining error budget" gauge per SLO, resetting on the first of each month.

---

## 9. n8n Workflow Monitoring

### 9.1 n8n Metrics Endpoint

n8n exposes metrics at `/metrics` (configures in n8n config):
```
n8n_workflow_executions_total{workflow_name, status}
n8n_workflow_execution_duration_seconds{workflow_name}
n8n_node_executions_total{workflow_name, node_name, status}
```

### 9.2 Critical Workflow Alerts

```yaml
      - alert: N8nWorkflowFailed
        expr: increase(n8n_workflow_executions_total{status="error"}[1h]) > 0
        for: 5m
        severity: warning
        annotations:
          summary: "n8n workflow {{ $labels.workflow_name }} failed in last hour"

      - alert: N8nIngestionWorkflowStale
        # 01_dsp_ingestion_pipeline should run every 24h
        expr: time() - n8n_workflow_last_success_timestamp{workflow="dsp_ingestion"} > 90000
        severity: critical
```

### 9.3 n8n Workflow Health Dashboard

**Panels:**
- Executions per workflow today (bar chart)
- Failed executions last 7 days by workflow
- Average execution time per workflow (trend)
- Last successful execution timestamp per workflow
- n8n queue depth (pending executions)

---

## 10. Data-Quality Drift Monitoring

### 10.1 What Is Data-Quality Drift?

Drift occurs when the statistical properties of incoming DSP data change unexpectedly:
- Match rate for a DSP drops by >10% month-over-month
- Average royalty rate per stream for a DSP deviates >3σ from historical baseline
- Null rate for `isrc` or `work_title` fields increases

These are leading indicators of DSP format changes, rate disputes, or data pipeline corruption.

### 10.2 Drift Detection Pipeline

```python
# Background task: runs nightly
async def detect_data_quality_drift(dsp: str, period: str):
    current_stats = await compute_statement_stats(dsp, period)
    baseline_stats = await get_baseline_stats(dsp, lookback_periods=6)  # 6 months

    drift_report = {}
    for metric in ["match_rate", "avg_rate_per_stream", "isrc_null_rate"]:
        z_score = (current_stats[metric] - baseline_stats[metric].mean) / baseline_stats[metric].std
        drift_report[metric] = {
            "current": current_stats[metric],
            "baseline_mean": baseline_stats[metric].mean,
            "z_score": z_score,
            "alert": abs(z_score) > 2.5
        }

    if any(v["alert"] for v in drift_report.values()):
        await emit_drift_alert(dsp, period, drift_report)
        await update_metric("data_quality_drift_score", dsp, max(abs(v["z_score"]) for v in drift_report.values()))
```

### 10.3 Drift Alert Actions

When drift is detected:
1. Slack alert to `#data-quality`
2. Flag all affected reconciliation runs as `requires_review`
3. Auto-pause claim filing for the affected DSP × period until analyst clears drift
4. Generate drift report in `audit_events` with full statistics

---

## 11. Production Readiness Checklist

Use this checklist before promoting any service to production for the first time, or after a major architectural change.

### Observability

- [ ] Structured JSON logging with `request_id`, `tenant_id`, `trace_id` in every log line
- [ ] Prometheus metrics endpoint (`/metrics`) registered and scraped by Prometheus
- [ ] OpenTelemetry instrumentation: FastAPI + SQLAlchemy + Redis + Celery
- [ ] Traces visible in Jaeger for all critical paths listed in Section 4.2
- [ ] All dashboards in Section 5 have data for the new service
- [ ] PII fields confirmed as masked in application logs (verified with test)

### Alerting

- [ ] All alerting rules in Section 6 applied to the service
- [ ] PagerDuty integration tested: send a test alert, confirm on-call receives it
- [ ] Alert runbooks written for every `critical` alert
- [ ] No alert fires without a documented response action

### SLOs

- [ ] SLIs defined and implemented as Prometheus queries
- [ ] SLO compliance dashboard visible in Grafana
- [ ] Error budget policy communicated to team

### Reliability

- [ ] Health check endpoint (`/healthz`) returns 200 with service status
- [ ] Readiness probe configured (Kubernetes): returns 503 until DB connection is verified
- [ ] Liveness probe configured: restarts pod if /healthz fails 3 consecutive times
- [ ] Graceful shutdown: SIGTERM handler flushes in-flight requests before termination
- [ ] DB connection pool monitored; pool size configured for expected load (not default)
- [ ] Celery worker concurrency configured based on load test results

### Data Quality

- [ ] Data quality drift detection running for all DSPs
- [ ] Match rate baseline established for each DSP
- [ ] Drift alert routes to correct Slack channel

### Incident Response

- [ ] Service added to PagerDuty escalation policy
- [ ] On-call runbook for the service written and linked from alerting rules
- [ ] Runbook tested with a simulated incident (fire drill)
- [ ] Rollback procedure for the service documented and tested

### Performance

- [ ] Load test run at 2× expected peak load; p99 latency within SLO
- [ ] DB query explain-analyze for all queries expected to run on tables > 1M rows
- [ ] Indexes verified for all foreign key columns and common filter columns
- [ ] No N+1 query patterns in critical paths (verified via SQLAlchemy query logging)

### Security

- [ ] All items in `docs/security_hardening_plan.md` Section 12 checklist completed
- [ ] Trivy scan: zero Critical/High CVEs
- [ ] bandit scan: zero High severity findings
- [ ] Cross-tenant isolation tested for new service endpoints
