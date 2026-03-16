# LangGraph Orchestrator

XR7 uses a typed graph state and a supervisor-driven execution model.

## State Model
State is defined in XR7/agents/state.py as XR7State and includes:
- Core recovery fields: anomalies, claims, evidence_hashes, negotiation_history, final_payout.
- Agent control fields: current_step, confidence_scores, next_action, pending_agent, retry_count.
- Onboarding fields: artist_intent, portal_guidance, catalog_profile, onboarding_progress, readiness_score, and related artifacts.

List fields use additive reducers for append-only semantics in graph transitions.

## Node Classes
- Existing core: DetectionAgent, EvidenceVerifierAgent, ClaimDrafterAgent, NegotiationAgent, EscalationAgent, DisbursementAgent, CalibrationAgent.
- Onboarding and enrichment: intent interpretation, portal navigation, upload fixing, catalog build, sync, explanations, expectations, split resolution, profile enrichment, summary, metadata registration, conflict detection, UGC collection, contract extraction, timeline, readiness, follow-up, persona adaptation.
- ReflectionNode: post-node critique and routing gate.

## Supervisor Routing
- If onboarding incomplete, route through onboarding sequence.
- If anomalies exist without a fast-track claim, prioritize FirstClaimFastTrackAgent.
- Route through recovery sequence for active claim lifecycle.
- Route to reflection when confidence drops below threshold.
- Route to human_review on escalation signals.

## Persistence + Resume
- Graph compile supports PostgresSaver when LANGGRAPH_CHECKPOINTER_URL is configured.
- checkpoint namespace: artist_{artist_id}
- thread id: artist-{artist_id}

## Safety Controls
- interrupt_before: escalation_agent, disbursement_agent
- max_steps: 100
- reflection-driven retry/escalation logic

## Traceability
- Execution events are streamed and retained in in-memory trace store for runtime visibility.
- API endpoint /artists/{id}/agent-trace/{run_id} exposes node events and state confidence.
