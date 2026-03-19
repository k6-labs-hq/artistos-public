# AI Agent Governance Framework

## Scope

XR7 Engine 2 uses exactly two autonomous agents under a single orchestration graph:

- Onboarding & Preparation Agent
- Recovery & Execution Agent

No additional peer agents are permitted in runtime orchestration.

## Non-Competition Contract

- The Onboarding & Preparation Agent can only execute preparation nodes.
- The Recovery & Execution Agent can only execute recovery/execution nodes.
- A typed handoff payload is required to move from preparation to recovery.
- The handoff gate is `readiness_score >= readiness_threshold` (default: `85.0`).
- Recovery agent execution is blocked while artist state is `preparing`.

## Decision Authority Matrix

| Action | Autonomous | Human Approval |
| --- | --- | --- |
| Read-only analysis and explanations | Yes | No |
| Catalog preparation and readiness scoring | Yes | No |
| Claim drafting and evidence assembly | Yes | No |
| Advance packet recommendation | Yes | No |
| Advance approval (analyst + executive) | No | Yes |
| Settlement acceptance / disbursement | No | Yes |
| Irreversible data deletion | No | Yes |

## Runtime Safety Controls

- Typed state schema with explicit `artist_status`, `active_agent`, and `handoff` channels.
- Reflection loop on low-confidence node output (< 0.85 confidence).
- Interrupt-safe boundaries for escalation/disbursement high-risk actions.
- Immutable trace events and evidence hash recording per critical node.
- Checkpointer-compatible orchestration for replay/recovery.

## Explainability Requirements

Every run must expose:

- Active agent and workflow phase
- Node-level confidence scores
- Handoff reason and readiness score
- Evidence references for major decisions
- Trace URL for dashboard and audit replay

## TV/Film Parity Requirements

Both governance and runtime controls apply to TV/Film workflows:

- Role taxonomy preparation in Agent 1
- TV/Film audits, bulk claims, and evidence export in Agent 2
- Same confidence/reflection and traceability guarantees as music workflows

## Compliance and Audit

- All run-level decisions are ledgered and queryable by run ID.
- Human overrides are stored with actor identity and timestamp.
- Weekly governance review checks:
	- cross-agent boundary violations
	- reflection escalation rates
	- confidence calibration drift
	- approval-gate bypass attempts (must be zero)
