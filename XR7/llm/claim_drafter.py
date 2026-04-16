from __future__ import annotations

import asyncio
import importlib
import json
import os
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from XR7.models.anomaly import AnomalySchema
from XR7.models.claim import ClaimSchema
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

try:
    _lc_xai = importlib.import_module("langchain_xai")
    ChatXAI = getattr(_lc_xai, "ChatXAI")
except Exception:  # pragma: no cover - optional dependency
    ChatXAI = None


logger = get_logger(__name__)


class EvidencePacketSchema(BaseModel):
    """Structured evidence packet payload used by LLM prompt construction."""

    model_config = ConfigDict(extra="allow")

    claim_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    anomaly: dict[str, Any] = Field(default_factory=dict)
    proof: dict[str, Any] = Field(default_factory=dict)
    reconciliation: dict[str, Any] = Field(default_factory=dict)
    legal_support: dict[str, Any] = Field(default_factory=dict)
    integrity: dict[str, Any] = Field(default_factory=dict)


class ClaimDraftInput(BaseModel):
    """Validated claim draft payload for demand-letter generation."""

    anomaly: AnomalySchema
    evidence: EvidencePacketSchema
    artist_id: str


class NegotiationInput(BaseModel):
    """Validated claim payload for negotiation strategy generation."""

    claim: ClaimSchema


@dataclass(slots=True)
class _RateWindow:
    timestamps: deque[float]


class _SimpleRateLimiter:
    """In-memory fixed-window limiter for LLM calls.

    This is intentionally lightweight and process-local to avoid introducing
    additional infrastructure dependencies inside core business logic.
    """

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._windows: dict[str, _RateWindow] = {}
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = time.time()
        cutoff = now - self.window_seconds
        with self._lock:
            window = self._windows.setdefault(key, _RateWindow(timestamps=deque()))
            while window.timestamps and window.timestamps[0] < cutoff:
                window.timestamps.popleft()
            if len(window.timestamps) >= self.max_requests:
                raise RuntimeError(
                    f"LLM rate limit exceeded for key={key}; "
                    f"allowed={self.max_requests}/{self.window_seconds}s"
                )
            window.timestamps.append(now)


class ClaimDrafter:
    """LLM-backed claim drafting service with fallback templates."""

    def __init__(self, provider: str | None = None, model: str | None = None):
        self.provider = (provider or os.environ.get("LLM_PROVIDER", "openai")).strip().lower()
        self.model = model or os.environ.get("LLM_MODEL", "gpt-4o-mini")
        self.api_key = os.environ.get("LLM_API_KEY", "")
        self._rate_limiter = _SimpleRateLimiter(max_requests=40, window_seconds=60)
        self._is_available = bool(self.api_key)

        if not self._is_available:
            logger.warning(
                "ClaimDrafter: LLM API key not configured - will use fallback templates",
                extra={"provider": self.provider, "model": self.model}
            )

    @property
    def is_available(self) -> bool:
        """Check if LLM provider is available and configured."""
        return self._is_available

    async def _build_llm(self):
        if not self.api_key:
            raise RuntimeError("LLM_API_KEY is not configured")

        if self.provider in {"xai", "xai-grok", "grok"} and ChatXAI is not None:
            return ChatXAI(
                model=os.environ.get("LLM_MODEL", "grok-beta"),
                api_key=self.api_key,
                temperature=0.2,
            )

        if ChatOpenAI is None:
            raise RuntimeError("langchain_openai is not installed")

        return ChatOpenAI(model=self.model, api_key=self.api_key, temperature=0.2)

    async def _invoke(self, *, system_prompt: str, user_prompt: str, rate_key: str) -> str:
        self._rate_limiter.check(rate_key)

        if HumanMessage is None or SystemMessage is None:
            raise RuntimeError("langchain_core is not installed")

        llm = await self._build_llm()
        result = await llm.ainvoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        )
        content = getattr(result, "content", "")
        if isinstance(content, list):
            return "\n".join(str(c) for c in content)
        return str(content or "")

    @staticmethod
    def _system_prompt(context: str) -> str:
        return (
            "You are XR7 Recovery Intelligence Counsel Assistant. "
            "Produce concise, professional, legally cautious output that can be reviewed by counsel. "
            "Always reference: (1) XR7 universal royalty event schema fields for provenance, "
            "(2) calibration health confidence ranges when making probability claims, and "
            "(3) evidence integrity checks including packet_hash, prior_packet_hash, chain_hash, and signature status. "
            "Never invent factual amounts; use placeholders if not present. "
            f"Task context: {context}."
        )

    @staticmethod
    def _fallback_demand_letter(payload: ClaimDraftInput) -> str:
        evidence = payload.evidence
        anomaly = payload.anomaly
        packet_hash = (evidence.integrity or {}).get("packet_hash", "[PACKET_HASH]")
        category = str(anomaly.category)
        return (
            f"# Demand Letter Draft\n\n"
            f"Date: {datetime.now(timezone.utc).date().isoformat()}\n"
            f"Artist ID: {payload.artist_id}\n"
            f"Claim Category: {category}\n"
            f"Amount in Dispute: [AMOUNT_PLACEHOLDER]\n"
            f"SOL Status: [SOL_STATUS_PLACEHOLDER]\n"
            f"Evidence Hash Link: {packet_hash}\n\n"
            "To Whom It May Concern,\n\n"
            "We represent the above-referenced artist regarding underreported or underpaid royalties. "
            "Preliminary analysis under the XR7 universal royalty event model indicates a material variance "
            "between expected and received amounts in the reporting period at issue.\n\n"
            "Please preserve all relevant books and records and provide a full reconciliation within 14 days. "
            "Failing that, we will pursue all available contractual and statutory remedies.\n\n"
            "Sincerely,\n"
            "XR7 Recovery Operations\n"
        )

    @staticmethod
    def _fallback_negotiation_script(claim: ClaimSchema) -> dict[str, Any]:
        payer = "generic"
        if isinstance(claim.evidence, dict):
            payer = str(
                (
                    (claim.evidence or {})
                    .get("legal_support", {})
                    .get("contract_basis", [{}])[0]
                    .get("counterparty")
                )
                or "generic"
            ).lower()

        return {
            "claim_id": claim.id,
            "payer": payer,
            "strategy": {
                "anchor": "Start at 100% of modeled shortfall with documented evidence packet.",
                "floor": "Do not settle below [SETTLEMENT_FLOOR_PLACEHOLDER] without counsel review.",
                "concessions": [
                    "Offer staged payment schedule tied to audit completion.",
                    "Trade timeline flexibility for accelerated first payment.",
                ],
            },
            "counter_offer_playbook": [
                {
                    "if_payer_says": "Data is incomplete",
                    "respond": "Provide packet hash, source citations, and reconciliation worksheet; request specific disputed rows.",
                },
                {
                    "if_payer_says": "SOL expired",
                    "respond": "Request tolling analysis and confirm accrual date assumptions before conceding time bar.",
                },
            ],
        }

    @staticmethod
    def _fallback_advice(dashboard: dict[str, Any]) -> str:
        catalog_health = (dashboard.get("catalog_health") or {}).get("health_score")
        return (
            "Based on your current dashboard, focus first on high-confidence recovery actions and deadlines. "
            f"Your catalog health score is {catalog_health if catalog_health is not None else '[UNKNOWN]'}. "
            "Prioritize missing metadata cleanup (ISRC/ISWC), then escalate claims with evidence discrepancy flags."
        )

    async def async_generate_demand_letter(
        self, anomaly: dict, evidence: dict, artist_id: str
    ) -> str:
        """Generate professional demand-letter markdown from anomaly + evidence payloads."""
        try:
            payload = ClaimDraftInput(
                anomaly=AnomalySchema.model_validate(anomaly),
                evidence=EvidencePacketSchema.model_validate(evidence),
                artist_id=artist_id,
            )
        except ValidationError:
            logger.exception("Demand letter payload validation failed")
            fallback_payload = ClaimDraftInput.model_construct(
                anomaly=AnomalySchema.model_construct(
                    id=str(anomaly.get("id") or "unknown-anomaly"),
                    artist_id=str(anomaly.get("artist_id") or artist_id),
                    category=anomaly.get("category") or "ROYALTY",
                    subtype=str(anomaly.get("subtype") or "unknown"),
                    severity=anomaly.get("severity") or "MEDIUM",
                    confidence_score=float(anomaly.get("confidence_score") or 0.0),
                    status=anomaly.get("status") or "OPEN",
                    created_at=datetime.now(timezone.utc),
                ),
                evidence=EvidencePacketSchema.model_validate(evidence or {}),
                artist_id=artist_id,
            )
            return self._fallback_demand_letter(fallback_payload)

        system_prompt = self._system_prompt("Generate demand letter")
        user_prompt = json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True)

        try:
            return await self._invoke(
                system_prompt=system_prompt,
                user_prompt=(
                    "Create a full professional demand letter in markdown. "
                    "Include explicit placeholders for amount, category, SOL status, and evidence hash link.\n\n"
                    f"Input:\n{user_prompt}"
                ),
                rate_key=f"demand:{artist_id}",
            )
        except Exception:
            logger.exception("Demand letter generation failed; using fallback template")
            return self._fallback_demand_letter(payload)

    async def async_generate_negotiation_script(self, claim: dict) -> dict[str, Any]:
        """Generate payer-playbook-aware counter-offer strategy."""
        try:
            payload = NegotiationInput(claim=ClaimSchema.model_validate(claim))
        except ValidationError:
            logger.exception("Negotiation payload validation failed")
            return self._fallback_negotiation_script(
                ClaimSchema.model_construct(
                    id=str(claim.get("id") or "unknown-claim"),
                    artist_id=str(claim.get("artist_id") or "unknown-artist"),
                    anomaly_id=str(claim.get("anomaly_id") or "unknown-anomaly"),
                    claim_type=str(claim.get("claim_type") or "royalty"),
                    status=claim.get("status") or "IDENTIFIED",
                    currency=str(claim.get("currency") or "USD"),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    evidence=(
                        claim.get("evidence") if isinstance(claim.get("evidence"), dict) else {}
                    ),
                )
            )

        system_prompt = self._system_prompt("Generate negotiation script")
        user_prompt = json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True)

        try:
            raw = await self._invoke(
                system_prompt=system_prompt,
                user_prompt=(
                    "Return JSON only. Build payer-specific counter-offer strategies with escalation steps.\n\n"
                    f"Input:\n{user_prompt}"
                ),
                rate_key=f"negotiate:{payload.claim.artist_id}",
            )
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            logger.exception("Negotiation script generation failed; using fallback")

        return self._fallback_negotiation_script(payload.claim)

    async def async_generate_personalized_advice(self, artist_dashboard: dict) -> str:
        """Generate chatbot-style personalized advice from dashboard context."""
        system_prompt = self._system_prompt("Generate personalized advice")
        user_prompt = json.dumps(artist_dashboard, indent=2, sort_keys=True)

        try:
            return await self._invoke(
                system_prompt=system_prompt,
                user_prompt=(
                    "Respond as a recovery coach in 1-3 short paragraphs, actionable and empathetic. "
                    "Reference catalog_health, deadlines, and evidence integrity if present.\n\n"
                    f"Input:\n{user_prompt}"
                ),
                rate_key="advice:global",
            )
        except Exception:
            logger.exception("Personalized advice generation failed; using fallback")
            return self._fallback_advice(artist_dashboard)

    @staticmethod
    def _run_sync(coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        if loop.is_running():
            raise RuntimeError("Cannot call sync LLM method from running event loop")
        return asyncio.run(coro)

    def generate_demand_letter(self, anomaly: dict, evidence: dict, artist_id: str) -> str:
        """Synchronous wrapper for demand-letter generation."""
        return self._run_sync(self.async_generate_demand_letter(anomaly, evidence, artist_id))

    def generate_negotiation_script(self, claim: dict) -> dict[str, Any]:
        """Synchronous wrapper for negotiation-script generation."""
        return self._run_sync(self.async_generate_negotiation_script(claim))

    def generate_personalized_advice(self, artist_dashboard: dict) -> str:
        """Synchronous wrapper for personalized advice generation."""
        return self._run_sync(self.async_generate_personalized_advice(artist_dashboard))


claim_drafter = ClaimDrafter()


class AILicensingAdvisor:
    """Advises on AI licensing strategy and agreement drafting."""

    def __init__(self):
        self.drafter = claim_drafter

    async def analyze_opt_in_value(self, artist_catalog: dict) -> dict[str, Any]:
        baseline = float((artist_catalog.get("earnings") or {}).get("trailing_12m") or 0.0)
        projected = round(baseline * 0.12, 2)
        prompt_context = {
            "trend_year": 2026,
            "models": [
                "influence-based licensing",
                "tiered royalty floors",
                "synthetic voice safeguards",
            ],
            "catalog": artist_catalog,
        }
        guidance = await self.drafter.async_generate_personalized_advice(prompt_context)
        return {
            "recommendation": "OPT_IN_GUARDED" if projected > 0 else "HOLD",
            "estimated_new_revenue": projected,
            "pros": ["New AI training/licensing revenue stream", "Negotiated usage controls"],
            "cons": ["Model leakage risk", "Potential brand dilution without strict controls"],
            "advisor_note": guidance,
        }

    async def draft_ai_license_agreement(self, artist_id: str, terms: dict) -> str:
        context = {
            "artist_id": artist_id,
            "terms": terms,
            "trends_2026": ["influence-based", "tiered royalties", "right-to-audit model outputs"],
            "include_blockchain_anchor_option": True,
        }
        base = await self.drafter.async_generate_personalized_advice(context)
        return (
            "# AI License Agreement Draft\n\n"
            f"Artist: {artist_id}\n"
            "## Core Terms\n"
            "- Usage-based royalties with tiered rates by model usage volume\n"
            "- Influence attribution and audit rights\n"
            "- Optional blockchain anchor for settlement records\n\n"
            "## Counsel Summary\n"
            f"{base}\n"
        )

    async def track_ai_royalty_payments(self, artist_id: str) -> dict[str, Any]:
        return {
            "artist_id": artist_id,
            "period": "monthly",
            "partner_rows": [
                {"partner": "ModelHub-A", "gross": 1200.0, "net": 980.0},
                {"partner": "ModelHub-B", "gross": 860.0, "net": 710.0},
            ],
            "status": "reconciled_simulated",
        }


class RoyaltyChatAgent:
    """Artist-facing chat agent for royalty Q&A with evidence-citation style responses."""

    def __init__(self):
        self.drafter = claim_drafter
        self._history: dict[str, list[dict[str, str]]] = {}

    async def handle_query(
        self, artist_id: str, question: str, context: dict | None = None
    ) -> dict[str, Any]:
        history = self._history.setdefault(artist_id, [])
        history.append({"role": "user", "content": question})
        response = await self.drafter.async_generate_personalized_advice(
            {
                "artist_id": artist_id,
                "question": question,
                "context": context or {},
                "instruction": "Always cite source fields and evidence hashes when available.",
            }
        )
        history.append({"role": "assistant", "content": response})
        self._history[artist_id] = history[-20:]
        return {
            "artist_id": artist_id,
            "response": response,
            "conversation_history": self._history[artist_id],
            "citations": [
                {"source": "dashboard", "evidence_hash": (context or {}).get("evidence_hash")}
            ],
        }


ai_licensing_advisor = AILicensingAdvisor()
royalty_chat_agent = RoyaltyChatAgent()
