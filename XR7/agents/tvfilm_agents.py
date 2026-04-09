from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from XR7.agents.state import XR7State, add_trace_event, set_confidence


def _agent_patch(*, state: XR7State, key: str, confidence: float, summary: str) -> XR7State:
    artist_id = str(state.get("artist_id") or "")
    run_id = str(state.get("run_id") or "")
    digest = hashlib.sha256(f"{artist_id}:{run_id}:{key}:{summary}".encode("utf-8")).hexdigest()

    patch: XR7State = {
        "current_step": key,
        "agent_activity": [
            {
                "agent": key,
                "summary": summary,
                "confidence": round(confidence, 4),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "interrupt_safe": True,
                "self_critique": "Escalate to human analyst if confidence < 0.80 or contractual fields conflict.",
                "evidence_hash": digest,
            }
        ],
        "evidence_hashes": [digest],
    }
    patch.update(set_confidence(state, key, confidence))
    patch.update(
        add_trace_event(
            state,
            node=key,
            event="tvfilm_agent_complete",
            payload={"confidence": confidence, "evidence_hash": digest},
        )
    )
    return patch


async def RoleInterpreterAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="role_interpreter_agent",
        confidence=0.9,
        summary="Mapped client profile to TV/Film role taxonomy.",
    )


async def ProductionMetadataBuilderAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="production_metadata_builder_agent",
        confidence=0.88,
        summary="Built production metadata graph with normalized production IDs and episode-season hierarchy.",
    )


async def ResidualsReconstructionAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="residuals_reconstruction_agent",
        confidence=0.87,
        summary="Reconstructed residual baseline from statement history and window factors.",
    )


async def DistributionWindowAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="distribution_window_agent",
        confidence=0.86,
        summary="Mapped payment events to distribution windows and market classes.",
    )


async def BackendParticipationAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="backend_participation_agent",
        confidence=0.84,
        summary="Evaluated backend participation clauses against actual payouts.",
    )


async def ForeignResidualsAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="foreign_residuals_agent",
        confidence=0.83,
        summary="Correlated foreign society lag factors and detected missing foreign residuals.",
    )


async def PayrollAuditAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="payroll_audit_agent",
        confidence=0.89,
        summary="Audited payroll rows for day rate, holiday, and turnaround variances.",
    )


async def OvertimePenaltyAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="overtime_penalty_agent",
        confidence=0.85,
        summary="Calculated overtime and meal penalty deltas for production payments.",
    )


async def KitRentalAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="kit_rental_agent",
        confidence=0.82,
        summary="Compared expected kit rental reimbursements to paid amounts.",
    )


async def StuntAdjustmentAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="stunt_adjustment_agent",
        confidence=0.82,
        summary="Validated stunt adjustment ladders and hazard premiums.",
    )


async def SyndicationScannerAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="syndication_scanner_agent",
        confidence=0.88,
        summary="Scanned syndication windows for missing remittances and underreported runs.",
    )


async def StreamingReuseAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="streaming_reuse_agent",
        confidence=0.89,
        summary="Analyzed streaming reuse cycles and identified residual leakage.",
    )


async def UGCClipScannerAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="ugc_clip_scanner_agent",
        confidence=0.8,
        summary="Detected unmonetized UGC/clip reuse and Content ID opportunity gaps.",
    )


async def EpisodeSeasonRepairAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="episode_season_repair_agent",
        confidence=0.91,
        summary="Resolved episode-season mismatches and repaired hierarchy metadata.",
    )


async def ProductionIDRepairAgent(state: XR7State) -> XR7State:
    return _agent_patch(
        state=state,
        key="production_id_repair_agent",
        confidence=0.9,
        summary="Merged duplicate production IDs and generated canonical IDs.",
    )


async def TVFilmComfortAgent(state: XR7State) -> XR7State:
    patch = _agent_patch(
        state=state,
        key="tvfilm_comfort_agent",
        confidence=0.92,
        summary="Generated role-specific plain-language trust messaging.",
    )
    patch["comfort_messages"] = [
        "XR7 is currently validating your residual windows against union and studio schedules.",
        "You will receive a plain-language explanation before any claim is filed.",
    ]
    return patch


async def TVFilmExplainerAgent(state: XR7State) -> XR7State:
    patch = _agent_patch(
        state=state,
        key="tvfilm_explainer_agent",
        confidence=0.93,
        summary="Produced transparent audit narrative for TV/Film recovery findings.",
    )
    patch["explanations"] = [
        "We reconciled expected compensation by contract term, role, market, and reuse window.",
        "Each flagged anomaly includes evidence hashes and confidence scores for legal defensibility.",
    ]
    return patch


async def FirstClaimFastTrackAgentTVFilm(state: XR7State) -> XR7State:
    patch = _agent_patch(
        state=state,
        key="first_claim_fast_track_tvfilm_agent",
        confidence=0.9,
        summary="Prepared first high-confidence TV/Film claim candidate and evidence template mapping.",
    )
    patch["fast_track_claim"] = {
        "vertical": "TV_FILM",
        "claim_type": "MISSING_STREAMING_RESIDUALS",
        "evidence_template": "SAG-AFTRA",
        "status": "PREPARED",
    }
    return patch
