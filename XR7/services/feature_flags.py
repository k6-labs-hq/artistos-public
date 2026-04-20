"""Feature flag service for runtime configuration management.

Provides feature flag evaluation, targeting, and gradual rollout logic.
"""

import hashlib

from sqlalchemy.orm import Session

from XR7.models.feature_flag import FeatureFlag


class FeatureFlagService:
    """Feature flag service for dynamic feature toggling.

    Supports:
    - Global enable/disable
    - Percentage-based rollouts
    - User ID targeting
    - Conditional activation
    """

    def __init__(self, db: Session):
        self.db = db

    def list_flags(self) -> list[FeatureFlag]:
        """List all feature flags."""
        return self.db.query(FeatureFlag).order_by(FeatureFlag.key).all()

    def get_flag(self, key: str) -> FeatureFlag | None:
        """Get feature flag by key."""
        return self.db.query(FeatureFlag).filter(FeatureFlag.key == key).first()

    def upsert_flag(
        self,
        key: str,
        description: str | None = None,
        enabled: bool = False,
        rollout_percentage: int = 0,
        target_user_ids: list[str] | None = None,
        conditions: dict | None = None,
    ) -> FeatureFlag:
        """Create or update a feature flag."""
        flag = self.get_flag(key)

        if flag:
            # Update existing flag
            if description is not None:
                flag.description = description
            flag.enabled = enabled
            flag.rollout_percentage = max(0, min(100, rollout_percentage))
            flag.target_user_ids = target_user_ids or []
            flag.conditions = conditions or {}
        else:
            # Create new flag
            flag = FeatureFlag(
                key=key,
                description=description,
                enabled=enabled,
                rollout_percentage=max(0, min(100, rollout_percentage)),
                target_user_ids=target_user_ids or [],
                conditions=conditions or {},
            )
            self.db.add(flag)

        self.db.flush()
        return flag

    def is_enabled(
        self,
        flag_key: str,
        subject_id: str | None = None,
        attributes: dict | None = None,
    ) -> bool:
        """Evaluate whether a feature flag is enabled for a subject.

        Args:
            flag_key: Feature flag key
            subject_id: User/artist ID for targeting
            attributes: Additional context for condition matching

        Returns:
            True if feature is enabled for this subject
        """
        flag = self.get_flag(flag_key)

        # Flag doesn't exist = disabled
        if not flag:
            return False

        # Globally disabled = disabled
        if not flag.enabled:
            return False

        # Explicit targeting
        if subject_id and subject_id in flag.target_user_ids:
            return True

        # Percentage rollout (deterministic hash-based)
        if flag.rollout_percentage > 0 and subject_id:
            # Use consistent hash to determine rollout bucket
            hash_input = f"{flag_key}:{subject_id}"
            hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest()[:8], 16)
            bucket = hash_value % 100
            if bucket < flag.rollout_percentage:
                return True

        # Condition matching (placeholder - extend as needed)
        if flag.conditions and attributes:
            for condition_key, condition_value in flag.conditions.items():
                if attributes.get(condition_key) == condition_value:
                    return True

        # Fall through: disabled
        return False

    def delete_flag(self, key: str) -> bool:
        """Delete a feature flag by key.

        Returns:
            True if flag was deleted, False if not found
        """
        flag = self.get_flag(key)
        if flag:
            self.db.delete(flag)
            self.db.flush()
            return True
        return False
