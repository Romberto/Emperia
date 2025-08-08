from httpx import AsyncClient
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.functions import func
from starlette import status

from models.user import UserBase


async def test_admin_panel(client: AsyncClient, generate_test_access_token_is_admin):
    token = generate_test_access_token_is_admin
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("admin/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"models": ["UserBase"]}


async def test_admin_panel_not_role_is_admin(
    client: AsyncClient, generate_test_access_token
):
    token = generate_test_access_token
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("admin/", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_get_rows_tablenames_not_role_is_admin(
    client: AsyncClient, generate_test_access_token
):
    token = generate_test_access_token
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("admin/UserBase", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


async def test_get_rows_tablenames(
    init_test_data,
    session: AsyncSession,
    client: AsyncClient,
    generate_test_access_token_is_admin,
):
    token = generate_test_access_token_is_admin
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("admin/UserBase", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data["data"]) == 10
    total_stmt = select(func.count()).select_from(UserBase)
    total_result = await session.execute(total_stmt)
    expected_total = total_result.scalar_one()
    assert response_data["total"] == expected_total
