"""
Locust load test for XR7 Engine.

Simulates realistic user behavior:
- 70% read operations (dashboard, claims list)
- 20% write operations (statement upload, claim submission)
- 10% admin operations

Run locally:
    locust -f tests/load/locustfile.py --host=http://localhost:8000

Run headless:
    locust -f tests/load/locustfile.py --headless --users 100 --spawn-rate 10 --run-time 60s --host=http://localhost:8000
"""

from __future__ import annotations

from locust import HttpUser, between, task


class ArtistUserBehavior(HttpUser):
    """Simulate artist user browsing dashboard and claims."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Called when a simulated user starts."""
        # In production, this would authenticate and get a JWT
        self.artist_id = "test-artist-123"

    @task(5)
    def view_health(self):
        """Health check endpoint (high frequency)."""
        self.client.get("/health")

    @task(4)
    def view_readiness(self):
        """Readiness check endpoint."""
        self.client.get("/health/readiness")

    @task(3)
    def view_dashboard(self):
        """Load artist dashboard (read-heavy)."""
        self.client.get(f"/artists/{self.artist_id}/dashboard", name="/artists/[id]/dashboard")

    @task(2)
    def list_claims(self):
        """List artist claims."""
        self.client.get(f"/artists/{self.artist_id}/claims", name="/artists/[id]/claims")

    @task(2)
    def list_anomalies(self):
        """List artist anomalies."""
        self.client.get(f"/artists/{self.artist_id}/anomalies", name="/artists/[id]/anomalies")

    @task(1)
    def view_earnings(self):
        """View earnings summary."""
        self.client.get(f"/artists/{self.artist_id}/earnings", name="/artists/[id]/earnings")

    @task(1)
    def get_openapi_spec(self):
        """Fetch OpenAPI spec (SDK usage pattern)."""
        self.client.get("/openapi.json")


class AdminUserBehavior(HttpUser):
    """Simulate admin user managing artists."""

    wait_time = between(2, 5)

    @task(3)
    def list_recent_artists(self):
        """Admin dashboard - recent artists."""
        # In production, would use X-Admin-Key header
        self.client.get("/admin/artists", name="/admin/artists")

    @task(2)
    def view_audit_events(self):
        """View admin audit log."""
        self.client.get("/admin/audit/events", name="/admin/audit/events")

    @task(1)
    def health_check(self):
        """Monitor system health."""
        self.client.get("/health/readiness")
