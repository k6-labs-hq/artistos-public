# MLC dispute filing — attorney review brief

**Status:** Draft for Matt's music-rights attorney. Do NOT file an underpayment
inquiry against The MLC in this format until the questions in §4 are resolved.

**Date drafted:** 2026-05-04
**Authors:** Jason Trent (CTO) + Claude

---

## 1. Why this document exists

ArtistOS automatically detects royalty anomalies (e.g. high-retroactive-payment
ratios, missing distributions) and prepares a dispute packet — a PDF + email
body — intended to surface underpayments to the relevant payer. The MLC is the
US statutory mechanical-royalty collective designated under the Music
Modernization Act (MMA, 17 U.S.C. § 115). Before we send a real
underpayment inquiry on behalf of a real artist to The MLC, we need an
attorney to confirm:

- The submission channel + address are correct.
- The legal/regulatory citations we invoke are accurate.
- A third-party service (XR7 / K6 Labs) operating under a Limited Power of
  Attorney is an acceptable submitter under MLC policies and the MMA.
- Whether the right vehicle is an informal Finance inquiry, a statutory member
  audit under 17 U.S.C. § 115(d)(3)(L), or both.

**Critical structural difference vs. BMI:** BMI is a contractual PRO with a
9-month claim window baked into the writer agreement. The MLC is a
**statutory** collective whose Members do not sign a BMI-style affiliation
agreement. The MLC's published "Dispute Policy" applies to **ownership
conflicts** between Members (Work overclaims, Share counterclaims) — NOT to
member-vs-MLC underpayment claims. The closest analogue to a formal
underpayment-claim window for The MLC is the statutory **member audit
right**, which has a 3-calendar-year look-back and is restricted to once per
year per audited year.

Sample rendered packet attached separately as `xr7-evidence-<claim_id>.pdf`.

---

## 2. What The MLC actually says (verbatim, with sources)

### 2.1 No published claim window for underpayment notices (gap to confirm)

The MLC publishes one binding dispute policy: the **Dispute Policy: Musical
Work Ownership** (February 2021). It is scoped only to ownership conflicts:

> "This policy applies to Conflicts concerning claims of Ownership to Works
> or Shares, which may include: Work overclaims, where Claims to a Work
> exceed 100% of Shares; Share counterclaims, where Claims to a specifically
> identifiable Share exceed the amount of that Share."
> — *MLC Dispute Policy: Musical Work Ownership, §2.1*

> "The Collective does not judge or resolve Conflicts or Disputes, or
> participate in the substantive resolution of Conflicts or Disputes. The
> Collective encourages Claimants to engage in dispute resolution processes,
> and may provide information on outside dispute resolution resources."
> — *§1.2*

A royalty-calculation underpayment claim by a Member against MLC is **not a
"Conflict"** under this policy. As of the date of this draft, our research
found no MLC-published policy that establishes a contractual deadline for
Members to file underpayment claims against MLC itself. **This is a gap to
confirm with counsel** — see §4.1.

### 2.2 The statutory member-audit right is the only formal recourse mechanism

Source: themlc.com/member-audits, citing **17 U.S.C. § 115(d)(3)(L)** and
**17 U.S.C. § 115(e)(25)**:

> "The MMA also grants rightsholders the right to conduct an audit of The
> MLC to verify the accuracy of their royalty payments, should they wish to
> do so."

> "A copyright owner can audit The MLC only once per year for any (or all)
> of the preceding three calendar years. Each year can only be audited
> once."

> "The audit must be conducted by a qualified auditor, which means an
> independent, certified public accountant with experience performing music
> royalty audits."

> "The copyright owner is responsible for the cost of the audit."

**Audit notice procedure** (themlc.com/member-audits):

> "Delivery of the notice to The MLC can be accomplished via email to
> MemberAudits@themlc.com, with a copy delivered by mail to The MLC at
> 333 11th Avenue South, Suite 200, Nashville, TN 37203 ATTN: Member Audit."

> "The notice must identify the period of time to be audited."

The notice must also be filed simultaneously with the U.S. Copyright Office.

**Implication:** The 3-year look-back (per § 115(d)(3)(L)) is a **statutory
right**, not a deadline for action. There is no published shorter window
forcing earlier informal inquiry. However, "underpaid amount" recovery
following an audit is bounded by which years are still in look-back at the
time of the audit notice — i.e. distributions older than 3 calendar years
prior to the audit notice are **not** auditable through this mechanism.

### 2.3 Informal channel — Finance inquiry

For routine royalty/payment questions, MLC publishes (themlc.com/contact):

> "Royalties & Payment Issues: finance@themlc.com — designated for
> 'questions related to Royalties or Assessment Payments'"

For general support: `support@themlc.com`, phone `(615) 488-3653` (Mon-Fri
8am-6pm CT), and the Portal contact form at `https://portal.themlc.com/contact-us`.

For misdirected royalties specifically (themlc.com/royalty-income-tracking):

> "Direct inquiries about potentially misdirected royalties to The MLC
> Support Team at https://portal.themlc.com/contact-us, including member
> name, member number, affected works, and relevant details."

This is the **informal** channel. It does not have a published response SLA
and does not trigger any statutory rights.

### 2.4 Required identifying fields for any inquiry

Synthesized from themlc.com/royalty-income-tracking and the audit-notice
procedure:

- **Member name** + **Member number** (MLC Member ID) — line 1 of any
  inquiry.
- **Affected works** identified by **MLC Song Code** (the MLC's internal
  work identifier) and ideally **ISWC**.
- For specific royalty lines: distribution period and **processing type**.
  MLC statements distinguish original ("Royalty Detail") distributions from
  reprocessing/adjustment distributions; identifying which is being
  challenged matters because reprocessings flow from DSP-side adjustments
  authorized under 37 CFR § 210.27(k).
- For audit notices: "the period of time to be audited" (per
  themlc.com/member-audits).

The MLC's two statement layouts are described in the Help Center
(help.themlc.com/en/support/what-do-the-different-statement-layouts-mean):

> "Royalty Detail: provides royalty data corresponding with the individual
> sound recordings contained in DSP usage reports."
> "Work Summary: provides royalty data summarized at the musical work level."

ISRC appears at the Royalty Detail (sound-recording) level; ISWC appears at
the Work Summary level. Both are useful evidence in any inquiry.

### 2.5 Format expectations

There is **no published format spec** for member-initiated inquiries (in
contrast to DSP-side reporting, which is heavily specified via DDEX DSRF and
the various cover-sheet templates at themlc.com/specifications-templates-and-guidelines).
The contact form at portal.themlc.com/contact-us is a free-text web form;
finance@themlc.com is a regular email inbox. We did not find evidence of a
character limit, attachment-type restriction, or one-song-per-packet rule.

For audit notices, the format is dictated by the Copyright Office's Notice
of Intent to Audit rules (37 C.F.R. and the Federal Register notices —
Justia regulation tracker shows historical filings, e.g. 2023-27554 and
2026-02298, demonstrating the form factor).

### 2.6 No published "Designated Member Representative" framework

We searched themlc.com, the Help Center, the Member Hub onboarding docs,
and policy PDFs for an LPOA-style "Designated Member Representative"
authorization. **We did not find one.** What MLC does publish:

- **User permissions inside the Portal** (help.themlc.com/en/support/new-member-adding-a-user):
  the Member's Super User can add other Users by email and assign permission
  levels. This is intra-Member access control, not third-party authorization.
- **Contact types in Member Settings** (help.themlc.com/en/support/contact-types):
  Public Contact (required, regulated), Finance Contact, Legal Contact,
  Copyright Contact. These are notification routing tags for MLC-to-Member
  communications, not authority-to-act tags.
- **Membership eligibility** (themlc.com/membership) does contemplate
  songwriters whose works are "managed by a publisher or administrator,"
  but the publisher/administrator's authority flows through that party's
  own Member account, not through an LPOA filed with MLC.

The MMA itself (17 U.S.C. § 115(d)(3)(D)(ix)(I)(aa)) requires MLC to
maintain a publicly accessible database, and § 115(d)(3) generally
contemplates that copyright owners "or their authorized representatives"
deal with MLC, but no MLC-published procedure governs how an authorized
representative who is not a Member files an underpayment inquiry on a
Member's behalf.

**This is the critical gap for our service-bureau model** — see §4.2.

### 2.7 How responses are returned

From the MLC Dispute Policy (ownership conflicts) §3.14:

> "Notice: A Notice that is provided either through The MLC Portal, to the
> email address provided for a Claimant in its Portal account, or as
> otherwise reasonably determined by The MLC to notify a Claimant."

So formal MLC notices for ownership conflicts go via Portal + Member email
of record. For informal Finance inquiries, response is by reply email. For
audit notices, MLC's response procedure post-audit (themlc.com/member-audits):

> "Underpayments: The MLC will pay the underpaid amount to the copyright
> owner."
> "Overpayments: Either The MLC will debit the copyright owner for the
> overpaid amount, or the copyright owner can refund the overpaid amounts
> to The MLC."

---

## 3. What we currently have, and what's wrong with it

**TODO — Jason fills this in.** Code-side gaps in `payer_config.py` (which
currently uses `support@themlc.com`), the email template, the evidence
packet, and the Claim model.

---

## 4. Open questions for attorney review

### 4.1 Is there any contractual or policy claim window for underpayment notices?

**Question:** Our research found no MLC-published deadline specific to
member-initiated underpayment inquiries. The only formal mechanism is the
statutory audit (3-year look-back, once-per-year, qualified-CPA-only). Is
there any contractual document — Member Onboarding Agreement, Portal Terms
of Use, MMA implementing regulation, or MLC Operations Advisory Committee
policy — that imposes a shorter informal claim window we missed? In
particular, is there anything that would foreclose an informal Finance
inquiry filed today against a 2024 distribution?

**Why it matters:** Drives whether our system needs a payer-specific
deadline calculator for MLC. If the answer is "no shorter window, only the
3-year statutory audit look-back applies to formal recovery," we just track
the audit-eligibility horizon. If counsel finds a hidden contractual
window, we need to surface it.

### 4.2 Third-party submission authority — the central question

**Question:** Can K6 Labs / XR7 file an informal underpayment inquiry to
`finance@themlc.com` on behalf of a Member using a Limited Power of
Attorney, when MLC does not publish a Designated Member Representative or
LPOA acceptance policy? Three sub-questions:

  a. Is informal Finance-channel inquiry by a non-Member representative
     accepted in practice (even if not formally documented), the way it
     is for most service-bureau interactions with payers?

  b. For a statutory audit under 17 U.S.C. § 115(d)(3)(L), the audit
     itself MUST be performed by a qualified independent CPA — K6 Labs
     does not qualify. Can K6 Labs nonetheless act as the Member's
     representative for *initiating* the audit (drafting and serving the
     Notice of Intent to Audit, retaining the CPA), with the CPA
     performing the audit work?

  c. Could K6 Labs become a Member directly (as a publisher/administrator)
     by having Members assign administration rights via a publishing
     administration agreement — and thus submit through our own MLC
     Member account rather than as an outside representative?

**Why it matters:** This is the core legal gating question for our
service-bureau model. If the answer to (a) is "no, MLC will only respond
to inquiries from the Member email of record," our model is "we draft the
packet, the Member submits it from their Portal account or email of
record." If (b) is "yes, with a CPA we retain," we have a viable formal
escalation path. If (c) is "yes," we restructure as a publisher
administrator, which has bigger implications.

### 4.3 LPOA template language

**Question:** Will you draft an LPOA template that:

- Authorizes K6 Labs to file royalty audit findings and informal Finance
  inquiries with The MLC on behalf of the Member.
- Authorizes K6 Labs to retain a qualified independent CPA to perform a
  statutory audit under 17 U.S.C. § 115(d)(3)(L) when warranted.
- Authorizes K6 Labs to receive correspondence from MLC in response.
- Does NOT authorize K6 Labs to settle, accept payment on behalf of, or
  release claims (we want all of those to flow through the Member's
  Portal-of-record bank account).
- Is revocable by the Member at any time.

### 4.4 Statutory citation in the inquiry email

**Question:** For an informal Finance inquiry (not a full audit notice),
is it appropriate to cite 17 U.S.C. § 115(d)(3)(L) in the email body to
signal that we know an audit is the next escalation step, or is this too
aggressive for a first-touch communication and likely to be received as
litigation-prep?

### 4.5 Tone and content of the packet

**Question:** Review the attached `xr7-evidence-<claim_id>.pdf`. Specifically:

- Is the cover-page SOL urgency framing appropriate for MLC, given that
  the binding deadline analysis is the audit 3-year look-back rather than
  state SOL?
- Is the "Cryptographic Provenance" page useful at the informal-inquiry
  stage or signaling-litigation-prep?
- Do the section names (Royalty Audit Finding, Supporting Evidence, etc.)
  fit MLC's expected vocabulary? MLC uses Work / Share / Claim /
  Conflict / Dispute as terms of art; should we avoid those when not
  strictly applicable to avoid confusion with the ownership-dispute
  process?

### 4.6 Multi-song batching

**Question:** Unlike BMI's "single packet per song" stated preference, MLC
publishes no per-song-vs-batched preference. For our HIGH_RETROACTIVE_PAYMENT_RATIO
or MISSING_DISTRIBUTION findings — which are payer-level patterns
spanning a Member's catalog — is one inquiry covering multiple Songs
(identified by MLC Song Code) acceptable, or should we split? In an audit
context, MLC's policy explicitly contemplates catalog-level review:

> "The MLC may address Conflicts and Disputes over multiple Works or
> Shares together where appropriate, such as at the catalog level."
> — *MLC Dispute Policy §2.3*

…but again, that's the ownership-dispute policy, not the underpayment
context.

### 4.7 Ownership-dispute policy bleed-through

**Question:** If our anomaly detection surfaces a finding that *might* be
explained by an unresolved ownership conflict (Royalties placed in
Suspense for Work/Share in Dispute), our packet would cite an
underpayment but the actual MLC-side cause would be a hold. Should our
packet language anticipate this — e.g. "If this distribution is held in
Suspense pending an ownership conflict, please advise per MLC Dispute
Policy §6" — or does that risk confusing the Finance team?

---

## 5. What we'll do based on attorney response

### If attorney approves third-party informal submission with LPOA:
1. Update `payer_config.py` MLC entry: `submission_email = finance@themlc.com`
   (replacing current `support@themlc.com`), salutation "To the MLC Finance
   Team," add CC to `support@themlc.com` only if attorney recommends.
2. Update `dispute_email.txt`: add Member name + Member number + MLC Song
   Code(s) + ISWC(s) + ISRC(s) as required header fields, replace any
   internal rule_id with plain English, frame the request as an inquiry
   not a demand.
3. Extend `Claim` model to capture MLC Member number + MLC Song Code +
   distribution period + processing type (regular vs reprocessing).
4. **Do NOT add a 9-month-style deadline calculator for MLC.** Track the
   3-calendar-year audit-eligibility horizon instead.
5. Block "File via email" in `/ops` until required fields populated.
6. Send first real test filing for an artist with attorney CC'd.

### If attorney requires a formal audit pathway (no informal-inquiry standing):
1. Build a "audit candidate" status in the Claim model — a finding that
   crosses some materiality threshold and is within the 3-year look-back.
2. Build a workflow that hands off to a qualified CPA (we identify and
   retain) under attorney supervision for actual audit execution.
3. Operator dashboard surfaces audit-candidate claims separately from
   informal inquiries.

### If attorney requires Member-direct submission only:
1. Repurpose the file-via-email flow from "send to MLC" to "send the
   packet to the Member for them to forward from their Portal-of-record
   email." Single mail-to-self send, no LPOA flow needed for the
   communication itself (LPOA still needed for our role generally).
2. Operator dashboard: "Send packet to Member for filing" instead of
   "File via email."

### If attorney recommends K6 Labs become a publisher administrator:
1. Separate workstream — restructure relationship with artists as a
   publishing administration agreement; K6 Labs gets its own MLC Member
   account; we then submit as the Member directly. Significant legal +
   business-model change; out of scope for this brief.

---

## 6. References

### Primary MLC sources
- **MLC Dispute Policy: Musical Work Ownership** (February 2021):
  https://www.themlc.com/hubfs/MLC%20Dispute%20Policy%20Statement%20(Musical%20Works%20Ownership).pdf
- **MLC Policies index**: https://www.themlc.com/policies
- **Member Audits**: https://www.themlc.com/member-audits
- **Audits overview**: https://www.themlc.com/audits
- **Royalty Income Tracking**: https://www.themlc.com/royalty-income-tracking
- **Royalty Distribution**: https://www.themlc.com/royalty-distribution
- **Blanket Royalties**: https://www.themlc.com/blanket-royalties
- **Contact**: https://www.themlc.com/contact
- **Membership**: https://www.themlc.com/membership
- **Specifications, Templates and Guidelines**:
  https://www.themlc.com/specifications-templates-and-guidelines

### MLC Help Center (Zendesk)
- **Help Center home**: https://help.themlc.com/en/support
- **Contact types** (Public/Finance/Legal/Copyright):
  https://help.themlc.com/en/support/contact-types
- **Adding a User**: https://help.themlc.com/en/support/new-member-adding-a-user
- **Statement layouts**:
  https://help.themlc.com/en/support/what-do-the-different-statement-layouts-mean
- **Payment timeline**:
  https://help.themlc.com/en/support/what-is-the-payment-timeline
- **Statement access**:
  https://help.themlc.com/en/support/how-can-i-access-my-statement-in-the-portal

### MLC contact channels
- `finance@themlc.com` — Royalties & Assessment Payments questions
- `support@themlc.com` — General support (currently in our `payer_config.py`)
- `MemberAudits@themlc.com` — Statutory audit notices under § 115(d)(3)(L)
- `data.quality@themlc.com` — Data quality issues
- `notices@themlc.com` — Portal access appeals
- Phone: `(615) 488-3653` Mon-Fri 8am-6pm CT
- Mail: 333 11th Avenue South, Suite 200, Nashville, TN 37203
- Portal contact form: https://portal.themlc.com/contact-us

### Statutory and regulatory citations
- **17 U.S.C. § 115** — Music Modernization Act compulsory blanket license
  - **§ 115(d)(3)(L)** — Member right to audit MLC
  - **§ 115(e)(25)** — "Qualified auditor" definition (independent CPA)
- **37 C.F.R. § 210.27(k)** — DSP-side retroactive adjustments authority
  (cited in MLC docs as basis for reprocessing distributions)
- **U.S. Copyright Office MMA FAQ**:
  https://www.copyright.gov/music-modernization/faq.html
- **U.S. Copyright Office MMA Designations FAQ**:
  https://www.copyright.gov/rulemaking/mma-designations/faq.html

### MLC Governance
- **Operations Advisory Committee** — comprised of six music publisher
  reps + six DSP reps, makes recommendations to the Board on operational
  policy. We did NOT find an OAC-published policy specifically governing
  member-initiated underpayment claims; the committee's published focus
  is on operational efficiency and IT/data deployment.
  Source: https://www.themlc.com/governance

### ArtistOS code (TODO §3 fills this in)
- `XR7/recovery/payer_config.py` — current MLC entry (uses support@themlc.com)
- `XR7/services/templates/dispute_email.txt` — current email body
- `XR7/services/templates/evidence_packet.html` — current PDF template

---

## Appendix A: What we explicitly did NOT find

To prevent the brief from looking thinner than it should, here's an
inventory of policy claims our research surfaced as **plausible-sounding
but not actually published by MLC**:

- **No `disputes@themlc.com` email** — does not appear in any official MLC
  contact listing. (Avoid; an earlier research draft hallucinated this.)
- **No "Designated Member Representative" framework** as a published
  category — User permissions and Contact types exist but are not the
  same thing.
- **No two-year claim window**, **no 90-day SLA**, **no acknowledgment-within-30-days
  commitment** — these were AI hallucinations during research; no MLC
  primary source contains them.
- **No published format spec for member-initiated dispute packets** — the
  DSP-side templates at `/specifications-templates-and-guidelines` are
  not member-side templates.
- **No MLC Operations Advisory Committee policy specifically governing
  member-initiated underpayment claims** as of research date 2026-05-04.
- **No MLC Member Bulletin** addressing dispute-claim windows turned up
  in keyword search; if such bulletins exist, they're behind the Member
  Hub login.
