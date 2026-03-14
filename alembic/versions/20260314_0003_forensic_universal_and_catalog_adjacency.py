"""forensic universal event and catalog adjacency tables

Revision ID: 20260314_0003
Revises: 20260314_0002
Create Date: 2026-03-14 01:10:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260314_0003"
down_revision = "20260314_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "forensic_universal_royalty_events",
        sa.Column("event_id", sa.String(), nullable=False),
        sa.Column("work_id", sa.String(), nullable=True),
        sa.Column("isrc", sa.String(), nullable=True),
        sa.Column("iswc", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("artist_name", sa.String(), nullable=True),
        sa.Column("writer_name", sa.String(), nullable=True),
        sa.Column("publisher_name", sa.String(), nullable=True),
        sa.Column("distributor", sa.String(), nullable=True),
        sa.Column("platform", sa.String(), nullable=True),
        sa.Column("usage_type", sa.String(), nullable=True),
        sa.Column("usage_count", sa.Integer(), nullable=False),
        sa.Column("payout_amount", sa.Float(), nullable=False),
        sa.Column("payout_currency", sa.String(), nullable=False),
        sa.Column("statement_period_start", sa.Date(), nullable=True),
        sa.Column("statement_period_end", sa.Date(), nullable=True),
        sa.Column("source_file_id", sa.String(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("metadata_flags", sa.Text(), nullable=False),
        sa.Column("ingestion_timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index("ix_forensic_ure_work_id", "forensic_universal_royalty_events", ["work_id"])
    op.create_index("ix_forensic_ure_isrc", "forensic_universal_royalty_events", ["isrc"])
    op.create_index("ix_forensic_ure_iswc", "forensic_universal_royalty_events", ["iswc"])
    op.create_index("ix_forensic_ure_artist_name", "forensic_universal_royalty_events", ["artist_name"])
    op.create_index("ix_forensic_ure_distributor", "forensic_universal_royalty_events", ["distributor"])
    op.create_index("ix_forensic_ure_platform", "forensic_universal_royalty_events", ["platform"])
    op.create_index("ix_forensic_ure_source_file_id", "forensic_universal_royalty_events", ["source_file_id"])
    op.create_index("ix_forensic_ure_ingestion_timestamp", "forensic_universal_royalty_events", ["ingestion_timestamp"])

    op.create_table(
        "catalog_graph_nodes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("node_type", sa.String(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("attributes_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_catalog_graph_nodes_artist_id", "catalog_graph_nodes", ["artist_id"])
    op.create_index("ix_catalog_graph_nodes_node_type", "catalog_graph_nodes", ["node_type"])
    op.create_index("ix_catalog_graph_nodes_external_id", "catalog_graph_nodes", ["external_id"])

    op.create_table(
        "catalog_graph_edges",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("source_node_id", sa.String(), nullable=False),
        sa.Column("target_node_id", sa.String(), nullable=False),
        sa.Column("edge_type", sa.String(), nullable=False),
        sa.Column("attributes_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["source_node_id"], ["catalog_graph_nodes.id"]),
        sa.ForeignKeyConstraint(["target_node_id"], ["catalog_graph_nodes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_catalog_graph_edges_artist_id", "catalog_graph_edges", ["artist_id"])
    op.create_index("ix_catalog_graph_edges_source_node_id", "catalog_graph_edges", ["source_node_id"])
    op.create_index("ix_catalog_graph_edges_target_node_id", "catalog_graph_edges", ["target_node_id"])
    op.create_index("ix_catalog_graph_edges_edge_type", "catalog_graph_edges", ["edge_type"])


def downgrade() -> None:
    op.drop_index("ix_catalog_graph_edges_edge_type", table_name="catalog_graph_edges")
    op.drop_index("ix_catalog_graph_edges_target_node_id", table_name="catalog_graph_edges")
    op.drop_index("ix_catalog_graph_edges_source_node_id", table_name="catalog_graph_edges")
    op.drop_index("ix_catalog_graph_edges_artist_id", table_name="catalog_graph_edges")
    op.drop_table("catalog_graph_edges")

    op.drop_index("ix_catalog_graph_nodes_external_id", table_name="catalog_graph_nodes")
    op.drop_index("ix_catalog_graph_nodes_node_type", table_name="catalog_graph_nodes")
    op.drop_index("ix_catalog_graph_nodes_artist_id", table_name="catalog_graph_nodes")
    op.drop_table("catalog_graph_nodes")

    op.drop_index("ix_forensic_ure_ingestion_timestamp", table_name="forensic_universal_royalty_events")
    op.drop_index("ix_forensic_ure_source_file_id", table_name="forensic_universal_royalty_events")
    op.drop_index("ix_forensic_ure_platform", table_name="forensic_universal_royalty_events")
    op.drop_index("ix_forensic_ure_distributor", table_name="forensic_universal_royalty_events")
    op.drop_index("ix_forensic_ure_artist_name", table_name="forensic_universal_royalty_events")
    op.drop_index("ix_forensic_ure_iswc", table_name="forensic_universal_royalty_events")
    op.drop_index("ix_forensic_ure_isrc", table_name="forensic_universal_royalty_events")
    op.drop_index("ix_forensic_ure_work_id", table_name="forensic_universal_royalty_events")
    op.drop_table("forensic_universal_royalty_events")
