from fastapi.exceptions import HTTPException
import uuid
import pytest
from pydantic_core._pydantic_core import ValidationError
from sqlalchemy import select
from sqlalchemy.sql.functions import func
from contextlib import nullcontext as not_raise
from api.crud.user_utils import _get_current_user, _get_all_user, add_user_to_db
from models.user import UserBase
from shcemes.auth_sheams import UserCreate


async def test__get_current_user(session, init_test_data):
    stmt = select(UserBase)
    result = await session.scalars(stmt)
    user = result.first()
    payload = {"sub": user.id}
    current_user = await _get_current_user(session, payload)
    assert user.telegram_id == current_user.telegram_id


@pytest.mark.parametrize(
    "payload, exc ",
    (
        ({"sub": "1231123123"}, pytest.raises(HTTPException)),  # не валидный id
        ({"sub": 231323431}, pytest.raises(HTTPException)),  # не валидный id
        (
            {"sub": uuid.uuid4()},
            pytest.raises(HTTPException),
        ),  # не существующий пользователь
    ),
)
async def test__get_current_user_invalid_id(session, init_test_data, payload, exc):
    with exc:
        await _get_current_user(session, payload)


async def test_get_all_user(session, init_test_data):
    stmt = select(func.count()).select_from(UserBase)
    result = await session.execute(stmt)
    total_count = result.scalar()
    users = await _get_all_user(session)
    assert len(users) == total_count


@pytest.mark.parametrize(
    "payload, exc",
    (
        (
            {
                "telegram_id": 2312723454,
                "first_name": "Testfirst1",
                "last_name": "Testfirst1",
                "username": "Testfirst1",
                "photo_url": "Testfirst1",
            },
            not_raise(),
        ),
        (
            {
                "telegram_id": 2312723454,
                "first_name": "Testfirst1",
                "last_name": "Testfirst1",
                "username": "Testfirst1",
                "photo_url": "Testfirst1",
            },
            pytest.raises(HTTPException),
        ),  # добавляет дубль
        (
            {
                "telegram_id": "34ew53453",
                "first_name": "Testfirst1",
                "last_name": "Testfirst1",
                "username": "Testfirst1",
                "photo_url": "Testfirst1",
            },
            pytest.raises(ValidationError),
        ),
        ({"telegram_id": 0}, not_raise()),
        ({"telegram_id": -1}, not_raise()),
        ({"telegram_id": 2**63 - 1}, not_raise()),
        ({"telegram_id": 2**63}, pytest.raises(HTTPException)),
        ({"telegram_id": None}, pytest.raises(ValidationError)),
        ({"telegram_id": "abc"}, pytest.raises(ValidationError)),
        ({"telegram_id": 9999, "first_name": "A" * 255}, not_raise()),
        ({"telegram_id": 9999, "first_name": "A" * 256}, pytest.raises(HTTPException)),
        ({"telegram_id": 10000, "photo_url": "a" * 5000}, not_raise()),
    ),
)
async def test_add_user_to_db(session, payload, exc):
    stmt = select(func.count()).select_from(UserBase)
    result = await session.execute(stmt)
    total_count = result.scalar()
    with exc:
        user_data = UserCreate(**payload)
        user = await add_user_to_db(session, user_data)
        stmt = select(func.count()).select_from(UserBase)
        result = await session.execute(stmt)
        new_total_count = result.scalar()
        assert user.telegram_id == payload.get("telegram_id")
        assert total_count == new_total_count - 1
