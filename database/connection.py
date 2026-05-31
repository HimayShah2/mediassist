"""
MediAssist Pro — Database Connection Layer.

SQLAlchemy engine configured for SQLite with WAL mode and foreign keys.
Provides ``SessionLocal`` factory, ``init_db()`` to create tables, and
``get_session()`` context manager with commit / rollback / close.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from loguru import logger
from sqlalchemy import event as sa_event
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import settings
from models.db_models import Base


def _build_engine() -> Engine:
    """
    Create a SQLAlchemy engine for the configured SQLite database.

    - Ensures the parent directory exists.
    - Registers pragmas for WAL mode and foreign-key enforcement.
    """
    db_path = settings.mediassist_db_path
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    db_url = settings.get_db_url()
    connect_args = {"check_same_thread": False}

    # Attempt to use pysqlcipher3 if installed
    try:
        import pysqlcipher3  # noqa: F401
        
        if db_url.startswith("sqlite:///"):
            cipher_pass = settings.secret_key
            path_part = db_url[10:]
            db_url = f"sqlite+pysqlcipher://:{cipher_pass}@/{path_part}"
            logger.info("pysqlcipher3 found. Using AES-256 database encryption.")
    except ImportError:
        logger.warning("pysqlcipher3 not found. Falling back to unencrypted SQLite database.")

    engine = create_engine(
        db_url,
        echo=False,
        connect_args=connect_args,
        pool_pre_ping=True,
    )

    # Enable WAL mode and foreign keys on every new connection
    @sa_event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_conn, connection_record):  # type: ignore[no-untyped-def]
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

    logger.info("Database engine created: {}", db_url)
    return engine


# Module-level engine and session factory
engine = _build_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# ═══════════════════════════════════════════════════════════════════════════
# init_db — create all tables
# ═══════════════════════════════════════════════════════════════════════════
def init_db() -> None:
    """
    Create all tables defined in :mod:`models.db_models`.

    Safe to call multiple times — uses ``CREATE TABLE IF NOT EXISTS``.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialised")


# ═══════════════════════════════════════════════════════════════════════════
# get_session — context manager
# ═══════════════════════════════════════════════════════════════════════════
@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Yield a scoped database session with automatic commit / rollback / close.

    Usage::

        with get_session() as session:
            patient = session.query(Patient).first()
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
