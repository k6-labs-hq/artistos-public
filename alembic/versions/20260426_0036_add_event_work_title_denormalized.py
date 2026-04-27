"""add denormalized work_title column to events

Adds a non-FK ``events.work_title`` column so that anomaly rules can
aggregate by track even before a Work record has been matched to the
event. Backfills NULL on existing rows (the column is nullable).

Revision ID: 20260426_0036
Revises: 20260422_0035
Create Date: 2026-04-26
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260426_0036"
down_revision = "20260422_0035"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "events",
        sa.Column("work_title", sa.String(), nullable=True),
    )
    op.create_index(
        "ix_events_work_title",
        "events",
        ["work_title"],
    )


def downgrade() -> None:
    op.drop_index("ix_events_work_title", table_name="events")
    op.drop_column("events", "work_title")
