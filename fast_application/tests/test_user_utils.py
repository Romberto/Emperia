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
                "id": 2312723454,
                "first_name": "Testfirst1",
                "last_name": "Testfirst1",
                "username": "Testfirst1",
                "photo_url": "Testfirst1",
            },
            not_raise(),
        ),
        (
            {
                "id": 2312723454,
                "first_name": "Testfirst1",
                "last_name": "Testfirst1",
                "username": "Testfirst1",
                "photo_url": "Testfirst1",
            },
            pytest.raises(HTTPException),
        ),  # добавляет дубль
        (
            {
                "id": "34ew53453",
                "first_name": "Testfirst1",
                "last_name": "Testfirst1",
                "username": "Testfirst1",
                "photo_url": "Testfirst1",
            },
            pytest.raises(ValidationError),
        ),
        ({"id": 0}, not_raise()),
        ({"id": -1}, not_raise()),
        ({"id": 2**63 - 1}, not_raise()),
        ({"id": 2**63}, pytest.raises(HTTPException)),
        ({"id": None}, pytest.raises(ValidationError)),
        ({"id": "abc"}, pytest.raises(ValidationError)),
        ({"id": 9999, "first_name": "A" * 255}, not_raise()),
        ({"id": 9999, "first_name": "A" * 256}, pytest.raises(HTTPException)),
        ({"id": 10000, "photo_url": "a" * 5000}, not_raise()),
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
        assert user.telegram_id == payload.get("id")
        assert total_count == new_total_count - 1


from contextlib import nullcontext

import pytest
import hashlib
import hmac

from typing import Dict
from contextlib import nullcontext as raise_not_det

from api.v1.auth_user import verify_telegram_auth
from core.config import settings

BOT_TOKEN = "settings.bot.bot_token"  # Убедись, что токен твой


# Функция для генерации хеша для проверки
def generate_telegram_data(data: Dict) -> Dict:

    # Генерация строки для хеширования
    check_data = {k: str(v) for k, v in data.items() if v is not None and k != "hash"}
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(check_data.items()))

    # Генерация хеша
    secret_key = hashlib.sha256(BOT_TOKEN.encode("utf-8")).digest()
    hmac_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # Добавляем хеш в данные
    data["hash"] = hmac_hash
    return data


# Параметризованный тест
@pytest.mark.parametrize(
    "input_data, expected_result, exc",
    [
        # Валидный набор данных (должен вернуться True)
        (
            generate_telegram_data(
                {
                    "id": 849160560,
                    "first_name": "Роман",
                    "last_name": "Корхов",
                    "username": "RomrtoK",
                    "auth_date": 1733354326,
                }
            ),
            True,
            raise_not_det(),
        ),
        # Невалидный набор данных (должен вернуться False)
        (
            generate_telegram_data(
                {
                    "id": 841163160,
                    "first_name": "Роман",
                    "last_name": "Корхов",
                    "username": "RombertoK",
                    "auth_date": 1753364326,
                }
            ).update({"hash": "incorrect_hash"}),
            False,
            pytest.raises(AttributeError),
        ),
        # Отсутствует поле "hash" (должен вернуться False)
        (
            {
                "id": 841163160,
                "first_name": "Роман",
                "last_name": "Корхов",
                "username": "RombertoK",
                "auth_date": 1753364326,
            },
            False,
            raise_not_det(),
        ),
    ],
)
def test_verify_telegram_auth(input_data, expected_result, exc):
    with exc:
        assert verify_telegram_auth(input_data, BOT_TOKEN) == expected_result
