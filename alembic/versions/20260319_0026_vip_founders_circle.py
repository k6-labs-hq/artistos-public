"""VIP Founders Circle: invite-only premier experience tables.

Revision ID: 20260319_0026_vip_founders_circle
Revises: 20260319_0025_agent_handoffs
Create Date: 2026-03-19 12:00:00.000000

New tables:
  founders_circle_members  – membership record per artist
  vip_invite_codes         – admin/referral-generated invite codes
  persona_profiles         – public-source persona enrichment
  concierge_messages       – in-app analyst ↔ artist messaging
  vip_referrals            – VIP peer-referral programme
  weekly_briefs            – AI-generated weekly strategy briefs
  copilot_queries          – copilot Q&A audit trail
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260319_0026"
down_revision = "20260319_0025"
branch_labels = None
depends_on = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        return name in insp.get_table_names()
    except Exception:  # noqa: BLE001
        return False


def _index_exists(table: str, index: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        return any(i.get("name") == index for i in insp.get_indexes(table))
    except Exception:  # noqa: BLE001
        return False


def upgrade() -> None:
    # ------------------------------------------------------------------
    # founders_circle_members
    # ------------------------------------------------------------------
    if not _table_exists("founders_circle_members"):
        op.create_table(
            "founders_circle_members",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("artist_id", sa.String(36), nullable=False),
            sa.Column("tier_level", sa.String(32), nullable=False, server_default="FOUNDERS_CIRCLE"),
            sa.Column("invite_code_used", sa.String(128), nullable=True),
            sa.Column("granted_by_admin", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("granted_by_admin_id", sa.String(36), nullable=True),
            sa.Column("activated_at", sa.DateTime(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
            sa.Column("perks_unlocked", sa.JSON(), nullable=True),
            sa.Column("referral_slots_remaining", sa.Integer(), nullable=False, server_default="5"),
            sa.Column("concierge_analyst_name", sa.String(128), nullable=True),
            sa.Column("concierge_analyst_email", sa.String(255), nullable=True),
            sa.Column("calendly_link", sa.String(512), nullable=True),
            sa.Column("logo_url", sa.String(1024), nullable=True),
            sa.Column("watermark_text", sa.String(256), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        if not _index_exists("founders_circle_members", "ix_founders_circle_members_artist_id"):
            op.create_index(
                "ix_founders_circle_members_artist_id",
                "founders_circle_members",
                ["artist_id"],
                unique=True,
            )

    # ------------------------------------------------------------------
    # vip_invite_codes
    # ------------------------------------------------------------------
    if not _table_exists("vip_invite_codes"):
        op.create_table(
            "vip_invite_codes",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("code", sa.String(128), nullable=False),
            sa.Column("code_hash", sa.String(256), nullable=False),
            sa.Column("tier_level", sa.String(32), nullable=False, server_default="FOUNDERS_CIRCLE"),
            sa.Column("created_by_admin_id", sa.String(36), nullable=True),
            sa.Column("created_by_artist_id", sa.String(36), nullable=True),
            sa.Column("is_used", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("used_by_artist_id", sa.String(36), nullable=True),
            sa.Column("used_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("max_uses", sa.Integer(), nullable=False, server_default="1"),
            sa.Column("use_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("perk_bonus", sa.String(128), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_vip_invite_codes_code", "vip_invite_codes", ["code"], unique=True)
        op.create_index("ix_vip_invite_codes_code_hash", "vip_invite_codes", ["code_hash"], unique=True)

    # ------------------------------------------------------------------
    # persona_profiles
    # ------------------------------------------------------------------
    if not _table_exists("persona_profiles"):
        op.create_table(
            "persona_profiles",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("artist_id", sa.String(36), nullable=False),
            sa.Column("enrichment_status", sa.String(32), nullable=False, server_default="pending"),
            sa.Column("enrichment_job_id", sa.String(128), nullable=True),
            sa.Column("enriched_at", sa.DateTime(), nullable=True),
            sa.Column("imdb_id", sa.String(64), nullable=True),
            sa.Column("discogs_artist_id", sa.String(64), nullable=True),
            sa.Column("spotify_artist_id", sa.String(64), nullable=True),
            sa.Column("musicbrainz_id", sa.String(64), nullable=True),
            sa.Column("allmusic_id", sa.String(64), nullable=True),
            sa.Column("pro_credits", sa.JSON(), nullable=True),
            sa.Column("social_handles", sa.JSON(), nullable=True),
            sa.Column("detected_roles", sa.JSON(), nullable=True),
            sa.Column("primary_vertical", sa.String(32), nullable=True),
            sa.Column("catalog_summary", sa.JSON(), nullable=True),
            sa.Column("bio_snippet", sa.Text(), nullable=True),
            sa.Column("genre_tags", sa.JSON(), nullable=True),
            sa.Column("notable_works", sa.JSON(), nullable=True),
            sa.Column("collaborators", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index(
            "ix_persona_profiles_artist_id", "persona_profiles", ["artist_id"], unique=True
        )

    # ------------------------------------------------------------------
    # concierge_messages
    # ------------------------------------------------------------------
    if not _table_exists("concierge_messages"):
        op.create_table(
            "concierge_messages",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("artist_id", sa.String(36), nullable=False),
            sa.Column("sender_type", sa.String(16), nullable=False, server_default="artist"),
            sa.Column("sender_name", sa.String(128), nullable=False),
            sa.Column("analyst_id", sa.String(36), nullable=True),
            sa.Column("message_body", sa.Text(), nullable=False),
            sa.Column("read_at", sa.DateTime(), nullable=True),
            sa.Column("attachments", sa.JSON(), nullable=True),
            sa.Column("escalated", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("escalated_at", sa.DateTime(), nullable=True),
            sa.Column("human_analyst_requested", sa.Boolean(), nullable=False, server_default="0"),
            sa.Column("thread_id", sa.String(36), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_concierge_messages_artist_id", "concierge_messages", ["artist_id"])
        op.create_index("ix_concierge_messages_analyst_id", "concierge_messages", ["analyst_id"])
        op.create_index("ix_concierge_messages_thread_id", "concierge_messages", ["thread_id"])

    # ------------------------------------------------------------------
    # vip_referrals
    # ------------------------------------------------------------------
    if not _table_exists("vip_referrals"):
        op.create_table(
            "vip_referrals",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("referrer_artist_id", sa.String(36), nullable=False),
            sa.Column("referred_email", sa.String(255), nullable=False),
            sa.Column("referred_artist_id", sa.String(36), nullable=True),
            sa.Column("invite_code_id", sa.String(36), nullable=True),
            sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
            sa.Column("perk_code_referrer", sa.String(128), nullable=True),
            sa.Column("perk_code_referred", sa.String(128), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("joined_at", sa.DateTime(), nullable=True),
            sa.Column("rewarded_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_vip_referrals_referrer", "vip_referrals", ["referrer_artist_id"])
        op.create_index("ix_vip_referrals_referred_email", "vip_referrals", ["referred_email"])
        op.create_index("ix_vip_referrals_referred_artist", "vip_referrals", ["referred_artist_id"])

    # ------------------------------------------------------------------
    # weekly_briefs
    # ------------------------------------------------------------------
    if not _table_exists("weekly_briefs"):
        op.create_table(
            "weekly_briefs",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("artist_id", sa.String(36), nullable=False),
            sa.Column("brief_week", sa.String(8), nullable=False),
            sa.Column("text_summary", sa.Text(), nullable=True),
            sa.Column("audio_url", sa.String(1024), nullable=True),
            sa.Column("video_url", sa.String(1024), nullable=True),
            sa.Column("key_insights", sa.JSON(), nullable=True),
            sa.Column("action_items", sa.JSON(), nullable=True),
            sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
            sa.Column("generated_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_weekly_briefs_artist_id", "weekly_briefs", ["artist_id"])

    # ------------------------------------------------------------------
    # copilot_queries
    # ------------------------------------------------------------------
    if not _table_exists("copilot_queries"):
        op.create_table(
            "copilot_queries",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("artist_id", sa.String(36), nullable=False),
            sa.Column("query_text", sa.Text(), nullable=False),
            sa.Column("response_text", sa.Text(), nullable=True),
            sa.Column("context_snapshot", sa.JSON(), nullable=True),
            sa.Column("confidence", sa.Float(), nullable=True),
            sa.Column("sources_cited", sa.JSON(), nullable=True),
            sa.Column("latency_ms", sa.Integer(), nullable=True),
            sa.Column("thumbs_up", sa.Boolean(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_copilot_queries_artist_id", "copilot_queries", ["artist_id"])


def downgrade() -> None:
    for tbl in [
        "copilot_queries",
        "weekly_briefs",
        "vip_referrals",
        "concierge_messages",
        "persona_profiles",
        "vip_invite_codes",
        "founders_circle_members",
    ]:
        if _table_exists(tbl):
            op.drop_table(tbl)
