from __future__ import annotations

from datetime import datetime, timezone

from XR7.models.artist import Artist, ArtistLifecycleStatus


def promote_to_onboarded(artist: Artist) -> bool:
    """Promote NEW artist to ONBOARDED. Returns True when state changed."""
    current = ArtistLifecycleStatus(artist.status)
    if current == ArtistLifecycleStatus.NEW:
        artist.status = ArtistLifecycleStatus.ONBOARDED.value
        artist.onboarded_at = datetime.now(timezone.utc)
        return True
    return False


def promote_to_active(artist: Artist) -> bool:
    """Promote NEW/ONBOARDED artist to ACTIVE. Returns True when state changed."""
    current = ArtistLifecycleStatus(artist.status)
    if current in {ArtistLifecycleStatus.NEW, ArtistLifecycleStatus.ONBOARDED}:
        if current == ArtistLifecycleStatus.NEW and artist.onboarded_at is None:
            artist.onboarded_at = datetime.now(timezone.utc)
        artist.status = ArtistLifecycleStatus.ACTIVE.value
        artist.activated_at = datetime.now(timezone.utc)
        return True
    return False
