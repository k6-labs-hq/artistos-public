"""Add artist-scoped unique constraint to idempotency records.

Revision ID: 20260416_2207
Revises: 20260416_2133
Create Date: 2026-04-16 22:07:00

This migration replaces the global unique index on idempotency_key with an
artist-scoped unique constraint on (idempotency_key, artist_id) to prevent
race-condition duplicates while allowing different artists to reuse the same key.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260416_2207"
down_revision = "20260416_2133"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(
        "ix_xr7_idempotency_records_idempotency_key",
        table_name="xr7_idempotency_records",
    )
    op.create_unique_constraint(
        "uq_xr7_idempotency_request_id_artist_id",
        "xr7_idempotency_records",
        ["idempotency_key", "artist_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_xr7_idempotency_request_id_artist_id",
        "xr7_idempotency_records",
        type_="unique",
    )
    op.create_index(
        "ix_xr7_idempotency_records_idempotency_key",
        "xr7_idempotency_records",
        ["idempotency_key"],
        unique=True,
    )
