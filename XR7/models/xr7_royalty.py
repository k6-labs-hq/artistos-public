from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timezone

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class XR7MatchMethod(str, enum.Enum):
    API = "api"
    FINGERPRINT = "fingerprint"
    FUZZY = "fuzzy"
    MANUAL = "manual"


class XR7SourceCategory(str, enum.Enum):
    API = "api"
    FILE = "file"
    FINGERPRINT = "fingerprint"


class XR7ConnectorStatus(str, enum.Enum):
    ACTIVE = "active"
    DISCONNECTED = "disconnected"


class XR7IdentityNodeType(str, enum.Enum):
    ARTIST = "artist"
    WORK = "work"
    TRACK = "track"
    RIGHTSHOLDER = "rightsholder"
    PLATFORM_PROFILE = "platform_profile"


class XR7Track(Base):
    __tablename__ = "xr7_tracks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    version: Mapped[str | None] = mapped_column(String, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    primary_artist_name: Mapped[str | None] = mapped_column(String, nullable=True)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    isrc: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    upc: Mapped[str | None] = mapped_column(String, nullable=True)
    label_name: Mapped[str | None] = mapped_column(String, nullable=True)
    distributor: Mapped[str | None] = mapped_column(String, nullable=True)
    audio_fingerprint_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    source_priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    canonical_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    metadata_quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metadata_quality_grade: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_repair_status: Mapped[str] = mapped_column(String, nullable=False, default="not_evaluated")
    ugc_usage_velocity_7d: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ugc_usage_velocity_30d: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ugc_platform_coverage_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    viral_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7Work(Base):
    __tablename__ = "xr7_works"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    iswc: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    territory_scope: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    registration_completeness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    split_conflict_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    split_conflict_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    recovery_forecast_90d: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recovery_forecast_365d: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7IdentifierMapping(Base):
    __tablename__ = "xr7_identifier_mappings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    track_id: Mapped[str | None] = mapped_column(String, ForeignKey("xr7_tracks.id"), nullable=True, index=True)
    work_id: Mapped[str | None] = mapped_column(String, ForeignKey("xr7_works.id"), nullable=True, index=True)
    isrc: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    iswc: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    ipi_number: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    cae_number: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    source_system: Mapped[str] = mapped_column(String, nullable=False)
    evidence_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7UsageEvent(Base):
    __tablename__ = "xr7_usage_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    territory: Mapped[str | None] = mapped_column(String, nullable=True)
    channel: Mapped[str | None] = mapped_column(String, nullable=True)
    units: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    asset_ref: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    track_id: Mapped[str | None] = mapped_column(String, ForeignKey("xr7_tracks.id"), nullable=True, index=True)
    work_id: Mapped[str | None] = mapped_column(String, ForeignKey("xr7_works.id"), nullable=True, index=True)
    match_method: Mapped[str] = mapped_column(Enum(XR7MatchMethod), nullable=False, default=XR7MatchMethod.API)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    monetization_estimate: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    source_category: Mapped[str] = mapped_column(Enum(XR7SourceCategory), nullable=False)
    raw_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    ugc_content_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    ugc_format: Mapped[str | None] = mapped_column(String, nullable=True)
    ugc_video_duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remix_parent_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    trend_cluster_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    short_form_signal_strength: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    black_box_risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    explainability_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7RoyaltyStatement(Base):
    __tablename__ = "xr7_royalty_statements"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_system: Mapped[str] = mapped_column(String, nullable=False, index=True)
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    gross_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    net_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    line_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    file_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    parse_status: Mapped[str] = mapped_column(String, nullable=False, default="processed")
    schema_version: Mapped[str] = mapped_column(String, nullable=False, default="v1")
    ingestion_errors_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7RoyaltyStatementLine(Base):
    __tablename__ = "xr7_royalty_statement_lines"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    statement_id: Mapped[str] = mapped_column(String, ForeignKey("xr7_royalty_statements.id"), nullable=False, index=True)
    row_index: Mapped[int] = mapped_column(Integer, nullable=False)
    raw_work_title: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_artist_name: Mapped[str | None] = mapped_column(String, nullable=True)
    isrc: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    iswc: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    territory: Mapped[str | None] = mapped_column(String, nullable=True)
    units: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="USD")
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class XR7UnmatchedWork(Base):
    __tablename__ = "xr7_unmatched_works"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_system: Mapped[str] = mapped_column(String, nullable=False, index=True)
    raw_title: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_writer: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_identifier: Mapped[str | None] = mapped_column(String, nullable=True)
    candidate_work_ids_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    reason_code: Mapped[str] = mapped_column(String, nullable=False)
    recommended_action: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="open")
    resolution_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    suggested_matches_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    suggested_resolution_actions_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    ai_resolution_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recovery_potential_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    urgency_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7IdentityNode(Base):
    __tablename__ = "xr7_identity_nodes"
    __table_args__ = (
        UniqueConstraint("tenant_id", "artist_id", "node_type", "node_key", name="uq_xr7_identity_node"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(Enum(XR7IdentityNodeType), nullable=False, index=True)
    node_key: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7IdentityEdge(Base):
    __tablename__ = "xr7_identity_edges"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    from_node_id: Mapped[str] = mapped_column(String, ForeignKey("xr7_identity_nodes.id"), nullable=False, index=True)
    to_node_id: Mapped[str] = mapped_column(String, ForeignKey("xr7_identity_nodes.id"), nullable=False, index=True)
    edge_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_system: Mapped[str] = mapped_column(String, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    active_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    active_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7ConnectorCredential(Base):
    __tablename__ = "xr7_connector_credentials"
    __table_args__ = (
        UniqueConstraint("tenant_id", "artist_id", "provider", "external_account_id", name="uq_xr7_connector_credential"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String, nullable=False, index=True)
    external_account_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    encrypted_access_token: Mapped[str] = mapped_column(Text, nullable=False)
    encrypted_refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    granted_scopes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    status: Mapped[str] = mapped_column(Enum(XR7ConnectorStatus), nullable=False, default=XR7ConnectorStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7CatalogValuationSnapshot(Base):
    __tablename__ = "xr7_catalog_valuation_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    baseline_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    corrected_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    upside_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence_interval_low: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence_interval_high: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    assumptions_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7RecoveryForecast(Base):
    __tablename__ = "xr7_recovery_forecasts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    scope_type: Mapped[str] = mapped_column(String, nullable=False, default="artist")
    scope_id: Mapped[str | None] = mapped_column(String, nullable=True)
    forecast_horizon_days: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    forecast_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence_interval_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    model_version: Mapped[str] = mapped_column(String, nullable=False, default="v1")
    feature_snapshot_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7SplitSheetImport(Base):
    __tablename__ = "xr7_split_sheet_imports"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    file_ref: Mapped[str] = mapped_column(String, nullable=False)
    import_status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    conflicts_found: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    auto_resolved_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    manual_required_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    imported_by: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7AIDecisionAuditLog(Base):
    __tablename__ = "xr7_ai_decision_audit_log"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, default="default", index=True)
    artist_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    decision_type: Mapped[str] = mapped_column(String, nullable=False)
    model_provider: Mapped[str] = mapped_column(String, nullable=False)
    model_version: Mapped[str] = mapped_column(String, nullable=False)
    prompt_hash: Mapped[str] = mapped_column(String, nullable=False)
    input_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    output_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    reviewer_id: Mapped[str | None] = mapped_column(String, nullable=True)
    override_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class XR7ConnectorCredentialUpsert(BaseModel):
    provider: str
    external_account_id: str
    access_token: str
    refresh_token: str | None = None
    expires_in_seconds: int | None = 3600
    granted_scopes: list[str] = Field(default_factory=list)
    tenant_id: str = "default"


class XR7PipelineResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pipeline: str
    artist_id: str
    tenant_id: str
    status: str
    processed: int
    details: dict[str, object] = Field(default_factory=dict)


class XR7RoyaltyGapRow(BaseModel):
    platform: str
    territory: str
    period_start: date | None = None
    period_end: date | None = None
    expected_amount: float
    reported_amount: float
    gap_amount: float
    gap_rate: float


class XR7RoyaltyGapReport(BaseModel):
    artist_id: str
    tenant_id: str
    generated_at: datetime
    rows: list[XR7RoyaltyGapRow] = Field(default_factory=list)
    total_expected: float = 0.0
    total_reported: float = 0.0
    total_gap: float = 0.0
