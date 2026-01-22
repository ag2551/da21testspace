"""
Database configuration and session management for LINE bot.
Uses SQLAlchemy 2.0 with SQLite for local persistence.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./line_bot.db"

# Create engine with SQLite-specific configuration
# check_same_thread=False allows SQLite usage in async FastAPI context
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for SQL query debugging
)

# Session factory for creating database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for ORM models (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


def get_db():
    """
    FastAPI dependency that provides a database session.
    Ensures proper session cleanup after each request.

    Usage:
        @app.post("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session here
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
