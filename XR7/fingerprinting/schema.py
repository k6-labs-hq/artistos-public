"""Shared normalized schema for the XR7 audio fingerprinting and matching engine.

All provider adapters normalize their raw responses into these structures.
The MatchingEngine consumes and emits these types.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class MatchType(str, enum.Enum):
    BROADCAST = "broadcast"
    RADIO = "radio"
    SOCIAL = "social"
    VENUE = "venue"
    UGC = "ugc"
    SYNC = "sync"
    STREAM = "stream"
    DOWNLOAD = "download"
    LIVE = "live"
    UNKNOWN = "unknown"


class RoyaltyStatus(str, enum.Enum):
    PAID = "paid"
    UNPAID = "unpaid"
    UNDERPAID = "underpaid"
    MISMATCHED = "mismatched"
    UNKNOWN = "unknown"


class AnomalyType(str, enum.Enum):
    USAGE_NO_ROYALTY = "usage_no_royalty"
    ROYALTY_NO_USAGE = "royalty_no_usage"
    FOREIGN_USAGE_NO_PRO = "foreign_usage_no_pro"
    LIVE_NO_PRO_PERFORMANCE = "live_no_pro_performance"
    SOCIAL_NO_DISTRIBUTOR = "social_no_distributor"
    CATALOG_MISMATCH = "catalog_mismatch"
    ISRC_CONFLICT = "isrc_conflict"
    ISWC_CONFLICT = "iswc_conflict"
    IPI_CONFLICT = "ipi_conflict"
    NONE = "none"


class ProviderStatus(str, enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


# ---------------------------------------------------------------------------
# Core normalized result
# ---------------------------------------------------------------------------


class NormalizedMatchResult(BaseModel):
    """Universal match result produced by every provider adapter."""

    track_id: str | None = None
    isrc: str | None = None
    iswc: str | None = None
    ipi: str | None = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    match_type: MatchType = MatchType.UNKNOWN
    platform: str | None = None
    territory: str | None = None
    timestamp: datetime
    provider: str
    royalty_status: RoyaltyStatus = RoyaltyStatus.UNKNOWN
    anomaly_type: AnomalyType = AnomalyType.NONE
    title: str | None = None
    artist_name: str | None = None
    album: str | None = None
    duration_seconds: float | None = None
    external_track_url: str | None = None
    raw_provider_payload: dict[str, Any] = Field(default_factory=dict)

    model_config = {"use_enum_values": False}


# ---------------------------------------------------------------------------
# Provider health
# ---------------------------------------------------------------------------


class ProviderHealthStatus(BaseModel):
    provider: str
    status: ProviderStatus
    latency_ms: float | None = None
    error_message: str | None = None
    checked_at: datetime


# ---------------------------------------------------------------------------
# Input / request schemas
# ---------------------------------------------------------------------------


class FingerprintSubmitRequest(BaseModel):
    """Input for a fingerprinting job."""

    artist_id: str
    audio_url: str | None = None
    audio_s3_key: str | None = None
    isrc: str | None = None
    title: str | None = None
    artist_name: str | None = None
    territory: str | None = None
    providers: list[str] | None = None  # None → all active providers
    tenant_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Matching Engine output
# ---------------------------------------------------------------------------


class CatalogMatchResult(BaseModel):
    """Result of a catalog lookup for a fingerprint match."""

    work_id: str | None = None
    isrc: str | None = None
    iswc: str | None = None
    ipi: str | None = None
    title: str | None = None
    artist_name: str | None = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    match_method: str = "unknown"  # isrc, iswc, ipi, title_artist_fuzzy, acoustic


class UsageMatchResult(BaseModel):
    """A detected usage event matched to a catalog work."""

    work_id: str | None = None
    isrc: str | None = None
    platform: str
    territory: str | None = None
    match_type: MatchType
    detected_at: datetime
    reported: bool = False
    provider: str


class RoyaltyGapResult(BaseModel):
    """A discrepancy between detected usage and received royalties."""

    work_id: str | None = None
    isrc: str | None = None
    platform: str | None = None
    territory: str | None = None
    match_type: MatchType
    detected_usage: bool = True
    royalty_received: bool = False
    estimated_gap_usd: float | None = None
    anomaly_type: AnomalyType = AnomalyType.USAGE_NO_ROYALTY
    description: str = ""


class MatchingEngineReport(BaseModel):
    """Aggregated output from a full Matching Engine reconciliation run."""

    artist_id: str
    fingerprint_results: list[NormalizedMatchResult] = Field(default_factory=list)
    catalog_matches: list[CatalogMatchResult] = Field(default_factory=list)
    usage_matches: list[UsageMatchResult] = Field(default_factory=list)
    royalty_gaps: list[RoyaltyGapResult] = Field(default_factory=list)
    anomalies: list[RoyaltyGapResult] = Field(default_factory=list)
    generated_at: datetime
    schema_version: str = "xr7.fingerprinting.matching_report.v1"
