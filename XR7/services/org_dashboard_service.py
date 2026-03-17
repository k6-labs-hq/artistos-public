from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.agents import orchestrator
from XR7.models.anomaly import Anomaly, AnomalyCategory, AnomalyStatus
from XR7.models.artist import Artist
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.evidence_anchor import EvidenceAnchor
from XR7.models.immutable_ledger_entry import ImmutableLedgerEntry
from XR7.models.metadata_issue import MetadataIssue
from XR7.models.sync_job import SyncJob
from XR7.services.post_repair_forecast_pipeline import FORECAST_DISCLAIMER, PostRepairForecastPipeline
from XR7.utils.datetime_utils import as_utc as _as_utc


_DEFAULT_HISTORICAL_START_DATE = datetime(2000, 1, 1, tzinfo=timezone.utc)
_ACTIVE_CLAIM_STATUSES = {
    ClaimStatus.IDENTIFIED.value,
    ClaimStatus.PREPARED.value,
    ClaimStatus.FILED.value,
    ClaimStatus.SUBMITTED.value,
    ClaimStatus.PROOF_SUBMITTED.value,
    ClaimStatus.IN_REVIEW.value,
    ClaimStatus.ACCEPTED.value,
}


def _to_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except Exception:  # noqa: BLE001
        return 0.0


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


class OrgDashboardService:
    """Aggregate org-scoped and global operator dashboard data."""

    def __init__(self, db: Session):
        self.db = db

    def scoped_artists_for_org(self, org_id: str) -> list[Artist]:
        artists = self.db.query(Artist).order_by(Artist.created_at.desc()).all()
        if not artists:
            return []

        explicit = [
            artist
            for artist in artists
            if str(artist.role or "").strip().lower() == f"org:{org_id}".lower()
        ]
        if explicit:
            return explicit

        # Fallback deterministic sharding keeps test/dev tenant data stable
        # before explicit org-to-artist mapping is configured.
        org_bucket = int(hashlib.sha256(org_id.encode("utf-8")).hexdigest(), 16) % 8
        return [
            artist
            for artist in artists
            if int(hashlib.sha256(str(artist.id).encode("utf-8")).hexdigest(), 16) % 8 == org_bucket
        ]

    def _collect_artist_scoped_rows(self, artists: list[Artist]) -> dict[str, Any]:
        artist_ids = [str(a.id) for a in artists]
        if not artist_ids:
            return {
                "anomalies": [],
                "claims": [],
                "metadata_issues": [],
                "sync_jobs": [],
                "ledger_entries": [],
                "evidence_anchors": [],
            }

        anomalies = self.db.query(Anomaly).filter(Anomaly.artist_id.in_(artist_ids)).all()
        claims = self.db.query(Claim).filter(Claim.artist_id.in_(artist_ids)).all()
        metadata_issues = self.db.query(MetadataIssue).filter(MetadataIssue.artist_id.in_(artist_ids)).all()
        sync_jobs = self.db.query(SyncJob).filter(SyncJob.artist_id.in_(artist_ids)).all()
        ledger_entries = self.db.query(ImmutableLedgerEntry).filter(ImmutableLedgerEntry.artist_id.in_(artist_ids)).all()
        claim_ids = [str(c.id) for c in claims]
        evidence_anchors = (
            self.db.query(EvidenceAnchor).filter(EvidenceAnchor.claim_id.in_(claim_ids)).all() if claim_ids else []
        )

        return {
            "anomalies": anomalies,
            "claims": claims,
            "metadata_issues": metadata_issues,
            "sync_jobs": sync_jobs,
            "ledger_entries": ledger_entries,
            "evidence_anchors": evidence_anchors,
        }

    def _aggregate_org_forecast(self, artists: list[Artist]) -> dict[str, Any]:
        end = datetime.now(timezone.utc)
        pipeline = PostRepairForecastPipeline(self.db)

        predicted_total = 0.0
        predicted_low = 0.0
        predicted_high = 0.0
        adjustments: list[float] = []
        per_artist: list[dict[str, Any]] = []

        for artist in artists:
            result = pipeline.run(str(artist.id), _DEFAULT_HISTORICAL_START_DATE, end)
            forecast = result.get("forecast") or {}
            metrics = forecast.get("leakage_avoided_metrics") or {}

            subtotal = _to_float(forecast.get("predicted_total_next_90_days"))
            low = _to_float(forecast.get("predicted_low"))
            high = _to_float(forecast.get("predicted_high"))
            predicted_total += subtotal
            predicted_low += low
            predicted_high += high
            adjustments.append(_to_float(metrics.get("adjustment_factor")))

            per_artist.append(
                {
                    "artist_id": str(artist.id),
                    "artist_name": artist.name,
                    "predicted_total_next_90_days": round(subtotal, 2),
                    "predicted_low": round(low, 2),
                    "predicted_high": round(high, 2),
                    "trend_indicator": forecast.get("trend_indicator") or "stable",
                    "forecast_adjusted_for_repairs": bool(forecast.get("forecast_adjusted_for_repairs")),
                }
            )

        return {
            "predicted_total_next_90_days": round(predicted_total, 2),
            "predicted_low": round(predicted_low, 2),
            "predicted_high": round(predicted_high, 2),
            "artist_count": len(artists),
            "average_adjustment_factor": round(sum(adjustments) / len(adjustments), 4) if adjustments else 1.0,
            "forecast_disclaimer": FORECAST_DISCLAIMER,
            "per_artist": per_artist,
        }

    def management_dashboard(self, org_id: str) -> dict[str, Any]:
        artists = self.scoped_artists_for_org(org_id)
        rows = self._collect_artist_scoped_rows(artists)
        anomalies: list[Anomaly] = rows["anomalies"]
        claims: list[Claim] = rows["claims"]
        metadata_issues: list[MetadataIssue] = rows["metadata_issues"]
        sync_jobs: list[SyncJob] = rows["sync_jobs"]
        ledger_entries: list[ImmutableLedgerEntry] = rows["ledger_entries"]
        evidence_anchors: list[EvidenceAnchor] = rows["evidence_anchors"]

        open_anomalies = [a for a in anomalies if str(a.status) == AnomalyStatus.OPEN.value]
        active_claims = [c for c in claims if str(c.status) in _ACTIVE_CLAIM_STATUSES]
        recovered_paid = [c for c in claims if str(c.status) in {ClaimStatus.PAID.value, ClaimStatus.CLOSED.value}]

        total_recoverable = sum(_to_float(a.estimated_recoverable) for a in anomalies)
        active_recoverable = sum(_to_float(a.estimated_recoverable) for a in open_anomalies)
        recovered_total = sum(_to_float(c.recovered_amount) for c in recovered_paid)
        money_left_index = round((active_recoverable / max(active_recoverable + recovered_total, 1.0)) * 100.0, 2)

        resolved_issues = [i for i in metadata_issues if str(i.repair_status).upper() in {"REPAIRED", "AUTO_REPAIRED"}]
        metadata_health_score = round((len(resolved_issues) / max(len(metadata_issues), 1)) * 100.0, 2)

        now = datetime.now(timezone.utc)
        sol_urgent = 0
        sol_watch = 0
        sol_expired = 0
        for claim in claims:
            if not claim.sol_deadline:
                continue
            sol_deadline = _as_utc(claim.sol_deadline)
            if not sol_deadline:
                continue
            delta_days = (sol_deadline - now).days
            if delta_days < 0:
                sol_expired += 1
            elif delta_days <= 30:
                sol_urgent += 1
            elif delta_days <= 90:
                sol_watch += 1

        ugc_candidates = [
            a
            for a in anomalies
            if str(a.category) in {AnomalyCategory.PLATFORM.value, AnomalyCategory.BRAND.value}
            or "ugc" in str(a.subtype or "").lower()
        ]

        queue_depth = {
            "pending": sum(1 for j in sync_jobs if str(j.status) == "PENDING"),
            "running": sum(1 for j in sync_jobs if str(j.status) == "RUNNING"),
            "retrying": sum(1 for j in sync_jobs if str(j.status) == "RETRYING"),
            "failed": sum(1 for j in sync_jobs if str(j.status) == "FAILED"),
            "completed": sum(1 for j in sync_jobs if str(j.status) == "COMPLETED"),
        }

        notifications = []
        if sol_urgent or sol_expired:
            notifications.append(
                {
                    "severity": "high",
                    "message": f"{sol_urgent + sol_expired} claim(s) require immediate SOL action.",
                }
            )
        if queue_depth["failed"] > 0:
            notifications.append(
                {
                    "severity": "medium",
                    "message": f"{queue_depth['failed']} failed ingestion/sync job(s) need retry.",
                }
            )
        if not notifications:
            notifications.append(
                {
                    "severity": "info",
                    "message": "No urgent cross-portfolio blockers detected.",
                }
            )

        forecast = self._aggregate_org_forecast(artists)
        drilldown_links = {
            "artists": f"/management/{org_id}/artists",
            "catalog": f"/management/{org_id}/catalog",
            "anomalies": f"/management/{org_id}/anomalies",
            "claims": f"/management/{org_id}/claims",
            "forecast": f"/management/{org_id}/forecast",
        }

        return {
            "org_id": org_id,
            "portfolio_overview": {
                "artist_count": len(artists),
                "anomaly_count": len(anomalies),
                "open_anomaly_count": len(open_anomalies),
                "active_claim_count": len(active_claims),
                "total_estimated_recoverable": round(total_recoverable, 2),
            },
            "wow_factor_analytics": {
                "metadata_health_score": metadata_health_score,
                "sol_risk_map": {
                    "urgent": sol_urgent,
                    "watchlist": sol_watch,
                    "expired": sol_expired,
                },
                "ugc_scanner": {
                    "ugc_signal_count": len(ugc_candidates),
                    "estimated_ugc_recoverable": round(sum(_to_float(a.estimated_recoverable) for a in ugc_candidates), 2),
                },
                "money_left_index": {
                    "score": money_left_index,
                    "active_recoverable": round(active_recoverable, 2),
                    "recovered_total": round(recovered_total, 2),
                },
                "repair_ledger": {
                    "entries": len(ledger_entries),
                    "metadata_repairs": len(resolved_issues),
                    "metadata_backlog": max(len(metadata_issues) - len(resolved_issues), 0),
                },
                "evidence_vault": {
                    "anchors_total": len(evidence_anchors),
                    "anchored": sum(1 for e in evidence_anchors if str(e.blockchain_status).upper() == "ANCHORED"),
                    "pending": sum(1 for e in evidence_anchors if str(e.blockchain_status).upper() != "ANCHORED"),
                },
            },
            "forecast": forecast,
            "notifications": notifications,
            "ingestion_health": {
                "queue_depth": queue_depth,
            },
            "drilldowns": drilldown_links,
        }

    def management_artist_detail(self, org_id: str, artist_id: str) -> dict[str, Any]:
        artists = self.scoped_artists_for_org(org_id)
        allowed = {str(a.id): a for a in artists}
        if artist_id not in allowed:
            raise LookupError("Artist not found for organization")
        artist = allowed[artist_id]

        anomalies = self.db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        claims = self.db.query(Claim).filter(Claim.artist_id == artist_id).all()
        metadata_issues = self.db.query(MetadataIssue).filter(MetadataIssue.artist_id == artist_id).all()
        forecast = self._aggregate_org_forecast([artist])

        return {
            "org_id": org_id,
            "artist": {
                "id": artist.id,
                "name": artist.name,
                "email": artist.email,
                "status": artist.status,
                "created_at": _iso(artist.created_at),
            },
            "anomalies": {
                "count": len(anomalies),
                "open": sum(1 for a in anomalies if str(a.status) == AnomalyStatus.OPEN.value),
                "estimated_recoverable": round(sum(_to_float(a.estimated_recoverable) for a in anomalies), 2),
            },
            "claims": {
                "count": len(claims),
                "active": sum(1 for c in claims if str(c.status) in _ACTIVE_CLAIM_STATUSES),
                "paid": sum(1 for c in claims if str(c.status) == ClaimStatus.PAID.value),
            },
            "catalog": {
                "metadata_issue_count": len(metadata_issues),
                "metadata_repairs": sum(
                    1 for i in metadata_issues if str(i.repair_status).upper() in {"REPAIRED", "AUTO_REPAIRED"}
                ),
            },
            "forecast": {
                "predicted_total_next_90_days": forecast["predicted_total_next_90_days"],
                "predicted_low": forecast["predicted_low"],
                "predicted_high": forecast["predicted_high"],
                "forecast_disclaimer": FORECAST_DISCLAIMER,
            },
        }

    def management_catalog(self, org_id: str) -> dict[str, Any]:
        artists = self.scoped_artists_for_org(org_id)
        artist_ids = [str(a.id) for a in artists]
        metadata_issues = (
            self.db.query(MetadataIssue).filter(MetadataIssue.artist_id.in_(artist_ids)).all() if artist_ids else []
        )
        by_artist: dict[str, dict[str, Any]] = {str(a.id): {"artist_name": a.name, "issue_count": 0, "repaired": 0} for a in artists}
        for issue in metadata_issues:
            row = by_artist.get(str(issue.artist_id))
            if not row:
                continue
            row["issue_count"] += 1
            if str(issue.repair_status).upper() in {"REPAIRED", "AUTO_REPAIRED"}:
                row["repaired"] += 1

        return {
            "org_id": org_id,
            "catalog_health": [
                {
                    "artist_id": artist_id,
                    **data,
                    "repair_rate": round((data["repaired"] / max(data["issue_count"], 1)) * 100.0, 2),
                }
                for artist_id, data in by_artist.items()
            ],
        }

    def management_anomalies(
        self,
        org_id: str,
        *,
        severity: str | None,
        status: str | None,
        category: str | None,
        limit: int,
    ) -> dict[str, Any]:
        artists = self.scoped_artists_for_org(org_id)
        artist_ids = [str(a.id) for a in artists]
        if not artist_ids:
            return {"org_id": org_id, "count": 0, "items": []}

        query = self.db.query(Anomaly).filter(Anomaly.artist_id.in_(artist_ids))
        if severity:
            query = query.filter(Anomaly.severity == severity.upper())
        if status:
            query = query.filter(Anomaly.status == status.upper())
        if category:
            query = query.filter(Anomaly.category == category.upper())
        rows = query.order_by(Anomaly.created_at.desc()).limit(max(1, min(limit, 250))).all()

        return {
            "org_id": org_id,
            "count": len(rows),
            "items": [
                {
                    "id": r.id,
                    "artist_id": r.artist_id,
                    "category": r.category,
                    "subtype": r.subtype,
                    "severity": r.severity,
                    "status": r.status,
                    "estimated_recoverable": _to_float(r.estimated_recoverable),
                    "created_at": _iso(r.created_at),
                }
                for r in rows
            ],
        }

    def management_claims(
        self,
        org_id: str,
        *,
        status: str | None,
        sol_window_days: int,
        limit: int,
    ) -> dict[str, Any]:
        artists = self.scoped_artists_for_org(org_id)
        artist_ids = [str(a.id) for a in artists]
        if not artist_ids:
            return {"org_id": org_id, "count": 0, "items": []}

        query = self.db.query(Claim).filter(Claim.artist_id.in_(artist_ids))
        if status:
            query = query.filter(Claim.status == status.upper())
        claims = query.order_by(Claim.updated_at.desc()).limit(max(1, min(limit, 250))).all()

        now = datetime.now(timezone.utc)
        items = []
        for c in claims:
            sol_days_remaining = None
            in_window = False
            if c.sol_deadline:
                sol_deadline = _as_utc(c.sol_deadline)
                if sol_deadline:
                    sol_days_remaining = (sol_deadline - now).days
                    in_window = sol_days_remaining <= sol_window_days
            items.append(
                {
                    "id": c.id,
                    "artist_id": c.artist_id,
                    "status": c.status,
                    "claim_type": c.claim_type,
                    "recovered_amount": _to_float(c.recovered_amount),
                    "sol_deadline": _iso(c.sol_deadline),
                    "sol_days_remaining": sol_days_remaining,
                    "in_sol_window": in_window,
                    "updated_at": _iso(c.updated_at),
                }
            )

        return {
            "org_id": org_id,
            "count": len(items),
            "items": items,
        }

    def management_forecast(self, org_id: str) -> dict[str, Any]:
        artists = self.scoped_artists_for_org(org_id)
        forecast = self._aggregate_org_forecast(artists)
        return {
            "org_id": org_id,
            **forecast,
        }

    def operator_dashboard(self) -> dict[str, Any]:
        artists = self.db.query(Artist).all()
        rows = self._collect_artist_scoped_rows(artists)
        anomalies: list[Anomaly] = rows["anomalies"]
        claims: list[Claim] = rows["claims"]
        sync_jobs: list[SyncJob] = rows["sync_jobs"]
        metadata_issues: list[MetadataIssue] = rows["metadata_issues"]

        open_anomalies = [a for a in anomalies if str(a.status) == AnomalyStatus.OPEN.value]
        active_claims = [c for c in claims if str(c.status) in _ACTIVE_CLAIM_STATUSES]

        by_category: dict[str, int] = {}
        for anomaly in open_anomalies:
            key = str(anomaly.category)
            by_category[key] = by_category.get(key, 0) + 1

        queue_depth = {
            "pending": sum(1 for j in sync_jobs if str(j.status) == "PENDING"),
            "running": sum(1 for j in sync_jobs if str(j.status) == "RUNNING"),
            "retrying": sum(1 for j in sync_jobs if str(j.status) == "RETRYING"),
            "failed": sum(1 for j in sync_jobs if str(j.status) == "FAILED"),
            "completed": sum(1 for j in sync_jobs if str(j.status) == "COMPLETED"),
        }

        run_state = getattr(orchestrator, "_RUN_STATE", {})
        now = datetime.now(timezone.utc)
        recent_runs = []
        for run_id, state in list(run_state.items())[:25]:
            recent_runs.append(
                {
                    "run_id": run_id,
                    "artist_id": state.get("artist_id"),
                    "current_step": state.get("current_step"),
                    "last_updated_at": _iso(state.get("updated_at") if isinstance(state.get("updated_at"), datetime) else now),
                }
            )

        return {
            "global_feed": {
                "artist_count": len(artists),
                "open_anomaly_count": len(open_anomalies),
                "active_claim_count": len(active_claims),
                "metadata_issue_backlog": sum(
                    1 for i in metadata_issues if str(i.repair_status).upper() not in {"REPAIRED", "AUTO_REPAIRED"}
                ),
                "failed_sync_jobs": queue_depth["failed"],
            },
            "system_health": {
                "sync_queue_depth": queue_depth,
                "retry_pressure_score": round(
                    (queue_depth["retrying"] + queue_depth["failed"]) / max(sum(queue_depth.values()), 1) * 100.0,
                    2,
                ),
            },
            "activity_map": {
                "open_anomalies_by_category": by_category,
                "recent_claim_updates_last_7_days": sum(
                    1
                    for c in claims
                    if _as_utc(c.updated_at) and _as_utc(c.updated_at) >= (now - timedelta(days=7))
                ),
            },
            "pipeline_overview": {
                "active_runs": len(run_state),
                "recent_runs": recent_runs,
            },
            "drilldowns": {
                "org_management": "/management/{org_id}/dashboard",
                "claims": "/management/{org_id}/claims",
                "anomalies": "/management/{org_id}/anomalies",
            },
        }