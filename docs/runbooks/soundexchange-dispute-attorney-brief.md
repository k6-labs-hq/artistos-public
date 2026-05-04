# SoundExchange dispute filing — attorney review brief

**Status:** Draft for Matt's music-rights attorney. Do NOT file disputes against
SoundExchange in this format until the questions in §4 are resolved.

**Date drafted:** 2026-05-04
**Authors:** Jason Trent (CTO) + Claude

---

## 1. Why this document exists

ArtistOS automatically detects royalty anomalies in member statements
(underpayment patterns, missing distributions, ISRC-match failures) and
prepares a dispute packet — a PDF + email body — intended for SoundExchange's
member resolutions team. Before we send a real dispute on behalf of a real
artist, we need an attorney to confirm:

- The submission channel + address are correct.
- The statutory and contractual citations we invoke are accurate.
- A third-party service (XR7 / K6 Labs) operating under a Limited Power of
  Attorney is an acceptable submitter under the SoundExchange member /
  registrant framework.
- The packet content is sufficient and appropriately framed.

**SoundExchange is structurally different from BMI/ASCAP/MLC.** It is a
*statutory* collective designated under 17 U.S.C. §§ 112 and 114, paying
**master-recording (sound recording) digital-performance royalties** to three
distinct payee classes:

1. **Sound Recording Copyright Owner (SRCO)** — 50% (§ 114(g)(2)(A))
2. **Featured artist** — 45% (§ 114(g)(2)(D))
3. **Non-featured musicians and vocalists** — 2.5% each, paid through the
   AFM & SAG-AFTRA Intellectual Property Rights Distribution Fund, NOT through
   SoundExchange directly (§ 114(g)(2)(B)–(C))

Our service-bureau model targets payee classes (1) and (2). We do **not** file
on behalf of non-featured performers — those go through the AFM & SAG-AFTRA
Fund. This needs to be encoded in our `payer_config` and rule eligibility
filters.

Sample rendered packet attached separately as `xr7-evidence-<claim_id>.pdf`.

---

## 2. What SoundExchange actually says (verbatim, with sources)

### 2.1 The 3-year unclaimed-royalty window — regulatory, not contractual

Unlike BMI's 9-month contractual window, SoundExchange's deadline pressure is
**regulatory**, codified in 37 CFR Parts 380, 382, and 384. From the
SoundExchange FAQ ("Do unclaimed royalties expire?"):

> "Yes, after 3 years royalties expire and SoundExchange is authorized by
> regulation to release unclaimed royalties."
> — `soundexchange.com/faq/do-unclaimed-royalties-expire/`

From 37 CFR § 380.4 (paraphrased by Cornell LII summary, verified):

> "the Collective must retain the required payment in a segregated trust
> account for a period of three years from the date of the first distribution
> of royalties. ... No claim to distribution shall be valid after the
> expiration of the three-year period."

**Implication:** the 3-year clock runs from the **first distribution date** of
the relevant licensee payment (not from when the artist registered, not from
when they noticed the underpayment). After 3 years, SoundExchange "may apply
the unclaimed funds to offset any costs deductible under 17 U.S.C. 114(g)(3)."

This is **longer** than BMI's 9-month window, but it has a different character:
- BMI: contractual, between the writer and BMI, claim-to-adjust.
- SoundExchange: regulatory, governs unclaimed-royalty redistribution, not
  the time to dispute a *received* statement.

**Open attorney question (§ 4.1 below):** What is the deadline to dispute a
SoundExchange distribution that was *received but allegedly miscalculated*?
The 3-year unclaimed-royalty rule does not directly answer this. We have not
located a published claim-window provision in the public SoundExchange member
agreement equivalent to BMI's 9-month rule. The full Membership Agreement is
not publicly hosted on soundexchange.com (only summary descriptions); attorney
should obtain the operative Featured Artist Membership Agreement and SRCO
Webcaster Agreement from SoundExchange directly.

### 2.2 What SoundExchange's published "dispute" process actually covers

**Critical:** the public-facing "dispute" process at SoundExchange is **not**
the same kind of process as BMI's. SoundExchange's published "Artist Disputes"
and "Overlaps & Disputes" workflow handles **competing-claim disputes**
(claimants whose stated shares for one recording sum to more than 100%), not
underpayment-by-licensee disputes.

From `soundexchange.com/2024/03/20/artist-disputes-what-are-they-how-are-they-resolved/`:

> "An Artist Dispute is a scenario when the total share (percentage) of
> featured artist royalties for a given recording is claimed by two or more
> claimants and exceeds 100%."

> "Log into your SoundExchange Direct account and submit an artist/featured
> performer claim for your share."

> "Once all claimants have agreed on performer shares, please contact
> [info@soundexchange.com], and we will update our records and process any
> royalty adjustments as necessary."

> "We will not decide or determine the rightful featured performer(s), sound
> recording copyright owner ... when disputes arise."

> "Holds are only removed when the dispute has been resolved."

From `soundexchange.com/2019/11/06/understanding-my-catalog-a-guide-to-overlaps-disputes/`:

> "Overlaps occur when multiple SRCOs claim shares of a sound recording that
> exceed 100% for the same collection period."

> "SoundExchange does not participate in the resolution process for disputed
> sound recordings."

> "SoundExchange will provide each SRCO involved in the dispute with email
> addresses of the other involved SRCOs."

Deadlines published for **competing-claim disputes**:

> "Initial response window: 90 days from the send date of the recording's
> original 'confirmation notice'"

> "New claimant response period: 30 days from the send date of the recording's
> original Reconfirmation Notice"

**These deadlines apply to inter-claimant disputes — they are NOT a published
SLA for SoundExchange's response to a member's underpayment-or-miscalculation
inquiry.** We cannot invoke them as SoundExchange's commitment.

### 2.3 What SoundExchange does NOT publish

We searched soundexchange.com, the FAQ, the LOD documents, and the public
membership-agreement summaries. We did **not** find:

- A claim-window provision analogous to BMI's 9-month rule for disputing a
  received-but-miscalculated distribution.
- A published email like `claims@soundexchange.com` (zero search results).
- A published "Royalty Inquiry" form distinct from the generic SXDirect
  "Contact Us" function.
- A published response SLA for member inquiries.
- A published policy on whether a third-party service-bureau (operating under
  an LPOA) may submit a royalty-discrepancy inquiry on behalf of a member.

These are gaps the attorney needs to resolve via direct contact with
SoundExchange's Client Resolutions team.

### 2.4 Submission channels — verbatim

From multiple SoundExchange pages:

> "If you have questions or would like more information about any of these
> updates, please contact our Customer Services team via 'Contact Us' in
> SXDirect or at 1-800-961-2091."
> — `soundexchange.com/2021/07/08/soundexchange-direct-update-membership-summary/`

> "you can contact Customer Services at 1-800-961-2091 (U.S. only),
> 202-803-8231 (outside of U.S.), or via 'Contact Us' in SXDirect."

> "To reach SoundExchange directly, use the Contact section of SXDirect or
> call our Support team at 800-961-2091."
> — `soundexchange.com/2019/11/06/understanding-my-catalog-a-guide-to-overlaps-disputes/`

Published email addresses (from public sources, including SoundExchange's
"Artist Disputes" article and contact aggregator pages):

| Address                              | Purpose (per SoundExchange)                           |
|--------------------------------------|-------------------------------------------------------|
| `info@soundexchange.com`             | General inquiries; resolution of agreed-share disputes |
| `accounts@soundexchange.com`         | Account-related                                       |
| `licenseerelations@soundexchange.com`| Licensee (payer) relations — **not** member relations |
| `repertoire@soundexchange.com`       | Repertoire / metadata corrections                     |
| `privacy@soundexchange.com`          | Privacy / data subject requests                       |
| `communications@soundexchange.com`   | Media / PR                                            |

**`support@soundexchange.com` is NOT documented as a published address on
soundexchange.com.** Our `payer_config.py` currently uses
`support@soundexchange.com`; that is unverified and likely wrong.

**`claims@soundexchange.com` returned ZERO public search results.** We could
not verify this address exists.

The verified primary channels for member royalty inquiries are:
1. The **"Contact Us"** form inside SXDirect (the authenticated member portal).
2. Phone: **800-961-2091** (US) / **202-803-8231** (international).
3. `info@soundexchange.com` for general inquiries.

There is also an internal **"Client Resolutions"** team at SoundExchange (Scott
Berenson is publicly listed as Director, Client Resolutions; Jameila Anderson
as Senior Specialist, Sound Recording Owner Resolutions, per public LinkedIn /
ZoomInfo). This team appears to be the right substantive contact, but their
emails are not publicly published — escalation requires going through
`info@soundexchange.com` or SXDirect first.

### 2.5 ISRC is THE key identifier

From `soundexchange.com/2024/01/09/all-about-isrcs/`:

> "recordings are required to have associated ISRCs by virtually all download
> and streaming services, as well as collecting societies, including
> SoundExchange."

> "It's important to submit your ISRCs to SoundExchange *before* the recordings
> are released or soon after so we have the good ISRC and metadata in our
> system to match with usage from the streaming services who report to us."

From `soundexchange.com/service-provider/reporting-requirements/`: licensees
submitting Reports of Use must provide "the International Standard Recording
Code ('ISRC'), or (if the ISRC is unavailable) the combination of both track
title and featured artist name."

**Implication for our packet:** ISRC is the canonical join key on
SoundExchange's side. Every disputed line in our packet must surface ISRC.
Where ISRC is missing, the fallback is `(track_title, featured_artist_name)` —
the same fallback SoundExchange's matching service uses.

### 2.6 Letter of Direction — does NOT authorize dispute filing

This is the key finding for the service-bureau model. From the LOD landing
page (`soundexchange.com/what-we-do/for-artists-labels-and-producers/letters-of-direction/`):

> "A SoundExchange Featured Artist Letter of Direction (LOD) is a document by
> which a Featured Artist directs SoundExchange to pay a portion of the
> Featured Artist's sound recording performance royalties to a participant
> involved in the creative process — producers, engineers, mixers, re-mixers,
> etc."

> "LODs cannot be used to direct payments to other third parties, including
> record labels, lenders, royalty advance companies, or any person or entity
> not directly involved in the creative process."

From `soundexchange.com/2025/09/30/letters-of-direction-signature-requirements/`:

> "SoundExchange does not recognize persons with power of attorney for a
> performer to be able to sign LODs unless they are also the primary contact
> on file for that performer."

**Implication:** The LOD instrument is **not** the right authorization vehicle
for K6 Labs / XR7 to dispute on a member's behalf. LOD is purely for
royalty-payment redirection to creative collaborators; it cannot authorize a
service-bureau to submit inquiries.

The relevant authorization vehicles are instead:

**(a) Account Authorization Form / Primary Contact** — from
`soundexchange.com/2020/11/24/primary-guest-access-in-soundexchange-direct-everything-you-need-to-know/`:

> "The primary contact 'manages, maintains, and administers the account on an
> everyday basis' and 'receives all statements and email communications from
> SoundExchange.'"

The primary contact "does not have to be the artist or rights owner the
account is registered to — it could be a financial advisor, business manager,
or anyone the registrant deems fit for the role."

**(b) Guest Access in SXDirect** — same source:

> "Up to 50 guest users may be added to an account."

> "View with Repertoire" guests get "the ability to see all recordings
> associated with an account and to submit claims on behalf of an account."

**Critical:** SoundExchange has built a **first-party** mechanism (Guest Access
with View+Repertoire permission, or designation as Primary Contact) that
authorizes a non-artist representative to act on the artist's account. This
is the official authorization path. An LPOA filed *outside* this system is
unlikely to be honored.

### 2.7 Third-party payment policy — explicitly prohibited

From the SoundExchange FAQ:

> "It is our strict policy that we cannot pay third parties. A third party is
> considered anyone that is not the featured performer (artist) or the owner
> of the Sound Recording Copyright."

**Implication:** K6 Labs / XR7 cannot be the payee. Any settlement or recovery
flows back to the artist's SoundExchange account directly. This is consistent
with our model (we don't want to be the payee), but the attorney needs to
confirm this prohibition does not extend to *correspondence-on-behalf-of* (i.e.
filing an inquiry).

### 2.8 SoundExchange does NOT mediate substantive disputes

From the Hypebot summary of SoundExchange's process:

> "we don't take sides. We simply put all royalties related to the recording...
> on hold"

> "SoundExchange will not interpret third-party agreements/contracts and will
> only take the direction of a track's direct registrants"

**Implication:** A dispute submitted *outside* the registered account (i.e.
via email from K6 Labs without a registered Primary Contact / Guest Access
relationship) is likely to be ignored or bounced back with a request that the
artist contact them directly through SXDirect. This drives the architecture
in §3.

---

## 3. What we currently have, and what's wrong with it

### 3.1 Submission email
- **What we have:** TODO — verify current value in `XR7/recovery/payer_config.py`.
  User stated `support@soundexchange.com` is current; that is not a documented
  address.
- **Problem:** `support@soundexchange.com` is not a published SoundExchange
  contact. `claims@soundexchange.com` is not published either. A real send
  could bounce, harming Postmark sender reputation.
- **Fix (pending attorney sign-off):** Default to the SXDirect "Contact Us"
  form (which requires authentication — see §3.X below) OR
  `info@soundexchange.com` for an initial inquiry. This is a structural
  change: SoundExchange's intended channel is the authenticated portal, not
  email.

### 3.2 Channel architecture
- **What we have:** TODO — current architecture assumes outbound email is the
  primary submission method (consistent with BMI).
- **Problem:** SoundExchange's documented intended channel is the
  authenticated SXDirect "Contact Us" form, accessed by the artist or by
  authorized Guest Access / Primary Contact. Outbound email from K6 Labs is
  not the documented path.
- **Fix (pending attorney sign-off):** Two-mode operation:
  - **Mode A (preferred): K6 Labs is provisioned as a SXDirect Guest with
    "View with Repertoire" permission OR as Primary Contact**, and we submit
    via the in-portal Contact Us form. Requires the artist to add us through
    Settings → Registrant Details → Guest List in their SXDirect.
  - **Mode B (fallback): Generate the packet, send to the artist for them to
    forward** (via email or paste into SXDirect Contact Us). Same model as
    BMI fallback in their brief §5.

### 3.3 Salutation
- **What we have:** TODO — verify current `dispute_email.txt` salutation.
- **Problem:** SoundExchange's substantive team is "Client Resolutions" (for
  artists) or "Sound Recording Owner Resolutions" (for SRCOs). There is no
  generic "Member Disputes Team."
- **Fix (pending attorney sign-off):**
  - For artist filings: "To the SoundExchange Client Resolutions Team,"
  - For SRCO filings: "To the SoundExchange Sound Recording Owner
    Resolutions Team,"

### 3.4 SLA framing
- **What we have:** TODO — verify current `dispute_email.txt` SLA language.
- **Problem:** SoundExchange does NOT publish a member-relations response SLA.
  The published 90-day / 30-day windows in the Overlaps & Disputes workflow
  apply to *inter-claimant* disputes, not member-vs-SoundExchange
  underpayment inquiries. Asserting either is a SoundExchange commitment is
  factually wrong.
- **Fix (pending attorney sign-off):** Reframe as our internal escalation
  timer, not their commitment.

### 3.5 Statutory / regulatory citation — currently absent
- **What we have:** TODO — `dispute_email.txt` likely has no SoundExchange-
  specific statutory citation.
- **Problem:** SoundExchange operates under 17 U.S.C. §§ 112 and 114 with
  distribution rules in 37 CFR Parts 380/382/384. A SoundExchange-targeted
  packet should cite the relevant CFR section for the licensee class
  (e.g. webcaster vs. preexisting subscription service vs. business
  establishment) and reference the 3-year retention rule where the underlying
  payments are approaching that horizon.
- **Fix (pending attorney sign-off):** Add a per-licensee-class citation
  block. Attorney to draft the boilerplate.

### 3.6 Required member-identifying fields — currently absent
- **What we have:** TODO — current `Claim` / `Artist` model fields.
- **Problem:** SoundExchange's required fields are different from BMI's:
  - **SoundExchange Account # / Registrant ID** (line 1 of any inquiry)
  - **Payee class** — Featured Artist, SRCO, or both (artist who also owns
    masters)
  - **ISRC** — the canonical recording identifier
  - Recording title + featured artist name (fallback when ISRC missing)
  - Distribution date being disputed (which quarterly distribution)
  - **Service type** — subscription, non-subscription / webcaster, business
    establishment, preexisting satellite, AHRA — because the licensee class
    drives both the rate proceeding and the CFR Part the dispute is cited
    under
  - **Licensee name** if known (e.g. "SiriusXM SDARS-3 distribution",
    "Pandora ad-supported")
- **Fix (pending attorney sign-off):** Extend `Claim` + `Artist` models.
  Block "File via email" in the operator dashboard until required fields are
  populated. Different required-field set per payee class.

### 3.7 Internal taxonomy bleeding through
- **What we have:** TODO — same `rule_id` strings as the BMI flow.
- **Problem:** Same as BMI brief §3.6. Internal rule_id labels are not useful
  to a SoundExchange Client Resolutions investigator.
- **Fix:** Same as BMI brief — lead with plain-English `description` and keep
  `rule_id` as an internal reference only.

### 3.8 Authorization framing
- **What we have:** TODO — current packet references an LPOA (Limited Power
  of Attorney).
- **Problem:** As established in §2.6, LPOA is **not** a SoundExchange-
  recognized instrument (per the LOD-signature-requirements page). The
  SoundExchange-native authorization mechanisms are Primary Contact + Guest
  Access in SXDirect. An LPOA referenced in our packet, without
  corresponding Guest/Primary Contact provisioning in SXDirect, is unlikely
  to be honored.
- **Fix (pending attorney sign-off):** During artist onboarding, require the
  artist to add K6 Labs as either Primary Contact or "View with Repertoire"
  Guest in SXDirect. The packet should reference *that* provisioning ("Filer
  is registered as authorized Guest on SXDirect account #XXXXX"), not an
  LPOA. The LPOA may still be useful for our internal audit trail and for
  states-side legal authorization, but should not be cited to SoundExchange
  as the basis for our authority.

### 3.9 Payee-class branching
- **What we have:** TODO — current model treats all SoundExchange anomalies
  uniformly.
- **Problem:** Three payee classes have different processes:
  - **Featured artist** → SoundExchange Client Resolutions
  - **SRCO** → SoundExchange Sound Recording Owner Resolutions
  - **Non-featured musician/vocalist** → AFM & SAG-AFTRA Fund (NOT
    SoundExchange) — we should refuse to file these
- **Fix (pending attorney sign-off):** Branch on payee class at rule
  evaluation. Different salutation, different team, different boilerplate.
  Add explicit "this rule is not eligible for artist X because their payee
  class is non-featured" guard.

### 3.10 Cryptographic Provenance section
- **Same concern as BMI brief §3.8.** Probably overkill for an initial member-
  resolutions inquiry. Question for attorney in §4.

---

## 4. Open questions for attorney review

### 4.1 What is the actual claim window for a received-but-miscalculated SoundExchange distribution?
**Question:** The 3-year unclaimed-royalty rule (37 CFR § 380.4 et seq.)
governs *unclaimed* royalties. It does not, on its face, govern the time to
dispute a *received* distribution that the member claims was miscalculated.
Is there:
(a) A claim-window provision in the operative SoundExchange Featured Artist
    Membership Agreement or SRCO Webcaster Agreement we should invoke?
(b) A general state-law SOL applicable (DC contract law, given SoundExchange's
    DC headquarters)?
(c) An effective practical window driven by the 3-year retention rule
    (i.e., once the source distribution is past 3 years, the underlying
    licensee payment may have been swept to administrative offset, making
    recovery practically impossible)?

**Why it matters:** Our deadline calculator needs a payer-specific rule. For
BMI it's 9 months. For SoundExchange we currently have no defensible answer.

### 4.2 Authorization mechanism for service-bureau filings
**Question:** Of the SoundExchange-recognized authorization mechanisms
(Primary Contact, "View with Repertoire" Guest in SXDirect), which is
appropriate for a service bureau like K6 Labs that:
- Drafts and submits royalty-discrepancy inquiries
- Receives correspondence in response
- Does NOT take payment on the artist's behalf
- Does NOT settle or release claims
- Is revocable by the artist at any time

**Why it matters:** This is the SoundExchange equivalent of the BMI brief's
§4.1 question. If the answer is "neither Primary Contact nor Guest is
appropriate for a service bureau," our model collapses to draft-and-forward
(BMI-style fallback in BMI brief §5).

### 4.3 LPOA as supplementary instrument
**Question:** Even if Guest/Primary Contact is the operative SoundExchange-
recognized mechanism, should we also have a notarized LPOA on file (for our
own records, for state-law authorization, and for situations where
SoundExchange asks for proof of authority beyond the SXDirect Guest entry)?
What language should the LPOA contain?

### 4.4 Initial submission channel
**Question:** Given that SoundExchange directs all member inquiries to the
authenticated SXDirect Contact Us form (or phone), is it acceptable to email
`info@soundexchange.com` with a packet, or will that be redirected /
deprioritized? Should we instead use SXDirect Contact Us as the artist's
authorized Guest, and only fall back to email if the portal channel does not
acknowledge within a defined window?

### 4.5 Packet content and tone
**Question:** Same as BMI brief §4.4. Specifically for SoundExchange:
- Is statutory/CFR citation appropriate at the initial inquiry stage, or
  too aggressive?
- Is the Cryptographic Provenance page useful or signaling-litigation-prep?
- Should the packet differentiate by licensee class (SiriusXM-specific vs.
  Pandora-specific vs. business establishment) — those go through different
  CFR sections and different audit cycles?

### 4.6 Featured artist vs. SRCO filing differences
**Question:** Confirm which payee class our pilot artists fall into. Most
indie/Nashville artists we've onboarded are *both* featured artist and SRCO
(they own their own masters). Do we file a single packet covering both
shares (the 50% SRCO share + the 45% featured artist share) or two separate
packets routed to the two separate Resolutions teams?

### 4.7 Non-featured filings — out of scope?
**Question:** Confirm we should configure our system to refuse non-featured
filings against SoundExchange (because non-featured shares are administered
by AFM & SAG-AFTRA Fund, not SoundExchange). Are there edge cases where
SoundExchange would still be the right recipient?

### 4.8 ISRC vs. account number — required vs. helpful
**Question:** SoundExchange's matching system is ISRC-driven. If an artist's
recording lacks an ISRC, can a filing still proceed by referencing
`(track_title, featured_artist_name)` (the documented fallback in the
Reports-of-Use rule), or will the inquiry be rejected as un-matchable?

---

## 5. What we'll do based on attorney response

### If attorney approves Guest-Access-based service-bureau filing:
1. Update `payer_config.py` SoundExchange entry: change `submission_email` to
   `info@soundexchange.com` (or remove email entirely in favor of in-portal
   submission); add `submission_channel: "sxdirect_contact_us"` field;
   add per-payee-class sub-config.
2. Update `dispute_email.txt` and packet template: reference SXDirect Guest
   provisioning as the basis of authority, not LPOA; add CFR citation block;
   fix SLA framing; differentiate Featured Artist vs. SRCO salutation.
3. Extend `Claim` + `Artist` model: SoundExchange Account #, ISRC,
   payee class, licensee class (subscription / non-subscription / business
   est. / etc.), distribution-date-disputed.
4. Add a deadline calculator that uses the 3-year retention rule as outer
   bound, with a configurable "internal urgency" threshold (e.g., flag at
   30 months out) — pending attorney clarification on whether there's a
   tighter contractual window in the actual Membership Agreement.
5. Add an onboarding step: "Add K6 Labs as a SXDirect Guest" with screen-
   recording instructions for the artist.
6. Block "File via email/portal" in `/ops` until SXDirect Guest provisioning
   is verified for that artist.
7. Add payee-class guard so non-featured anomalies are routed to AFM &
   SAG-AFTRA Fund (or refused).
8. Send first real test filing for a featured-artist + SRCO pilot artist
   with attorney CC'd.

### If attorney requires artist-direct submission (no service-bureau filing):
1. Same fallback architecture as BMI brief §5: repurpose
   `/admin/claims/{id}/file-via-email` to "send packet to artist for them to
   submit via SXDirect."
2. Operator dashboard label changes from "File via email" to "Send packet to
   artist for filing."
3. Inbound webhook: artist BCCs us when they correspond with SoundExchange,
   or we ask them to forward responses.

### If attorney requires LPOA + Guest Access (belt-and-suspenders):
1. Generate the LPOA at onboarding, store in artist record.
2. Walk the artist through SXDirect Guest provisioning as well.
3. Reference both in the packet (Guest is the operative SoundExchange-
   recognized authority; LPOA is supplementary state-law authorization).

---

## 6. References

### SoundExchange (primary)
- Artist Disputes — soundexchange.com/2024/03/20/artist-disputes-what-are-they-how-are-they-resolved/
- Overlaps & Disputes guide — soundexchange.com/2019/11/06/understanding-my-catalog-a-guide-to-overlaps-disputes/
- Bulk Resolution update — soundexchange.com/2021/12/06/my-catalog-update-overlaps-disputes-bulk-resolution-other-enhancements/
- Letters of Direction — soundexchange.com/what-we-do/for-artists-labels-and-producers/letters-of-direction/
- LOD Signature Requirements — soundexchange.com/2025/09/30/letters-of-direction-signature-requirements/
- LOD Part 1 Agreement (PDF) — soundexchange.com/wp-content/uploads/2023/04/LOD-Part-1-SoundExchange-LOD-Part-1-Agreement-Combo.pdf
- Primary & Guest Access — soundexchange.com/2020/11/24/primary-guest-access-in-soundexchange-direct-everything-you-need-to-know/
- Account Authorization Form (PDF) — register.soundexchange.com/static/files/SXAccountAuthorizationForm.pdf
- Membership Summary update — soundexchange.com/2021/07/08/soundexchange-direct-update-membership-summary/
- Search & Claim Artist Royalties — soundexchange.com/2020/10/26/my-catalog-update-search-claim-artist-royalties/
- All About ISRCs — soundexchange.com/2024/01/09/all-about-isrcs/
- Reporting Requirements — soundexchange.com/service-provider/reporting-requirements/
- FAQ index — soundexchange.com/frequently-asked-questions/
- FAQ: Do unclaimed royalties expire? — soundexchange.com/faq/do-unclaimed-royalties-expire/
- SXDirect login — sxdirect.soundexchange.com/login/
- ISRC Search — isrc.soundexchange.com

### Statutory / regulatory
- 17 U.S.C. § 114 (Cornell LII) — law.cornell.edu/uscode/text/17/114
- 37 CFR § 380.4 — law.cornell.edu/cfr/text/37/380.4 (and parallel Parts 382, 384)

### Industry commentary (not authoritative; for context)
- Hypebot, "How are artist and royalty disputes resolved on SoundExchange?"
  (Apr 2024) — hypebot.com/hypebot/2024/04/how-are-artist-and-royalty-disputes-resolved-on-soundexchange.html
- Mogul Help Center — help.usemogul.com/en/articles/10753658-soundexchange-disputes-and-overlaps
- The Jacobson Firm, "What is SoundExchange and Why You Should Sign-Up?"
- EPGD Business Law, "What Is the SoundExchange Letter of Direction?"

### ArtistOS code (TODO — verify each at the time of attorney review)
- `XR7/recovery/payer_config.py` — current per-payer config
- `XR7/services/templates/dispute_email.txt` — current email body
- `XR7/services/templates/evidence_packet.html` — current PDF template
