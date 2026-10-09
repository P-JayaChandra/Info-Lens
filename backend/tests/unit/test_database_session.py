import pytest
from sqlalchemy import text
from app.database.session import (
    async_transactional_session,
    check_db_health,
    check_sync_db_health,
    get_engine_args,
    sync_transactional_session,
)


def test_engine_args_for_sqlite():
    args = get_engine_args("sqlite:///./test.db", is_async=False)
    assert "connect_args" in args
    assert args["connect_args"]["check_same_thread"] is False


def test_engine_args_for_postgres():
    args = get_engine_args("postgresql://user:pass@localhost:5432/db", is_async=False)
    assert "pool_size" in args
    assert "max_overflow" in args
    assert args["pool_pre_ping"] is True


@pytest.mark.asyncio
async def test_async_health_check():
    # Will use the configured default engine
    result = await check_db_health()
    assert isinstance(result, bool)


def test_sync_health_check():
    result = check_sync_db_health()
    assert isinstance(result, bool)


def test_sync_transactional_session(sync_test_session):
    with sync_transactional_session() as session:
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
