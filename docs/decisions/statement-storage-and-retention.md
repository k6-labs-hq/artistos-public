# ADR: statement file storage + 7-year retention + dedup strategy

**Status:** Decided 2026-05-05. Implementation pending.
**Context driver:** Jason's "do we save uploaded files / how do we not double-report?" question during a feature re-assessment.

---

## 1. Decision

1. **Store original uploaded statement bytes** in S3-compatible object storage at upload time, keyed by `statements/{artist_id}/{file_hash}.{ext}`.
2. **Retain for 7 years** from upload date, enforced via bucket lifecycle policy.
3. **Use self-hosted MinIO on the same Hetzner VM** as the API for closed beta. Migrate to managed object storage (Hetzner Object Storage preferred) when real artist data is at stake.
4. **Three-layer deduplication** (file hash, row reference_id, anomaly deterministic ID) covers the most common failure modes; restatement and cross-format overlap remain known gaps with documented mitigations.
5. **Upload-to-artist correlation is URL-routed only** today; semantic content-vs-artist validation is a known gap to address before self-serve scale.

---

## 2. Why save the file at all

Pre-decision, the upload pipeline was hash-only — we kept SHA-256 of the bytes for dedup but discarded the original. Three drivers for reversing this:

### 2.1 Audit defensibility
A SHA-256 hash isn't admissible evidence on its own. Federal Rules of Evidence require authentication via the actual document. If BMI ever questions a finding, we'd be relying on the artist or BMI to provide the source statement back — fragile.

### 2.2 Reprocessing under updated parsers
This already bit us on 2026-05-04. We extended the BMI parser (#240) to capture `payer_account_id`, `payer_ip_number`, `payer_work_id`. Existing uploads couldn't be re-derived because the bytes were gone. With files stored, we can re-run the latest parser against historical uploads and get the new fields populated.

### 2.3 Legal evidence in escalation
Tennessee's contract SOL is 6 years for written contracts. If a dispute escalates beyond BMI Member Services to litigation, the source statement becomes evidence. 7 years rounds up safely past TN SOL + IRS records norm + most states' contract SOLs.

### 2.4 What we are NOT relying on
There is no music-industry equivalent to HIPAA. The 7-year number is **policy, not regulation**. Don't cite it as "required by law."

---

## 3. Why 7 years specifically

Not a regulation. A defensible round-up covering the longest reasonable thing the lawyer might ask for:

| Driver | Period |
|---|---|
| TN written-contract SOL (Matt's home base) | 6 years |
| IRS records retention norm (royalties feed 1099-MISC) | 7 years |
| Audit-firm professional custom (Cohn Reznick, CitrinCooperman) | Indefinite |
| BMI 9-month claim window | < 1 year (active dispute only) |
| Federal copyright SOL | 3 years |

7 lands above all the relevant SOLs and matches IRS norms. Above 7 (e.g. indefinite) costs more storage with diminishing legal benefit.

---

## 4. Storage backend choice (and why MinIO-on-VM today)

### 4.1 Options considered

| Option | Cost | Durability | Migration effort | Picked? |
|---|---|---|---|---|
| Self-hosted MinIO on the same Hetzner VM (current) | Free (VM disk) | Single-VM disk | — | **Yes (closed beta)** |
| Hetzner Object Storage | ~€0.0049/GB-month | Multi-AZ | Env var change | Future |
| Cloudflare R2 | $0.015/GB-month, zero egress | Multi-region | Env var change | Future |
| Backblaze B2 | $0.006/GB-month | Multi-AZ | Env var change | Future |
| AWS S3 | $0.023/GB-month + egress | 11 nines | Env var change | No |

### 4.2 Why MinIO-on-VM is acceptable for closed beta
- Already provisioned (`artistos-minio-1` running 8+ days on QA, MinIO container on local docker-compose). Zero new infra.
- Storage volume is tiny — typical artist statement is 50-500KB; even 1000 artists × 24 statements/artist/year × 5 years = ~60GB.
- Acceptable risk: closed beta is pre-attorney-approval, no real disputes filed yet, so loss of statements would set us back days, not catastrophe.

### 4.3 Trigger for migration
When **either** of these is true, migrate to managed storage:
- First real BMI dispute filed against real artist data
- Backup audit + restore drill demonstrates we can recover from VM loss (which it won't, today)

Migration is a config change: `S3_ENDPOINT_URL` + new credentials. The boto3 client and all our application code stay identical because every option above speaks the S3 protocol.

---

## 5. Object key convention

```
statements/{artist_id}/{file_hash}.{original_ext}
```

- `statements/` namespace prevents collision with future artifact types
- `{artist_id}` namespace: deletion-on-account-removal becomes a single prefix delete
- `{file_hash}` (SHA-256 hex of raw bytes) is the dedup primary key + content-addressed name
- `{original_ext}` preserved (`.csv`, `.xlsx`, `.numbers`) so re-parse can dispatch the right parser

Object metadata tags:
- `artist_id`
- `format_detected` (after parse)
- `uploaded_at`
- `original_filename`
- `parsed_status` (PROCESSED / FAILED / DUPLICATE)

---

## 6. Deduplication strategy (three layers)

We dedup at three layers, each catching a different failure mode. None of these is sufficient alone.

### 6.1 File-level
- **Mechanism:** SHA-256 of raw bytes, unique constraint on `(artist_id, file_hash)` in `statements` table.
- **Catches:** "same file uploaded twice."
- **Strength:** bulletproof. Returns 409 with the existing `statement_id`.

### 6.2 Row-level
- **Mechanism:** `Payment.reference_id = sha256(canonicalized_row + format_id)` per row at parse time. Unique constraint on `(artist_id, reference_id)` in `payments`.
- **Catches:** "different file with overlapping rows" — common when an artist re-exports a longer date range that overlaps a previous upload.
- **Strength:** strong if rows are byte-identical between uploads. Loses to restatement (see §6.4 gap).

### 6.3 Anomaly-level
- **Mechanism:** Deterministic anomaly ID `_deterministic_anomaly_id(artist_id, rule_id, identity_key)`. Each rule declares a stable `identity_key`. `_persist_anomaly` upserts on re-detect (updates `confidence_score`, `estimated_recoverable`, etc. rather than inserting a new row).
- **Catches:** "re-running detection after a re-ingest" — without this, the same finding would be re-inserted whenever the upload pipeline runs.
- **Strength:** bulletproof for detection idempotency.

### 6.4 Known gaps (no mitigation yet)

#### Restated statements
BMI sends Q3 2025 → 3 months later sends a corrected Q3 2025 with different amounts. Different file → new `Statement` row. New rows have different `reference_id` (amount changed) → both Payment sets coexist. Artist's "total Q3 income" doubles.

**Future mitigation:** detect when a new statement covers a period that's already been processed; surface "potential restatement" warning in the operator dashboard. Operator decides whether to mark old payments as `superseded`. Not implemented.

#### Cross-format overlap
Artist uploads DistroKid roll-up CSV (which lists BMI as a line item) AND the BMI portal CSV directly. Same money, different formats, different `reference_id`. Both Payment sets ingest.

**Future mitigation:** surface "potential overlap" warning when `(artist, period, source_keyword)` triples appear in two different formats. Auto-dedup is too risky (false positives swallow real income); manual reconciliation in the dashboard is the right floor. Not implemented.

#### Multi-claim per anomaly
No uniqueness on `(artist_id, anomaly_id)` in `claims`. Technically two claims for one anomaly is possible.

**Future mitigation:** add a unique constraint on `(artist_id, anomaly_id)` where `claims.deleted_at IS NULL`. Allow multiple claims only across non-overlapping `payer_office`s when an anomaly spans multiple PROs (rare). Not implemented.

---

## 7. Upload-to-artist correlation

### 7.1 What's in place
- URL routing: `POST /artists/{artist_id}/statements/upload` — `artist_id` from URL is set on `Statement.artist_id`, propagates to all `Event` and `Payment` rows.
- Per-artist dedup: `unique(artist_id, file_hash)` and `unique(artist_id, reference_id)` mean two different artists can legitimately upload the same statement bytes (e.g. co-writers on the same BMI account) without collision.

### 7.2 What's NOT in place (gap)
**Semantic content-vs-artist validation.** We don't check that the statement's content actually corresponds to the URL's artist. An admin could PUT Artist A's statement under Artist B's URL and we'd ingest it under B.

**Mitigation when we need it:** parse the artist-name field from the statement (BMI 28-col CSV has `PARTICIPANT NAME`; ASCAP and MLC have similar) and warn/block when it doesn't fuzzy-match the Artist row's `name`. Not blocking for closed beta because (a) artist-side uploads come from the signed-in artist's dashboard (URL is their own ID), (b) operator-side uploads are deliberate. For self-serve / external API access it would be a real risk.

---

## 8. Implementation TODO

Not yet implemented. Tracked in [issue #tbd]:

- [ ] Add `S3Client` wrapper module (boto3) reading `S3_*` env vars (already populated).
- [ ] Modify `POST /artists/{artist_id}/statements/upload` to write the original bytes to S3 before the parse step, store `Statement.s3_uri`.
- [ ] Add `s3_uri` column to `Statement` model + alembic migration.
- [ ] Add `GET /admin/statements/{statement_id}/download` (admin-gated) for retrieving the stored original.
- [ ] Reprocess script: `python scripts/reprocess_statements.py --artist <id>` — pulls each statement's `s3_uri`, runs the latest parser, replaces or augments Events+Payments.
- [ ] Bucket lifecycle policy: expire objects 7 years after `uploaded_at`. (Manual config on the MinIO bucket initially; codified when we migrate to managed storage.)
- [ ] Backup procedure for the MinIO volume on QA — daily snapshot to a separate Hetzner volume until we migrate.

---

## 9. References

- [Data retention & privacy compliance](../data_retention_privacy_compliance.md)
- [Manual recovery runbook](../runbooks/manual-recovery.md)
- [BMI dispute attorney brief](../runbooks/bmi-dispute-attorney-brief.md)
- IRS Pub. 583 (records retention)
- TN Code §28-3-109 (6-year SOL for written contracts)
- Federal Rules of Evidence §901 (authentication of writings)
