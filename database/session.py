"""
Database session configuration for SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from typing import Generator

# Get database URL from environment variable with fallback
DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://user:password@localhost:5432/linkedin_job_matcher")

# Create SQLAlchemy engine with proper configuration
engine = create_engine(
    DATABASE_URI,
    pool_pre_ping=True,  # Verify connection before using from pool
    pool_size=10,  # Default connection pool size
    max_overflow=20,  # Allow up to 20 additional connections
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true"  # SQL echo for debugging
)

# Create session factory bound to the engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ScopedSession = scoped_session(SessionLocal)

# Base class for all ORM models
Base = declarative_base()


@contextmanager
def get_db() -> Generator:
    """
    Context manager for database sessions.

    Usage:
        with get_db() as db:
            db.query(User).filter(User.id == 1).first()

    Yields:
        SQLAlchemy Session: A database session.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_current_db_session():
    """
    Get the current scoped session.

    This is useful for routing and middleware that need a consistent session.

    Returns:
        SQLAlchemy Session: The current scoped database session.
    """
    return ScopedSession()


def remove_session():
    """
    Remove the current scoped session.

    This should be called at the end of a request cycle.
    """
    ScopedSession.remove()