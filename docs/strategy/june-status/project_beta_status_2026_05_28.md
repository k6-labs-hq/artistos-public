---
name: project-beta-status-2026-05-28
description: "Late-May closed-beta wave shipped — dashboard polish, payee-of-record protection in dispute templates, per-file recovery attribution, duplicate-content UX"
metadata: 
  node_type: memory
  type: project
  originSessionId: 534fc797-ff47-46c1-9c64-7e8e4000b165
---

Late-May (2026-05-20 → 2026-05-28) closed-beta wave. Wraps the work that came out of Matt's first close read of the dashboard and the first round of internal demo prep.

**Shipped this wave:**

- **Dashboard "Get statements" panel** (#315, #319, #320, #321, #323): tabbed payer categories — PRO (BMI/ASCAP/SESAC/GMR), Mechanical (MLC/HFA/Music Reports), Distributor (DistroKid/TuneCore/CD Baby/UnitedMasters/Vydia/The Orchard), International (placeholder). SoundExchange removed at user direction (not a competitor — see SoundExchange notes in MEMORY).
- **Dashboard spacing + status visibility** (#316, #317, #318, #337): tightened vertical rhythm; status badges in Upload history now render `error_summary` as a hover tooltip with dotted-underline cue.
- **Payee-of-record protection** (#329, #330): every PRO/MLC dispute packet (email + PDF cover) now includes a "Payee Confirmation Request" block. See [[project-payee-of-record-risk]].
- **Per-file recovery attribution** (#333, #334): `events.statement_id` + `payments.statement_id` columns added (nullable, indexed, no FK — see [[project-statement-id-attribution]]). All new uploads stamp source statement; historical rows stay NULL by design.
- **Duplicate-content status** (#336, #337): new `DUPLICATE` statement status when parser produces rows but DB-level dedup catches every one (common when same data re-uploaded in different file wrapper). Surfaces with an explanation in the error_summary tooltip.

**Known parser scope (unchanged from prior wave):**

- PDFs: only BMI Royalty Statement PDFs parse. ASCAP/SESAC/GMR/MLC PDFs fail with "PDF format not recognized."
- .numbers: works via numbers-parser, but a file named "MLC Statement.numbers" can be anything inside — checked one during demo prep that contained DistroKid data (table literally named `DistroKid_*`). Format detection runs on headers, not filename, so this is fine.
- Excel: one corpus file in QA history (Chris DeAnda) failed with 6,539 skipped rows; the XLSX path isn't wired for whatever shape that file has. Not investigated.

**Open follow-ups from this wave:**

- #331 — settings-singleton caching env vars at import time, breaks 5 dispute-delivery tests on main. Not yet fixed.
- 4 pre-existing TuneCore/Ditto detection tests failing on main; not caused by this work, not investigated.
- Dashboard's Upload history still shows file-system status; no view yet of per-statement \$ attributed (we have the data via statement_id, just no UI for it).

**Demo readiness:**

David Tolliver (`jtdman+dtolliver@gmail.com`) is the demo artist; wiped 3 times this session via [[project-qa-artist-wipe-procedure]] to support clean walkthroughs. Other QA artists preserved (Matt Alderman, Mark Addison Chandler, Brody Kean, Chris DeAnda, Nova, Barrett Baber).

**How to apply:**
- This snapshot supersedes [[project-beta-status-2026-04-30-eod]] for "what does the beta look like right now."
- The runway constraint ([[project-runway-constraint]]) still dominates roadmap calls; this wave is closed-beta polish for vetted-user demos, not new acquisition surface.
