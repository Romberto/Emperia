# conftest.py

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.config import settings
from models.base import Base
from main import app_main
from fastapi.testclient import TestClient
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from models.db_helper import db_helper
from models.user import UserBase


# Указываем backend
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# Создаём engine и session_factory внутри фикстуры
@pytest.fixture(scope="session")
async def engine():
    if settings.run.debug != 1:
        pytest.exit("❌ Тесты можно запускать только в режиме DEBUG", returncode=1)

    engine = create_async_engine(
        str(settings.db.test_url),
        echo=False,
        poolclass=NullPool,  # ВАЖНО: без пула, чтобы избежать конфликтов loop'ов
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True)
async def override_get_db(session):
    async def _get_db_override():
        yield session

    app_main.dependency_overrides.clear()
    app_main.dependency_overrides[db_helper.session_getter] = (
        _get_db_override  # get_db — твоя depends-функция
    )
    yield
    app_main.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def init_test_data(session: AsyncSession):
    await session.execute(text("DELETE FROM users;;"))
    """Инициализация данных для тестов, создавая пользователей в тестовой базе."""
    test_data_users = [
        {"telegram_id": 23412723454, "first_name": "Testfirst1", "last_name": "Testfirst1", "username": "Testfirst1", "photo_url": "Testfirst1"},
        {"telegram_id": 2342595454, "first_name": "Testfirst2", "last_name": "Testfirst2", "username": "Testfirst2", "photo_url": "Testfirst2"},
        {"telegram_id": 2347523454, "first_name": "Testfirst3", "last_name": "Testfirst3", "username": "Testfirst3", "photo_url": "Testfirst3"},
        {"telegram_id": 234252454, "first_name": "Testfirst4", "last_name": "Testfirst4", "username": "Testfirst4", "photo_url": "Testfirst4"}
    ]

    # Добавляем пользователей в таблицу
    users = [UserBase(**data) for data in test_data_users]
    session.add_all(users)
    await session.commit()
