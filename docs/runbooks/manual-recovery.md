# Operator runbook — recovery loop

**Last updated:** 2026-05-05
**Audience:** K6 Labs operators (Jason, Matt) + the music-rights attorney during review

This runbook is the daily playbook for running the recovery loop — file disputes, track replies, record remittances. Most of what was manual in the original 2026-04 version of this doc is now driven by the operator dashboard at `/ops`.

---

## 1. What's automated vs. manual today

| Step | State |
|---|---|
| Statement ingestion + parse | ✅ automated (POST /artists/{id}/statements/upload) |
| Anomaly detection | ✅ automated, runs after every successful upload |
| Claim drafting | ✅ automated, runs as part of detection |
| Evidence packet (PDF) generation | ✅ automated, on demand via Preview button or at file-via-email time |
| Dispute outbound (Postmark + per-payer regional office) | ✅ automated (operator clicks button) |
| Inbound reply correlation | ✅ automated (Postmark inbound webhook → claim communications timeline) |
| Status advance: PREPARED → FILED → IN_REVIEW | ✅ automated by the file/reply events |
| Remittance recording | ✅ operator-triggered (button in /ops) |
| Trolley payout to artist | ✅ wired but operator-triggered (not auto-fired post-remittance, by design — sanity check before money moves) |
| Per-payer language polish | ⏳ pending attorney review of the four briefs in `docs/runbooks/*-dispute-attorney-brief.md` |
| LPOA template | ⏳ Matt's attorney drafts |
| Render BMI required identifiers on packet PDF (account #, Work ID, distribution period) | ⏳ data captured at ingestion; PDF rendering pending |
| 9-month BMI deadline calculator (instead of generic SOL) | ⏳ pending |

---

## 2. Daily flow at `/ops`

### 2.1 Sign in
- Browse to `https://app.qa.xr7.k6-labs.com/login` (or `localhost:5173/login` for dev).
- Sign in with an admin email — `XR7_ADMIN_USER_EMAILS` env var on the API host controls the allowlist; today it's `jtrent@k6-labs.com,mkallberg@k6-labs.com`.
- Admin sign-ins skip artist auto-provisioning and route directly to `/ops`.

### 2.2 Load the queue
- Click **Load queue**. The dashboard shows all claims across all artists, grouped into tabs:
  - **Ready to file** — `PREPARED` status, evidence packet attached, awaiting filing
  - **Filed (awaiting reply)** — `FILED`, no inbound yet
  - **In review** — `IN_REVIEW`, payer has replied
  - **All** — everything
- Each row shows artist name, payer, anomaly subtype, estimated recoverable, SOL countdown, status, claim reference (`XR7-YYYY-XXXXXX`).

### 2.3 Preview the packet
- **Preview** button per row → opens the rendered evidence packet PDF in a new tab.
- The PDF includes destination office (e.g. "BMI — Nashville Office, 10 Music Square East..."), audit determination, supporting evidence, line-item detail, and a SHA-256 cryptographic signature.

### 2.4 File via email
- **File via email** button per row in `Ready to file`.
- Click → confirm dialog → POST to `/admin/claims/{id}/file-via-email`.
- The system: renders the evidence PDF, looks up the right regional office (BMI: from `Artist.bmi_office_name`, default Nashville), composes the email (HTML + plaintext), sends via Postmark, stores the outbound MessageID on the Claim's `communications` array, advances status to `FILED`.
- **Test mode:** when `XR7_DISPUTE_REDIRECT_EMAIL` is set on the API host, every send is rerouted to that test address. Subject is prefixed `[XR7 INTERNAL REVIEW]`. Use this until the attorney signs off on the language. Today it's set on local dev (`jtrent@k6-labs.com`); QA will be set when ready for the first real attorney walkthrough.
- Stub mode: if `POSTMARK_API_TOKEN` isn't set, the result panel shows `(stub — POSTMARK_API_TOKEN not set)` and no email is actually sent. Default for local without copying the token in.

### 2.5 Watch for replies
- Click the chevron on any row to expand the comms timeline. Outbound entries show MessageID + submission address. Inbound replies (when BMI responds) show From / Subject / body excerpt — Postmark's inbound webhook correlates them by `InReplyTo` header pointing at our outbound MessageID.
- Status auto-advances `FILED` → `IN_REVIEW` on first inbound.

### 2.6 Record remittance
- When the bank statement shows a wire / check from the payer, click **Record remittance** on the claim row.
- Inline form: gross amount, method (ACH / wire / check / other), reference number.
- Submit → POST to `/admin/claims/{id}/record-remittance`.
- The system: validates `gross_amount > 0`, computes platform fee (12% Founders rate) + artist net, sets `recovered_amount` + `remittance_*` fields, advances status to `FUNDS_RECEIVED`, writes a `TrolleyTransaction` row (type=REMITTANCE), appends to the immutable ledger.
- Trolley disbursement to the artist is **a separate manual step** — sanity-check the amount before money actually moves. Use `BillingEngine.disburse_via_trolley(claim_id)` (no UI button yet).

---

## 3. Per-payer specifics

| Payer | Channel | Submission target | Notes |
|---|---|---|---|
| **BMI** | Email | Regional Writer/Publisher Relations office (Nashville default) | 6 offices in `payer_offices` table; per-artist preference via `Artist.bmi_office_name`. Email body cites paragraph 6(b)(iv) of the writer agreement (9-month claim window). See [bmi-dispute-attorney-brief.md](bmi-dispute-attorney-brief.md). |
| **ASCAP** | Portal-only (Member Access Messages) | N/A — not yet supported | Attorney brief flags portal-handoff or Designated User as the path. See [ascap-dispute-attorney-brief.md](ascap-dispute-attorney-brief.md). Filing pipeline doesn't support ASCAP claims yet. |
| **MLC** | Email (`finance@themlc.com`) or Statutory audit | Not yet seeded | Attorney brief covers contractual basis. See [mlc-dispute-attorney-brief.md](mlc-dispute-attorney-brief.md). No regional offices — single team. |
| **SoundExchange** | SXDirect Contact form (authenticated) or `info@soundexchange.com` | Not yet seeded | Three payee classes (Featured Artist / SRCO / non-featured). LOD ≠ dispute authority. See [soundexchange-dispute-attorney-brief.md](soundexchange-dispute-attorney-brief.md). |

---

## 4. Data retention & dedup notes (operator-relevant)

These apply at upload time but operators should know about them when an artist asks "what happens if I upload the same file twice?":

- **Same file uploaded twice** → 409 with the existing statement ID (file_hash dedup).
- **Different file with overlapping rows** → only the new rows are persisted (row-level reference_id dedup).
- **Re-running detection on existing data** → existing anomalies get updated, no duplicates created (anomaly-level deterministic ID).
- **Restated statement (BMI sends a corrected Q3)** → both old and new payments coexist in the database. Period totals double. **Operator should manually flag this** until the restatement-detection feature ships. Reference: [data_retention_privacy_compliance.md §3.4](../data_retention_privacy_compliance.md).

Original statement files are saved in S3-compatible storage (MinIO today) for 7 years to support reprocessing under updated parsers and audit defensibility. ADR: [statement-storage-and-retention.md](../decisions/statement-storage-and-retention.md). **Implementation is pending** — at the time of this update, the upload pipeline still hashes and parses but doesn't write the original bytes. To be wired next.

---

## 5. Things to escalate (don't handle alone)

- A payer disputes the underlying anomaly methodology — engineering sign-off before responding.
- A claim approaches `sol_deadline - 30d` with no acknowledgment — legal review to decide whether to escalate. **For BMI specifically, the 9-month claim window is much shorter than SOL — bring forward to attorney earlier.**
- A remittance amount differs materially from the claimed amount — open a follow-up with the payer to itemize, then either accept-and-close or escalate to attorney.
- A payer responds with a refusal that cites contractual language — pause filing further claims against that payer until the attorney has reviewed the refusal language.

---

## 6. Linked work

- [Statement storage + retention ADR](../decisions/statement-storage-and-retention.md)
- [Data retention & privacy compliance](../data_retention_privacy_compliance.md)
- [Postmark setup runbook](postmark-setup.md)
- [BMI / MLC / ASCAP / SoundExchange attorney briefs](.) (in this directory)
- [Strategic 30-day plan](../strategy/next-30-days.md)
- Parent epic: [#176](https://github.com/k6-labs-hq/ArtistOS/issues/176) (now substantially complete; remaining items live in the attorney briefs)
- Operator dashboard: [#181](https://github.com/k6-labs-hq/ArtistOS/issues/181) (closed by #230 / #232 / #233 / #234 / #243)
