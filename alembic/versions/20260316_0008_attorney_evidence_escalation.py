"""attorney evidence escalation fields and preferences

Revision ID: 20260316_0008
Revises: 20260316_0007
Create Date: 2026-03-16
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260316_0008"
down_revision = "20260316_0007"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        return table_name in insp.get_table_names()
    except Exception:  # noqa: BLE001
        return False


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        cols = insp.get_columns(table_name)
    except Exception:  # noqa: BLE001
        return False
    return any(c.get("name") == column_name for c in cols)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE claimstatus ADD VALUE IF NOT EXISTS 'PROOF_SUBMITTED'")

    if _table_exists("artists") and not _column_exists("artists", "default_attorney_grace_period_days"):
        op.add_column(
            "artists",
            sa.Column("default_attorney_grace_period_days", sa.Integer(), nullable=False, server_default="60"),
        )

    if _table_exists("claims"):
        if not _column_exists("claims", "payer_name"):
            op.add_column("claims", sa.Column("payer_name", sa.String(), nullable=True))
        if not _column_exists("claims", "payer_contact"):
            op.add_column("claims", sa.Column("payer_contact", sa.String(), nullable=True))
        if not _column_exists("claims", "original_due_date"):
            op.add_column("claims", sa.Column("original_due_date", sa.DateTime(), nullable=True))
        if not _column_exists("claims", "proof_submitted_at"):
            op.add_column("claims", sa.Column("proof_submitted_at", sa.DateTime(), nullable=True))
        if not _column_exists("claims", "grace_period_days"):
            op.add_column(
                "claims",
                sa.Column("grace_period_days", sa.Integer(), nullable=False, server_default="60"),
            )
        if not _column_exists("claims", "sol_deadline"):
            op.add_column("claims", sa.Column("sol_deadline", sa.DateTime(), nullable=True))
        if not _column_exists("claims", "communications"):
            op.add_column("claims", sa.Column("communications", sa.JSON(), nullable=True))
        if not _column_exists("claims", "anomaly_report"):
            op.add_column("claims", sa.Column("anomaly_report", sa.JSON(), nullable=True))
        if not _column_exists("claims", "supporting_documents"):
            op.add_column("claims", sa.Column("supporting_documents", sa.JSON(), nullable=True))
        if not _column_exists("claims", "attorney_file_generated"):
            op.add_column(
                "claims",
                sa.Column("attorney_file_generated", sa.Boolean(), nullable=False, server_default=sa.false()),
            )
        if not _column_exists("claims", "attorney_file_generated_at"):
            op.add_column("claims", sa.Column("attorney_file_generated_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    if _table_exists("claims"):
        if _column_exists("claims", "attorney_file_generated_at"):
            op.drop_column("claims", "attorney_file_generated_at")
        if _column_exists("claims", "attorney_file_generated"):
            op.drop_column("claims", "attorney_file_generated")
        if _column_exists("claims", "supporting_documents"):
            op.drop_column("claims", "supporting_documents")
        if _column_exists("claims", "anomaly_report"):
            op.drop_column("claims", "anomaly_report")
        if _column_exists("claims", "communications"):
            op.drop_column("claims", "communications")
        if _column_exists("claims", "sol_deadline"):
            op.drop_column("claims", "sol_deadline")
        if _column_exists("claims", "grace_period_days"):
            op.drop_column("claims", "grace_period_days")
        if _column_exists("claims", "proof_submitted_at"):
            op.drop_column("claims", "proof_submitted_at")
        if _column_exists("claims", "original_due_date"):
            op.drop_column("claims", "original_due_date")
        if _column_exists("claims", "payer_contact"):
            op.drop_column("claims", "payer_contact")
        if _column_exists("claims", "payer_name"):
            op.drop_column("claims", "payer_name")

    if _table_exists("artists") and _column_exists("artists", "default_attorney_grace_period_days"):
        op.drop_column("artists", "default_attorney_grace_period_days")
