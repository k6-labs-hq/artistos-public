from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.recovery.immutable_ledger import ImmutableLedgerService


def _to_utc(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            return None
    return None


def _hash_payload(payload: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class DiscoveryTrigger:
    key: str
    label: str


_TRIGGER_PRIORITY: list[DiscoveryTrigger] = [
    DiscoveryTrigger("statement_receipt_date", "Statement receipt date with anomaly visible"),
    DiscoveryTrigger(
        "metadata_repair_event_date", "Metadata repair event revealing misattribution"
    ),
    DiscoveryTrigger("third_party_audit_date", "Third-party audit or PRO data release"),
    DiscoveryTrigger("xr7_detection_timestamp", "XR7 detection timestamp (constructive discovery)"),
    DiscoveryTrigger("industry_publication_date", "Industry publication or society announcement"),
]


def _us_deadline(discovery_date: datetime) -> datetime:
    return discovery_date + timedelta(days=365 * 3)


def _uk_deadline(discovery_date: datetime) -> datetime:
    return discovery_date + timedelta(days=365 * 6)


def _de_deadline(discovery_date: datetime) -> datetime:
    end_of_year = datetime(discovery_date.year, 12, 31, tzinfo=timezone.utc)
    return end_of_year + timedelta(days=365 * 3)


def _fr_deadline(discovery_date: datetime) -> datetime:
    return discovery_date + timedelta(days=365 * 5)


def _jp_deadline(discovery_date: datetime) -> datetime:
    return discovery_date + timedelta(days=365 * 10)


_JURISDICTION_SOL = {
    "US": _us_deadline,
    "UK": _uk_deadline,
    "GB": _uk_deadline,
    "GERMANY": _de_deadline,
    "DE": _de_deadline,
    "FRANCE": _fr_deadline,
    "FR": _fr_deadline,
    "JAPAN": _jp_deadline,
    "JP": _jp_deadline,
}


class DiscoveryRuleEngine:
    def __init__(self, db: Session | None = None) -> None:
        self.db = db

    def _pick_discovery_date(
        self, anomaly_like: dict[str, Any]
    ) -> tuple[datetime | None, list[dict[str, Any]]]:
        timeline: list[dict[str, Any]] = []
        first_dt: datetime | None = None
        first_key = None
        for trigger in _TRIGGER_PRIORITY:
            dt = _to_utc(anomaly_like.get(trigger.key))
            evidence = anomaly_like.get(f"{trigger.key}_evidence")
            row = {
                "trigger_key": trigger.key,
                "label": trigger.label,
                "date": dt.isoformat() if dt else None,
                "source_evidence": evidence,
                "evidence_hash": _hash_payload(
                    {
                        "key": trigger.key,
                        "date": dt.isoformat() if dt else None,
                        "evidence": evidence,
                    }
                ),
            }
            timeline.append(row)
            if first_dt is None and dt is not None:
                first_dt = dt
                first_key = trigger.key

        if first_dt is None:
            fallback = _to_utc(anomaly_like.get("created_at")) or datetime.now(timezone.utc)
            timeline.append(
                {
                    "trigger_key": "fallback_created_at",
                    "label": "Fallback created_at discovery",
                    "date": fallback.isoformat(),
                    "source_evidence": "system fallback",
                    "evidence_hash": _hash_payload(
                        {"key": "fallback_created_at", "date": fallback.isoformat()}
                    ),
                }
            )
            first_dt = fallback
            first_key = "fallback_created_at"

        timeline.append(
            {
                "trigger_key": "selected_discovery_trigger",
                "label": "Selected discovery trigger",
                "date": first_dt.isoformat(),
                "source_evidence": first_key,
                "evidence_hash": _hash_payload(
                    {"selected": first_key, "date": first_dt.isoformat()}
                ),
            }
        )
        return first_dt, timeline

    def _deadline_for_jurisdiction(self, jurisdiction: str, discovery_date: datetime) -> datetime:
        key = str(jurisdiction or "US").strip().upper()
        fn = _JURISDICTION_SOL.get(key, _us_deadline)
        return fn(discovery_date)

    def generate_discovery_memo(
        self, anomaly_like: dict[str, Any], analysis: dict[str, Any]
    ) -> dict[str, Any]:
        checklist = {
            "facts_section_present": bool(anomaly_like.get("description")),
            "timeline_section_present": bool(analysis.get("discovery_timeline")),
            "jurisdiction_section_present": bool(analysis.get("jurisdiction")),
            "sol_section_present": bool(analysis.get("statute_of_limitations_deadline")),
            "evidence_hashes_present": bool((analysis.get("discovery_timeline") or [])),
            "attorney_review_required": True,
        }
        memo = {
            "title": "Discovery Rule Memorandum Draft",
            "prepared_at": datetime.now(timezone.utc).isoformat(),
            "anomaly_id": anomaly_like.get("id"),
            "jurisdiction": analysis.get("jurisdiction"),
            "discovery_date": analysis.get("discovery_date"),
            "sol_deadline": analysis.get("statute_of_limitations_deadline"),
            "urgent_flag": analysis.get("urgent_flag"),
            "facts": {
                "subtype": anomaly_like.get("subtype"),
                "description": anomaly_like.get("description"),
                "estimated_recoverable": anomaly_like.get("estimated_recoverable"),
            },
            "analysis": {
                "trigger_priority_applied": [t.key for t in _TRIGGER_PRIORITY],
                "discovery_timeline": analysis.get("discovery_timeline"),
                "legal_rationale": "Discovery date selected from highest-priority available trigger with hash-verifiable evidence references.",
            },
            "attorney_review_checklist": checklist,
            "status": "draft_for_attorney_review",
        }
        memo["memo_hash"] = _hash_payload(memo)
        return memo

    def evaluate(
        self, anomaly_like: dict[str, Any], *, as_of: datetime | None = None
    ) -> dict[str, Any]:
        now = as_of or datetime.now(timezone.utc)
        discovery_date, timeline = self._pick_discovery_date(anomaly_like)
        jurisdiction = str(
            anomaly_like.get("jurisdiction") or anomaly_like.get("territory") or "US"
        ).upper()
        deadline = self._deadline_for_jurisdiction(jurisdiction, discovery_date)
        days_remaining = int((deadline - now).total_seconds() // 86400)
        urgent_flag = days_remaining <= 90

        analysis = {
            "anomaly_id": anomaly_like.get("id"),
            "jurisdiction": jurisdiction,
            "discovery_date": discovery_date.isoformat(),
            "discovery_timeline": timeline,
            "statute_of_limitations_deadline": deadline.isoformat(),
            "days_remaining": max(days_remaining, 0),
            "urgent_flag": bool(urgent_flag),
        }
        analysis["discovery_memo"] = self.generate_discovery_memo(anomaly_like, analysis)

        if self.db is not None and anomaly_like.get("artist_id"):
            ImmutableLedgerService(self.db).append(
                str(anomaly_like.get("artist_id")),
                "discovery_rule_analysis",
                {
                    "anomaly_id": anomaly_like.get("id"),
                    "analysis_hash": _hash_payload(analysis),
                    "deadline": analysis["statute_of_limitations_deadline"],
                    "urgent_flag": analysis["urgent_flag"],
                },
            )

        return analysis
