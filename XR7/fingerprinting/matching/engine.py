"""MatchingEngine — master reconciliation orchestrator.

Ties together:
    - CatalogMatchingModule
    - UsageMatchingModule
    - RoyaltyMatchingModule
    - FingerprintAnomalyDetectionEngine

Produces a ``MatchingEngineReport`` suitable for the XR7 dashboard,
audit trail, and downstream anomaly workflows.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from XR7.fingerprinting.matching.anomaly import FingerprintAnomalyDetectionEngine
from XR7.fingerprinting.matching.catalog import CatalogMatchingModule
from XR7.fingerprinting.matching.royalty import RoyaltyMatchingModule
from XR7.fingerprinting.matching.usage import UsageMatchingModule
from XR7.fingerprinting.schema import (
    MatchingEngineReport,
    NormalizedMatchResult,
)
from xr7_common.logging import get_logger

logger = get_logger(__name__)


class MatchingEngine:
    """Full reconciliation engine for the XR7 fingerprinting subsystem.

    Example::

        engine = MatchingEngine(db=db_session)
        report = engine.run(artist_id="artist-uuid", fingerprints=results)
    """

    def __init__(self, db: Session) -> None:
        self._db = db
        self._catalog = CatalogMatchingModule(db)
        self._usage = UsageMatchingModule(db)
        self._royalty = RoyaltyMatchingModule(db)
        self._anomaly = FingerprintAnomalyDetectionEngine(db)

    def run(
        self,
        artist_id: str,
        fingerprints: list[NormalizedMatchResult],
    ) -> MatchingEngineReport:
        """Run all matching and anomaly detection stages.

        Args:
            artist_id: XR7 artist identifier.
            fingerprints: Normalized results from the orchestrator.

        Returns:
            A complete ``MatchingEngineReport``.
        """
        logger.info(
            "MatchingEngine: starting run artist_id=%s fingerprints=%d",
            artist_id,
            len(fingerprints),
        )

        # Stage 1 — Catalog matching
        all_catalog_matches = []
        for fp in fingerprints:
            catalog_hits = self._catalog.match(fp, return_all=True)
            all_catalog_matches.extend(catalog_hits)

        logger.info(
            "MatchingEngine: catalog_matches=%d", len(all_catalog_matches)
        )

        # Stage 2 — Usage matching
        usage_map = self._usage.match_batch(fingerprints)
        all_usage = [u for sub in usage_map.values() for u in sub]

        logger.info("MatchingEngine: usage_matches=%d", len(all_usage))

        # Stage 3 — Royalty gap matching
        royalty_gaps = self._royalty.compare_batch(fingerprints, usage_map, artist_id)

        logger.info("MatchingEngine: royalty_gaps=%d", len(royalty_gaps))

        # Stage 4 — Anomaly detection
        anomalies = self._anomaly.detect(
            artist_id=artist_id,
            fingerprints=fingerprints,
            catalog_matches=all_catalog_matches,
            usage_results=all_usage,
            existing_gaps=royalty_gaps,
        )

        logger.info("MatchingEngine: anomalies=%d", len(anomalies))

        report = MatchingEngineReport(
            artist_id=artist_id,
            fingerprint_results=fingerprints,
            catalog_matches=all_catalog_matches,
            usage_matches=all_usage,
            royalty_gaps=royalty_gaps,
            anomalies=anomalies,
            generated_at=datetime.now(timezone.utc),
        )

        self._persist_report(report)
        return report

    def run_anomaly_sweep(self, artist_id: str) -> list:
        """Run anomaly detection without requiring new fingerprint results.

        Useful for periodic batch reconciliation against existing data.
        """
        # Load recent fingerprint matches from DB as surrogate fingerprints
        fingerprints = self._load_recent_matches(artist_id)
        if not fingerprints:
            logger.info(
                "MatchingEngine: no recent matches for artist_id=%s", artist_id
            )
            return []
        report = self.run(artist_id, fingerprints)
        return report.anomalies + report.royalty_gaps

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _persist_report(self, report: MatchingEngineReport) -> None:
        """Append the report to the immutable ledger."""
        try:
            from XR7.recovery.immutable_ledger import ImmutableLedgerService

            ImmutableLedgerService(self._db).append(
                report.artist_id,
                "fingerprint_matching_report",
                {
                    "generated_at": report.generated_at.isoformat(),
                    "fingerprint_count": len(report.fingerprint_results),
                    "catalog_match_count": len(report.catalog_matches),
                    "usage_match_count": len(report.usage_matches),
                    "royalty_gap_count": len(report.royalty_gaps),
                    "anomaly_count": len(report.anomalies),
                    "schema_version": report.schema_version,
                },
            )
        except Exception as exc:
            logger.debug("_persist_report skipped: %s", exc)

    def _load_recent_matches(
        self, artist_id: str
    ) -> list[NormalizedMatchResult]:
        """Load recent FingerprintMatch rows as NormalizedMatchResult proxies."""
        try:
            from datetime import timedelta

            from XR7.models.fingerprint_match import FingerprintMatch
            from XR7.models.fingerprint_job import FingerprintJob
            from XR7.fingerprinting.schema import AnomalyType, MatchType, RoyaltyStatus

            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            jobs = (
                self._db.query(FingerprintJob)
                .filter(FingerprintJob.artist_id == artist_id)
                .filter(FingerprintJob.created_at >= cutoff)
                .all()
            )
            job_ids = [j.id for j in jobs]
            if not job_ids:
                return []

            matches = (
                self._db.query(FingerprintMatch)
                .filter(FingerprintMatch.job_id.in_(job_ids))
                .limit(500)
                .all()
            )

            results: list[NormalizedMatchResult] = []
            for m in matches:
                try:
                    mt_val = m.match_type or MatchType.UNKNOWN.value
                    mt = MatchType(mt_val) if mt_val in MatchType._value2member_map_ else MatchType.UNKNOWN
                    rs_val = m.royalty_status or RoyaltyStatus.UNKNOWN.value
                    rs = RoyaltyStatus(rs_val) if rs_val in RoyaltyStatus._value2member_map_ else RoyaltyStatus.UNKNOWN
                    at_val = m.anomaly_type or AnomalyType.NONE.value
                    at = AnomalyType(at_val) if at_val in AnomalyType._value2member_map_ else AnomalyType.NONE

                    results.append(
                        NormalizedMatchResult(
                            track_id=m.track_id,
                            isrc=m.isrc,
                            iswc=m.iswc,
                            ipi=m.ipi,
                            confidence_score=m.confidence_score or 0.0,
                            match_type=mt,
                            platform=m.platform,
                            territory=m.territory,
                            timestamp=m.matched_at or datetime.now(timezone.utc),
                            provider=m.provider or "unknown",
                            royalty_status=rs,
                            anomaly_type=at,
                            title=m.title,
                            artist_name=m.artist_name,
                            raw_provider_payload=m.raw_payload or {},
                        )
                    )
                except Exception as row_exc:
                    logger.debug("Skipping malformed FingerprintMatch row: %s", row_exc)

            return results
        except Exception as exc:
            logger.debug("_load_recent_matches skipped: %s", exc)
            return []
