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

    async def _build_llm(self):
        if not self.api_key:
            raise RuntimeError("LLM_API_KEY is not configured")

        if self.provider in {"xai", "xai-grok", "grok"} and ChatXAI is not None:
            return ChatXAI(model=os.environ.get("LLM_MODEL", "grok-beta"), api_key=self.api_key, temperature=0.2)

        if ChatOpenAI is None:
            raise RuntimeError("langchain_openai is not installed")

        return ChatOpenAI(model=self.model, api_key=self.api_key, temperature=0.2)

    async def _invoke(self, *, system_prompt: str, user_prompt: str, rate_key: str) -> str:
        self._rate_limiter.check(rate_key)

        if HumanMessage is None or SystemMessage is None:
            raise RuntimeError("langchain_core is not installed")

        llm = await self._build_llm()
        result = await llm.ainvoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
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
                ((claim.evidence or {}).get("legal_support", {}).get("contract_basis", [{}])[0].get("counterparty"))
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

    async def async_generate_demand_letter(self, anomaly: dict, evidence: dict, artist_id: str) -> str:
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
                    evidence=claim.get("evidence") if isinstance(claim.get("evidence"), dict) else {},
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
