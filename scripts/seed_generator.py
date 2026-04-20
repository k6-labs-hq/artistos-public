"""
Realistic Seed Data Generator for ArtistOS Development and Testing.

Generates comprehensive test data across all major workflows to support:
- Local development with realistic catalog distributions
- Multi-tenant isolation testing at scale
- Claims lifecycle validation (identified → filed → paid)
- Anomaly detection and review queue workflows
- Performance testing at 10x, 100x scale targets

Usage:
    # Development scale (10 artists)
    python scripts/seed_generator.py --scale dev

    # Staging scale (100 artists, multiple tenants)
    python scripts/seed_generator.py --scale staging

    # Load test scale (1000+ artists)
    python scripts/seed_generator.py --scale load

Closes: XR7-409
Domain: developer-experience
Scale-target: 10x tenant/catalog testing with realistic data distributions
"""

from __future__ import annotations

import argparse
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from XR7.models.anomaly import Anomaly, AnomalySeverity  # noqa: E402
from XR7.models.artist import Artist  # noqa: E402
from XR7.models.base import SessionLocal  # noqa: E402
from XR7.models.claim import Claim, ClaimStatus  # noqa: E402
from XR7.models.event import Event, EventType  # noqa: E402
from XR7.models.payment import Payment  # noqa: E402
from XR7.models.review_queue import ReviewItem, ReviewItemStatus, ReviewSourceType  # noqa: E402
from XR7.models.work import Work, WorkType  # noqa: E402

# Seed data configurations by scale
SCALE_CONFIGS = {
    "dev": {
        "num_artists": 10,
        "num_tenants": 2,
        "works_per_artist": (5, 20),  # (min, max)
        "events_per_work": (50, 200),
        "historical_days": 90,
    },
    "staging": {
        "num_artists": 100,
        "num_tenants": 10,
        "works_per_artist": (10, 100),
        "events_per_work": (100, 1000),
        "historical_days": 180,
    },
    "load": {
        "num_artists": 1000,
        "num_tenants": 50,
        "works_per_artist": (20, 500),
        "events_per_work": (200, 5000),
        "historical_days": 365,
    },
}

# Realistic platforms and territories
PLATFORMS = ["Spotify", "Apple Music", "YouTube", "Amazon Music", "Deezer", "Tidal"]
TERRITORIES = ["US", "GB", "DE", "FR", "CA", "AU", "JP", "BR"]
CURRENCIES = {
    "US": "USD",
    "GB": "GBP",
    "DE": "EUR",
    "FR": "EUR",
    "CA": "CAD",
    "AU": "AUD",
    "JP": "JPY",
    "BR": "BRL",
}

# Anomaly types for diverse test scenarios
ANOMALY_TYPES = [
    ("RATE_DRIFT", AnomalySeverity.MEDIUM, 0.75),
    ("MISSING_PAYMENT", AnomalySeverity.HIGH, 0.85),
    ("METADATA_CONFLICT", AnomalySeverity.LOW, 0.60),
    ("UNDERPAYMENT", AnomalySeverity.HIGH, 0.90),
    ("TERRITORY_MISMATCH", AnomalySeverity.MEDIUM, 0.70),
]

# Claim status distribution (realistic lifecycle states)
CLAIM_STATUS_DISTRIBUTION = [
    (ClaimStatus.IDENTIFIED, 0.30),  # 30% in initial state
    (ClaimStatus.IN_REVIEW, 0.25),  # 25% under review
    (ClaimStatus.FILED, 0.20),  # 20% filed with payer
    (ClaimStatus.ACCEPTED, 0.15),  # 15% accepted
    (ClaimStatus.PAID, 0.10),  # 10% fully paid
]


class SeedDataGenerator:
    """Generates realistic seed data for ArtistOS workflows."""

    def __init__(self, db, config: dict):
        self.db = db
        self.config = config
        self.artists: List[Artist] = []
        self.works: List[Work] = []
        self.tenants: List[str] = []

    def generate_all(self) -> dict:
        """Generate complete seed data set.

        Returns:
            Summary dict with counts of created objects
        """
        print(
            f"🌱 Generating seed data: {self.config['num_artists']} artists across {self.config['num_tenants']} tenants"
        )

        # Create unique tenant IDs
        self.tenants = [f"tenant-{uuid.uuid4()}" for _ in range(self.config["num_tenants"])]

        # Generate artists, works, events
        self._generate_artists()
        self._generate_works()
        self._generate_events()

        # Generate anomalies and claims
        self._generate_anomalies()
        self._generate_claims()

        # Populate review queue
        self._generate_review_queue_items()

        self.db.commit()

        return {
            "artists": len(self.artists),
            "works": len(self.works),
            "tenants": len(self.tenants),
            "distinct_territories": len(TERRITORIES),
            "distinct_platforms": len(PLATFORMS),
        }

    def _generate_artists(self) -> None:
        """Create artists distributed across tenants."""
        print("  Creating artists...")
        for i in range(self.config["num_artists"]):
            artist = Artist(
                id=str(uuid.uuid4()),
                name=f"Seed Artist {i + 1}",
                email=f"artist{i + 1}@artistos-seed.local",
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(10, 365)),
            )
            self.db.add(artist)
            self.artists.append(artist)

        self.db.commit()
        print(f"    ✓ Created {len(self.artists)} artists")

    def _generate_works(self) -> None:
        """Create catalog works for each artist."""
        print("  Creating works...")
        for artist in self.artists:
            num_works = random.randint(*self.config["works_per_artist"])

            for i in range(num_works):
                # Generate unique identifiers
                isrc = f"US{random.choice(['AAA', 'BBB', 'CCC'])}{random.randint(1000000, 9999999)}"
                iswc = f"T-{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(0, 9)}"

                work = Work(
                    id=str(uuid.uuid4()),
                    artist_id=artist.id,
                    title=f"{artist.name} - Track {i + 1}",
                    isrc=isrc,
                    iswc=iswc,
                    work_type=WorkType.RECORDING,
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(30, 730)),
                )
                self.db.add(work)
                self.works.append(work)

        self.db.commit()
        print(f"    ✓ Created {len(self.works)} works")

    def _generate_events(self) -> None:
        """Create royalty events with realistic time series."""
        print("  Creating royalty events...")
        total_events = 0

        for work in self.works:
            num_events = random.randint(*self.config["events_per_work"])

            for i in range(num_events):
                # Distribute events over historical period
                days_ago = random.randint(0, self.config["historical_days"])
                timestamp = datetime.now(timezone.utc) - timedelta(days=days_ago)

                platform = random.choice(PLATFORMS)
                territory = random.choice(TERRITORIES)
                currency = CURRENCIES[territory]

                # Realistic stream counts with seasonal variation
                # Higher volume for newer events (recency bias)
                volume_factor = (
                    1.0
                    + (self.config["historical_days"] - days_ago) / self.config["historical_days"]
                )
                quantity = int(random.randint(10, 1000) * volume_factor)

                # Platform-specific rates (Spotify ~$0.003-0.005, YouTube ~$0.001-0.002)
                if platform == "Spotify":
                    unit_value = random.uniform(0.003, 0.005)
                elif platform == "YouTube":
                    unit_value = random.uniform(0.001, 0.002)
                else:
                    unit_value = random.uniform(0.002, 0.004)

                event = Event(
                    id=str(uuid.uuid4()),
                    artist_id=work.artist_id,
                    event_type=EventType.STREAM,
                    platform=platform,
                    territory=territory,
                    timestamp=timestamp,
                    quantity=quantity,
                    unit_value=unit_value,
                    currency=currency,
                )
                self.db.add(event)
                total_events += 1

                # Batch commit every 1000 events for performance
                if total_events % 1000 == 0:
                    self.db.commit()

        self.db.commit()
        print(f"    ✓ Created {total_events} royalty events")

    def _generate_anomalies(self) -> None:
        """Create diverse anomaly types for testing detection workflows."""
        print("  Creating anomalies...")
        total_anomalies = 0

        # Create anomalies for ~30% of artists
        sample_artists = random.sample(self.artists, int(len(self.artists) * 0.3))

        for artist in sample_artists:
            # Each artist gets 1-5 anomalies of varying types
            num_anomalies = random.randint(1, 5)

            for _ in range(num_anomalies):
                subtype, severity, base_confidence = random.choice(ANOMALY_TYPES)

                # Add noise to confidence scores for realistic distribution
                confidence = min(0.99, max(0.30, base_confidence + random.uniform(-0.10, 0.10)))

                # Estimated recoverable based on severity
                if severity == AnomalySeverity.HIGH:
                    estimated = random.uniform(5000, 50000)
                elif severity == AnomalySeverity.MEDIUM:
                    estimated = random.uniform(1000, 10000)
                else:
                    estimated = random.uniform(100, 2000)

                anomaly = Anomaly(
                    id=str(uuid.uuid4()),
                    artist_id=artist.id,
                    category="ROYALTY",
                    subtype=subtype,
                    severity=severity,
                    confidence_score=round(confidence, 4),
                    estimated_recoverable=round(estimated, 2),
                    description=f"Seed anomaly: {subtype} detected for {artist.name}",
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90)),
                )
                self.db.add(anomaly)
                total_anomalies += 1

        self.db.commit()
        print(f"    ✓ Created {total_anomalies} anomalies")

    def _generate_claims(self) -> None:
        """Create claims in various lifecycle states."""
        print("  Creating claims...")
        total_claims = 0

        # Create claim for each anomaly
        anomalies = self.db.query(Anomaly).all()

        for anomaly in anomalies:
            # Choose random claim status based on distribution
            rand = random.random()
            cumulative = 0.0
            status = ClaimStatus.IDENTIFIED

            for claim_status, probability in CLAIM_STATUS_DISTRIBUTION:
                cumulative += probability
                if rand <= cumulative:
                    status = claim_status
                    break

            # Recovered amount increases with claim progression
            if status == ClaimStatus.PAID:
                recovered = anomaly.estimated_recoverable * random.uniform(0.8, 1.0)
            elif status == ClaimStatus.ACCEPTED:
                recovered = anomaly.estimated_recoverable * random.uniform(0.5, 0.9)
            elif status == ClaimStatus.FILED:
                recovered = 0.0  # Not yet settled
            else:
                recovered = 0.0

            claim = Claim(
                id=str(uuid.uuid4()),
                artist_id=anomaly.artist_id,
                anomaly_id=anomaly.id,
                claim_type="ROYALTY",
                status=status,
                recovered_amount=round(recovered, 2),
                evidence={"seed_generated": True, "confidence": anomaly.confidence_score},
                created_at=anomaly.created_at + timedelta(days=random.randint(1, 14)),
                updated_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30)),
            )
            self.db.add(claim)
            total_claims += 1

        self.db.commit()
        print(f"    ✓ Created {total_claims} claims")

    def _generate_review_queue_items(self) -> None:
        """Populate review queue with prioritized items."""
        print("  Creating review queue items...")
        total_items = 0

        # Add review items for anomalies with confidence < 0.75
        low_confidence_anomalies = (
            self.db.query(Anomaly).filter(Anomaly.confidence_score < 0.75).all()
        )

        for anomaly in low_confidence_anomalies:
            priority = anomaly.estimated_recoverable / 10000  # Priority based on $ value

            review_item = ReviewItem(
                id=str(uuid.uuid4()),
                artist_id=anomaly.artist_id,
                source_type=ReviewSourceType.ML_CONFIDENCE,
                source_id=anomaly.id,
                reason=f"Low confidence ({anomaly.confidence_score:.2f}) anomaly requires analyst review",
                priority_score=round(priority, 2),
                status=(
                    ReviewItemStatus.PENDING
                    if random.random() < 0.7
                    else ReviewItemStatus.IN_PROGRESS
                ),
                payload={
                    "anomaly_subtype": anomaly.subtype,
                    "estimated_recoverable": anomaly.estimated_recoverable,
                },
                created_at=anomaly.created_at + timedelta(hours=random.randint(1, 48)),
            )
            self.db.add(review_item)
            total_items += 1

        self.db.commit()
        print(f"    ✓ Created {total_items} review queue items")


def main() -> None:
    """CLI entry point for seed data generation."""
    parser = argparse.ArgumentParser(description="Generate realistic seed data for ArtistOS")
    parser.add_argument(
        "--scale",
        choices=["dev", "staging", "load"],
        default="dev",
        help="Data scale: dev (10 artists), staging (100 artists), load (1000+ artists)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before seeding (USE WITH CAUTION)",
    )

    args = parser.parse_args()

    config = SCALE_CONFIGS[args.scale]

    db = SessionLocal()
    try:
        if args.clear:
            print("⚠️  Clearing existing data...")
            # WARNING: This deletes all data - only for dev/test environments
            db.query(ReviewItem).delete()
            db.query(Claim).delete()
            db.query(Anomaly).delete()
            db.query(Payment).delete()
            db.query(Event).delete()
            db.query(Work).delete()
            db.query(Artist).delete()
            db.commit()
            print("    ✓ Data cleared")

        generator = SeedDataGenerator(db, config)
        summary = generator.generate_all()

        print("\n✅ Seed data generation complete!")
        print(f"   Artists: {summary['artists']}")
        print(f"   Works: {summary['works']}")
        print(f"   Tenants: {summary['tenants']}")
        print(f"   Territories: {summary['distinct_territories']}")
        print(f"   Platforms: {summary['distinct_platforms']}")
        print("\n💡 Tip: Use different tenant IDs to test multi-tenant isolation")

    except Exception as e:
        print(f"\n❌ Error generating seed data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
