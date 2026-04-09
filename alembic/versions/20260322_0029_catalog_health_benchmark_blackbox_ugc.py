"""
Catalog health, benchmark aggregates, blackbox matches, and UGC opportunities.

Revision ID: 20260322_0029
Revises: 20260321_0028
Create Date: 2026-03-22
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260322_0029"
down_revision = "20260321_0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # ──────────────────────────────────────────────────────────────────────────
    # catalog_fix_issues
    # ──────────────────────────────────────────────────────────────────────────
    if "catalog_fix_issues" not in existing_tables:
        op.create_table(
            "catalog_fix_issues",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), sa.ForeignKey("artists.id"), nullable=False),
            sa.Column("category", sa.String(), nullable=False),
            sa.Column("priority", sa.String(), nullable=False, server_default="medium"),
            sa.Column("description", sa.String(), nullable=False),
            sa.Column("affected_works_json", sa.String(), nullable=True),
            sa.Column("estimated_recoverable_usd", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("suggested_action", sa.String(), nullable=False, server_default="other"),
            sa.Column("status", sa.String(), nullable=False, server_default="pending"),
            sa.Column("requested_at", sa.DateTime(), nullable=True),
            sa.Column("resolved_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("template_payload", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_catalog_fix_issues_artist_id", "catalog_fix_issues", ["artist_id"])
        op.create_index("ix_catalog_fix_issues_category", "catalog_fix_issues", ["category"])
        op.create_index("ix_catalog_fix_issues_status", "catalog_fix_issues", ["status"])
        op.create_index("ix_catalog_fix_issues_created_at", "catalog_fix_issues", ["created_at"])

    # ──────────────────────────────────────────────────────────────────────────
    # benchmark_aggregates
    # ──────────────────────────────────────────────────────────────────────────
    if "benchmark_aggregates" not in existing_tables:
        op.create_table(
            "benchmark_aggregates",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("genre", sa.String(), nullable=False),
            sa.Column("role_type", sa.String(), nullable=False),
            sa.Column("catalog_size_bucket", sa.String(), nullable=False),
            sa.Column("leakage_pct_p25", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("leakage_pct_p50", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("leakage_pct_p75", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("recovery_rate_p25", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("recovery_rate_p50", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("recovery_rate_p75", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("avg_recovered_per_anomaly_p25", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("avg_recovered_per_anomaly_p50", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("avg_recovered_per_anomaly_p75", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("sample_size", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_benchmark_aggregates_genre", "benchmark_aggregates", ["genre"])
        op.create_index("ix_benchmark_aggregates_role_type", "benchmark_aggregates", ["role_type"])
        op.create_index("ix_benchmark_aggregates_catalog_size_bucket", "benchmark_aggregates", ["catalog_size_bucket"])

    # ──────────────────────────────────────────────────────────────────────────
    # blackbox_matches
    # ──────────────────────────────────────────────────────────────────────────
    if "blackbox_matches" not in existing_tables:
        op.create_table(
            "blackbox_matches",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), sa.ForeignKey("artists.id"), nullable=False),
            sa.Column("society", sa.String(), nullable=False),
            sa.Column("match_type", sa.String(), nullable=False, server_default="name_alias"),
            sa.Column("matched_identifier", sa.String(), nullable=True),
            sa.Column("source_list", sa.String(), nullable=False, server_default="mlc_blackbox"),
            sa.Column("amount_range_low", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("amount_range_high", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("territory", sa.String(), nullable=True),
            sa.Column("redistribution_window_end_date", sa.DateTime(), nullable=False),
            sa.Column("urgency_days_remaining", sa.Integer(), nullable=False, server_default="365"),
            sa.Column("status", sa.String(), nullable=False, server_default="new"),
            sa.Column("anomaly_id", sa.String(), sa.ForeignKey("anomalies.id"), nullable=True),
            sa.Column("raw_society_data_json", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_blackbox_matches_artist_id", "blackbox_matches", ["artist_id"])
        op.create_index("ix_blackbox_matches_society", "blackbox_matches", ["society"])
        op.create_index("ix_blackbox_matches_status", "blackbox_matches", ["status"])
        op.create_index("ix_blackbox_matches_anomaly_id", "blackbox_matches", ["anomaly_id"])
        op.create_index("ix_blackbox_matches_created_at", "blackbox_matches", ["created_at"])

    # ──────────────────────────────────────────────────────────────────────────
    # ugc_opportunities
    # ──────────────────────────────────────────────────────────────────────────
    if "ugc_opportunities" not in existing_tables:
        op.create_table(
            "ugc_opportunities",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), sa.ForeignKey("artists.id"), nullable=False),
            sa.Column("anomaly_id", sa.String(), sa.ForeignKey("anomalies.id"), nullable=True),
            sa.Column("platform", sa.String(), nullable=False, server_default="youtube"),
            sa.Column("video_url", sa.String(), nullable=False),
            sa.Column("video_id", sa.String(), nullable=True),
            sa.Column("video_title", sa.String(), nullable=True),
            sa.Column("channel_name", sa.String(), nullable=True),
            sa.Column("matched_work_title", sa.String(), nullable=True),
            sa.Column("matched_isrc", sa.String(), nullable=True),
            sa.Column("estimated_views", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("estimated_recoverable", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("status", sa.String(), nullable=False, server_default="detected"),
            sa.Column("is_monetized", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("claim_draft_json", sa.String(), nullable=True),
            sa.Column("content_id_asset_id", sa.String(), nullable=True),
            sa.Column("detected_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("last_scanned_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ugc_opportunities_artist_id", "ugc_opportunities", ["artist_id"])
        op.create_index("ix_ugc_opportunities_platform", "ugc_opportunities", ["platform"])
        op.create_index("ix_ugc_opportunities_status", "ugc_opportunities", ["status"])
        op.create_index("ix_ugc_opportunities_video_id", "ugc_opportunities", ["video_id"])
        op.create_index("ix_ugc_opportunities_detected_at", "ugc_opportunities", ["detected_at"])
        op.create_index("ix_ugc_opportunities_anomaly_id", "ugc_opportunities", ["anomaly_id"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    for table in ["ugc_opportunities", "blackbox_matches", "benchmark_aggregates", "catalog_fix_issues"]:
        if table in existing_tables:
            op.drop_table(table)
