"""Shared FastAPI dependencies and helper utilities for all routers.

DOMAIN BOUNDARY NOTE:
    This module contains CANONICAL versions of common FastAPI operations.
    All API routers and application services should import from here to avoid
    duplication. This ensures consistent error handling and response formats
    across the API surface.

    Do NOT duplicate these functions in other modules. If you need similar
    functionality, either:
    1. Use this canonical version if you're in the API/service layer
    2. Create a separate domain-specific variant if you need different behavior
       (e.g., raising ValueError instead of HTTPException for pure business logic)
"""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from XR7.models.artist import Artist


def get_artist_or_404(artist_id: str, db: Session) -> Artist:
    """Fetch an artist by primary key or raise HTTP 404.
    
    CANONICAL VERSION: Do not duplicate this logic elsewhere in the codebase.
    All API routes and application services should use this function.
    
    Args:
        artist_id: The artist's unique identifier (UUID string)
        db: SQLAlchemy database session
        
    Returns:
        Artist: The artist record
        
    Raises:
        HTTPException: 404 if artist not found
        
    Domain Boundary:
        - For API routes: Use this directly
        - For background jobs/services: Use this or extract to a shared service layer
        - For pure domain logic: Consider raising ValueError instead and catching
          at the API boundary
    """
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist
