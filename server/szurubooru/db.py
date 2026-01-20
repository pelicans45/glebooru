"""
Database connection and session management for SQLAlchemy 2.0.

This module provides optimized connection pooling and session management
for the PostgreSQL database connection.
"""
from typing import Any

import sqlalchemy as sa
from sqlalchemy.pool import QueuePool

from szurubooru import config


def _create_engine() -> sa.Engine:
    """
    Create SQLAlchemy engine with optimized settings for PostgreSQL.

    Connection pool settings are tuned for a WSGI application with
    multiple threads serving concurrent requests.
    """
    database_url = config.config["database"]

    # SQLAlchemy 2.0 engine with optimized pooling
    engine = sa.create_engine(
        database_url,
        # Connection pooling configuration
        poolclass=QueuePool,
        pool_size=10,           # Base connections to keep open
        max_overflow=20,        # Additional connections under load
        pool_timeout=30,        # Seconds to wait for connection
        pool_recycle=1800,      # Recycle connections after 30 minutes
        pool_pre_ping=True,     # Verify connection validity before use

        # Performance settings
        echo=config.config.get("show_sql", False),

        # Use psycopg3 driver features if available
        # These options work with both psycopg2 and psycopg3
        connect_args={
            # Application name for easier debugging in pg_stat_activity
            "application_name": "szurubooru",
        },
    )

    return engine


_engine: sa.Engine = _create_engine()
_sessionmaker = sa.orm.sessionmaker(bind=_engine, autoflush=False)
session = sa.orm.scoped_session(_sessionmaker)


def get_session() -> Any:
    """Get the current thread-local session."""
    global session
    return session


def set_sesssion(new_session: Any) -> None:
    """Replace the current session (used in tests)."""
    global session
    session = new_session


def get_engine() -> sa.Engine:
    """Get the SQLAlchemy engine for direct access if needed."""
    return _engine


def dispose_engine() -> None:
    """
    Dispose of the engine and all connections.
    Call this when shutting down the application.
    """
    _engine.dispose()
