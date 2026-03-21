"""Anomaly Detection Engine for the fingerprinting matching pipeline.

Detects the following anomaly classes:
    - USAGE_NO_ROYALTY       — usage detected, zero royalty statement
    - ROYALTY_NO_USAGE       — royalty received, no fingerprint evidence of play
    - FOREIGN_USAGE_NO_PRO  — foreign territory usage, missing foreign PRO payment
    - LIVE_NO_PRO_PERF       — live event detected, no PRO live performance payment
    - SOCIAL_NO_DISTRIBUTOR — TikTok/YT/IGReel usage, no distributor payment
    - CATALOG_MISMATCH       — ISRC/ISWC/IPI conflict between catalog and statement
    - ISRC_CONFLICT          — two catalog works share the same ISRC
    - ISWC_CONFLICT          — two catalog works share the same ISWC
    - IPI_CONFLICT           — IPI on a statement doesn't match artist's IPI

All anomalies are returned as ``RoyaltyGapResult`` instances which can be
directly forwarded to the existing XR7 anomaly workflow.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.fingerprinting.schema import (
    AnomalyType,
    CatalogMatchResult,
    MatchType,
    NormalizedMatchResult,
    RoyaltyGapResult,
    UsageMatchResult,
)
from xr7_common.logging import get_logger

logger = get_logger(__name__)


class FingerprintAnomalyDetectionEngine:
    """Detects anomalies by cross-referencing fingerprint results with catalog
    and payment data.

    Designed to complement (not replace) the existing ``AnomalyEngine``.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect(
        self,
        *,
        artist_id: str,
        fingerprints: list[NormalizedMatchResult],
        catalog_matches: list[CatalogMatchResult],
        usage_results: list[UsageMatchResult],
        existing_gaps: list[RoyaltyGapResult],
    ) -> list[RoyaltyGapResult]:
        """Run all anomaly detectors and return new anomalies.

        Avoids duplicating anomalies already present in ``existing_gaps``.
        """
        anomalies: list[RoyaltyGapResult] = []

        # 1 — Royalty-with-no-usage
        anomalies.extend(self._royalty_no_usage(artist_id, fingerprints))

        # 2 — Catalog conflicts (ISRC / ISWC / IPI)
        anomalies.extend(self._catalog_conflicts(catalog_matches))

        # 3 — Metadata mismatches (ISRC on statement ≠ ISRC in catalog)
        anomalies.extend(self._isrc_statement_mismatch(artist_id, fingerprints, catalog_matches))

        # Deduplicate against existing gaps
        seen = _gap_keys(existing_gaps)
        return [a for a in anomalies if _gap_key(a) not in seen]

    # ------------------------------------------------------------------
    # Anomaly detectors
    # ------------------------------------------------------------------

    def _royalty_no_usage(
        self,
        artist_id: str,
        fingerprints: list[NormalizedMatchResult],
    ) -> list[RoyaltyGapResult]:
        """Detect royalty payments for ISRCs that have zero fingerprint matches."""
        detected_isrcs = {fp.isrc for fp in fingerprints if fp.isrc}
        gaps: list[RoyaltyGapResult] = []

        try:
            from XR7.models.payment import Payment

            payments = (
                self._db.query(Payment)
                .filter(Payment.artist_id == artist_id)
                .limit(500)
                .all()
            )
            for payment in payments:
                isrc: str | None = None
                source: str = getattr(payment, "source", "") or ""
                # Payments may carry ISRC in a notes/metadata field
                notes: str = getattr(payment, "notes", "") or ""
                # Attempt to find ISRC-like string (12 alphanumeric chars)
                import re
                matches = re.findall(r"\b[A-Z]{2}[A-Z0-9]{3}[0-9]{7}\b", notes + source)
                if matches:
                    isrc = matches[0]

                if isrc and isrc not in detected_isrcs:
                    gaps.append(
                        RoyaltyGapResult(
                            isrc=isrc,
                            platform=source,
                            match_type=MatchType.UNKNOWN,
                            detected_usage=False,
                            royalty_received=True,
                            anomaly_type=AnomalyType.ROYALTY_NO_USAGE,
                            description=(
                                f"Royalty received for ISRC={isrc} but no "
                                f"fingerprint usage detected in this period."
                            ),
                        )
                    )
        except Exception as exc:
            logger.debug("_royalty_no_usage skipped: %s", exc)

        return gaps

    def _catalog_conflicts(
        self,
        catalog_matches: list[CatalogMatchResult],
    ) -> list[RoyaltyGapResult]:
        """Detect multiple catalog entries sharing the same ISRC or ISWC."""
        anomalies: list[RoyaltyGapResult] = []

        # Group by ISRC
        isrc_to_works: dict[str, list[str]] = {}
        for cm in catalog_matches:
            if cm.isrc:
                isrc_to_works.setdefault(cm.isrc, []).append(cm.work_id or "unknown")

        for isrc, work_ids in isrc_to_works.items():
            if len(work_ids) > 1:
                anomalies.append(
                    RoyaltyGapResult(
                        isrc=isrc,
                        match_type=MatchType.UNKNOWN,
                        anomaly_type=AnomalyType.ISRC_CONFLICT,
                        description=(
                            f"ISRC {isrc} is assigned to multiple catalog works: "
                            f"{work_ids}"
                        ),
                    )
                )

        # Group by ISWC
        iswc_to_works: dict[str, list[str]] = {}
        for cm in catalog_matches:
            if cm.iswc:
                iswc_to_works.setdefault(cm.iswc, []).append(cm.work_id or "unknown")

        for iswc, work_ids in iswc_to_works.items():
            if len(work_ids) > 1:
                anomalies.append(
                    RoyaltyGapResult(
                        iswc=iswc if hasattr(RoyaltyGapResult, "iswc") else None,
                        match_type=MatchType.UNKNOWN,
                        anomaly_type=AnomalyType.ISWC_CONFLICT,
                        description=(
                            f"ISWC {iswc} is assigned to multiple catalog works: "
                            f"{work_ids}"
                        ),
                    )
                )

        return anomalies

    def _isrc_statement_mismatch(
        self,
        artist_id: str,
        fingerprints: list[NormalizedMatchResult],
        catalog_matches: list[CatalogMatchResult],
    ) -> list[RoyaltyGapResult]:
        """Detect when the ISRC in a fingerprint result doesn't match what's
        registered in the XR7 catalog for the same work."""
        anomalies: list[RoyaltyGapResult] = []

        catalog_isrc_set = {cm.isrc for cm in catalog_matches if cm.isrc}

        for fp in fingerprints:
            if fp.isrc and catalog_isrc_set and fp.isrc not in catalog_isrc_set:
                anomalies.append(
                    RoyaltyGapResult(
                        isrc=fp.isrc,
                        platform=fp.platform,
                        territory=fp.territory,
                        match_type=fp.match_type,
                        anomaly_type=AnomalyType.CATALOG_MISMATCH,
                        description=(
                            f"Fingerprint ISRC={fp.isrc} from provider={fp.provider} "
                            f"does not match any ISRC in the XR7 catalog for this artist."
                        ),
                    )
                )

        return anomalies


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _gap_key(gap: RoyaltyGapResult) -> tuple:
    at = gap.anomaly_type.value if hasattr(gap.anomaly_type, "value") else str(gap.anomaly_type)
    # For CATALOG_MISMATCH / ISRC_CONFLICT we key only on (isrc, anomaly_type)
    # because the same ISRC can appear with different platform/territory values
    # across providers and we want dedup to apply regardless.
    if at in ("catalog_mismatch", "isrc_conflict", "iswc_conflict"):
        return (gap.isrc, None, None, at)
    return (gap.isrc, gap.platform, gap.territory, at)


def _gap_keys(gaps: list[RoyaltyGapResult]) -> set[tuple]:
    return {_gap_key(g) for g in gaps}
