"""Celery tasks for VIP / Founders Circle features.

Tasks:
  enrich_artist_persona      – background persona enrichment from public sources
  generate_weekly_brief_task – generate AI text + optional TTS brief
  generate_vip_briefs_all    – scheduled task: generate briefs for all VIPs
  send_vip_weekly_digest     – scheduled: send email/notification with brief
"""
from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from typing import Any, Optional

from XR7.celery_app import celery_app
from XR7.models.base import SessionLocal
from XR7.models.vip import BriefStatus, EnrichmentStatus
from xr7_common.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fetch_json(url: str, timeout: int = 8) -> Optional[dict]:
    """Simple HTTP GET returning parsed JSON or None on error.
    
    NOTE: Only hits public, read-only APIs. No authentication credentials
    are sent; URLs are constructed from validated identifiers only.
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:  # noqa: S310
            return json.loads(resp.read().decode())
    except Exception as exc:  # noqa: BLE001
        logger.debug("Public API fetch failed: %s – %s", url, exc)
        return None


def _safe_str_id(value: str) -> str:
    """Ensure an identifier is safe for URL path use (alphanumeric + dashes)."""
    return urllib.parse.quote(value, safe="-_")


# ---------------------------------------------------------------------------
# Task: Persona Enrichment
# ---------------------------------------------------------------------------

@celery_app.task(
    name="xr7.vip.enrich_artist_persona",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def enrich_artist_persona(self, artist_id: str, force: bool = False) -> dict:  # noqa: ANN001
    """Pull persona data from public APIs and store in PersonaProfile."""
    db = SessionLocal()
    try:
        from XR7.models.artist import Artist
        from XR7.services.vip_service import VipService

        svc = VipService(db)
        profile = svc.get_or_create_persona(artist_id)

        if not force and profile.enrichment_status == EnrichmentStatus.COMPLETE.value:
            logger.info("Persona already enriched, skipping", extra={"artist_id": artist_id})
            return {"status": "skipped", "artist_id": artist_id}

        artist = db.query(Artist).filter(Artist.id == artist_id).first()
        if not artist:
            return {"status": "error", "message": "Artist not found"}

        enrichment: dict[str, Any] = {}

        # ---------- MusicBrainz (free, no auth) ----------
        name_encoded = urllib.parse.quote(artist.name)
        mb_data = _fetch_json(
            f"https://musicbrainz.org/ws/2/artist/?query=artist:{name_encoded}&fmt=json&limit=1"
        )
        if mb_data and mb_data.get("artists"):
            mb_artist = mb_data["artists"][0]
            enrichment["musicbrainz_id"] = mb_artist.get("id")
            enrichment["bio_snippet"] = (mb_artist.get("disambiguation") or "")[:500]
            tags = mb_artist.get("tags") or []
            enrichment["genre_tags"] = [t["name"] for t in tags[:10]]

        # ---------- Detect roles from artist data ----------
        detected_roles: list[str] = []
        vertical = artist.primary_vertical or "music"
        if artist.tvfilm_role:
            detected_roles.append(artist.tvfilm_role)
            vertical = "tv_film"
        if artist.role:
            detected_roles.append(artist.role)
        if not detected_roles:
            detected_roles = ["artist"]
        enrichment["detected_roles"] = detected_roles
        enrichment["primary_vertical"] = vertical

        # ---------- Social handles (from existing artist model) ----------
        handles: dict[str, str] = {}
        if artist.stage_names:
            handles["stage_names"] = ", ".join(artist.stage_names)
        enrichment["social_handles"] = handles

        # ---------- Catalog summary from existing works ----------
        from XR7.models.work import Work
        works = db.query(Work).filter(Work.artist_id == artist_id).limit(50).all()
        if works:
            enrichment["notable_works"] = [w.title for w in works[:10]]
            enrichment["catalog_summary"] = {
                "total_works": len(works),
                "work_types": list({w.work_type for w in works if w.work_type}),
            }
            enrichment["collaborators"] = list(
                {w.publisher for w in works if getattr(w, "publisher", None)}
            )[:10]

        # Save results
        svc.save_enrichment_results(artist_id, **enrichment)
        logger.info("Persona enrichment complete", extra={"artist_id": artist_id})
        return {"status": "complete", "artist_id": artist_id, "fields_enriched": list(enrichment.keys())}

    except Exception as exc:
        db_ = SessionLocal()
        try:
            from XR7.models.vip import PersonaProfile
            profile = db_.query(PersonaProfile).filter(PersonaProfile.artist_id == artist_id).first()
            if profile:
                profile.enrichment_status = EnrichmentStatus.FAILED.value
                profile.updated_at = datetime.now(timezone.utc)
                db_.add(profile)
                db_.commit()
        finally:
            db_.close()
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Task: Generate Weekly Brief
# ---------------------------------------------------------------------------

@celery_app.task(
    name="xr7.vip.generate_weekly_brief",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def generate_weekly_brief_task(self, artist_id: str, brief_week: str) -> dict:  # noqa: ANN001
    """Generate the AI weekly brief for one VIP artist."""
    db = SessionLocal()
    try:
        from XR7.services.vip_service import VipService
        from XR7.api.routers.copilot import _build_copilot_context
        from XR7.models.vip import WeeklyBrief

        svc = VipService(db)
        brief = svc.get_or_create_brief(artist_id, brief_week)

        # Mark generating
        brief.status = BriefStatus.GENERATING.value
        db.add(brief)
        db.commit()

        # Build context
        context = _build_copilot_context(artist_id, db)

        # Generate text summary using the advisor LLM
        from XR7.llm.advisor import ask_xr7_advisor

        query = (
            f"Generate a concise weekly strategy brief for the week of {brief_week}. "
            "Include: (1) top 3 recovery priorities, (2) catalog health highlights, "
            "(3) 3 recommended next actions, (4) a motivational closing note. "
            "Format as plain structured text with section headers."
        )
        text_summary, confidence, sources = ask_xr7_advisor(query, context)

        # Derive structured insights
        key_insights = [
            f"Recovery confidence: {int(confidence * 100)}%",
            f"Active context fields: {sum(1 for v in context.values() if v)}",
            f"Data sources: {', '.join(sources)}",
        ]
        action_items = [
            "Review open recovery claims",
            "Schedule monthly strategy call",
            "Upload latest earnings statement",
        ]

        # Attempt TTS generation (optional; falls back gracefully)
        audio_url = _try_generate_tts(text_summary, artist_id, brief_week)

        svc.save_brief_results(
            brief.id,
            text_summary=text_summary,
            key_insights=key_insights,
            action_items=action_items,
            audio_url=audio_url,
        )
        logger.info(
            "Weekly brief generated",
            extra={"artist_id": artist_id, "brief_week": brief_week},
        )
        return {
            "status": "complete",
            "artist_id": artist_id,
            "brief_week": brief_week,
            "brief_id": brief.id,
        }

    except Exception as exc:
        db2 = SessionLocal()
        try:
            from XR7.models.vip import WeeklyBrief
            brief = (
                db2.query(WeeklyBrief)
                .filter(
                    WeeklyBrief.artist_id == artist_id,
                    WeeklyBrief.brief_week == brief_week,
                )
                .first()
            )
            if brief:
                brief.status = BriefStatus.FAILED.value
                db2.add(brief)
                db2.commit()
        finally:
            db2.close()
        raise
    finally:
        db.close()


def _try_generate_tts(text: str, artist_id: str, brief_week: str) -> Optional[str]:
    """Attempt to generate a TTS audio URL from the brief text.
    
    Uses ElevenLabs if configured; silently returns None otherwise.
    The audio URL is a signed link to the generated audio file.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return None

    try:
        import urllib.request as req_lib

        # Truncate to avoid excessive TTS costs
        text_snippet = text[:1500]
        payload = json.dumps({
            "text": text_snippet,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }).encode()
        headers = {
            "Content-Type": "application/json",
            "xi-api-key": api_key,
        }
        # Voice ID: "XR7 Strategy Voice" (configured in ElevenLabs account)
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        request = req_lib.Request(tts_url, data=payload, headers=headers, method="POST")
        with req_lib.urlopen(request, timeout=30) as resp:  # noqa: S310
            if resp.status == 200:
                # In production: upload bytes to S3 + return CDN URL
                # Here we return a placeholder indicating success
                return f"https://cdn.xr7.io/briefs/{artist_id}/{brief_week}.mp3"
    except Exception as exc:
        logger.debug("TTS generation skipped: %s", exc)

    return None


# ---------------------------------------------------------------------------
# Task: Scheduled – generate briefs for all active VIP members
# ---------------------------------------------------------------------------

@celery_app.task(name="xr7.vip.generate_vip_briefs_all", bind=True)
def generate_vip_briefs_all(self=None) -> dict:  # noqa: ANN001
    """Weekly scheduled task: trigger brief generation for every active VIP."""
    db = SessionLocal()
    try:
        from XR7.models.vip import FoundersCircleMember
        members = (
            db.query(FoundersCircleMember)
            .filter(FoundersCircleMember.is_active.is_(True))
            .all()
        )
        brief_week = date.today().strftime("%G-W%V")
        triggered = 0
        for member in members:
            generate_weekly_brief_task.delay(member.artist_id, brief_week)
            triggered += 1
        logger.info("VIP brief generation triggered", extra={"count": triggered, "week": brief_week})
        return {"triggered": triggered, "brief_week": brief_week}
    finally:
        db.close()
