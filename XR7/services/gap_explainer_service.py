"""LLM-backed gap explainability service for reconciliation anomalies.

Generates plain-language, evidence-grounded explanations of why royalty gaps
exist between expected and reported amounts, with structured output including
summary, top drivers, confidence, and recommended next actions.
"""

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
from sqlalchemy.orm import Session

from XR7.models.anomaly import AnomalySchema
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


class GapExplainerEvidenceSchema(BaseModel):
    """Structured evidence payload for gap explanation."""

    model_config = ConfigDict(extra="allow")

    anomaly_id: str
    category: str
    subtype: str
    expected_amount: float | None = None
    actual_amount: float | None = None
    gap_amount: float | None = None
    gap_pct: float | None = None
    territory: str | None = None
    time_window_start: str | None = None
    time_window_end: str | None = None
    confidence_score: float | None = None
    description: str | None = None


class GapExplanationOutput(BaseModel):
    """Structured output for gap explanation."""

    anomaly_id: str
    summary: str
    top_drivers: list[str]
    confidence: float
    recommended_actions: list[str]
    evidence_references: list[str]
    model_version: str
    generated_at: str


@dataclass(slots=True)
class _RateWindow:
    timestamps: deque[float]


class _SimpleRateLimiter:
    """In-memory fixed-window limiter for LLM calls."""

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


class GapExplainerService:
    """LLM-backed gap explainability service with fallback templates."""

    def __init__(self, provider: str | None = None, model: str | None = None, db: Session | None = None):
        self.provider = (provider or os.environ.get("LLM_PROVIDER", "openai")).strip().lower()
        self.model = model or os.environ.get("LLM_MODEL", "gpt-4o-mini")
        self.api_key = os.environ.get("LLM_API_KEY", "")
        self.db = db
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
    def _system_prompt() -> str:
        return (
            "You are XR7 Recovery Intelligence Explainability Assistant. "
            "Generate clear, concise, evidence-grounded explanations of royalty gaps. "
            "Focus on: (1) what caused the gap, (2) when it occurred, (3) confidence level, "
            "(4) how to verify it, and (5) recommended next steps. "
            "Always cite evidence sources and acknowledge limitations in available data. "
            "Be direct and avoid speculation."
        )

    @staticmethod
    def _fallback_explanation(anomaly: dict[str, Any]) -> dict[str, Any]:
        """Fallback explanation when LLM is unavailable."""
        category = anomaly.get("category", "UNKNOWN")
        subtype = anomaly.get("subtype", "unknown")
        expected = anomaly.get("expected_amount")
        actual = anomaly.get("actual_amount")
        confidence = float(anomaly.get("confidence_score") or 0.5)
        territory = anomaly.get("territory") or "unspecified"

        gap_desc = "The reported royalty amount differs from expected."
        if expected is not None and actual is not None:
            gap_amount = max(0, expected - actual)
            if gap_amount > 0:
                gap_desc = f"Royalty payment of {actual} appears {gap_amount} short of expected {expected}"

        return {
            "anomaly_id": anomaly.get("id", "unknown"),
            "summary": gap_desc,
            "top_drivers": [
                f"Anomaly category: {category}",
                f"Anomaly subtype: {subtype}",
                f"Territory: {territory}",
                "Possible causes: underreporting, platform blackbox, rate variance, or unmatched metadata",
            ],
            "confidence": round(confidence, 3),
            "recommended_actions": [
                "Review original reporting period statement",
                "Check if all platforms properly configured for territory",
                "Verify artist identity graph completeness",
                "Escalate to attorney if gap exceeds policy threshold",
            ],
            "evidence_references": [
                f"anomaly:{anomaly.get('id', 'unknown')}",
            ],
            "model_version": "fallback-v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def explain_gap(self, anomaly: dict[str, Any], evidence: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate natural-language gap explanation with evidence citations.

        Args:
            anomaly: Anomaly payload with expected_amount, actual_amount, confidence_score, etc.
            evidence: Optional detailed evidence packet (statements, proof, integrity checks)

        Returns:
            Structured explanation output with summary, drivers, confidence, and actions.
        """
        try:
            evidence_payload = GapExplainerEvidenceSchema(
                anomaly_id=anomaly.get("id") or "unknown",
                category=anomaly.get("category") or "UNKNOWN",
                subtype=anomaly.get("subtype") or "unknown",
                expected_amount=anomaly.get("expected_amount"),
                actual_amount=anomaly.get("actual_amount"),
                gap_amount=max(0, float(anomaly.get("expected_amount") or 0) - float(anomaly.get("actual_amount") or 0)),
                gap_pct=(
                    (max(0, float(anomaly.get("expected_amount") or 0) - float(anomaly.get("actual_amount") or 0)))
                    / max(float(anomaly.get("expected_amount") or 0.01), 0.01)
                ),
                territory=anomaly.get("territory"),
                time_window_start=anomaly.get("time_window_start"),
                time_window_end=anomaly.get("time_window_end"),
                confidence_score=anomaly.get("confidence_score"),
                description=anomaly.get("description"),
            )
        except ValidationError:
            logger.exception("Gap explanation payload validation failed; using fallback")
            return self._fallback_explanation(anomaly)

        system_prompt = self._system_prompt()
        user_prompt = (
            "Explain the following royalty gap in clear, evidence-grounded terms. "
            "Output a JSON object with: summary (1-2 sentences), top_drivers (array), confidence (0-1), "
            "recommended_actions (array), evidence_references (array).\n\n"
            f"Anomaly data:\n{json.dumps(evidence_payload.model_dump(exclude_none=True), indent=2)}\n\n"
        )
        if evidence:
            user_prompt += f"Additional evidence packet:\n{json.dumps(evidence, indent=2, default=str)}\n\n"

        user_prompt += "Output strictly valid JSON only, no markdown fencing."

        try:
            llm_response = await self._invoke(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                rate_key=f"gap_explain:{evidence_payload.anomaly_id}",
            )
            parsed = json.loads(llm_response)
            parsed.setdefault("anomaly_id", evidence_payload.anomaly_id)
            parsed.setdefault("model_version", self.model)
            parsed.setdefault("generated_at", datetime.now(timezone.utc).isoformat())
            return parsed
        except (ValueError, json.JSONDecodeError) as e:
            logger.warning(f"LLM response parsing failed: {e}; using fallback")
            return self._fallback_explanation(anomaly)

    def explain_gap_sync(self, anomaly: dict[str, Any], evidence: dict[str, Any] | None = None) -> dict[str, Any]:
        """Synchronous wrapper for explain_gap using asyncio.run (blocking)."""
        try:
            return asyncio.run(self.explain_gap(anomaly, evidence))
        except Exception as e:
            logger.exception(f"Gap explanation failed: {e}")
            return self._fallback_explanation(anomaly)
