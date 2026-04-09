"""
Artist-query helpers that encapsulate DB filter logic for Celery tasks.

Each function executes exactly one bounded query and returns a plain
``list[str]`` of artist IDs.  Keeping these here prevents query logic from
leaking into task bodies, making both layer easier to test independently.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from XR7.models.artist import Artist, ArtistLifecycleStatus
from XR7.models.statement import Statement


def artists_pending_onboarding(db: Session) -> list[str]:
    """Return IDs of artists that have not yet reached ACTIVE status."""
    return [
        a.id
        for a in db.query(Artist)
        .filter(Artist.status != ArtistLifecycleStatus.ACTIVE.value)
        .all()
    ]


def all_artist_ids(db: Session) -> list[str]:
    """Return IDs of every artist in the DB (used for follow-up scans)."""
    return [row.id for row in db.query(Artist.id).all()]


def artist_ids_with_new_statements(db: Session, since: datetime) -> list[str]:
    """Return sorted, deduplicated artist IDs that have statements uploaded after *since*."""
    rows = (
        db.query(Statement.artist_id)
        .join(Artist, Artist.id == Statement.artist_id)
        .filter(Statement.uploaded_at >= since)
        .filter(Artist.status == ArtistLifecycleStatus.ACTIVE.value)
        .all()
    )
    return sorted({r.artist_id for r in rows})


def artist_ids_with_soundcloud_statements(db: Session) -> list[str]:
    """Return sorted, deduplicated artist IDs that have at least one SoundCloud statement."""
    rows = (
        db.query(Statement.artist_id)
        .filter(Statement.format_detected == "soundcloud")
        .all()
    )
    return sorted({r.artist_id for r in rows})


def active_soundcloud_artist_ids_since(db: Session, since: datetime) -> list[str]:
    """SoundCloud artists whose statements were uploaded after *since*."""
    rows = (
        db.query(Statement.artist_id)
        .filter(
            Statement.format_detected == "soundcloud",
            Statement.uploaded_at >= since,
        )
        .all()
    )
    return sorted({r.artist_id for r in rows})
