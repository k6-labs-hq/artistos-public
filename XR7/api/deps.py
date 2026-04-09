"""Shared FastAPI dependencies and helper utilities for all routers."""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from XR7.models.artist import Artist


def get_artist_or_404(artist_id: str, db: Session) -> Artist:
    """Fetch an artist by primary key or raise HTTP 404."""
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist
