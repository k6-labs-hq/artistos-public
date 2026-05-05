# Data retention & privacy compliance

**Last updated:** 2026-05-05

This doc captures what data ArtistOS retains, for how long, and why. Companion ADR: [docs/decisions/statement-storage-and-retention.md](decisions/statement-storage-and-retention.md).

---

## TL;DR

| Data class | Stored where | Retention | Why |
|---|---|---|---|
| Royalty statement files (raw bytes) | S3-compatible (MinIO today) | **7 years from upload** | TN 6-year contract SOL + IRS records norm + reprocessing if parser updates |
| Statement metadata (hash, filename, parse stats) | Postgres `statements` table | Indefinite (small footprint) | Audit trail, dedup key |
| Parsed events + payments | Postgres `events`, `payments` | Indefinite (closed beta scale) | Anomaly detection, dispute evidence |
| Anomaly findings | Postgres `anomalies` | Indefinite | Recovery loop core |
| Claims + communications | Postgres `claims` (JSON `communications`) | Indefinite | Legal evidence chain |
| Trolley payouts | Postgres `trolley_transactions` + Trolley API | Indefinite (financial records) | Tax + 1099 reporting |
| Supabase auth.users | Supabase | Until user deletion request | Identity |
| Postmark email artifacts | Postmark (90 days) | 90 days | Provider-controlled |
| LPOA artifacts | TODO (#tbd) | 7 years from execution | Legal evidence of authority |

---

## 1. Why we retain royalty statement files (the core decision)

We keep the **original uploaded statement bytes** for 7 years. Three drivers:

### 1.1 Audit defensibility
When we file a dispute against BMI saying "your Q3 2025 statement under-reported X by $Y," we may be asked to produce the source statement. A SHA-256 hash isn't enough — Federal Rules of Evidence require authentication via the actual document. Without the original we'd be relying on the artist or the payer to provide it back, which is fragile.

### 1.2 Reprocessing under updated parsers
This already bit us once. We extended the BMI parser on 2026-05-04 (PR #240) to capture `payer_account_id` (BMI `PARTICIPANT #`), `payer_ip_number` (IPI), and `payer_work_id` (TITLE #). Existing uploads couldn't be re-derived because the bytes were gone. Storage means future-us can re-run the latest parser against historical uploads.

### 1.3 Legal evidence in escalation
If a dispute escalates beyond BMI Member Services to litigation, the source statement becomes evidence. Tennessee's contract SOL is 6 years for written contracts; the longest reasonable period covering escalation tail is 7. IRS records retention norm is also 7 years (royalty statements feed 1099-MISC).

### 1.4 What we are NOT relying on
There is **no** music-industry equivalent to HIPAA's 7-year mandate. Our 7-year number is a defensible round-up, not a regulation. Don't cite it as "required by law" — it's our policy.

---

## 2. Storage architecture

### 2.1 Today
- **Local dev:** MinIO container on `localhost:9000`, bucket `xr7-artifacts`. Pre-configured in `.env`.
- **QA:** MinIO container `artistos-minio-1` running on the Hetzner VM via docker-compose, endpoint `http://minio:9000` inside the compose network, same bucket name.
- **Storage backend choice:** self-hosted MinIO on the same VM as the API. Durability is whatever the Hetzner VM volume gives us.

### 2.2 Migration plan
When real artist data is at stake (post-attorney-approval, first real dispute filed), migrate from self-hosted MinIO to managed object storage. Candidates ordered by preference:

1. **Hetzner Object Storage** — same provider, same datacenter, free egress within Hetzner network, ~€0.0049/GB-month
2. **Cloudflare R2** — zero egress fees, $0.015/GB-month
3. **Backblaze B2** — $0.006/GB-month
4. **AWS S3** — battle-tested, but most expensive and we're not on AWS

Migration is a config change (`S3_ENDPOINT_URL` + credentials) since boto3 is S3-protocol-agnostic. ADR: [docs/decisions/statement-storage-and-retention.md](decisions/statement-storage-and-retention.md) §4.

### 2.3 Object key convention
```
statements/{artist_id}/{file_hash}.{original_ext}
```
- `artist_id` namespace prevents cross-artist key collisions
- `file_hash` (SHA-256 of raw bytes) is the dedup key + content-addressed name
- Original extension preserved for downstream re-parse (`.csv`, `.xlsx`, `.numbers`)

---

## 3. Deduplication strategy (three layers)

We dedup at three layers, each catching a different failure mode:

### 3.1 File-level
- Mechanism: SHA-256 of raw bytes, unique constraint on `(artist_id, file_hash)` in `statements` table.
- Catches: "same file uploaded twice"
- Strength: bulletproof. 409 returned with the existing statement ID.

### 3.2 Row-level
- Mechanism: `Payment.reference_id = sha256(canonicalized_row + format_id)`. Unique constraint on `(artist_id, reference_id)`.
- Catches: "different file containing identical rows" (e.g. a partial re-upload that overlaps)
- Strength: medium. Works only if rows are byte-identical. A restated statement where BMI changed an amount won't be caught here.

### 3.3 Anomaly-level
- Mechanism: deterministic anomaly ID `(artist_id, rule_id, identity_key)`. Each rule declares a stable `identity_key` so re-detections upsert (update existing) rather than insert.
- Catches: "same finding produced by detection re-run after re-ingestion"
- Strength: bulletproof for detection idempotency.

### 3.4 Known gaps (not yet covered)
- **Restated statements.** When BMI sends Q3 2025 → corrected Q3 2025 (different amounts, same period), both sets of payments coexist. Period totals double. Mitigation: surface a "potential restatement" warning in the operator dashboard. Not implemented yet.
- **Cross-format overlap.** Artist uploads distributor's roll-up (which includes BMI as line item) AND BMI portal CSV directly. Same money, different `reference_id`. Mitigation: surface as "potential overlap" warning. Not implemented yet.
- **Multi-claim per anomaly.** No uniqueness on `(artist_id, anomaly_id)` in `claims`. Two claims for one anomaly is technically possible. Probably hasn't happened in practice but isn't guarded.

---

## 4. PII inventory & handling

| Field | Source | Where stored | Sensitivity |
|---|---|---|---|
| Artist name | Supabase user_metadata or signup form | `artists.name`, JWT | Low — public-ish |
| Artist email | Supabase auth | `artists.email`, JWT, Postmark headers | Medium |
| Supabase user_id | Supabase auth | `artists.supabase_user_id` | Low (opaque) |
| BMI member account number | Statement column `PARTICIPANT #` | `payments.payer_account_id` | Medium — financial identifier |
| IPI / CAE number | Statement column `IP #` | `payments.payer_ip_number` | Low — public-ish |
| Trolley recipient ID | Trolley onboarding | `artists.trolley_recipient_id` | High — payment routing |
| Bank account last4 | Trolley | `artists.payout_last4` | Medium |
| Royalty amounts | Statements | `payments.amount`, `claims.recovered_amount` | High — financial |

We **do not** store: SSNs, full bank account numbers, full credit card numbers, government-issued IDs, biometric data. Trolley holds those; we hold a `trolley_recipient_id` reference.

---

## 5. Retention enforcement

### 5.1 What's automated
- Statement files: bucket lifecycle rule expires objects 7 years after upload (`upload_date` tag on each object). **Not yet implemented** — to be done as part of the S3 wiring PR.
- `payer_offices.last_verified` — date stamp, not enforced; reviewed manually.

### 5.2 What's manual
- Postgres data lifecycle (no automatic deletion of old claims/anomalies). Footprint is small enough at closed-beta scale that retention doesn't pay back.
- Supabase auth.users deletion on user request — manual via Supabase dashboard.

### 5.3 User-initiated deletion (right-to-be-forgotten)
Not yet implemented. When required (post-EU/CA expansion), we'll need a script that:
- Removes Artist row + all dependent rows (claims, anomalies, payments, events)
- Removes statement objects from S3
- Removes Supabase auth user
- Records the deletion in an immutable ledger (so we can answer "did we delete X's data?" without retaining their identity)

---

## 6. Compliance touchpoints

- **GDPR / CCPA**: not yet a focus — closed beta is US artists only. When we expand internationally, we'll need: explicit consent capture at signup, data subject access endpoint, deletion endpoint.
- **SOC 2**: not pursuing in closed beta. Some controls (immutable ledger, audit logs) are SOC-2-shaped already.
- **Payment Card Industry (PCI)**: not in scope — Trolley handles all payment-card processing.
- **HIPAA**: not in scope — no PHI.

---

## 7. References

- [Statement storage + retention ADR](decisions/statement-storage-and-retention.md)
- [Manual recovery runbook](runbooks/manual-recovery.md)
- [Postmark setup runbook](runbooks/postmark-setup.md)
- BMI Writer Agreement paragraph 6(b)(iv) — 9-month claim window (governs how long we need a statement for active disputes)
- IRS Pub. 583 — records retention guidance for businesses
