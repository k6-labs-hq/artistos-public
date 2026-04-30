# Next 30 days — runway-constrained action plan

**Date:** 2026-04-30 EOD
**Audience:** Jason (CTO), Matt (CEO)
**Purpose:** Tactical companion to [disruption-analysis-2026-04-29.md](disruption-analysis-2026-04-29.md). The strategic doc was written assuming 24 months of runway. As of tonight's diagnostic, the actual runway is **<6 months** and "money yesterday" pressure is real. This document captures what to do when the dominant constraint shifted from engineering throughput to capital event.

---

## The frame, in one sentence

**The next 30 days is about creating a capital event, not about reaching $200M.** The $200M outcome was a 24-month story. Until runway is solved, that story is on pause; survival is the frame.

The contingency-fee model — which the entire disruption analysis was built around — does NOT solve runway. Even if we file 5 BMI disputes next week, BMI's response is 30/90 days, remittance lands 30 days after that, 12% of small-artist recoveries is small dollars. **Contingency revenue is months 6–12, not months 1–4.**

So the realistic paths to runway extension:

| Path | Timeframe | Realistic? |
|---|---|---|
| Pre-seed / seed raise on the asset | 60–120 days | **Most likely path** |
| Services revenue (flat-fee audit for label/manager) | 30–60 days | **Fastest cash, best signal** |
| Strategic acquihire / asset sale | 90–180 days | Possible but speculative |
| Partner / whitelabel deal with retainer | 60–120 days | Yes, depends on Matt's network |
| Wait for contingency revenue to compound | 6–18 months | **No — kills the company** |

## What's true about our position

Honest inventory of the assets and constraints, based on the 5-question diagnostic on 2026-04-30:

### Assets (real)

- **Engineering complete** for the missing-middle. As of EOD: detection → claim drafting → PDF rendering → real Postmark email outbound with per-payer config → inbound reply correlation → operator-trigger endpoint. Curl `POST /claims/{id}/file-via-email` would file a real BMI dispute today.
- **Matt's Nashville network.** Country/Americana songwriter scene = deep BMI exposure = exact PRO our engine handles best. Middle Tennessee is the right city for our use case.
- **50+ waitlist** with well-known names (claim, distribution unverified). Could plausibly grow to 1000 short-term per Jason's read. **Action: pull HubSpot data this week to actually see the recovery-estimate distribution.**
- **Matt has music-rights attorney relationships** — LPOA review is a 2–5 day item, not a 2-week scramble.
- **Postmark is fully operational** — account approved, domain verified, MX wired, inbound + outbound both verified end-to-end.
- **Trolley payout pipeline** already wired for post-remittance disbursement.

### Constraints (real)

- **<6 months personal runway for Jason.** Hard floor.
- **Matt full-time on K6 Labs** (per Jason's belief).
- **Contingency-fee model is wall-clock-bound** to PRO response cycles. Cannot produce meaningful revenue inside 6 months.
- **Jason has not personally talked to songwriters/managers about this product.** Matt has. Risk: Jason's product instincts are based on engineering completeness, not on user signal. *Critical: Jason needs to be on at least 2–3 customer calls in next 30 days, as product lead, not as sales lead.*
- **Jason's existing contacts are off-limits until "more solidified"** — relationship-protection. Means top-of-funnel = Matt's network + waitlist, not Jason's.

---

## The 30-day execution plan

Sequenced, with specific weekly outcomes. **Reality-check at end of each week — if the week's outcome didn't land, adjust before the next.**

### Week 1 (2026-04-30 → 2026-05-07): Cohort + legal in motion

**Engineering tasks (Jason)**

- [ ] Pull HubSpot waitlist sorted by `xr7_recovery_estimate` desc. Top 20. Names + numbers.
- [ ] Generate sample evidence packet PDF for top 3 waitlist names *if data on hand* (preview what we'd send for them — useful for Matt's outreach).
- [ ] Operator dashboard MVP — at minimum a list of claims with a "file via email" button. Half day of frontend. Make it real enough to demo to investors.

**Business tasks (Matt)**

- [ ] LPOA template drafted (use industry-standard language; Matt's attorney reviews).
- [ ] Outreach to top 5 candidates — mix of Nashville network warm intros + top waitlist signups. Pitch: "free audit, file on your behalf with LPOA, 12% contingency on actual recovery, nothing if zero recovered."
- [ ] Get 2–3 of those 5 to commit to uploading statements within the next 7–10 days.

**Outcome target end of week 1:** 1+ artist with statements uploaded + LPOA in the loop. If we don't hit that, **the strategic plan needs a different first move** — services revenue conversation with a label/manager, since waiting on individual artist conversion is too slow.

### Week 2 (2026-05-07 → 2026-05-14): First filing + investor narrative

**Engineering tasks (Jason)**

- [ ] First real BMI dispute filed via the operator dashboard, on real beta artist data, with signed LPOA. **This is the proof point everything else hinges on.**
- [ ] Capture the filed dispute as a "case in motion" exhibit — screenshots of operator dashboard, the rendered PDF, the Postmark MessageID, the dispute email body.

**Business tasks (Matt)**

- [ ] Investor 1-pager drafted. Focus: engineering completeness + first dispute filed + Nashville cohort + projected pipeline. NOT 24-month roadmap — that's not the pitch right now. The pitch is "fund 12 months of runway, get to first wave of recoveries + 100-artist cohort."
- [ ] Identify 5–10 target investors. Filters: pre-seed / seed funds with music-vertical interest, music-tech-savvy angels, Nashville-aware investors. Avoid generic SaaS VCs — they don't grok the market.
- [ ] First 2–3 investor coffees / Zoom intros (warm intros from Matt's network preferred).

**Outcome target end of week 2:** First dispute filed + investor outreach started. **Both must happen this week.** If first dispute hasn't filed by week 2, weeks 3–4 don't work — the pitch needs the filing as proof.

### Week 3 (2026-05-14 → 2026-05-21): Pipeline + services revenue path

**Engineering tasks (Jason)**

- [ ] 2–4 more disputes filed if cohort allows.
- [ ] Investor demo flow polished — screen-share-ready demonstration of detection → PDF → file-via-email → audit log.

**Business tasks (Matt)**

- [ ] First investor pitch meetings (3–5).
- [ ] **Parallel: services revenue conversation with one label or management company in Nashville.** Pitch: "We'll audit your roster's BMI/MLC for $5K–$25K flat. Surface findings; you decide what to file. Deliverable in 30 days." Even one signed deal extends runway 1–2 months and creates a "we have customers" data point for the raise.

**Outcome target end of week 3:** Investor conversations active + services revenue conversation seriously underway. If neither has movement by end of week 3, the investor strategy is wrong (wrong investors, wrong pitch, wrong timing) and we pivot to acquihire conversations.

### Week 4 (2026-05-21 → 2026-05-28): Conversion week

**Engineering tasks (Jason)**

- [ ] More disputes filed; first response from BMI possibly arrives (acknowledgement, not decision yet).
- [ ] Operator dashboard polished for investor-demo-quality.

**Business tasks (Matt)**

- [ ] Term sheet conversations with 1–2 most-engaged investors.
- [ ] Services revenue: closing or close-to-closing conversation with one client.

**Outcome target end of week 4:** Term sheet in hand OR services revenue agreement signed. Either constitutes a capital event that extends runway. **If neither, the runway clock is now operationally critical — we need to talk about emergency moves: bridge from friends/family, founder credit lines, asset sale conversations.**

---

## Critical paths and decision points

### "If we hit a wall on artist sourcing"

Symptom: by end of week 1, no artist has committed to uploading statements.

Pivot: services revenue path becomes primary, not parallel. Find one Nashville label or management company, charge them $10K-$25K flat for portfolio audit. Their roster of 20–200 artists becomes the cohort by proxy.

### "If we hit a wall on legal review"

Symptom: LPOA review delays beyond week 1.

Pivot: file disputes with the artist's signed authorization on a more basic form (artist signs an "I authorize K6 Labs to file royalty audit findings on my behalf at BMI/MLC/etc." 2-paragraph letter). Less ironclad than a full LPOA but legally sufficient to start. Full LPOA replaces it once attorney review completes.

### "If we hit a wall on investor interest"

Symptom: no investor traction by end of week 3.

Pivot: strategic acquihire conversations. Approach Songtrust/Downtown, Royalty Exchange's audit arm, smaller royalty-recovery firms. Deal shape: asset acquisition + retained team for X months. Lower exit value than a Series A trajectory but solves runway immediately.

### "If services revenue is the only thing that lands"

Lean in. Services revenue is real revenue, supports a Series A pitch later, and proves the model works. The disruption analysis assumed contingency-fee was the path to scale; services revenue is a parallel path that may actually scale faster in our specific situation (Nashville label/manager network has clearer customer acquisition than artist-by-artist).

---

## What this document is NOT

- A 24-month strategic plan. The runway constraint makes that document irrelevant for now.
- A revised disruption analysis. The thesis is unchanged; the timeline shifted.
- A detailed engineering roadmap. Engineering is essentially done; this is execution work.

## What this document IS

A 30-day survival-and-acceleration plan, with specific weekly outcomes that are checkable and adjustable. Re-read at the start of each week. **The plan should change based on what's working.**

---

*Last updated 2026-04-30 EOD by Jason + Claude diagnostic conversation. Re-evaluate at the end of each week. The 5-question diagnostic that produced this plan should be re-run if the situation changes materially (artist commits, investor expresses real interest, services deal signs, or — opposite — none of those happen by end of week 2).*
