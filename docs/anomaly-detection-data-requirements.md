# Anomaly detection — what data unlocks what

**Last updated:** 2026-05-06

This doc explains why XR7's anomaly engine sometimes returns "no anomalies detected" even on substantial datasets, and what data shape unlocks each rule. Surfaced during the Tolliver walkthrough on 2026-05-06: 47 statements ingested, 24,027 payments persisted, 6+ years of history — and zero findings. The empty state was correct.

The conclusion is simple: **royalty recovery is fundamentally a cross-source, cross-period exercise.** Distributor-only data (TuneCore alone, DistroKid alone, etc.) is not enough to fire most of our rules. The high-value findings live at the seams between PRO data, mechanical-collective data, and distributor data.

This is consistent with how real audit firms work — they don't audit a single distributor; they reconcile across all the income streams a writer or artist has.

---

## 1. The empty state, decoded

When the dashboard says "No anomalies detected for the data you've uploaded so far," it means the engine ran and produced zero finding dicts. Not a failure mode — a correct answer for the inputs.

We surface that empty state on `/dashboard` with a list of what XR7 looks for and what would unlock each surface. That copy is the source of truth for the user-facing version. This doc is the engineering view.

---

## 2. Rule-by-rule data requirements

Rules live in `XR7/anomaly/rules/transparent_rules.py`. Each one needs a specific signal pattern to fire. Distributor-only data is missing several of those patterns by construction.

### `STREAM_PAYOUT_UNDER_50` — Stream payout less than 50% of baseline

- **What it does:** flags artists whose median per-stream payout rate is below 50% of a "platform baseline."
- **Current implementation gap:** the "baseline" is computed as the median of the artist's own rates (`median_platform_rate = median(stream_rates)`). That's a degenerate comparison — the artist's median can never be much less than itself. **This rule effectively never fires on real data today.** Real fix: replace with an external baseline (industry per-platform rate table) or a peer comparison across similar artists.
- **What unlocks it (after the fix):** any platform with stream events and unit_value populated.

### `HIGH_RETROACTIVE_RATIO` — High proportion of retroactive payments

- **What it does:** flags when a payer (BMI, MLC, etc.) is delivering a high share of payments as retroactive corrections rather than current-period income. Strong signal of unrecovered current-period royalties.
- **What it needs:** payments where `Payment.source` ends with `/reprocessing` or `/adjustment`. Our parser tags these for BMI's 28-col CSV (BMI distinguishes "current activity" rows from "reprocessing" rows in `PERIOD` column suffixes) and for MLC's official statement (`Processing Type` column has "regular" vs "reprocessing"). **TuneCore + DistroKid don't differentiate — they pass-through DSP earnings without retroactive-vs-current classification.**
- **What unlocks it:** real BMI 28-col CSV, real MLC member-portal export.

### `STREAM_MONTH_WITHOUT_PAYMENT` — Stream activity without corresponding payment

- **What it does:** flags months where the artist has stream events but no royalty payment for that period.
- **What it needs:** events and payments from **different sources** so the engine can spot mismatches. When events and payments come from the same upload (e.g., a TuneCore CSV that contains both stream counts and earnings), the rule sees no mismatches because every event has a payment by construction.
- **What unlocks it:** DSP-direct stream data (Spotify for Artists, Apple Music for Artists) cross-referenced with distributor or PRO payment data. Today we don't have a path for DSP-direct data. Future ingestion target.

### `PAYMENT_GAP_OVER_60` — Extended payment gap

- **What it does:** flags artists with a 60+ day gap in their royalty payment history.
- **What it needs:** payment-period continuity check. Tolliver has continuous monthly TuneCore payments → no gaps → rule doesn't fire.
- **What unlocks it:** automatically active for any source. Fires when a payer goes silent for >60d on an artist.

### `TRACK_RATE_OUTLIER` — Track-level rate outlier

- **What it does:** flags individual tracks earning materially below the artist's catalog median rate at the same platform.
- **What it needs:** 4+ tracks with meaningful per-track stream volume, and per-track rate variance above a threshold.
- **What unlocks it:** active on distributor data once the artist has enough tracks. Tolliver might have hit this if his catalog is large enough — but the current rule's threshold may not have been crossed. Worth re-running once we add explicit per-rule trace logging.

### `BMI_BELOW_THRESHOLD_ACCRUALS` — Royalties accrued but unpaid (sub-threshold)

- **What it does:** finds royalties that accrued under BMI's $2 minimum distribution threshold and were therefore held rather than paid. Common for catalog tracks with low international play volume.
- **What it needs:** BMI Accrual Report PDF — a separate document from the regular royalty statement, showing held balances per work.
- **What unlocks it:** parser for the BMI Accrual PDF. Open issue. The 78 PDFs in Tolliver's `/Downloads/6/tolliver/BMI Statements/` directory aren't accrual reports — those are formatted distribution statements. A separate request.

---

## 3. Cross-source unlocks (the high-value ones)

Several findings only fire when we can compare two different income streams for the same artist:

| Finding | Needs |
|---|---|
| **DSP rate vs distributor rate mismatch** | DSP-direct stream data + distributor payment data |
| **PRO retroactive vs MLC current-period** | BMI 28-col CSV + MLC official export |
| **Distributor admin-fee anomaly** | Distributor-as-given vs DSP-as-source |
| **Lost foreign performance royalties** | BMI/ASCAP foreign distribution data + DSP territory data |
| **Black-box income claims** | MLC unmatched works data + distributor catalog metadata |

None of these fire with TuneCore alone. The Tolliver walkthrough surfaced this clearly: distributor data tells us how much DSPs paid via the distributor, but says nothing about what BMI/ASCAP/MLC should have paid for the same activity.

---

## 4. What this means for product

### For artist onboarding

The "Where do your statements come from?" screen now lists both PROs and distributors. **Ideally we should encourage artists to upload from every checked source** — having TuneCore but not BMI cuts off the cross-source comparisons that produce the highest-value findings.

Future polish: on the dashboard's empty state, if the artist checked BMI/ASCAP/MLC at onboarding but hasn't uploaded those statements yet, the empty state should specifically say "Upload your BMI statement to unlock retroactive analysis" rather than the generic "additional data unlocks" copy.

### For investor narrative

This is actually a STRENGTH of the product positioning, not a weakness. Audit firms charge $5K-$25K for cross-source reconciliation because the work is real. We charge 12% contingency because we automate it. Rules that fire on single-source data alone aren't where the value is — that's why competitors stuck on "DSP rate analysis" produce noise rather than recovery.

### For attorney review

The four payer attorney briefs (`bmi-`, `ascap-`, `mlc-`, `soundexchange-dispute-attorney-brief.md`) cover the dispute-filing side of recovery. This doc covers the detection side. Both are needed: detect → file → recover.

---

## 5. Concrete next steps for actually surfacing anomalies on real artists

In priority order, what would have made the Tolliver walkthrough produce findings:

1. **Get the BMI 28-col CSV from the BMI member portal.** This is the format our parser already supports (`bmi_real`). Tolliver's BMI member ID is 885077 (visible in the PDF filenames he shared). If he can grab the CSV export — separate download from the PDFs in BMI Online Services — we'd have the retroactive data.
2. **Get the real MLC member-portal export.** The "MLC Statement.numbers" in his folder isn't actually MLC format — it's a DistroKid summary saved with an MLC-y filename. The real MLC export has `Payee MLC Number / Usage Period Start Date / DSP Name / Work Primary Title / ISWC / Processing Type / Royalty Amount / Distributed Amount` columns.
3. **Build the BMI PDF parser** (issue #206). Less urgent if we can get the CSV (option 1), but useful if artists only have PDFs.
4. **Build a BMI Accrual Report PDF parser** (separate from #206). This is the document that surfaces the below-threshold-accruals finding — small recurring royalties that BMI holds because they're under the $2 distribution minimum.
5. **Replace `STREAM_PAYOUT_UNDER_50`'s degenerate self-baseline** with an external industry baseline or peer comparison. As written today the rule almost never fires.

---

## 6. References

- `XR7/anomaly/rules/transparent_rules.py` — the rules themselves
- `XR7/anomaly/engine.py` — engine wiring (`AnomalyEngine.detect_all` calls `detect_rule_anomalies`)
- `XR7/api/routers/anomalies.py:run_detection_and_persist` — confidence gating + DB persistence
- `XR7/ingestion/statement_parser.py` — format detection + per-payer parsers
- [BMI dispute attorney brief](runbooks/bmi-dispute-attorney-brief.md) — dispute-filing side
- Issue #206 — BMI PDF parser
