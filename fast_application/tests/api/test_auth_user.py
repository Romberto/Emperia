from http.client import responses

import pytest


@pytest.mark.anyio
async def test_api_telegram_login(client):
    response = await client.get("/auth/")
    assert response.status_code == 200
    assert response.json() == {"message": "saccess /"}
