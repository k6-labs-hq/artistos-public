"""claim status audit trigger

Revision ID: 20260416_2123
Revises: 20260416_0033
Create Date: 2026-04-16

CRITICAL COMPLIANCE FIX: Add immutable audit log for claim status transitions.

Without this audit log, disputes could claim XR7 never filed claims or changed
statuses fraudulently. This creates a cryptographically-chained audit trail
in the immutable_ledger_entries table that proves:
  - When each status transition occurred (timestamp)
  - What the old and new status values were
  - Who made the change (user context if available)
  - Hash chain prevents tampering with historical records

Implementation uses SQLAlchemy event listeners (XR7.services.claim_status_audit)
instead of database triggers, making it database-agnostic and testable.

Legal protection for:
  - Statute of limitations disputes (proof of filing date)
  - Attorney malpractice claims (proof we filed on time)
  - Artist disputes about payment delays (status progression proof)
  - Regulatory audits (complete compliance trail)

NOTE: This migration is intentionally empty. The audit functionality is
implemented via SQLAlchemy event listeners which are automatically registered
when the application starts. See XR7/services/claim_status_audit.py.
"""

from __future__ import annotations

revision = "20260416_2123"
down_revision = "20260416_0033"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    No database changes needed.

    Claim status auditing is handled by SQLAlchemy event listeners in
    XR7.services.claim_status_audit which automatically log status changes
    to the immutable_ledger_entries table.

    The event listener is registered when the application imports the module.
    """
    pass


def downgrade() -> None:
    """
    No database changes to revert.

    To disable claim status auditing, remove the import of
    XR7.services.claim_status_audit from the application startup.
    """
    pass
