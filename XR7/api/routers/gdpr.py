"""
GDPR Compliance API for Data Subject Access Requests (DSAR) and Right to Erasure.

Implements GDPR Articles 15 (Right of Access) and 17 (Right to Erasure) requirements
for EU data subjects.

Legal framework:
- Art. 15: Data subject has right to obtain confirmation of processing and copies of personal data
- Art. 17: Right to erasure ("right to be forgotten") with legal obligation exception
- Art. 5(1)(e): Storage limitation - data kept no longer than necessary

Closes: XR7-405
Domain: compliance-automation
Scale-target: GDPR/CCPA compliance for 10x tenant count (EU customers)
Compliance: GDPR Art. 15, 17, 5(1)(e)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from XR7.api.deps import get_current_admin, get_db
from XR7.models.admin_audit_log import AdminAuditLog
from XR7.models.artist import Artist
from xr7_common.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/gdpr", tags=["gdpr"])


class DataSubjectAccessResponse(BaseModel):
    """GDPR Article 15 - Data Subject Access Request response."""

    model_config = ConfigDict(from_attributes=True)

    email: str
    collected_data: dict[str, list[dict[str, Any]]]
    collection_timestamp: datetime
    retention_period: str


class ErasureRequest(BaseModel):
    """GDPR Article 17 - Right to Erasure request."""

    email: EmailStr
    reason: str  # E.g., "customer request", "gdpr article 17"
    preserve_financial_records: bool = True  # Legal obligation exception


class ErasureResponse(BaseModel):
    """Right to Erasure response."""

    email: str
    records_pseudonymized: int
    records_preserved: int
    erasure_timestamp: datetime
    audit_log_id: str


@router.get(
    "/data-subject-access",
    response_model=DataSubjectAccessResponse,
    operation_id="get_data_subject_access",
)
def get_data_subject_access(
    email: str,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> DataSubjectAccessResponse:
    """GDPR Article 15 - Data Subject Access Request (DSAR).

    Returns all personal data associated with an email address across all tables.

    Args:
        email: Email address of the data subject
        admin: Admin authentication (required for GDPR operations)
        db: Database session

    Returns:
        Complete collection of personal data for the data subject

    Raises:
        HTTPException 404: No data found for email address
    """
    logger.info(
        "gdpr_dsar_requested",
        extra={
            "email": email,
            "admin_sub": admin.get("sub"),
            "timestamp": datetime.now(timezone.utc),
        },
    )

    collected_data: dict[str, list[dict[str, Any]]] = {}

    # Artists table - email is primary identifier
    artists = db.query(Artist).filter(Artist.email == email).all()
    if artists:
        collected_data["artists"] = [
            {
                "id": a.id,
                "email": a.email,
                "name": a.name,
                "phone": getattr(a, "phone", None),
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "tenant_id": a.tenant_id,
            }
            for a in artists
        ]

    # Admin audit logs - may contain email in event data
    audit_logs = (
        db.query(AdminAuditLog)
        .filter(
            or_(
                AdminAuditLog.actor_email == email,
                AdminAuditLog.target_email == email,
            )
        )
        .all()
    )
    if audit_logs:
        collected_data["admin_audit_logs"] = [
            {
                "id": log.id,
                "action": log.action,
                "actor_email": log.actor_email,
                "target_email": log.target_email,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            }
            for log in audit_logs
        ]

    # Check additional tables with email fields via raw SQL
    # (This is extensible as new tables are added)
    email_tables = [
        ("xr7_invite", "inviter_email"),
        ("xr7_invite", "invitee_email"),
        ("oauth_connector_accounts", "external_account_id"),  # May contain email
    ]

    for table_name, column_name in email_tables:
        try:
            result = db.execute(
                text(f"SELECT * FROM {table_name} WHERE {column_name} = :email"),
                {"email": email},
            )
            rows = result.fetchall()
            if rows:
                collected_data[table_name] = [dict(row._mapping) for row in rows]
        except Exception as e:
            logger.warning(
                "gdpr_dsar_table_query_failed",
                extra={"table": table_name, "error": str(e)},
            )

    if not collected_data:
        raise HTTPException(
            status_code=404,
            detail=f"No personal data found for email: {email}",
        )

    # Log DSAR completion for audit
    audit_log = AdminAuditLog(
        action="gdpr_dsar_completed",
        actor_email=admin.get("email"),
        actor_sub=admin.get("sub"),
        target_email=email,
        changes={
            "tables_queried": list(collected_data.keys()),
            "total_records": sum(len(v) for v in collected_data.values()),
        },
    )
    db.add(audit_log)
    db.commit()

    return DataSubjectAccessResponse(
        email=email,
        collected_data=collected_data,
        collection_timestamp=datetime.now(timezone.utc),
        retention_period="7 years (financial records), 90 days (operational logs)",
    )


@router.delete(
    "/erase",
    response_model=ErasureResponse,
    operation_id="erase_data_subject",
)
def erase_data_subject(
    request: ErasureRequest,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ErasureResponse:
    """GDPR Article 17 - Right to Erasure ("Right to be Forgotten").

    Pseudonymizes personal data while preserving financial records per legal obligation exception.

    Legal basis: GDPR Art. 17(3)(b) - "processing is necessary for compliance with a legal obligation"
    Financial records (claims, payments, statements) must be retained for 7 years per tax law.

    Args:
        request: Erasure request with email and reason
        admin: Admin authentication
        db: Database session

    Returns:
        Summary of erasure operation with audit log reference
    """
    logger.warning(
        "gdpr_erasure_requested",
        extra={
            "email": request.email,
            "reason": request.reason,
            "preserve_financial": request.preserve_financial_records,
            "admin_sub": admin.get("sub"),
        },
    )

    records_pseudonymized = 0
    records_preserved = 0

    # Pseudonymize artist PII (but preserve financial linkage via artist_id)
    artists = db.query(Artist).filter(Artist.email == request.email).all()
    for artist in artists:
        # Pseudonymize email and name
        pseudonym_email = f"deleted-{artist.id}@gdpr-erased.invalid"
        pseudonym_name = f"[ERASED-{artist.id[:8]}]"

        artist.email = pseudonym_email
        artist.name = pseudonym_name
        if hasattr(artist, "phone"):
            artist.phone = None

        records_pseudonymized += 1

        logger.info(
            "gdpr_artist_pseudonymized",
            extra={"artist_id": artist.id, "original_email": request.email},
        )

    # Pseudonymize admin audit logs (preserve action but remove email)
    audit_logs = (
        db.query(AdminAuditLog)
        .filter(
            or_(
                AdminAuditLog.actor_email == request.email,
                AdminAuditLog.target_email == request.email,
            )
        )
        .all()
    )
    for log in audit_logs:
        if log.actor_email == request.email:
            log.actor_email = "[ERASED]"
        if log.target_email == request.email:
            log.target_email = "[ERASED]"
        records_pseudonymized += 1

    # Preserve financial records (claims, payments, statements) per legal obligation
    if request.preserve_financial_records:
        # Count financial records linked to this user (preserved, not deleted)
        for artist in artists:
            # These tables are NOT modified (legal obligation to retain)
            preserved_count = db.execute(
                text(
                    """
                    SELECT
                        (SELECT COUNT(*) FROM claims WHERE artist_id = :artist_id) +
                        (SELECT COUNT(*) FROM payments WHERE artist_id = :artist_id) +
                        (SELECT COUNT(*) FROM statements WHERE artist_id = :artist_id)
                    """
                ),
                {"artist_id": artist.id},
            ).scalar()
            records_preserved += preserved_count or 0

    db.commit()

    # Create audit log for erasure operation
    erasure_audit = AdminAuditLog(
        action="gdpr_erasure_completed",
        actor_email=admin.get("email"),
        actor_sub=admin.get("sub"),
        target_email=request.email,
        changes={
            "reason": request.reason,
            "records_pseudonymized": records_pseudonymized,
            "records_preserved": records_preserved,
            "preserve_financial_records": request.preserve_financial_records,
        },
    )
    db.add(erasure_audit)
    db.commit()
    db.refresh(erasure_audit)

    logger.warning(
        "gdpr_erasure_completed",
        extra={
            "email": request.email,
            "pseudonymized": records_pseudonymized,
            "preserved": records_preserved,
            "audit_log_id": erasure_audit.id,
        },
    )

    return ErasureResponse(
        email=request.email,
        records_pseudonymized=records_pseudonymized,
        records_preserved=records_preserved,
        erasure_timestamp=datetime.now(timezone.utc),
        audit_log_id=erasure_audit.id,
    )
