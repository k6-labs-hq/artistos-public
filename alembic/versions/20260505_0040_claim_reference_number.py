"""Add reference_number to claims and backfill existing rows.

Human-readable reference (e.g. ``XR7-2026-A7B3F2``) for use in dispute
emails, PDF cover pages, and the operator dashboard. The UUID stays as
the internal primary key. Backfilling deterministically from the UUID's
first 6 hex chars so existing claims have a stable reference without us
having to mint a fresh random value (which would silently change the
"reference" any operator might already have written down).

Revision ID: 20260505_0040
Revises: 20260504_0039
Create Date: 2026-05-05
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260505_0040"
down_revision = "20260504_0039"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("claims", sa.Column("reference_number", sa.String(), nullable=True))

    # Backfill: derive each row's reference from the UUID's first 6 hex
    # chars + the year of created_at (or 2026 if null). This is stable —
    # re-running the migration on the same row produces the same value —
    # and avoids minting a fresh random for rows that may already be
    # referenced in operator notes.
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            UPDATE claims
            SET reference_number = (
                'XR7-' || COALESCE(EXTRACT(YEAR FROM created_at)::int::text, '2026')
                       || '-' || UPPER(SUBSTRING(REPLACE(id::text, '-', '') FROM 1 FOR 6))
            )
            WHERE reference_number IS NULL
            """
        )
    )

    op.create_unique_constraint(
        "uq_claims_reference_number", "claims", ["reference_number"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_claims_reference_number", "claims", type_="unique")
    op.drop_column("claims", "reference_number")
