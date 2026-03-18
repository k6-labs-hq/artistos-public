"""xr7 forensic core entities

Revision ID: 20260317_0014
Revises: 20260317_0013
Create Date: 2026-03-17
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260317_0014"
down_revision = "20260317_0013"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        return table_name in insp.get_table_names()
    except Exception:  # noqa: BLE001
        return False


def upgrade() -> None:
    if not _table_exists("xr7_tracks"):
        op.create_table(
            "xr7_tracks",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("version", sa.String(), nullable=True),
            sa.Column("duration_ms", sa.Integer(), nullable=True),
            sa.Column("primary_artist_name", sa.String(), nullable=True),
            sa.Column("release_date", sa.Date(), nullable=True),
            sa.Column("isrc", sa.String(), nullable=True),
            sa.Column("upc", sa.String(), nullable=True),
            sa.Column("label_name", sa.String(), nullable=True),
            sa.Column("distributor", sa.String(), nullable=True),
            sa.Column("audio_fingerprint_id", sa.String(), nullable=True),
            sa.Column("source_priority", sa.Integer(), nullable=False, server_default="100"),
            sa.Column("canonical_confidence", sa.Float(), nullable=False, server_default="1.0"),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_xr7_tracks_tenant_id", "xr7_tracks", ["tenant_id"])
        op.create_index("ix_xr7_tracks_artist_id", "xr7_tracks", ["artist_id"])
        op.create_index("ix_xr7_tracks_isrc", "xr7_tracks", ["isrc"])
        op.create_index("ix_xr7_tracks_audio_fingerprint_id", "xr7_tracks", ["audio_fingerprint_id"])

    if not _table_exists("xr7_works"):
        op.create_table(
            "xr7_works",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("iswc", sa.String(), nullable=True),
            sa.Column("territory_scope", sa.String(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_xr7_works_tenant_id", "xr7_works", ["tenant_id"])
        op.create_index("ix_xr7_works_artist_id", "xr7_works", ["artist_id"])
        op.create_index("ix_xr7_works_iswc", "xr7_works", ["iswc"])

    if not _table_exists("xr7_identifier_mappings"):
        op.create_table(
            "xr7_identifier_mappings",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("track_id", sa.String(), nullable=True),
            sa.Column("work_id", sa.String(), nullable=True),
            sa.Column("isrc", sa.String(), nullable=True),
            sa.Column("iswc", sa.String(), nullable=True),
            sa.Column("ipi_number", sa.String(), nullable=True),
            sa.Column("cae_number", sa.String(), nullable=True),
            sa.Column("source_system", sa.String(), nullable=False),
            sa.Column("evidence_ref", sa.String(), nullable=True),
            sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["track_id"], ["xr7_tracks.id"]),
            sa.ForeignKeyConstraint(["work_id"], ["xr7_works.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _table_exists("xr7_usage_events"):
        op.create_table(
            "xr7_usage_events",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("platform", sa.String(), nullable=False),
            sa.Column("event_type", sa.String(), nullable=False),
            sa.Column("event_timestamp", sa.DateTime(), nullable=False),
            sa.Column("territory", sa.String(), nullable=True),
            sa.Column("channel", sa.String(), nullable=True),
            sa.Column("units", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("asset_ref", sa.String(), nullable=True),
            sa.Column("track_id", sa.String(), nullable=True),
            sa.Column("work_id", sa.String(), nullable=True),
            sa.Column("match_method", sa.Enum("api", "fingerprint", "fuzzy", "manual", name="xr7matchmethod"), nullable=False, server_default="api"),
            sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("monetization_estimate", sa.Float(), nullable=True),
            sa.Column("currency", sa.String(), nullable=False, server_default="USD"),
            sa.Column("source_category", sa.Enum("api", "file", "fingerprint", name="xr7sourcecategory"), nullable=False),
            sa.Column("raw_ref", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["track_id"], ["xr7_tracks.id"]),
            sa.ForeignKeyConstraint(["work_id"], ["xr7_works.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _table_exists("xr7_royalty_statements"):
        op.create_table(
            "xr7_royalty_statements",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("source_system", sa.String(), nullable=False),
            sa.Column("period_start", sa.Date(), nullable=True),
            sa.Column("period_end", sa.Date(), nullable=True),
            sa.Column("currency", sa.String(), nullable=False, server_default="USD"),
            sa.Column("gross_amount", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("net_amount", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("line_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("file_ref", sa.String(), nullable=True),
            sa.Column("parse_status", sa.String(), nullable=False, server_default="processed"),
            sa.Column("schema_version", sa.String(), nullable=False, server_default="v1"),
            sa.Column("ingestion_errors_json", sa.Text(), nullable=False, server_default="[]"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _table_exists("xr7_royalty_statement_lines"):
        op.create_table(
            "xr7_royalty_statement_lines",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("statement_id", sa.String(), nullable=False),
            sa.Column("row_index", sa.Integer(), nullable=False),
            sa.Column("raw_work_title", sa.String(), nullable=True),
            sa.Column("raw_artist_name", sa.String(), nullable=True),
            sa.Column("isrc", sa.String(), nullable=True),
            sa.Column("iswc", sa.String(), nullable=True),
            sa.Column("territory", sa.String(), nullable=True),
            sa.Column("units", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("rate", sa.Float(), nullable=True),
            sa.Column("amount", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("currency", sa.String(), nullable=False, server_default="USD"),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
            sa.ForeignKeyConstraint(["statement_id"], ["xr7_royalty_statements.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _table_exists("xr7_unmatched_works"):
        op.create_table(
            "xr7_unmatched_works",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("source_system", sa.String(), nullable=False),
            sa.Column("raw_title", sa.String(), nullable=True),
            sa.Column("raw_writer", sa.String(), nullable=True),
            sa.Column("raw_identifier", sa.String(), nullable=True),
            sa.Column("candidate_work_ids_json", sa.Text(), nullable=False, server_default="[]"),
            sa.Column("reason_code", sa.String(), nullable=False),
            sa.Column("recommended_action", sa.String(), nullable=False),
            sa.Column("status", sa.String(), nullable=False, server_default="open"),
            sa.Column("resolution_ref", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _table_exists("xr7_identity_nodes"):
        op.create_table(
            "xr7_identity_nodes",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("node_type", sa.Enum("artist", "work", "track", "rightsholder", "platform_profile", name="xr7identitynodetype"), nullable=False),
            sa.Column("node_key", sa.String(), nullable=False),
            sa.Column("label", sa.String(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("tenant_id", "artist_id", "node_type", "node_key", name="uq_xr7_identity_node"),
        )

    if not _table_exists("xr7_identity_edges"):
        op.create_table(
            "xr7_identity_edges",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("from_node_id", sa.String(), nullable=False),
            sa.Column("to_node_id", sa.String(), nullable=False),
            sa.Column("edge_type", sa.String(), nullable=False),
            sa.Column("source_system", sa.String(), nullable=False),
            sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("evidence_ref", sa.String(), nullable=True),
            sa.Column("active_from", sa.Date(), nullable=True),
            sa.Column("active_to", sa.Date(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["from_node_id"], ["xr7_identity_nodes.id"]),
            sa.ForeignKeyConstraint(["to_node_id"], ["xr7_identity_nodes.id"]),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _table_exists("xr7_connector_credentials"):
        op.create_table(
            "xr7_connector_credentials",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("tenant_id", sa.String(), nullable=False, server_default="default"),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("provider", sa.String(), nullable=False),
            sa.Column("external_account_id", sa.String(), nullable=False),
            sa.Column("encrypted_access_token", sa.Text(), nullable=False),
            sa.Column("encrypted_refresh_token", sa.Text(), nullable=True),
            sa.Column("token_expires_at", sa.DateTime(), nullable=True),
            sa.Column("granted_scopes_json", sa.Text(), nullable=False, server_default="[]"),
            sa.Column("status", sa.Enum("active", "disconnected", name="xr7connectorstatus"), nullable=False, server_default="active"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("tenant_id", "artist_id", "provider", "external_account_id", name="uq_xr7_connector_credential"),
        )


def downgrade() -> None:
    for table in [
        "xr7_connector_credentials",
        "xr7_identity_edges",
        "xr7_identity_nodes",
        "xr7_unmatched_works",
        "xr7_royalty_statement_lines",
        "xr7_royalty_statements",
        "xr7_usage_events",
        "xr7_identifier_mappings",
        "xr7_works",
        "xr7_tracks",
    ]:
        if _table_exists(table):
            op.drop_table(table)
