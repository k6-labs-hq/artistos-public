"""Seed a demo artist + anomaly + PREPARED claim for the operator dashboard.

Creates the minimum data needed to exercise the /ops dashboard end-to-end:
- One artist with a recognisable name
- One anomaly with a realistic feature_snapshot (rule_id, evidence)
- One claim in PREPARED status, payer_name=BMI, sol_deadline set ~120 days
  out so the SOL badge renders the "ok" tone

After seeding, hit the /ops page with X-Admin-Key set, click "File via
email" — without POSTMARK_API_TOKEN set, dispute_delivery returns
stubbed=True (no real email sent) but the claim still advances to FILED
and the result panel shows the (None) MessageID.

Usage:

    python scripts/seed_ops_demo.py

Requires the same env as the API process (DATABASE_URL or default sqlite).
Idempotent on artist name — re-running creates additional claims for the
same artist rather than duplicating the artist row.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from XR7.models.anomaly import (  # noqa: E402
    Anomaly,
    AnomalyCategory,
    AnomalySeverity,
    AnomalyStatus,
)
from XR7.models.artist import Artist  # noqa: E402
from XR7.models.base import SessionLocal  # noqa: E402
from XR7.models.claim import Claim, ClaimStatus  # noqa: E402

DEMO_ARTIST_NAME = "Demo Songwriter (BMI affiliate)"


def main() -> None:
    db = SessionLocal()
    try:
        artist = db.query(Artist).filter(Artist.name == DEMO_ARTIST_NAME).first()
        if artist is None:
            artist = Artist(
                id=str(uuid.uuid4()),
                name=DEMO_ARTIST_NAME,
                created_at=datetime.now(timezone.utc),
            )
            db.add(artist)
            db.flush()
            print(f"Created artist {artist.id} ({DEMO_ARTIST_NAME})")
        else:
            print(f"Reusing artist {artist.id} ({DEMO_ARTIST_NAME})")

        now = datetime.now(timezone.utc)
        feature_snapshot = {
            "rule_id": "HIGH_RETROACTIVE_PAYMENT_RATIO",
            "evidence": {
                "worst_payer": "BMI",
                "ratio": 0.72,
                "window_months": 12,
                "expected_pattern": "monthly within 30d of statement period",
                "observed_pattern": "lump retroactive payments months later",
            },
            "model_version": "ops-demo-1",
        }

        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            category=AnomalyCategory.ROYALTY,
            subtype="HIGH_RETROACTIVE_PAYMENT_RATIO",
            severity=AnomalySeverity.HIGH,
            expected_amount=8500.0,
            actual_amount=2380.0,
            estimated_recoverable=6120.0,
            confidence_score=0.87,
            time_window_start=now - timedelta(days=365),
            time_window_end=now,
            territory="US",
            status=AnomalyStatus.OPEN,
            description=(
                "72% of BMI payments to this writer arrived as lump retroactive "
                "settlements 4-9 months after the statement period — pattern "
                "consistent with delayed work-registration matching."
            ),
            feature_snapshot=json.dumps(feature_snapshot),
            urgent_flag=False,
            created_at=now,
        )
        db.add(anomaly)
        db.flush()

        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=anomaly.id,
            claim_type="ROYALTY",
            status=ClaimStatus.PREPARED,
            payer_name="BMI",
            sol_deadline=now + timedelta(days=120),
            governing_law_state="USA",
            contract_type="recording",
            currency="USD",
            evidence={"seed": True, "demo": "ops_dashboard"},
            created_at=now,
            updated_at=now,
        )
        db.add(claim)
        db.commit()

        print()
        print("=" * 72)
        print("OPS DASHBOARD DEMO — ready to drive")
        print("=" * 72)
        print(f"Artist ID    : {artist.id}")
        print(f"Anomaly ID   : {anomaly.id}")
        print(f"Claim ID     : {claim.id}")
        print(f"Status       : {getattr(claim.status, 'value', claim.status)}")
        print(f"Payer        : {claim.payer_name}")
        print(f"$ recoverable: ${anomaly.estimated_recoverable:,.0f}")
        print(f"SOL deadline : {claim.sol_deadline.date()} (~120 days)")
        print()
        print("Next steps:")
        print("  1. Set ADMIN_API_KEY in your .env (any value, e.g. 'dev-admin-key')")
        print("     Leave POSTMARK_API_TOKEN unset to use the stub sender.")
        print("  2. Start the API:        make run")
        print("  3. Start the frontend:   make frontend-dev")
        print("  4. Open http://localhost:5173/ops")
        print("  5. Paste your ADMIN_API_KEY into the Admin key field, click")
        print("     Load queue. The 'Ready to file' tab should show this claim.")
        print("  6. Click 'File via email'. Confirm. The result panel will show")
        print("     stubbed=True (no real Postmark send) and the claim advances")
        print("     to FILED. Re-load the queue to see it move tabs.")
        print()

    finally:
        db.close()


if __name__ == "__main__":
    main()
