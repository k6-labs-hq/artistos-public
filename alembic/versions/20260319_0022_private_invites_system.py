"""Create invites system tables.

Revision ID: 20260319_0022_private_invites_system
Revises: 20260318_0021_tvfilm_enterprise_foundation
Create Date: 2026-03-19 00:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260319_0022_private_invites_system"
down_revision = "20260318_0021"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        return table_name in insp.get_table_names()
    except Exception:  # noqa: BLE001
        return False


def _index_exists(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        indexes = insp.get_indexes(table_name)
    except Exception:  # noqa: BLE001
        return False
    return any((index.get("name") or "") == index_name for index in indexes)


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
    if not _table_exists("invites"):
        op.create_table(
            "invites",
            sa.Column("id", sa.String(36), nullable=False),
            sa.Column("recipient_name", sa.String(255), nullable=False),
            sa.Column("recipient_email", sa.String(255), nullable=True),
            sa.Column("recipient_phone", sa.String(20), nullable=True),
            sa.Column("status", sa.Enum("pending", "sent", "opened", "redeemed", "expired", "revoked", name="invitestatus", create_type=False), nullable=False),
            sa.Column("channel", sa.Enum("email", "instagram_dm", "sms", "manual", name="invitechannel", create_type=False), nullable=False),
            sa.Column("role", sa.Enum("artist", "writer", "director", "actor", "studio", "distributor", "manager", "agent", "analyst", name="inviterole", create_type=False), nullable=False),
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
    for index_name, columns in [
        ("ix_invites_recipient_name", ["recipient_name"]),
        ("ix_invites_recipient_email", ["recipient_email"]),
        ("ix_invites_status", ["status"]),
        ("ix_invites_token_status", ["invite_token", "status"]),
        ("ix_invites_recipient_status", ["recipient_email", "status"]),
        ("ix_invites_created_status", ["created_at", "status"]),
        ("ix_invites_referring_agent_id", ["referring_agent_id"]),
        ("ix_invites_referring_manager_id", ["referring_manager_id"]),
        ("ix_invites_is_vip", ["is_vip"]),
        ("ix_invites_redeemed_by_artist_id", ["redeemed_by_artist_id"]),
    ]:
        if not _index_exists("invites", index_name):
            op.create_index(index_name, "invites", columns, unique=False)

    # Create invite_events table
    if not _table_exists("invite_events"):
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
    for index_name, columns in [
        ("ix_invite_events_invite_id", ["invite_id"]),
        ("ix_invite_events_event_type", ["event_type"]),
        ("ix_invite_events_invite_id_created", ["invite_id", "created_at"]),
    ]:
        if not _index_exists("invite_events", index_name):
            op.create_index(index_name, "invite_events", columns, unique=False)

    # Create invite_analytics table
    if not _table_exists("invite_analytics"):
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
    for index_name, columns in [
        ("ix_invite_analytics_campaign", ["campaign"]),
        ("ix_invite_analytics_date", ["date"]),
        ("ix_invite_analytics_campaign_date", ["campaign", "date"]),
    ]:
        if not _index_exists("invite_analytics", index_name):
            op.create_index(index_name, "invite_analytics", columns, unique=False)


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
