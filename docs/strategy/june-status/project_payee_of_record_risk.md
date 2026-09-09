---
name: project-payee-of-record-risk
description: "Chain-of-title risk in dispute flow can route around XR7's 12% contingency; every PRO submission needs an upfront payee-of-record confirmation"
metadata: 
  node_type: memory
  type: project
  originSessionId: 534fc797-ff47-46c1-9c64-7e8e4000b165
---

Every PRO/MLC dispute packet must include a "please confirm the current payee of record before processing" line. The PRO's reply (payee is X) is the definitive answer about who'll receive the recovery check.

**Status:** Shipped in #330 (2026-05-26) — the line now renders unconditionally in all three dispute artifacts (text email, HTML email, PDF cover page). Applies to every payer, not just BMI; the templates are unified.

**Why:** If XR7 audits a catalog where the writer has assigned/sold their rights, the recovery payment goes to the new payee of record — not the writer, not XR7. We do the work, somebody else cashes the check, our 12% contingency vanishes. Matt Kallberg flagged this on 2026-05-26 as "the nuclear option that guarantees you never get blindsided."

**How to apply:**
- When working on dispute templates (BMI/ASCAP/SESAC/GMR/MLC/HFA), the confirmation line is non-negotiable — don't ship a template without it
- When reviewing the dispute workflow, the [[project-beta-status-2026-04-30-eod]] reply-correlation work (Postmark inbound, PR #226) is what captures the payee answer back to the dispute record
- Distributor disputes are lower-risk because the artist owns their own distributor account, but the same principle applies to any payer where ownership can transfer
- Don't gate recovery work programmatically on positive confirmation until we've seen real PRO reply patterns — manual review first
- If a stakeholder proposes scope changes to the dispute system that skip the payee step ("just send the packet, we'll deal with it"), push back — this is the wedge between an enforceable contingency business and a service customers can route around
