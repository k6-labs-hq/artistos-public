"""Catalog Matching Module.

Reconciles fingerprinting results against XR7's catalog (Works table) using:
    1. Exact ISRC match
    2. Exact ISWC match
    3. IPI match
    4. Title + Artist fuzzy match (difflib SequenceMatcher)
    5. Acoustic fingerprint track_id cross-reference

Confidence scoring reflects the quality and precision of the match method.
Multi-match resolution returns the highest-confidence result unless
``return_all=True`` is specified.
"""

from __future__ import annotations

import difflib
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from XR7.fingerprinting.schema import CatalogMatchResult, NormalizedMatchResult
from xr7_common.logging import get_logger

if TYPE_CHECKING:
    from XR7.models.work import Work

logger = get_logger(__name__)

# Confidence weights per match method
_CONFIDENCE = {
    "isrc": 1.0,
    "iswc": 0.95,
    "ipi": 0.85,
    "title_artist_fuzzy": 0.70,
    "acoustic_track_id": 0.80,
}

# Fuzzy match threshold — matches below this are discarded
_FUZZY_THRESHOLD = 0.70


class CatalogMatchingModule:
    """Matches fingerprint results to XR7's catalog works.

    Args:
        db: SQLAlchemy session (required for DB lookups).
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def match(
        self,
        fingerprint: NormalizedMatchResult,
        *,
        return_all: bool = False,
    ) -> list[CatalogMatchResult]:
        """Attempt to match a fingerprint result to a catalog work.

        Returns a list of ``CatalogMatchResult`` sorted by confidence
        descending.  When ``return_all=False`` only the best match is
        returned.
        """
        results: list[CatalogMatchResult] = []

        # 1 — ISRC exact match (always attempted; returns None quickly when isrc absent)
        r = self._match_by_isrc(fingerprint.isrc)
        if r:
            results.append(r)

        # 2 — ISWC exact match
        if fingerprint.iswc and not _already_matched(results, "iswc"):
            r = self._match_by_iswc(fingerprint.iswc)
            if r:
                results.append(r)

        # 3 — IPI exact match
        if fingerprint.ipi and not _already_matched(results, "ipi"):
            r = self._match_by_ipi(fingerprint.ipi)
            if r:
                results.append(r)

        # 4 — Title + artist fuzzy match
        if fingerprint.title and not results:
            fuzzy_results = self._match_by_title_artist(
                fingerprint.title, fingerprint.artist_name
            )
            results.extend(fuzzy_results)

        # 5 — Acoustic track_id cross-reference
        if fingerprint.track_id and not results:
            r = self._match_by_acoustic_id(fingerprint.track_id)
            if r:
                results.append(r)

        # Sort by confidence descending
        results.sort(key=lambda r: r.confidence_score, reverse=True)

        if not results:
            logger.debug(
                "CatalogMatching: no match for isrc=%s title=%s",
                fingerprint.isrc,
                fingerprint.title,
            )
            return []

        if return_all:
            return results
        return [results[0]]

    def match_batch(
        self,
        fingerprints: list[NormalizedMatchResult],
    ) -> dict[int, list[CatalogMatchResult]]:
        """Match a batch of fingerprints.  Returns a dict keyed by index."""
        return {i: self.match(fp) for i, fp in enumerate(fingerprints)}

    # ------------------------------------------------------------------
    # Match strategies
    # ------------------------------------------------------------------

    def _match_by_isrc(self, isrc: str | None) -> CatalogMatchResult | None:
        from XR7.models.work import Work

        work = (
            self._db.query(Work)
            .filter(Work.isrc == isrc)
            .first()
        )
        if not work:
            return None
        return CatalogMatchResult(
            work_id=work.id,
            isrc=work.isrc,
            iswc=work.iswc,
            title=work.title,
            confidence_score=_CONFIDENCE["isrc"],
            match_method="isrc",
        )

    def _match_by_iswc(self, iswc: str) -> CatalogMatchResult | None:
        from XR7.models.work import Work

        work = (
            self._db.query(Work)
            .filter(Work.iswc == iswc)
            .first()
        )
        if not work:
            return None
        return CatalogMatchResult(
            work_id=work.id,
            isrc=work.isrc,
            iswc=work.iswc,
            title=work.title,
            confidence_score=_CONFIDENCE["iswc"],
            match_method="iswc",
        )

    def _match_by_ipi(self, ipi: str) -> CatalogMatchResult | None:
        """Match by IPI via the artist table (IPI is a composer identifier)."""
        from XR7.models.artist import Artist
        from XR7.models.work import Work

        artist = (
            self._db.query(Artist)
            .filter(Artist.ipi == ipi)
            .first()
        )
        if not artist:
            return None
        work = (
            self._db.query(Work)
            .filter(Work.artist_id == artist.id)
            .first()
        )
        if not work:
            return None
        return CatalogMatchResult(
            work_id=work.id,
            ipi=ipi,
            isrc=work.isrc,
            iswc=work.iswc,
            title=work.title,
            confidence_score=_CONFIDENCE["ipi"],
            match_method="ipi",
        )

    def _match_by_title_artist(
        self,
        title: str,
        artist_name: str | None,
    ) -> list[CatalogMatchResult]:
        from XR7.models.work import Work

        # Load a bounded candidate set (avoids full table scan)
        candidates = (
            self._db.query(Work)
            .filter(Work.title.ilike(f"%{title[:20]}%"))
            .limit(200)
            .all()
        )

        scored: list[tuple[float, Work]] = []
        for work in candidates:
            title_ratio = difflib.SequenceMatcher(
                None, title.lower(), work.title.lower()
            ).ratio()

            artist_ratio = 0.0
            if artist_name and hasattr(work, "artist") and work.artist:
                artist_ratio = difflib.SequenceMatcher(
                    None,
                    artist_name.lower(),
                    getattr(work.artist, "name", "").lower(),
                ).ratio()

            combined = title_ratio * 0.6 + artist_ratio * 0.4
            if combined >= _FUZZY_THRESHOLD:
                scored.append((combined, work))

        scored.sort(key=lambda t: t[0], reverse=True)
        return [
            CatalogMatchResult(
                work_id=work.id,
                isrc=work.isrc,
                iswc=work.iswc,
                title=work.title,
                confidence_score=round(
                    score * _CONFIDENCE["title_artist_fuzzy"], 4
                ),
                match_method="title_artist_fuzzy",
            )
            for score, work in scored[:5]
        ]

    def _match_by_acoustic_id(self, track_id: str) -> CatalogMatchResult | None:
        """Cross-reference a provider acoustic track_id stored in work metadata."""
        from XR7.models.work import Work

        # Works may store provider IDs in a JSON metadata column in future.
        # For now, attempt an ISRC-equivalent lookup via track_id as ISRC.
        work = (
            self._db.query(Work)
            .filter(Work.isrc == track_id)
            .first()
        )
        if not work:
            return None
        return CatalogMatchResult(
            work_id=work.id,
            isrc=work.isrc,
            iswc=work.iswc,
            title=work.title,
            confidence_score=_CONFIDENCE["acoustic_track_id"],
            match_method="acoustic_track_id",
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _already_matched(results: list[CatalogMatchResult], method: str) -> bool:
    return any(r.match_method == method for r in results)
