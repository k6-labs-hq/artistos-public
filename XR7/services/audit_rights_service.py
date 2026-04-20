"""Audit rights workflow automation service.

Feature #16: Audit Rights Workflow Automation (Product Backlog #18)

Generates formal audit demand letters from templates and tracks audit workflow state.

Workflow states:
- IDENTIFIED: Audit right clause detected in contract
- LETTER_DRAFTED: Demand letter generated from template
- LETTER_SENT: Demand letter sent to counterparty
- RESPONSE_RECEIVED: Counterparty acknowledged audit request
- AUDIT_SCHEDULED: Inspection date confirmed
- AUDIT_COMPLETED: Audit findings documented
- SETTLEMENT_NEGOTIATED: Discrepancies resolved
- CLOSED: Audit workflow complete

Value: Scale recovery operations by automating legal escalation.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, Session, mapped_column

from XR7.models.base import Base

if TYPE_CHECKING:
    pass


class AuditWorkflowStatus(str, enum.Enum):
    IDENTIFIED = "IDENTIFIED"
    LETTER_DRAFTED = "LETTER_DRAFTED"
    LETTER_SENT = "LETTER_SENT"
    RESPONSE_RECEIVED = "RESPONSE_RECEIVED"
    AUDIT_SCHEDULED = "AUDIT_SCHEDULED"
    AUDIT_COMPLETED = "AUDIT_COMPLETED"
    SETTLEMENT_NEGOTIATED = "SETTLEMENT_NEGOTIATED"
    CLOSED = "CLOSED"


class AuditRightsWorkflow(Base):
    """Audit rights workflow tracker."""

    __tablename__ = "audit_rights_workflows"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    contract_id: Mapped[str | None] = mapped_column(String, nullable=True)

    # Counterparty information
    counterparty_name: Mapped[str] = mapped_column(String, nullable=False)
    counterparty_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    counterparty_contact: Mapped[str | None] = mapped_column(String, nullable=True)

    # Workflow state
    status: Mapped[str] = mapped_column(
        Enum(AuditWorkflowStatus),
        default=AuditWorkflowStatus.IDENTIFIED,
        nullable=False,
    )

    # Demand letter details
    letter_generated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    letter_sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    letter_template_version: Mapped[str | None] = mapped_column(String, nullable=True)

    # Audit details
    audit_period_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    audit_period_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    audit_scheduled_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Findings
    discrepancies_found: Mapped[str | None] = mapped_column(Text, nullable=True)
    settlement_amount: Mapped[float | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# Letter template (simplified version - production would use Jinja2 templates)
AUDIT_DEMAND_LETTER_TEMPLATE = """
{date}

{counterparty_name}
{counterparty_address}

Re: Notice of Audit Rights Exercise — Artist: {artist_name}

Dear {counterparty_contact}:

Pursuant to Section {audit_clause_reference} of the {contract_name} dated {contract_date}, {artist_name} hereby exercises their contractual right to inspect and audit books, records, and accounts related to royalty payments for the period from {audit_period_start} to {audit_period_end}.

In accordance with the Agreement, we request that you make available for inspection all documents, ledgers, statements, and supporting materials related to:
- Gross receipts and net revenues from all exploitations
- Deductions, expenses, and recoupments applied
- Third-party payments and sub-licensing agreements
- Territory-specific breakdowns and currency conversions

We propose to conduct this audit on or around {proposed_audit_date} at your principal place of business, or at such other location and time as may be mutually agreed upon within thirty (30) days of this notice.

Our independent certified public accountant, {auditor_name}, will conduct the audit on behalf of the Artist. Please provide confirmation of your receipt of this notice and your availability for the proposed audit date within ten (10) business days.

If discrepancies are discovered, we reserve all rights under the Agreement including reimbursement of audit costs and interest on unpaid amounts.

Sincerely,

{attorney_name}
Attorney for {artist_name}

cc: {artist_name}
"""


def generate_audit_demand_letter(
    db: Session,
    workflow_id: str,
    artist_name: str,
    contract_name: str,
    contract_date: str,
    audit_clause_reference: str,
    proposed_audit_date: datetime,
    attorney_name: str,
    auditor_name: str = "Independent Certified Public Accountant",
) -> str:
    """
    Generate formal audit demand letter from template.

    Args:
        db: Database session
        workflow_id: AuditRightsWorkflow ID
        artist_name: Artist's legal name
        contract_name: Contract title
        contract_date: Contract execution date
        audit_clause_reference: Section reference (e.g., "Section 12.3")
        proposed_audit_date: Proposed date for audit inspection
        attorney_name: Attorney representing artist
        auditor_name: CPA firm conducting audit

    Returns:
        Formatted demand letter text
    """
    workflow = db.query(AuditRightsWorkflow).filter(AuditRightsWorkflow.id == workflow_id).first()

    if not workflow:
        raise ValueError(f"Audit workflow {workflow_id} not found")

    # Format letter
    letter_text = AUDIT_DEMAND_LETTER_TEMPLATE.format(
        date=datetime.now(timezone.utc).strftime("%B %d, %Y"),
        counterparty_name=workflow.counterparty_name,
        counterparty_address=workflow.counterparty_address or "[Address]",
        counterparty_contact=workflow.counterparty_contact or "To Whom It May Concern",
        artist_name=artist_name,
        audit_clause_reference=audit_clause_reference,
        contract_name=contract_name,
        contract_date=contract_date,
        audit_period_start=(
            workflow.audit_period_start or datetime.now(timezone.utc) - timedelta(days=365 * 3)
        ).strftime("%B %d, %Y"),
        audit_period_end=(workflow.audit_period_end or datetime.now(timezone.utc)).strftime(
            "%B %d, %Y"
        ),
        proposed_audit_date=proposed_audit_date.strftime("%B %d, %Y"),
        auditor_name=auditor_name,
        attorney_name=attorney_name,
    )

    # Update workflow state
    workflow.status = AuditWorkflowStatus.LETTER_DRAFTED
    workflow.letter_generated_at = datetime.now(timezone.utc)
    workflow.letter_template_version = "v1.0"
    db.commit()

    return letter_text
