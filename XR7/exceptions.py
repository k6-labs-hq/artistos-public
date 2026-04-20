"""
XR7 Platform Exceptions

 Custom exception types for platform-wide error handling.
Compliance: SOC 2 CC6.1 - Logical access controls must be enforced with specific exceptions
"""


class TenantIsolationViolation(Exception):
    """
    Raised when a data operation attempts to cross tenant boundaries.

    This is a P0 security exception that indicates a potential data leak or
    cross-tenant contamination. Every occurrence must trigger immediate investigation.

    Compliance: SOC 2 CC6.1 - Multi-tenant data isolation enforcement
    Security: Prevents cross-tenant data exfiltration at the ORM layer
    """

    def __init__(self, message: str, context: dict | None = None):
        super().__init__(message)
        self.context = context or {}
