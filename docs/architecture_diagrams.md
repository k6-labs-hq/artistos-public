# XR7 Architecture Diagrams

All diagrams use [Mermaid](https://mermaid.js.org/) syntax. Render in GitHub, Obsidian, or any Mermaid-compatible viewer.

---

## Diagram 1: System Overview (C4 Context)

```mermaid
C4Context
    title XR7 Engine 2 — System Context

    Person(artist, "Artist", "Music creator; views earnings, files claims")
    Person(analyst, "Analyst", "Reviews anomalies, approves advances, manages claims")
    Person(admin, "Platform Admin", "Manages tenants, users, and platform configuration")

    System(xr7, "XR7 Engine", "Earnings accuracy platform — ingests, reconciles, recovers")

    System_Ext(spotify, "Spotify API", "Streaming statements, play counts")
    System_Ext(apple, "Apple Music API", "Streaming statements")
    System_Ext(soundcloud, "SoundCloud API", "Streaming data")
    System_Ext(pro, "PRO (ASCAP/BMI/PRS)", "Performance royalty data")
    System_Ext(mlc, "MLC Registry", "Mechanical royalty metadata")
    System_Ext(trolley, "Trolley", "Payout disbursement")
    System_Ext(n8n, "n8n", "Workflow orchestration")
    System_Ext(openai, "OpenAI / Anthropic", "LLM for agent workflows")

    Rel(artist, xr7, "Views earnings, submits claims", "HTTPS")
    Rel(analyst, xr7, "Reviews, approves", "HTTPS")
    Rel(admin, xr7, "Configures, audits", "HTTPS")
    Rel(xr7, spotify, "Ingests statements", "HTTPS/OAuth2")
    Rel(xr7, apple, "Ingests statements", "HTTPS/OAuth2")
    Rel(xr7, soundcloud, "Ingests statements", "HTTPS/OAuth2")
    Rel(xr7, pro, "Reconciles performance data", "HTTPS")
    Rel(xr7, mlc, "Aligns metadata", "HTTPS")
    Rel(xr7, trolley, "Disburses payments", "HTTPS")
    Rel(n8n, xr7, "Orchestrates workflows", "REST/HTTPS")
    Rel(xr7, openai, "LLM agent calls", "HTTPS")
```

---

## Diagram 2: Module Layer Boundaries

```mermaid
graph TD
    subgraph "Public Layer"
        API["XR7/api/\n(FastAPI routers)"]
    end
    subgraph "Business Logic Layer"
        SVC["XR7/services/\n(ORM + business rules)"]
        ML["XR7/ml/\n(anomaly detect, forecast)"]
        AGENTS["XR7/agents/\n(LangGraph)"]
    end
    subgraph "Pure Logic Layer (no I/O)"
        CORE["XR7/core/\n(state machine, scoring,\nintegrity, workflow)"]
    end
    subgraph "Utility Layer (zero deps)"
        UTILS["shared/utils/\n(math, dates, ISRC, currency)"]
    end
    subgraph "Infrastructure"
        DB[("PostgreSQL")]
        CACHE[("Redis")]
        QUEUE["Celery workers"]
    end

    API -->|calls| SVC
    SVC -->|imports| CORE
    SVC -->|imports| UTILS
    ML -->|imports| CORE
    ML -->|imports| UTILS
    AGENTS -->|calls| SVC
    SVC -->|reads/writes| DB
    SVC -->|caches| CACHE
    SVC -->|enqueues| QUEUE

    style CORE fill:#d4edda,stroke:#28a745
    style UTILS fill:#d4edda,stroke:#28a745
    style API fill:#cce5ff,stroke:#004085
    style SVC fill:#fff3cd,stroke:#856404
```

---

## Diagram 3: DSP Ingestion Data Flow

```mermaid
sequenceDiagram
    autonumber
    participant n8n
    participant API as XR7 API
    participant Celery
    participant Ingestion as XR7/ingestion/
    participant Services as XR7/services/
    participant ML as XR7/ml/
    participant DB as PostgreSQL

    n8n->>API: POST /ingestion/trigger {dsp: "spotify", artist_id: "..."}
    API->>Celery: enqueue ingestion_task(artist_id, dsp)
    API-->>n8n: {job_id: "job_abc", status: "queued"}

    loop Poll until complete
        n8n->>API: GET /jobs/job_abc/status
        API-->>n8n: {status: "running"}
    end

    Celery->>Ingestion: run(artist_id, dsp)
    Ingestion->>Ingestion: fetch raw statement (DSP API / S3)
    Ingestion->>Ingestion: parse CSV/DDEX → StatementRow[]
    Ingestion->>Ingestion: normalize field names (work_title, isrc)
    Ingestion->>Services: persist_statement_rows(rows)
    Services->>DB: INSERT INTO statement_rows

    Services->>ML: score_anomalies(artist_id, period)
    ML->>DB: SELECT historical rows
    ML-->>Services: anomaly_flags[]
    Services->>DB: UPDATE anomaly_flags

    Services-->>Celery: job complete
    Celery->>n8n: webhook POST /n8n/callback {job_id, status: "completed"}
    n8n->>API: POST /artists/{id}/reconciliation/trigger
```

---

## Diagram 4: Claims State Machine

```mermaid
stateDiagram-v2
    [*] --> DRAFT : Claim created

    DRAFT --> EVIDENCE_PENDING : Request evidence generation
    EVIDENCE_PENDING --> EVIDENCE_READY : Evidence generated (Celery)
    EVIDENCE_PENDING --> FAILED : Generation error

    EVIDENCE_READY --> SUBMITTED : Artist/analyst submits to DSP
    EVIDENCE_READY --> DRAFT : Recall for revision

    SUBMITTED --> UNDER_REVIEW : DSP acknowledged
    SUBMITTED --> REJECTED : DSP rejected immediately

    UNDER_REVIEW --> RESOLVED : DSP accepted — payment issued
    UNDER_REVIEW --> DISPUTED : DSP denied claim
    UNDER_REVIEW --> EXPIRED : No response after 90 days

    DISPUTED --> ESCALATED : Analyst escalates to legal
    DISPUTED --> CLOSED : Artist withdraws

    ESCALATED --> RESOLVED : Legal settlement reached
    ESCALATED --> CLOSED : Claim abandoned

    FAILED --> DRAFT : Retry
    EXPIRED --> DRAFT : Refile
    RESOLVED --> [*]
    CLOSED --> [*]
```

---

## Diagram 5: Reconciliation Sequence (Earnings Accuracy Engine)

```mermaid
sequenceDiagram
    autonumber
    participant Trigger as Celery / n8n
    participant RecSvc as ReconciliationService
    participant Core as XR7/core/workflow/
    participant Scoring as XR7/core/scoring/
    participant Integrity as XR7/core/integrity/
    participant DB as PostgreSQL
    participant Claims as XR7/services/claims/

    Trigger->>RecSvc: reconcile(artist_id, period)

    RecSvc->>DB: SELECT statement_rows WHERE artist_id + period
    RecSvc->>DB: SELECT expected_royalties WHERE artist_id + period
    RecSvc-->>Core: build_variance_rows(actual[], expected[])

    Core->>Core: compute per-ISRC delta
    Core->>Core: compute period totals
    Core-->>Scoring: score_discrepancies(variance_rows[])

    Scoring->>Scoring: apply threshold rules
    Scoring->>Scoring: compute confidence score
    Scoring-->>RecSvc: scored_rows[] with flags

    RecSvc->>Integrity: sign_evidence_packet(scored_rows)
    Integrity->>Integrity: compute HMAC-SHA256
    Integrity-->>RecSvc: {packet, hmac_signature}

    RecSvc->>DB: INSERT INTO evidence_packets
    RecSvc->>Claims: auto_create_claims(flagged_rows)
    Claims->>DB: INSERT INTO claims (state=EVIDENCE_READY)
    RecSvc-->>Trigger: {claims_created: N, total_delta_usd: X}
```

---

## Diagram 6: LangGraph Agent Orchestration

```mermaid
graph LR
    subgraph "LangGraph Agent Graph"
        ENTRYPOINT["Entry\n(artist query)"]
        ROUTER["Router Node\n(intent classifier)"]
        EARNINGS_AGENT["Earnings Agent\n(XR7 API lookups)"]
        CLAIMS_AGENT["Claims Agent\n(evidence generation)"]
        RECOVERY_AGENT["Recovery Agent\n(advance qualification)"]
        RESPONSE["Response\nRenderer"]
        HANDOFF["Human Handoff\n(analyst escalation)"]
    end

    subgraph "XR7 API (tools)"
        EARN_TOOL["GET /artists/{id}/earnings"]
        CLAIM_TOOL["POST /claims"]
        ADVANCE_TOOL["POST /artists/{id}/advance/qualify"]
    end

    ENTRYPOINT --> ROUTER
    ROUTER -->|earnings intent| EARNINGS_AGENT
    ROUTER -->|claim intent| CLAIMS_AGENT
    ROUTER -->|advance intent| RECOVERY_AGENT
    ROUTER -->|complex/ambiguous| HANDOFF

    EARNINGS_AGENT --> EARN_TOOL
    CLAIMS_AGENT --> CLAIM_TOOL
    RECOVERY_AGENT --> ADVANCE_TOOL

    EARNINGS_AGENT --> RESPONSE
    CLAIMS_AGENT --> RESPONSE
    RECOVERY_AGENT --> RESPONSE
    HANDOFF --> RESPONSE
```

---

## Diagram 7: Multi-Tenancy Isolation Model

```mermaid
graph TB
    subgraph "Request path"
        JWT["JWT token\n{tenant_id: t_abc}"]
        ROUTER["FastAPI Router"]
        DEP["Depends(get_current_user)\nextracts tenant_id"]
        SVC["Service function\nreceives tenant_id explicitly"]
        DB["PostgreSQL\nWHERE tenant_id = 't_abc'"]
    end

    JWT --> ROUTER
    ROUTER --> DEP
    DEP --> SVC
    SVC --> DB

    note1["tenant_id is NEVER\nread from request body"]
    note2["All queries include\nWHERE tenant_id = ?"]
    note3["Cross-tenant reads\nare impossible by design"]
```

---

## Diagram 8: n8n Workflow Orchestration Overview

```mermaid
graph TB
    subgraph "n8n Workflows"
        INGEST["1. DSP Ingestion Pipeline\n(scheduled nightly)"]
        RECON["2. PRO Reconciliation\n(scheduled weekly)"]
        MLC["3. MLC Metadata Alignment\n(scheduled daily)"]
        EXPORT["4. Recovery Claim Export\n(triggered by analyst)"]
    end

    subgraph "XR7 API (execution layer)"
        INGEST_EP["POST /ingestion/trigger"]
        RECON_EP["POST /reconciliation/trigger"]
        MLC_EP["POST /catalog/align"]
        CLAIM_EP["POST /claims/{id}/evidence/export"]
    end

    subgraph "Notifications"
        SLACK["Slack alerts"]
        EMAIL["Email digest"]
        WEBHOOK["XR7 webhook callback"]
    end

    INGEST --> INGEST_EP
    RECON --> RECON_EP
    MLC --> MLC_EP
    EXPORT --> CLAIM_EP

    INGEST_EP -->|anomalies found| SLACK
    RECON_EP -->|gaps flagged| EMAIL
    EXPORT -->|export complete| WEBHOOK
```

---

## Diagram 9: CI/CD Pipeline

```mermaid
graph LR
    PR["Pull Request\n(push to any branch)"]

    subgraph "CI — Quality Gate"
        LINT["lint\n(ruff + black)"]
        TYPES["type-check\n(mypy)"]
        TESTS["test\n(pytest + coverage)"]
        DOMAIN["domain-guard\n(boundary script)"]
        NAMING["naming-check\n(naming script)"]
    end

    subgraph "CD — Production Deploy (main only)"
        FULLTEST["full-test\n(postgres + redis)"]
        BUILD["docker-build\n(+ trivy scan)"]
        STAGING["deploy-staging\n(auto)"]
        SMOKE["smoke-test\n(staging)"]
        PROD["deploy-prod\n(approval gate, tag only)"]
    end

    subgraph "Nightly Analysis (02:00 UTC)"
        DEAD["dead-code\n(vulture)"]
        DUP["duplication\n(pylint)"]
        CIRC["circular-deps\n(import-linter)"]
        SEC["security\n(bandit)"]
        AUDIT["dependency-audit\n(pip-audit)"]
    end

    PR --> LINT & TYPES & TESTS & DOMAIN & NAMING
    LINT & TYPES & TESTS & DOMAIN & NAMING -->|all green| FULLTEST
    FULLTEST --> BUILD --> STAGING --> SMOKE --> PROD
```
