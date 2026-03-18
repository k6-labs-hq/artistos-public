"""TV/Film enterprise foundation fields and portfolio jobs.

Revision ID: 20260318_0021
Revises: 20260318_0020
Create Date: 2026-03-18
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260318_0021"
down_revision = "20260318_0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "artists" in table_names:
        artist_columns = {c["name"] for c in inspector.get_columns("artists")}
        if "primary_vertical" not in artist_columns:
            op.add_column("artists", sa.Column("primary_vertical", sa.String(), nullable=True))
        if "tvfilm_role" not in artist_columns:
            op.add_column("artists", sa.Column("tvfilm_role", sa.String(), nullable=True))
        if "organization_type" not in artist_columns:
            op.add_column("artists", sa.Column("organization_type", sa.String(), nullable=True))
        if "enterprise_mode_enabled" not in artist_columns:
            op.add_column(
                "artists",
                sa.Column("enterprise_mode_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            )

        index_names = {idx["name"] for idx in inspector.get_indexes("artists")}
        if "ix_artists_primary_vertical" not in index_names:
            op.create_index("ix_artists_primary_vertical", "artists", ["primary_vertical"], unique=False)
        if "ix_artists_tvfilm_role" not in index_names:
            op.create_index("ix_artists_tvfilm_role", "artists", ["tvfilm_role"], unique=False)
        if "ix_artists_organization_type" not in index_names:
            op.create_index("ix_artists_organization_type", "artists", ["organization_type"], unique=False)

    if "tvfilm_portfolio_jobs" not in table_names:
        op.create_table(
            "tvfilm_portfolio_jobs",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("organization_name", sa.String(), nullable=False),
            sa.Column("entity_type", sa.String(), nullable=False),
            sa.Column("uploaded_filename", sa.String(), nullable=True),
            sa.Column("roster_size", sa.Integer(), nullable=False, server_default="0"),
            sa.Column(
                "status",
                sa.Enum("QUEUED", "RUNNING", "COMPLETE", "FAILED", name="tvfilmportfoliojobstatus"),
                nullable=False,
                server_default="QUEUED",
            ),
            sa.Column("summary_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_tvfilm_portfolio_jobs_organization_name", "tvfilm_portfolio_jobs", ["organization_name"], unique=False)
        op.create_index("ix_tvfilm_portfolio_jobs_entity_type", "tvfilm_portfolio_jobs", ["entity_type"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "tvfilm_portfolio_jobs" in table_names:
        index_names = {idx["name"] for idx in inspector.get_indexes("tvfilm_portfolio_jobs")}
        if "ix_tvfilm_portfolio_jobs_entity_type" in index_names:
            op.drop_index("ix_tvfilm_portfolio_jobs_entity_type", table_name="tvfilm_portfolio_jobs")
        if "ix_tvfilm_portfolio_jobs_organization_name" in index_names:
            op.drop_index("ix_tvfilm_portfolio_jobs_organization_name", table_name="tvfilm_portfolio_jobs")
        op.drop_table("tvfilm_portfolio_jobs")

    if "artists" in table_names:
        index_names = {idx["name"] for idx in inspector.get_indexes("artists")}
        if "ix_artists_organization_type" in index_names:
            op.drop_index("ix_artists_organization_type", table_name="artists")
        if "ix_artists_tvfilm_role" in index_names:
            op.drop_index("ix_artists_tvfilm_role", table_name="artists")
        if "ix_artists_primary_vertical" in index_names:
            op.drop_index("ix_artists_primary_vertical", table_name="artists")

        artist_columns = {c["name"] for c in inspector.get_columns("artists")}
        if "enterprise_mode_enabled" in artist_columns:
            op.drop_column("artists", "enterprise_mode_enabled")
        if "organization_type" in artist_columns:
            op.drop_column("artists", "organization_type")
        if "tvfilm_role" in artist_columns:
            op.drop_column("artists", "tvfilm_role")
        if "primary_vertical" in artist_columns:
            op.drop_column("artists", "primary_vertical")
