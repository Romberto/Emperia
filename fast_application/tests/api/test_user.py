from sqlalchemy.future import select
from sqlalchemy.sql.functions import func

from models.user import UserBase


async def test_get_user(client, generate_test_access_token):
    token = generate_test_access_token
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("user/me", headers=headers)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["first_name"] == "@testUser"


async def test_get_user_not_validate_token(client, session):
    token = "invalidetoken"
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("user/me", headers=headers)
    assert response.status_code == 401


async def test_get_all_users(
    client, session, init_test_data, generate_test_access_token
):
    token = generate_test_access_token
    headers = {"Authorization": f"Bearer {token}"}
    stmt = select(func.count()).select_from(UserBase)
    result = await session.execute(stmt)
    count = result.scalar()
    response = await client.get("user/all", headers=headers)
    response_data = response.json()
    assert response.status_code == 200
    assert len(response_data) == count


async def test_get_all_users_invalide_token(client):
    token = "invalidToken"
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("user/all", headers=headers)
    assert response.status_code == 401
