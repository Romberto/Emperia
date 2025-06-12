from fastapi.testclient import TestClient

from fast_application.core.config import settings
from fast_application.main import app_main

client = TestClient(app_main)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

import pytest
import hashlib
import hmac
import os

# Функция из вашего кода
def verify_telegram_auth(data: dict, bot_token: str) -> bool:
    data = data.copy()  # чтобы не мутировать оригинал
    auth_hash = data.pop("hash")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac_hash == auth_hash

@pytest.fixture
def telegram_test_data():
    return {
        "id": 841163160,
        "first_name": "Роман",
        "last_name": "Корхов",
        "username": "RombertoK",
        "auth_date": 1749630438,
        "hash": "d2835082563e82601f3077eeea1e2fde7a1907d75281697a99324b02d75e21ad"
    }

def test_verify_telegram_auth_valid(telegram_test_data):
    bot_token = settings.bot_token  # Заменить на тот, что был использован для генерации hash
    is_valid = verify_telegram_auth(telegram_test_data, bot_token)
    assert is_valid is True

