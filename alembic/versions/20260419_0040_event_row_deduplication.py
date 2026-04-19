"""Add composite unique constraint on events for row-level deduplication.

Revision ID: 20260419_0040
Revises: 20260416_2207
Create Date: 2026-04-19 14:00:00.000000

Prevents duplicate royalty events from being inserted when artists upload
overlapping statement files (e.g., quarterly statements that include events
already present in monthly statements).

Unique constraint: (artist_id, platform, timestamp, quantity, event_type, territory, unit_value)

This ensures the exact same royalty event cannot be inserted twice, while
allowing legitimate corrections (e.g., updated unit_value for the same event).

Closes: XR7-401
Domain: ingestion
Scale-target: 10x ingestion volume with correctness guarantees
SOC 2: CC6.1 — Data integrity controls
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260419_0040"
down_revision = "20260416_2228"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add unique constraint to prevent duplicate events."""
    # Create unique index to enforce row-level deduplication
    # Using index instead of constraint for better performance on large tables
    op.create_index(
        "uq_event_identity",
        "events",
        [
            "artist_id",
            "event_type",
            "platform",
            "territory",
            "timestamp",
            "quantity",
            "unit_value",
        ],
        unique=True,
        postgresql_where=sa.text("work_id IS NULL"),
    )

    # Separate index for events with work_id
    op.create_index(
        "uq_event_identity_with_work",
        "events",
        [
            "artist_id",
            "event_type",
            "platform",
            "territory",
            "timestamp",
            "quantity",
            "unit_value",
            "work_id",
        ],
        unique=True,
        postgresql_where=sa.text("work_id IS NOT NULL"),
    )


def downgrade() -> None:
    """Remove unique constraint."""
    op.drop_index("uq_event_identity_with_work", table_name="events")
    op.drop_index("uq_event_identity", table_name="events")
