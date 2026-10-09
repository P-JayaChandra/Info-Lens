import os
import shutil
import tempfile
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.database.base import Base
from app.main import create_application


@pytest.fixture(scope="session")
def test_temp_dir() -> Generator[str, None, None]:
    temp_dir = tempfile.mkdtemp(prefix="doc_intel_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def test_settings(test_temp_dir: str) -> Settings:
    settings = Settings(
        ENVIRONMENT="testing",
        DEBUG=True,
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        DATABASE_SYNC_URL="sqlite:///:memory:",
        LOCAL_STORAGE_PATH=os.path.join(test_temp_dir, "storage"),
        SECRET_KEY="test-secret-key-for-unit-and-integration-testing-only",
        ACCESS_TOKEN_EXPIRE_MINUTES=5,
        REFRESH_TOKEN_EXPIRE_DAYS=1,
    )
    return settings


@pytest_asyncio.fixture
async def async_test_engine(test_settings: Settings):
    engine = create_async_engine(
        test_settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_test_session(async_test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(
        bind=async_test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
def sync_test_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    application = create_application()
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
