import hashlib
import hmac

import pytest

from api.v1 import auth_user
from api.v1.auth_user import verify_telegram_auth
from core.config import settings

BOT_TOKEN = settings.bot_token


@pytest.fixture()
def data():
    return {
        "id": 841163160, "first_name": "Роман", "last_name": "Корхов", "username": "RombertoK", "auth_date": 1751280236,
        }


def generate_hash(data: dict, token: str) -> str:
    check_data = {k: str(v) for k, v in data.items() if k != "hash" and v is not None}
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(check_data.items()))
    secret_key = hashlib.sha256(token.encode("utf-8")).digest()
    return hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()


def test_valid_hash(monkeypatch, data):
    monkeypatch.setattr(auth_user, "BOT_TOKEN", BOT_TOKEN)
    data["hash"] = generate_hash(data, BOT_TOKEN)
    assert verify_telegram_auth(data) is True


def test_invalid_hash(monkeypatch, data):
    monkeypatch.setattr(auth_user, "BOT_TOKEN", BOT_TOKEN)
    assert verify_telegram_auth(data) is False


def test_missing_hash(data):
    assert verify_telegram_auth(data) is False


def test_none_values(monkeypatch, data):
    from api.v1 import auth_user
    monkeypatch.setattr(auth_user, "BOT_TOKEN", BOT_TOKEN)
    data["hash"] = generate_hash(data, BOT_TOKEN)
    assert verify_telegram_auth(data) is True
