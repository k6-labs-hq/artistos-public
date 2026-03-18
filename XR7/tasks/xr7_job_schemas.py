from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RetryPolicy(BaseModel):
    max_retries: int
    backoff_seconds: int
    max_backoff_seconds: int


RETRY_POLICIES: dict[str, RetryPolicy] = {
    "api_ingestion": RetryPolicy(max_retries=5, backoff_seconds=10, max_backoff_seconds=300),
    "file_ingestion": RetryPolicy(max_retries=3, backoff_seconds=15, max_backoff_seconds=180),
    "fingerprinting": RetryPolicy(max_retries=4, backoff_seconds=20, max_backoff_seconds=240),
    "reconciliation": RetryPolicy(max_retries=3, backoff_seconds=15, max_backoff_seconds=180),
    "black_box_detection": RetryPolicy(max_retries=3, backoff_seconds=15, max_backoff_seconds=180),
}


class APIIngestionJobPayload(BaseModel):
    tenant_id: str = "default"
    artist_id: str
    providers: list[str] = Field(default_factory=list)
    since: datetime | None = None
    until: datetime | None = None


class FileIngestionJobPayload(BaseModel):
    tenant_id: str = "default"
    artist_id: str
    source_system: str
    filename: str
    content_base64: str


class FingerprintJobPayload(BaseModel):
    tenant_id: str = "default"
    artist_id: str
    platform: str
    detections: list[dict[str, object]] = Field(default_factory=list)


class ReconciliationJobPayload(BaseModel):
    tenant_id: str = "default"
    artist_id: str
    min_auto_match: float = 0.92


class BlackBoxJobPayload(BaseModel):
    tenant_id: str = "default"
    artist_id: str
    min_confidence: float = 0.85
