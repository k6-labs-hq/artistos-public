# Manual recovery runbook (beta)

**Status:** Active for the closed-beta period. Will be retired piece by piece as
[#176](https://github.com/k6-labs-hq/ArtistOS/issues/176) lands.

## Why this runbook exists

ArtistOS automates the upstream half of royalty recovery: ingestion, anomaly
detection, claim drafting, evidence packet generation, claim state machine,
and (once a remittance is recorded) fee calculation + Trolley payout.

It does **not yet** automate the middle: actually contacting payers (PROs /
DSPs), filing the dispute, tracking the response, and recording the inbound
payment. Today that work is done by hand by a K6 Labs operator. This runbook
is the checklist for that work.

**Status as of 2026-04-30:**

| Layer | State |
|---|---|
| Email provider | ✅ Postmark provisioned, domain verified, env vars wired (#180 / #219 / #220) |
| Outbound dispute send via Postmark | ✅ infrastructure live; dispute_delivery.py wiring is #179 |
| Inbound dispute reply parse | ✅ webhook live at `/webhooks/postmark/inbound`; correlation logic is #179 |
| Per-payer dispute templates | ⏳ #179 — the next major PR |
| `XR7/recovery/dispute_delivery.py` | ⏳ still returns `"detail": "simulated"` until #179 wires it through |
| `XR7/recovery/auto_filing_engine.py` | ⏳ still returns a payload dict; #179 wires the queue + delivery |
| `XR7/tasks/pipeline.py::submit_recovery_action` | ⏳ still only flips `Claim.status` to `IN_REVIEW`; #179 advances it through real states |
| Ops dashboard for filing queue | ⏳ [#181](https://github.com/k6-labs-hq/ArtistOS/issues/181) |
| Postmark account approval status | ⏳ pending (Postmark policy review for new accounts; outbound to non-domain recipients sandboxed until cleared) |

So the **email pipe** is wired and verified end-to-end on QA. What's left
is the **per-payer playbook content** (what the dispute email actually says,
which payer accepts which attachments, how we render the evidence packet to
PDF, how we correlate replies back to specific Claims). That's #179 work and
ships next.

Until #179 lands, the operator follows the steps below.

## What the system has already done before you start

For each artist with at least one statement uploaded:

- Events + payments persisted (`events`, `payments` tables)
- Anomalies detected, gated by confidence, persisted (`anomalies` table) — once
  [#196](https://github.com/k6-labs-hq/ArtistOS/pull/196) is in
- A draft `Claim` row in state `IDENTIFIED` (the `ClaimsOrchestrator` auto-drafts
  the first one on upload)
- A signed evidence packet attached to the claim

## Operator steps (per artist, weekly cadence)

### 1. Find what's ready to file

Until the dashboard ships, query the DB directly:

```sql
SELECT c.id, c.artist_id, a.name, c.payer_name, c.amount,
       c.sol_deadline, c.status, c.created_at
FROM claims c JOIN artists a ON a.id = c.artist_id
WHERE c.status = 'IDENTIFIED'
ORDER BY c.sol_deadline NULLS LAST, c.created_at;
```

Prioritise by `sol_deadline` ascending — anything within 60 days of statute is
urgent.

### 2. Pull the evidence packet

```bash
curl -H "Authorization: Bearer $XR7_TOKEN" \
  https://api.qa.xr7.k6-labs.com/artists/$ARTIST/claims/$CLAIM/evidence-packet \
  -o packet-$CLAIM.json
```

The packet is JSON with the signed forensic record. PDF rendering is not
automated yet — paste the relevant sections into the dispute email manually,
or convert with `pandoc` if the payer accepts markdown attachments.

### 3. Open the dispute with the payer

Each payer has a different process. Keep the per-payer details in your own
notes until the `PayerPlaybook` model lands (part of #176):

| Payer | Channel | Submission point | Notes |
|---|---|---|---|
| BMI | Email | `disputes@bmi.com` | Include BMI work IDs; 30-day ack, 90-day decision |
| ASCAP | Portal + email | Member portal "Inquiry" form | Attach evidence packet PDF |
| MLC | Portal | TheMLC.com member portal | Use their dispute form; reference the song-code (`M####H`) |
| SoundExchange | Portal | soundexchange.com `My SX Account` | Letter of representation may be required |

For email channels: today, still send from your personal/ops mailbox. The
Postmark outbound infrastructure is live (#219), but `dispute_delivery.py`
hasn't been wired to call it yet — that's #179. **Don't manually compose
dispute emails through Postmark either** — once #179 lands, every dispute
needs to flow through the system to capture the outbound MessageID for
reply correlation. Mixing manual + automated sends breaks the audit chain.

### 4. Mark the claim as filed in XR7

After you send, record the case reference returned by the payer:

```bash
curl -X POST -H "Authorization: Bearer $XR7_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"payer_case_reference":"BMI-DR-12345","filed_at":"2026-04-27T15:00:00Z"}' \
  https://api.qa.xr7.k6-labs.com/artists/$ARTIST/claims/$CLAIM/mark-filed
```

(If that endpoint isn't wired yet, drop into the DB and update
`claims.status = 'FILED'`, `claims.payer_case_reference = '...'`,
`claims.proof_submitted_at = now()`.)

### 5. Track the response

Until the dashboard ships, keep a spreadsheet keyed by `claim_id` with:
- Filed date
- Payer case reference
- Expected acknowledgment date (filed + payer SLA)
- Expected decision date
- Status of last inbound communication

Re-check weekly. If a payer goes past their stated decision SLA, escalate per
their portal's rules — there's no automated nudge today.

### 6. Record the remittance when it arrives

When the bank statement shows the wire/check from the payer:

```bash
curl -X POST -H "Authorization: Bearer $XR7_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount":1234.56,"currency":"USD","received_at":"2026-05-15T00:00:00Z","reference":"BMI wire 0428"}' \
  https://api.qa.xr7.k6-labs.com/artists/$ARTIST/claims/$CLAIM/manual-remittance
```

This is the one part of the loop that's already wired end-to-end:
`record_manual_remittance` triggers `BillingEngine` (12% Founders fee) and
queues the Trolley disbursement to the artist. The audit ledger logs every
state transition.

## Things to escalate (don't try to handle alone)

- A payer disputes the underlying anomaly methodology — engineering sign-off
  before responding.
- A claim approaches `sol_deadline - 30d` with no acknowledgment — legal review
  to decide whether to escalate to outside counsel (`attorney_escalation.py`
  has hardcoded firm names; treat them as placeholders).
- A remittance amount differs materially from the claimed amount — open an issue
  on the recovery loop EPIC #176 with the discrepancy.

## Linked work

- Parent epic: [#176](https://github.com/k6-labs-hq/ArtistOS/issues/176) —
  replace simulated claim filing with real per-payer execution
- Ops dashboard: [#181](https://github.com/k6-labs-hq/ArtistOS/issues/181)
- SMTP delivery: [#178](https://github.com/k6-labs-hq/ArtistOS/issues/178) —
  infrastructure wired by #219; per-payer wiring of `dispute_delivery.py` is #179
- Per-payer playbook framework: [#179](https://github.com/k6-labs-hq/ArtistOS/issues/179) — **the next major PR; closes most of this runbook**
- Email provider provisioning: [#180](https://github.com/k6-labs-hq/ArtistOS/issues/180) — **closed by #219 + #220 on 2026-04-30**
- Postmark setup runbook: [docs/runbooks/postmark-setup.md](postmark-setup.md)
