# 04 — Data Flows

**Status:** Current. Sequence diagrams for the four flows that together make up the recovery lifecycle.

## 1. Statement ingestion

**Trigger:** a user (artist / manager / label staff) uploads a royalty statement file.

```mermaid
sequenceDiagram
    actor user as User
    participant fe as Frontend
    participant api as API<br/>(FastAPI)
    participant s3 as S3 / MinIO
    participant db as Postgres
    participant q as Redis<br/>(Celery broker)
    participant w as Worker

    user->>fe: Select statement file
    fe->>api: POST /ingestion (multipart)
    api->>s3: Put object (raw file)
    api->>db: Insert statement row (state=PENDING)
    api->>q: Enqueue parse_statement(statement_id)
    api-->>fe: 202 Accepted + statement_id
    fe-->>user: "Upload received, parsing..."

    w->>q: Claim parse_statement
    w->>s3: Get raw file
    w->>w: statement_parser.parse()<br/>(XR7/ingestion/statement_parser.py)
    w->>db: Insert normalized line items
    w->>db: Update statement (state=PARSED)
    w->>q: Enqueue classify_anomalies(statement_id)
```

**Code anchors:**
- Router: [`XR7/api/routers/ingestion.py`](../../XR7/api/routers/ingestion.py)
- Parser: [`XR7/ingestion/statement_parser.py`](../../XR7/ingestion/statement_parser.py)
- Pipeline: [`XR7/ingestion/file_ingestion_pipeline.py`](../../XR7/ingestion/file_ingestion_pipeline.py)

**Ingestion format catalog:** [`docs/ingestion_format_catalog.md`](../ingestion_format_catalog.md).

## 2. Anomaly detection

**Trigger:** a parsed statement enters `classify_anomalies`, OR scheduled recovery scan (`run_recovery_for_new_data`, every 6 h).

```mermaid
sequenceDiagram
    participant q as Redis
    participant w as Worker
    participant db as Postgres
    participant ml as ML detector<br/>(XR7/ml/anomaly_detector.py)
    participant sl as Statute tracker<br/>(XR7/recovery/statute_tracker.py)

    w->>q: Claim classify_anomalies(statement_id)
    w->>db: Load statement + historical baseline
    w->>ml: IsolationForest score
    w->>ml: Z-score drift check
    w->>ml: Missingness check (expected-but-absent rows)
    ml-->>w: Candidate anomalies with scores
    w->>sl: classify_anomalies() — statute-of-limitations aware
    sl-->>w: Anomalies with recoverability tier
    w->>db: Insert anomaly rows (state=IDENTIFIED)
    w->>q: Enqueue review or auto-advance per policy
```

**Code anchors:**
- Rule + ML engine: [`XR7/ml/anomaly_detector.py`](../../XR7/ml/anomaly_detector.py)
- Statute-aware classifier: [`XR7/recovery/statute_tracker.py`](../../XR7/recovery/statute_tracker.py)
- Router: [`XR7/api/routers/anomalies.py`](../../XR7/api/routers/anomalies.py)

**Rule catalog:** [`docs/anomaly_rule_catalog.md`](../anomaly_rule_catalog.md).

## 3. Claim filing

**Trigger:** an anomaly passes analyst review (or policy auto-advance), becoming a claim draft.

```mermaid
sequenceDiagram
    actor analyst as Analyst
    participant fe as Frontend
    participant api as API
    participant db as Postgres
    participant q as Redis
    participant w as Worker
    participant llm as LLM provider<br/>(OpenAI / xAI)
    participant s3 as S3

    analyst->>fe: Approve anomaly for claim filing
    fe->>api: POST /claims (anomaly_id)
    api->>db: Insert claim (status=IDENTIFIED)
    api->>q: Enqueue draft_claim(claim_id)
    api-->>fe: 202 Accepted

    w->>q: Claim draft_claim
    w->>db: Load claim + anomaly context
    w->>llm: Draft claim letter<br/>(XR7/llm/claim_drafter.py)
    llm-->>w: Draft text + rationale
    w->>w: Build evidence packet<br/>(XR7/recovery/ — statement rows, audit, computation)
    w->>s3: Write evidence packet
    w->>db: Update claim (status=PREPARED)

    analyst->>fe: Review + approve packet
    fe->>api: POST /claims/{id}/submit
    api->>db: Update claim (status=FILED → SUBMITTED)
    api->>q: Enqueue send_claim(claim_id) (PRO/DSP-specific submission)
    w->>q: Claim send_claim — routes per PRO/DSP<br/>(file upload, email, or API)
    w->>db: Update claim (status=PROOF_SUBMITTED → IN_REVIEW)
```

**Claim state machine:** `IDENTIFIED → PREPARED → FILED → SUBMITTED → PROOF_SUBMITTED → IN_REVIEW → ACCEPTED → FUNDS_RECEIVED → PAID → CLOSED`, with a `DISBURSEMENT_FAILED` branch. Defined in [`XR7/models/claim.py`](../../XR7/models/claim.py).

**Code anchors:**
- State machine: [`XR7/models/claim.py`](../../XR7/models/claim.py)
- Router: [`XR7/api/routers/claims.py`](../../XR7/api/routers/claims.py)
- LLM drafter: [`XR7/llm/claim_drafter.py`](../../XR7/llm/claim_drafter.py)
- Audit: [`XR7/services/claim_status_audit.py`](../../XR7/services/claim_status_audit.py)

Detailed runbook: [`docs/claims_state_machine.md`](../claims_state_machine.md).

## 4. Payout (Trolley disbursement)

**Trigger:** claim reaches `FUNDS_RECEIVED` — payer has settled and money is with us to distribute.

```mermaid
sequenceDiagram
    participant w as Worker
    participant db as Postgres
    participant bl as Ledger<br/>(immutable append)
    participant tr as Trolley API<br/>(XR7/trolley/client.py)
    actor artist as Artist

    w->>db: Load claim (status=FUNDS_RECEIVED)
    w->>db: Compute fee split (contingency model)<br/>per billing_contingency_fee_model.md
    w->>bl: Append debit/credit entries (pre-disbursement)
    w->>tr: POST /recipients (upsert) + /payments (initiate)
    alt Trolley accepts
        tr-->>w: payment_id, status=PENDING
        w->>db: Update claim (status=PAID)
        w->>bl: Append settlement entries
        tr->>artist: Funds land in artist's account
    else Trolley fails
        tr-->>w: error
        w->>db: Update claim (status=DISBURSEMENT_FAILED)
        w->>bl: Append failure marker
        Note over w,tr: Operator runbook:<br/>docs/trolley_failure_playbook.md
    end
    w->>db: Close claim (status=CLOSED) after settlement window
```

**Code anchors:**
- Trolley client: [`XR7/trolley/client.py`](../../XR7/trolley/client.py)
- Router: [`XR7/api/routers/trolley.py`](../../XR7/api/routers/trolley.py)
- Billing / payout orchestration: [`XR7/billing/`](../../XR7/billing/)

**Fee model:** [`docs/billing_contingency_fee_model.md`](../billing_contingency_fee_model.md).
**Failure playbook:** [`docs/trolley_failure_playbook.md`](../trolley_failure_playbook.md).

## Cross-cutting: human-in-the-loop gates

Two points in the lifecycle are gated by an analyst (configurable per tenant / policy):

1. **Anomaly → claim draft** — analyst approves before LLM spends tokens drafting.
2. **Claim packet → submission** — analyst approves the generated packet before it's sent to the payer.

See [`docs/analyst_gated_recovery_advance_system.md`](../analyst_gated_recovery_advance_system.md).

## Cross-cutting: ledger

Every decision that moves money or obligation is append-only to the immutable ledger (`XR7/blockchain/` + `XR7/transparency/`). Used for audit, reconciliation, and investor-grade provenance. See [`docs/data_lineage_provenance_tracking.md`](../data_lineage_provenance_tracking.md).

## See also

- [02 — Containers](02-containers.md) for which container owns each step
- [05 — Integrations](05-integrations.md) for the external-system boundary details
- [`docs/celery_workflows.md`](../celery_workflows.md) for the full task registry + beat schedule
