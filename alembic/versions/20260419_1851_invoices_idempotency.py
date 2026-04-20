"""Add invoices table with database-level idempotency for revenue integrity.

Revision ID: 20260419_1851
Revises: 20260419_0041
Create Date: 2026-04-19 18:51:00.000000

TDD-BILL-001 Remediation: Database-level unique constraint on claim_id ensures
that duplicate invoice creation (via Celery retry after process crash) is prevented
at the database layer, not relying on in-memory application state.

Previous implementation used in-memory dict which was lost on process restart,
creating double-billing risk under Celery retry scenarios.

Closes: TDD-BILL-001
Domain: billing-integrity
Severity: CRITICAL
Compliance: SOC 2 CC6.1 — Logical access controls (revenue integrity)
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260419_1851"
down_revision = "20260419_0041"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create invoices table with idempotency constraint."""
    op.create_table(
        "invoices",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("claim_id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("recovered_amount", sa.Float(), nullable=False),
        sa.Column("contingency_fee", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False, server_default="USD"),
        sa.Column(
            "status",
            sa.Enum("PENDING", "PAID", "CANCELLED", "REFUNDED", name="invoicestatus"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_invoices"),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], name="fk_invoices_claim_id"),
        sa.ForeignKeyConstraint(["artist_id"], ["artists.id"], name="fk_invoices_artist_id"),
        # TDD-BILL-001: CRITICAL idempotency constraint
        # Prevents duplicate invoices for same claim under Celery retry + process crash
        sa.UniqueConstraint("claim_id", name="uq_invoices_claim_id"),
        # Business logic constraints
        sa.CheckConstraint("recovered_amount >= 0", name="ck_invoices_recovered_amount_positive"),
        sa.CheckConstraint("contingency_fee >= 0", name="ck_invoices_contingency_fee_positive"),
        sa.CheckConstraint(
            "contingency_fee <= recovered_amount", name="ck_invoices_fee_not_exceeds_recovery"
        ),
    )

    # Performance indexes
    op.create_index("ix_invoices_claim_id", "invoices", ["claim_id"], unique=True)
    op.create_index("ix_invoices_artist_id", "invoices", ["artist_id"])
    op.create_index("ix_invoices_created_at", "invoices", ["created_at"])


def downgrade() -> None:
    """Drop invoices table."""
    op.drop_index("ix_invoices_created_at", table_name="invoices")
    op.drop_index("ix_invoices_artist_id", table_name="invoices")
    op.drop_index("ix_invoices_claim_id", table_name="invoices")
    op.drop_table("invoices")

    # Drop enum type (PostgreSQL-specific)
    op.execute("DROP TYPE IF EXISTS invoicestatus")
