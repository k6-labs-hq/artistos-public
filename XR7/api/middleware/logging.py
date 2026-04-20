"""Logging middleware stub."""

import logging
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        return await call_next(request)

def configure_structured_logging():
    logging.basicConfig(level=logging.INFO)
