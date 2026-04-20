"""Add audit_rights_workflows table for audit rights automation.

Feature #16: Audit Rights Workflow Automation (Product Backlog #18)

Create table for tracking audit rights exercise workflows:
- Formal audit demand letter generation
- 8-state workflow tracking (IDENTIFIED → CLOSED)
- Counterparty management
- Settlement tracking

Workflow states:
- IDENTIFIED: Audit right clause detected in contract
- LETTER_DRAFTED: Demand letter generated from template
- LETTER_SENT: Demand letter sent to counterparty
- RESPONSE_RECEIVED: Counterparty acknowledged
- AUDIT_SCHEDULED: Inspection date confirmed
- AUDIT_COMPLETED: Audit findings documented
- SETTLEMENT_NEGOTIATED: Discrepancies resolved
- CLOSED: Audit workflow complete

Revision ID: fbec60e49504
Revises: 20260419_0032
Create Date: 2026-04-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "fbec60e49504"
down_revision = "20260419_0032"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create audit_rights_workflows table."""
    
    # Create enum type for workflow status
    op.execute("""
        CREATE TYPE auditworkflowstatus AS ENUM (
            'IDENTIFIED', 
            'LETTER_DRAFTED', 
            'LETTER_SENT', 
            'RESPONSE_RECEIVED',
            'AUDIT_SCHEDULED', 
            'AUDIT_COMPLETED', 
            'SETTLEMENT_NEGOTIATED', 
            'CLOSED'
        )
    """)
    
    op.create_table(
        "audit_rights_workflows",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("artist_id", sa.String(), nullable=False),
        sa.Column("contract_id", sa.String(), nullable=True),
        sa.Column("counterparty_name", sa.String(), nullable=False),
        sa.Column("counterparty_address", sa.Text(), nullable=True),
        sa.Column("counterparty_contact", sa.String(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "IDENTIFIED",
                "LETTER_DRAFTED",
                "LETTER_SENT",
                "RESPONSE_RECEIVED",
                "AUDIT_SCHEDULED",
                "AUDIT_COMPLETED",
                "SETTLEMENT_NEGOTIATED",
                "CLOSED",
                name="auditworkflowstatus",
                create_type=False,
            ),
            nullable=False,
            server_default="IDENTIFIED",
        ),
        sa.Column("letter_generated_at", sa.DateTime(), nullable=True),
        sa.Column("letter_sent_at", sa.DateTime(), nullable=True),
        sa.Column("letter_template_version", sa.String(), nullable=True),
        sa.Column("audit_period_start", sa.DateTime(), nullable=True),
        sa.Column("audit_period_end", sa.DateTime(), nullable=True),
        sa.Column("audit_scheduled_date", sa.DateTime(), nullable=True),
        sa.Column("discrepancies_found", sa.Text(), nullable=True),
        sa.Column("settlement_amount", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create index on artist_id for filtering by artist
    op.create_index(
        "ix_audit_rights_workflows_artist_id",
        "audit_rights_workflows",
        ["artist_id"],
    )
    
    # Create index on status for workflow dashboard queries
    op.create_index(
        "ix_audit_rights_workflows_status",
        "audit_rights_workflows",
        ["status"],
    )
    
    # Create composite index for artist-specific workflow filtering
    op.create_index(
        "ix_audit_rights_workflows_artist_status",
        "audit_rights_workflows",
        ["artist_id", "status"],
    )


def downgrade() -> None:
    """Drop audit_rights_workflows table."""
    
    op.drop_index("ix_audit_rights_workflows_artist_status", table_name="audit_rights_workflows")
    op.drop_index("ix_audit_rights_workflows_status", table_name="audit_rights_workflows")
    op.drop_index("ix_audit_rights_workflows_artist_id", table_name="audit_rights_workflows")
    op.drop_table("audit_rights_workflows")
    op.execute("DROP TYPE IF EXISTS auditworkflowstatus")
