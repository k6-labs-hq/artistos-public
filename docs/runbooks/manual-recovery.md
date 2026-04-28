# Manual recovery runbook (beta)

**Status:** Active for the closed-beta period. Will be retired piece by piece as
[#176](https://github.com/k6-labs-hq/ArtistOS/issues/176) lands.

## Why this runbook exists

ArtistOS automates the upstream half of royalty recovery: ingestion, anomaly
detection, claim drafting, evidence packet generation, claim state machine,
and (once a remittance is recorded) fee calculation + Trolley payout.

It does **not** automate the middle: actually contacting payers (PROs / DSPs),
filing the dispute, tracking the response, and recording the inbound payment.
Today that work is done by hand by a K6 Labs operator. This runbook is the
checklist for that work.

The blocker is concrete:

- `XR7/recovery/dispute_delivery.py` returns `"detail": "simulated"` for every
  channel — no SMTP send, no portal POST.
- `XR7/recovery/auto_filing_engine.py` returns a payload dict and never enqueues
  anything.
- `XR7/tasks/pipeline.py::submit_recovery_action` flips `Claim.status` to
  `IN_REVIEW` and exits.
- An SMTP host is already wired into the notification path but **not** the
  dispute path — see [#178](https://github.com/k6-labs-hq/ArtistOS/issues/178).
- An email-sending provider has not been provisioned —
  [#180](https://github.com/k6-labs-hq/ArtistOS/issues/180).
- The ops dashboard that would replace this runbook is tracked in
  [#181](https://github.com/k6-labs-hq/ArtistOS/issues/181).

Until the above land, the operator follows the steps below.

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

For email channels: today, send from your personal/ops mailbox — `dispute_delivery.py`
will eventually do this through the SMTP host once #178 lands.

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
- SMTP delivery: [#178](https://github.com/k6-labs-hq/ArtistOS/issues/178)
- Per-payer playbook framework: [#179](https://github.com/k6-labs-hq/ArtistOS/issues/179)
- Email provider provisioning: [#180](https://github.com/k6-labs-hq/ArtistOS/issues/180)
