"""Team management endpoints with role-based access control.

Feature #8: Collaborative role-based access

RESTful API for managing artist team members:
- List team members
- Invite new team members (requires MANAGER role)
- Remove team members (requires MANAGER role)
- Check user permissions

Roles:
- ARTIST: Owner with upload/view permissions
- MANAGER: Extended permissions + team management
- ATTORNEY: Legal-specific permissions (claims, evidence)
- ANALYST: Internal admin permissions (advance approval, ML review)
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.team_access import TeamMemberSchema, TeamRole
from XR7.services.rbac_service import Permission, RBACService
from XR7.services.router_v21_phase1 import router_service_for

router = APIRouter(tags=["teams"])
_router_service = router_service_for("teams")


class AddTeamMemberRequest(BaseModel):
    user_email: EmailStr
    role: TeamRole


class CheckPermissionRequest(BaseModel):
    user_email: EmailStr
    permission: Permission


@router.get("/artists/{artist_id}/team")
def list_team_members(
    artist_id: str,
    user_email: str,  # From auth middleware in production
    db: Session = Depends(get_db),
):
    """
    List all team members for an artist.

    Feature #8: Collaborative RBAC

    Requires VIEW_TEAM permission (MANAGER, ANALYST roles).

    Returns:
        List of team members with roles
    """
    _router_service.get_artist_or_404(artist_id, db)

    rbac = RBACService(db)

    # Check permission
    rbac.require_permission(artist_id, user_email, Permission.VIEW_TEAM)

    from XR7.models.team_access import TeamMember

    members = db.query(TeamMember).filter(TeamMember.artist_id == artist_id).all()

    return {
        "artist_id": artist_id,
        "team_members": [TeamMemberSchema.model_validate(m).model_dump() for m in members],
    }


@router.post("/artists/{artist_id}/team")
def add_team_member(
    artist_id: str,
    payload: AddTeamMemberRequest,
    user_email: str,  # From auth middleware in production
    db: Session = Depends(get_db),
):
    """
    Add team member to artist with specific role.

    Feature #8: Collaborative RBAC

    Requires INVITE_TEAM permission (MANAGER role).

    Roles:
    - ARTIST: Owner with basic permissions
    - MANAGER: Team management + export permissions
    - ATTORNEY: Legal-specific permissions

    Returns:
        Created team member

    Security:
        - Audit logged with added_by user
        - Email validation prevents typos
        - Duplicate detection
    """
    _router_service.get_artist_or_404(artist_id, db)

    rbac = RBACService(db)

    # Permission check is done in add_team_member()
    member = rbac.add_team_member(
        artist_id=artist_id,
        user_email=payload.user_email,
        role=payload.role,
        added_by=user_email,
    )

    return {
        "status": "added",
        "team_member": TeamMemberSchema.model_validate(member).model_dump(),
    }


@router.delete("/artists/{artist_id}/team/{member_email}")
def remove_team_member(
    artist_id: str,
    member_email: str,
    user_email: str,  # From auth middleware in production
    db: Session = Depends(get_db),
):
    """
    Remove team member from artist.

    Feature #8: Collaborative RBAC

    Requires INVITE_TEAM permission (MANAGER role).

    Args:
        artist_id: Artist identifier
        member_email: Email of team member to remove
        user_email: Email of user performing removal (from auth)

    Returns:
        Confirmation of removal

    Security:
        - Audit logged with removed_by user
        - Cannot remove last ARTIST role (prevents lockout)
    """
    _router_service.get_artist_or_404(artist_id, db)

    rbac = RBACService(db)

    # Permission check is done in remove_team_member()
    rbac.remove_team_member(
        artist_id=artist_id,
        user_email=member_email,
        removed_by=user_email,
    )

    return {"status": "removed", "user_email": member_email}


@router.post("/artists/{artist_id}/team/check-permission")
def check_user_permission(
    artist_id: str,
    payload: CheckPermissionRequest,
    db: Session = Depends(get_db),
):
    """
    Check if user has specific permission for artist.

    Feature #8: Collaborative RBAC

    Used for frontend UI authorization (e.g., show/hide buttons).

    Args:
        artist_id: Artist identifier
        payload: User email and permission to check

    Returns:
        Boolean indicating whether user has permission

    Example:
        >>> POST /artists/art_123/team/check-permission
        >>> {"user_email": "lawyer@example.com", "permission": "update_claims"}
        >>> {"has_permission": true, "role": "attorney"}
    """
    _router_service.get_artist_or_404(artist_id, db)

    rbac = RBACService(db)

    has_permission = rbac.check_permission(
        artist_id=artist_id,
        user_email=payload.user_email,
        required_permission=payload.permission,
    )

    role = rbac.get_user_role(artist_id, payload.user_email)

    return {
        "has_permission": has_permission,
        "role": role.value if role else None,
        "permission": payload.permission.value,
    }


@router.get("/artists/{artist_id}/team/{member_email}/permissions")
def list_user_permissions(
    artist_id: str,
    member_email: str,
    db: Session = Depends(get_db),
):
    """
    List all permissions for a specific team member.

    Feature #8: Collaborative RBAC

    Returns all permissions the user has based on their role.

    Args:
        artist_id: Artist identifier
        member_email: Team member email

    Returns:
        List of Permission enums
    """
    _router_service.get_artist_or_404(artist_id, db)

    rbac = RBACService(db)

    permissions = rbac.list_permissions(artist_id, member_email)
    role = rbac.get_user_role(artist_id, member_email)

    return {
        "artist_id": artist_id,
        "user_email": member_email,
        "role": role.value if role else None,
        "permissions": [p.value for p in permissions],
    }
