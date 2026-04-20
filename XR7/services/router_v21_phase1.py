"""Router service helper that provides common API utilities.

Provides a lightweight wrapper around deps.py canonical functions
for consistent error handling across all routers.
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404 as _get_artist_or_404
from XR7.models.artist import Artist


class RouterService:
    """Service class providing common router utilities."""
    
    def __init__(self, router_name: str):
        self.router_name = router_name
    
    def get_artist_or_404(self, artist_id: str, db: Session) -> Artist:
        """
        Fetch artist or raise 404.
        
        Delegates to canonical deps.get_artist_or_404.
        """
        return _get_artist_or_404(artist_id, db)


def router_service_for(router_name: str) -> RouterService:
    """
    Factory function to create router service instance.
    
    Usage:
        ```python
        router = APIRouter(tags=["exports"])
        _router_service = router_service_for("exports")
        
        @router.get("/artists/{artist_id}/reports/summary")
        def export_summary(artist_id: str, db: Session = Depends(get_db)):
            _router_service.get_artist_or_404(artist_id, db)
            # ... rest of endpoint
        ```
    
    Args:
        router_name: Name of the router (for logging/debugging)
    
    Returns:
        RouterService instance
    """
    return RouterService(router_name)
