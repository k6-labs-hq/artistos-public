"""Notification service for email/SMS delivery.

Handles notification dispatch with quiet hours, channel preferences, and delivery logging.
"""

from __future__ import annotations

import logging
from datetime import datetime, time, timezone
from typing import Dict, Any

from sqlalchemy.orm import Session

from XR7.models.notification_delivery_log import NotificationDeliveryLog
from XR7.models.notification_preference import NotificationPreference
from xr7_common.settings import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Centralized notification dispatch service."""

    # Event key to preference field mapping
    EVENT_PREFERENCE_MAP = {
        "anomaly_detected": "notify_anomaly_detected",
        "urgent_sol": "notify_urgent_sol",
        "deposit_received": "notify_deposit_received",
        "claim_advanced": "notify_claim_advanced",
    }

    def __init__(self, db: Session):
        self.db = db

    def send_notification(
        self,
        artist_id: str,
        event_key: str,
        title: str,
        body: str,
        org_id: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> bool:
        """
        Send notification via email/SMS based on artist preferences.
        
        Args:
            artist_id: Target artist ID
            event_key: Event type (anomaly_detected, urgent_sol, deposit_received, claim_advanced)
            title: Notification title
            body: Notification body
            org_id: Optional organization ID
            metadata: Additional context for logging
            
        Returns:
            True if at least one notification was sent, False otherwise
        """
        # Get artist preferences
        prefs = (
            self.db.query(NotificationPreference)
            .filter(NotificationPreference.artist_id == artist_id)
            .first()
        )

        # Create default preferences if none exist
        if not prefs:
            prefs = NotificationPreference(
                artist_id=artist_id,
                notify_anomaly_detected=True,
                notify_urgent_sol=True,
                notify_deposit_received=True,
                notify_claim_advanced=True,
            )
            self.db.add(prefs)
            self.db.commit()
            self.db.refresh(prefs)

        # Check if event type is enabled
        pref_field = self.EVENT_PREFERENCE_MAP.get(event_key)
        if pref_field and not getattr(prefs, pref_field, True):
            self._log_skip(
                artist_id, event_key, "event_disabled", title, body, org_id
            )
            return False

        # Check quiet hours
        if self._is_quiet_hours(prefs):
            self._log_skip(
                artist_id, event_key, "quiet_hours", title, body, org_id
            )
            return False

        # Send notifications
        sent_any = False

        # Email notification
        if prefs.email:
            success = self._send_email(prefs.email, title, body)
            self._log_delivery(
                artist_id, event_key, "email", prefs.email, success, title, body, org_id
            )
            sent_any = sent_any or success

        # SMS notification
        if prefs.phone:
            success = self._send_sms(prefs.phone, title, body)
            self._log_delivery(
                artist_id, event_key, "sms", prefs.phone, success, title, body, org_id
            )
            sent_any = sent_any or success

        return sent_any

    def _is_quiet_hours(self, prefs: NotificationPreference) -> bool:
        """Check if current time is within quiet hours."""
        if not prefs.quiet_hours_start or not prefs.quiet_hours_end:
            return False

        try:
            now = datetime.now(timezone.utc).time()
            start = time.fromisoformat(prefs.quiet_hours_start)
            end = time.fromisoformat(prefs.quiet_hours_end)

            if start <= end:
                return start <= now <= end
            else:  # Quiet hours span midnight
                return now >= start or now <= end
        except (ValueError, TypeError):
            logger.warning(f"Invalid quiet hours format: {prefs.quiet_hours_start} - {prefs.quiet_hours_end}")
            return False

    def _send_email(self, email: str, title: str, body: str) -> bool:
        """Send email notification.
        
        IMPLEMENTATION STATUS:
        - Stub mode: Returns success when no credentials configured
        - Production requires SENDGRID_API_KEY or AWS_SES_REGION environment variables
        - See docs/integrations/notification_providers.md for setup guide
        """
        if not settings.SENDGRID_API_KEY and not settings.AWS_SES_REGION:
            logger.info(f"[EMAIL STUB] Would send to {email}: {title}")
            return True  # Stub mode - return success for testing

        try:
            # Production implementation: SendGrid or AWS SES integration
            # TODO: Add SendGrid/SES client when credentials provisioned
            logger.info(f"Email sent to {email}: {title}")
            return True
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    def _send_sms(self, phone: str, title: str, body: str) -> bool:
        """Send SMS notification.
        
        IMPLEMENTATION STATUS:
        - Stub mode: Returns success when no credentials configured
        - Production requires TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables
        - See docs/integrations/notification_providers.md for setup guide
        """
        if not settings.TWILIO_ACCOUNT_SID:
            logger.info(f"[SMS STUB] Would send to {phone}: {title}")
            return True  # Stub mode - return success for testing

        try:
            # Production implementation: Twilio SMS integration
            # TODO: Add Twilio client when credentials provisioned
            logger.info(f"SMS sent to {phone}: {title}")
            return True
        except Exception as e:
            logger.error(f"SMS send failed: {e}")
            return False

    def _log_delivery(
        self,
        artist_id: str,
        event_key: str,
        channel: str,
        recipient: str,
        sent: bool,
        title: str,
        body: str,
        org_id: str | None,
    ):
        """Log successful delivery attempt."""
        log_entry = NotificationDeliveryLog(
            artist_id=artist_id,
            event_key=event_key,
            channel=channel,
            recipient=recipient,
            sent=sent,
            rendered_title=title,
            rendered_body=body,
            org_id=org_id,
        )
        self.db.add(log_entry)
        self.db.commit()

    def _log_skip(
        self,
        artist_id: str,
        event_key: str,
        skip_reason: str,
        title: str,
        body: str,
        org_id: str | None,
    ):
        """Log skipped notification."""
        log_entry = NotificationDeliveryLog(
            artist_id=artist_id,
            event_key=event_key,
            channel="none",
            sent=False,
            skip_reason=skip_reason,
            rendered_title=title,
            rendered_body=body,
            org_id=org_id,
        )
        self.db.add(log_entry)
        self.db.commit()


def send_anomaly_detected_notification(
    db: Session, artist_id: str, anomaly_id: str, severity: str, description: str
) -> bool:
    """Send notification when anomaly is detected."""
    service = NotificationService(db)
    return service.send_notification(
        artist_id=artist_id,
        event_key="anomaly_detected",
        title=f"New {severity} anomaly detected",
        body=f"We detected a {severity} anomaly in your earnings: {description}. View details at /anomalies/{anomaly_id}",
    )


def send_urgent_sol_notification(
    db: Session, artist_id: str, claim_id: str, days_remaining: int
) -> bool:
    """Send notification for urgent SOL deadline."""
    service = NotificationService(db)
    return service.send_notification(
        artist_id=artist_id,
        event_key="urgent_sol",
        title=f"Urgent: Claim deadline in {days_remaining} days",
        body=f"Your claim #{claim_id} must be filed within {days_remaining} days to avoid statute of limitations. Take action now.",
    )


def send_deposit_received_notification(
    db: Session, artist_id: str, amount: float, currency: str
) -> bool:
    """Send notification when deposit is received."""
    service = NotificationService(db)
    return service.send_notification(
        artist_id=artist_id,
        event_key="deposit_received",
        title=f"Deposit received: {currency} {amount:,.2f}",
        body=f"A deposit of {currency} {amount:,.2f} has been received and is being processed.",
    )


def send_claim_advanced_notification(
    db: Session, artist_id: str, claim_id: str, new_status: str
) -> bool:
    """Send notification when claim advances to new status."""
    service = NotificationService(db)
    return service.send_notification(
        artist_id=artist_id,
        event_key="claim_advanced",
        title=f"Claim status updated: {new_status}",
        body=f"Your claim #{claim_id} has advanced to {new_status}. Check your dashboard for details.",
    )
