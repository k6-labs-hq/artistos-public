from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from XR7.agents.advance_recovery_agents import AdvanceRecoveryPacketAgent
from XR7.agents.onboarding_agents import (
    ArtistComfortAgent,
    ArtistExplainerAgent,
    AutoFollowUpAgent,
    AutoSplitResolverAgent,
    BlackBoxExpirationAgent,
    ClaimDrafterAgent,
    ClaimOutcomeForecasterAgent,
    ContractRecoverabilityAgent,
    DetectionAgent,
    DisbursementAgent,
    DiscoveryRuleAgent,
    DistributorSyncAgent,
    EarningsExpectationAgent,
    EvidencePackageAgent,
    LeakageBenchmarkAgent,
    LegalAuthorityAgent,
    LegalRiskScoringAgent,
    NegotiationToneAdapterAgent,
    PortalAutoNavigatorAgent,
    RecoverabilityClassificationAgent,
    RecoverabilityExplainerAgent,
    ReflectionNode,
    SocietySignalAgent,
)
from XR7.agents.tvfilm_agents import (
    BackendParticipationAgent,
    DistributionWindowAgent,
    ForeignResidualsAgent,
    PayrollAuditAgent,
    StreamingReuseAgent,
    SyndicationScannerAgent,
    TVFilmComfortAgent,
    TVFilmExplainerAgent,
    UGCClipScannerAgent,
)
from XR7.agents.two_agent_state import TwoAgentState, add_trace_event

AgentFn = Callable[[TwoAgentState], Awaitable[dict[str, Any]]]


RECOVERY_NODE_ORDER: list[str] = [
    "portal_auto_navigator",
    "distributor_sync",
    "artist_explainer",
    "earnings_expectation",
    "auto_split_resolver",
    "artist_comfort",
    "detection_agent",
    "black_box_expiration_agent",
    "recoverability_classification_agent",
    "recoverability_explainer_agent",
    "discovery_rule_agent",
    "contract_recoverability_agent",
    "leakage_benchmark_agent",
    "society_signal_agent",
    "auto_evidence_builder",
    "claim_drafter",
    "auto_advance_evaluator",
    "advance_recovery_orchestrator",
    "rights_registration_agent",
    "auto_payer_chaser",
    "auto_settlement_tracker",
    "auto_sol_guardian",
    "auto_follow_up",
    "distribution_window_agent",
    "backend_participation_agent",
    "foreign_residuals_agent",
    "payroll_audit_agent",
    "syndication_scanner_agent",
    "streaming_reuse_agent",
    "ugc_clip_scanner_agent",
    "tvfilm_explainer_agent",
    "tvfilm_comfort_agent",
]

RECOVERY_NODE_MAP: dict[str, AgentFn] = {
    "portal_auto_navigator": PortalAutoNavigatorAgent,
    "distributor_sync": DistributorSyncAgent,
    "artist_explainer": ArtistExplainerAgent,
    "earnings_expectation": EarningsExpectationAgent,
    "auto_split_resolver": AutoSplitResolverAgent,
    "artist_comfort": ArtistComfortAgent,
    "detection_agent": DetectionAgent,
    "black_box_expiration_agent": BlackBoxExpirationAgent,
    "recoverability_classification_agent": RecoverabilityClassificationAgent,
    "recoverability_explainer_agent": RecoverabilityExplainerAgent,
    "discovery_rule_agent": DiscoveryRuleAgent,
    "contract_recoverability_agent": ContractRecoverabilityAgent,
    "leakage_benchmark_agent": LeakageBenchmarkAgent,
    "society_signal_agent": SocietySignalAgent,
    "auto_evidence_builder": EvidencePackageAgent,
    "claim_drafter": ClaimDrafterAgent,
    "auto_advance_evaluator": ClaimOutcomeForecasterAgent,
    "advance_recovery_orchestrator": AdvanceRecoveryPacketAgent,
    "rights_registration_agent": LegalAuthorityAgent,
    "auto_payer_chaser": NegotiationToneAdapterAgent,
    "auto_settlement_tracker": DisbursementAgent,
    "auto_sol_guardian": LegalRiskScoringAgent,
    "auto_follow_up": AutoFollowUpAgent,
    "distribution_window_agent": DistributionWindowAgent,
    "backend_participation_agent": BackendParticipationAgent,
    "foreign_residuals_agent": ForeignResidualsAgent,
    "payroll_audit_agent": PayrollAuditAgent,
    "syndication_scanner_agent": SyndicationScannerAgent,
    "streaming_reuse_agent": StreamingReuseAgent,
    "ugc_clip_scanner_agent": UGCClipScannerAgent,
    "tvfilm_explainer_agent": TVFilmExplainerAgent,
    "tvfilm_comfort_agent": TVFilmComfortAgent,
}


def _merge(base: TwoAgentState, patch: dict[str, Any]) -> TwoAgentState:
    merged: TwoAgentState = dict(base)
    for key, value in patch.items():
        if isinstance(value, list) and key in {
            "anomalies",
            "claims",
            "evidence_hashes",
            "error_log",
            "agent_activity",
            "trace",
            "explanations",
            "comfort_messages",
            "follow_up_actions",
            "negotiation_history",
        }:
            merged[key] = list(merged.get(key) or []) + list(value)
        elif isinstance(value, dict) and key in {
            "confidence_scores",
            "distributor_sync_status",
            "expected_earnings",
            "recovery_execution_state",
            "escalation_prepared_packet",
            "claims_evidence_package",
            "recoverability_explainer",
            "society_signal_updates",
        }:
            merged[key] = {**(merged.get(key) or {}), **value}
        else:
            merged[key] = value
    return merged


def _node_confidence(state: TwoAgentState, node_name: str) -> float:
    return float((state.get("confidence_scores") or {}).get(node_name, 1.0) or 1.0)


async def _run_recovery_node(state: TwoAgentState, node_name: str) -> TwoAgentState:
    fn = RECOVERY_NODE_MAP[node_name]
    patch = await fn(state)
    out = _merge(state, patch)

    # Preserve confidence-triggered reflection loop.
    if _node_confidence(out, node_name) < 0.85:
        reflection_patch = await ReflectionNode(out)
        out = _merge(out, reflection_patch)
        if str(out.get("next_action") or "proceed") == "retry_previous_node":
            retry_patch = await fn(out)
            out = _merge(out, retry_patch)

    out = _merge(
        out,
        add_trace_event(
            out,
            node="recovery_execution_agent",
            event="node_complete",
            payload={"node": node_name, "confidence": _node_confidence(out, node_name)},
        ),
    )
    return out


async def run_recovery_execution_agent(state: TwoAgentState) -> TwoAgentState:
    artist_status = str(state.get("artist_status") or "preparing").lower()
    if artist_status not in {"ready", "active"}:
        return _merge(
            state,
            {
                "active_agent": "recovery_execution",
                "workflow_phase": "recovery_execution",
                "orchestrator_decision": "skip_recovery_not_ready",
                **add_trace_event(
                    state,
                    node="recovery_execution_agent",
                    event="skipped",
                    payload={"artist_status": state.get("artist_status")},
                ),
            },
        )

    current = _merge(
        state,
        {
            "active_agent": "recovery_execution",
            "workflow_phase": "recovery_execution",
            "artist_status": "active",
            **add_trace_event(state, node="recovery_execution_agent", event="start"),
        },
    )

    if current.get("handoff"):
        current = _merge(
            current,
            {
                "recovery_execution_state": {
                    "handoff_id": (current.get("handoff") or {}).get("handoff_id"),
                    "received_at": datetime.now(timezone.utc).isoformat(),
                    "catalog_profile": (current.get("handoff") or {}).get("catalog_profile") or {},
                    "readiness_score": (current.get("handoff") or {}).get("readiness_score") or current.get("readiness_score"),
                }
            },
        )

    for node_name in RECOVERY_NODE_ORDER:
        current = await _run_recovery_node(current, node_name)

    current = _merge(
        current,
        {
            "artist_status": "active",
            "orchestrator_decision": "recovery_execution_complete",
            **add_trace_event(current, node="recovery_execution_agent", event="complete"),
        },
    )
    return current
