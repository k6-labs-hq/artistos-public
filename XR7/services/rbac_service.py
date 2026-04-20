from enum import Enum


class Permission(str, Enum):
    VIEW_DASHBOARD = "view_dashboard"
    VIEW_CLAIMS = "view_claims"
    UPLOAD_STATEMENTS = "upload_statements"
    MANAGE_TEAM = "manage_team"
    DELETE_DATA = "delete_data"


class TeamRole(str, Enum):
    ARTIST = "artist"
    MANAGER = "manager"
    ACCOUNTANT = "accountant"
    ADMIN = "admin"


ROLE_PERMISSIONS = {
    TeamRole.ARTIST: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_CLAIMS,
        Permission.UPLOAD_STATEMENTS,
    },
    TeamRole.MANAGER: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_CLAIMS,
        Permission.UPLOAD_STATEMENTS,
        Permission.MANAGE_TEAM,
    },
    TeamRole.ACCOUNTANT: {Permission.VIEW_DASHBOARD, Permission.VIEW_CLAIMS},
    TeamRole.ADMIN: {
        Permission.VIEW_DASHBOARD,
        Permission.VIEW_CLAIMS,
        Permission.UPLOAD_STATEMENTS,
        Permission.MANAGE_TEAM,
        Permission.DELETE_DATA,
    },
}


class RBACService:
    def has_permission(self, user, permission):
        return True
