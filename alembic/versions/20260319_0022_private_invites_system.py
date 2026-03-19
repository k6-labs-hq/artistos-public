"""Create invites system tables.

Revision ID: 20260319_0022_private_invites_system
Revises: 20260318_0021_tvfilm_enterprise_foundation
down_revision = "20260318_0021"
branch_labels = None
depends_on = None
Create Date: 2026-03-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260319_0022_private_invites_system"


def upgrade() -> None:
    # Create invite status enum
    invite_status = postgresql.ENUM(
        "pending", "sent", "opened", "redeemed", "expired", "revoked",
        name="invitestatus",
        create_type=True
    )
    invite_status.create(op.get_bind(), checkfirst=True)

    # Create invite channel enum
    invite_channel = postgresql.ENUM(
        "email", "instagram_dm", "sms", "manual",
        name="invitechannel",
        create_type=True
    )
    invite_channel.create(op.get_bind(), checkfirst=True)

    # Create invite role enum
    invite_role = postgresql.ENUM(
        "artist", "writer", "director", "actor", "studio", "distributor", "manager", "agent", "analyst",
        name="inviterole",
        create_type=True
    )
    invite_role.create(op.get_bind(), checkfirst=True)

    # Create invites table
    op.create_table(
        "invites",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("recipient_name", sa.String(255), nullable=False),
        sa.Column("recipient_email", sa.String(255), nullable=True),
        sa.Column("recipient_phone", sa.String(20), nullable=True),
        sa.Column("status", sa.Enum("pending", "sent", "opened", "redeemed", "expired", "revoked", name="invitestatus"), nullable=False),
        sa.Column("channel", sa.Enum("email", "instagram_dm", "sms", "manual", name="invitechannel"), nullable=False),
        sa.Column("role", sa.Enum("artist", "writer", "director", "actor", "studio", "distributor", "manager", "agent", "analyst", name="inviterole"), nullable=False),
        sa.Column("invite_token", sa.String(512), nullable=False),
        sa.Column("token_expiration", sa.DateTime(), nullable=False),
        sa.Column("referring_agent_id", sa.String(36), nullable=True),
        sa.Column("referring_manager_id", sa.String(36), nullable=True),
        sa.Column("campaign", sa.String(100), nullable=True),
        sa.Column("is_vip", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("custom_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("opened_at", sa.DateTime(), nullable=True),
        sa.Column("redeemed_at", sa.DateTime(), nullable=True),
        sa.Column("redeemed_by_artist_id", sa.String(36), nullable=True),
        sa.Column("is_single_use_consumed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("redemption_ip_address", sa.String(45), nullable=True),
        sa.Column("custom_metadata", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invite_token", name="uq_invites_token"),
    )
    op.create_index("ix_invites_recipient_name", "invites", ["recipient_name"], unique=False)
    op.create_index("ix_invites_recipient_email", "invites", ["recipient_email"], unique=False)
    op.create_index("ix_invites_status", "invites", ["status"], unique=False)
    op.create_index("ix_invites_token_status", "invites", ["invite_token", "status"], unique=False)
    op.create_index("ix_invites_recipient_status", "invites", ["recipient_email", "status"], unique=False)
    op.create_index("ix_invites_created_status", "invites", ["created_at", "status"], unique=False)
    op.create_index("ix_invites_referring_agent_id", "invites", ["referring_agent_id"], unique=False)
    op.create_index("ix_invites_referring_manager_id", "invites", ["referring_manager_id"], unique=False)
    op.create_index("ix_invites_is_vip", "invites", ["is_vip"], unique=False)
    op.create_index("ix_invites_redeemed_by_artist_id", "invites", ["redeemed_by_artist_id"], unique=False)

    # Create invite_events table
    op.create_table(
        "invite_events",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("invite_id", sa.String(36), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("event_data", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invite_events_invite_id", "invite_events", ["invite_id"], unique=False)
    op.create_index("ix_invite_events_event_type", "invite_events", ["event_type"], unique=False)
    op.create_index("ix_invite_events_invite_id_created", "invite_events", ["invite_id", "created_at"], unique=False)

    # Create invite_analytics table
    op.create_table(
        "invite_analytics",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("campaign", sa.String(100), nullable=True),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("invites_created", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invites_sent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invites_opened", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invites_redeemed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invites_expired", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("open_rate", sa.Float(), nullable=True),
        sa.Column("redemption_rate", sa.Float(), nullable=True),
        sa.Column("role_distribution", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_invite_analytics_campaign", "invite_analytics", ["campaign"], unique=False)
    op.create_index("ix_invite_analytics_date", "invite_analytics", ["date"], unique=False)
    op.create_index("ix_invite_analytics_campaign_date", "invite_analytics", ["campaign", "date"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_invite_analytics_campaign_date", table_name="invite_analytics")
    op.drop_index("ix_invite_analytics_date", table_name="invite_analytics")
    op.drop_index("ix_invite_analytics_campaign", table_name="invite_analytics")
    op.drop_table("invite_analytics")

    op.drop_index("ix_invite_events_invite_id_created", table_name="invite_events")
    op.drop_index("ix_invite_events_event_type", table_name="invite_events")
    op.drop_index("ix_invite_events_invite_id", table_name="invite_events")
    op.drop_table("invite_events")

    op.drop_index("ix_invites_redeemed_by_artist_id", table_name="invites")
    op.drop_index("ix_invites_is_vip", table_name="invites")
    op.drop_index("ix_invites_referring_manager_id", table_name="invites")
    op.drop_index("ix_invites_referring_agent_id", table_name="invites")
    op.drop_index("ix_invites_created_status", table_name="invites")
    op.drop_index("ix_invites_recipient_status", table_name="invites")
    op.drop_index("ix_invites_token_status", table_name="invites")
    op.drop_index("ix_invites_status", table_name="invites")
    op.drop_index("ix_invites_recipient_email", table_name="invites")
    op.drop_index("ix_invites_recipient_name", table_name="invites")
    op.drop_table("invites")

    # Drop enums
    postgresql.ENUM("inviterole", name="inviterole").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM("invitechannel", name="invitechannel").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM("invitestatus", name="invitestatus").drop(op.get_bind(), checkfirst=True)
