"""metadata repair audit table

Revision ID: 20260316_0009
Revises: 20260316_0008
Create Date: 2026-03-16
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260316_0009"
down_revision = "20260316_0008"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        return table_name in insp.get_table_names()
    except Exception:  # noqa: BLE001
        return False


def upgrade() -> None:
    if _table_exists("metadata_issues"):
        return

    op.create_table(
        "metadata_issues",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("issue_type", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False, server_default="MEDIUM"),
        sa.Column("issue_key", sa.String(), nullable=False),
        sa.Column("source_system", sa.String(), nullable=True),
        sa.Column("work_id", sa.String(), nullable=True),
        sa.Column("event_id", sa.String(), nullable=True),
        sa.Column("before_value_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("after_value_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("repair_status", sa.String(), nullable=False, server_default="DETECTED"),
        sa.Column("repair_rationale", sa.String(), nullable=True),
        sa.Column("chain_of_custody_hash", sa.String(), nullable=True),
        sa.Column("projected_leakage_avoided", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("repaired_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
        sa.ForeignKeyConstraint(["work_id"], ["works.id"]),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_metadata_issues_artist_id", "metadata_issues", ["artist_id"])
    op.create_index("ix_metadata_issues_issue_type", "metadata_issues", ["issue_type"])
    op.create_index("ix_metadata_issues_issue_key", "metadata_issues", ["issue_key"])
    op.create_index("ix_metadata_issues_work_id", "metadata_issues", ["work_id"])
    op.create_index("ix_metadata_issues_event_id", "metadata_issues", ["event_id"])
    op.create_index("ix_metadata_issues_repair_status", "metadata_issues", ["repair_status"])
    op.create_index("ix_metadata_issues_created_at", "metadata_issues", ["created_at"])


def downgrade() -> None:
    if not _table_exists("metadata_issues"):
        return
    op.drop_index("ix_metadata_issues_created_at", table_name="metadata_issues")
    op.drop_index("ix_metadata_issues_repair_status", table_name="metadata_issues")
    op.drop_index("ix_metadata_issues_event_id", table_name="metadata_issues")
    op.drop_index("ix_metadata_issues_work_id", table_name="metadata_issues")
    op.drop_index("ix_metadata_issues_issue_key", table_name="metadata_issues")
    op.drop_index("ix_metadata_issues_issue_type", table_name="metadata_issues")
    op.drop_index("ix_metadata_issues_artist_id", table_name="metadata_issues")
    op.drop_table("metadata_issues")
