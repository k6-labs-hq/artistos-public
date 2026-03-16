import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from xr7_common.settings import settings

DATABASE_URL = settings.database_url


def _engine_connect_args(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}

engine = create_engine(DATABASE_URL, connect_args=_engine_connect_args(DATABASE_URL), pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models."""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
