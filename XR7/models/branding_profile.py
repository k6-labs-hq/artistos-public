from __future__ import annotations

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from XR7.models.base import Base


class BrandingProfile(Base):
    __tablename__ = "branding_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False, default="XR7")
    logo_url: Mapped[str] = mapped_column(
        String, nullable=False, default="https://assets.xr7.ai/logo.svg"
    )
    primary_color: Mapped[str] = mapped_column(String, nullable=False, default="#1f7a5a")
    secondary_color: Mapped[str] = mapped_column(String, nullable=False, default="#2f9c74")
    accent_color: Mapped[str] = mapped_column(String, nullable=False, default="#f59e0b")
    dashboard_header_text: Mapped[str] = mapped_column(
        String, nullable=False, default="Artist Recovery Dashboard"
    )
    dashboard_footer_text: Mapped[str] = mapped_column(
        String, nullable=False, default="Powered by XR7 Engine"
    )
    support_email: Mapped[str] = mapped_column(String, nullable=False, default="support@xr7.ai")
    support_phone: Mapped[str] = mapped_column(String, nullable=False, default="+1-800-XR7-HELP")
    legal_disclaimer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=(
            "Forecasts and recovery estimates are provided for operational guidance only. "
            "Actual outcomes may vary based on payer behavior, legal deadlines, and data quality."
        ),
    )
    custom_domain: Mapped[str | None] = mapped_column(String, nullable=True)
    white_label_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class BrandingHelpArticle(Base):
    __tablename__ = "branding_help_articles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, default="faq")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class BrandingProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    display_name: str
    logo_url: str
    primary_color: str
    secondary_color: str
    accent_color: str
    dashboard_header_text: str
    dashboard_footer_text: str
    support_email: str
    support_phone: str
    legal_disclaimer: str
    custom_domain: str | None
    white_label_enabled: bool
    created_at: datetime
    updated_at: datetime


class BrandingHelpArticleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    org_id: str
    title: str
    body: str
    category: str
    created_at: datetime
    updated_at: datetime
