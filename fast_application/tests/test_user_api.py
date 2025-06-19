import sys
import os
import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# --- Start Comprehensive Mocking of settings ---
mock_settings_object = MagicMock()
mock_settings_object.db.url = "sqlite+aiosqlite:///:memory:"
mock_settings_object.db.echo = False
mock_settings_object.db.echo_pool = False
mock_settings_object.db.max_overflow = 10
mock_settings_object.db.pool_size = 15
mock_settings_object.bot_token = "dummy_bot_token_for_user_api_tests"
mock_settings_object.api.prefix = "/api"      # Global API prefix from api_router in api.__init__.py
mock_settings_object.api.v1.prefix = "/v1"    # Prefix for v1 router

private_key_path = Path(os.path.join(os.path.dirname(__file__), "private_key.pem"))
public_key_path = Path(os.path.join(os.path.dirname(__file__), "public_key.pem"))
if not private_key_path.exists(): private_key_path.touch()
if not public_key_path.exists(): public_key_path.touch()

mock_settings_object.auth_jwt.private_key_path = private_key_path
mock_settings_object.auth_jwt.public_key_path = public_key_path
mock_settings_object.auth_jwt.algorithm = "RS256"
mock_settings_object.auth_jwt.access_token_expire_minutes = 15
mock_settings_object.auth_jwt.refresh_token_expire_days = 7
mock_settings_object.auth_jwt.secret_key = "test-secret-key"

mock_config_module = MagicMock()
mock_config_module.settings = mock_settings_object
sys.modules['fast_application.core.config'] = mock_config_module
sys.modules['core.config'] = mock_config_module
sys.modules['core'] = MagicMock(config=mock_config_module)
# --- End Comprehensive Mocking of settings ---

from fast_application.main import app_main as app
from fast_application.models.user import UserBase
from fast_application.api.crud.jwt_utils import _get_current_payload as get_current_payload_dependency
# For user_utils, we will mock them where they are used (in fast_application.api.v1.user)
# from fast_application.api.crud.user_utils import _get_current_user, _get_all_user
from fast_application.models.db_helper import db_helper
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


# Fixtures
@pytest_asyncio.fixture(scope="function")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_db_session_tuple():
    session_mock = AsyncMock(spec=AsyncSession)
    scalar_results_mock = MagicMock() # Represents AsyncScalarResult; its methods like .first() are sync.

    execute_result_mock = MagicMock() # Represents AsyncResult
    execute_result_mock.scalars.return_value = scalar_results_mock
    session_mock.execute = AsyncMock(return_value=execute_result_mock)

    session_mock.add = MagicMock()
    session_mock.commit = AsyncMock()
    session_mock.refresh = AsyncMock(return_value=None) # Typically returns None, modifies in-place
    return session_mock, scalar_results_mock

@pytest.fixture
def mock_user_payload(): # Corresponds to JWT payload
    return {'sub': 123, 'first_name': 'TestyFromToken', 'telegram_id': 12345, 'token_type': 'access'}

@pytest.fixture
def mock_user_data_for_read_model(): # Data that _get_current_user would return (dict form)
    return {
        "id": 123,
        "telegram_id": 12345,
        "first_name": "TestyFromDB", # Name might differ from token, DB is source of truth
        "username": "testy_mcuser",
        "photo_url": "http://example.com/photo.jpg",
        "last_name": None
        # UserRead does not include is_active, is_superuser, etc.
    }


class TestUserApi:
    @pytest.mark.asyncio
    async def test_get_user_me_success(self, client: AsyncClient, mocker, mock_db_session_tuple, mock_user_payload, mock_user_data_for_read_model):
        mock_session, _ = mock_db_session_tuple

        # Define override functions for dependencies
        async def override_get_current_payload():
            return mock_user_payload

        # _get_current_user is imported in fast_application.api.v1.user
        # Mock it to return a dictionary that matches the UserRead schema fields
        mocked_get_user_util = mocker.patch('fast_application.api.v1.user._get_current_user', return_value=mock_user_data_for_read_model)

        async def override_get_db_session():
            yield mock_session

        # Apply overrides
        app.dependency_overrides[get_current_payload_dependency] = override_get_current_payload
        app.dependency_overrides[db_helper.session_getter] = override_get_db_session

        response = await client.get("/api/v1/user/me", headers={"Authorization": "Bearer testtoken"})

        assert response.status_code == 200
        data = response.json()
        # Assert against the data returned by the mocked _get_current_user, which should be UserRead compatible
        assert data['id'] == mock_user_data_for_read_model['id']
        assert data['first_name'] == mock_user_data_for_read_model['first_name']
        assert data['telegram_id'] == mock_user_data_for_read_model['telegram_id']
        assert data['username'] == mock_user_data_for_read_model['username']

        mocked_get_user_util.assert_called_once_with(session=mock_session, payload=mock_user_payload)

        # Cleanup overrides
        del app.dependency_overrides[get_current_payload_dependency]
        del app.dependency_overrides[db_helper.session_getter]

    @pytest.mark.asyncio
    async def test_get_user_me_unauthorized(self, client: AsyncClient, mocker):
        async def override_get_current_payload_raises_unauth():
            raise HTTPException(status_code=401, detail="Not authenticated by mock")

        app.dependency_overrides[get_current_payload_dependency] = override_get_current_payload_raises_unauth

        response = await client.get("/api/v1/user/me", headers={"Authorization": "Bearer invalidtoken"})

        assert response.status_code == 401
        assert response.json()['detail'] == "Not authenticated by mock"

        del app.dependency_overrides[get_current_payload_dependency]

    @pytest.mark.asyncio
    async def test_get_user_me_user_not_found(self, client: AsyncClient, mocker, mock_db_session_tuple, mock_user_payload):
        mock_session, _ = mock_db_session_tuple

        async def override_get_current_payload():
            return mock_user_payload

        # Mock _get_current_user to raise HTTPException(404)
        mocked_get_user_util = mocker.patch(
            'fast_application.api.v1.user._get_current_user',
            side_effect=HTTPException(status_code=404, detail="User not found by mock")
        )

        async def override_get_db_session():
            yield mock_session

        app.dependency_overrides[get_current_payload_dependency] = override_get_current_payload
        app.dependency_overrides[db_helper.session_getter] = override_get_db_session

        response = await client.get("/api/v1/user/me", headers={"Authorization": "Bearer testtoken"})

        assert response.status_code == 404
        assert response.json()['detail'] == "User not found by mock"

        mocked_get_user_util.assert_called_once_with(session=mock_session, payload=mock_user_payload)

        del app.dependency_overrides[get_current_payload_dependency]
        del app.dependency_overrides[db_helper.session_getter]

    @pytest.mark.asyncio
    async def test_get_all_users_success(self, client: AsyncClient, mocker, mock_db_session_tuple, mock_user_payload, mock_user_data_for_read_model):
        mock_session, _ = mock_db_session_tuple

        # Prepare a list of user data dicts (UserRead compatible)
        user1_data = mock_user_data_for_read_model
        user2_data = {**user1_data, "id": 124, "telegram_id": 12346, "username": "anotheruser"}
        list_of_mock_users_data = [user1_data, user2_data]

        # Define override functions for dependencies
        async def override_get_current_payload():
            return mock_user_payload

        # Mock _get_all_user from where it's used in fast_application.api.v1.user
        mocked_get_all_users_util = mocker.patch(
            'fast_application.api.v1.user._get_all_user',
            return_value=list_of_mock_users_data
        )

        async def override_get_db_session():
            yield mock_session

        # Apply overrides
        app.dependency_overrides[get_current_payload_dependency] = override_get_current_payload
        app.dependency_overrides[db_helper.session_getter] = override_get_db_session

        response = await client.get("/api/v1/user/all", headers={"Authorization": "Bearer testtoken"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(list_of_mock_users_data)
        assert data[0]['id'] == user1_data['id']
        assert data[1]['id'] == user2_data['id']
        assert data[0]['first_name'] == user1_data['first_name']
        assert data[1]['username'] == user2_data['username']

        mocked_get_all_users_util.assert_called_once_with(session=mock_session, payload=mock_user_payload)

        # Cleanup overrides
        del app.dependency_overrides[get_current_payload_dependency]
        del app.dependency_overrides[db_helper.session_getter]


    @pytest.mark.asyncio
    async def test_get_all_users_unauthorized(self, client: AsyncClient, mocker):
        async def override_get_current_payload_raises_unauth():
            raise HTTPException(status_code=401, detail="Not authorized for all users")

        app.dependency_overrides[get_current_payload_dependency] = override_get_current_payload_raises_unauth

        response = await client.get("/api/v1/user/all", headers={"Authorization": "Bearer invalidtoken"})

        assert response.status_code == 401
        assert response.json()['detail'] == "Not authorized for all users"

        del app.dependency_overrides[get_current_payload_dependency]
