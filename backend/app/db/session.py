"""
db/session.py
-------------
Async SQLAlchemy engine + session factory.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# Load .env file explicitly — ensures vars are available before anything else
try:
    from dotenv import load_dotenv

    load_dotenv(override=True)
except ImportError:
    pass


def _get_database_url() -> str:
    from app.core.config import settings

    return settings.DATABASE_URL


def _get_engine():
    url = _get_database_url()
    return create_async_engine(
        url,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
    )


# Lazy engine — created on first use, not at import time
_engine = None
_AsyncSessionLocal = None


def _get_session_factory():
    global _engine, _AsyncSessionLocal
    if _engine is None:
        _engine = _get_engine()
        _AsyncSessionLocal = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _AsyncSessionLocal


async def get_db():
    """
    FastAPI dependency — yields one AsyncSession per request.
    Commits on success, rolls back on exception.
    """
    factory = _get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_all_tables() -> None:
    """Create all tables. Called at startup in main.py."""
    from app.db.models import Base

    engine = _get_engine()
    try:
        async with engine.begin() as conn:
            # Enable pgvector extension first
            await conn.execute(
                __import__("sqlalchemy").text("CREATE EXTENSION IF NOT EXISTS vector")
            )
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        print("[DB] Tables and pgvector extension ready")
    except Exception as e:
        err = str(e)
        if "connection refused" in err.lower() or "could not connect" in err.lower():
            raise RuntimeError(
                "\n[DB] Cannot connect to PostgreSQL!\n"
                "Fix: Make sure Docker is running:\n"
                "     docker start chatbot-postgres\n"
                f"     DATABASE_URL = {settings.DATABASE_URL}"
            )
        if "password" in err.lower() or "authentication" in err.lower():
            raise RuntimeError(
                "\n[DB] Wrong database password!\n"
                "Check POSTGRES_PASSWORD in docker run matches\n"
                "the password in DATABASE_URL in your .env"
            )
        raise
    finally:
        await engine.dispose()
