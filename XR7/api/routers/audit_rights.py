"""Audit rights endpoints for workflow automation.

Feature #16: Audit Rights Workflow Automation (Product Backlog #18)

Provides attorneys and analysts with tools to:
- Track audit rights exercise workflows
- Generate formal audit demand letters
- Manage counterparty communication
- Document settlement outcomes
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.services.audit_rights_service import (
    AuditRightsWorkflow,
    AuditWorkflowStatus,
    generate_audit_demand_letter,
)
from XR7.services.router_v21_phase1 import router_service_for

router = APIRouter(tags=["audit-rights"])
_router_service = router_service_for("audit_rights")


# Pydantic models for request/response
class CreateAuditWorkflowRequest(BaseModel):
    """Request body for creating a new audit workflow."""

    artist_id: str = Field(..., description="Artist ID")
    contract_id: Optional[str] = Field(None, description="Contract ID if available")
    counterparty_name: str = Field(..., description="Counterparty legal name")
    counterparty_address: Optional[str] = Field(None, description="Counterparty mailing address")
    counterparty_contact: Optional[str] = Field(None, description="Counterparty contact person")
    audit_period_start: Optional[datetime] = Field(None, description="Audit period start date")
    audit_period_end: Optional[datetime] = Field(None, description="Audit period end date")


class GenerateLetterRequest(BaseModel):
    """Request body for generating audit demand letter."""

    artist_name: str = Field(..., description="Artist legal name")
    contract_name: str = Field(..., description="Contract title")
    contract_date: str = Field(..., description="Contract execution date")
    audit_clause_reference: str = Field(
        ..., description="Audit clause section reference (e.g., 'Section 12.3')"
    )
    proposed_audit_date: datetime = Field(..., description="Proposed audit inspection date")
    attorney_name: str = Field(..., description="Attorney representing artist")
    auditor_name: str = Field(
        default="Independent Certified Public Accountant", description="CPA firm"
    )


class UpdateWorkflowStatusRequest(BaseModel):
    """Request body for updating workflow status."""

    status: AuditWorkflowStatus = Field(..., description="New workflow status")
    notes: Optional[str] = Field(None, description="Update notes")


class AuditWorkflowResponse(BaseModel):
    """Response model for audit workflow."""

    id: str
    artist_id: str
    contract_id: Optional[str]
    counterparty_name: str
    counterparty_address: Optional[str]
    counterparty_contact: Optional[str]
    status: str
    letter_generated_at: Optional[datetime]
    letter_sent_at: Optional[datetime]
    letter_template_version: Optional[str]
    audit_period_start: Optional[datetime]
    audit_period_end: Optional[datetime]
    audit_scheduled_date: Optional[datetime]
    discrepancies_found: Optional[str]
    settlement_amount: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


@router.get("/artists/{artist_id}/audit-workflows")
def list_audit_workflows(
    artist_id: str,
    status: Optional[AuditWorkflowStatus] = None,
    db: Session = Depends(get_db),
) -> List[AuditWorkflowResponse]:
    """
    List audit rights workflows for an artist.

    **Query parameters:**
    - status: Filter by workflow status (optional)

    **Returns:**
    - List of audit workflows ordered by created_at desc

    **Use cases:**
    - Attorney dashboard showing active audit workflows
    - Analyst review of settlement outcomes
    - Historical audit tracking
    """
    _router_service.get_artist_or_404(artist_id, db)

    query = db.query(AuditRightsWorkflow).filter(AuditRightsWorkflow.artist_id == artist_id)

    if status:
        query = query.filter(AuditRightsWorkflow.status == status)

    workflows = query.order_by(AuditRightsWorkflow.created_at.desc()).all()

    return [AuditWorkflowResponse.model_validate(w) for w in workflows]


@router.post("/artists/{artist_id}/audit-workflows")
def create_audit_workflow(
    artist_id: str,
    request: CreateAuditWorkflowRequest,
    db: Session = Depends(get_db),
) -> AuditWorkflowResponse:
    """
    Create a new audit rights workflow.

    **Use case:**
    - Attorney or analyst identifies audit rights clause in contract
    - System creates workflow tracking record
    - Status initialized to IDENTIFIED

    **Acceptance criteria:**
    - Validates artist_id exists
    - Creates workflow with IDENTIFIED status
    - Returns workflow ID for subsequent operations
    """
    _router_service.get_artist_or_404(artist_id, db)

    # Ensure request artist_id matches path parameter
    if request.artist_id != artist_id:
        raise HTTPException(status_code=400, detail="artist_id mismatch between path and body")

    workflow = AuditRightsWorkflow(
        artist_id=request.artist_id,
        contract_id=request.contract_id,
        counterparty_name=request.counterparty_name,
        counterparty_address=request.counterparty_address,
        counterparty_contact=request.counterparty_contact,
        status=AuditWorkflowStatus.IDENTIFIED,
        audit_period_start=request.audit_period_start,
        audit_period_end=request.audit_period_end,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return AuditWorkflowResponse.model_validate(workflow)


@router.get("/artists/{artist_id}/audit-workflows/{workflow_id}")
def get_audit_workflow(
    artist_id: str,
    workflow_id: str,
    db: Session = Depends(get_db),
) -> AuditWorkflowResponse:
    """
    Get detailed audit workflow information.

    **Returns:**
    - Complete workflow state including all dates and notes
    - Current status
    - Letter generation history
    - Settlement information if applicable
    """
    _router_service.get_artist_or_404(artist_id, db)

    workflow = (
        db.query(AuditRightsWorkflow)
        .filter(
            AuditRightsWorkflow.id == workflow_id,
            AuditRightsWorkflow.artist_id == artist_id,
        )
        .first()
    )

    if not workflow:
        raise HTTPException(status_code=404, detail=f"Audit workflow {workflow_id} not found")

    return AuditWorkflowResponse.model_validate(workflow)


@router.post("/artists/{artist_id}/audit-workflows/{workflow_id}/generate-letter")
def generate_letter(
    artist_id: str,
    workflow_id: str,
    request: GenerateLetterRequest,
    db: Session = Depends(get_db),
):
    """
    Generate formal audit demand letter from template.

    **Use case:**
    - Attorney ready to exercise audit rights
    - System generates formal demand letter with legal language
    - Updates workflow status to LETTER_DRAFTED
    - Returns plain text letter for review

    **Letter includes:**
    - Audit clause reference
    - Proposed audit dates
    - Required records list
    - Attorney signature block
    - 30-day response deadline

    **Acceptance criteria:**
    - Validates workflow exists and is in appropriate state
    - Generates letter from template
    - Returns plain text for attorney review/editing
    - Updates workflow state
    """
    _router_service.get_artist_or_404(artist_id, db)

    try:
        letter_text = generate_audit_demand_letter(
            db=db,
            workflow_id=workflow_id,
            artist_name=request.artist_name,
            contract_name=request.contract_name,
            contract_date=request.contract_date,
            audit_clause_reference=request.audit_clause_reference,
            proposed_audit_date=request.proposed_audit_date,
            attorney_name=request.attorney_name,
            auditor_name=request.auditor_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"audit_demand_{workflow_id}_{timestamp}.txt"

    return Response(
        content=letter_text,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.patch("/artists/{artist_id}/audit-workflows/{workflow_id}")
def update_workflow_status(
    artist_id: str,
    workflow_id: str,
    request: UpdateWorkflowStatusRequest,
    db: Session = Depends(get_db),
) -> AuditWorkflowResponse:
    """
    Update audit workflow status.

    **Use cases:**
    - Mark letter as sent (LETTER_SENT)
    - Record counterparty response (RESPONSE_RECEIVED)
    - Schedule audit date (AUDIT_SCHEDULED)
    - Document audit completion (AUDIT_COMPLETED)
    - Record settlement (SETTLEMENT_NEGOTIATED)
    - Close workflow (CLOSED)

    **Acceptance criteria:**
    - Validates workflow exists
    - Updates status and updated_at timestamp
    - Returns updated workflow state
    """
    _router_service.get_artist_or_404(artist_id, db)

    workflow = (
        db.query(AuditRightsWorkflow)
        .filter(
            AuditRightsWorkflow.id == workflow_id,
            AuditRightsWorkflow.artist_id == artist_id,
        )
        .first()
    )

    if not workflow:
        raise HTTPException(status_code=404, detail=f"Audit workflow {workflow_id} not found")

    workflow.status = request.status
    workflow.updated_at = datetime.now(timezone.utc)

    # Auto-populate letter_sent_at when status changes to LETTER_SENT
    if request.status == AuditWorkflowStatus.LETTER_SENT and not workflow.letter_sent_at:
        workflow.letter_sent_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(workflow)

    return AuditWorkflowResponse.model_validate(workflow)


@router.get("/audit-workflows/stats")
def get_audit_workflow_stats(db: Session = Depends(get_db)):
    """
    Get system-wide audit workflow statistics.

    **Use case:**
    - Admin dashboard showing audit activity
    - Platform health monitoring

    **Returns:**
    - Total workflows by status
    - Average time-to-settlement
    - Total settlement value
    """
    from sqlalchemy import func

    # Count workflows by status
    status_counts = (
        db.query(
            AuditRightsWorkflow.status,
            func.count(AuditRightsWorkflow.id).label("count"),
        )
        .group_by(AuditRightsWorkflow.status)
        .all()
    )

    return {
        "by_status": {status: count for status, count in status_counts},
        "total_workflows": sum(count for _, count in status_counts),
    }
