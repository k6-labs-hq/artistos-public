from __future__ import annotations

import asyncio
import importlib
import os
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable
from uuid import uuid4

from XR7.agents.onboarding_agents import (
    AttorneyExportAgent,
    ArtistComfortAgent,
    ArtistExplainerAgent,
    ArtistIntentInterpreterAgent,
    ArtistPersonaAdapterAgent,
    ArtistProfileEnricherAgent,
    ArtistReadinessScoreAgent,
    AutoContractExtractorAgent,
    AutoFollowUpAgent,
    AutoMetadataRegistrarAgent,
    AutoSplitResolverAgent,
    AutoTermsAcceptorAgent,
    CalibrationAgent,
    CatalogAutoBuilderAgent,
    ClaimDrafterAgent,
    ClaimEscalationAgent,
    ClaimOutcomeForecasterAgent,
    DetectionAgent,
    DistributorSyncAgent,
    DisbursementAgent,
    EarningsExpectationAgent,
    EvidenceNarrativeAgent,
    EscalationAgent,
    EvidenceVerifierAgent,
    FileClassifierAgent,
    FirstClaimFastTrackAgent,
    InitialScanOrchestratorAgent,
    LegalAuthorityAgent,
    LegalCounselPrepAgent,
    LegalRiskScoringAgent,
    MissingStatementHunterAgent,
    NegotiationAgent,
    NegotiationToneAdapterAgent,
    OnboardingWizardAgent,
    PayerBehaviorPredictionAgent,
    PortalAutoNavigatorAgent,
    PROPortalGuideAgent,
    ReflectionNode,
    ReleaseTimelineAgent,
    RightsConflictDetectorAgent,
    SocialUGCCollectorAgent,
    SmartUploadFixerAgent,
    WelcomeSummaryAgent,
)
from XR7.agents.state import XR7State, add_trace_event, initial_state
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# Runtime stores for dashboard status and trace replay.
_RUN_STATE: dict[str, XR7State] = {}
_RUN_TRACE: dict[str, list[dict[str, Any]]] = {}
_ARTIST_LATEST_RUN: dict[str, str] = {}

# Optional LangGraph runtime.
try:
    _graph_mod = importlib.import_module("langgraph.graph")
    StateGraph = getattr(_graph_mod, "StateGraph")
    START = getattr(_graph_mod, "START")
    END = getattr(_graph_mod, "END")
    _types_mod = importlib.import_module("langgraph.types")
    Send = getattr(_types_mod, "Send")
    _cp_mod = importlib.import_module("langgraph.checkpoint.postgres")
    PostgresSaver = getattr(_cp_mod, "PostgresSaver")
    LANGGRAPH_AVAILABLE = True
except Exception:  # noqa: BLE001
    StateGraph = None
    START = "__start__"
    END = "__end__"
    Send = None
    PostgresSaver = None
    LANGGRAPH_AVAILABLE = False


AgentFn = Callable[[XR7State], Awaitable[XR7State]]


AGENTS: dict[str, AgentFn] = {
    "artist_intent_interpreter": ArtistIntentInterpreterAgent,
    "artist_persona_adapter": ArtistPersonaAdapterAgent,
    "onboarding_wizard": OnboardingWizardAgent,
    "auto_terms_acceptor": AutoTermsAcceptorAgent,
    "file_classifier": FileClassifierAgent,
    "smart_upload_fixer": SmartUploadFixerAgent,
    "catalog_auto_builder": CatalogAutoBuilderAgent,
    "portal_auto_navigator": PortalAutoNavigatorAgent,
    "pro_portal_guide": PROPortalGuideAgent,
    "missing_statement_hunter": MissingStatementHunterAgent,
    "distributor_sync": DistributorSyncAgent,
    "artist_explainer": ArtistExplainerAgent,
    "earnings_expectation": EarningsExpectationAgent,
    "auto_split_resolver": AutoSplitResolverAgent,
    "artist_comfort": ArtistComfortAgent,
    "artist_profile_enricher": ArtistProfileEnricherAgent,
    "auto_metadata_registrar": AutoMetadataRegistrarAgent,
    "rights_conflict_detector": RightsConflictDetectorAgent,
    "social_ugc_collector": SocialUGCCollectorAgent,
    "auto_contract_extractor": AutoContractExtractorAgent,
    "release_timeline": ReleaseTimelineAgent,
    "artist_readiness_score": ArtistReadinessScoreAgent,
    "auto_follow_up": AutoFollowUpAgent,
    "initial_scan_orchestrator": InitialScanOrchestratorAgent,
    "first_claim_fast_track": FirstClaimFastTrackAgent,
    "welcome_summary": WelcomeSummaryAgent,
    "detection_agent": DetectionAgent,
    "evidence_verifier": EvidenceVerifierAgent,
    "claim_drafter": ClaimDrafterAgent,
    "legal_authority_agent": LegalAuthorityAgent,
    "legal_risk_scoring_agent": LegalRiskScoringAgent,
    "payer_behavior_prediction_agent": PayerBehaviorPredictionAgent,
    "negotiation_tone_adapter_agent": NegotiationToneAdapterAgent,
    "claim_outcome_forecaster_agent": ClaimOutcomeForecasterAgent,
    "evidence_narrative_agent": EvidenceNarrativeAgent,
    "legal_counsel_prep_agent": LegalCounselPrepAgent,
    "claim_escalation_agent": ClaimEscalationAgent,
    "attorney_export_agent": AttorneyExportAgent,
    "negotiation_agent": NegotiationAgent,
    "escalation_agent": EscalationAgent,
    "disbursement_agent": DisbursementAgent,
    "calibration_agent": CalibrationAgent,
    "reflection": ReflectionNode,
}


ONBOARDING_ORDER: list[str] = [
    "artist_intent_interpreter",
    "artist_persona_adapter",
    "onboarding_wizard",
    "auto_terms_acceptor",
    "file_classifier",
    "smart_upload_fixer",
    "catalog_auto_builder",
    "portal_auto_navigator",
    "pro_portal_guide",
    "missing_statement_hunter",
    "distributor_sync",
    "artist_explainer",
    "earnings_expectation",
    "auto_split_resolver",
    "artist_comfort",
    "artist_profile_enricher",
    "auto_metadata_registrar",
    "rights_conflict_detector",
    "social_ugc_collector",
    "auto_contract_extractor",
    "release_timeline",
    "artist_readiness_score",
    "auto_follow_up",
    "initial_scan_orchestrator",
    "first_claim_fast_track",
    "welcome_summary",
]

RECOVERY_ORDER: list[str] = [
    "detection_agent",
    "evidence_verifier",
    "claim_drafter",
    "legal_authority_agent",
    "legal_risk_scoring_agent",
    "payer_behavior_prediction_agent",
    "negotiation_tone_adapter_agent",
    "claim_outcome_forecaster_agent",
    "evidence_narrative_agent",
    "legal_counsel_prep_agent",
    "claim_escalation_agent",
    "attorney_export_agent",
    "negotiation_agent",
    "escalation_agent",
    "disbursement_agent",
    "calibration_agent",
]

REFLECTION_AFTER = {
    "smart_upload_fixer",
    "catalog_auto_builder",
    "first_claim_fast_track",
    "auto_metadata_registrar",
    "legal_authority_agent",
    "legal_risk_scoring_agent",
    "payer_behavior_prediction_agent",
    "negotiation_tone_adapter_agent",
    "claim_outcome_forecaster_agent",
    "evidence_narrative_agent",
    "legal_counsel_prep_agent",
    "claim_escalation_agent",
    "attorney_export_agent",
}


def _merge_state(base: XR7State, patch: XR7State) -> XR7State:
    merged: XR7State = dict(base)
    for key, value in patch.items():
        if key in {
            "anomalies",
            "claims",
            "evidence_hashes",
            "negotiation_history",
            "error_log",
            "portal_guidance",
            "fixed_files",
            "upload_errors",
            "explanations",
            "split_conflicts",
            "split_suggestions",
            "comfort_messages",
            "registration_actions",
            "rights_conflicts",
            "ugc_opportunities",
            "release_timeline",
            "follow_up_actions",
            "agent_activity",
            "trace",
            "reflection_suggestions",
            "legal_authority_sections",
            "legal_compliance_statements",
            "adapted_messages",
            "recommended_packet_emphasis",
            "attorney_exhibits_index",
            "narrative_highlights",
        } and isinstance(value, list):
            merged[key] = list(merged.get(key) or []) + list(value)
        elif key == "confidence_scores" and isinstance(value, dict):
            merged[key] = {**(merged.get(key) or {}), **value}
        elif key == "onboarding_progress" and isinstance(value, dict):
            merged[key] = {**(merged.get(key) or {}), **value}
        elif key in {
            "catalog_profile",
            "expected_earnings",
            "public_profile",
            "contract_terms",
            "distributor_sync_status",
            "persona_profile",
            "legal_structured_packet",
            "legal_appendix",
            "escalation_prepared_packet",
            "negotiation_tone_profile",
            "payer_behavior_profile",
            "attorney_briefing_packet",
            "attorney_case_file",
            "attorney_packet_metadata",
            "narrative_sections",
            "attorney_export_package",
            "attorney_export_manifest",
        } and isinstance(value, dict):
            merged[key] = {**(merged.get(key) or {}), **value}
        else:
            merged[key] = value
    return merged


def get_latest_artist_state(artist_id: str) -> XR7State | None:
    run_id = _ARTIST_LATEST_RUN.get(artist_id)
    if not run_id:
        return None
    return _RUN_STATE.get(run_id)


def get_run_trace(artist_id: str, run_id: str) -> dict[str, Any]:
    state = _RUN_STATE.get(run_id)
    if not state or str(state.get("artist_id")) != artist_id:
        return {
            "artist_id": artist_id,
            "run_id": run_id,
            "found": False,
            "events": [],
        }
    return {
        "artist_id": artist_id,
        "run_id": run_id,
        "found": True,
        "events": _RUN_TRACE.get(run_id, []),
        "current_step": state.get("current_step"),
        "confidence_scores": state.get("confidence_scores", {}),
    }


def _should_reflect(state: XR7State, node_name: str) -> bool:
    conf = float((state.get("confidence_scores") or {}).get(node_name, 1.0) or 1.0)
    return node_name in REFLECTION_AFTER and conf < 0.85


def _supervisor_next(state: XR7State) -> str:
    if state.get("next_action") == "human_review":
        return END
    if state.get("next_action") == "reflection":
        return "reflection"

    progress = dict(state.get("onboarding_progress") or {})
    completed = bool(progress.get("completed"))
    current = str(state.get("current_step") or "")

    if not completed:
        for node in ONBOARDING_ORDER:
            if node == current:
                continue
            conf = float((state.get("confidence_scores") or {}).get(node, 0.0) or 0.0)
            if conf == 0.0:
                return node
        return "initial_scan_orchestrator"

    if not state.get("fast_track_claim") and (state.get("anomalies") or []):
        return "first_claim_fast_track"

    # Legal authority must run when evidence exists, when negotiation is active,
    # or when an export flow was requested.
    legal_done = float((state.get("confidence_scores") or {}).get("legal_authority_agent", 0.0) or 0.0) > 0.0
    has_evidence_packet = bool(state.get("evidence_hashes") or state.get("legal_structured_packet"))
    entering_negotiation = bool(state.get("negotiation_history") or state.get("negotiation_tone_profile"))
    export_requested = bool(state.get("export_requested"))
    if not legal_done and (has_evidence_packet or entering_negotiation or export_requested):
        return "legal_authority_agent"

    if current in RECOVERY_ORDER:
        idx = RECOVERY_ORDER.index(current)
        return END if idx == len(RECOVERY_ORDER) - 1 else RECOVERY_ORDER[idx + 1]

    return RECOVERY_ORDER[0]


async def _run_node(state: XR7State, node_name: str) -> XR7State:
    fn = AGENTS[node_name]
    out = await fn(state)
    merged = _merge_state(state, out)
    merged = _merge_state(
        merged,
        add_trace_event(
            merged,
            node=node_name,
            event="node_complete",
            payload={
                "confidence": (merged.get("confidence_scores") or {}).get(node_name),
                "next_action": merged.get("next_action", "proceed"),
            },
        ),
    )
    if _should_reflect(merged, node_name):
        merged["next_action"] = "reflection"
        merged["pending_agent"] = node_name
    else:
        if node_name != "reflection" and merged.get("next_action") != "reflection":
            merged["next_action"] = "proceed"
    return merged


async def _fallback_execute(initial: XR7State) -> XR7State:
    state = dict(initial)
    max_steps = 100
    for _ in range(max_steps):
        nxt = _supervisor_next(state)
        if nxt == END:
            break
        state = await _run_node(state, nxt)
        if nxt == "reflection":
            action = str(state.get("next_action") or "proceed")
            pending = str(state.get("pending_agent") or "")
            if action == "retry_previous_node" and pending in AGENTS:
                state = await _run_node(state, pending)
                state["next_action"] = "proceed"
            elif action in {"escalate_to_human", "escalate_to_escalation_agent", "human_review"}:
                state["next_action"] = "human_review"
                break
    return state


def _build_graph():
    if not LANGGRAPH_AVAILABLE:
        return None

    builder = StateGraph(XR7State)

    async def supervisor_node(state: XR7State) -> XR7State:
        nxt = _supervisor_next(state)
        return {
            "current_step": "supervisor",
            "next_action": "stop" if nxt == END else "proceed",
            "pending_agent": None,
            "trace": [
                {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "node": "supervisor",
                    "event": "route",
                    "payload": {"next": nxt},
                }
            ],
        }

    builder.add_node("supervisor", supervisor_node)
    for name in AGENTS:
        builder.add_node(name, AGENTS[name])

    builder.add_edge(START, "supervisor")

    def route_from_supervisor(state: XR7State):
        nxt = _supervisor_next(state)
        if nxt == END:
            return END
        if nxt == "claim_drafter" and len(state.get("anomalies") or []) > 3 and Send is not None:
            sends = []
            for anomaly in (state.get("anomalies") or [])[:5]:
                sends.append(Send("claim_drafter", {**state, "anomalies": [anomaly]}))
            return sends
        return nxt

    builder.add_conditional_edges("supervisor", route_from_supervisor)

    for node in AGENTS:
        if node == "reflection":
            def _reflection_route(state: XR7State) -> str:
                action = str(state.get("next_action") or "proceed")
                if action == "retry_previous_node":
                    pending = str(state.get("pending_agent") or "")
                    return pending if pending in AGENTS else "supervisor"
                if action in {"escalate_to_human", "escalate_to_escalation_agent", "human_review"}:
                    return END
                return "supervisor"

            builder.add_conditional_edges("reflection", _reflection_route)
        else:
            builder.add_edge(node, "supervisor")

    checkpointer = None
    if PostgresSaver is not None:
        try:
            url = os.environ.get("LANGGRAPH_CHECKPOINTER_URL") or os.environ.get("DATABASE_URL")
            if url:
                checkpointer = PostgresSaver.from_conn_string(url)
        except Exception:  # noqa: BLE001
            logger.exception("Failed to initialize PostgresSaver; proceeding without checkpointer")

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["escalation_agent", "disbursement_agent"],
        max_steps=100,
    )


xr7_recovery_orchestra = _build_graph()


async def run_xr7_recovery_orchestra(artist_id: str, run_id: str | None = None) -> XR7State:
    rid = run_id or str(uuid4())
    state = initial_state(artist_id, rid)
    _RUN_STATE[rid] = state
    _ARTIST_LATEST_RUN[artist_id] = rid
    _RUN_TRACE[rid] = []

    if xr7_recovery_orchestra is None:
        final_state = await _fallback_execute(state)
    else:
        cfg = {"configurable": {"thread_id": f"artist-{artist_id}", "checkpoint_ns": f"artist_{artist_id}"}}
        final_state = dict(state)
        try:
            async for evt in xr7_recovery_orchestra.astream_events(state, config=cfg, version="v2"):
                _RUN_TRACE[rid].append(dict(evt))
                if "data" in evt and isinstance(evt["data"], dict):
                    maybe_state = evt["data"].get("output") or evt["data"].get("state")
                    if isinstance(maybe_state, dict):
                        final_state = _merge_state(final_state, maybe_state)
            if not final_state.get("current_step"):
                final_state = await _fallback_execute(state)
        except Exception:  # noqa: BLE001
            logger.exception("LangGraph execution failed; switching to fallback path", extra={"artist_id": artist_id, "run_id": rid})
            final_state = await _fallback_execute(state)

    _RUN_STATE[rid] = final_state
    if rid not in _RUN_TRACE:
        _RUN_TRACE[rid] = []
    return final_state


async def run_export_prep_pipeline(artist_id: str, run_id: str | None = None) -> XR7State:
    rid = run_id or _ARTIST_LATEST_RUN.get(artist_id) or str(uuid4())
    state = dict(_RUN_STATE.get(rid) or initial_state(artist_id, rid))
    state["export_requested"] = True

    ordered = [
        "evidence_verifier",
        "claim_drafter",
        "legal_authority_agent",
        "legal_risk_scoring_agent",
        "payer_behavior_prediction_agent",
        "negotiation_tone_adapter_agent",
        "claim_outcome_forecaster_agent",
        "evidence_narrative_agent",
        "legal_counsel_prep_agent",
        "claim_escalation_agent",
        "attorney_export_agent",
    ]
    for node in ordered:
        state = await _run_node(state, node)
        if state.get("next_action") == "reflection":
            state = await _run_node(state, "reflection")
            action = str(state.get("next_action") or "proceed")
            pending = str(state.get("pending_agent") or "")
            if action == "retry_previous_node" and pending in AGENTS:
                state = await _run_node(state, pending)

    _RUN_STATE[rid] = state
    _ARTIST_LATEST_RUN[artist_id] = rid
    _RUN_TRACE.setdefault(rid, [])
    return state


def run_xr7_recovery_orchestra_sync(artist_id: str, run_id: str | None = None) -> XR7State:
    return asyncio.run(run_xr7_recovery_orchestra(artist_id, run_id))


def run_export_prep_pipeline_sync(artist_id: str, run_id: str | None = None) -> XR7State:
    return asyncio.run(run_export_prep_pipeline(artist_id, run_id))
