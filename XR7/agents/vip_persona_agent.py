"""LangGraph node: VIP Persona Enrichment (Onboarding & Preparation Agent).

This node runs as part of the Onboarding & Preparation Agent pipeline.
It detects whether the artist is a VIP member and, if so:
  1. Dispatches a background persona enrichment task (non-blocking)
  2. Injects a personalised greeting + adaptive workflow hint into the state
  3. Determines adaptive UI mode (music vs tv_film) from detected roles

Node placement: after `first_claim_fast_track`, before `welcome_summary`.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from XR7.agents.two_agent_state import TwoAgentState, add_trace_event
from XR7.models.base import SessionLocal
from xr7_common.logging import get_logger

logger = get_logger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def VipPersonaEnrichmentNode(state: TwoAgentState) -> dict[str, Any]:
    """
    Onboarding-phase VIP persona detection and enrichment dispatch.

    Returns state patches only (never overwrites entire state).
    """
    artist_id = str(state.get("artist_id") or "")
    if not artist_id:
        return {}

    db = SessionLocal()
    try:
        from XR7.services.vip_service import VipService
        svc = VipService(db)
        membership = svc.get_membership(artist_id)

        if not membership:
            # Non-VIP artist: pass through cleanly
            return add_trace_event(
                state,
                node="vip_persona_enrichment",
                event="skipped",
                payload={"reason": "not_vip"},
            )

        # Check if persona needs enrichment
        profile = svc.get_persona(artist_id)
        needs_enrichment = (
            profile is None
            or profile.enrichment_status in ("pending", "failed")
        )

        job_id = None
        if needs_enrichment:
            try:
                from XR7.tasks.vip_tasks import enrich_artist_persona
                task = enrich_artist_persona.delay(artist_id, force=False)
                job_id = task.id
                svc.mark_enrichment_in_progress(artist_id, job_id)
                logger.info(
                    "VIP persona enrichment dispatched",
                    extra={"artist_id": artist_id, "job_id": job_id},
                )
            except Exception as exc:
                logger.warning(
                    "Could not dispatch VIP persona enrichment task",
                    extra={"artist_id": artist_id},
                    exc_info=exc,
                )

        # Build personalised greeting
        from XR7.models.artist import Artist
        artist = db.query(Artist).filter(Artist.id == artist_id).first()
        artist_name = artist.name if artist else "Creator"

        greeting = (
            f"Welcome back, {artist_name}. "
            "Your Founders Circle experience is active. "
            "Your XR7 Advisor, Legacy Map, and Concierge Inbox are ready."
        )

        # Determine adaptive UI mode from profile
        adaptive_mode = "music"
        if profile:
            list(profile.detected_roles or [])
            if profile.primary_vertical in ("tv_film", "both"):
                adaptive_mode = "tv_film"
        elif artist and artist.primary_vertical:
            adaptive_mode = "tv_film" if "film" in (artist.primary_vertical or "").lower() else "music"

        perks = list(membership.perks_unlocked or [])
        analyst_name = membership.concierge_analyst_name or "XR7 Strategy Team"

        patch: dict[str, Any] = {
            "vip_active": True,
            "vip_tier": membership.tier_level,
            "vip_perks": perks,
            "persona_greeting": greeting,
            "adaptive_ui_mode": adaptive_mode,
            "concierge_analyst_name": analyst_name,
            "concierge_calendly_link": membership.calendly_link,
            "agent_activity": [
                {
                    "step": "vip_persona_enrichment",
                    "status": "completed",
                    "decision": f"vip_detected tier={membership.tier_level}",
                    "confidence": 1.0,
                    "evidence_hash": None,
                }
            ],
        }
        if job_id:
            patch["persona_enrichment_job_id"] = job_id

        return {
            **add_trace_event(
                state,
                node="vip_persona_enrichment",
                event="completed",
                payload={
                    "tier": membership.tier_level,
                    "adaptive_mode": adaptive_mode,
                    "enrichment_dispatched": job_id is not None,
                },
            ),
            **patch,
        }

    except Exception as exc:
        logger.exception(
            "VipPersonaEnrichmentNode failed",
            extra={"artist_id": artist_id},
            exc_info=exc,
        )
        return add_trace_event(
            state,
            node="vip_persona_enrichment",
            event="error",
            payload={"error": str(exc)},
        )
    finally:
        db.close()
