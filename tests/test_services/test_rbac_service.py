"""Unit tests for rbac_service.py (Feature #8: Collaborative RBAC).

Test permission matrix and role-based access control without database dependencies where possible.
"""

import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from XR7.services.rbac_service import RBACService, Permission, ROLE_PERMISSIONS, TeamRole


class TestRBACService:
    """Unit tests for role-based access control service."""
    
    def test_role_permissions_matrix_completeness(self):
        """Test that all roles have defined permissions."""
        # Assert: All TeamRole values should have permission mappings
        for role in TeamRole:
            assert role in ROLE_PERMISSIONS
            assert isinstance(ROLE_PERMISSIONS[role], set)
            assert len(ROLE_PERMISSIONS[role]) > 0
    
    def test_artist_role_has_basic_permissions(self):
        """Test that ARTIST role has core read/upload permissions."""
        artist_perms = ROLE_PERMISSIONS[TeamRole.ARTIST]
        
        # Assert: Artist should have basic dashboard access
        assert Permission.VIEW_DASHBOARD in artist_perms
        assert Permission.VIEW_CLAIMS in artist_perms
        assert Permission.UPLOAD_STATEMENTS in artist_perms
        
        # Assert: Artist should NOT have admin/export permissions
        assert Permission.APPROVE_ADVANCES not in artist_perms
        assert Permission.VIEW_ADMIN not in artist_perms
    
    def test_manager_role_has_team_management(self):
        """Test that MANAGER role has team invite permissions."""
        manager_perms = ROLE_PERMISSIONS[TeamRole.MANAGER]
        
        # Assert: Manager should have all artist permissions plus more
        assert Permission.VIEW_DASHBOARD in manager_perms
        assert Permission.INVITE_TEAM in manager_perms
        assert Permission.EXPORT_REPORTS in manager_perms
        
        # Assert: Manager should NOT have admin-only permissions
        assert Permission.APPROVE_ADVANCES not in manager_perms
    
    def test_attorney_role_has_legal_permissions(self):
        """Test that ATTORNEY role has claim/evidence access."""
        attorney_perms = ROLE_PERMISSIONS[TeamRole.ATTORNEY]
        
        # Assert: Attorney should have legal-specific access
        assert Permission.VIEW_CLAIMS in attorney_perms
        assert Permission.VIEW_EVIDENCE in attorney_perms
        assert Permission.UPDATE_CLAIMS in attorney_perms
        assert Permission.EXPORT_LEGAL_CSV in attorney_perms
        
        # Assert: Attorney should NOT have general dashboard access
        assert Permission.VIEW_DASHBOARD not in attorney_perms
    
    def test_analyst_role_has_admin_permissions(self):
        """Test that ANALYST role has admin/approval permissions."""
        analyst_perms = ROLE_PERMISSIONS[TeamRole.ANALYST]
        
        # Assert: Analyst should have admin panel access
        assert Permission.VIEW_ADMIN in analyst_perms
        assert Permission.APPROVE_ADVANCES in analyst_perms
        
        # Assert: Analyst should NOT have invite permissions (internal role)
        assert Permission.INVITE_TEAM not in analyst_perms
    
    def test_check_permission_with_valid_role(self):
        """Test permission check succeeds for authorized role."""
        # Arrange
        mock_db = Mock()
        mock_member = Mock()
        mock_member.role = TeamRole.MANAGER.value
        mock_db.query.return_value.filter.return_value.first.return_value = mock_member
        
        rbac = RBACService(mock_db)
        
        # Act
        has_permission = rbac.check_permission(
            "art_123", "manager@example.com", Permission.INVITE_TEAM
        )
        
        # Assert
        assert has_permission is True
    
    def test_check_permission_with_invalid_role(self):
        """Test permission check fails for unauthorized role."""
        # Arrange
        mock_db = Mock()
        mock_member = Mock()
        mock_member.role = TeamRole.ARTIST.value
        mock_db.query.return_value.filter.return_value.first.return_value = mock_member
        
        rbac = RBACService(mock_db)
        
        # Act
        has_permission = rbac.check_permission(
            "art_123", "artist@example.com", Permission.APPROVE_ADVANCES
        )
        
        # Assert
        assert has_permission is False
    
    def test_require_permission_raises_403_when_unauthorized(self):
        """Test require_permission raises HTTPException 403 for unauthorized users."""
        # Arrange
        mock_db = Mock()
        mock_member = Mock()
        mock_member.role = TeamRole.ARTIST.value
        mock_db.query.return_value.filter.return_value.first.return_value = mock_member
        
        rbac = RBACService(mock_db)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            rbac.require_permission(
                "art_123", "artist@example.com", Permission.UPDATE_CLAIMS
            )
        
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in exc_info.value.detail
    
    def test_list_permissions_returns_all_role_permissions(self):
        """Test list_permissions returns complete permission set for role."""
        # Arrange
        mock_db = Mock()
        mock_member = Mock()
        mock_member.role = TeamRole.ATTORNEY.value
        mock_db.query.return_value.filter.return_value.first.return_value = mock_member
        
        rbac = RBACService(mock_db)
        
        # Act
        permissions = rbac.list_permissions("art_123", "lawyer@example.com")
        
        # Assert
        assert len(permissions) > 0
        assert Permission.VIEW_EVIDENCE in permissions
        assert Permission.UPDATE_CLAIMS in permissions
        assert Permission.APPROVE_ADVANCES not in permissions  # Not an attorney permission
