from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool, StaticPool

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


def get_engine_args(url: str, is_async: bool = True) -> dict:
    """Return appropriate pool and engine configuration based on dialect."""
    args = {"echo": settings.DATABASE_ECHO}
    if "sqlite" in url:
        if ":memory:" in url or "mode=memory" in url:
            args["poolclass"] = StaticPool
            args["connect_args"] = {"check_same_thread": False}
        else:
            args["connect_args"] = {"check_same_thread": False}
    else:
        # PostgreSQL / MySQL enterprise pooling
        args["poolclass"] = QueuePool
        args["pool_size"] = settings.DATABASE_POOL_SIZE
        args["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
        args["pool_timeout"] = settings.DATABASE_POOL_TIMEOUT
        args["pool_recycle"] = settings.DATABASE_POOL_RECYCLE
        args["pool_pre_ping"] = True
    return args


# Global Async and Sync Engines
async_engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    **get_engine_args(settings.DATABASE_URL, is_async=True),
)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

sync_engine = create_engine(
    settings.DATABASE_SYNC_URL,
    **get_engine_args(settings.DATABASE_SYNC_URL, is_async=False),
)

sync_session_factory = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for obtaining an asynchronous database session."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as exc:
            await session.rollback()
            logger.error("Database session transaction rolled back due to error: %s", exc)
            raise
        finally:
            await session.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency or worker helper for obtaining a synchronous database session."""
    session = sync_session_factory()
    try:
        yield session
    except Exception as exc:
        session.rollback()
        logger.error("Sync database session rolled back due to error: %s", exc)
        raise
    finally:
        session.close()


@asynccontextmanager
async def async_transactional_session() -> AsyncGenerator[AsyncSession, None]:
    """Transactional context manager committing on success and rolling back on failure."""
    async with async_session_factory() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


@contextmanager
def sync_transactional_session() -> Generator[Session, None, None]:
    """Transactional context manager for synchronous database operations."""
    session = sync_session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def check_db_health() -> bool:
    """Execute a lightweight ping to verify database responsiveness."""
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Async database health check ping failed: %s", exc)
        return False


def check_sync_db_health() -> bool:
    """Synchronous ping to verify database responsiveness."""
    try:
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Sync database health check ping failed: %s", exc)
        return False


async def close_database_connections() -> None:
    """Gracefully terminate engine connection pools during app shutdown."""
    logger.info("Closing database engine connections...")
    await async_engine.dispose()
    sync_engine.dispose()
