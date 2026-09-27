"""CheckoutLab — SQLite database setup."""
from __future__ import annotations

import os
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from checkoutlab.app.models import Base

if os.environ.get("VERCEL"):
    DATABASE_URL = f"sqlite:///{tempfile.gettempdir()}/checkoutlab.db"
else:
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./checkoutlab.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Create all tables. Idempotent — safe to call on startup."""
    Base.metadata.create_all(bind=engine)


def get_db():  # type: ignore[return]
    """FastAPI dependency: yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
