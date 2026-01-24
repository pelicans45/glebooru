"""
Database connection and session management for SQLAlchemy 2.0.

This module provides optimized connection pooling and session management
for the PostgreSQL database connection.
"""
from typing import Any

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.pool import QueuePool

from szurubooru import config


def _create_engine() -> sa.Engine:
    """
    Create SQLAlchemy engine with optimized settings for PostgreSQL.

    Connection pool settings are tuned for Granian WSGI with multiple
    worker processes. Each worker gets its own connection pool.

    For a 2 vCPU / 2GB RAM server with Granian (2 workers, 4 threads):
      - pool_size=4: Base connections per worker (matches blocking-threads)
      - max_overflow=4: Burst capacity under load
      - Total max connections: 2 workers × 8 = 16 (well under PG default of 100)
    """
    database_url = config.config["database"]

    # SQLAlchemy 2.0 engine with optimized pooling
    engine = sa.create_engine(
        database_url,
        # Connection pooling configuration
        poolclass=QueuePool,
        pool_size=4,            # Base connections (match Granian blocking-threads)
        max_overflow=4,         # Burst capacity under load
        pool_timeout=15,        # Seconds to wait for connection
        pool_recycle=1800,      # Recycle connections after 30 minutes
        pool_pre_ping=True,     # Verify connection validity before use
        pool_use_lifo=True,     # Better cache locality under bursty load

        # Performance settings
        echo=config.config.get("show_sql", False),

        # psycopg3 driver options
        connect_args={
            # Application name for easier debugging in pg_stat_activity
            "application_name": "szurubooru",
        },
    )

    return engine


_engine: sa.Engine = _create_engine()
_sessionmaker = orm.sessionmaker(bind=_engine, autoflush=False)
session = orm.scoped_session(_sessionmaker)


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
