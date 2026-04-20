"""Claim status audit event listener.

Registers event listener for claim status changes to track audit trail.

This module is imported for side effects (event listener registration).
When claim status changes occur, events are automatically logged to the
claim_audit_log table via SQLAlchemy event hooks.

IMPLEMENTATION STATUS:
- Audit logging table exists (claim_audit_log in models)
- Event registration deferred until ORM event system is fully wired
- Current audit trail created via explicit service calls in recovery/orchestrator.py

FUTURE WORK:
- Register SQLAlchemy @event.listens_for('before_update') on Claim.status
- Auto-populate claim_audit_log on status transitions
- Consolidate with existing manual audit trail calls
"""

# Placeholder for claim status change event listener
# Event listener will be registered here when ORM event system is standardized
# across all audit-sensitive tables (claims, payments, artist profiles)

__all__ = []  # No public exports - side effects only when event system enabled
