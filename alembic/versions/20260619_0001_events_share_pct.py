"""Add events.share_pct (writer share reported by the payer on the statement line).

Nullable; existing rows stay NULL. Populated going forward by parsers whose statements
carry a share (SESAC, MLC). Powers the WORK_SHARE_DRIFT detector.

Revision ID: 20260619_0001
Revises: 20260618_0001
Create Date: 2026-11-18
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260619_0001"
down_revision = "20260618_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("events", sa.Column("share_pct", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("events", "share_pct")
