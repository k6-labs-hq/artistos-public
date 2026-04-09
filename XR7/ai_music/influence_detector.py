from __future__ import annotations

import asyncio
import hashlib
import importlib
import os
import time
import uuid
from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any

from sqlalchemy.orm import Session

from XR7.celery_app import celery_app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.base import SessionLocal
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.ml_feedback import CalibrationSnapshot
from XR7.models.universal_royalty_event import UniversalRoyaltyEvent
from xr7_common.logging import get_logger

try:
    _lc_openai = importlib.import_module("langchain_openai")
    ChatOpenAI = getattr(_lc_openai, "ChatOpenAI")
except Exception:  # pragma: no cover
    ChatOpenAI = None

try:
    _librosa = importlib.import_module("librosa")
except Exception:  # pragma: no cover
    _librosa = None


logger = get_logger(__name__)


class _ApiRateLimiter:
    def __init__(self, max_requests: int = 20, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._lock = Lock()
        self._hits: deque[float] = deque()

    async def check(self) -> None:
        now = time.time()
        cutoff = now - self.window_seconds
        with self._lock:
            while self._hits and self._hits[0] < cutoff:
                self._hits.popleft()
            if len(self._hits) >= self.max_requests:
                raise RuntimeError("Public API rate limit exceeded")
            self._hits.append(now)


class InfluenceDetector:
    """Detect likely AI-generated influence infringements from public release streams."""

    def __init__(self, db: Session):
        self.db = db
        self._rate = _ApiRateLimiter(max_requests=30, window_seconds=60)
        self._simulated = os.environ.get("XR7_AI_MUSIC_SIMULATED", "1").strip().lower() in {
            "1",
            "true",
            "yes",
        }

    @staticmethod
    def _fingerprint(work_title: str, artist_id: str) -> str:
        base = f"{artist_id}:{work_title}".encode("utf-8")
        return hashlib.sha256(base).hexdigest()

    async def _fetch_public_releases(self, artist_id: str) -> list[dict[str, Any]]:
        await self._rate.check()
        if self._simulated:
            return [
                {
                    "external_id": f"ai-{artist_id}-1",
                    "title": "Neon Skyline (AI Remix)",
                    "platform": "synthetic-feed",
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "estimated_streams": 120000,
                },
                {
                    "external_id": f"ai-{artist_id}-2",
                    "title": "Midnight Echo Voice Model",
                    "platform": "synthetic-feed",
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "estimated_streams": 64000,
                },
            ]
        return []

    async def _style_similarity(self, title: str, artist_id: str) -> float:
        # Placeholder perceptual hash path; if librosa is available this could be expanded.
        digest = self._fingerprint(title, artist_id)
        return (int(digest[:8], 16) % 1000) / 1000.0

    async def scan_new_ai_releases(self, artist_id: str) -> list[dict[str, Any]]:
        """Scan public AI release feeds and return potential influence claims."""
        releases = await self._fetch_public_releases(artist_id)
        snapshots = (
            self.db.query(CalibrationSnapshot)
            .filter(CalibrationSnapshot.artist_id == artist_id)
            .all()
        )
        calibration = max((float(s.posterior_mean or 0.5) for s in snapshots), default=0.5)

        potential_claims: list[dict[str, Any]] = []
        for rel in releases:
            sim = await self._style_similarity(str(rel.get("title") or ""), artist_id)
            confidence = round((sim * 0.6) + (calibration * 0.4), 4)
            if confidence < 0.62:
                continue
            potential_claims.append(
                {
                    "artist_id": artist_id,
                    "release": rel,
                    "similarity_score": sim,
                    "confidence": confidence,
                    "fingerprint": self._fingerprint(str(rel.get("title") or ""), artist_id),
                }
            )
        return potential_claims

    async def generate_influence_evidence(self, claim: dict) -> dict[str, Any]:
        """Generate evidence payload with catalog matching and micro-royalty estimate."""
        release = claim.get("release") or {}
        streams = int(release.get("estimated_streams") or 0)
        micro_rate = 0.0037
        est = round(streams * micro_rate * float(claim.get("confidence") or 0.0), 2)

        events = (
            self.db.query(UniversalRoyaltyEvent)
            .filter(UniversalRoyaltyEvent.artist_id == claim.get("artist_id"))
            .order_by(UniversalRoyaltyEvent.ingested_at.desc())
            .limit(5)
            .all()
        )
        lineage = [
            {
                "event_id": e.id,
                "work_id": e.work_id,
                "source_name": e.source_name,
                "amount": e.amount,
            }
            for e in events
        ]

        return {
            "claim_type": "AI_INFLUENCE",
            "release": release,
            "confidence": claim.get("confidence"),
            "fingerprint": claim.get("fingerprint"),
            "micro_royalty_estimate": est,
            "catalog_lineage": lineage,
            "integrity": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "packet_hash": hashlib.sha256(str(claim).encode("utf-8")).hexdigest(),
            },
        }

    async def auto_create_claim(self, artist_id: str, influence_match: dict) -> str:
        """Create anomaly and claim for a high-confidence influence match."""
        evidence = await self.generate_influence_evidence(influence_match)
        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist_id,
            category=AnomalyCategory.ROYALTY,
            subtype="ai_influence",
            severity=AnomalySeverity.HIGH,
            status=AnomalyStatus.OPEN,
            confidence_score=float(influence_match.get("confidence") or 0.0),
            estimated_recoverable=float(evidence.get("micro_royalty_estimate") or 0.0),
            description=f"Potential AI influence detected: {(influence_match.get('release') or {}).get('title')}",
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(anomaly)
        self.db.commit()

        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist_id,
            anomaly_id=anomaly.id,
            claim_type="AI_INFLUENCE",
            status=ClaimStatus.IDENTIFIED,
            evidence=evidence,
            currency="USD",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(claim)
        self.db.commit()
        return claim.id


@celery_app.task(
    name="xr7.pipeline.scan_ai_influence_daily",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def scan_ai_influence_daily(self) -> dict:  # noqa: ANN001
    """Daily background scan for AI influence opportunities."""
    db = SessionLocal()
    try:
        artist_ids = {
            r.artist_id for r in db.query(UniversalRoyaltyEvent.artist_id).all() if r.artist_id
        }
        created = 0
        for artist_id in artist_ids:
            detector = InfluenceDetector(db)
            matches = asyncio.run(detector.scan_new_ai_releases(artist_id))
            for match in matches:
                asyncio.run(detector.auto_create_claim(artist_id, match))
                created += 1
        return {"artists_scanned": len(artist_ids), "claims_created": created}
    finally:
        db.close()
