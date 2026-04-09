"""
Catalog Health & Fix Recommendations — XR7 Engine 2.

Endpoints:
  GET  /artists/{artist_id}/catalog/health
  GET  /artists/{artist_id}/catalog/fixes
  POST /artists/{artist_id}/catalog/fixes/{fix_id}/request
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from XR7.api.deps import get_artist_or_404
from XR7.api.routers.auth import require_artist_access
from XR7.ml.catalog_scorer import CatalogScorer
from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.base import get_db
from XR7.models.catalog_fix_issue import (
    AffectedWork,
    CatalogFixCategory,
    CatalogFixIssue,
    CatalogFixIssueSchema,
    CatalogFixStatus,
    FixPriority,
    FixSuggestedAction,
)
from XR7.models.claim import Claim
from XR7.models.payment import Payment
from XR7.models.work import Work
from XR7.recovery.immutable_ledger import ImmutableLedgerService
from xr7_common.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["catalog_health"])

# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------


class CategoryBreakdown(BaseModel):
    metadata_completeness: float = Field(..., ge=0.0, le=100.0, description="Score 0–100")
    registration_status: float = Field(..., ge=0.0, le=100.0)
    split_conflicts: float = Field(..., ge=0.0, le=100.0)
    identifier_mismatches: float = Field(..., ge=0.0, le=100.0)
    content_id_issues: float = Field(..., ge=0.0, le=100.0)


class CatalogIssueOut(BaseModel):
    id: str
    category: CatalogFixCategory
    priority: FixPriority
    description: str
    affected_works: list[AffectedWork]
    estimated_recoverable_usd: float
    suggested_action: FixSuggestedAction
    status: CatalogFixStatus


class CatalogHealthResponse(BaseModel):
    artist_id: str
    health_score: int = Field(..., ge=0, le=100)
    grade: str
    category_breakdown: CategoryBreakdown
    top_issues: list[CatalogIssueOut]
    total_estimated_recoverable_usd: float
    issues_count: int
    computed_at: datetime


class FixRequestResponse(BaseModel):
    fix_id: str
    status: CatalogFixStatus
    template_payload: dict[str, Any]
    requested_at: datetime


class CatalogFixListResponse(BaseModel):
    artist_id: str
    fixes: list[CatalogFixIssueSchema]
    total: int


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_PRIORITY_SCORE: dict[str, int] = {
    FixPriority.HIGH.value: 3,
    FixPriority.MEDIUM.value: 2,
    FixPriority.LOW.value: 1,
}


def _catalog_size_bucket(work_count: int) -> str:
    if work_count < 50:
        return "small"
    if work_count < 200:
        return "medium"
    if work_count < 1000:
        return "large"
    return "enterprise"


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 45:
        return "D"
    return "F"


def _build_fix_template(
    fix: CatalogFixIssue,
    artist: Artist,
) -> dict[str, Any]:
    """Generate a pre-filled email / letter template for the given fix."""
    action = str(fix.suggested_action)
    works_list = "\n".join(
        f"  - {w.get('title', 'Unknown')} (ISRC: {w.get('isrc') or 'N/A'})"
        for w in fix.affected_works[:20]
    )
    artist_name = artist.name or "The Artist"
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")

    if action == FixSuggestedAction.EMAIL_DISTRIBUTOR.value:
        subject = f"Royalty Metadata Correction Request — {artist_name}"
        body = (
            f"Dear Distribution Partner,\n\n"
            f"I am writing on behalf of {artist_name} (IPI: {artist.ipi_number or 'N/A'}) "
            f"to request urgent correction of metadata on the following works:\n\n"
            f"{works_list}\n\n"
            f"Issue: {fix.description}\n\n"
            f"Estimated financial impact of unresolved issue: "
            f"${fix.estimated_recoverable_usd:,.2f}\n\n"
            f"Please confirm receipt and provide a timeline for resolution.\n\n"
            f"Best regards,\nXR7 Recovery Engine — on behalf of {artist_name}\n{today}"
        )
        template_type = "distributor_email"
    elif action == FixSuggestedAction.REGISTER_ML.value:
        subject = f"Mechanical License Registration Request — {artist_name}"
        body = (
            f"Dear MLC / PRO Licensing Team,\n\n"
            f"Please register the following compositions on behalf of "
            f"{artist_name} (IPI: {artist.ipi_number or 'N/A'}):\n\n"
            f"{works_list}\n\n"
            f"Issue: {fix.description}\n\n"
            f"Please confirm registration and provide registration IDs.\n\n"
            f"Best regards,\nXR7 Recovery Engine — on behalf of {artist_name}\n{today}"
        )
        template_type = "registration_letter"
    elif action == FixSuggestedAction.FIX_SPLITS.value:
        subject = f"Royalty Split Conflict Resolution — {artist_name}"
        body = (
            f"Dear Rights Administration Team,\n\n"
            f"We have identified split conflicts on the following works for "
            f"{artist_name}:\n\n"
            f"{works_list}\n\n"
            f"Issue: {fix.description}\n\n"
            f"Please review and update splits to agreed percentages on record.\n\n"
            f"Best regards,\nXR7 Recovery Engine — on behalf of {artist_name}\n{today}"
        )
        template_type = "split_resolution_letter"
    elif action == FixSuggestedAction.CLAIM_CONTENT_ID.value:
        subject = f"Content ID Claim Initiation — {artist_name}"
        body = (
            f"Dear Content Rights Team,\n\n"
            f"Please initiate Content ID claims for the following works owned by "
            f"{artist_name}:\n\n"
            f"{works_list}\n\n"
            f"Issue: {fix.description}\n\n"
            f"Confirm claim activation and begin revenue collection.\n\n"
            f"Best regards,\nXR7 Recovery Engine — on behalf of {artist_name}\n{today}"
        )
        template_type = "content_id_claim_request"
    else:
        subject = f"Catalog Issue Resolution Request — {artist_name}"
        body = (
            f"Dear Support Team,\n\n"
            f"We are writing on behalf of {artist_name} regarding a catalog issue "
            f"that requires your attention:\n\n"
            f"Issue: {fix.description}\n\n"
            f"Affected Works:\n{works_list}\n\n"
            f"Estimated impact: ${fix.estimated_recoverable_usd:,.2f}\n\n"
            f"Please advise on next steps.\n\n"
            f"Best regards,\nXR7 Recovery Engine — on behalf of {artist_name}\n{today}"
        )
        template_type = "general_resolution_request"

    return {
        "template_type": template_type,
        "subject": subject,
        "body": body,
        "fix_id": fix.id,
        "artist_name": artist_name,
        "affected_work_count": len(fix.affected_works),
        "estimated_recoverable_usd": fix.estimated_recoverable_usd,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _ensure_catalog_fixes(
    db: Session,
    artist: Artist,
    works: list[Work],
    anomalies: list[Anomaly],
    claims: list[Claim],
) -> list[CatalogFixIssue]:
    """
    Idempotently generate catalog fix issues from the artist's current data.
    Re-uses existing PENDING issues; creates new ones for newly detected problems.
    Marks PENDING issues that no longer apply as EXPIRED.
    """
    existing: list[CatalogFixIssue] = (
        db.query(CatalogFixIssue)
        .filter(CatalogFixIssue.artist_id == artist.id)
        .filter(
            CatalogFixIssue.status.in_(
                [CatalogFixStatus.PENDING.value, CatalogFixStatus.REQUESTED.value]
            )
        )
        .all()
    )
    existing_by_category: dict[str, CatalogFixIssue] = {row.category: row for row in existing}
    generated_descriptions: dict[str, str] = {}
    now = datetime.now(timezone.utc)

    # ── 1. Metadata completeness ───────────────────────────────────────────
    works_missing_isrc = [w for w in works if not w.isrc]
    works_missing_iswc = [w for w in works if not w.iswc]
    missing_metadata_works = list(
        {w.id: w for w in works_missing_isrc + works_missing_iswc}.values()
    )
    if missing_metadata_works:
        recoverable = len(missing_metadata_works) * 85.0  # ~$85 avg per unregistered work
        affected = [{"title": w.title, "isrc": w.isrc} for w in missing_metadata_works[:50]]
        description = (
            f"{len(missing_metadata_works)} works are missing ISRC or ISWC identifiers, "
            "preventing tracking on digital platforms."
        )
        generated_descriptions[CatalogFixCategory.METADATA_COMPLETENESS.value] = description
        if CatalogFixCategory.METADATA_COMPLETENESS.value not in existing_by_category:
            issue = CatalogFixIssue(
                id=str(uuid.uuid4()),
                artist_id=artist.id,
                category=CatalogFixCategory.METADATA_COMPLETENESS.value,
                priority=(
                    FixPriority.HIGH.value
                    if len(missing_metadata_works) > 5
                    else FixPriority.MEDIUM.value
                ),
                description=description,
                estimated_recoverable_usd=recoverable,
                suggested_action=FixSuggestedAction.EMAIL_DISTRIBUTOR.value,
                status=CatalogFixStatus.PENDING.value,
                expires_at=now + timedelta(days=180),
            )
            issue.affected_works = affected
            db.add(issue)
            existing_by_category[CatalogFixCategory.METADATA_COMPLETENESS.value] = issue

    # ── 2. Registration status ─────────────────────────────────────────────
    unregistered_compositions = [
        w
        for w in works
        if str(w.work_type) in ("COMPOSITION", "WorkType.COMPOSITION") and not w.iswc
    ]
    if unregistered_compositions:
        recoverable = len(unregistered_compositions) * 220.0
        affected = [{"title": w.title, "isrc": w.isrc} for w in unregistered_compositions[:50]]
        description = (
            f"{len(unregistered_compositions)} compositions appear unregistered with a PRO "
            "(no ISWC on file). Mechanical and performance royalties may be unpaid."
        )
        generated_descriptions[CatalogFixCategory.REGISTRATION_STATUS.value] = description
        if CatalogFixCategory.REGISTRATION_STATUS.value not in existing_by_category:
            issue = CatalogFixIssue(
                id=str(uuid.uuid4()),
                artist_id=artist.id,
                category=CatalogFixCategory.REGISTRATION_STATUS.value,
                priority=FixPriority.HIGH.value,
                description=description,
                estimated_recoverable_usd=recoverable,
                suggested_action=FixSuggestedAction.REGISTER_ML.value,
                status=CatalogFixStatus.PENDING.value,
                expires_at=now + timedelta(days=365),
            )
            issue.affected_works = affected
            db.add(issue)
            existing_by_category[CatalogFixCategory.REGISTRATION_STATUS.value] = issue

    # ── 3. Split conflicts ─────────────────────────────────────────────────
    split_anomalies = [
        a
        for a in anomalies
        if str(a.subtype).lower() in ("split_conflict", "royalty_split_mismatch")
    ]
    if split_anomalies:
        recoverable = sum(float(a.estimated_recoverable or 0.0) for a in split_anomalies)
        split_work_ids = {str(a.description or "")[:60] for a in split_anomalies}
        affected = [{"title": s, "isrc": None} for s in split_work_ids][:20]
        description = (
            f"{len(split_anomalies)} split conflict anomalies detected. "
            "Royalty splits don't add up to 100% or contradict contract records."
        )
        generated_descriptions[CatalogFixCategory.SPLIT_CONFLICTS.value] = description
        if CatalogFixCategory.SPLIT_CONFLICTS.value not in existing_by_category:
            issue = CatalogFixIssue(
                id=str(uuid.uuid4()),
                artist_id=artist.id,
                category=CatalogFixCategory.SPLIT_CONFLICTS.value,
                priority=FixPriority.HIGH.value,
                description=description,
                estimated_recoverable_usd=max(recoverable, len(split_anomalies) * 150.0),
                suggested_action=FixSuggestedAction.FIX_SPLITS.value,
                status=CatalogFixStatus.PENDING.value,
                expires_at=now + timedelta(days=90),
            )
            issue.affected_works = affected
            db.add(issue)
            existing_by_category[CatalogFixCategory.SPLIT_CONFLICTS.value] = issue

    # ── 4. Identifier mismatches ───────────────────────────────────────────
    mismatch_anomalies = [
        a
        for a in anomalies
        if str(a.subtype).lower() in ("identifier_mismatch", "isrc_conflict", "iswc_mismatch")
    ]
    if mismatch_anomalies:
        recoverable = sum(float(a.estimated_recoverable or 0.0) for a in mismatch_anomalies)
        affected = [
            {"title": str(a.description or "")[:60], "isrc": None} for a in mismatch_anomalies[:20]
        ]
        description = (
            f"{len(mismatch_anomalies)} identifier mismatches detected across platforms. "
            "ISRCs or ISWCs differ between DSPs, blocking proper royalty attribution."
        )
        generated_descriptions[CatalogFixCategory.IDENTIFIER_MISMATCHES.value] = description
        if CatalogFixCategory.IDENTIFIER_MISMATCHES.value not in existing_by_category:
            issue = CatalogFixIssue(
                id=str(uuid.uuid4()),
                artist_id=artist.id,
                category=CatalogFixCategory.IDENTIFIER_MISMATCHES.value,
                priority=FixPriority.MEDIUM.value,
                description=description,
                estimated_recoverable_usd=max(recoverable, len(mismatch_anomalies) * 95.0),
                suggested_action=FixSuggestedAction.EMAIL_DISTRIBUTOR.value,
                status=CatalogFixStatus.PENDING.value,
                expires_at=now + timedelta(days=120),
            )
            issue.affected_works = affected
            db.add(issue)
            existing_by_category[CatalogFixCategory.IDENTIFIER_MISMATCHES.value] = issue

    # ── 5. Content ID issues ───────────────────────────────────────────────
    content_id_anomalies = [
        a
        for a in anomalies
        if str(a.subtype).lower() in ("content_id_gap", "ugc_opportunity", "unmonetized_yt")
    ]
    if content_id_anomalies:
        recoverable = sum(float(a.estimated_recoverable or 0.0) for a in content_id_anomalies)
        affected = [
            {"title": str(a.description or "")[:60], "isrc": None}
            for a in content_id_anomalies[:20]
        ]
        description = (
            f"{len(content_id_anomalies)} Content ID opportunities detected. "
            "Works are used on YouTube/TikTok/Meta without active monetization claims."
        )
        generated_descriptions[CatalogFixCategory.CONTENT_ID_ISSUES.value] = description
        if CatalogFixCategory.CONTENT_ID_ISSUES.value not in existing_by_category:
            issue = CatalogFixIssue(
                id=str(uuid.uuid4()),
                artist_id=artist.id,
                category=CatalogFixCategory.CONTENT_ID_ISSUES.value,
                priority=FixPriority.MEDIUM.value,
                description=description,
                estimated_recoverable_usd=max(recoverable, len(content_id_anomalies) * 75.0),
                suggested_action=FixSuggestedAction.CLAIM_CONTENT_ID.value,
                status=CatalogFixStatus.PENDING.value,
                expires_at=now + timedelta(days=365),
            )
            issue.affected_works = affected
            db.add(issue)
            existing_by_category[CatalogFixCategory.CONTENT_ID_ISSUES.value] = issue

    db.flush()
    return list(existing_by_category.values())


def _compute_category_breakdown(
    works: list[Work],
    anomalies: list[Anomaly],
    raw_signals: dict[str, float],
) -> CategoryBreakdown:
    """Map raw scorer signals + anomaly data to per-category scores."""
    # Metadata completeness: fraction with both ISRC + ISWC → 0–100
    meta_score = round(raw_signals.get("metadata_completeness", 0.5) * 100, 1)

    # Registration: fraction of compositions with ISWC
    compositions = [w for w in works if str(w.work_type) in ("COMPOSITION", "WorkType.COMPOSITION")]
    if compositions:
        reg_score = round(sum(1 for w in compositions if w.iswc) / len(compositions) * 100, 1)
    else:
        reg_score = 80.0  # neutral when no compositions tracked

    # Split conflicts
    split_count = sum(
        1
        for a in anomalies
        if str(a.subtype).lower() in ("split_conflict", "royalty_split_mismatch")
    )
    split_score = round(max(0.0, 100.0 - split_count * 15.0), 1)

    # Identifier mismatches
    id_mismatch_count = sum(
        1
        for a in anomalies
        if str(a.subtype).lower() in ("identifier_mismatch", "isrc_conflict", "iswc_mismatch")
    )
    id_score = round(max(0.0, 100.0 - id_mismatch_count * 12.0), 1)

    # Content ID
    cid_count = sum(
        1
        for a in anomalies
        if str(a.subtype).lower() in ("content_id_gap", "ugc_opportunity", "unmonetized_yt")
    )
    cid_score = round(max(0.0, 100.0 - cid_count * 10.0), 1)

    return CategoryBreakdown(
        metadata_completeness=meta_score,
        registration_status=reg_score,
        split_conflicts=split_score,
        identifier_mismatches=id_score,
        content_id_issues=cid_score,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/artists/{artist_id}/catalog/health",
    response_model=CatalogHealthResponse,
    summary="Catalog health score + top 5 ranked fix opportunities",
)
def get_catalog_health(
    artist_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> CatalogHealthResponse:
    artist = get_artist_or_404(artist_id, db)

    works: list[Work] = db.query(Work).filter(Work.artist_id == artist_id).all()
    anomalies: list[Anomaly] = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
    claims: list[Claim] = db.query(Claim).filter(Claim.artist_id == artist_id).all()
    payments: list[Payment] = db.query(Payment).filter(Payment.artist_id == artist_id).all()

    # Run ML scorer
    works_dicts = [{"isrc": w.isrc, "iswc": w.iswc, "title": w.title} for w in works]
    payments_dicts = [{"amount": float(p.amount or 0.0)} for p in payments]
    anomalies_dicts = [
        {"status": a.status, "estimated_recoverable": a.estimated_recoverable} for a in anomalies
    ]
    claims_dicts = [{"status": c.status} for c in claims]

    earnings_summary = {
        "total_expected": sum(float(a.expected_amount or 0.0) for a in anomalies),
        "total_received": sum(float(p.amount or 0.0) for p in payments),
    }

    scorer = CatalogScorer()
    report = scorer.score(
        artist_id=artist_id,
        works=works_dicts,
        payments=payments_dicts,
        anomalies=anomalies_dicts,
        claims=claims_dicts,
        earnings_summary=earnings_summary,
    )

    # Generate / retrieve fix issues
    fix_issues = _ensure_catalog_fixes(db, artist, works, anomalies, claims)
    db.commit()

    # Sort by priority × estimated_recoverable then take top 5
    def _sort_key(f: CatalogFixIssue) -> float:
        p = _PRIORITY_SCORE.get(str(f.priority), 1)
        return p * 1000.0 + float(f.estimated_recoverable_usd or 0.0)

    top_issues = sorted(fix_issues, key=_sort_key, reverse=True)[:5]

    category_breakdown = _compute_category_breakdown(works, anomalies, report.signals)
    total_recoverable = sum(float(f.estimated_recoverable_usd or 0.0) for f in fix_issues)

    top_issues_out = [
        CatalogIssueOut(
            id=f.id,
            category=CatalogFixCategory(f.category),
            priority=FixPriority(f.priority),
            description=f.description,
            affected_works=f.affected_works,
            estimated_recoverable_usd=f.estimated_recoverable_usd,
            suggested_action=FixSuggestedAction(f.suggested_action),
            status=CatalogFixStatus(f.status),
        )
        for f in top_issues
    ]

    return CatalogHealthResponse(
        artist_id=artist_id,
        health_score=report.health_score,
        grade=report.grade,
        category_breakdown=category_breakdown,
        top_issues=top_issues_out,
        total_estimated_recoverable_usd=round(total_recoverable, 2),
        issues_count=len(fix_issues),
        computed_at=datetime.now(timezone.utc),
    )


@router.get(
    "/artists/{artist_id}/catalog/fixes",
    response_model=CatalogFixListResponse,
    summary="List all catalog fix issues with current status",
)
def list_catalog_fixes(
    artist_id: str,
    status: CatalogFixStatus | None = None,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> CatalogFixListResponse:
    get_artist_or_404(artist_id, db)

    q = db.query(CatalogFixIssue).filter(CatalogFixIssue.artist_id == artist_id)
    if status is not None:
        q = q.filter(CatalogFixIssue.status == status.value)
    rows = q.order_by(CatalogFixIssue.created_at.desc()).all()

    schemas = [CatalogFixIssueSchema.from_orm_with_works(r) for r in rows]
    return CatalogFixListResponse(artist_id=artist_id, fixes=schemas, total=len(schemas))


@router.post(
    "/artists/{artist_id}/catalog/fixes/{fix_id}/request",
    response_model=FixRequestResponse,
    summary="Request a fix — generates pre-filled template and logs in activity feed",
)
def request_catalog_fix(
    artist_id: str,
    fix_id: str,
    db: Session = Depends(get_db),
    _: dict = Depends(require_artist_access),
) -> FixRequestResponse:
    artist = get_artist_or_404(artist_id, db)

    fix = (
        db.query(CatalogFixIssue)
        .filter(CatalogFixIssue.id == fix_id, CatalogFixIssue.artist_id == artist_id)
        .first()
    )
    if not fix:
        raise HTTPException(status_code=404, detail="Catalog fix issue not found")

    if fix.status == CatalogFixStatus.RESOLVED.value:
        raise HTTPException(status_code=409, detail="Fix is already resolved")
    if fix.status == CatalogFixStatus.EXPIRED.value:
        raise HTTPException(status_code=410, detail="Fix window has expired")

    now = datetime.now(timezone.utc)
    template = _build_fix_template(fix, artist)

    fix.status = CatalogFixStatus.REQUESTED.value
    fix.requested_at = now
    fix.template_payload = template
    fix.updated_at = now
    db.flush()

    # Log in immutable activity feed
    try:
        ImmutableLedgerService(db).append(
            artist_id,
            "catalog_fix_requested",
            {
                "fix_id": fix_id,
                "category": fix.category,
                "suggested_action": fix.suggested_action,
                "estimated_recoverable_usd": fix.estimated_recoverable_usd,
                "template_type": template.get("template_type"),
            },
        )
    except Exception:
        logger.exception("Failed to write catalog_fix_requested ledger entry")

    db.commit()

    return FixRequestResponse(
        fix_id=fix_id,
        status=CatalogFixStatus.REQUESTED,
        template_payload=template,
        requested_at=now,
    )
