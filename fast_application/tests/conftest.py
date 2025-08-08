# conftest.py

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from api.crud.jwt_utils import (
    _get_payload_refresh_token,
    _get_current_payload,
    Token,
    encode_jwt,
)
from core.config import settings
from models.base import Base
from main import app_main
from fastapi.testclient import TestClient
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from models.db_helper import db_helper
from models.user import UserBase
from httpx import AsyncClient, ASGITransport

from shcemes.auth_sheams import Role


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
async def override_dependencies_refresh(session):
    async def _get_db_override():
        yield session

    async def _get_payload_override():
        return {
            "sub": "fake-user-id",
            "first_name": "Fake",
            "telegram_id": 123456789,
        }

    app_main.dependency_overrides.clear()
    app_main.dependency_overrides[db_helper.session_getter] = _get_db_override
    app_main.dependency_overrides[_get_payload_refresh_token] = _get_payload_override

    yield

    app_main.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def override_dependencies(session):
    async def _get_db_override():
        yield session

    app_main.dependency_overrides.clear()
    app_main.dependency_overrides[db_helper.session_getter] = _get_db_override

    yield

    app_main.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def override_current_payload():
    async def _override():
        return {
            "sub": "test-user-id",
            "first_name": "John",
            "telegram_id": 123456789,
            "token_type": "access",
        }

    app_main.dependency_overrides[_get_current_payload] = _override
    yield
    app_main.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def init_test_data(session: AsyncSession):
    await session.execute(text("DELETE FROM users;;"))
    """Инициализация данных для тестов, создавая пользователей в тестовой базе."""
    test_data_users = [
        {
            "telegram_id": 23412723454,
            "first_name": "Testfirst1",
            "last_name": "Testfirst1",
            "username": "Testfirst1",
            "photo_url": "Testfirst1",
        },
        {
            "telegram_id": 2342595454,
            "first_name": "Testfirst2",
            "last_name": "Testfirst2",
            "username": "Testfirst2",
            "photo_url": "Testfirst2",
        },
        {
            "telegram_id": 2347523454,
            "first_name": "Testfirst3",
            "last_name": "Testfirst3",
            "username": "Testfirst3",
            "photo_url": "Testfirst3",
        },
        {
            "telegram_id": 234252454,
            "first_name": "Testfirst4",
            "last_name": "Testfirst4",
            "username": "Testfirst4",
            "photo_url": "Testfirst4",
        },
    ]

    # Добавляем пользователей в таблицу
    users = [UserBase(**data) for data in test_data_users]
    session.add_all(users)
    await session.commit()


BASE_URL_DISH = "http://test/api/v1"


@pytest.fixture()
async def client():
    async with AsyncClient(
        transport=ASGITransport(app_main), base_url=BASE_URL_DISH
    ) as ac:
        yield ac


@pytest.fixture()
async def generate_test_access_token(session):
    user = UserBase(telegram_id=234234231, first_name="@testUser")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    payload = {
        "sub": str(user.id),
        "first_name": user.first_name,
        "telegram_id": user.telegram_id,
        Token.field: Token.access,  # важно!
        "role": Role.user,
    }
    yield encode_jwt(
        payload=payload,
        token_type=Token.access,
        private_key=settings.auth_jwt.private_key_path.read_text(),
        algorithm=settings.auth_jwt.algorithm,
        expire_minutes=15,
    )

    await session.delete(user)
    await session.commit()


@pytest.fixture()
async def generate_test_access_token_is_admin(session):
    user = UserBase(telegram_id=234234231, first_name="@testUser")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    payload = {
        "sub": str(user.id),
        "first_name": user.first_name,
        "telegram_id": user.telegram_id,
        Token.field: Token.access,  # важно!
        "role": Role.admin,
    }
    yield encode_jwt(
        payload=payload,
        token_type=Token.access,
        private_key=settings.auth_jwt.private_key_path.read_text(),
        algorithm=settings.auth_jwt.algorithm,
        expire_minutes=15,
    )

    await session.delete(user)
    await session.commit()
