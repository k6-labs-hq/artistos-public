"""artist lifecycle status, review queue, and admin audit tables

Revision ID: 20260314_0004
Revises: 20260314_0003
Create Date: 2026-03-14 02:05:00
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260314_0004"
down_revision = "20260314_0003"
branch_labels = None
depends_on = None


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        cols = insp.get_columns(table_name)
    except Exception:  # noqa: BLE001
        return False
    return any(c.get("name") == column_name for c in cols)


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        return table_name in insp.get_table_names()
    except Exception:  # noqa: BLE001
        return False


def upgrade() -> None:
    if _table_exists("artists"):
        if not _column_exists("artists", "status"):
            op.add_column("artists", sa.Column("status", sa.String(), nullable=False, server_default="NEW"))
        if not _column_exists("artists", "onboarded_at"):
            op.add_column("artists", sa.Column("onboarded_at", sa.DateTime(), nullable=True))
        if not _column_exists("artists", "activated_at"):
            op.add_column("artists", sa.Column("activated_at", sa.DateTime(), nullable=True))
        op.execute("UPDATE artists SET status = 'NEW' WHERE status IS NULL")

    if _table_exists("artists") and not _table_exists("review_items"):
        op.create_table(
            "review_items",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("artist_id", sa.String(), nullable=False),
            sa.Column("source_type", sa.String(), nullable=False),
            sa.Column("source_id", sa.String(), nullable=True),
            sa.Column("reason", sa.String(), nullable=False),
            sa.Column("priority_score", sa.Float(), nullable=False, server_default="0"),
            sa.Column("status", sa.String(), nullable=False, server_default="OPEN"),
            sa.Column("assigned_analyst_email", sa.String(), nullable=True),
            sa.Column("payload", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.Column("resolved_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["artist_id"], ["artists.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_review_items_artist_id", "review_items", ["artist_id"])
        op.create_index("ix_review_items_source_type", "review_items", ["source_type"])
        op.create_index("ix_review_items_source_id", "review_items", ["source_id"])
        op.create_index("ix_review_items_status", "review_items", ["status"])
        op.create_index("ix_review_items_assigned_analyst_email", "review_items", ["assigned_analyst_email"])
        op.create_index("ix_review_items_created_at", "review_items", ["created_at"])

    if _table_exists("review_items") and not _table_exists("review_assignments"):
        op.create_table(
            "review_assignments",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("review_item_id", sa.String(), nullable=False),
            sa.Column("analyst_email", sa.String(), nullable=False),
            sa.Column("assigned_at", sa.DateTime(), nullable=False),
            sa.Column("unassigned_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["review_item_id"], ["review_items.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_review_assignments_review_item_id", "review_assignments", ["review_item_id"])
        op.create_index("ix_review_assignments_analyst_email", "review_assignments", ["analyst_email"])

    if _table_exists("review_items") and not _table_exists("review_decisions"):
        op.create_table(
            "review_decisions",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("review_item_id", sa.String(), nullable=False),
            sa.Column("analyst_email", sa.String(), nullable=False),
            sa.Column("decision", sa.String(), nullable=False),
            sa.Column("notes", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["review_item_id"], ["review_items.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_review_decisions_review_item_id", "review_decisions", ["review_item_id"])
        op.create_index("ix_review_decisions_analyst_email", "review_decisions", ["analyst_email"])
        op.create_index("ix_review_decisions_created_at", "review_decisions", ["created_at"])

    if not _table_exists("admin_audit_logs"):
        op.create_table(
            "admin_audit_logs",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("actor", sa.String(), nullable=False),
            sa.Column("action", sa.String(), nullable=False),
            sa.Column("resource_type", sa.String(), nullable=False),
            sa.Column("resource_id", sa.String(), nullable=True),
            sa.Column("details", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_admin_audit_logs_actor", "admin_audit_logs", ["actor"])
        op.create_index("ix_admin_audit_logs_action", "admin_audit_logs", ["action"])
        op.create_index("ix_admin_audit_logs_resource_type", "admin_audit_logs", ["resource_type"])
        op.create_index("ix_admin_audit_logs_resource_id", "admin_audit_logs", ["resource_id"])
        op.create_index("ix_admin_audit_logs_created_at", "admin_audit_logs", ["created_at"])


def downgrade() -> None:
    if _table_exists("admin_audit_logs"):
        op.drop_index("ix_admin_audit_logs_created_at", table_name="admin_audit_logs")
        op.drop_index("ix_admin_audit_logs_resource_id", table_name="admin_audit_logs")
        op.drop_index("ix_admin_audit_logs_resource_type", table_name="admin_audit_logs")
        op.drop_index("ix_admin_audit_logs_action", table_name="admin_audit_logs")
        op.drop_index("ix_admin_audit_logs_actor", table_name="admin_audit_logs")
        op.drop_table("admin_audit_logs")

    if _table_exists("review_decisions"):
        op.drop_index("ix_review_decisions_created_at", table_name="review_decisions")
        op.drop_index("ix_review_decisions_analyst_email", table_name="review_decisions")
        op.drop_index("ix_review_decisions_review_item_id", table_name="review_decisions")
        op.drop_table("review_decisions")

    if _table_exists("review_assignments"):
        op.drop_index("ix_review_assignments_analyst_email", table_name="review_assignments")
        op.drop_index("ix_review_assignments_review_item_id", table_name="review_assignments")
        op.drop_table("review_assignments")

    if _table_exists("review_items"):
        op.drop_index("ix_review_items_created_at", table_name="review_items")
        op.drop_index("ix_review_items_assigned_analyst_email", table_name="review_items")
        op.drop_index("ix_review_items_status", table_name="review_items")
        op.drop_index("ix_review_items_source_id", table_name="review_items")
        op.drop_index("ix_review_items_source_type", table_name="review_items")
        op.drop_index("ix_review_items_artist_id", table_name="review_items")
        op.drop_table("review_items")

    if _table_exists("artists"):
        if _column_exists("artists", "activated_at"):
            op.drop_column("artists", "activated_at")
        if _column_exists("artists", "onboarded_at"):
            op.drop_column("artists", "onboarded_at")
        if _column_exists("artists", "status"):
            op.drop_column("artists", "status")
