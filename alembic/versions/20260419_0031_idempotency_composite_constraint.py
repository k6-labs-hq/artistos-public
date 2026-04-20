"""Add composite unique constraint on idempotency_key + artist_id.

Issue #83: Add unique constraint on idempotency keys (request_id, artist_id)

CRITICAL SECURITY: Prevent duplicate idempotent operations per artist.

Previous migration (20260319_0024) created unique index on idempotency_key only,
but model defines UniqueConstraint(idempotency_key, artist_id). This migration
corrects the discrepancy by adding the proper composite constraint.

Why composite (idempotency_key, artist_id) instead of just idempotency_key:
- Same idempotency_key may be used by different artists (UUID collision risk minimal but non-zero)
- Artist-scoped operations should be independently idempotent
- Follows security best practices for multi-tenant isolation

Revision ID: 20260419_0031
Revises: 20260407_0030
Create Date: 2026-04-19
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260419_0031"
down_revision = "20260407_0030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add composite unique constraint on (idempotency_key, artist_id)."""
    
    # Drop the old single-column unique index
    op.drop_index(
        "ix_xr7_idempotency_records_idempotency_key",
        table_name="xr7_idempotency_records",
    )
    
    # Create non-unique index on idempotency_key for lookups
    op.create_index(
        "ix_xr7_idempotency_records_idempotency_key",
        "xr7_idempotency_records",
        ["idempotency_key"],
        unique=False,
    )
    
    # Add composite unique constraint matching the model definition
    op.create_unique_constraint(
        "uq_xr7_idempotency_request_id_artist_id",
        "xr7_idempotency_records",
        ["idempotency_key", "artist_id"],
    )


def downgrade() -> None:
    """Revert to single-column unique index."""
    
    # Drop composite unique constraint
    op.drop_constraint(
        "uq_xr7_idempotency_request_id_artist_id",
        "xr7_idempotency_records",
        type_="unique",
    )
    
    # Drop non-unique index
    op.drop_index(
        "ix_xr7_idempotency_records_idempotency_key",
        table_name="xr7_idempotency_records",
    )
    
    # Recreate single-column unique index
    op.create_index(
        "ix_xr7_idempotency_records_idempotency_key",
        "xr7_idempotency_records",
        ["idempotency_key"],
        unique=True,
    )
