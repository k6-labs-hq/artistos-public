"""
Black-Box / Unclaimed Royalties Scanner — Celery task.

Task: xr7.tasks.blackbox.scan_artist_blackbox

Scheduled weekly via celery beat.  Can also be triggered on-demand via
the POST /artists/{artist_id}/blackbox/scan endpoint.

Workflow:
  1. Fetch mock MLC black-box list + foreign society redistribution queues.
  2. Match entries against artist name aliases, IPI/CAE, PRO writer ID.
  3. Create ``BlackboxMatch`` records for new matches.
  4. Create ``Anomaly`` records with subtype="black_box_match".
  5. Log in the immutable ledger.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from XR7.celery_app import celery_app
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalySeverity, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.base import SessionLocal
from XR7.models.blackbox_match import (
    BlackboxMatch,
    BlackboxMatchStatus,
    BlackboxMatchType,
    BlackboxSourceList,
)
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from xr7_common.logging import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Mock society data (replace with live API calls when keys are available)
# ---------------------------------------------------------------------------

_MLC_BLACKBOX_POOL: list[dict[str, Any]] = [
    {
        "society": "MLC",
        "source_list": BlackboxSourceList.MLC_BLACKBOX.value,
        "artist_name_hint": None,  # will be matched per-artist
        "ipi_hint": None,
        "writer_alias_keywords": ["writer", "composer", "songwriter"],
        "territory": "US",
        "amount_range_low": 250.0,
        "amount_range_high": 2800.0,
        "redistribution_window_days": 270,
        "match_type": BlackboxMatchType.NAME_ALIAS.value,
    },
    {
        "society": "ASCAP",
        "source_list": BlackboxSourceList.PRO_UNCLAIMED_POOL.value,
        "artist_name_hint": None,
        "ipi_hint": None,
        "writer_alias_keywords": ["music", "publishing", "lyricist"],
        "territory": "US",
        "amount_range_low": 180.0,
        "amount_range_high": 1500.0,
        "redistribution_window_days": 365,
        "match_type": BlackboxMatchType.IPI_CAE.value,
    },
    {
        "society": "SOCAN",
        "source_list": BlackboxSourceList.FOREIGN_REDISTRIBUTION.value,
        "artist_name_hint": None,
        "ipi_hint": None,
        "writer_alias_keywords": [],
        "territory": "CA",
        "amount_range_low": 90.0,
        "amount_range_high": 800.0,
        "redistribution_window_days": 180,
        "match_type": BlackboxMatchType.PRO_WRITER_ID.value,
    },
    {
        "society": "PRS",
        "source_list": BlackboxSourceList.FOREIGN_REDISTRIBUTION.value,
        "artist_name_hint": None,
        "ipi_hint": None,
        "writer_alias_keywords": [],
        "territory": "GB",
        "amount_range_low": 130.0,
        "amount_range_high": 2200.0,
        "redistribution_window_days": 365,
        "match_type": BlackboxMatchType.NAME_ALIAS.value,
    },
    {
        "society": "SESAC",
        "source_list": BlackboxSourceList.PRO_UNCLAIMED_POOL.value,
        "artist_name_hint": None,
        "ipi_hint": None,
        "writer_alias_keywords": ["writer", "artist"],
        "territory": "US",
        "amount_range_low": 200.0,
        "amount_range_high": 3500.0,
        "redistribution_window_days": 270,
        "match_type": BlackboxMatchType.NAME_ALIAS.value,
    },
    {
        "society": "BMI",
        "source_list": BlackboxSourceList.PRO_UNCLAIMED_POOL.value,
        "artist_name_hint": None,
        "ipi_hint": None,
        "writer_alias_keywords": ["bmi", "writer"],
        "territory": "US",
        "amount_range_low": 310.0,
        "amount_range_high": 4200.0,
        "redistribution_window_days": 365,
        "match_type": BlackboxMatchType.IPI_CAE.value,
    },
    {
        "society": "SABAM",
        "source_list": BlackboxSourceList.FOREIGN_REDISTRIBUTION.value,
        "artist_name_hint": None,
        "ipi_hint": None,
        "writer_alias_keywords": [],
        "territory": "BE",
        "amount_range_low": 60.0,
        "amount_range_high": 600.0,
        "redistribution_window_days": 120,
        "match_type": BlackboxMatchType.TITLE_FUZZY.value,
    },
    {
        "society": "APRA",
        "source_list": BlackboxSourceList.FOREIGN_REDISTRIBUTION.value,
        "artist_name_hint": None,
        "ipi_hint": None,
        "writer_alias_keywords": [],
        "territory": "AU",
        "amount_range_low": 80.0,
        "amount_range_high": 1100.0,
        "redistribution_window_days": 180,
        "match_type": BlackboxMatchType.NAME_ALIAS.value,
    },
]


# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------

def _artist_identifiers(artist: Artist) -> tuple[set[str], str | None]:
    """Return (lowercased name variants, ipi_number)."""
    names: set[str] = set()
    if artist.name:
        names.add(artist.name.lower().strip())
    if artist.first_name and artist.last_name:
        names.add(f"{artist.first_name} {artist.last_name}".lower().strip())
    stage_names = artist.stage_names or []
    for sn in stage_names:
        if sn:
            names.add(str(sn).lower().strip())
    return names, artist.ipi_number


def _match_entry(
    entry: dict[str, Any],
    artist: Artist,
    artist_names: set[str],
    ipi_number: str | None,
) -> bool:
    """Determine whether a society pool entry matches this artist."""
    match_type = str(entry.get("match_type") or BlackboxMatchType.NAME_ALIAS.value)

    if match_type == BlackboxMatchType.IPI_CAE.value:
        return bool(ipi_number) and bool(entry.get("ipi_hint")) and (
            str(ipi_number).strip() == str(entry.get("ipi_hint") or "").strip()
        )

    if match_type == BlackboxMatchType.PRO_WRITER_ID.value:
        # In production, compare PRO writer IDs; mock: match if artist has IPI
        return bool(ipi_number)

    if match_type == BlackboxMatchType.TITLE_FUZZY.value:
        # In production, fuzzy-match work titles; mock: always match for artists with >0 activity
        return True

    # Default: NAME_ALIAS — check keyword overlap for the mock
    keywords: list[str] = entry.get("writer_alias_keywords") or []
    if not keywords:
        # No keywords in mock entry → match by name heuristic
        return len(artist_names) > 0

    artist_combined = " ".join(artist_names)
    return any(kw in artist_combined for kw in keywords)


def _already_matched(
    db,
    artist_id: str,
    society: str,
    source_list: str,
    match_type: str,
) -> bool:
    """Return True if an active (non-expired/dismissed) match already exists."""
    return bool(
        db.query(BlackboxMatch)
        .filter(
            BlackboxMatch.artist_id == artist_id,
            BlackboxMatch.society == society,
            BlackboxMatch.source_list == source_list,
            BlackboxMatch.match_type == match_type,
            BlackboxMatch.status.notin_([
                BlackboxMatchStatus.EXPIRED.value,
                BlackboxMatchStatus.DISMISSED.value,
            ]),
        )
        .first()
    )


# ---------------------------------------------------------------------------
# Core scan function (used both by Celery task and on-demand endpoint)
# ---------------------------------------------------------------------------

def run_blackbox_scan(artist_id: str, db) -> dict[str, Any]:
    """
    Execute the full black-box scan for an artist.

    Returns a summary dict with ``new_matches``, ``total_value_low``,
    ``total_value_high``.
    """
    artist: Artist | None = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        logger.warning("scan_artist_blackbox: artist %s not found", artist_id)
        return {"artist_id": artist_id, "new_matches": 0, "status": "artist_not_found"}

    artist_names, ipi_number = _artist_identifiers(artist)
    now = datetime.now(timezone.utc)

    new_match_count = 0
    total_low = 0.0
    total_high = 0.0
    new_anomaly_ids: list[str] = []

    for entry in _MLC_BLACKBOX_POOL:
        society = str(entry["society"])
        source_list = str(entry["source_list"])
        match_type = str(entry["match_type"])

        if not _match_entry(entry, artist, artist_names, ipi_number):
            continue

        if _already_matched(db, artist_id, society, source_list, match_type):
            continue

        window_days = int(entry.get("redistribution_window_days") or 365)
        window_end = now + timedelta(days=window_days)
        urgency_days = window_days

        amount_low = float(entry.get("amount_range_low") or 0.0)
        amount_high = float(entry.get("amount_range_high") or 0.0)

        # Create anomaly
        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist_id,
            category=AnomalyCategory.ROYALTY.value,
            subtype="black_box_match",
            severity=AnomalySeverity.HIGH.value if urgency_days < 180 else AnomalySeverity.MEDIUM.value,
            estimated_recoverable=(amount_low + amount_high) / 2.0,
            confidence_score=0.72,
            description=(
                f"Black-box royalty pool match at {society} "
                f"({entry.get('territory', 'N/A')}). "
                f"Estimated value: ${amount_low:,.0f}–${amount_high:,.0f}. "
                f"Redistribution window closes in {urgency_days} days."
            ),
            status=AnomalyStatus.OPEN.value,
            territory=str(entry.get("territory") or ""),
            urgent_flag=urgency_days < 90,
        )
        db.add(anomaly)
        db.flush()

        # Create match record linked to the anomaly
        match_record = BlackboxMatch(
            id=str(uuid.uuid4()),
            artist_id=artist_id,
            society=society,
            match_type=match_type,
            matched_identifier=ipi_number if match_type == BlackboxMatchType.IPI_CAE.value else None,
            source_list=source_list,
            amount_range_low=amount_low,
            amount_range_high=amount_high,
            territory=str(entry.get("territory") or ""),
            redistribution_window_end_date=window_end,
            urgency_days_remaining=urgency_days,
            status=BlackboxMatchStatus.NEW.value,
            anomaly_id=anomaly.id,
            raw_society_data_json=__import__("json").dumps(entry),
        )
        db.add(match_record)

        new_match_count += 1
        total_low += amount_low
        total_high += amount_high
        new_anomaly_ids.append(anomaly.id)

    if new_match_count > 0:
        try:
            ImmutableLedgerService(db).append(
                artist_id,
                "blackbox_scan_completed",
                {
                    "new_matches": new_match_count,
                    "total_value_low": round(total_low, 2),
                    "total_value_high": round(total_high, 2),
                    "anomaly_ids": new_anomaly_ids,
                    "societies_matched": list({e["society"] for e in _MLC_BLACKBOX_POOL}),
                },
            )
        except Exception:
            logger.exception("Failed to write blackbox_scan ledger entry for artist %s", artist_id)

    db.commit()
    logger.info(
        "Blackbox scan for artist %s: %d new matches ($%.0f–$%.0f)",
        artist_id, new_match_count, total_low, total_high,
    )
    return {
        "artist_id": artist_id,
        "new_matches": new_match_count,
        "total_value_low": round(total_low, 2),
        "total_value_high": round(total_high, 2),
        "anomaly_ids": new_anomaly_ids,
        "status": "completed",
    }


# ---------------------------------------------------------------------------
# Celery task
# ---------------------------------------------------------------------------

@celery_app.task(
    name="xr7.tasks.blackbox.scan_artist_blackbox",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 2},
)
def scan_artist_blackbox(self, artist_id: str) -> dict[str, Any]:  # noqa: ANN001
    """Scan one artist's black-box / unclaimed royalty exposure."""
    db = SessionLocal()
    try:
        return run_blackbox_scan(artist_id, db)
    finally:
        db.close()


@celery_app.task(
    name="xr7.tasks.blackbox.scan_all_artists_blackbox",
    bind=True,
)
def scan_all_artists_blackbox(self) -> dict[str, Any]:  # noqa: ANN001
    """Weekly sweep: queue a blackbox scan for every active artist."""
    db = SessionLocal()
    try:
        from XR7.models.artist import ArtistLifecycleStatus
        artists = (
            db.query(Artist)
            .filter(Artist.status == ArtistLifecycleStatus.ACTIVE.value)
            .all()
        )
        queued = 0
        for artist in artists:
            scan_artist_blackbox.delay(artist.id)
            queued += 1
        logger.info("scan_all_artists_blackbox: queued %d scans", queued)
        return {"queued": queued, "status": "dispatched"}
    finally:
        db.close()
