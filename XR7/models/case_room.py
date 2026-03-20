"""Case Rooms — collaborative per-claim workspaces.

Tables:
  case_rooms          – one room per claim (or standalone), with SLA timer
  case_room_members   – role-aware membership (viewer/commenter/approver/owner)
  case_comments       – threaded comments with @mention support
  case_attachments    – role-scoped file attachments
  case_approvals      – formal approval workflow records
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, Enum, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class CaseRoomStatus(str, enum.Enum):
    OPEN = "open"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class CaseRoomMemberRole(str, enum.Enum):
    OWNER = "owner"
    APPROVER = "approver"
    COMMENTER = "commenter"
    VIEWER = "viewer"


class ApprovalDecision(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# CaseRoom
# ---------------------------------------------------------------------------

class CaseRoom(Base):
    __tablename__ = "case_rooms"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    claim_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(CaseRoomStatus), nullable=False, default=CaseRoomStatus.OPEN
    )
    # SLA: absolute deadline by which the room must reach a terminal state
    sla_deadline_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sla_breached: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    org_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    created_by: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


# ---------------------------------------------------------------------------
# CaseRoomMember
# ---------------------------------------------------------------------------

class CaseRoomMember(Base):
    __tablename__ = "case_room_members"
    __table_args__ = (
        UniqueConstraint("room_id", "email", name="uq_case_room_member"),
    )

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    room_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(
        Enum(CaseRoomMemberRole), nullable=False, default=CaseRoomMemberRole.VIEWER
    )
    is_external: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )  # external partner collaborator
    joined_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# CaseComment
# ---------------------------------------------------------------------------

class CaseComment(Base):
    __tablename__ = "case_comments"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    room_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    author_email: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # comma-separated email list of @mentioned users
    mentions: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[str | None] = mapped_column(
        String, nullable=True
    )  # thread parent
    edited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# CaseAttachment
# ---------------------------------------------------------------------------

class CaseAttachment(Base):
    __tablename__ = "case_attachments"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    room_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    uploaded_by: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    storage_key: Mapped[str] = mapped_column(String, nullable=False)
    content_type: Mapped[str | None] = mapped_column(String, nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(String, nullable=True)
    # minimum role required to view this attachment
    min_role_required: Mapped[str] = mapped_column(
        Enum(CaseRoomMemberRole), nullable=False, default=CaseRoomMemberRole.VIEWER
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# CaseApproval
# ---------------------------------------------------------------------------

class CaseApproval(Base):
    __tablename__ = "case_approvals"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    room_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    requested_by: Mapped[str] = mapped_column(String, nullable=False)
    approver_email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    decision: Mapped[str] = mapped_column(
        Enum(ApprovalDecision), nullable=False, default=ApprovalDecision.PENDING
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    # SLA: approver must decide by this time
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class CaseRoomSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    artist_id: str
    claim_id: str | None
    title: str
    status: str
    sla_deadline_at: datetime | None
    sla_breached: bool
    org_id: str | None
    created_by: str | None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None


class CaseRoomCreate(BaseModel):
    artist_id: str
    claim_id: str | None = None
    title: str
    sla_deadline_at: datetime | None = None
    org_id: str | None = None


class CaseRoomMemberSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    room_id: str
    email: str
    display_name: str | None
    role: str
    is_external: bool
    joined_at: datetime


class AddMemberRequest(BaseModel):
    email: str
    display_name: str | None = None
    role: CaseRoomMemberRole = CaseRoomMemberRole.VIEWER
    is_external: bool = False


class CaseCommentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    room_id: str
    author_email: str
    body: str
    mentions: str | None
    parent_id: str | None
    edited: bool
    created_at: datetime
    updated_at: datetime


class PostCommentRequest(BaseModel):
    author_email: str
    body: str
    mentions: str | None = None
    parent_id: str | None = None


class CaseAttachmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    room_id: str
    uploaded_by: str
    filename: str
    storage_key: str
    content_type: str | None
    size_bytes: int | None
    min_role_required: str
    created_at: datetime


class CaseApprovalSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    room_id: str
    requested_by: str
    approver_email: str
    decision: str
    notes: str | None
    due_at: datetime | None
    decided_at: datetime | None
    created_at: datetime


class RequestApprovalRequest(BaseModel):
    requested_by: str
    approver_email: str
    due_at: datetime | None = None


class DecideApprovalRequest(BaseModel):
    decision: ApprovalDecision
    notes: str | None = None
