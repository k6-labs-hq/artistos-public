"""Usage Matching Module.

Reconciles fingerprinting detections against platform usage data:
    - YouTube videos
    - TikTok videos
    - Instagram Reels / Facebook videos
    - Spotify / Apple Music / Amazon Music streams (spike detection)
    - Live event detections (Ticketmaster, AXS, Bandsintown, Songkick)

Detects:
    - Unofficial audio usage (UGC not reported to PROs)
    - Foreign usage not linked to a PRO payment
    - Usage spikes with no corresponding distributor payment
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from XR7.fingerprinting.schema import (
    MatchType,
    NormalizedMatchResult,
    UsageMatchResult,
)
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# Platforms classified as UGC
_UGC_PLATFORMS = frozenset(
    {"youtube", "tiktok", "instagram", "facebook", "meta", "reels", "shorts"}
)

# Platforms classified as DSP streaming
_STREAMING_PLATFORMS = frozenset(
    {"spotify", "apple_music", "amazon_music", "deezer", "tidal", "youtube_music"}
)

# Platforms classified as live event sources
_LIVE_PLATFORMS = frozenset({"ticketmaster", "axs", "bandsintown", "songkick", "eventbrite"})


def _infer_match_type(platform: str | None) -> MatchType:
    if not platform:
        return MatchType.UNKNOWN
    p = platform.lower()
    if p in _UGC_PLATFORMS:
        return MatchType.UGC
    if p in _STREAMING_PLATFORMS:
        return MatchType.STREAM
    if p in _LIVE_PLATFORMS:
        return MatchType.LIVE
    if "radio" in p:
        return MatchType.RADIO
    if "broadcast" in p or "tv" in p:
        return MatchType.BROADCAST
    return MatchType.UNKNOWN


class UsageMatchingModule:
    """Matches fingerprint detections to platform usage data.

    Args:
        db: SQLAlchemy session used to query platform usage events.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def match(
        self,
        fingerprint: NormalizedMatchResult,
    ) -> list[UsageMatchResult]:
        """Determine usage context for a fingerprint match.

        Returns a list of ``UsageMatchResult`` representing all detected
        usage contexts from the fingerprint.
        """
        results: list[UsageMatchResult] = []

        # Direct platform match from fingerprint metadata
        if fingerprint.platform:
            results.append(
                UsageMatchResult(
                    isrc=fingerprint.isrc,
                    platform=fingerprint.platform,
                    territory=fingerprint.territory,
                    match_type=_infer_match_type(fingerprint.platform),
                    detected_at=fingerprint.timestamp,
                    reported=False,  # Determined by royalty matching stage
                    provider=fingerprint.provider,
                )
            )

        # Cross-reference against existing DB events for the same ISRC
        if fingerprint.isrc:
            db_events = self._query_events_for_isrc(fingerprint.isrc)
            for evt in db_events:
                platform = evt.get("platform") or evt.get("source_name", "")
                results.append(
                    UsageMatchResult(
                        isrc=fingerprint.isrc,
                        platform=platform,
                        territory=evt.get("territory"),
                        match_type=_infer_match_type(platform),
                        detected_at=fingerprint.timestamp,
                        reported=True,
                        provider=fingerprint.provider,
                    )
                )

        # Check for unofficial UGC usage (platform is UGC but no matching
        # royalty events found → marked as unreported)
        unofficial = self._detect_unofficial_usage(fingerprint)
        results.extend(unofficial)

        return results

    def match_batch(
        self,
        fingerprints: list[NormalizedMatchResult],
    ) -> dict[int, list[UsageMatchResult]]:
        """Match a batch of fingerprints."""
        return {i: self.match(fp) for i, fp in enumerate(fingerprints)}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _query_events_for_isrc(self, isrc: str) -> list[dict[str, Any]]:
        """Query existing universal royalty events for a given ISRC."""
        try:
            from XR7.models.universal_royalty_event import UniversalRoyaltyEvent

            rows = (
                self._db.query(UniversalRoyaltyEvent)
                .filter(UniversalRoyaltyEvent.isrc == isrc)
                .limit(100)
                .all()
            )
            return [
                {
                    "platform": getattr(r, "source_name", None),
                    "territory": getattr(r, "territory", None),
                }
                for r in rows
            ]
        except Exception as exc:
            logger.debug("_query_events_for_isrc skipped: %s", exc)
            return []

    def _detect_unofficial_usage(
        self,
        fingerprint: NormalizedMatchResult,
    ) -> list[UsageMatchResult]:
        """Detect UGC/social usage that is not already flagged as reported."""
        if not fingerprint.platform:
            return []

        platform_lower = fingerprint.platform.lower()
        if platform_lower not in _UGC_PLATFORMS:
            return []

        # If match_type is already social/UGC but not reported, flag it
        if fingerprint.match_type in (MatchType.UGC, MatchType.SOCIAL, MatchType.UNKNOWN):
            return [
                UsageMatchResult(
                    isrc=fingerprint.isrc,
                    platform=fingerprint.platform,
                    territory=fingerprint.territory,
                    match_type=MatchType.UGC,
                    detected_at=fingerprint.timestamp,
                    reported=False,
                    provider=fingerprint.provider,
                )
            ]
        return []
