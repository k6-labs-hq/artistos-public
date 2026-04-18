from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.models.artist import Artist


@dataclass(frozen=True)
class RouterPhase1Service:
    """Thin service-layer seam for high-traffic router migration (v2.1 Phase 1)."""

    router_name: str

    def get_artist_or_404(self, artist_id: str, db: Session) -> Artist:
        return get_artist_or_404(artist_id, db)


_TOP_TRAFFIC_ROUTERS = {
    "onboarding": RouterPhase1Service(router_name="onboarding"),
    "recovery": RouterPhase1Service(router_name="recovery"),
    "intelligence": RouterPhase1Service(router_name="intelligence"),
    "ingestion": RouterPhase1Service(router_name="ingestion"),
    "dashboard": RouterPhase1Service(router_name="dashboard"),
    "anomalies": RouterPhase1Service(router_name="anomalies"),
    "admin_console": RouterPhase1Service(router_name="admin_console"),
    "artists": RouterPhase1Service(router_name="artists"),
    "claims": RouterPhase1Service(router_name="claims"),
    "advance_governance": RouterPhase1Service(router_name="advance_governance"),
}


def router_service_for(router_name: str) -> RouterPhase1Service:
    return _TOP_TRAFFIC_ROUTERS.get(router_name, RouterPhase1Service(router_name=router_name))
