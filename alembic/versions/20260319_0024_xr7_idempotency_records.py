"""Alembic migration: Add XR7 idempotency records for write operation deduplication.

Adding:
- xr7_idempotency_records table for recording idempotent operation keys and cached responses
- Indexes on idempotency_key, tenant_id, artist_id for fast lookups
"""

from datetime import datetime, timezone

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260319_0024"
down_revision = "20260319_0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create xr7_idempotency_records table."""
    op.create_table(
        "xr7_idempotency_records",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("idempotency_key", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=True),
        sa.Column("request_path", sa.String(), nullable=True),
        sa.Column("request_method", sa.String(), nullable=True),
        sa.Column("response_status", sa.Integer(), nullable=False),
        sa.Column("response_body", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, default=lambda: datetime.now(timezone.utc)),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create unique index on idempotency_key to prevent duplicates
    op.create_index(
        "ix_xr7_idempotency_records_idempotency_key",
        "xr7_idempotency_records",
        ["idempotency_key"],
        unique=True,
    )

    # Create index on tenant_id for multi-tenant queries
    op.create_index(
        "ix_xr7_idempotency_records_tenant_id",
        "xr7_idempotency_records",
        ["tenant_id"],
    )

    # Create index on artist_id for artist-specific lookups
    op.create_index(
        "ix_xr7_idempotency_records_artist_id",
        "xr7_idempotency_records",
        ["artist_id"],
    )


def downgrade() -> None:
    """Drop xr7_idempotency_records table."""
    op.drop_index("ix_xr7_idempotency_records_artist_id")
    op.drop_index("ix_xr7_idempotency_records_tenant_id")
    op.drop_index("ix_xr7_idempotency_records_idempotency_key")
    op.drop_table("xr7_idempotency_records")
