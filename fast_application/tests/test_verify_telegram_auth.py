from contextlib import nullcontext

import pytest
import hashlib
import hmac

from typing import Dict
from contextlib import nullcontext as raise_not_det

from api.v1.auth_user import verify_telegram_auth
from core.config import settings


# Функция для генерации хеша для проверки
def generate_telegram_data(data: Dict) -> Dict:
    BOT_TOKEN = settings.bot.bot_token  # Убедись, что токен твой

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
        assert verify_telegram_auth(input_data) == expected_result
