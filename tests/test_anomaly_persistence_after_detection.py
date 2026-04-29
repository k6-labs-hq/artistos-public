"""
Regression test for #194: anomaly findings must be persisted to the DB.

Before the fix, ``AnomalyEngine.detect_all()`` returned a list of dicts but
the upload flow discarded them — so the ``anomalies`` table stayed empty
even when the engine produced findings. The dashboard / notification path,
which reads from the ``anomalies`` table, then saw nothing.

These tests pin: calling ``run_detection_and_persist`` writes one row per
gating-accepted finding, and re-running is idempotent (no duplicates).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from tests.conftest import TestSession as _TestSession
from XR7.api.routers.anomalies import run_detection_and_persist
from XR7.models.anomaly import Anomaly
from XR7.models.artist import Artist
from XR7.models.event import Event, EventType


def _seed_artist_with_streams_no_payments() -> str:
    """Seed an artist with stream events but zero payments.

    This deterministically triggers STREAM_MONTH_NO_PAYMENT (Rule 4) in the
    transparent rule library, so we know the engine has at least one finding
    to persist.
    """
    db = _TestSession()
    artist_id = str(uuid.uuid4())
    db.add(
        Artist(
            id=artist_id,
            name="Persistence Regression",
            email=f"reg-{artist_id[:8]}@example.com",
            country_code="US",
            created_at=datetime.now(timezone.utc),
        )
    )
    db.flush()
    for month in (1, 2, 3):
        db.add(
            Event(
                id=str(uuid.uuid4()),
                event_type=EventType.STREAM,
                artist_id=artist_id,
                platform="Spotify",
                territory="US",
                timestamp=datetime(2025, month, 15, tzinfo=timezone.utc),
                quantity=1000,
                unit_value=0.004,
                currency="USD",
            )
        )
    db.commit()
    db.close()
    return artist_id


def test_run_detection_persists_findings():
    artist_id = _seed_artist_with_streams_no_payments()

    db = _TestSession()
    try:
        before = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).count()
        assert before == 0

        enriched = run_detection_and_persist(artist_id, db)
        assert len(enriched) >= 1, "engine should produce at least one finding"

        after = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).count()
        assert after == len(enriched), (
            f"each enriched finding must land in the DB; got {after} rows for "
            f"{len(enriched)} enriched dicts"
        )
        assert all("id" in row for row in enriched)
    finally:
        db.close()


def test_run_detection_is_idempotent():
    """Re-running detection on the same artist must not duplicate rows.

    The deterministic anomaly id (rule_id + evidence hash) means a second
    call upserts existing rows rather than inserting fresh ones.
    """
    artist_id = _seed_artist_with_streams_no_payments()

    db = _TestSession()
    try:
        run_detection_and_persist(artist_id, db)
        first_count = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).count()

        run_detection_and_persist(artist_id, db)
        second_count = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).count()

        assert first_count == second_count, "second run must not create duplicates"
    finally:
        db.close()


def test_anomaly_count_stable_when_dataset_grows(monkeypatch):
    """Regression for #216.

    Two upload events for the same artist (more data the second time) used to
    duplicate same-rule anomaly rows because the deterministic id hashed on
    the full evidence dict, which contains time-varying counts. Each new
    detection therefore produced a fresh hash → fresh INSERT instead of
    UPSERT.

    Pin: regardless of how many times detection re-runs against an evolving
    dataset, only one row per (rule_id, identity_key) should exist.
    """
    from XR7.models.payment import Payment, PaymentType

    artist_id = _seed_artist_with_streams_no_payments()

    db = _TestSession()
    try:
        # First detection: events only, no payments.
        run_detection_and_persist(artist_id, db)
        first_count = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).count()
        assert first_count >= 1

        # Second wave: add a payment, re-run. Payment count + last_payment_at
        # change in the underlying engine evidence; pre-fix this guaranteed
        # duplicate INSERTs for any rule using payment_count in evidence.
        db.add(
            Payment(
                id=str(uuid.uuid4()),
                payment_type=PaymentType.ROYALTY,
                artist_id=artist_id,
                amount=4.0,
                currency="USD",
                source="DistroKid",
                received_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
        run_detection_and_persist(artist_id, db)
        second_count = db.query(Anomaly).filter(Anomaly.artist_id == artist_id).count()

        # Same number of distinct anomalies — additional data may have updated
        # values in place, but no new rows created for already-firing rules.
        assert second_count == first_count, (
            f"adding new data must update existing anomaly rows, not create duplicates "
            f"(first={first_count}, second={second_count})"
        )
    finally:
        db.close()
