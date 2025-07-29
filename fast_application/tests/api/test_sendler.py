from unittest.mock import patch
from uuid import uuid4
from httpx import AsyncClient

import api.v1.sendler
from models.user import UserBase


@patch("api.v1.sendler._get_current_user")
async def test_send_sos(user_mock, client: AsyncClient, generate_test_access_token):
    user_mock.return_value = UserBase(
        id=uuid4(), first_name="@rfrfrf", last_name="fvfvfvf", username="edede"
    )

    token = generate_test_access_token
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "type": "dtp",
        "latitude": 22.4343,
        "longitude": 55.4342342,
    }

    response = await client.post("send/sos", json=data, headers=headers)
    assert response.status_code == 200
