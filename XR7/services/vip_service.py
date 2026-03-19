"""VIP Founders Circle service — business logic layer.

Handles invite-code validation, membership creation, admin grants,
persona enrichment dispatch, concierge messaging, copilot queries,
referral management, and weekly brief generation.
"""
from __future__ import annotations

import hashlib
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from XR7.models.artist import Artist
from XR7.models.vip import (
    BriefStatus,
    ConciergeMessage,
    ConciergeMessageSender,
    CopilotQuery,
    EnrichmentStatus,
    FoundersCircleMember,
    PersonaProfile,
    ReferralStatus,
    VipInviteCode,
    VipReferral,
    VipTierLevel,
    WeeklyBrief,
)
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VIP_CODE_BYTES = 24          # 192-bit entropy → 32-char base64url
VIP_CODE_DEFAULT_TTL_DAYS = 30
VIP_REFERRAL_PERKS = {
    "referrer": "fee_discount_0_5pct",   # 0.5% contingency reduction (one-time)
    "referred": "priority_queue_access",
}
DEFAULT_VIP_DROPS: list[dict] = [
    {
        "title": "Legacy Map Beta",
        "description": "Interactive visual graph of all your connected works, credits, and earnings.",
        "available_since": "2026-03-19",
        "is_new": True,
        "feature_flag": "vip_legacy_map",
    },
    {
        "title": "Concierge Analyst Access",
        "description": "Direct messaging with your named XR7 strategy analyst.",
        "available_since": "2026-03-19",
        "is_new": True,
        "feature_flag": "vip_concierge_inbox",
    },
    {
        "title": "Weekly AI Voice Brief",
        "description": "Proactive audio summary of your recovery progress and next actions.",
        "available_since": "2026-03-19",
        "is_new": True,
        "feature_flag": "vip_weekly_brief",
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash_code(code: str) -> str:
    return hashlib.sha3_256(code.encode()).hexdigest()


def _generate_code() -> str:
    return secrets.token_urlsafe(VIP_CODE_BYTES)


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# VIP Membership
# ---------------------------------------------------------------------------

class VipService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Membership queries
    # ------------------------------------------------------------------

    def get_membership(self, artist_id: str) -> Optional[FoundersCircleMember]:
        return (
            self.db.query(FoundersCircleMember)
            .filter(
                and_(
                    FoundersCircleMember.artist_id == artist_id,
                    FoundersCircleMember.is_active.is_(True),
                )
            )
            .first()
        )

    def is_vip(self, artist_id: str) -> bool:
        return self.get_membership(artist_id) is not None

    def get_persona(self, artist_id: str) -> Optional[PersonaProfile]:
        return (
            self.db.query(PersonaProfile)
            .filter(PersonaProfile.artist_id == artist_id)
            .first()
        )

    # ------------------------------------------------------------------
    # Invite codes
    # ------------------------------------------------------------------

    def create_invite_code(
        self,
        *,
        tier_level: VipTierLevel = VipTierLevel.FOUNDERS_CIRCLE,
        created_by_admin_id: Optional[str] = None,
        created_by_artist_id: Optional[str] = None,
        expires_in_days: int = VIP_CODE_DEFAULT_TTL_DAYS,
        perk_bonus: Optional[str] = None,
    ) -> VipInviteCode:
        code = _generate_code()
        code_hash = _hash_code(code)
        expires_at = _now() + timedelta(days=expires_in_days)
        entry = VipInviteCode(
            code=code,
            code_hash=code_hash,
            tier_level=tier_level.value,
            created_by_admin_id=created_by_admin_id,
            created_by_artist_id=created_by_artist_id,
            expires_at=expires_at,
            perk_bonus=perk_bonus,
            created_at=_now(),
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        logger.info("VIP invite code created", extra={"id": entry.id, "tier": tier_level.value})
        return entry

    def _lookup_code(self, code: str) -> Optional[VipInviteCode]:
        code_hash = _hash_code(code)
        return (
            self.db.query(VipInviteCode)
            .filter(VipInviteCode.code_hash == code_hash)
            .first()
        )

    def claim_invite(self, artist_id: str, code: str) -> FoundersCircleMember:
        """Validate invite code, create membership, mark code used."""
        now = _now()

        invite = self._lookup_code(code)
        if invite is None:
            raise ValueError("Invalid invite code.")
        if invite.is_used or invite.use_count >= invite.max_uses:
            raise ValueError("Invite code has already been used.")
        if invite.expires_at and invite.expires_at.replace(tzinfo=timezone.utc) < now:
            raise ValueError("Invite code has expired.")

        # Prevent double membership
        existing = self.get_membership(artist_id)
        if existing:
            raise ValueError("Artist already has an active VIP membership.")

        # Validate artist exists
        artist = self.db.query(Artist).filter(Artist.id == artist_id).first()
        if not artist:
            raise ValueError("Artist not found.")

        membership = FoundersCircleMember(
            artist_id=artist_id,
            tier_level=invite.tier_level,
            invite_code_used=code[:8] + "****",   # store partial so we can trace without leaking
            granted_by_admin=False,
            activated_at=now,
            is_active=True,
            perks_unlocked=["founders_badge", "concierge_inbox", "weekly_brief", "legacy_map"],
            referral_slots_remaining=5,
            created_at=now,
            updated_at=now,
        )
        if invite.perk_bonus:
            membership.perks_unlocked = list(membership.perks_unlocked or []) + [invite.perk_bonus]

        # Mark code used
        invite.is_used = True if invite.max_uses == 1 else None
        invite.use_count = (invite.use_count or 0) + 1
        if invite.use_count >= invite.max_uses:
            invite.is_used = True
        invite.used_by_artist_id = artist_id
        invite.used_at = now

        self.db.add(membership)
        self.db.add(invite)
        self.db.commit()
        self.db.refresh(membership)
        logger.info("VIP membership activated", extra={"artist_id": artist_id, "tier": invite.tier_level})
        return membership

    # ------------------------------------------------------------------
    # Admin grant (bypasses invite code)
    # ------------------------------------------------------------------

    def admin_grant_vip(
        self,
        artist_id: str,
        *,
        tier_level: VipTierLevel = VipTierLevel.FOUNDERS_CIRCLE,
        admin_id: Optional[str] = None,
        concierge_analyst_name: Optional[str] = None,
        concierge_analyst_email: Optional[str] = None,
        calendly_link: Optional[str] = None,
    ) -> FoundersCircleMember:
        now = _now()
        existing = self.get_membership(artist_id)
        if existing:
            # Update existing membership
            existing.tier_level = tier_level.value
            existing.is_active = True
            existing.granted_by_admin = True
            existing.granted_by_admin_id = admin_id
            if concierge_analyst_name:
                existing.concierge_analyst_name = concierge_analyst_name
            if concierge_analyst_email:
                existing.concierge_analyst_email = concierge_analyst_email
            if calendly_link:
                existing.calendly_link = calendly_link
            existing.updated_at = now
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        artist = self.db.query(Artist).filter(Artist.id == artist_id).first()
        if not artist:
            raise ValueError("Artist not found.")

        membership = FoundersCircleMember(
            artist_id=artist_id,
            tier_level=tier_level.value,
            granted_by_admin=True,
            granted_by_admin_id=admin_id,
            activated_at=now,
            is_active=True,
            perks_unlocked=[
                "founders_badge",
                "concierge_inbox",
                "weekly_brief",
                "legacy_map",
                "priority_queue_access",
                "custom_branding",
            ],
            referral_slots_remaining=10,
            concierge_analyst_name=concierge_analyst_name,
            concierge_analyst_email=concierge_analyst_email,
            calendly_link=calendly_link,
            created_at=now,
            updated_at=now,
        )
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        logger.info(
            "Admin granted VIP membership",
            extra={"artist_id": artist_id, "admin_id": admin_id, "tier": tier_level.value},
        )
        return membership

    def revoke_vip(self, artist_id: str, admin_id: Optional[str] = None) -> bool:
        membership = self.get_membership(artist_id)
        if not membership:
            return False
        membership.is_active = False
        membership.updated_at = _now()
        self.db.add(membership)
        self.db.commit()
        logger.info("VIP membership revoked", extra={"artist_id": artist_id, "revoked_by": admin_id})
        return True

    # ------------------------------------------------------------------
    # Persona profiles
    # ------------------------------------------------------------------

    def get_or_create_persona(self, artist_id: str) -> PersonaProfile:
        profile = self.get_persona(artist_id)
        if profile:
            return profile
        now = _now()
        profile = PersonaProfile(
            artist_id=artist_id,
            enrichment_status=EnrichmentStatus.PENDING.value,
            created_at=now,
            updated_at=now,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def mark_enrichment_in_progress(self, artist_id: str, job_id: str) -> PersonaProfile:
        profile = self.get_or_create_persona(artist_id)
        profile.enrichment_status = EnrichmentStatus.IN_PROGRESS.value
        profile.enrichment_job_id = job_id
        profile.updated_at = _now()
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def save_enrichment_results(
        self,
        artist_id: str,
        *,
        imdb_id: Optional[str] = None,
        discogs_artist_id: Optional[str] = None,
        spotify_artist_id: Optional[str] = None,
        musicbrainz_id: Optional[str] = None,
        pro_credits: Optional[list] = None,
        social_handles: Optional[dict] = None,
        detected_roles: Optional[list] = None,
        primary_vertical: Optional[str] = None,
        catalog_summary: Optional[dict] = None,
        bio_snippet: Optional[str] = None,
        genre_tags: Optional[list] = None,
        notable_works: Optional[list] = None,
        collaborators: Optional[list] = None,
    ) -> PersonaProfile:
        profile = self.get_or_create_persona(artist_id)
        now = _now()
        if imdb_id is not None:
            profile.imdb_id = imdb_id
        if discogs_artist_id is not None:
            profile.discogs_artist_id = discogs_artist_id
        if spotify_artist_id is not None:
            profile.spotify_artist_id = spotify_artist_id
        if musicbrainz_id is not None:
            profile.musicbrainz_id = musicbrainz_id
        if pro_credits is not None:
            profile.pro_credits = pro_credits
        if social_handles is not None:
            profile.social_handles = social_handles
        if detected_roles is not None:
            profile.detected_roles = detected_roles
        if primary_vertical is not None:
            profile.primary_vertical = primary_vertical
        if catalog_summary is not None:
            profile.catalog_summary = catalog_summary
        if bio_snippet is not None:
            profile.bio_snippet = bio_snippet
        if genre_tags is not None:
            profile.genre_tags = genre_tags
        if notable_works is not None:
            profile.notable_works = notable_works
        if collaborators is not None:
            profile.collaborators = collaborators
        profile.enrichment_status = EnrichmentStatus.COMPLETE.value
        profile.enriched_at = now
        profile.updated_at = now
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    # ------------------------------------------------------------------
    # Concierge messaging
    # ------------------------------------------------------------------

    def get_messages(
        self,
        artist_id: str,
        *,
        limit: int = 50,
        thread_id: Optional[str] = None,
    ) -> list[ConciergeMessage]:
        q = self.db.query(ConciergeMessage).filter(ConciergeMessage.artist_id == artist_id)
        if thread_id:
            q = q.filter(ConciergeMessage.thread_id == thread_id)
        return q.order_by(ConciergeMessage.created_at.asc()).limit(limit).all()

    def send_message(
        self,
        artist_id: str,
        *,
        sender_type: ConciergeMessageSender,
        sender_name: str,
        message_body: str,
        analyst_id: Optional[str] = None,
        attachments: Optional[list] = None,
        request_human_analyst: bool = False,
        thread_id: Optional[str] = None,
    ) -> ConciergeMessage:
        now = _now()
        msg = ConciergeMessage(
            artist_id=artist_id,
            sender_type=sender_type.value,
            sender_name=sender_name,
            analyst_id=analyst_id,
            message_body=message_body,
            attachments=attachments,
            human_analyst_requested=request_human_analyst,
            thread_id=thread_id,
            created_at=now,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)

        if request_human_analyst:
            msg.escalated = True
            msg.escalated_at = now
            self.db.add(msg)
            self.db.commit()
            logger.info("Human analyst escalation requested", extra={"artist_id": artist_id})

        return msg

    def mark_messages_read(self, artist_id: str, message_ids: list[str]) -> int:
        now = _now()
        updated = 0
        for mid in message_ids:
            msg = (
                self.db.query(ConciergeMessage)
                .filter(
                    ConciergeMessage.id == mid,
                    ConciergeMessage.artist_id == artist_id,
                    ConciergeMessage.read_at.is_(None),
                )
                .first()
            )
            if msg:
                msg.read_at = now
                self.db.add(msg)
                updated += 1
        self.db.commit()
        return updated

    # ------------------------------------------------------------------
    # Referrals
    # ------------------------------------------------------------------

    def create_referral(
        self, referrer_artist_id: str, referred_email: str
    ) -> tuple[VipReferral, VipInviteCode]:
        membership = self.get_membership(referrer_artist_id)
        if not membership:
            raise ValueError("Referrer is not a VIP member.")
        if (membership.referral_slots_remaining or 0) <= 0:
            raise ValueError("No referral slots remaining.")

        # Generate a VIP invite code for referred party
        code_entry = self.create_invite_code(
            tier_level=VipTierLevel(membership.tier_level),
            created_by_artist_id=referrer_artist_id,
            perk_bonus=VIP_REFERRAL_PERKS["referred"],
        )

        referral = VipReferral(
            referrer_artist_id=referrer_artist_id,
            referred_email=referred_email,
            invite_code_id=code_entry.id,
            status=ReferralStatus.PENDING.value,
            perk_code_referrer=VIP_REFERRAL_PERKS["referrer"],
            perk_code_referred=VIP_REFERRAL_PERKS["referred"],
            created_at=_now(),
        )
        membership.referral_slots_remaining = max(0, (membership.referral_slots_remaining or 0) - 1)
        membership.updated_at = _now()
        self.db.add(referral)
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(referral)
        return referral, code_entry

    # ------------------------------------------------------------------
    # Weekly briefs
    # ------------------------------------------------------------------

    def get_or_create_brief(self, artist_id: str, brief_week: str) -> WeeklyBrief:
        brief = (
            self.db.query(WeeklyBrief)
            .filter(WeeklyBrief.artist_id == artist_id, WeeklyBrief.brief_week == brief_week)
            .first()
        )
        if brief:
            return brief
        brief = WeeklyBrief(
            artist_id=artist_id,
            brief_week=brief_week,
            status=BriefStatus.PENDING.value,
            created_at=_now(),
        )
        self.db.add(brief)
        self.db.commit()
        self.db.refresh(brief)
        return brief

    def save_brief_results(
        self,
        brief_id: str,
        *,
        text_summary: str,
        key_insights: list,
        action_items: list,
        audio_url: Optional[str] = None,
        video_url: Optional[str] = None,
    ) -> WeeklyBrief:
        brief = self.db.query(WeeklyBrief).filter(WeeklyBrief.id == brief_id).first()
        if not brief:
            raise ValueError("Brief not found.")
        brief.text_summary = text_summary
        brief.key_insights = key_insights
        brief.action_items = action_items
        brief.audio_url = audio_url
        brief.video_url = video_url
        brief.status = BriefStatus.COMPLETE.value
        brief.generated_at = _now()
        self.db.add(brief)
        self.db.commit()
        self.db.refresh(brief)
        return brief

    # ------------------------------------------------------------------
    # Copilot queries (storage side)
    # ------------------------------------------------------------------

    def record_copilot_query(
        self,
        artist_id: str,
        query_text: str,
        response_text: str,
        *,
        context_snapshot: Optional[dict] = None,
        confidence: float = 0.0,
        sources_cited: Optional[list] = None,
        latency_ms: int = 0,
    ) -> CopilotQuery:
        qr = CopilotQuery(
            artist_id=artist_id,
            query_text=query_text,
            response_text=response_text,
            context_snapshot=context_snapshot,
            confidence=confidence,
            sources_cited=sources_cited or [],
            latency_ms=latency_ms,
            created_at=_now(),
        )
        self.db.add(qr)
        self.db.commit()
        self.db.refresh(qr)
        return qr

    def feedback_copilot(self, query_id: str, artist_id: str, thumbs_up: bool) -> CopilotQuery:
        qr = (
            self.db.query(CopilotQuery)
            .filter(CopilotQuery.id == query_id, CopilotQuery.artist_id == artist_id)
            .first()
        )
        if not qr:
            raise ValueError("Query not found.")
        qr.thumbs_up = thumbs_up
        self.db.add(qr)
        self.db.commit()
        self.db.refresh(qr)
        return qr

    # ------------------------------------------------------------------
    # VIP Drop catalogue (static for now, extensible via feature flags)
    # ------------------------------------------------------------------

    def get_vip_drops(self) -> list[dict]:
        return DEFAULT_VIP_DROPS
