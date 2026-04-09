"""onboarding architecture baseline

Revision ID: 20260314_0001
Revises:
Create Date: 2026-03-14 00:00:00
"""

import sqlalchemy as sa

from alembic import op

revision = "20260314_0001"
down_revision = "20260314_0000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "oauth_connector_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("redirect_uri", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("requested_scopes", sa.Text(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_by_email", sa.String(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("state"),
    )
    op.create_index("ix_oauth_connector_sessions_artist_id", "oauth_connector_sessions", ["artist_id"])
    op.create_index("ix_oauth_connector_sessions_provider", "oauth_connector_sessions", ["provider"])

    op.create_table(
        "connector_account_links",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("external_account_id", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=True),
        sa.Column("granted_scopes", sa.Text(), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_type", sa.String(), nullable=False),
        sa.Column("token_expires_at", sa.DateTime(), nullable=True),
        sa.Column("last_refreshed_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_by_email", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "artist_id",
            "provider",
            "tenant_id",
            "external_account_id",
            name="uq_connector_account_artist_provider_tenant_external",
        ),
    )
    op.create_index("ix_connector_account_links_artist_id", "connector_account_links", ["artist_id"])

    op.create_table(
        "catalog_confirmations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("work_id", sa.String(), nullable=False),
        sa.Column("ownership_confirmed", sa.String(), nullable=False),
        sa.Column("splits_confirmed", sa.String(), nullable=False),
        sa.Column("publisher_confirmed", sa.String(), nullable=False),
        sa.Column("admin_confirmed", sa.String(), nullable=False),
        sa.Column("correction_notes", sa.Text(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "immutable_ledger_entries",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("entry_type", sa.String(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("prior_hash", sa.String(), nullable=True),
        sa.Column("entry_hash", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "parser_plugins",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("parser_type", sa.String(), nullable=False),
        sa.Column("plugin_name", sa.String(), nullable=False),
        sa.Column("plugin_entrypoint", sa.Text(), nullable=False),
        sa.Column("plugin_signature", sa.String(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("artist_id", "parser_type", name="uq_parser_plugin_artist_type"),
    )

    op.create_table(
        "sync_jobs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("integration", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("result_json", sa.Text(), nullable=True),
        sa.Column("queue_backend", sa.String(), nullable=False),
        sa.Column("last_task_id", sa.String(), nullable=True),
        sa.Column("enqueued_at", sa.DateTime(), nullable=True),
        sa.Column("next_run_at", sa.DateTime(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "universal_royalty_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("source_name", sa.String(), nullable=False),
        sa.Column("record_type", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit_value", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("territory", sa.String(), nullable=True),
        sa.Column("work_id", sa.String(), nullable=True),
        sa.Column("work_title", sa.String(), nullable=True),
        sa.Column("isrc", sa.String(), nullable=True),
        sa.Column("ipi", sa.String(), nullable=True),
        sa.Column("statement_period", sa.String(), nullable=True),
        sa.Column("source_ref", sa.String(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=False),
        sa.Column("ingested_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "catalog_graph_snapshots",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("graph_version", sa.String(), nullable=False),
        sa.Column("nodes_json", sa.Text(), nullable=False),
        sa.Column("edges_json", sa.Text(), nullable=False),
        sa.Column("duplicates_json", sa.Text(), nullable=False),
        sa.Column("missing_metadata_json", sa.Text(), nullable=False),
        sa.Column("ownership_conflicts_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("catalog_graph_snapshots")
    op.drop_table("universal_royalty_events")
    op.drop_table("sync_jobs")
    op.drop_table("parser_plugins")
    op.drop_table("immutable_ledger_entries")
    op.drop_table("catalog_confirmations")
    op.drop_table("connector_account_links")
    op.drop_table("oauth_connector_sessions")
