from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class XR7Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./XR7.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://redis:6379/0"))
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://redis:6379/1"))
    s3_endpoint_url: str | None = os.getenv("S3_ENDPOINT_URL")
    s3_region: str = os.getenv("S3_REGION", "us-east-1")
    s3_bucket: str = os.getenv("S3_BUCKET", "xr7-artifacts")
    s3_access_key_id: str | None = os.getenv("S3_ACCESS_KEY_ID")
    s3_secret_access_key: str | None = os.getenv("S3_SECRET_ACCESS_KEY")
    s3_use_ssl: bool = os.getenv("S3_USE_SSL", "0").strip().lower() in {"1", "true", "yes"}
    sync_requeue_seconds: int = int(os.getenv("XR7_SYNC_REQUEUE_SECONDS", "60"))
    plugin_allowed_prefixes_raw: str = os.getenv("XR7_PLUGIN_ALLOWED_PREFIXES", "XR7.plugins,tests.plugins")
    plugin_blocked_prefixes_raw: str = os.getenv("XR7_PLUGIN_BLOCKED_PREFIXES", "os,sys,subprocess,builtins,importlib")
    plugin_signature_secret: str = os.getenv("XR7_PLUGIN_SIGNATURE_SECRET", "")

    @property
    def plugin_allowed_prefixes(self) -> tuple[str, ...]:
        return tuple(p.strip() for p in self.plugin_allowed_prefixes_raw.split(",") if p.strip())

    @property
    def plugin_blocked_prefixes(self) -> tuple[str, ...]:
        return tuple(p.strip() for p in self.plugin_blocked_prefixes_raw.split(",") if p.strip())


settings = XR7Settings()
