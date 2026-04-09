"""
Collaborator share leads — tracks co-writers, producers, and publishers
identified during a creator's analysis for viral invite loop and CRM logging.

Revision ID: 20260407_0030
Revises: 20260322_0029
Create Date: 2026-04-07
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260407_0030"
down_revision = "20260322_0029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "collaborator_share_leads" not in existing_tables:
        op.create_table(
            "collaborator_share_leads",
            sa.Column("id", sa.String(36), nullable=False),
            sa.Column("source_artist_id", sa.String(36), nullable=False),
            sa.Column("collaborator_name", sa.String(255), nullable=False),
            sa.Column("collaborator_email", sa.String(255), nullable=True),
            sa.Column("collaborator_role", sa.String(50), nullable=False, server_default="co_writer"),
            sa.Column("invite_id", sa.String(36), nullable=True),
            sa.Column("hubspot_contact_id", sa.String(100), nullable=True),
            sa.Column("share_message_text", sa.String(2000), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["source_artist_id"], ["artists.id"]),
            sa.ForeignKeyConstraint(["invite_id"], ["invites.id"]),
        )
        op.create_index(
            "ix_collaborator_share_leads_source_artist_id",
            "collaborator_share_leads",
            ["source_artist_id"],
        )
        op.create_index(
            "ix_collaborator_share_leads_collaborator_email",
            "collaborator_share_leads",
            ["collaborator_email"],
        )
        op.create_index(
            "ix_collaborator_share_leads_invite_id",
            "collaborator_share_leads",
            ["invite_id"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "collaborator_share_leads" in existing_tables:
        op.drop_index("ix_collaborator_share_leads_invite_id", "collaborator_share_leads")
        op.drop_index("ix_collaborator_share_leads_collaborator_email", "collaborator_share_leads")
        op.drop_index("ix_collaborator_share_leads_source_artist_id", "collaborator_share_leads")
        op.drop_table("collaborator_share_leads")
