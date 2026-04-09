from __future__ import annotations

import importlib
import json
import os
from datetime import datetime, timezone
from typing import Any

import networkx as nx

from XR7.ml.catalog_scorer import CatalogScorer
from XR7.models.anomaly import Anomaly
from XR7.models.catalog_graph import CatalogGraphSnapshot
from XR7.models.claim import Claim
from XR7.models.payment import Payment
from XR7.models.work import Work
from xr7_common.logging import get_logger

try:
    _lc_messages = importlib.import_module("langchain_core.messages")
    HumanMessage = getattr(_lc_messages, "HumanMessage")
    SystemMessage = getattr(_lc_messages, "SystemMessage")
except Exception:  # pragma: no cover - optional dependency
    HumanMessage = None
    SystemMessage = None

try:
    _lc_openai = importlib.import_module("langchain_openai")
    ChatOpenAI = getattr(_lc_openai, "ChatOpenAI")
except Exception:  # pragma: no cover - optional dependency
    ChatOpenAI = None


logger = get_logger(__name__)


class CatalogAuditor:
    """Catalog audit engine for metadata, split, and payout integrity checks."""

    def __init__(self, db_session):
        self.db = db_session
        self.scorer = CatalogScorer()

    def _load_catalog_graph(self, artist_id: str) -> nx.DiGraph:
        graph = nx.DiGraph()
        snapshot = (
            self.db.query(CatalogGraphSnapshot)
            .filter(CatalogGraphSnapshot.artist_id == artist_id)
            .order_by(CatalogGraphSnapshot.created_at.desc())
            .first()
        )
        if not snapshot:
            return graph

        try:
            nodes = json.loads(snapshot.nodes_json or "[]")
            edges = json.loads(snapshot.edges_json or "[]")
        except json.JSONDecodeError:
            logger.exception("Catalog graph snapshot JSON decode failed")
            return graph

        for node in nodes:
            node_id = str(node.get("id") or "")
            if node_id:
                graph.add_node(
                    node_id, **(node.get("attributes") or {}), node_type=node.get("node_type")
                )

        for edge in edges:
            src = str(edge.get("source_id") or "")
            dst = str(edge.get("target_id") or "")
            if src and dst:
                graph.add_edge(
                    src, dst, **(edge.get("attributes") or {}), edge_type=edge.get("edge_type")
                )

        return graph

    async def _llm_issue_summary(self, issues: list[dict[str, Any]]) -> str | None:
        if not issues or ChatOpenAI is None or HumanMessage is None or SystemMessage is None:
            return None

        key = os.environ.get("LLM_API_KEY", "")
        if not key:
            return None

        model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
        llm = ChatOpenAI(model=model, api_key=key, temperature=0.1)

        prompt = json.dumps(issues[:20], indent=2, sort_keys=True)
        try:
            out = await llm.ainvoke(
                [
                    SystemMessage(
                        content=(
                            "You are XR7 catalog audit assistant. "
                            "Summarize issue concentration and priority in <=120 words."
                        )
                    ),
                    HumanMessage(content=f"Issues:\n{prompt}"),
                ]
            )
            return str(getattr(out, "content", "") or "").strip() or None
        except Exception:
            logger.exception("Catalog audit LLM summary failed")
            return None

    async def scan_catalog(self, artist_id: str) -> list[dict[str, Any]]:
        """Scan catalog and return structured issue rows."""
        works = self.db.query(Work).filter(Work.artist_id == artist_id).all()
        claims = self.db.query(Claim).filter(Claim.artist_id == artist_id).all()
        anomalies = self.db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()

        graph = self._load_catalog_graph(artist_id)
        issues: list[dict[str, Any]] = []

        for work in works:
            if not work.isrc:
                issues.append(
                    {
                        "issue_type": "missing_isrc",
                        "severity": "high",
                        "work_id": work.id,
                        "title": work.title,
                        "detail": "Work is missing ISRC metadata.",
                    }
                )

        for anomaly in anomalies:
            if str(anomaly.subtype).lower() == "split_conflict":
                issues.append(
                    {
                        "issue_type": "split_conflict",
                        "severity": "high",
                        "reference_id": anomaly.id,
                        "detail": anomaly.description,
                    }
                )

        # Rate drift heuristic: compare average expected vs received from claim evidence proof totals.
        for claim in claims:
            evidence = claim.evidence or {}
            totals = (evidence.get("proof") or {}).get("totals") or {}
            expected = float(totals.get("total_expected_amount") or 0.0)
            received = float(totals.get("total_received_amount") or 0.0)
            if expected <= 0:
                continue
            drift = abs(expected - received) / expected
            if drift >= 0.15:
                issues.append(
                    {
                        "issue_type": "rate_drift",
                        "severity": "medium" if drift < 0.3 else "high",
                        "claim_id": claim.id,
                        "detail": f"Expected/received drift is {drift:.2%}",
                        "drift_ratio": round(drift, 4),
                    }
                )

        # AI-generation risk flag heuristic from graph metadata.
        for node_id, attrs in graph.nodes(data=True):
            title = str(attrs.get("title") or attrs.get("name") or "")
            tags = str(attrs.get("tags") or "").lower()
            if "ai" in title.lower() or "synthetic" in tags:
                issues.append(
                    {
                        "issue_type": "ai_generation_risk",
                        "severity": "medium",
                        "node_id": node_id,
                        "detail": "Potential AI-generated asset detected; verify ownership and rights chain.",
                    }
                )

        llm_summary = await self._llm_issue_summary(issues)
        if llm_summary:
            issues.append(
                {
                    "issue_type": "audit_summary",
                    "severity": "info",
                    "detail": llm_summary,
                }
            )

        return issues

    async def auto_suggest_fixes(self, issues: list[dict[str, Any]]) -> dict[str, Any]:
        """Return fix suggestions grouped by issue type."""
        suggestions: dict[str, list[str]] = {}
        for issue in issues:
            issue_type = str(issue.get("issue_type") or "unknown")
            if issue_type == "missing_isrc":
                suggestions.setdefault(issue_type, []).append(
                    "Add ISRC via MusicBrainz lookup and distributor metadata sync."
                )
            elif issue_type == "split_conflict":
                suggestions.setdefault(issue_type, []).append(
                    "Reconcile contract split terms and update writer/publisher shares in source systems."
                )
            elif issue_type == "rate_drift":
                suggestions.setdefault(issue_type, []).append(
                    "Run historical rate benchmark and request statement-level true-up from payer."
                )
            elif issue_type == "ai_generation_risk":
                suggestions.setdefault(issue_type, []).append(
                    "Collect provenance docs and register explicit AI-rights clauses in contract metadata."
                )

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "suggestions": suggestions,
        }

    async def run(self, artist_id: str) -> dict[str, Any]:
        """Run full catalog audit and return catalog_health-compatible payload."""
        works = self.db.query(Work).filter(Work.artist_id == artist_id).all()
        anomalies = self.db.query(Anomaly).filter(Anomaly.artist_id == artist_id).all()
        claims = self.db.query(Claim).filter(Claim.artist_id == artist_id).all()
        payments = self.db.query(Payment).filter(Payment.artist_id == artist_id).all()

        earnings_summary = {
            "total_expected": sum(
                float(
                    (c.evidence or {})
                    .get("proof", {})
                    .get("totals", {})
                    .get("total_expected_amount")
                    or 0.0
                )
                for c in claims
            ),
            "total_received": sum(
                float(
                    (c.evidence or {})
                    .get("proof", {})
                    .get("totals", {})
                    .get("total_received_amount")
                    or 0.0
                )
                for c in claims
            ),
        }

        report = self.scorer.score(
            artist_id=artist_id,
            works=[{"isrc": w.isrc, "iswc": w.iswc} for w in works],
            payments=[{"amount": p.amount} for p in payments],
            anomalies=[{"status": str(a.status)} for a in anomalies],
            claims=[{"status": str(c.status)} for c in claims],
            earnings_summary=earnings_summary,
        )

        issues = await self.scan_catalog(artist_id)
        fixes = await self.auto_suggest_fixes(issues)

        return {
            "artist_id": artist_id,
            "catalog_health": report.to_dict(),
            "signals": report.signals,
            "issues": issues,
            "fixes": fixes,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }


class AutomatedRegistrationFixer:
    """Detect and apply metadata/registration fixes with downloadable package outputs."""

    def __init__(self, db_session):
        self.db = db_session

    def detect_missing_metadata(self, artist_id: str) -> list[dict[str, Any]]:
        works = self.db.query(Work).filter(Work.artist_id == artist_id).all()
        issues: list[dict[str, Any]] = []
        for w in works:
            if not w.isrc:
                issues.append(
                    {
                        "type": "missing_isrc",
                        "work_id": w.id,
                        "title": w.title,
                        "suggested_source": "MusicBrainz",
                    }
                )
            if not w.iswc:
                issues.append(
                    {
                        "type": "missing_iswc",
                        "work_id": w.id,
                        "title": w.title,
                        "suggested_source": "PRO portal",
                    }
                )
        if not works:
            issues.append({"type": "catalog_empty", "detail": "No works registered for artist"})
        return issues

    def auto_suggest_and_apply_fixes(
        self, artist_id: str, issues: list[dict[str, Any]]
    ) -> dict[str, Any]:
        rows = []
        instructions = []
        for issue in issues:
            issue_type = str(issue.get("type") or "unknown")
            if issue_type == "missing_isrc":
                rows.append(
                    {
                        "work_id": issue.get("work_id"),
                        "action": "populate_isrc",
                        "source": "musicbrainz_lookup",
                    }
                )
                instructions.append(
                    "Upload generated ISRC CSV to DistroKid/label portal and re-sync catalog."
                )
            elif issue_type == "missing_iswc":
                rows.append(
                    {
                        "work_id": issue.get("work_id"),
                        "action": "submit_pro_registration",
                        "source": "pro_simulation",
                    }
                )
                instructions.append(
                    "Submit generated PRO registration payload in your PRO dashboard."
                )
            else:
                rows.append(
                    {"work_id": issue.get("work_id"), "action": "manual_review", "source": "system"}
                )

        package = {
            "artist_instructions": list(dict.fromkeys(instructions)) or ["No fixes required."],
            "fix_csv_rows": rows,
            "downloadable_fix_package": {
                "filename": f"registration_fixes_{artist_id}.csv",
                "row_count": len(rows),
            },
            "pro_submission_simulation": {
                "submitted": sum(1 for r in rows if r.get("action") == "submit_pro_registration"),
                "status": "simulated",
            },
        }
        return package

    def run_preventive_audit(self, artist_id: str) -> dict[str, Any]:
        issues = self.detect_missing_metadata(artist_id)
        fixes = self.auto_suggest_and_apply_fixes(artist_id, issues)
        audit = CatalogAuditor(self.db)
        report = __import__("asyncio").run(audit.run(artist_id))
        return {
            "artist_id": artist_id,
            "issues": issues,
            "fixes": fixes,
            "updated_catalog_health_score": (report.get("catalog_health") or {}).get(
                "health_score"
            ),
            "catalog_health": report.get("catalog_health"),
        }
