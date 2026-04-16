from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.core.scoring.metadata_match import (
    confidence_score,
    metadata_triangulation_score,
)
from XR7.core.scoring.metadata_match import (
    text_similarity as _similarity,
)
from XR7.ingestion.connectors.xr7_platform_clients import (
    XR7PlatformAPIClient,
    XR7RateLimitScheduler,
)
from XR7.ingestion.file_ingestion_pipeline import FileIngestionPipeline
from XR7.models.sync_job import SyncJob
from XR7.models.xr7_royalty import (
    XR7ConnectorCredential,
    XR7ConnectorStatus,
    XR7MatchMethod,
    XR7PipelineResult,
    XR7RoyaltyGapReport,
    XR7RoyaltyGapRow,
    XR7RoyaltyStatement,
    XR7RoyaltyStatementLine,
    XR7SourceCategory,
    XR7Track,
    XR7UnmatchedWork,
    XR7UsageEvent,
    XR7Work,
)
from XR7.services.xr7_crypto_vault import open_sealed, seal


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class CandidateMatch:
    work_id: str
    score: float


def fuzzy_match_works(raw_title: str, works: list[XR7Work], limit: int = 5) -> list[CandidateMatch]:
    scored: list[CandidateMatch] = []
    for work in works:
        s = _similarity(raw_title, work.title)
        scored.append(CandidateMatch(work_id=work.id, score=s))
    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[:limit]


def upsert_connector_credential(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    provider: str,
    external_account_id: str,
    access_token: str,
    refresh_token: str | None,
    expires_at: datetime | None,
    scopes: list[str],
) -> XR7ConnectorCredential:
    row = (
        db.query(XR7ConnectorCredential)
        .filter(
            XR7ConnectorCredential.tenant_id == tenant_id,
            XR7ConnectorCredential.artist_id == artist_id,
            XR7ConnectorCredential.provider == provider,
            XR7ConnectorCredential.external_account_id == external_account_id,
        )
        .first()
    )
    if not row:
        row = XR7ConnectorCredential(
            tenant_id=tenant_id,
            artist_id=artist_id,
            provider=provider,
            external_account_id=external_account_id,
            encrypted_access_token=seal(access_token),
            encrypted_refresh_token=seal(refresh_token) if refresh_token else None,
            token_expires_at=expires_at,
            granted_scopes_json=json.dumps(scopes, sort_keys=True),
            status=XR7ConnectorStatus.ACTIVE,
        )
        db.add(row)
    else:
        row.encrypted_access_token = seal(access_token)
        row.encrypted_refresh_token = seal(refresh_token) if refresh_token else None
        row.token_expires_at = expires_at
        row.granted_scopes_json = json.dumps(scopes, sort_keys=True)
        row.status = XR7ConnectorStatus.ACTIVE
        row.updated_at = _now()

    db.commit()
    db.refresh(row)
    return row


def run_api_ingestion_pipeline(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    providers: list[str],
    since: datetime | None,
    until: datetime | None,
) -> XR7PipelineResult:
    scheduler = XR7RateLimitScheduler()
    processed = 0
    details: dict[str, object] = {}

    for provider in providers:
        cred = (
            db.query(XR7ConnectorCredential)
            .filter(
                XR7ConnectorCredential.tenant_id == tenant_id,
                XR7ConnectorCredential.artist_id == artist_id,
                XR7ConnectorCredential.provider == provider,
                XR7ConnectorCredential.status == XR7ConnectorStatus.ACTIVE,
            )
            .order_by(XR7ConnectorCredential.updated_at.desc())
            .first()
        )
        if not cred:
            details[provider] = {"status": "missing_credential"}
            continue

        token = open_sealed(cred.encrypted_access_token)
        
        # Use connection pooling via context manager
        with XR7PlatformAPIClient(provider, token) as client:
            payload = client.fetch_all(scheduler, since=since, until=until)

            catalog_rows = payload.get("catalog") or []
            usage_rows = payload.get("usage") or []
            monetization_rows = payload.get("monetization") or []

            for item in catalog_rows:
                track = XR7Track(
                    tenant_id=tenant_id,
                    artist_id=artist_id,
                    title=str(item.get("title") or item.get("name") or "Unknown Track"),
                    version=str(item.get("version") or "") or None,
                    duration_ms=int(item.get("duration_ms") or item.get("duration") or 0) or None,
                    primary_artist_name=str(item.get("artist") or item.get("artist_name") or "")
                    or None,
                    isrc=str(item.get("isrc") or "") or None,
                    upc=str(item.get("upc") or "") or None,
                    label_name=str(item.get("label") or "") or None,
                    distributor=str(item.get("distributor") or "") or None,
                    metadata_json=json.dumps(item, sort_keys=True),
                    source_priority=100,
                    canonical_confidence=0.8,
                )
                db.add(track)
                processed += 1

            for item in usage_rows + monetization_rows:
                event = XR7UsageEvent(
                    tenant_id=tenant_id,
                    artist_id=artist_id,
                    platform=provider,
                    event_type=str(item.get("event_type") or "usage"),
                    event_timestamp=since or _now(),
                    territory=str(item.get("territory") or "") or None,
                    channel=str(item.get("channel") or "api") or "api",
                    units=float(item.get("units") or item.get("plays") or 0.0),
                    asset_ref=str(item.get("asset_ref") or item.get("id") or "") or None,
                    match_method=XR7MatchMethod.API,
                    confidence_score=0.75,
                    monetization_estimate=float(item.get("amount") or item.get("revenue") or 0.0),
                    source_category=XR7SourceCategory.API,
                    raw_ref=str(item.get("id") or "") or None,
                )
                db.add(event)
                processed += 1

            details[provider] = {
                "status": "ingested",
                "catalog_rows": len(catalog_rows),
                "usage_rows": len(usage_rows),
                "monetization_rows": len(monetization_rows),
            }

    db.commit()
    return XR7PipelineResult(
        pipeline="api_ingestion",
        artist_id=artist_id,
        tenant_id=tenant_id,
        status="completed",
        processed=processed,
        details=details,
    )


def run_file_ingestion_pipeline(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    source_system: str,
    filename: str,
    content: bytes,
) -> XR7PipelineResult:
    pipeline = FileIngestionPipeline()
    report = pipeline.process([(filename, content)])
    doc = report.documents[0]

    stmt = XR7RoyaltyStatement(
        tenant_id=tenant_id,
        artist_id=artist_id,
        source_system=source_system,
        currency="USD",
        gross_amount=0.0,
        net_amount=0.0,
        line_count=len(doc.extracted_rows),
        file_ref=filename,
        parse_status="processed" if doc.validation_passed else "failed",
        schema_version="v1",
        ingestion_errors_json=json.dumps(doc.warnings, sort_keys=True),
    )
    db.add(stmt)
    db.flush()

    total_amount = 0.0
    total_units = 0.0

    for idx, row in enumerate(doc.extracted_rows):
        amount = float(row.get("amount") or row.get("net") or 0.0)
        units = float(row.get("units") or row.get("plays") or 0.0)
        total_amount += amount
        total_units += units

        line = XR7RoyaltyStatementLine(
            statement_id=stmt.id,
            row_index=idx,
            raw_work_title=str(row.get("title") or row.get("track") or "") or None,
            raw_artist_name=str(row.get("artist") or "") or None,
            isrc=str(row.get("isrc") or "") or None,
            iswc=str(row.get("iswc") or "") or None,
            territory=str(row.get("territory") or "") or None,
            units=units,
            rate=float(row.get("rate") or 0.0),
            amount=amount,
            currency=str(row.get("currency") or "USD"),
            metadata_json=json.dumps(row, sort_keys=True),
        )
        db.add(line)

    stmt.gross_amount = total_amount
    stmt.net_amount = total_amount

    db.commit()
    return XR7PipelineResult(
        pipeline="file_ingestion",
        artist_id=artist_id,
        tenant_id=tenant_id,
        status="completed",
        processed=stmt.line_count,
        details={
            "statement_id": stmt.id,
            "virus_scan_passed": report.virus_scan_passed,
            "warnings": doc.warnings,
            "units_observed": total_units,
        },
    )


def run_fingerprinting_pipeline(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    platform: str,
    detections: list[dict[str, Any]],
) -> XR7PipelineResult:
    tracks = (
        db.query(XR7Track)
        .filter(XR7Track.tenant_id == tenant_id, XR7Track.artist_id == artist_id)
        .all()
    )
    processed = 0
    matched = 0

    for row in detections:
        title = str(row.get("title") or "")
        artist = str(row.get("artist") or "")
        duration_ms = int(row.get("duration_ms") or 0) or None
        best: XR7Track | None = None
        best_score = 0.0
        for track in tracks:
            score = metadata_triangulation_score(
                title_a=title,
                title_b=track.title,
                artist_a=artist,
                artist_b=track.primary_artist_name,
                duration_ms_a=duration_ms,
                duration_ms_b=track.duration_ms,
                id_match=False,
                context_match=True,
            )
            if score > best_score:
                best_score = score
                best = track

        conf = confidence_score(
            best_score, float(row.get("fingerprint_score") or 0.0), 0.5, 0.6, 0.0
        )
        event = XR7UsageEvent(
            tenant_id=tenant_id,
            artist_id=artist_id,
            platform=platform,
            event_type="fingerprint_detection",
            event_timestamp=_now(),
            territory=str(row.get("territory") or "") or None,
            channel=str(row.get("channel") or "ugc") or "ugc",
            units=float(row.get("units") or 1.0),
            asset_ref=str(row.get("asset_ref") or "") or None,
            track_id=best.id if best and conf >= 0.8 else None,
            match_method=XR7MatchMethod.FINGERPRINT,
            confidence_score=conf,
            monetization_estimate=float(row.get("estimated_value") or 0.0),
            source_category=XR7SourceCategory.FINGERPRINT,
            raw_ref=str(row.get("detection_id") or "") or None,
        )
        db.add(event)
        processed += 1
        if event.track_id:
            matched += 1

    db.commit()
    return XR7PipelineResult(
        pipeline="fingerprinting",
        artist_id=artist_id,
        tenant_id=tenant_id,
        status="completed",
        processed=processed,
        details={"matched": matched, "unmatched": processed - matched},
    )


def run_reconciliation_pipeline(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    min_auto_match: float = 0.92,
) -> XR7PipelineResult:
    works = (
        db.query(XR7Work)
        .filter(XR7Work.tenant_id == tenant_id, XR7Work.artist_id == artist_id)
        .all()
    )
    lines = (
        db.query(XR7RoyaltyStatementLine)
        .join(XR7RoyaltyStatement, XR7RoyaltyStatement.id == XR7RoyaltyStatementLine.statement_id)
        .filter(
            XR7RoyaltyStatement.tenant_id == tenant_id, XR7RoyaltyStatement.artist_id == artist_id
        )
        .all()
    )

    unmatched_count = 0
    for line in lines:
        if line.iswc or line.isrc:
            continue
        title = line.raw_work_title or ""
        if not title:
            continue

        candidates = fuzzy_match_works(title, works)
        if not candidates or candidates[0].score < min_auto_match:
            unmatched = XR7UnmatchedWork(
                tenant_id=tenant_id,
                artist_id=artist_id,
                source_system="statement",
                raw_title=title,
                raw_writer=None,
                raw_identifier=None,
                candidate_work_ids_json=json.dumps([c.work_id for c in candidates], sort_keys=True),
                reason_code="low_match_confidence",
                recommended_action="manual_review",
                status="open",
            )
            db.add(unmatched)
            unmatched_count += 1

    db.commit()

    gap = build_royalty_gap_report(db, tenant_id=tenant_id, artist_id=artist_id)
    return XR7PipelineResult(
        pipeline="reconciliation",
        artist_id=artist_id,
        tenant_id=tenant_id,
        status="completed",
        processed=len(lines),
        details={
            "unmatched_created": unmatched_count,
            "gap_rows": len(gap.rows),
            "total_gap": gap.total_gap,
        },
    )


def build_royalty_gap_report(db: Session, *, tenant_id: str, artist_id: str) -> XR7RoyaltyGapReport:
    usage = (
        db.query(XR7UsageEvent)
        .filter(XR7UsageEvent.tenant_id == tenant_id, XR7UsageEvent.artist_id == artist_id)
        .all()
    )
    statement_lines = (
        db.query(XR7RoyaltyStatementLine)
        .join(XR7RoyaltyStatement, XR7RoyaltyStatement.id == XR7RoyaltyStatementLine.statement_id)
        .filter(
            XR7RoyaltyStatement.tenant_id == tenant_id, XR7RoyaltyStatement.artist_id == artist_id
        )
        .all()
    )

    expected_by_key: dict[tuple[str, str], float] = {}
    for row in usage:
        key = (row.platform, row.territory or "GLOBAL")
        expected_by_key[key] = expected_by_key.get(key, 0.0) + float(
            row.monetization_estimate or 0.0
        )

    reported_by_key: dict[tuple[str, str], float] = {}
    for row in statement_lines:
        key = ("statement", row.territory or "GLOBAL")
        reported_by_key[key] = reported_by_key.get(key, 0.0) + float(row.amount or 0.0)

    rows: list[XR7RoyaltyGapRow] = []
    all_keys = set(expected_by_key) | set(reported_by_key)
    for platform, territory in sorted(all_keys):
        expected = expected_by_key.get((platform, territory), 0.0)
        reported = reported_by_key.get((platform, territory), 0.0)
        gap = expected - reported
        rate = 0.0 if expected <= 0 else gap / expected
        if abs(gap) < 1e-6:
            continue
        rows.append(
            XR7RoyaltyGapRow(
                platform=platform,
                territory=territory,
                expected_amount=round(expected, 2),
                reported_amount=round(reported, 2),
                gap_amount=round(gap, 2),
                gap_rate=round(rate, 4),
            )
        )

    total_expected = round(sum(r.expected_amount for r in rows), 2)
    total_reported = round(sum(r.reported_amount for r in rows), 2)
    total_gap = round(sum(r.gap_amount for r in rows), 2)

    return XR7RoyaltyGapReport(
        artist_id=artist_id,
        tenant_id=tenant_id,
        generated_at=_now(),
        rows=rows,
        total_expected=total_expected,
        total_reported=total_reported,
        total_gap=total_gap,
    )


def run_black_box_detection(
    db: Session,
    *,
    tenant_id: str,
    artist_id: str,
    min_confidence: float = 0.85,
) -> XR7PipelineResult:
    fingerprint_events = (
        db.query(XR7UsageEvent)
        .filter(
            XR7UsageEvent.tenant_id == tenant_id,
            XR7UsageEvent.artist_id == artist_id,
            XR7UsageEvent.source_category == XR7SourceCategory.FINGERPRINT,
            XR7UsageEvent.confidence_score >= min_confidence,
        )
        .all()
    )

    reported_events = (
        db.query(XR7UsageEvent)
        .filter(
            XR7UsageEvent.tenant_id == tenant_id,
            XR7UsageEvent.artist_id == artist_id,
            XR7UsageEvent.source_category == XR7SourceCategory.API,
        )
        .all()
    )

    reported_refs = {e.asset_ref for e in reported_events if e.asset_ref}
    ghost = [e for e in fingerprint_events if e.asset_ref and e.asset_ref not in reported_refs]

    return XR7PipelineResult(
        pipeline="black_box_detection",
        artist_id=artist_id,
        tenant_id=tenant_id,
        status="completed",
        processed=len(fingerprint_events),
        details={
            "ghost_usage_count": len(ghost),
            "ghost_asset_refs": [e.asset_ref for e in ghost[:200]],
        },
    )


def create_sync_job(
    db: Session,
    *,
    artist_id: str,
    integration: str,
    payload: dict[str, Any],
    max_attempts: int,
    queue_backend: str,
) -> SyncJob:
    now = _now()
    job = SyncJob(
        artist_id=artist_id,
        integration=integration,
        status="PENDING",
        attempts=0,
        max_attempts=max_attempts,
        payload_json=json.dumps(payload, sort_keys=True),
        queue_backend=queue_backend,
        enqueued_at=now,
        next_run_at=now,
        updated_at=now,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
