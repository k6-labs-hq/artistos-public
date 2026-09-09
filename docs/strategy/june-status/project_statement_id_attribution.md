---
name: project-statement-id-attribution
description: events.statement_id + payments.statement_id ship as of
metadata: 
  node_type: memory
  type: project
  originSessionId: 534fc797-ff47-46c1-9c64-7e8e4000b165
---

`events` and `payments` carry a nullable `statement_id` column as of 2026-05-27 (#333 + #334). Every new event/payment inserted via the statement upload paths is stamped with the source statement's UUID.

**What works now:**
- Per-file recovery reporting: "this BMI PDF surfaced $X, this CSV surfaced $Y" — computable for any artist whose data was ingested after #334 shipped.
- Reprocess flow (`POST /admin/statements/{id}/reprocess`) also stamps statement_id correctly.

**What doesn't:**
- Historical rows from before #334 stay NULL. No backfill — we don't have the data and synthesizing it would put wrong numbers in reports.
- No DB-level FK constraint. The upload flow commits events + payments BEFORE the Statement row exists, so an immediate-check FK would fail every upload. Adding the FK requires restructuring the write order (Statement created early, counts UPDATEd at end). Out of scope for #334.

**How to apply:**
- When generating recovery reports, prefer the per-file attribution columns over filename heuristics. Beware of NULLs for old data.
- If anyone asks "why doesn't `statement_id` have a FK constraint" — see migration `20260527_0001` docstring; restructuring the upload commit order is the right follow-up, not adding the FK on top of the current order.
- If a future PR restructures upload to create Statement first → add the FK constraint at that point. The column shape is already correct (nullable VARCHAR matching statements.id).
- This unlocks the per-file recovery report Jason asked about on 2026-05-27. The report query template lives in the conversation that produced #333 — re-derive with: `SELECT s.format_detected, COUNT(DISTINCT e.statement_id), COUNT(e.id) FROM events e LEFT JOIN statements s ON s.id = e.statement_id WHERE e.artist_id = ? GROUP BY 1`.

**Related:** [[project-beta-status-2026-05-28]]
