"""Add s3_uri to statements for storing the original uploaded bytes.

See docs/decisions/statement-storage-and-retention.md for the rationale —
audit defensibility, reprocessing under updated parsers, legal evidence
chain. 7-year retention enforced via bucket lifecycle policy (configured
out-of-band on the MinIO bucket; lifecycle codification deferred to the
managed-storage migration).

Backfill is intentionally NOT done here — the original file bytes for
existing rows are gone (we hashed and discarded). Existing rows stay at
NULL `s3_uri`. Re-uploading the same file (same `(artist_id, file_hash)`)
still 409s as before; we just won't have the bytes for the historical
upload.

Revision ID: 20260505_0041
Revises: 20260505_0040
Create Date: 2026-05-05
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260505_0041"
down_revision = "20260505_0040"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("statements", sa.Column("s3_uri", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("statements", "s3_uri")
