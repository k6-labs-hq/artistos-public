"""
Security Headers Middleware for XR7 Engine.

Implements OWASP security headers to protect against common web vulnerabilities:
- HSTS: Force HTTPS, prevent MITM attacks
- CSP: Content Security Policy to prevent XSS
- X-Frame-Options: Prevent clickjacking
- X-Content-Type-Options: Prevent MIME sniffing
- Referrer-Policy: Control referrer information
- Permissions-Policy: Control browser features

Documented in docs/security_hardening_plan.md
"""

from __future__ import annotations

import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all HTTP responses.

    Production requirements:
    - HSTS with 1-year max-age
    - Strict CSP (default-src 'self')
    - Frame denial (X-Frame-Options: DENY)
    - MIME type enforcement (X-Content-Type-Options: nosniff)

    Configurable via environment variables:
    - XR7_CSP_POLICY: Override default CSP (default: "default-src 'self'")
    - XR7_FRAME_OPTIONS: Override X-Frame-Options (default: "DENY")
    """

    def __init__(self, app, **kwargs):
        super().__init__(app)
        self.csp_policy = os.environ.get("XR7_CSP_POLICY", "default-src 'self'")
        self.frame_options = os.environ.get("XR7_FRAME_OPTIONS", "DENY")

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # HSTS: Force HTTPS for 1 year, include subdomains
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Clickjacking protection
        response.headers["X-Frame-Options"] = self.frame_options

        # Legacy XSS protection (modern browsers use CSP)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = self.csp_policy

        # Referrer policy: only send origin for cross-origin requests
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy: disable camera, microphone, geolocation
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        return response
