# BMI dispute filing — attorney review brief

**Status:** Draft for Matt's music-rights attorney. Do NOT file disputes against
BMI's real submission addresses until the questions in §4 are resolved. We CAN
fly the full pipeline to a test inbox (see §3.10) — set
`XR7_DISPUTE_REDIRECT_EMAIL` and the system reroutes every send to that address.

**Date drafted:** 2026-05-04
**Last updated:** 2026-05-04 (post-#246/#247 implementation pass)
**Authors:** Jason Trent (CTO) + Claude

---

## 1. Why this document exists

ArtistOS automatically detects royalty anomalies (e.g. high-retroactive-payment
ratios, missing distributions) and prepares a dispute packet — a PDF + email body
— intended for BMI's Writer/Publisher Relations team. Before we send a real
dispute on behalf of a real artist, we need an attorney to confirm:

- The submission channel + address are correct. **(Implementation done; review
  the rendered output.)**
- The contractual citations we invoke are accurate. **(Citation now in the email
  body — paragraph 6(b)(iv); review the language.)**
- A third-party service (XR7 / K6 Labs) operating under a Limited Power of
  Attorney is an acceptable submitter under BMI's writer agreement. **(Open —
  §4.1.)**
- The packet content is sufficient and appropriately framed (not aggressive,
  not under-supported). **(Open — §4.4. Sample PDF attached.)**

### Implementation status (2026-05-04)

| Item | Brief § | Status |
|---|---|---|
| Submission email — drop bouncing placeholder, route via DB-backed regional offices | 3.1 | **Fixed** — `payer_offices` table seeded with all 6 BMI regions; filing pipeline reads artist's `bmi_office_name` (default Nashville) |
| Salutation — replace fake "Member Disputes Team" | 3.2 | **Fixed** — now "Writer/Publisher Relations Team — `<office>` Office" |
| SLA framing — stop asserting BMI's "published procedure" | 3.3 | **Fixed** — now "we respectfully request a response by `<date>`" framed as our request, not their commitment |
| Contractual citation — paragraph 6(b)(iv) | 3.4 | **Fixed** — citation block in every BMI dispute email body |
| Per-row identifiers — BMI account #, IPI, Work ID, distribution period | 3.5 | **Partial** — fields captured at ingestion (`Payment.payer_account_id`, `payer_ip_number`, `payer_work_id`), not yet rendered on the packet PDF |
| Internal taxonomy in email body (`HIGH_RETROACTIVE_PAYMENT_RATIO`) | 3.6 | **Not fixed** — still leaks the rule_id; needs a plain-English mapping |
| LPOA framing | 3.7 | **Open** — language slightly improved but the legal gate is §4.1 |
| Cryptographic Provenance section in PDF | 3.8 | **Open** — §4.4 |
| Foreign vs. domestic differentiation | 3.9 | **Open** — single-template still; rule-evaluation branching deferred |
| Test-mode redirect (fly the pipeline to ourselves) | 3.10 | **Implemented** — `XR7_DISPUTE_REDIRECT_EMAIL` env var |

Sample rendered packet attached separately as `xr7-evidence-<claim_id>.pdf`.
Sample rendered email body available on request — file a redirect-mode test
send and check the inbox.

---

## 2. What BMI actually says (verbatim, with sources)

### 2.1 The 9-month claim window (binding — this is in every writer's contract)

From the **BMI Writer Agreement** (form W800 225, page 2, paragraph 6(b)(iv)):

> "we shall have no obligation to make payment hereunder with respect to ...
> (iv) any performance of a Work which you claim was either omitted from or
> miscalculated on a royalty statement and for which we have not received
> written notice from you of such claimed omission or miscalculation within
> nine (9) months of the date of the royalty distribution seeking to be
> adjusted."

From the **Miscellaneous Royalty Rules** page
(`bmi.com/creators/royalty/miscellaneous_royalty_rules`):

> "All claims for adjustments to royalty distributions must be made in writing
> to your local Writer/Publisher Relations office within nine months of the
> date of the distribution seeking to be adjusted. Adjustments to royalties
> which were or should have been paid more than nine months before notice of
> the claim is received by BMI will not be considered."

**Implication:** SOL (statute of limitations) is irrelevant for BMI claims —
BMI's contractual 9-month window is the binding deadline and is much shorter
than any state SOL. Our system today calculates SOL deadlines (3+ years out);
for BMI claims this is misleading. We need a payer-specific deadline calculator
that uses the distribution date + 9 months for BMI rows.

### 2.2 Submission channel — regional, not central

The BMI writer kit (form 3-2025) directs all member inquiries to the regional
Writer/Publisher Relations office:

| Office     | Email                  | Address                                          |
|------------|------------------------|--------------------------------------------------|
| Nashville  | nashville@bmi.com      | 10 Music Square East, Nashville, TN 37203        |
| New York   | newyork@bmi.com        | 7 World Trade Center, 250 Greenwich, NY 10007    |
| Los Angeles| losangeles@bmi.com     | 9420 Wilshire Blvd, Suite 200, Beverly Hills CA  |
| Atlanta    | atlanta@bmi.com        | (Atlanta office)                                 |
| Austin     | austin@bmi.com         | 1400 S. Congress Ave, Suite B 200, Austin TX     |
| London     | london@bmi.com         | 84 Harley House Marylebone Road, London NW1 5HN  |

For royalty *statement questions* specifically (vs. formal claims):
`statement@bmi.com` is mentioned in BMI FAQ as the address for missing-payment
inquiries, particularly foreign distributions.

**For our Nashville-network artists** (the cohort we'll start with), the right
address is `nashville@bmi.com`.

### 2.3 What BMI asks the member to include

From the FAQ + writer kit:

- Member name + **BMI account number** (line 1 of any inquiry)
- Song title + **BMI Work ID** (if available)
- Performance source (TV / radio / streaming / international)
- Territory of activity (esp. for foreign)
- Specific distribution date being disputed
- "A single packet per song" with timeline + numbered evidence list

---

## 3. What we currently send (post-#246/#247)

### 3.1 Submission email — Fixed
- **Before:** `member-disputes@bmi.com` (invented placeholder; would have
  bounced).
- **Now:** Submission goes to a regional Writer/Publisher Relations office
  resolved at filing time from our `payer_offices` table. The artist's
  region preference (`Artist.bmi_office_name`) controls routing; default
  is **Nashville (`nashville@bmi.com`)** for our country/Americana
  cohort. All six BMI offices are seeded with their published email +
  mailing address from the BMI Writer Kit (form 3-2025).
- **Implementation:** `XR7/models/payer_office.py`, alembic migration
  `20260504_0038`, `XR7/recovery/payer_config.py:get_payer_office()`.
- **Attorney check needed:** verify the Nashville address is the right
  default for our writer cohort, and confirm the address-resolution
  scheme (writer self-selects region at signup) is acceptable.

### 3.2 Salutation — Fixed
- **Before:** "To the BMI Member Disputes Team," — a team that doesn't
  exist by that name.
- **Now:** "To the Broadcast Music, Inc. Writer/Publisher Relations Team
  — Nashville Office," (the office name varies per artist's region).
  Falls back to a generic "Writer/Publisher Relations Team," for any
  payer without an office record.
- **Attorney check needed:** confirm the regional-office form is
  appropriate; flag if a different in-house naming convention is more
  conventional.

### 3.3 SLA framing — Fixed
- **Before:** "in line with BMI's published member-relations procedure"
  — factually wrong, BMI doesn't publish one.
- **Now:** "We respectfully request a response by `<filing date + 30
  days>`. We understand response times can vary; this date is provided
  as our internal escalation reference and is not asserted as your
  published commitment." (Concrete date, framed as our request not their
  commitment.)
- **Attorney check needed:** is 30 days too aggressive? Too soft? The
  brief's recommendation was generic; a concrete view from someone who's
  worked actual BMI inquiries would help.

### 3.4 Contractual citation — Fixed
- **Before:** absent.
- **Now:** For every BMI claim, the email body includes:
  > "Pursuant to paragraph 6(b)(iv) of the BMI writer affiliation
  > agreement, this constitutes timely written notice of claimed
  > omission or miscalculation. The 9-month claim window from the
  > subject distribution date applies; we are filing within that
  > window."
- **Attorney check needed:** is paragraph 6(b)(iv) the right citation?
  Is the language overconfident or underconfident? Are we adequately
  identifying which distribution we're disputing? (Today the language
  doesn't name a specific period — the packet shows it but the email
  body just says "the subject distribution.")

### 3.5 Required member-identifying fields — Partial
- **Before:** Just artist name + claim ID; no member account number,
  Work ID, or distribution period.
- **Now (data layer):** Every Payment row carries:
  - `payer_account_id` (BMI `PARTICIPANT #`)
  - `payer_ip_number` (`IP #` / IPI)
  - `payer_work_id` (BMI `TITLE #` / BWID)
  Plus `period_start`/`period_end` decoded from the `PERIOD` column.
  Captured at ingestion from BMI's 28-column Royalty Distribution
  Statement CSV.
- **Still pending:** the packet PDF doesn't yet render these
  identifiers in a "Subject distribution" or "Member of record" block.
  The data is on hand; the template just doesn't surface it. Half-day
  follow-up to add the section once the attorney confirms what BMI
  expects to see prominently.

### 3.6 Internal taxonomy bleeding — NOT fixed
- **Before:** `Finding: HIGH_RETROACTIVE_PAYMENT_RATIO` in email body.
- **Now:** Same. The template still does `Finding: {{ finding_subtype
  }}` where `finding_subtype` resolves to the rule_id.
- **Why not fixed yet:** rule_ids map to plain-English descriptions per
  rule, not per dispute, and choosing the right framing per rule is
  better done with attorney input on tone. Probably a sentence per rule,
  e.g. "We have identified an unusually high proportion of retroactive
  payments to this writer — 72% of BMI distributions in the past 12
  months arrived 4-9 months after the statement period."
- **Attorney check needed:** language for each rule's "plain English
  framing." Quick to land once we have attorney-blessed phrasing.

### 3.7 LPOA framing — Marginally improved; legal gate still open
- **Before:** "A signed Limited Power of Attorney is available on
  request."
- **Now:** "`<artist>` has authorised XR7 (a service of K6 Labs, Inc.)
  under a signed Limited Power of Attorney to submit royalty audit
  findings on their behalf and to receive correspondence in response. A
  copy of the LPOA is available on request."
- **Whether BMI accepts a third-party LPOA-authorized submitter at all
  remains §4.1 — central legal question.**

### 3.8 Cryptographic Provenance section in PDF — Unchanged
- **What we have:** SHA-256 hash of the rendered packet contents
  embedded on the cover and on a "Cryptographic Provenance" section
  near the end.
- **Question for attorney:** §4.4 below. Easy to drop the section if it
  signals litigation-prep; trivially restored later if we ever escalate.

### 3.9 Foreign vs. domestic — Unchanged
- **What we have:** Single template for all BMI claims.
- **Pending attorney input.** Per BMI's docs, foreign claims may go to
  `statement@bmi.com` instead of the regional office; we'd need to
  branch on the underlying payments' territory.

### 3.10 Test-mode redirect — Implemented
- **What we built (#247):** `XR7_DISPUTE_REDIRECT_EMAIL` env var. When
  set, every outbound dispute is rerouted from the payer's real
  submission inbox to that test address. The full Postmark pipeline
  still runs (MessageID persisted, claim advances to `FILED`, inbound
  webhook can correlate replies), but BMI never sees anything. The
  email subject gets a `[XR7 INTERNAL REVIEW]` prefix and a footer
  block flags the redirect for whoever opens it.
- **Why this exists:** so the attorney (or you, or Matt) can review the
  rendered email by triggering a real dispute file from `/ops` and
  checking the resulting inbox, without exposing BMI to anything. Unset
  the env var when ready to fly real disputes.
- **Currently set to:** `jtrent@k6-labs.com` on local dev; not yet set
  on QA (will be set as part of the QA deploy for #246/#247).

---

## 4. Open questions for attorney review

### 4.1 Third-party submission authority
**Question:** Can K6 Labs / XR7 submit a royalty claim to BMI on behalf of an
artist using a Limited Power of Attorney, when the writer agreement (paragraph
17, paraphrased) restricts assignment of monies-due rights to attorneys-in-fact
without written consent? Does the LPOA need to be from a licensed attorney, or
is a notarized writer-signed LPOA sufficient?

**Why it matters:** This is the core legal gating question for our service
bureau model. If the answer is "no third-party submissions," our model needs
to change to "we draft the packet, the writer themselves submits it from their
own email." If the answer is "yes, with these conditions," we need to draft
the LPOA accordingly.

### 4.2 LPOA template language
**Question:** Will you draft an LPOA template that:
- Authorizes K6 Labs to file royalty audit findings with BMI on behalf of the
  writer
- Authorizes K6 Labs to receive correspondence in response
- Does NOT authorize K6 Labs to settle, accept payment on behalf of, or release
  claims (we want all of those to flow through the writer)
- Is revocable by the writer at any time
- Is consistent with the BMI writer agreement's restrictions

### 4.3 Contractual citation accuracy
**Question:** Is citing paragraph 6(b)(iv) of the BMI writer agreement appropriate
in the dispute email body, given that the writer (not K6 Labs) is the contracting
party? Is there better language to use?

### 4.4 Tone and content of the packet
**Question:** Review the attached `xr7-evidence-<claim_id>.pdf`. Specifically:
- Is the cover-page SOL urgency framing too aggressive for an initial inquiry?
- Is the "Cryptographic Provenance" page useful or signaling-litigation-prep?
- Are the section names (Royalty Audit Finding, Supporting Evidence, etc.)
  appropriate, or should we adopt BMI's preferred terminology?
- Is anything missing that an investigator would need on first read?

### 4.5 Single-packet-per-song requirement
**Question:** BMI's stated preference is "a single packet per song." Our system
detects anomaly-level findings that may span multiple songs (e.g.
HIGH_RETROACTIVE_PAYMENT_RATIO is a payer-level pattern across the whole
catalog). Is it acceptable to file one packet per anomaly with multiple songs
referenced, or do we need to split into per-song packets?

### 4.6 Account number / Work ID — required vs. helpful
**Question:** If the writer has a BMI account number and Work IDs, including
them is obviously good. If they don't have them readily available, can a
filing still proceed by referencing artist legal name + song title + ISRC, or
will BMI reject as insufficient?

---

## 5. What we'll do based on attorney response

### If attorney approves third-party submission with LPOA:

Most of the structural work is already shipped (#245/#246/#247) and is
visible to the attorney via the test-mode redirect. What remains is
language polish + the deadline calculator + flying real disputes.

1. ~~Update `payer_config.py` BMI entry: `submission_email`, `salutation`,
   add region awareness.~~ **Done** — empty placeholder, regional offices in
   `payer_offices` table, lookup in `get_payer_office()`.
2. Update `dispute_email.txt`: ~~add contractual citation~~ ✅ done,
   ~~fix SLA framing~~ ✅ done, **still pending: replace the internal
   `rule_id` with plain English (§3.6).** Need attorney-blessed phrasing.
3. ~~Extend `Claim` model to capture BMI account number + Work ID +
   distribution date being disputed.~~ **Done** at the Payment level —
   `Payment.payer_account_id`, `payer_ip_number`, `payer_work_id`,
   `period_start/end`. **Still pending: render those fields in a
   "Subject distribution" block on the packet PDF (§3.5).**
4. Add a 9-month deadline calculator that supersedes SOL for BMI claims.
   **Not started.**
5. Block "File via email" in `/ops` until required fields populated.
   **Not started** — currently only validates that `payer_name` is set.
6. Send first real test filing for a Nashville-network artist with
   attorney CC'd. **Ready** — unset `XR7_DISPUTE_REDIRECT_EMAIL` and click
   "File via email" on the operator dashboard.

### If attorney requires writer-direct submission:
Most of the existing pipeline can be repurposed; the change is in who
the email is addressed to.

1. Repurpose `/admin/claims/{id}/file-via-email` from "send to BMI" to
   "send the packet to the writer for them to forward." Single
   mail-to-self send, no LPOA flow needed.
2. Adjust the operator dashboard: instead of "File via email" we have
   "Send packet to writer for filing."
3. Inbound webhook still works — the writer can BCC us when forwarding.

### If attorney requires a CC to BMI's legal/compliance team:
1. Add CC field to the `payer_office` schema (a new column, generic
   across payers — not all payers need a CC).
2. Update the email send logic to CC when present.

### If attorney rejects the contractual citation language (§3.4):
1. Update the `contractual_citation` block in
   `XR7/recovery/dispute_delivery.py:_render_email_body()` per attorney
   guidance. Keep the structure (the citation is per-payer logic, not
   per-call).

---

## 6. References

- BMI Writer Agreement (form W800 225) — paragraph 6(b)(iv) for the 9-month
  claim window; paragraphs 17 + 20 for assignment restrictions.
- BMI Miscellaneous Royalty Rules: bmi.com/creators/royalty/miscellaneous_royalty_rules
- BMI FAQ: bmi.com/faq/category/royalties
- BMI Writer Kit (form 3-2025) — regional office addresses.
- ArtistOS code:
  - `XR7/recovery/payer_config.py` — current per-payer config
  - `XR7/services/templates/dispute_email.txt` — current email body
  - `XR7/services/templates/evidence_packet.html` — current PDF template
