# ArtistOS Reference Architecture

Canonical reference architecture for ArtistOS. Read in order if you're new; jump around once you know your way around.

> **Goal:** a new engineer can read this folder and understand the full system in 30 minutes.

## Status legend

- **Current** — documents what runs today, grounded in source paths.
- **Target** — documents the intended future state. A status banner in each doc names the blocking issues.

## Index

| # | Doc | Status | Blocked on |
|---|-----|--------|------------|
| 01 | [System context (C4 L1)](01-system-context.md) | Current | — |
| 02 | [Containers (C4 L2)](02-containers.md) | Current | — |
| 03 | [Deployment (AWS)](03-deployment.md) | Target | [#102](https://github.com/k6-labs-hq/ArtistOS/issues/102) |
| 04 | [Data flows](04-data-flows.md) | Current | — |
| 05 | [Integrations](05-integrations.md) | Current | — |
| 06 | [Identity & auth](06-identity.md) | Target | [#100](https://github.com/k6-labs-hq/ArtistOS/issues/100), [#101](https://github.com/k6-labs-hq/ArtistOS/issues/101) |
| 07 | [Observability](07-observability.md) | Target | [#94](https://github.com/k6-labs-hq/ArtistOS/issues/94)-[#98](https://github.com/k6-labs-hq/ArtistOS/issues/98) |
| 08 | [Security boundaries](08-security-boundaries.md) | Current | — |
| 09 | [**Production readiness checklist**](09-production-readiness.md) | Gate | — |

## Conventions

- Diagrams are Mermaid, embedded inline. GitHub renders them natively.
- Code references use `path:line` so you can click into the source.
- "Target" docs describe what we intend to build; they are not a promise.

## Related existing docs

These remain authoritative for their subjects and are linked from the relevant section above:

- [`final_architecture_summary.md`](../final_architecture_summary.md) — comprehensive stack and data-model overview
- [`partner_integration_architecture.md`](../partner_integration_architecture.md) — partner integration patterns
- [`claims_state_machine.md`](../claims_state_machine.md) — claim lifecycle runbook
- [`celery_workflows.md`](../celery_workflows.md) — Celery task registry and beat schedule
- [`security_hardening_plan.md`](../security_hardening_plan.md) — STRIDE model and controls roadmap
- [`trolley_failure_playbook.md`](../trolley_failure_playbook.md) — disbursement failure runbook

The older root-level architecture files (`architecture_overview.md`, `architecture_diagrams.md`) are superseded by this suite and kept only as redirect stubs.

## Tracking

This suite is delivered under [EPIC #107](https://github.com/k6-labs-hq/ArtistOS/issues/107) with one sub-issue per doc:
[#109](https://github.com/k6-labs-hq/ArtistOS/issues/109) ·
[#110](https://github.com/k6-labs-hq/ArtistOS/issues/110) ·
[#111](https://github.com/k6-labs-hq/ArtistOS/issues/111) ·
[#112](https://github.com/k6-labs-hq/ArtistOS/issues/112) ·
[#113](https://github.com/k6-labs-hq/ArtistOS/issues/113) ·
[#114](https://github.com/k6-labs-hq/ArtistOS/issues/114) ·
[#115](https://github.com/k6-labs-hq/ArtistOS/issues/115) ·
[#116](https://github.com/k6-labs-hq/ArtistOS/issues/116) ·
[#117](https://github.com/k6-labs-hq/ArtistOS/issues/117)
