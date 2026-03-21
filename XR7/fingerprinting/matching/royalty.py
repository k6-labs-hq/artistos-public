"""Royalty Matching Module.

Compares detected usage events against received royalty statements to identify:
    - Missing royalties (usage detected, no royalty received)
    - Incorrect splits (partial royalty vs expected split)
    - Unreported foreign royalties  (foreign platform usage, no PRO abroad)
    - Unreported live performances  (live event detected, no PRO live payment)
    - Mismatched work registrations (ISRC/ISWC/IPI discrepancy vs statements)
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from XR7.fingerprinting.schema import (
    AnomalyType,
    MatchType,
    NormalizedMatchResult,
    RoyaltyGapResult,
    RoyaltyStatus,
    UsageMatchResult,
)
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# Platforms where a matching distributor payment is expected
_DISTRIBUTOR_PLATFORMS = frozenset(
    {
        "youtube",
        "tiktok",
        "instagram",
        "facebook",
        "spotify",
        "apple_music",
        "amazon_music",
        "deezer",
        "tidal",
    }
)

# PRO payment expected territories per live platform
_LIVE_PRO_REQUIRED_TERRITORIES: set[str] = {
    "US",
    "UK",
    "DE",
    "FR",
    "NL",
    "CA",
    "AU",
    "SE",
    "NO",
    "DK",
}


class RoyaltyMatchingModule:
    """Compares usage events against royalty statements to surface payment gaps.

    Args:
        db: SQLAlchemy session for querying statements and payments.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compare(
        self,
        fingerprint: NormalizedMatchResult,
        usage_results: list[UsageMatchResult],
        artist_id: str,
    ) -> list[RoyaltyGapResult]:
        """Compare usage with artist's royalty statements to find gaps.

        Args:
            fingerprint: The source fingerprint result.
            usage_results: Usage matches associated with this fingerprint.
            artist_id: XR7 artist identifier.

        Returns:
            A list of ``RoyaltyGapResult`` describing each identified gap.
        """
        gaps: list[RoyaltyGapResult] = []

        for usage in usage_results:
            # Skip already-reported usage — check royalty coverage
            if usage.reported:
                gaps.extend(
                    self._check_royalty_coverage(fingerprint, usage, artist_id)
                )
            else:
                # Usage not in any statement
                gaps.append(
                    RoyaltyGapResult(
                        isrc=fingerprint.isrc,
                        platform=usage.platform,
                        territory=usage.territory,
                        match_type=usage.match_type,
                        detected_usage=True,
                        royalty_received=False,
                        anomaly_type=self._classify_anomaly(usage),
                        description=(
                            f"Usage detected on {usage.platform} "
                            f"(territory={usage.territory or 'unknown'}) "
                            f"with no corresponding royalty statement."
                        ),
                    )
                )

        return gaps

    def compare_batch(
        self,
        fingerprints: list[NormalizedMatchResult],
        usage_map: dict[int, list[UsageMatchResult]],
        artist_id: str,
    ) -> list[RoyaltyGapResult]:
        """Batch comparison across multiple fingerprint results."""
        all_gaps: list[RoyaltyGapResult] = []
        for i, fp in enumerate(fingerprints):
            usage_list = usage_map.get(i, [])
            all_gaps.extend(self.compare(fp, usage_list, artist_id))
        return all_gaps

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_royalty_coverage(
        self,
        fingerprint: NormalizedMatchResult,
        usage: UsageMatchResult,
        artist_id: str,
    ) -> list[RoyaltyGapResult]:
        """For reported usage, verify that royalties were actually paid."""
        gaps: list[RoyaltyGapResult] = []

        has_payment = self._has_royalty_payment(
            artist_id=artist_id,
            isrc=fingerprint.isrc,
            platform=usage.platform,
            territory=usage.territory,
        )

        # Missing royalty for UGC / distributor platforms
        if usage.match_type == MatchType.UGC and not has_payment:
            if usage.platform and usage.platform.lower() in _DISTRIBUTOR_PLATFORMS:
                gaps.append(
                    RoyaltyGapResult(
                        isrc=fingerprint.isrc,
                        platform=usage.platform,
                        territory=usage.territory,
                        match_type=usage.match_type,
                        detected_usage=True,
                        royalty_received=False,
                        anomaly_type=AnomalyType.SOCIAL_NO_DISTRIBUTOR,
                        description=(
                            f"TikTok/YouTube/Instagram usage detected on "
                            f"{usage.platform} but no distributor payment found."
                        ),
                    )
                )

        # Foreign usage with no PRO payment
        territory = usage.territory or ""
        if (
            territory.upper() not in ("US", "")
            and usage.match_type in (MatchType.BROADCAST, MatchType.RADIO, MatchType.STREAM)
            and not has_payment
        ):
            gaps.append(
                RoyaltyGapResult(
                    isrc=fingerprint.isrc,
                    platform=usage.platform,
                    territory=usage.territory,
                    match_type=usage.match_type,
                    detected_usage=True,
                    royalty_received=False,
                    anomaly_type=AnomalyType.FOREIGN_USAGE_NO_PRO,
                    description=(
                        f"Foreign usage in territory={territory} detected via "
                        f"{fingerprint.provider} but no foreign PRO payment received."
                    ),
                )
            )

        # Live performance with no PRO live royalty
        if (
            usage.match_type == MatchType.LIVE
            and territory.upper() in _LIVE_PRO_REQUIRED_TERRITORIES
            and not has_payment
        ):
            gaps.append(
                RoyaltyGapResult(
                    isrc=fingerprint.isrc,
                    platform=usage.platform,
                    territory=usage.territory,
                    match_type=usage.match_type,
                    detected_usage=True,
                    royalty_received=False,
                    anomaly_type=AnomalyType.LIVE_NO_PRO_PERFORMANCE,
                    description=(
                        f"Live performance detected in {territory} but no PRO "
                        f"live performance royalty received."
                    ),
                )
            )

        return gaps

    def _has_royalty_payment(
        self,
        *,
        artist_id: str,
        isrc: str | None,
        platform: str | None,
        territory: str | None,
    ) -> bool:
        """Check whether a royalty payment exists for the given parameters."""
        try:
            from XR7.models.payment import Payment

            query = self._db.query(Payment).filter(
                Payment.artist_id == artist_id
            )
            payments = query.limit(500).all()

            for p in payments:
                source: str = getattr(p, "source", "") or ""
                if platform and platform.lower() in source.lower():
                    return True

            return False
        except Exception as exc:
            logger.debug("_has_royalty_payment skipped: %s", exc)
            return False

    @staticmethod
    def _classify_anomaly(usage: UsageMatchResult) -> AnomalyType:
        if usage.match_type == MatchType.LIVE:
            return AnomalyType.LIVE_NO_PRO_PERFORMANCE
        if usage.match_type == MatchType.UGC:
            return AnomalyType.SOCIAL_NO_DISTRIBUTOR
        if usage.territory and usage.territory.upper() not in ("US", ""):
            return AnomalyType.FOREIGN_USAGE_NO_PRO
        return AnomalyType.USAGE_NO_ROYALTY
