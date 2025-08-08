from httpx import AsyncClient
from starlette import status


async def test_admin_panel(client: AsyncClient, generate_test_access_token_is_admin):
    token = generate_test_access_token_is_admin
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("admin/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'models': ['UserBase']}
