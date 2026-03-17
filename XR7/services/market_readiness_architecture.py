from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from xr7_common.settings import settings


@dataclass
class GateResult:
    name: str
    passed: bool
    detail: str


def evaluate_architecture_readiness(*, environment: str) -> dict[str, Any]:
    env = (environment or "development").strip().lower()

    gates: list[GateResult] = [
        GateResult(
            name="database_configured",
            passed=bool(settings.database_url),
            detail="DATABASE_URL is set",
        ),
        GateResult(
            name="queue_configured",
            passed=bool(settings.redis_url and settings.celery_broker_url and settings.celery_result_backend),
            detail="Redis + Celery broker/result are configured",
        ),
        GateResult(
            name="object_storage_configured",
            passed=bool(settings.s3_endpoint_url and settings.s3_bucket),
            detail="S3-compatible object storage endpoint and bucket are configured",
        ),
        GateResult(
            name="plugin_signature_enforced",
            passed=bool(settings.plugin_signature_secret),
            detail="Plugin signature secret is configured",
        ),
        GateResult(
            name="openapi_generation_enabled",
            passed=bool(getattr(settings, "enable_openapi", True)),
            detail="OpenAPI generation is enabled for SDK and integration consistency",
        ),
    ]

    prod_only: list[GateResult] = [
        GateResult(
            name="jwt_secret_strength",
            passed=bool(len(getattr(settings, "jwt_secret", "") or "") >= 32),
            detail="JWT secret length >= 32 characters",
        ),
        GateResult(
            name="analyst_api_key_configured",
            passed=bool(getattr(settings, "analyst_api_key", "")),
            detail="Analyst review queue gate is configured",
        ),
        GateResult(
            name="admin_api_key_configured",
            passed=bool(getattr(settings, "admin_api_key", "")),
            detail="Admin console gate is configured",
        ),
        GateResult(
            name="cors_hardened",
            passed="*" not in (getattr(settings, "allowed_origins", []) or []),
            detail="CORS allow-list does not include wildcard origins",
        ),
    ]
    if env == "production":
        gates.extend(prod_only)

    passed_count = sum(1 for g in gates if g.passed)
    total_count = len(gates)
    score = round((passed_count / max(total_count, 1)) * 100.0, 2)
    status = "ready" if score >= 90 else ("warning" if score >= 70 else "not_ready")

    return {
        "status": status,
        "score": score,
        "required_gate_count": total_count,
        "passed_gate_count": passed_count,
        "failed_gates": [g.name for g in gates if not g.passed],
        "gates": [
            {
                "name": g.name,
                "passed": g.passed,
                "detail": g.detail,
            }
            for g in gates
        ],
    }