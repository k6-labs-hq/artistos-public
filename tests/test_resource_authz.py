"""
Test resource-level authorization decorator.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi import Depends, Header
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import TestSession
from XR7.api.app import app
from XR7.api.authz import require_permission
from XR7.models.base import get_db
from XR7.models.artist import Artist
from XR7.models.team_access import TeamMember, TeamRole


# Test endpoint using the decorator
from fastapi import APIRouter

test_router = APIRouter()


@test_router.delete("/test/claims/{claim_id}")
@require_permission("delete", resource_type="claim")
def delete_test_claim(
    claim_id: str,
    db: Session = Depends(get_db),
    actor_email: str | None = Header(default=None, alias="X-Actor-Email"),
):
    return {"status": "deleted", "claim_id": claim_id}


# Mount the test router
app.include_router(test_router)

client = TestClient(app)


class TestResourceLevelAuthz:
    @pytest.fixture
    def setup_artist_and_team(self):
        """Create test artist and team members."""
        db = TestSession()
        try:
            artist_id = str(uuid.uuid4())
            artist = Artist(id=artist_id, name="Test Artist", email=f"artist_{artist_id[:8]}@test.com")
            db.add(artist)

            # Add manager
            manager = TeamMember(
                artist_id=artist_id,
                user_email="manager@test.com",
                role=TeamRole.MANAGER.value,
            )
            db.add(manager)

            # Add analyst
            analyst = TeamMember(
                artist_id=artist_id,
                user_email="analyst@test.com",
                role=TeamRole.ANALYST.value,
            )
            db.add(analyst)

            db.commit()
            return {"artist_id": artist_id, "manager_email": "manager@test.com", "analyst_email": "analyst@test.com"}
        finally:
            db.close()

    def test_delete_permission_allowed_for_manager(self, setup_artist_and_team):
        """Manager should be able to delete resources."""
        artist_id = setup_artist_and_team["artist_id"]
        manager_email = setup_artist_and_team["manager_email"]

        response = client.delete(
            f"/test/claims/{artist_id}",
            headers={"X-Actor-Email": manager_email},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "deleted"

    def test_delete_permission_denied_for_analyst(self, setup_artist_and_team):
        """Analyst should NOT be able to delete resources."""
        artist_id = setup_artist_and_team["artist_id"]
        analyst_email = setup_artist_and_team["analyst_email"]

        response = client.delete(
            f"/test/claims/{artist_id}",
            headers={"X-Actor-Email": analyst_email},
        )

        assert response.status_code == 403
        assert "Insufficient role" in response.json()["detail"]

    def test_delete_permission_denied_without_actor_email(self, setup_artist_and_team):
        """Request without actor email should be denied."""
        artist_id = setup_artist_and_team["artist_id"]

        response = client.delete(f"/test/claims/{artist_id}")

        assert response.status_code == 403
        assert "Authentication required" in response.json()["detail"]

    def test_delete_permission_denied_for_non_team_member(self, setup_artist_and_team):
        """Non-team member should be denied."""
        artist_id = setup_artist_and_team["artist_id"]

        response = client.delete(
            f"/test/claims/{artist_id}",
            headers={"X-Actor-Email": "outsider@test.com"},
        )

        assert response.status_code == 403
        assert "not a team member" in response.json()["detail"]
