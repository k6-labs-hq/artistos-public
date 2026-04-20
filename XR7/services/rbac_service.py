"""Role-based access control service for collaborative artist teams.

Feature #8: Collaborative role-based access

Permission matrix for artist, manager, and attorney roles:

ARTIST:
- View own dashboard, claims, statements
- Upload statements and contracts
- Accept terms and agreements
- Trigger ingestion and analysis
- Request advances (if VIP)

MANAGER:
- All artist permissions
- View team members
- Invite additional team members (managers, attorneys)
- Configure notification preferences
- Download reports (CSV/PDF)

ATTORNEY:
- View claims and evidence packets
- Download evidence PDFs
- Update claim status (with audit logging)
- Review SOL deadlines and risk scoring
- Access legal exports (CSV)

ANALYST (internal only):
- Approve/reject advance requests
- Review low-confidence ML extractions
- Access admin panels and audit logs
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy.orm import Session

from XR7.models.team_access import TeamMember, TeamRole

if TYPE_CHECKING:
    pass


class Permission(str, Enum):
    """Granular permissions for RBAC enforcement."""
    
    # Read permissions
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_CLAIMS = "view_claims"
    VIEW_STATEMENTS = "view_statements"
    VIEW_TEAM = "view_team"
    VIEW_EVIDENCE = "view_evidence"
    VIEW_ADMIN = "view_admin"
    
    # Write permissions
    UPLOAD_STATEMENTS = "upload_statements"
    UPLOAD_CONTRACTS = "upload_contracts"
    UPDATE_CLAIMS = "update_claims"
    INVITE_TEAM = "invite_team"
    APPROVE_ADVANCES = "approve_advances"
    
    # Export permissions
    EXPORT_REPORTS = "export_reports"
    EXPORT_EVIDENCE = "export_evidence"
    EXPORT_LEGAL_CSV = "export_legal_csv"


# Permission matrix: role → allowed permissions
ROLE_PERMISSIONS = {
    TeamRole.ARTIST: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_CLAIMS,
        Permission.VIEW_STATEMENTS,
        Permission.UPLOAD_STATEMENTS,
        Permission.UPLOAD_CONTRACTS,
    },
    TeamRole.MANAGER: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_CLAIMS,
        Permission.VIEW_STATEMENTS,
        Permission.VIEW_TEAM,
        Permission.UPLOAD_STATEMENTS,
        Permission.UPLOAD_CONTRACTS,
        Permission.INVITE_TEAM,
        Permission.EXPORT_REPORTS,
    },
    TeamRole.ATTORNEY: {
        Permission.VIEW_CLAIMS,
        Permission.VIEW_EVIDENCE,
        Permission.UPDATE_CLAIMS,
        Permission.EXPORT_EVIDENCE,
        Permission.EXPORT_LEGAL_CSV,
    },
    TeamRole.ANALYST: {
        Permission.VIEW_ADMIN,
        Permission.APPROVE_ADVANCES,
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_CLAIMS,
        Permission.VIEW_STATEMENTS,
        Permission.VIEW_EVIDENCE,
    },
}


class RBACService:
    """Role-based access control enforcement service."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_role(self, artist_id: str, user_email: str) -> TeamRole | None:
        """
        Get user's role for a specific artist.
        
        Args:
            artist_id: Artist identifier
            user_email: User email address
        
        Returns:
            TeamRole if user has access, None if no access
        """
        member = (
            self.db.query(TeamMember)
            .filter(
                TeamMember.artist_id == artist_id,
                TeamMember.user_email == user_email,
            )
            .first()
        )
        
        if not member:
            return None
        
        return TeamRole(member.role)
    
    def check_permission(
        self,
        artist_id: str,
        user_email: str,
        required_permission: Permission,
    ) -> bool:
        """
        Check if user has specific permission for artist.
        
        Args:
            artist_id: Artist identifier
            user_email: User email address
            required_permission: Permission to check
        
        Returns:
            True if user has permission, False otherwise
        """
        role = self.get_user_role(artist_id, user_email)
        
        if not role:
            return False
        
        allowed_permissions = ROLE_PERMISSIONS.get(role, set())
        return required_permission in allowed_permissions
    
    def require_permission(
        self,
        artist_id: str,
        user_email: str,
        required_permission: Permission,
    ) -> None:
        """
        Require user to have specific permission, raise 403 if not.
        
        Args:
            artist_id: Artist identifier
            user_email: User email address
            required_permission: Permission to check
        
        Raises:
            HTTPException: 403 Forbidden if user lacks permission
        
        Example:
            >>> rbac.require_permission("art_123", "user@example.com", Permission.UPDATE_CLAIMS)
            # Raises 403 if user is not an attorney
        """
        if not self.check_permission(artist_id, user_email, required_permission):
            role = self.get_user_role(artist_id, user_email)
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Insufficient permissions. Required: {required_permission.value}. "
                    f"Your role: {role.value if role else 'none'}"
                ),
            )
    
    def list_permissions(self, artist_id: str, user_email: str) -> list[Permission]:
        """
        List all permissions for user on artist.
        
        Args:
            artist_id: Artist identifier
            user_email: User email address
        
        Returns:
            List of Permission enums user has access to
        """
        role = self.get_user_role(artist_id, user_email)
        
        if not role:
            return []
        
        return list(ROLE_PERMISSIONS.get(role, set()))
    
    def add_team_member(
        self,
        artist_id: str,
        user_email: str,
        role: TeamRole,
        added_by: str,
    ) -> TeamMember:
        """
        Add team member to artist with specific role.
        
        Args:
            artist_id: Artist identifier
            user_email: New team member email
            role: TeamRole to assign
            added_by: Email of user adding this team member
        
        Returns:
            Created TeamMember
        
        Raises:
            HTTPException: 403 if added_by user lacks INVITE_TEAM permission
        """
        # Check if inviter has permission
        self.require_permission(artist_id, added_by, Permission.INVITE_TEAM)
        
        # Check if member already exists
        existing = (
            self.db.query(TeamMember)
            .filter(
                TeamMember.artist_id == artist_id,
                TeamMember.user_email == user_email,
            )
            .first()
        )
        
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"User {user_email} is already a team member"
            )
        
        # Create new team member
        member = TeamMember(
            artist_id=artist_id,
            user_email=user_email,
            role=role,
        )
        
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        
        return member
    
    def remove_team_member(
        self,
        artist_id: str,
        user_email: str,
        removed_by: str,
    ) -> None:
        """
        Remove team member from artist.
        
        Args:
            artist_id: Artist identifier
            user_email: Team member email to remove
            removed_by: Email of user performing removal
        
        Raises:
            HTTPException: 403 if removed_by user lacks INVITE_TEAM permission
        """
        # Check if remover has permission
        self.require_permission(artist_id, removed_by, Permission.INVITE_TEAM)
        
        member = (
            self.db.query(TeamMember)
            .filter(
                TeamMember.artist_id == artist_id,
                TeamMember.user_email == user_email,
            )
            .first()
        )
        
        if not member:
            raise HTTPException(status_code=404, detail=f"Team member {user_email} not found")
        
        self.db.delete(member)
        self.db.commit()
