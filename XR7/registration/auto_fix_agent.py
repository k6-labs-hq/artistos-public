from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from XR7.recovery.immutable_ledger import ImmutableLedgerService


class AutoFixRegistrationAgent:
    def __init__(self, db: Session):
        self.db = db

    def scan_registration_gaps(self, artist_id: str) -> list[dict[str, Any]]:
        return [
            {
                "type": "missing_pro_registration",
                "severity": "high",
                "suggested_action": "Register work with PRO",
            },
            {
                "type": "missing_isrc",
                "severity": "medium",
                "suggested_action": "Create ISRC and update distributor metadata",
            },
        ]

    def auto_register_or_prepare_submission(
        self, artist_id: str, issues: list[dict[str, Any]]
    ) -> dict[str, Any]:
        forms = [
            {"issue": i["type"], "submission_mode": "simulated", "status": "prepared"}
            for i in issues
        ]
        payload = {
            "artist_id": artist_id,
            "prepared_forms": forms,
            "instructions": "Review prepared forms and click submit in your PRO/distributor portal.",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        ImmutableLedgerService(self.db).append(artist_id, "registration_autofix", payload)
        return payload

    def track_success(self, artist_id: str, submitted: int, accepted: int) -> dict[str, Any]:
        ratio = (accepted / submitted) if submitted else 0.0
        return {
            "artist_id": artist_id,
            "submitted": submitted,
            "accepted": accepted,
            "success_ratio": round(ratio, 4),
        }
