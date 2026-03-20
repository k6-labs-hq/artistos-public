"""Case Rooms — collaborative per-claim workspaces.

Endpoints:
  POST   /case-rooms                                  – create room
  GET    /case-rooms/{room_id}                        – get room detail
  GET    /artists/{artist_id}/case-rooms              – list rooms for artist
  PATCH  /case-rooms/{room_id}/status                 – update status (close/escalate)
  POST   /case-rooms/{room_id}/members                – add member
  GET    /case-rooms/{room_id}/members                – list members
  DELETE /case-rooms/{room_id}/members/{email}        – remove member
  POST   /case-rooms/{room_id}/comments               – post comment
  GET    /case-rooms/{room_id}/comments               – list timeline
  PATCH  /case-rooms/{room_id}/comments/{comment_id} – edit comment
  GET    /case-rooms/{room_id}/attachments            – list attachments
  POST   /case-rooms/{room_id}/approvals              – request approval
  GET    /case-rooms/{room_id}/approvals              – list approvals
  POST   /case-rooms/{room_id}/approvals/{approval_id}/decide – record decision
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.case_room import (
    AddMemberRequest,
    ApprovalDecision,
    CaseApproval,
    CaseApprovalSchema,
    CaseAttachment,
    CaseAttachmentSchema,
    CaseComment,
    CaseCommentSchema,
    CaseRoom,
    CaseRoomCreate,
    CaseRoomMember,
    CaseRoomMemberRole,
    CaseRoomMemberSchema,
    CaseRoomSchema,
    CaseRoomStatus,
    DecideApprovalRequest,
    PostCommentRequest,
    RequestApprovalRequest,
)

router = APIRouter(tags=["case-rooms"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_room_or_404(room_id: str, db: Session) -> CaseRoom:
    room = db.query(CaseRoom).filter(CaseRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Case room not found")
    return room


def _require_min_role(
    room_id: str,
    actor_email: str | None,
    required_role: CaseRoomMemberRole,
    db: Session,
) -> None:
    """Raise 403 if actor does not have at least required_role in the room."""
    if not actor_email:
        return  # unauthenticated callers allowed in dev; tighten per deployment
    role_order = {
        CaseRoomMemberRole.VIEWER: 0,
        CaseRoomMemberRole.COMMENTER: 1,
        CaseRoomMemberRole.APPROVER: 2,
        CaseRoomMemberRole.OWNER: 3,
    }
    member = (
        db.query(CaseRoomMember)
        .filter(
            CaseRoomMember.room_id == room_id,
            CaseRoomMember.email == actor_email,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this case room")
    if role_order.get(member.role, -1) < role_order.get(required_role, 99):
        raise HTTPException(status_code=403, detail="Insufficient role for this action")


# ---------------------------------------------------------------------------
# Room CRUD
# ---------------------------------------------------------------------------

@router.post(
    "/case-rooms",
    response_model=CaseRoomSchema,
    status_code=201,
    summary="Create a case room",
)
def create_case_room(
    body: CaseRoomCreate,
    x_actor_email: Optional[str] = Header(default=None, alias="X-Actor-Email"),
    db: Session = Depends(get_db),
) -> CaseRoom:
    room = CaseRoom(
        artist_id=body.artist_id,
        claim_id=body.claim_id,
        title=body.title,
        sla_deadline_at=body.sla_deadline_at,
        org_id=body.org_id,
        created_by=x_actor_email,
    )
    db.add(room)
    db.flush()
    # Auto-add creator as owner
    if x_actor_email:
        db.add(
            CaseRoomMember(
                room_id=room.id,
                email=x_actor_email,
                role=CaseRoomMemberRole.OWNER,
            )
        )
    db.commit()
    db.refresh(room)
    return room


@router.get(
    "/case-rooms/{room_id}",
    response_model=CaseRoomSchema,
    summary="Get case room detail",
)
def get_case_room(room_id: str, db: Session = Depends(get_db)) -> CaseRoom:
    return _get_room_or_404(room_id, db)


@router.get(
    "/artists/{artist_id}/case-rooms",
    response_model=List[CaseRoomSchema],
    summary="List case rooms for an artist",
)
def list_case_rooms(
    artist_id: str,
    status: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> List[CaseRoom]:
    q = db.query(CaseRoom).filter(CaseRoom.artist_id == artist_id)
    if status:
        q = q.filter(CaseRoom.status == status)
    return q.order_by(CaseRoom.created_at.desc()).limit(limit).all()


class UpdateStatusRequest(CaseRoomCreate):
    status: CaseRoomStatus


@router.patch(
    "/case-rooms/{room_id}/status",
    response_model=CaseRoomSchema,
    summary="Update case room status",
)
def update_case_room_status(
    room_id: str,
    body: dict,
    x_actor_email: Optional[str] = Header(default=None, alias="X-Actor-Email"),
    db: Session = Depends(get_db),
) -> CaseRoom:
    room = _get_room_or_404(room_id, db)
    _require_min_role(room_id, x_actor_email, CaseRoomMemberRole.OWNER, db)
    new_status = body.get("status")
    if new_status:
        room.status = new_status
        if new_status in (CaseRoomStatus.CLOSED, CaseRoomStatus.APPROVED):
            room.closed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(room)
    return room


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

@router.post(
    "/case-rooms/{room_id}/members",
    response_model=CaseRoomMemberSchema,
    status_code=201,
    summary="Add a member to a case room",
)
def add_member(
    room_id: str,
    body: AddMemberRequest,
    x_actor_email: Optional[str] = Header(default=None, alias="X-Actor-Email"),
    db: Session = Depends(get_db),
) -> CaseRoomMember:
    room = _get_room_or_404(room_id, db)
    _require_min_role(room_id, x_actor_email, CaseRoomMemberRole.OWNER, db)
    existing = (
        db.query(CaseRoomMember)
        .filter(CaseRoomMember.room_id == room_id, CaseRoomMember.email == body.email)
        .first()
    )
    if existing:
        existing.role = body.role
        existing.is_external = body.is_external
        db.commit()
        db.refresh(existing)
        return existing
    member = CaseRoomMember(
        room_id=room_id,
        email=body.email,
        display_name=body.display_name,
        role=body.role,
        is_external=body.is_external,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.get(
    "/case-rooms/{room_id}/members",
    response_model=List[CaseRoomMemberSchema],
    summary="List case room members",
)
def list_members(room_id: str, db: Session = Depends(get_db)) -> List[CaseRoomMember]:
    _get_room_or_404(room_id, db)
    return db.query(CaseRoomMember).filter(CaseRoomMember.room_id == room_id).all()


@router.delete(
    "/case-rooms/{room_id}/members/{email}",
    status_code=204,
    summary="Remove a member from a case room",
)
def remove_member(
    room_id: str,
    email: str,
    x_actor_email: Optional[str] = Header(default=None, alias="X-Actor-Email"),
    db: Session = Depends(get_db),
):
    _get_room_or_404(room_id, db)
    _require_min_role(room_id, x_actor_email, CaseRoomMemberRole.OWNER, db)
    db.query(CaseRoomMember).filter(
        CaseRoomMember.room_id == room_id, CaseRoomMember.email == email
    ).delete()
    db.commit()


# ---------------------------------------------------------------------------
# Comments / Timeline
# ---------------------------------------------------------------------------

@router.post(
    "/case-rooms/{room_id}/comments",
    response_model=CaseCommentSchema,
    status_code=201,
    summary="Post a comment to a case room",
)
def post_comment(
    room_id: str,
    body: PostCommentRequest,
    db: Session = Depends(get_db),
) -> CaseComment:
    _get_room_or_404(room_id, db)
    comment = CaseComment(
        room_id=room_id,
        author_email=body.author_email,
        body=body.body,
        mentions=body.mentions,
        parent_id=body.parent_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get(
    "/case-rooms/{room_id}/comments",
    response_model=List[CaseCommentSchema],
    summary="List case room timeline (comments)",
)
def list_comments(
    room_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> List[CaseComment]:
    _get_room_or_404(room_id, db)
    return (
        db.query(CaseComment)
        .filter(CaseComment.room_id == room_id)
        .order_by(CaseComment.created_at.asc())
        .limit(limit)
        .all()
    )


@router.patch(
    "/case-rooms/{room_id}/comments/{comment_id}",
    response_model=CaseCommentSchema,
    summary="Edit a case room comment",
)
def edit_comment(
    room_id: str,
    comment_id: str,
    body: dict,
    x_actor_email: Optional[str] = Header(default=None, alias="X-Actor-Email"),
    db: Session = Depends(get_db),
) -> CaseComment:
    _get_room_or_404(room_id, db)
    comment = (
        db.query(CaseComment)
        .filter(CaseComment.id == comment_id, CaseComment.room_id == room_id)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if x_actor_email and comment.author_email != x_actor_email:
        raise HTTPException(status_code=403, detail="Can only edit your own comments")
    if "body" in body:
        comment.body = body["body"]
        comment.edited = True
    db.commit()
    db.refresh(comment)
    return comment


# ---------------------------------------------------------------------------
# Attachments
# ---------------------------------------------------------------------------

@router.get(
    "/case-rooms/{room_id}/attachments",
    response_model=List[CaseAttachmentSchema],
    summary="List case room attachments (role-filtered)",
)
def list_attachments(
    room_id: str,
    x_actor_email: Optional[str] = Header(default=None, alias="X-Actor-Email"),
    db: Session = Depends(get_db),
) -> List[CaseAttachment]:
    _get_room_or_404(room_id, db)
    role_order = {
        CaseRoomMemberRole.VIEWER: 0,
        CaseRoomMemberRole.COMMENTER: 1,
        CaseRoomMemberRole.APPROVER: 2,
        CaseRoomMemberRole.OWNER: 3,
    }
    actor_level = 0
    if x_actor_email:
        member = (
            db.query(CaseRoomMember)
            .filter(
                CaseRoomMember.room_id == room_id,
                CaseRoomMember.email == x_actor_email,
            )
            .first()
        )
        actor_level = role_order.get(
            CaseRoomMemberRole(member.role) if member else CaseRoomMemberRole.VIEWER, 0
        )

    attachments = db.query(CaseAttachment).filter(CaseAttachment.room_id == room_id).all()
    return [
        a
        for a in attachments
        if role_order.get(CaseRoomMemberRole(a.min_role_required), 99) <= actor_level
    ]


# ---------------------------------------------------------------------------
# Approvals
# ---------------------------------------------------------------------------

@router.post(
    "/case-rooms/{room_id}/approvals",
    response_model=CaseApprovalSchema,
    status_code=201,
    summary="Request approval in a case room",
)
def request_approval(
    room_id: str,
    body: RequestApprovalRequest,
    db: Session = Depends(get_db),
) -> CaseApproval:
    room = _get_room_or_404(room_id, db)
    approval = CaseApproval(
        room_id=room_id,
        requested_by=body.requested_by,
        approver_email=body.approver_email,
        due_at=body.due_at,
    )
    db.add(approval)
    room.status = CaseRoomStatus.PENDING_APPROVAL
    db.commit()
    db.refresh(approval)
    return approval


@router.get(
    "/case-rooms/{room_id}/approvals",
    response_model=List[CaseApprovalSchema],
    summary="List approvals for a case room",
)
def list_approvals(room_id: str, db: Session = Depends(get_db)) -> List[CaseApproval]:
    _get_room_or_404(room_id, db)
    return db.query(CaseApproval).filter(CaseApproval.room_id == room_id).all()


@router.post(
    "/case-rooms/{room_id}/approvals/{approval_id}/decide",
    response_model=CaseApprovalSchema,
    summary="Record an approval decision",
)
def decide_approval(
    room_id: str,
    approval_id: str,
    body: DecideApprovalRequest,
    db: Session = Depends(get_db),
) -> CaseApproval:
    room = _get_room_or_404(room_id, db)
    approval = (
        db.query(CaseApproval)
        .filter(CaseApproval.id == approval_id, CaseApproval.room_id == room_id)
        .first()
    )
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    approval.decision = body.decision
    approval.notes = body.notes
    approval.decided_at = datetime.now(timezone.utc)
    if body.decision == ApprovalDecision.APPROVED:
        room.status = CaseRoomStatus.APPROVED
        room.closed_at = datetime.now(timezone.utc)
    elif body.decision == ApprovalDecision.REJECTED:
        room.status = CaseRoomStatus.OPEN
    db.commit()
    db.refresh(approval)
    return approval
