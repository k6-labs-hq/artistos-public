# ASCAP dispute filing — attorney review brief

**Status:** Draft for Matt's music-rights attorney. Do NOT file disputes against
ASCAP in this format until the questions in §4 are resolved.

**Date drafted:** 2026-05-04
**Authors:** Jason Trent (CTO) + Claude

---

## 1. Why this document exists

ArtistOS automatically detects royalty anomalies (e.g. high-retroactive-payment
ratios, missing distributions) and prepares a dispute packet — a PDF + email body
— intended for the relevant PRO. We have a parallel brief for BMI
(`docs/runbooks/bmi-dispute-attorney-brief.md`); ASCAP's process is materially
different and warrants its own review. Before sending a real dispute on behalf
of a real ASCAP-affiliated artist, we need an attorney to confirm:

- The submission channel + address are correct. ASCAP's published guidance
  routes virtually everything through the **Member Access** portal (Messages),
  not email. Our existing `payer_config.py` placeholder
  (`memberinquiry@ascap.com`) does not appear anywhere in ASCAP's published
  contact materials and likely needs to be replaced.
- The contractual citations we invoke are accurate (Article XIV of the
  Articles of Association; Section 2.8 of the Compendium of Rules and
  Regulations).
- A third-party service (XR7 / K6 Labs) operating under a Limited Power of
  Attorney can be onboarded as a **"Designated User" (DU)** of the member's
  Member Access account, which is ASCAP's published mechanism for trusted
  advisors / business managers to file on a member's behalf.
- The packet content is sufficient and appropriately framed for portal
  submission (text-area Message + attachments) rather than the email-letter
  format we use for BMI.

---

## 2. What ASCAP actually says (verbatim, with sources)

### 2.1 The 9-month claim window — Article XIV, Articles of Association

The binding deadline is in **Article XIV of ASCAP's Articles of Association**,
referenced in the **Compendium of ASCAP Rules and Regulations § 2.8** and in
the **Survey and Distribution System: Rules & Policies** document.

Verbatim language reproduced across multiple ASCAP help pages and the Compendium:

> "Pursuant to Article XIV of the Articles of Association, any claims
> concerning writer-member or publisher-member distributions during any Annual
> Distribution Period must be made within nine (9) months from the end of that
> Annual Distribution Period."

Concrete deadline mapping (also reproduced from ASCAP's published material):

> "For publisher members, the deadline for claims is December 31 of a given
> year (i.e., nine (9) months following the March royalty distribution of the
> same year). For writer members, the deadline is January 31 of a given year
> (i.e., nine (9) months after the April royalty distribution)."

**Compared to BMI:** BMI's 9-month window runs from each individual
distribution date (rolling). **ASCAP's 9-month window runs from the end of the
Annual Distribution Period, not from the individual distribution.** This is a
materially different deadline math: a writer who got an October 2025 ASCAP
distribution still has until **January 31, 2027** (9 months after April 2026,
which is the "end" of the 2025 Annual Distribution Period for writer members)
to file. Our deadline calculator must be PRO-specific.

**Disputed-share holds (separate from claim window).** From ASCAP's published
help center / Section 2.8 summary:

> "If there is a dispute between two or more parties as to entitlement to all
> or part of the credits and/or royalties for a work or membership and ASCAP
> concludes that there is a reasonable basis for the claim, ASCAP may hold
> royalties attributable to the disputed portion of such interests for as long
> as ASCAP deems appropriate."

> "ASCAP may determine that an agreement indemnifying ASCAP against claims by
> either Member, or a suitable bond, can be accepted as a condition to release
> such royalties."

This is ASCAP's inter-member dispute mechanism (e.g. two writers claiming the
same share). It is distinct from a member-vs-ASCAP distribution claim, but
relevant if our finding alleges incorrect share allocation.

### 2.2 Submission channel — Member Access portal, not email

ASCAP does **not** publish a member-facing email address for royalty disputes.
The published help-center language is consistent across multiple FAQ pages:

> "If you have a question about your ASCAP membership, log into your ASCAP
> Member Access account to submit an inquiry, or call ASCAP Global Member
> Services at 1-800-95-ASCAP from 9am-6pm ET, Monday through Friday."

For royalty/statement questions specifically:

> "To ask about your royalty amount, you should submit a Message via your
> Member Access account by choosing the category 'Statement and Payment
> Questions' and selecting the topic that matches your question."

For retroactive-royalty research (the closest published equivalent to our
"underpayment finding"):

> "To request ASCAP research whether retroactive royalties may be owed,
> members should submit a Message through their Member Access account using
> the 'Performance Claims' message category."

For check-replacement (illustrative of the same pattern — everything is a
typed Message):

> "All requests to cancel and replace outstanding checks must be made through
> ASCAP Member Access via Message (Category: 'My Royalties,' Topic: 'Cancel
> and Re-issue Distribution Check')."

For inter-member share/credit disputes (work-record corrections):

> "To submit an inquiry through Member Access, click 'Messages,' and create a
> 'New Message.' Then select the category 'My Catalog' and the topic 'Work
> Record Update.'"

For the formal escalation tier (after a Member Services Message is unsatisfying):
the **Board of Review** under **Article XIV, Section 5(3)** of the Articles of
Association, governed by the Board of Review Rules of Procedure
(`board_of_review_procedure.pdf`). Excerpt:

> "The Complaint shall constitute the Protesting Member's initial submission.
> ... in the case of a Protest brought under Rule 2.1, ASCAP shall file an
> answer thereto within 45 days of the date on which the Protest was filed."

**Implication for our pipeline:** ASCAP's first-line dispute path is a
**portal Message + attachments**, not an email letter. Our entire BMI-style
"send a packet email from Postmark" architecture does not map to ASCAP without
modification. Either:
- (a) We render the packet, the operator (or DU) logs into Member Access and
  pastes the body into a "Statement and Payment Questions" Message and uploads
  the PDF as attachment, or
- (b) We obtain DU credentials for the member and our service files the
  Message programmatically (Member Access does not appear to publish a public
  API — would require browser automation, with all the fragility that implies).

### 2.3 Designated User (DU) — ASCAP's third-party representative model

Verbatim from ASCAP help-center material on Designated Users:

> "A designated user (DU) is someone who has been authorized by an ASCAP
> member to view or manage their Member Access account. It might be a trusted
> advisor, business manager, employee, etc."

> "To authorize a Designated User, click the 'Designated Users' link under the
> Profile menu in Member Access, hit 'Add,' then check off the permissions you
> want to give that user. You can change or delete permissions at any time."

> "You can make them a 'designated user' of your Member Access account, with
> their own username and password, so they can view or manage your Member
> Access account on your behalf using their own credentials, and you don't
> have to provide them with your personal Member Access username and
> password."

> "You should only grant 'designated user' access to people on your team that
> absolutely need it, and you should never share your own login details with
> them."

**This is the central path for our service-bureau model.** ASCAP has an
explicit, documented mechanism for a third party to act on a member's behalf.
A K6 Labs analyst onboarded as the writer's DU would have their own ASCAP
login, see the writer's catalog/statements, and could file a Message in
"Statement and Payment Questions" or "Performance Claims" using their own
credentials with the member's catalog visible.

ASCAP also recognizes the related but different concept of a publisher
**Administrator**:

> "An Admin (short for 'Administrator') is the business agent for another
> ASCAP publisher. Often it is part of the admin or publisher's
> responsibilities to register music with ASCAP on your behalf."

> "Any ASCAP Publisher Member may administer the works of any other ASCAP
> Publisher Member, with an administration agreement signed by an authorized
> representative of the administered Publisher and the administrator
> Publisher."

The Administrator concept is a **publisher-to-publisher** business
relationship; it requires the administrator to itself be an ASCAP publisher
member. The DU concept is broader — any trusted advisor — and is the right
fit for a service bureau that is not a publisher.

### 2.4 Required member-identifying fields

ASCAP does not publish a single "what to include in your dispute" checklist
the way BMI does. Inferring from the work-registration and IPI material:

> "An Interested Party Information (IPI) number is a unique, international
> identification number, usually 9–11 digits long, and IPIs are assigned to
> songwriters, composers and music publishers. Most of the world's performing
> rights organizations (including ASCAP) use IPI numbers to link you to your
> musical works."

> "ASCAP's database shows their own Work ID, which Societies use for their own
> internal matching and reporting purposes, but often also include it in their
> onwards reporting to writers and publishers."

In practice, a portal-submitted Message ties to the logged-in member, so the
"member number" question solves itself once you're in the right account. The
fields that matter on the work side:
- ASCAP **Work ID** (visible in the member's catalog in Member Access)
- **IPI** (writer/publisher identifier)
- **ISWC** (where assigned)
- **Title**
- **Distribution period and distribution date** being disputed
- **Performance source** (radio / TV / streaming / international)

**TODO (verify with attorney / a real DU walkthrough):** confirm exact field
labels in the "Statement and Payment Questions" and "Performance Claims"
Message forms.

### 2.5 How responses are returned

Responses arrive as replies inside the **Member Access Messages** thread, not
as outbound email. Members typically also get an email **notification** that a
new Message is available, but the substantive content lives in the portal.
This is materially different from BMI, where replies come back to the email
address that filed. Our inbound webhook (Postmark inbound) won't receive ASCAP
replies — we'd need to either (a) have the DU forward them or (b) scrape them
from Member Access.

**TODO (verify):** does ASCAP's email notification include the response body,
or is it a "you have a new message, log in to read" stub? If the former, our
existing inbound-correlation pipeline could still capture it.

### 2.6 Member portal dispute tooling

There is no dedicated "self-service dispute submission tool" in Member Access
in the sense BMI doesn't have one either. The path is the generic Messages
interface with the right Category/Topic. ASCAP's help-center FAQ effectively
treats "submit a Message in the right category" as the dispute submission
tool.

---

## 3. What we currently have, and what's wrong with it

### 3.1 Submission email
- **What we have:** `memberinquiry@ascap.com` (placeholder in
  `XR7/recovery/payer_config.py`, by analogy with the BMI placeholder).
- **Problem:** This address does not appear anywhere in ASCAP's published
  contact materials. ASCAP's published guidance is unambiguous: dispute
  inquiries go through the **Member Access** portal (Messages) or by phone to
  1-800-95-ASCAP. A bouncing send hurts our Postmark sender reputation; a
  delivered-but-ignored send (if the address silently exists internally)
  delays the claim while the 9-month window runs.
- **Fix (pending attorney sign-off):** TODO — replace the email-based ASCAP
  flow with a portal-based flow. Either render-and-handoff (operator pastes
  into Member Access) or DU-based programmatic submission. See §4.1 + §4.2.

### 3.2 Channel architecture mismatch
- **What we have:** Email-out via Postmark, inbound via Postmark webhook —
  works for BMI's regional offices.
- **Problem:** ASCAP doesn't publish an email channel for disputes. Our entire
  send/correlate pipeline assumes an email-shaped conversation. For ASCAP,
  the "outbound message" is a portal Message and the "inbound reply" is a
  portal Message reply (with email notification only).
- **Fix (pending attorney sign-off):** TODO — model ASCAP filings as a
  separate `submission_method = portal_handoff` (or `portal_du`) in
  `payer_config.py` and adjust the operator dashboard accordingly. The "File
  via email" button should not appear for ASCAP claims; instead a "Generate
  packet for portal submission" action that produces the Message body + PDF
  attachment for the DU to paste in.

### 3.3 Salutation
- **What we have:** "To the [Payer] Member Disputes Team," (BMI-shaped).
- **Problem:** ASCAP Messages don't really have a salutation — they have a
  Category and a Topic. The body is plain prose to whichever Member Services
  rep picks up the queue.
- **Fix (pending attorney sign-off):** TODO — ASCAP body template starts with
  the substance, not a salutation. If a salutation is desired, "To ASCAP
  Member Services," is generic and accurate.

### 3.4 Deadline calculator
- **What we have:** Generic 9-month rolling window (BMI-shaped) or SOL.
- **Problem:** ASCAP's 9-month window runs from the **end of the Annual
  Distribution Period**, not from the individual distribution date. Using
  BMI's per-distribution math against ASCAP rows will produce wrong
  deadlines (typically too aggressive — we'd flag claims as expiring earlier
  than they actually are).
- **Fix (pending attorney sign-off):** TODO — payer-aware deadline calculator.
  For ASCAP writer members: deadline = January 31 of (year of distribution
  + 1). For ASCAP publisher members: deadline = December 31 of (year of
  distribution). Also branch by member type.

### 3.5 Contractual citation — currently absent for ASCAP
- **What we have:** No reference to ASCAP governing documents.
- **Problem:** Citing the binding rule signals timeliness and contractual
  basis. For ASCAP that means **Article XIV of the Articles of Association**
  and **Section 2.8 of the Compendium of ASCAP Rules and Regulations**.
- **Fix (pending attorney sign-off):** TODO — add to ASCAP packet:
  "Pursuant to Article XIV of the ASCAP Articles of Association and
  Section 2.8 of the Compendium of ASCAP Rules and Regulations, this
  constitutes timely written notice of a claim concerning the [PERIOD]
  Annual Distribution Period within nine (9) months of the end of that
  period."

### 3.6 Required member-identifying fields
- **What we have:** Artist name + claim ID; optionally `artist_pro_id` (not
  populated today).
- **Problem:** For ASCAP packets we want to capture: **ASCAP IPI, ASCAP Work
  ID, ISWC, ASCAP member status (writer vs publisher member — controls
  deadline math), distribution period, performance source.**
- **Fix (pending attorney sign-off):** TODO — extend the Artist + Claim model
  with ASCAP-specific fields and the `member_type` enum. Block "Generate
  packet" for ASCAP claims if any required field is missing.

### 3.7 LPOA framing → DU onboarding
- **What we have:** "A signed Limited Power of Attorney is available on
  request" (BMI-shaped).
- **Problem:** For ASCAP this is the wrong instrument. ASCAP has a published
  **Designated User** mechanism that is the correct way to authorize a
  service bureau. An LPOA on top is fine and may be useful for our internal
  records, but it is not what ASCAP looks for — they look for the DU
  authorization completed inside Member Access by the member.
- **Fix (pending attorney sign-off):** TODO — onboarding flow for ASCAP
  artists: (1) writer signs LPOA with us, (2) writer logs into ASCAP Member
  Access and adds K6 Labs (named individual on our side) as a Designated
  User with appropriate permissions, (3) we log in with our own DU
  credentials and proceed.

### 3.8 Inbound reply correlation
- **What we have:** Postmark inbound webhook with Basic Auth (#220).
- **Problem:** ASCAP responses come back through Member Access Messages, not
  email. Our correlation pipeline won't see them.
- **Fix (pending attorney sign-off):** TODO — for ASCAP claims, the operator
  (DU) checks Member Access on a cadence and either forwards relevant
  threads to our inbound address or pastes the response into the operator
  dashboard manually.

---

## 4. Open questions for attorney review

### 4.1 Designated User vs. LPOA — what's the right legal frame?
**Question:** ASCAP's published mechanism for third-party representation is
the Designated User. From a contractual-authority standpoint, is being
appointed as a DU sufficient authority for K6 Labs to file a royalty claim
on a writer's behalf, or do we still want a separate LPOA on top? If both,
what should the LPOA carve out vs. cover?

**Why it matters:** This is the equivalent of the §4.1 question in the BMI
brief, but ASCAP-specific. ASCAP appears to have answered "yes, third
parties can act on a member's behalf" by publishing the DU mechanism — but
we want the attorney's read on whether DU status alone is enough or whether
we also want an internal LPOA as a belt-and-suspenders for our records and
for any later dispute about what the writer authorized us to do.

### 4.2 LPOA scope for ASCAP-specific actions
**Question:** Will you draft an ASCAP-specific LPOA template (or amend the
BMI one) that:
- Authorizes K6 Labs to be onboarded as a Designated User on the writer's
  Member Access account
- Authorizes K6 Labs to file Messages in any of: Statement and Payment
  Questions, Performance Claims, My Catalog, My Royalties categories
- Does NOT authorize K6 Labs to change banking/payment details, change
  primary contact info, change DU permissions for other parties, or initiate
  a Board of Review Protest (those should require explicit additional
  writer sign-off)
- Is revocable, both contractually and via the writer revoking DU
  permissions in Member Access

### 4.3 Contractual citation accuracy
**Question:** Is citing **Article XIV of the Articles of Association** and
**Section 2.8 of the Compendium** appropriate language to include in an ASCAP
Member Access Message body, or does it come across as adversarial in a
context where Member Services reps expect plain prose?

### 4.4 Member-type ambiguity (writer vs publisher)
**Question:** A given ASCAP affiliation is either as a writer member or as a
publisher member, with different distribution periods and different
contractual terms. If our anomaly spans a single writer who is also a
self-published publisher (very common), do we file two separate
claims/Messages — one as the writer member, one as the publisher member —
or a single combined Message? ASCAP's rules treat them as separate streams
with separate deadlines.

### 4.5 Annual Distribution Period mapping
**Question:** Confirm that for a writer member, the "Annual Distribution
Period" ending in April YYYY covers performances surveyed during the year
preceding that distribution (rolling, with the survey-period offsets), and
that the 9-month claim window therefore captures any specific quarterly
distribution paid within that period. We want to be confident our deadline
calculator (deadline = Jan 31 of YYYY+1 for writer members) is correct.

### 4.6 Portal vs. paper / email fallback
**Question:** If a writer doesn't want K6 Labs to be a DU (e.g. trust
concerns), is there any paper or email fallback that ASCAP will accept for
a member-filed claim, or is it strictly Member Access + phone? The
help-center language reads as "portal or phone, full stop." Do you have
practical experience filing a substantive ASCAP claim by physical mail to
an ASCAP office that we should know about?

### 4.7 Board of Review escalation
**Question:** If a Member Services Message goes nowhere or is denied, the
formal next step is a Protest before the **Board of Review** under
**Article XIV, Section 5(3)** of the Articles of Association. That is a
quasi-litigation forum (45-day ASCAP answer, written submissions, hearings).
Should we even mention Board of Review escalation in our initial
Message — as a marker of seriousness — or does that poison the well at the
Member Services tier?

---

## 5. What we'll do based on attorney response

### If attorney approves DU-based third-party submission:
1. Update `payer_config.py` ASCAP entry: replace the email field with a
   `submission_method = portal_handoff` (or `portal_du`) flag, and a
   `member_access_url` pointer.
2. Add an ASCAP-specific dispute Message body template to
   `XR7/services/templates/` — written for portal paste, with the Article
   XIV / Section 2.8 citation, plain-English finding summary, and explicit
   reference to "Statement and Payment Questions" or "Performance Claims"
   category.
3. Extend the `Claim` and `Artist` models with: `ascap_ipi`,
   `ascap_work_id`, `iswc`, `ascap_member_type` (writer | publisher),
   `distribution_period`.
4. Add a payer-specific deadline calculator: for ASCAP writer members,
   deadline = Jan 31 of (year of Annual Distribution Period end + 1); for
   publisher members, Dec 31 of (year of period end). Supersedes SOL.
5. Adjust the operator dashboard: for ASCAP claims, replace "File via
   email" with "Generate packet for portal submission" → produces (a) the
   Message body text the DU can paste and (b) the PDF attachment.
6. DU onboarding runbook for new ASCAP-affiliated artists: writer signs LPOA
   with us; writer adds K6 Labs (named individual) as DU on Member Access;
   we verify DU access; first real test filing with attorney CC'd on the
   internal record.

### If attorney requires writer-direct ASCAP submission:
1. ASCAP claims become "render and email the writer the packet text + PDF;
   the writer pastes into their own Member Access Messages."
2. Operator dashboard "File via" action for ASCAP rows becomes "Send
   packet to writer for self-filing."
3. Inbound correlation: writer either forwards Member Access response
   notifications to us, or pastes the response back into the operator
   dashboard manually.

### If attorney requires publisher-Administrator route instead of DU:
1. Onboarding gets heavier: K6 Labs would have to itself become an ASCAP
   publisher member and accept a publisher-administration agreement with
   each artist's writer-publisher entity. Almost certainly out of scope for
   the closed-beta phase.

---

## 6. References

### ASCAP governing documents (primary)
- **Compendium of ASCAP Rules and Regulations** (effective Sept 19, 2025) —
  Section 2.8 (claims policy):
  https://www.ascap.com/~/media/files/pdf/members/governing-documents/ascap-compendium---current.pdf
- **Articles of Association** — Article XIV (claim window, Board of Review):
  https://www.ascap.com/~/media/files/pdf/members/governing-documents/articles-of-association.pdf
- **Survey and Distribution System: Rules & Policies** (Oct 2022) — restates
  the Article XIV 9-month rule:
  https://www.ascap.com/~/media/files/pdf/members/governing-documents/ascap-survey--distribution-rules--10322.pdf
- **Board of Review Rules of Procedure** — escalation forum under
  Article XIV § 5(3):
  https://www.ascap.com/~/media/files/pdf/members/governing-documents/board_of_review_procedure.pdf
- ASCAP Governing Documents index:
  https://www.ascap.com/about-us/governingDocuments

### ASCAP help-center / contact (operational)
- Royalties and Payment FAQ (Section 2.8 reference; Message categories):
  https://www.ascap.com/help/royalties-and-payment
- My ASCAP Membership FAQ (Designated User definition + setup):
  https://www.ascap.com/help/my-ascap-membership
- IPI FAQ:
  https://www.ascap.com/help/registering-your-music/ipi-faqs
- ISWC FAQ:
  https://www.ascap.com/help/registering-your-music/iswc-number-work-codes-faq
- Member Access portal:
  https://www.ascap.com/member-access
- Contact Us:
  https://www.ascap.com/contact-us
- Global Member Services phone: 1-800-95-ASCAP (1-800-952-7227),
  Mon–Fri 9am–6pm ET.

### ArtistOS code (TODO — fill in once attorney response is in)
- `XR7/recovery/payer_config.py` — current per-payer config; no ASCAP-
  specific submission method yet. **TODO:** add `portal_handoff` mode.
- `XR7/services/templates/dispute_email.txt` — current email body; BMI-shaped.
  **TODO:** add ASCAP portal-Message template.
- `XR7/services/templates/evidence_packet.html` — current PDF template;
  reusable as the Message attachment for ASCAP.
- Deadline calculator — currently SOL or BMI 9-month. **TODO:** add ASCAP
  Annual-Distribution-Period 9-month math, branched on writer-vs-publisher
  member type.

---

**Diff vs. BMI brief (for the attorney's quick orientation):**
- **Deadline:** ASCAP 9 months from end of Annual Distribution Period (not
  per-distribution rolling like BMI).
- **Channel:** ASCAP is portal-only (Member Access Messages); BMI is email
  to a regional office.
- **Third-party:** ASCAP has a published Designated User mechanism; BMI's
  position on third-party submitters is the central open question of the
  BMI brief.
- **Citation:** ASCAP → Article XIV of Articles of Association + Compendium
  § 2.8; BMI → paragraph 6(b)(iv) of the Writer Agreement.
- **Escalation:** ASCAP has a formal Board of Review under Article XIV § 5(3)
  with published Rules of Procedure; BMI's equivalent is less formalized.
