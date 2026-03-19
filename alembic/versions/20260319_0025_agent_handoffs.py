"""Add persistent two-agent handoff records.

Revision ID: 20260319_0025
Revises: 20260319_0024
Create Date: 2026-03-19
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260319_0025"
down_revision = "20260319_0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_handoffs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("run_id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("handoff_id", sa.String(), nullable=False),
        sa.Column("from_agent", sa.String(), nullable=False),
        sa.Column("to_agent", sa.String(), nullable=False),
        sa.Column("readiness_score", sa.Float(), nullable=False),
        sa.Column("readiness_threshold", sa.Float(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_handoffs_run_id", "agent_handoffs", ["run_id"], unique=False)
    op.create_index("ix_agent_handoffs_artist_id", "agent_handoffs", ["artist_id"], unique=False)
    op.create_index("ix_agent_handoffs_handoff_id", "agent_handoffs", ["handoff_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_agent_handoffs_handoff_id", table_name="agent_handoffs")
    op.drop_index("ix_agent_handoffs_artist_id", table_name="agent_handoffs")
    op.drop_index("ix_agent_handoffs_run_id", table_name="agent_handoffs")
    op.drop_table("agent_handoffs")
