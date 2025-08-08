from types import SimpleNamespace


import pytest

from sqlalchemy import select, exists
from sqlalchemy.sql.functions import func

from models.user import UserBase


@pytest.mark.anyio
async def test_test(client):
    response = await client.get("/auth/")
    assert response.status_code == 200
    assert response.json() == {"message": "saccess /"}


import pytest
from unittest.mock import patch
from httpx import AsyncClient
from contextlib import nullcontext as does_not_raise


@pytest.mark.parametrize(
    "payload, verify_return, expected_status, expected_keys",
    [
        # Новый пользователь
        (
            {
                "id": 1001,
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "auth_date": 1722070500,
                "hash": "validhash",
            },
            True,
            200,
            {"access_token", "refresh_token"},
        ),
        # Существующий пользователь
        (
            {
                "id": 1001,
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "auth_date": 1722070500,
                "hash": "validhash",
            },
            True,
            200,
            {"access_token", "refresh_token"},
        ),
        # Отсутствует hash → ошибка валидации
        (
            {
                "id": 1003,
                "auth_date": 1722070500,
            },
            True,
            422,
            set(),
        ),
        # verify возвращает False
        (
            {
                "id": 100432,
                "first_name": "Jane",
                "auth_date": 1722070500,
                "hash": "invalidhash",
            },
            False,
            401,
            set(),
        ),
    ],
)
@patch("api.v1.auth.auth_user.verify_telegram_auth")
async def test_api_telegram_login(
    verify_telegram_mock,
    client: AsyncClient,
    payload,
    verify_return,
    expected_status,
    expected_keys,
    session,
):
    verify_telegram_mock.return_value = verify_return

    stmt = select(func.count()).select_from(UserBase)
    result = await session.execute(stmt)
    count_start = result.scalar()

    stmt = select(exists().where(UserBase.telegram_id == payload["id"]))
    result = await session.execute(stmt)
    user_exists = result.scalar()

    response = await client.post("/auth/telegram/login", json=payload)

    assert response.status_code == expected_status

    stmt = select(func.count()).select_from(UserBase)
    result = await session.execute(stmt)
    count_after_add = result.scalar()

    if expected_status == 200 and not user_exists:
        assert count_start != count_after_add
    else:
        assert count_start == count_after_add

    data = response.json()
    if expected_status == 200:
        assert expected_keys.issubset(data.keys())
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
    else:
        assert not expected_keys.intersection(data.keys())


@pytest.mark.parametrize(
    "payload",
    [
        {
            "sub": "UUIDtoken",
            "first_name": "firstName",
            "telegram_id": 1234567890,
        }
    ],
)
@patch("api.v1.auth.auth_user._get_current_user")
async def test_refresh_token(user_mock, client: AsyncClient, payload):
    user_mock.return_value = SimpleNamespace(
        id="user-id-123", first_name="Test", telegram_id=123456789
    )

    response = await client.post("/auth/telegram/refresh")
    data = response.json()
    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "Bearer"
