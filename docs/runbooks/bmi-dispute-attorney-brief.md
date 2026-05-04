# BMI dispute filing — attorney review brief

**Status:** Draft for Matt's music-rights attorney. Do NOT file disputes against
BMI in this format until the questions in §4 are resolved.

**Date drafted:** 2026-05-04
**Authors:** Jason Trent (CTO) + Claude

---

## 1. Why this document exists

ArtistOS automatically detects royalty anomalies (e.g. high-retroactive-payment
ratios, missing distributions) and prepares a dispute packet — a PDF + email body
— intended for BMI's Writer/Publisher Relations team. Before we send a real
dispute on behalf of a real artist, we need an attorney to confirm:

- The submission channel + address are correct.
- The contractual citations we invoke are accurate.
- A third-party service (XR7 / K6 Labs) operating under a Limited Power of
  Attorney is an acceptable submitter under BMI's writer agreement.
- The packet content is sufficient and appropriately framed (not aggressive,
  not under-supported).

Sample rendered packet attached separately as `xr7-evidence-<claim_id>.pdf`.

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

## 3. What we currently have, and what's wrong with it

### 3.1 Submission email
- **What we have:** `member-disputes@bmi.com` (invented placeholder in
  `XR7/recovery/payer_config.py:71`).
- **Problem:** That address does not exist. A real send would bounce — and
  bouncebacks against our verified Postmark sender hurt our deliverability
  reputation.
- **Fix (pending attorney sign-off):** Default to `nashville@bmi.com`. Add a
  per-artist "BMI region" override when we onboard non-Nashville artists.

### 3.2 Salutation
- **What we have:** "To the BMI Member Disputes Team,"
- **Problem:** That team does not exist by that name. BMI's process directs
  inquiries to the regional Writer/Publisher Relations office.
- **Fix (pending attorney sign-off):** "To the BMI Writer/Publisher Relations
  Team — Nashville Office,"

### 3.3 SLA framing
- **What we have:** "We respectfully request acknowledgement of receipt within
  30 days, and a substantive response within 90 days, in line with BMI's
  published member-relations procedure."
- **Problem:** BMI does NOT publish a member-relations response SLA. Asserting
  one as their commitment is factually wrong and could undermine credibility.
  Our 30/90 days are our *internal* escalation timer, not their commitment.
- **Fix (pending attorney sign-off):** Reframe as our request, not their
  obligation. "We respectfully request a response by [date], which we will
  treat as the customary response window for the Nashville Writer/Publisher
  Relations office."

### 3.4 Contractual citation — currently absent
- **What we have:** No reference to the writer agreement.
- **Problem:** BMI's 9-month claim window is the binding rule. Citing it
  directly (paragraph 6(b)(iv) of the BMI writer agreement) signals to the
  investigator that we know the contractual basis and are filing within the
  window. Without it, our notice could be processed as a generic complaint
  rather than a contractually-timely claim.
- **Fix (pending attorney sign-off):** Add: "Pursuant to paragraph 6(b)(iv)
  of the BMI writer affiliation agreement, this constitutes timely written
  notice of claimed omission/miscalculation within nine (9) months of the
  [DISTRIBUTION DATE] royalty distribution."

### 3.5 Required member-identifying fields — currently absent
- **What we have:** Artist name + claim ID. Optionally `artist_pro_id` (which
  we don't actually populate today).
- **Problem:** BMI's required fields aren't in our model: BMI account number,
  song title, BMI Work ID, distribution date being disputed.
- **Fix (pending attorney sign-off):** Extend the Artist + Claim model to
  capture these, surface them in the dispute packet. Block "File via email"
  in the operator dashboard if any required field is missing.

### 3.6 Internal taxonomy bleeding through
- **What we have:** `Finding: HIGH_RETROACTIVE_PAYMENT_RATIO` in the email body.
- **Problem:** That's our internal rule_id. BMI investigators want plain
  English, not our category labels.
- **Fix (pending attorney sign-off):** Replace with a one-sentence plain-English
  summary keyed off the rule. The `description` field on the Anomaly already
  has plain English; we should lead with it.

### 3.7 LPOA framing
- **What we have:** "A signed Limited Power of Attorney is available on request."
- **Problem:** Whether BMI accepts an LPOA-authorized third-party submitter is
  the **central legal question** of our service-bureau model. BMI's writer
  agreement is bilateral (writer ↔ BMI). A third party (K6 Labs) submitting on
  behalf of the writer is not explicitly contemplated.
- **Question for attorney:** §4.1 below.

### 3.8 Cryptographic Provenance section in PDF
- **What we have:** SHA-256 hash chain references in the rendered packet.
- **Problem:** Probably overkill for a BMI member-relations review. Useful if
  the matter ever escalates to discovery, but at the initial-inquiry stage it
  may signal "this is litigation-prep" rather than "we want to resolve this."
- **Question for attorney:** §4.4 below.

### 3.9 Foreign vs. domestic
- **What we have:** One template for all BMI claims.
- **Problem:** BMI's procedure differentiates foreign performances. Foreign
  claims include territory + performance source detail and may go to a
  different team (`statement@bmi.com` is mentioned for foreign).
- **Fix (pending attorney sign-off):** Branch on whether the underlying
  payments are domestic or foreign at the rule-evaluation step.

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
1. Update `payer_config.py` BMI entry: `submission_email`, `salutation`,
   add region awareness.
2. Update `dispute_email.txt`: add contractual citation, fix SLA framing,
   replace internal rule_id with plain English.
3. Extend `Claim` model to capture BMI account number + Work ID + distribution
   date being disputed.
4. Add a 9-month deadline calculator that supersedes SOL for BMI claims.
5. Block "File via email" in `/ops` until required fields populated.
6. Send first real test filing for a Nashville-network artist with attorney CC'd.

### If attorney requires writer-direct submission:
1. Repurpose `/admin/claims/{id}/file-via-email` from "send to BMI" to
   "send the packet to the writer for them to forward." Single mail-to-self
   send, no LPOA flow needed.
2. Adjust the operator dashboard: instead of "File via email" we have
   "Send packet to writer for filing."
3. Inbound webhook still works — the writer can BCC us when forwarding.

### If attorney requires a CC to BMI's legal/compliance team:
1. Add CC field to `payer_config.py`.
2. Update the email send logic to CC.

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
