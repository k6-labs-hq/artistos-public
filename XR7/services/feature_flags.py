from __future__ import annotations

import hashlib
from typing import Any

from sqlalchemy.orm import Session

from XR7.models.feature_flag import FeatureFlag


class FeatureFlagService:
    def __init__(self, db: Session):
        self.db = db

    def list_flags(self) -> list[FeatureFlag]:
        return self.db.query(FeatureFlag).order_by(FeatureFlag.key.asc()).all()

    def upsert_flag(
        self,
        *,
        key: str,
        description: str | None,
        enabled: bool,
        rollout_percentage: int,
        target_user_ids: list[str] | None = None,
        conditions: dict[str, Any] | None = None,
    ) -> FeatureFlag:
        row = self.db.query(FeatureFlag).filter(FeatureFlag.key == key).first()
        if row is None:
            row = FeatureFlag(key=key)
            self.db.add(row)
        row.description = description
        row.enabled = enabled
        row.rollout_percentage = max(0, min(100, int(rollout_percentage)))
        row.target_user_ids = target_user_ids or []
        row.conditions = conditions or {}
        self.db.commit()
        self.db.refresh(row)
        return row

    def is_enabled(
        self,
        key: str,
        *,
        subject_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> bool:
        row = self.db.query(FeatureFlag).filter(FeatureFlag.key == key).first()
        if row is None or not row.enabled:
            return False

        attrs = attributes or {}
        if subject_id and subject_id in (row.target_user_ids or []):
            return True

        required_env = str((row.conditions or {}).get("environment") or "").strip().lower()
        if required_env and str(attrs.get("environment") or "").strip().lower() != required_env:
            return False

        if not subject_id:
            return row.rollout_percentage >= 100

        digest = hashlib.sha256(f"{key}:{subject_id}".encode("utf-8")).hexdigest()
        bucket = int(digest[:8], 16) % 100
        return bucket < int(row.rollout_percentage or 0)
