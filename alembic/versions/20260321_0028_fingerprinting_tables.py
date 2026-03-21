"""Create fingerprint_jobs and fingerprint_matches tables.

Revision ID: 20260321_0028
Revises: 20260320_0027
Create Date: 2026-03-21 00:28:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# ---------------------------------------------------------------------------
# Alembic metadata
# ---------------------------------------------------------------------------

revision = "20260321_0028"
down_revision = "20260320_0027"
branch_labels = None
depends_on = None


# ---------------------------------------------------------------------------
# Upgrade
# ---------------------------------------------------------------------------


def upgrade() -> None:
    # ------------------------------------------------------------------
    # fingerprint_jobs
    # ------------------------------------------------------------------
    op.create_table(
        "fingerprint_jobs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "processing",
                "completed",
                "failed",
                "partial",
                name="fingerprintjobstatus",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "mode",
            sa.Enum(
                "realtime",
                "batch",
                "reference",
                name="fingerprintjobmode",
            ),
            nullable=False,
            server_default="realtime",
        ),
        sa.Column("provider", sa.String(), nullable=True),
        sa.Column("audio_url", sa.String(), nullable=True),
        sa.Column("audio_s3_key", sa.String(), nullable=True),
        sa.Column("isrc", sa.String(), nullable=True),
        sa.Column("tenant_id", sa.String(), nullable=True),
        sa.Column("job_metadata", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["artist_id"], ["artists.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fingerprint_jobs_artist_id", "fingerprint_jobs", ["artist_id"])
    op.create_index("ix_fingerprint_jobs_status", "fingerprint_jobs", ["status"])
    op.create_index("ix_fingerprint_jobs_isrc", "fingerprint_jobs", ["isrc"])
    op.create_index("ix_fingerprint_jobs_tenant_id", "fingerprint_jobs", ["tenant_id"])
    op.create_index("ix_fingerprint_jobs_created_at", "fingerprint_jobs", ["created_at"])

    # ------------------------------------------------------------------
    # fingerprint_matches
    # ------------------------------------------------------------------
    op.create_table(
        "fingerprint_matches",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("job_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("track_id", sa.String(), nullable=True),
        sa.Column("isrc", sa.String(), nullable=True),
        sa.Column("iswc", sa.String(), nullable=True),
        sa.Column("ipi", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("artist_name", sa.String(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("match_type", sa.String(), nullable=False, server_default="unknown"),
        sa.Column("platform", sa.String(), nullable=True),
        sa.Column("territory", sa.String(), nullable=True),
        sa.Column("royalty_status", sa.String(), nullable=False, server_default="unknown"),
        sa.Column("anomaly_type", sa.String(), nullable=False, server_default="none"),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column(
            "matched_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["job_id"], ["fingerprint_jobs.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_fingerprint_matches_job_id", "fingerprint_matches", ["job_id"])
    op.create_index("ix_fingerprint_matches_isrc", "fingerprint_matches", ["isrc"])
    op.create_index("ix_fingerprint_matches_provider", "fingerprint_matches", ["provider"])
    op.create_index("ix_fingerprint_matches_platform", "fingerprint_matches", ["platform"])
    op.create_index("ix_fingerprint_matches_matched_at", "fingerprint_matches", ["matched_at"])


# ---------------------------------------------------------------------------
# Downgrade
# ---------------------------------------------------------------------------


def downgrade() -> None:
    op.drop_table("fingerprint_matches")
    op.drop_table("fingerprint_jobs")
    # Drop custom enum types (PostgreSQL only — SQLite is a no-op)
    with op.get_context().autocommit_block():
        op.execute("DROP TYPE IF EXISTS fingerprintjobstatus")
        op.execute("DROP TYPE IF EXISTS fingerprintjobmode")
