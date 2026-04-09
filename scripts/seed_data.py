from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from XR7.models.artist import Artist
from XR7.models.base import SessionLocal
from XR7.models.claim import Claim, ClaimStatus
from XR7.models.event import Event, EventType
from XR7.models.payment import Payment, PaymentType
from XR7.models.work import Work, WorkType


def main() -> None:
    db = SessionLocal()
    try:
        artist = Artist(id=str(uuid.uuid4()), name="Seed Artist", created_at=datetime.now(timezone.utc))
        db.add(artist)

        work = Work(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            title="Seed Track",
            isrc="USAAA1234567",
            iswc="T-000.000.001-0",
            work_type=WorkType.RECORDING,
        )
        db.add(work)

        event = Event(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            event_type=EventType.STREAM,
            platform="Spotify",
            territory="US",
            timestamp=datetime.now(timezone.utc),
            quantity=1000,
            unit_value=0.004,
            currency="USD",
        )
        db.add(event)

        payment = Payment(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            payment_type=PaymentType.ROYALTY,
            amount=4.0,
            currency="USD",
            source="Seed Statement",
        )
        db.add(payment)

        claim = Claim(
            id=str(uuid.uuid4()),
            artist_id=artist.id,
            anomaly_id=str(uuid.uuid4()),
            claim_type="ROYALTY",
            status=ClaimStatus.IDENTIFIED,
            recovered_amount=0.0,
            evidence={"seed": True},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(claim)

        db.commit()
        print(f"Seeded artist {artist.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
