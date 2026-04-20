"""Re-export of the canonical get_db dependency from XR7.models.base."""

from XR7.models.base import SessionLocal, engine, get_db

__all__ = ["SessionLocal", "engine", "get_db"]
