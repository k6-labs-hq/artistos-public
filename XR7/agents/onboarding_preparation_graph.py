from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Awaitable, Callable
from uuid import uuid4

from XR7.agents.onboarding_agents import (
    ArtistIntentInterpreterAgent,
    ArtistPersonaAdapterAgent,
    OnboardingWizardAgent,
    FileClassifierAgent,
    SmartUploadFixerAgent,
    CatalogAutoBuilderAgent,
    ArtistProfileEnricherAgent,
    AutoMetadataRegistrarAgent,
    RightsConflictDetectorAgent,
    SocialUGCCollectorAgent,
    AutoContractExtractorAgent,
    ReleaseTimelineAgent,
    ArtistReadinessScoreAgent,
    FirstClaimFastTrackAgent,
    WelcomeSummaryAgent,
    ReflectionNode,
)
from XR7.agents.tvfilm_agents import (
    RoleInterpreterAgent,
    ProductionMetadataBuilderAgent,
    EpisodeSeasonRepairAgent,
)
from XR7.agents.two_agent_state import TwoAgentState, add_trace_event, update_onboarding_progress


AgentFn = Callable[[TwoAgentState], Awaitable[dict[str, Any]]]


PREPARATION_NODE_ORDER: list[str] = [
    "artist_intent_interpreter",
    "artist_persona_adapter",
    "onboarding_wizard",
    "file_classifier",
    "smart_upload_fixer",
    "catalog_auto_builder",
    "artist_profile_enricher",
    "auto_metadata_registrar",
    "rights_conflict_detector",
    "social_ugc_collector",
    "auto_contract_extractor",
    "release_timeline",
    "role_interpreter_agent",
    "production_metadata_builder_agent",
    "episode_season_repair_agent",
    "artist_readiness_score",
    "first_claim_fast_track",
    "welcome_summary",
]

PREPARATION_NODE_MAP: dict[str, AgentFn] = {
    "artist_intent_interpreter": ArtistIntentInterpreterAgent,
    "artist_persona_adapter": ArtistPersonaAdapterAgent,
    "onboarding_wizard": OnboardingWizardAgent,
    "file_classifier": FileClassifierAgent,
    "smart_upload_fixer": SmartUploadFixerAgent,
    "catalog_auto_builder": CatalogAutoBuilderAgent,
    "artist_profile_enricher": ArtistProfileEnricherAgent,
    "auto_metadata_registrar": AutoMetadataRegistrarAgent,
    "rights_conflict_detector": RightsConflictDetectorAgent,
    "social_ugc_collector": SocialUGCCollectorAgent,
    "auto_contract_extractor": AutoContractExtractorAgent,
    "release_timeline": ReleaseTimelineAgent,
    "role_interpreter_agent": RoleInterpreterAgent,
    "production_metadata_builder_agent": ProductionMetadataBuilderAgent,
    "episode_season_repair_agent": EpisodeSeasonRepairAgent,
    "artist_readiness_score": ArtistReadinessScoreAgent,
    "first_claim_fast_track": FirstClaimFastTrackAgent,
    "welcome_summary": WelcomeSummaryAgent,
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
            "rights_conflicts",
            "ugc_opportunities",
            "release_timeline",
            "explanations",
            "comfort_messages",
            "registration_actions",
            "follow_up_actions",
        }:
            merged[key] = list(merged.get(key) or []) + list(value)
        elif isinstance(value, dict) and key in {
            "confidence_scores",
            "catalog_profile",
            "public_profile",
            "contract_terms",
            "onboarding_progress",
            "persona_profile",
            "prepared_state",
        }:
            merged[key] = {**(merged.get(key) or {}), **value}
        else:
            merged[key] = value
    return merged


def _node_confidence(state: TwoAgentState, node_name: str) -> float:
    return float((state.get("confidence_scores") or {}).get(node_name, 1.0) or 1.0)


async def run_onboarding_preparation_agent(state: TwoAgentState) -> TwoAgentState:
    if str(state.get("artist_status") or "preparing") != "preparing":
        return _merge(
            state,
            {
                "active_agent": "onboarding_preparation",
                "workflow_phase": "onboarding_preparation",
                "orchestrator_decision": "skip_preparation_non_preparing_state",
                **add_trace_event(
                    state,
                    node="onboarding_preparation_agent",
                    event="skipped",
                    payload={"artist_status": state.get("artist_status")},
                ),
            },
        )

    current = _merge(
        state,
        {
            "active_agent": "onboarding_preparation",
            "workflow_phase": "onboarding_preparation",
            **add_trace_event(state, node="onboarding_preparation_agent", event="start"),
        },
    )

    for node_name in PREPARATION_NODE_ORDER:
        node_fn = PREPARATION_NODE_MAP[node_name]
        patch = await node_fn(current)
        current = _merge(current, patch)
        current = _merge(
            current,
            add_trace_event(
                current,
                node="onboarding_preparation_agent",
                event="node_complete",
                payload={"node": node_name, "confidence": _node_confidence(current, node_name)},
            ),
        )

        # Confidence safety rail preserved from prior architecture.
        if _node_confidence(current, node_name) < 0.85:
            reflection_patch = await ReflectionNode(current)
            current = _merge(current, reflection_patch)
            current = _merge(
                current,
                add_trace_event(
                    current,
                    node="onboarding_preparation_agent",
                    event="reflection_complete",
                    payload={"node": node_name, "next_action": current.get("next_action")},
                ),
            )
            if str(current.get("next_action") or "proceed") == "retry_previous_node":
                retry_patch = await node_fn(current)
                current = _merge(current, retry_patch)

    readiness = float(current.get("readiness_score") or 0.0)
    threshold = float(current.get("readiness_threshold") or 85.0)
    explicit_handoff = str(current.get("handoff_trigger") or "").lower() in {"ready", "manual", "force"}
    ready = readiness >= threshold or explicit_handoff

    tvfilm_prep = {
        "role_interpreted": _node_confidence(current, "role_interpreter_agent") > 0,
        "production_metadata_prepared": _node_confidence(current, "production_metadata_builder_agent") > 0,
        "episode_hierarchy_repaired": _node_confidence(current, "episode_season_repair_agent") > 0,
    }

    if ready:
        handoff = {
            "handoff_id": str(uuid4()),
            "artist_id": str(current.get("artist_id") or ""),
            "from_agent": "onboarding_preparation",
            "to_agent": "recovery_execution",
            "readiness_score": readiness,
            "readiness_threshold": threshold,
            "catalog_profile": dict(current.get("catalog_profile") or {}),
            "public_profile": dict(current.get("public_profile") or {}),
            "onboarding_progress": dict(current.get("onboarding_progress") or {}),
            "contract_terms": dict(current.get("contract_terms") or {}),
            "rights_conflicts": list(current.get("rights_conflicts") or []),
            "release_timeline": list(current.get("release_timeline") or []),
            "persona_profile": dict(current.get("persona_profile") or {}),
            "tvfilm_preparation": tvfilm_prep,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        current = _merge(
            current,
            {
                "artist_status": "ready",
                "prepared_state": {
                    "catalog_profile": dict(current.get("catalog_profile") or {}),
                    "public_profile": dict(current.get("public_profile") or {}),
                    "readiness_score": readiness,
                    "onboarding_progress": dict(current.get("onboarding_progress") or {}),
                    "tvfilm_preparation": tvfilm_prep,
                },
                "handoff": handoff,
                "handoff_history": list(current.get("handoff_history") or []) + [handoff],
                "orchestrator_decision": "handoff_to_recovery_execution",
                **update_onboarding_progress(current, completed_step="catalog"),
                **add_trace_event(
                    current,
                    node="onboarding_preparation_agent",
                    event="handoff_ready",
                    payload={"readiness_score": readiness, "threshold": threshold},
                ),
            },
        )
    else:
        current = _merge(
            current,
            {
                "artist_status": "preparing",
                "orchestrator_decision": "remain_in_preparation",
                **add_trace_event(
                    current,
                    node="onboarding_preparation_agent",
                    event="incomplete",
                    payload={"readiness_score": readiness, "threshold": threshold},
                ),
            },
        )

    return current
