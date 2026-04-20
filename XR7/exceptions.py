"""Custom exceptions for XR7 Engine."""


class TenantIsolationViolation(Exception):
    """Raised when a tenant isolation boundary is violated."""
    
    pass


class XR7Exception(Exception):
    """Base exception for all XR7 errors."""
    
    pass


class ValidationError(XR7Exception):
    """Raised when input validation fails."""
    
    pass


class NotFoundError(XR7Exception):
    """Raised when a resource is not found."""
    
    pass


class AuthenticationError(XR7Exception):
    """Raised when authentication fails."""
    
    pass


class AuthorizationError(XR7Exception):
    """Raised when authorization fails."""
    
    pass
