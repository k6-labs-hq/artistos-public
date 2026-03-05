"""
XR7 Platform — Artist Recovery Services Agreement (Terms & Conditions).

This module is the single source of truth for the current T&C text and
version.  Every acceptance event stores a SHA-256 hash of the text that was
presented to the artist at the time of acceptance, creating an immutable
audit trail.

Versioning convention: "YYYY-MM-DD.N" where N is a same-day revision counter
(starts at 1).  Bump the version and update the text whenever the legal terms
change.  Previous acceptance records are retained unchanged in the database.
"""

from __future__ import annotations

import hashlib

# ---------------------------------------------------------------------------
# Version identifier — bump this whenever the text below changes.
# ---------------------------------------------------------------------------

TERMS_VERSION: str = "2026-03-05.1"

# ---------------------------------------------------------------------------
# Full legal text of the Artist Recovery Services Agreement.
#
# Drafting notes:
#  - Contingency fee: 10% of gross recovery (no upfront cost to artist).
#  - Fund routing: all recoveries received by XR7 / Celero Commerce
#    (Merchant of Record) are held in a segregated client account, net 10%
#    fee, and disbursed to the artist's registered bank account as cleared.
#  - Autonomous real-time monitoring: artist grants XR7 a limited, revocable
#    power of attorney to file and pursue claims on their behalf.
#  - Governing law: State of California / US federal copyright law.
# ---------------------------------------------------------------------------

TERMS_TEXT: str = """\
ARTIST RECOVERY SERVICES AGREEMENT

Last Updated: March 5, 2026  |  Version: {version}

PLEASE READ THIS ARTIST RECOVERY SERVICES AGREEMENT ("AGREEMENT") CAREFULLY
BEFORE SUBMITTING YOUR INFORMATION.  BY CLICKING "I AGREE AND SUBMIT" YOU
ACKNOWLEDGE THAT YOU HAVE READ, UNDERSTOOD, AND AGREE TO BE LEGALLY BOUND BY
THE TERMS AND CONDITIONS SET FORTH HEREIN.  IF YOU DO NOT AGREE TO ALL OF THE
TERMS AND CONDITIONS, DO NOT CLICK "I AGREE AND SUBMIT" AND DO NOT SUBMIT YOUR
INFORMATION.

───────────────────────────────────────────────────────────────────────────────

RECITALS

This Agreement is entered into between the Artist (as identified by the
information submitted through the XR7 Platform) ("Artist" or "you") and
XR7, Inc. ("XR7," "we," "us," or "our"), a platform that identifies,
pursues, and recovers unpaid or underpaid royalties, licensing fees, and other
music-industry revenues on behalf of music creators and rights holders.

By agreeing to these terms and submitting your information, you engage XR7
to provide the Recovery Services described herein on a contingency basis.

───────────────────────────────────────────────────────────────────────────────

1.  DEFINITIONS

1.1 "Recovery Services" means (a) historical analysis of royalty statements,
    payment records, and catalog metadata to identify underpayments, missed
    payments, or licensing anomalies; (b) real-time continuous monitoring of
    all income streams identified or connected through the Platform; and (c)
    the preparation, submission, negotiation, and resolution of claims against
    Responsible Parties on Artist's behalf.

1.2 "Platform" means the XR7 Engine 2 software platform, APIs, and
    associated infrastructure operated by XR7.

1.3 "Recovered Funds" means any and all monies (including principal, interest,
    late fees, and damages) actually collected by XR7 from Responsible
    Parties as a direct result of the Recovery Services.

1.4 "Responsible Party" means any digital service provider, performing rights
    organisation, mechanical licensing collective, streaming platform,
    publisher, record label, synchronisation licensee, or other entity that
    owes payment to Artist for the use of Artist's musical works or sound
    recordings.

1.5 "Gross Recovery" means the total amount of Recovered Funds received by
    XR7 or its designated payment processor (Celero Commerce) from a
    Responsible Party before deduction of the Contingency Fee.

1.6 "Net Recovery" means Gross Recovery minus the Contingency Fee.

1.7 "Contingency Fee" has the meaning set forth in Section 4.1.

1.8 "Celero Commerce" means XR7's designated Merchant of Record and payment
    processor responsible for receiving, holding, and disbursing Recovered
    Funds pursuant to this Agreement.

───────────────────────────────────────────────────────────────────────────────

2.  ENGAGEMENT AND SCOPE OF SERVICES

2.1 Engagement.  Artist hereby engages XR7, and XR7 hereby accepts such
    engagement, to provide the Recovery Services on the terms and conditions
    set forth herein.

2.2 Historical Analysis.  Upon receipt of Artist's catalog and statement data,
    XR7 shall conduct a historical analysis covering all available periods
    for which data has been provided or is accessible through connected
    sources.  XR7 will use commercially reasonable efforts to identify all
    underpayments, unreported uses, and other recoverable amounts.

2.3 Real-Time Monitoring.  Following completion of the initial historical
    analysis, XR7 will continuously monitor Artist's connected income
    streams for anomalies, rate discrepancies, missing payments, and
    unreported uses.  Monitoring will continue for the duration of this
    Agreement or until Artist terminates the Agreement pursuant to Section 7.

2.4 Claim Filing and Pursuit.  XR7 will, in its sole professional
    discretion, determine which identified discrepancies warrant formal claims.
    XR7 will prepare and submit such claims, negotiate with Responsible
    Parties, and take all commercially reasonable steps to collect Recovered
    Funds.  XR7 may engage outside counsel or third-party specialists at
    its own expense; such costs shall not be passed to Artist.

2.5 No Guarantee.  XR7 does not guarantee any specific recovery amount or
    outcome.  The Recovery Services are provided on a best-efforts basis.
    Artist acknowledges that some claims may be disputed, unenforceable, or
    otherwise irrecoverable, and that XR7 shall not be liable for any
    failure to recover disputed amounts.

───────────────────────────────────────────────────────────────────────────────

3.  GRANT OF LIMITED AUTHORITY

3.1 Limited Power of Attorney.  Artist hereby grants XR7 a limited,
    revocable power of attorney, solely to the extent necessary to: (a) submit
    inquiries, disputes, and formal claims to Responsible Parties on Artist's
    behalf; (b) negotiate payment of Recovered Funds directly to XR7 or
    Celero Commerce for the benefit of Artist; and (c) execute settlement
    agreements valued at or below ten thousand United States dollars
    (USD $10,000.00) per individual claim without further written consent from
    Artist.  For any settlement exceeding USD $10,000.00, XR7 shall obtain
    Artist's written approval prior to execution.

3.2 Non-Exclusive.  The authority granted herein is non-exclusive.  Artist
    retains the right to independently pursue any claim; provided that Artist
    shall notify XR7 in writing before doing so with respect to any claim
    already in active pursuit by XR7, to avoid duplication of efforts.

3.3 Revocation.  Artist may revoke this limited power of attorney at any time
    by providing written notice to XR7 pursuant to Section 9.5.  Revocation
    shall not affect claims already submitted or settlements already negotiated.

───────────────────────────────────────────────────────────────────────────────

4.  FEES AND COMPENSATION

4.1 Contingency Fee.  In consideration for the Recovery Services, XR7 shall
    retain a contingency fee equal to ten percent (10%) of the Gross Recovery
    from each individual recovery event ("Contingency Fee").  No upfront
    retainer, setup fee, or monthly subscription is charged.  XR7 is
    compensated exclusively from Recovered Funds; if no funds are recovered,
    Artist owes XR7 nothing.

    EXAMPLE: If XR7 recovers USD $1,000.00 from a Responsible Party,
    XR7 retains USD $100.00 (10%) and disburses USD $900.00 (90%) to Artist.

4.2 Calculation Transparency.  XR7 shall provide Artist with an itemised
    recovery statement for each disbursement, showing Gross Recovery, the
    Contingency Fee deducted, Net Recovery disbursed, the source Responsible
    Party, the applicable period, and the date of disbursement.  This
    information is available at all times through the Artist's recovery
    dashboard at GET /artists/{{id}}/dashboard.

4.3 No Double-Dipping.  XR7 will not charge a Contingency Fee on any
    amounts that are recovered through the independent efforts of Artist or
    Artist's other representatives, provided Artist has furnished XR7 with
    prompt written notice of such independent recovery.

───────────────────────────────────────────────────────────────────────────────

5.  FUND COLLECTION, HOLDING, AND DISBURSEMENT

5.1 Designated Merchant of Record.  All Recovered Funds shall be remitted by
    Responsible Parties directly to Celero Commerce, XR7's designated
    Merchant of Record and payment processor.  Celero Commerce holds all
    inbound funds in a segregated client account maintained solely for Artist
    disbursements.

5.2 Disbursement Timeline.  XR7 shall cause Celero Commerce to disburse Net
    Recovery amounts to Artist's registered bank account within five (5)
    business days of clearance of the received funds into the segregated
    client account.  "Clearance" means the earlier of: (a) confirmation that
    the payment is irrevocable and free of charge-back risk; or (b) thirty
    (30) calendar days after receipt.

5.3 Partial and Multi-Source Disbursements.  Artist acknowledges that
    recoveries will be received from multiple Responsible Parties at different
    times, in different amounts, and potentially in different currencies.
    XR7 will disburse each tranche of Net Recovery as it is cleared,
    without waiting to aggregate all recoveries.  Each disbursement will be
    accompanied by the itemised statement described in Section 4.2.

5.4 Currency.  All disbursements to Artist will be made in United States
    dollars (USD) by default.  Recovered Funds received in foreign currency
    will be converted to USD at the prevailing mid-market rate on the date of
    conversion, with no markup applied by XR7.

5.5 Unclaimed Funds.  If XR7 is unable to disburse Net Recovery to Artist
    due to invalid, outdated, or missing bank account information, XR7 will
    hold such funds for a period of twelve (12) months and make commercially
    reasonable efforts to contact Artist.  If Artist does not provide valid
    disbursement instructions within such period, the funds shall be subject to
    applicable state unclaimed property laws.

5.6 Payment Credentials.  Artist's bank account and payment credentials are
    stored exclusively within the Celero Commerce Customer Vault.  XR7
    never stores or transmits raw payment card or ACH routing data.

───────────────────────────────────────────────────────────────────────────────

6.  ARTIST REPRESENTATIONS AND WARRANTIES

6.1 Authority.  Artist represents and warrants that: (a) Artist is the legal
    owner or exclusive licensee of all intellectual property rights in the
    musical works and sound recordings to be covered by the Recovery Services;
    (b) Artist has full legal authority to enter into this Agreement; (c) no
    third party (including any label, publisher, or manager) has an
    outstanding conflicting claim, lien, or assignment over the revenues at
    issue; and (d) Artist is at least eighteen (18) years of age or has
    obtained the required parental or guardian consent.

6.2 Accuracy of Information.  Artist represents that all information submitted
    through the Platform (including catalog metadata, royalty statements, and
    banking details) is accurate, complete, and not misleading as of the date
    of submission.  Artist agrees to promptly update any information that
    becomes inaccurate.

6.3 No Conflicting Engagements.  Artist represents that Artist has not
    engaged, and will not engage during the term of this Agreement, any other
    royalty recovery service to pursue the same claims that XR7 is actively
    pursuing, without first notifying XR7 in writing.

───────────────────────────────────────────────────────────────────────────────

7.  TERM AND TERMINATION

7.1 Term.  This Agreement commences on the date Artist accepts these terms and
    shall continue on a rolling month-to-month basis until terminated by
    either party as provided herein.

7.2 Termination by Artist.  Artist may terminate this Agreement at any time by
    providing written notice to XR7.  Termination will take effect within
    thirty (30) calendar days of receipt of such notice.

7.3 Termination by XR7.  XR7 may terminate this Agreement upon thirty
    (30) calendar days' written notice to Artist, or immediately if Artist
    breaches any material provision of this Agreement and fails to cure such
    breach within ten (10) business days of written notice thereof.

7.4 Effect of Termination.  Termination shall not affect: (a) XR7's right
    to receive and retain the Contingency Fee on Recovered Funds that were
    collected or for which a binding settlement was reached prior to or within
    ninety (90) days after the effective termination date; or (b) any
    outstanding disbursement obligations to Artist under Section 5.

───────────────────────────────────────────────────────────────────────────────

8.  LIMITATION OF LIABILITY; INDEMNIFICATION

8.1 LIMITATION OF LIABILITY.  TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE
    LAW, IN NO EVENT SHALL XR7 BE LIABLE FOR ANY INDIRECT, INCIDENTAL,
    CONSEQUENTIAL, SPECIAL, EXEMPLARY, OR PUNITIVE DAMAGES ARISING OUT OF OR
    RELATED TO THIS AGREEMENT OR THE RECOVERY SERVICES, EVEN IF XR7 HAS
    BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.  XR7'S TOTAL AGGREGATE
    LIABILITY SHALL NOT EXCEED THE TOTAL CONTINGENCY FEES ACTUALLY PAID TO
    XR7 BY OR ON BEHALF OF ARTIST IN THE TWELVE (12) MONTHS PRECEDING THE
    CLAIM.

8.2 Indemnification by Artist.  Artist shall indemnify, defend, and hold
    harmless XR7, its officers, directors, employees, and agents from and
    against any claims, damages, losses, and expenses (including reasonable
    attorneys' fees) arising out of or relating to: (a) Artist's breach of any
    representation, warranty, or obligation under this Agreement; or (b) any
    third-party claim that Artist's catalog or the Recovery Services infringe
    upon the intellectual property rights of such third party.

───────────────────────────────────────────────────────────────────────────────

9.  GENERAL PROVISIONS

9.1 Governing Law.  This Agreement shall be governed by and construed in
    accordance with the laws of the State of California and applicable United
    States federal copyright law (17 U.S.C. § 101 et seq.), without regard to
    its conflict-of-laws principles.

9.2 Dispute Resolution.  Any dispute arising under this Agreement shall be
    resolved by binding arbitration administered by the American Arbitration
    Association under its Commercial Arbitration Rules.  Arbitration shall be
    conducted in Los Angeles County, California.  Judgment on the award may
    be entered in any court of competent jurisdiction.  Nothing herein shall
    prevent either party from seeking injunctive or other equitable relief in
    a court of competent jurisdiction.

9.3 Entire Agreement.  This Agreement constitutes the entire agreement between
    the parties with respect to its subject matter and supersedes all prior and
    contemporaneous agreements, representations, and understandings.

9.4 Amendments.  XR7 reserves the right to update these terms at any time.
    Material changes will be communicated to Artist via the email address on
    file.  Continued use of the Platform after the effective date of an update
    constitutes acceptance of the revised terms.

9.5 Notices.  Notices to XR7 shall be sent to legal@XR7.com.  Notices
    to Artist shall be sent to the email address provided during registration.

9.6 Severability.  If any provision of this Agreement is found unenforceable,
    the remaining provisions shall remain in full force and effect.

9.7 Waiver.  No waiver of any provision of this Agreement shall be effective
    unless in writing and signed by the party against whom the waiver is
    sought to be enforced.

9.8 Electronic Signature.  Artist agrees that clicking "I AGREE AND SUBMIT"
    constitutes a valid electronic signature and legally binding acceptance of
    this Agreement, equivalent to a handwritten signature, pursuant to the
    Electronic Signatures in Global and National Commerce Act (E-SIGN Act,
    15 U.S.C. § 7001 et seq.) and the Uniform Electronic Transactions Act
    (UETA).

───────────────────────────────────────────────────────────────────────────────

BY CLICKING "I AGREE AND SUBMIT" YOU CONFIRM THAT:

  ✓ You have read and understood this entire Agreement.
  ✓ You agree that XR7 will retain 10% of every recovery as a Contingency
    Fee, with the remaining 90% (Net Recovery) disbursed to you.
  ✓ You authorise Celero Commerce to receive Recovered Funds on your behalf
    and to disburse Net Recovery to your registered bank account.
  ✓ You grant XR7 the limited power of attorney described in Section 3.
  ✓ You confirm you have the legal authority to enter into this Agreement.

───────────────────────────────────────────────────────────────────────────────

Version: {version}
© 2026 XR7, Inc.  All rights reserved.
""".format(version=TERMS_VERSION)


def terms_text_sha256() -> str:
    """Return the SHA-256 hex-digest of the current T&C text."""
    return hashlib.sha256(TERMS_TEXT.encode("utf-8")).hexdigest()
