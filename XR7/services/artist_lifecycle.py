from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from XR7.models.artist import Artist, ArtistLifecycleStatus
from XR7.services.founder_program import FounderAssignmentResult, assign_founder_slot_on_activation


def promote_to_onboarded(artist: Artist) -> bool:
    """Promote NEW artist to ONBOARDED. Returns True when state changed."""
    current = ArtistLifecycleStatus(artist.status)
    if current == ArtistLifecycleStatus.NEW:
        artist.status = ArtistLifecycleStatus.ONBOARDED.value
        artist.onboarded_at = datetime.now(timezone.utc)
        return True
    return False


def promote_to_active(db: Session, artist: Artist) -> tuple[bool, FounderAssignmentResult | None]:
    """Promote NEW/ONBOARDED artist to ACTIVE and assign founder slot atomically."""
    current = ArtistLifecycleStatus(artist.status)
    if current in {ArtistLifecycleStatus.NEW, ArtistLifecycleStatus.ONBOARDED}:
        if current == ArtistLifecycleStatus.NEW and artist.onboarded_at is None:
            artist.onboarded_at = datetime.now(timezone.utc)
        artist.status = ArtistLifecycleStatus.ACTIVE.value
        artist.activated_at = datetime.now(timezone.utc)
        founder_result = assign_founder_slot_on_activation(db, artist)
        return True, founder_result
    return False, None
