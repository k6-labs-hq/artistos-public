"""Idempotency key support for write operation deduplication."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict
from sqlalchemy import String
from sqlalchemy.orm import Mapped, Session, mapped_column

from XR7.models.base import Base


class XR7IdempotencyRecord(Base):
    """Record of idempotent operations keyed by Idempotency-Key header value."""

    __tablename__ = "xr7_idempotency_records"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    idempotency_key: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    artist_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    request_path: Mapped[str | None] = mapped_column(String, nullable=True)
    request_method: Mapped[str | None] = mapped_column(String, nullable=True)
    response_status: Mapped[int] = mapped_column(nullable=False)
    response_body: Mapped[str] = mapped_column(nullable=False)  # JSON
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))


class XR7IdempotencyRecordSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    idempotency_key: str
    tenant_id: str
    artist_id: str | None = None
    request_path: str | None = None
    request_method: str | None = None
    response_status: int
    response_body: str
    created_at: datetime


class IdempotencyService:
    """Service for managing idempotent operation deduplication."""

    def __init__(self, db: Session):
        self.db = db

    def check_and_record(
        self,
        *,
        idempotency_key: str,
        tenant_id: str,
        artist_id: str | None = None,
        request_path: str | None = None,
        request_method: str | None = None,
        response_status: int,
        response_body: dict | list | str | None,
    ) -> tuple[bool, dict | list | str | None]:
        """Check if idempotency key has been seen before.

        Args:
            idempotency_key: The Idempotency-Key header value
            tenant_id: Tenant ID
            artist_id: Optional artist ID
            request_path: Request path for logging
            request_method: Request method for logging
            response_status: HTTP response status code
            response_body: Response body payload

        Returns:
            (is_duplicate, cached_response_or_none) tuple
            - If idempotency_key was previously processed, returns (True, cached_body)
            - If this is the first time seeing the key, stores the record and returns (False, None)
        """
        # Check if we've seen this key before
        existing = (
            self.db.query(XR7IdempotencyRecord)
            .filter(XR7IdempotencyRecord.idempotency_key == idempotency_key)
            .first()
        )

        if existing:
            # Return the cached response
            try:
                cached_body = json.loads(existing.response_body)
            except (json.JSONDecodeError, ValueError):
                cached_body = existing.response_body
            return (True, cached_body)

        # First time seeing this key; store it
        response_body_str = (
            json.dumps(response_body, default=str)
            if not isinstance(response_body, str)
            else response_body
        )

        record = XR7IdempotencyRecord(
            id=str(uuid.uuid4()),
            idempotency_key=idempotency_key,
            tenant_id=tenant_id,
            artist_id=artist_id,
            request_path=request_path,
            request_method=request_method,
            response_status=response_status,
            response_body=response_body_str,
        )
        self.db.add(record)
        self.db.commit()

        return (False, None)

    def get_by_key(self, idempotency_key: str) -> dict | None:
        """Retrieve a recorded idempotency response by key."""
        record = (
            self.db.query(XR7IdempotencyRecord)
            .filter(XR7IdempotencyRecord.idempotency_key == idempotency_key)
            .first()
        )
        if not record:
            return None

        try:
            response_body = json.loads(record.response_body)
        except (json.JSONDecodeError, ValueError):
            response_body = record.response_body

        return {
            "id": record.id,
            "idempotency_key": record.idempotency_key,
            "tenant_id": record.tenant_id,
            "artist_id": record.artist_id,
            "request_path": record.request_path,
            "request_method": record.request_method,
            "response_status": record.response_status,
            "response_body": response_body,
            "created_at": record.created_at.isoformat(),
        }
