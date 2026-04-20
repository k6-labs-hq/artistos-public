"""Tests for notification service."""

from sqlalchemy.orm import Session

from XR7.models.notification_delivery_log import NotificationDeliveryLog
from XR7.models.notification_preference import NotificationPreference
from XR7.services.notification_service import (
    NotificationService,
    send_anomaly_detected_notification,
    send_claim_advanced_notification,
    send_deposit_received_notification,
    send_urgent_sol_notification,
)


def test_notification_service_creates_default_preferences(db: Session):
    """Test that service creates default preferences for new artists."""
    service = NotificationService(db)
    artist_id = "test-artist-1"

    # Send notification for artist with no preferences
    service.send_notification(
        artist_id=artist_id,
        event_key="anomaly_detected",
        title="Test",
        body="Test body",
    )

    # Verify preferences were created
    prefs = (
        db.query(NotificationPreference)
        .filter(NotificationPreference.artist_id == artist_id)
        .first()
    )
    assert prefs is not None
    assert prefs.notify_anomaly_detected is True


def test_notification_service_respects_event_preferences(db: Session):
    """Test that disabled event types are skipped."""
    artist_id = "test-artist-2"

    # Create preferences with anomaly notifications disabled
    prefs = NotificationPreference(
        artist_id=artist_id,
        notify_anomaly_detected=False,
        email="test@example.com",
    )
    db.add(prefs)
    db.commit()

    service = NotificationService(db)
    result = service.send_notification(
        artist_id=artist_id,
        event_key="anomaly_detected",
        title="Test",
        body="Test body",
    )

    # Verify notification was skipped
    assert result is False

    # Verify skip was logged
    logs = (
        db.query(NotificationDeliveryLog)
        .filter(NotificationDeliveryLog.artist_id == artist_id)
        .all()
    )
    assert len(logs) == 1
    assert logs[0].sent is False
    assert logs[0].skip_reason == "event_disabled"


def test_notification_service_respects_quiet_hours(db: Session):
    """Test that notifications during quiet hours are skipped."""
    artist_id = "test-artist-3"

    # Create preferences with quiet hours (current time will be in quiet hours)
    prefs = NotificationPreference(
        artist_id=artist_id,
        email="test@example.com",
        quiet_hours_start="00:00:00",
        quiet_hours_end="23:59:59",
    )
    db.add(prefs)
    db.commit()

    service = NotificationService(db)
    result = service.send_notification(
        artist_id=artist_id,
        event_key="anomaly_detected",
        title="Test",
        body="Test body",
    )

    # Verify notification was skipped
    assert result is False

    # Verify skip was logged
    logs = (
        db.query(NotificationDeliveryLog)
        .filter(NotificationDeliveryLog.artist_id == artist_id)
        .all()
    )
    assert len(logs) == 1
    assert logs[0].skip_reason == "quiet_hours"


def test_notification_service_logs_delivery(db: Session):
    """Test that successful deliveries are logged."""
    artist_id = "test-artist-4"

    # Create preferences with email
    prefs = NotificationPreference(
        artist_id=artist_id,
        email="test@example.com",
    )
    db.add(prefs)
    db.commit()

    service = NotificationService(db)
    result = service.send_notification(
        artist_id=artist_id,
        event_key="deposit_received",
        title="Deposit received",
        body="Your deposit has been received",
    )

    # Verify notification was sent (stub implementation returns True)
    assert result is True

    # Verify delivery was logged
    logs = (
        db.query(NotificationDeliveryLog)
        .filter(NotificationDeliveryLog.artist_id == artist_id)
        .all()
    )
    assert len(logs) == 1
    assert logs[0].sent is True
    assert logs[0].channel == "email"
    assert logs[0].recipient == "test@example.com"


def test_helper_functions(db: Session):
    """Test notification helper functions."""
    artist_id = "test-artist-5"

    # Create preferences
    prefs = NotificationPreference(
        artist_id=artist_id,
        email="test@example.com",
    )
    db.add(prefs)
    db.commit()

    # Test anomaly notification
    result = send_anomaly_detected_notification(
        db, artist_id, "anomaly-123", "P1", "Suspicious earnings pattern"
    )
    assert result is True

    # Test SOL notification
    result = send_urgent_sol_notification(db, artist_id, "claim-456", 5)
    assert result is True

    # Test deposit notification
    result = send_deposit_received_notification(db, artist_id, 1000.50, "USD")
    assert result is True

    # Test claim advanced notification
    result = send_claim_advanced_notification(db, artist_id, "claim-789", "FILED")
    assert result is True

    # Verify all were logged
    logs = (
        db.query(NotificationDeliveryLog)
        .filter(NotificationDeliveryLog.artist_id == artist_id)
        .all()
    )
    assert len(logs) == 4


def test_quiet_hours_spanning_midnight(db: Session):
    """Test quiet hours that span midnight (e.g., 22:00 - 07:00)."""
    artist_id = "test-artist-6"

    prefs = NotificationPreference(
        artist_id=artist_id,
        email="test@example.com",
        quiet_hours_start="22:00:00",
        quiet_hours_end="07:00:00",
    )
    db.add(prefs)
    db.commit()

    service = NotificationService(db)

    # Check quiet hours logic (will be in quiet hours if current time is between 22:00 and 07:00)
    is_quiet = service._is_quiet_hours(prefs)

    # Verify the function doesn't crash with midnight-spanning hours
    assert isinstance(is_quiet, bool)
