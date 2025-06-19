import sys
import os
import pytest
import pytest_asyncio # Import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from pathlib import Path
from httpx import AsyncClient, ASGITransport # Import ASGITransport

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# --- Start Comprehensive Mocking of settings ---
# This is crucial because importing `app` from `main` will load settings.
mock_settings_object = MagicMock()
mock_settings_object.db.url = "sqlite+aiosqlite:///:memory:"
mock_settings_object.db.echo = False
mock_settings_object.db.echo_pool = False
mock_settings_object.db.max_overflow = 10
mock_settings_object.db.pool_size = 15
mock_settings_object.bot_token = "dummy_bot_token_for_api_tests"
mock_settings_object.api.v1.prefix = "/v1"    # Prefix for v1 router (corrected)
mock_settings_object.api.prefix = "/api"      # Global API prefix from api_router in api.__init__.py
                                         # If not, requests will be made to /v1/auth...
                                         # Assuming for now the main app doesn't add a global /api prefix to this router
                                         # and the test client will hit /api/v1/... directly based on router setup.
                                         # The task states full path is /api/v1/auth...
                                         # This implies settings.api.prefix might be "/" or not used for this router by main.py
                                         # Let's assume settings.api.prefix is indeed /api as used in previous tests.

# JWT settings
# These need to exist for when jwt_utils is imported (e.g. by auth_user.py)
# The actual reading of keys might be bypassed if encode_jwt is fully mocked.
private_key_path = Path(os.path.join(os.path.dirname(__file__), "private_key.pem"))
public_key_path = Path(os.path.join(os.path.dirname(__file__), "public_key.pem"))
if not private_key_path.exists(): private_key_path.touch()
if not public_key_path.exists(): public_key_path.touch()

mock_settings_object.auth_jwt.private_key_path = private_key_path
mock_settings_object.auth_jwt.public_key_path = public_key_path
mock_settings_object.auth_jwt.algorithm = "RS256"
mock_settings_object.auth_jwt.access_token_expire_minutes = 15
mock_settings_object.auth_jwt.refresh_token_expire_days = 7
mock_settings_object.auth_jwt.secret_key = "test-secret-key" # For HS256 if ever used by mistake

mock_config_module = MagicMock()
mock_config_module.settings = mock_settings_object
sys.modules['fast_application.core.config'] = mock_config_module
sys.modules['core.config'] = mock_config_module
sys.modules['core'] = MagicMock(config=mock_config_module) # if 'from core import config'
# --- End Comprehensive Mocking of settings ---

# Now import app, AFTER settings are mocked
from fast_application.main import app_main as app # Correctly import app_main as app
from fast_application.shcemes.auth_sheams import TelegramAuthPayload
from fast_application.models.user import UserBase # For creating mock user instances
from fast_application.api.crud.jwt_utils import Token # For type hints if needed
from sqlalchemy.ext.asyncio import AsyncSession # Import for mock_db_session

# Fixture for AsyncClient
@pytest_asyncio.fixture(scope="function") # Use pytest_asyncio.fixture
async def client():
    # The base_url needs to be http://test for httpx, paths will be /api/v1/...
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# Fixture for mock AsyncSession
@pytest.fixture
def mock_db_session():
    session = AsyncMock(spec=AsyncSession)
    session.add = MagicMock() # session.add is synchronous
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    # For `session.execute(...).scalars().first()`:
    # `session.execute` (async) returns an AsyncResult (MagicMock for simplicity: mock_execute_result)
    # `mock_execute_result.scalars()` (sync) returns an AsyncScalarResult (MagicMock: mock_async_scalar_result)
    # `mock_async_scalar_result.first()` (sync) returns the model instance or None.

    mock_async_scalar_result = MagicMock() # Represents AsyncScalarResult; its methods like .first() are sync.

    mock_execute_result = MagicMock() # Represents AsyncResult
    mock_execute_result.scalars.return_value = mock_async_scalar_result
    session.execute = AsyncMock(return_value=mock_execute_result)

    return session, mock_async_scalar_result # Return session and the mock for AsyncScalarResult

@pytest.fixture
def mock_user_base():
    """Fixture to create a mock UserBase object."""
    user = MagicMock(spec=UserBase)
    # Set common attributes that might be accessed. Specific tests can override.
    user.id = "default_user_id"
    user.telegram_id = 123456789
    user.first_name = "Test"
    user.username = "TestUser"
    user.photo_url = None # Or some default
    return user

# Test Class
class TestAuthUserApi:

    @pytest.mark.asyncio
    async def test_telegram_login_new_user(self, client: AsyncClient, mocker, mock_db_session):
        mock_session, mock_scalar_result = mock_db_session

        # 1. Mock verify_telegram_auth
        mocker.patch('fast_application.api.v1.auth_user.verify_telegram_auth', return_value=True)

        # 2. Mock db_helper.session_getter to use our mock_session
        # This is tricky if db_helper is module-level. Patching its session_getter.
        # Simpler: use app.dependency_overrides
        # For now, assuming db_helper.session_getter is a dependency that can be overridden
        # If it's harder, will need to patch where db_helper.get_session() or similar is called.
        # The route uses: session: AsyncSession = Depends(db_helper.session_getter)
        # So, we can override db_helper.session_getter for the app.

        # This is how dependency overrides work:
        # from fast_application.models.db_helper import db_helper
        # async def override_get_db():
        #     yield mock_session
        # app.dependency_overrides[db_helper.session_getter] = override_get_db
        # This should be done BEFORE the client makes a request.
        # For simplicity with mocker, if db_helper.session_getter is directly callable:
        # mocker.patch('fast_application.models.db_helper.db_helper.session_getter', return_value=mock_session)
        # Using dependency_overrides is cleaner for FastAPI
        from fast_application.models.db_helper import db_helper # Import for override key
        async def override_get_db_session():
            yield mock_session
        app.dependency_overrides[db_helper.session_getter] = override_get_db_session


        # 3. Mock User not found initially
        mock_scalar_result.first.return_value = None

        # 4. Mock UserBase constructor and session methods (add, commit, refresh are on session)
        # UserBase itself doesn't need much mocking if we control what's returned from DB
        # and what's passed to encode_jwt.
        # We do need to ensure that the user object passed to session.refresh() is fine.
        # The actual UserBase class will be called. We need to control its attributes after refresh.

        # Mocking session.refresh (which is an async method)
        # The real session.refresh modifies the instance in place and typically returns None.
        mock_session.refresh = AsyncMock(return_value=None) # What 'await session.refresh()' resolves to.
        async def mock_refresh_side_effect_in_place(user_instance, attribute_names=None, with_for_update=None):
            # UserBase model likely has id as a Mapped column, initially None for a new instance.
            if user_instance.id is None:
                user_instance.id = "new_user_id_from_db_in_place"
            # No explicit return needed if modifying in place and mock is configured with return_value=None.
            # The side_effect is awaited, its return value (if not None) would override AsyncMock's return_value.
            # To be safe, let's make it explicit that the side effect's job is modification,
            # and the AsyncMock's configured return_value is what the await expression yields.
        mock_session.refresh.side_effect = mock_refresh_side_effect_in_place

        # 5. Mock encode_jwt where it's looked up by the auth_user module
        mocked_encode_jwt = mocker.patch('fast_application.api.v1.auth_user.encode_jwt')
        # Configure different return values based on token_type argument
        def encode_jwt_side_effect(payload, token_type, **kwargs):
            if token_type == Token.access:
                return "test_access_token_new_user"
            elif token_type == Token.refresh:
                return "test_refresh_token_new_user"
            return "default_mock_token"
        mocked_encode_jwt.side_effect = encode_jwt_side_effect

        # 6. Prepare payload
        auth_payload_data = {
            "id": 12345, "first_name": "Test", "username": "testuser",
            "auth_date": 1678886400, "hash": "dummyhash"
        }
        payload = TelegramAuthPayload(**auth_payload_data)

        # 7. Make request
        # The path should be /api/v1/auth/telegram/login based on router prefixes
        response = await client.post("/api/v1/auth/telegram/login", json=payload.model_dump())

        # 8. Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["access_token"] == "test_access_token_new_user"
        assert response_data["refresh_token"] == "test_refresh_token_new_user"

        # Assert encode_jwt calls
        # Check first call (access token)
        call_args_access = mocked_encode_jwt.call_args_list[0][1] # kwargs of first call
        assert call_args_access['payload']['telegram_id'] == auth_payload_data['id']
        assert call_args_access['payload']['first_name'] == auth_payload_data['first_name']
        assert call_args_access['token_type'] == Token.access

        # Check second call (refresh token)
        call_args_refresh = mocked_encode_jwt.call_args_list[1][1] # kwargs of second call
        assert 'sub' in call_args_refresh['payload'] # sub should be new_user_id_from_db
        assert call_args_refresh['token_type'] == Token.refresh

        # Assert session calls for new user
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        # mock_session.refresh.assert_called_once() # refresh is called on the instance

    # More tests will follow here...
    # For now, submitting this initial structure and first test.

        # Cleanup dependency override
        del app.dependency_overrides[db_helper.session_getter]

    @pytest.mark.asyncio
    async def test_telegram_login_existing_user(self, client: AsyncClient, mocker, mock_db_session, mock_user_base):
        mock_session, mock_scalar_result = mock_db_session

        # 1. Mock verify_telegram_auth
        mocker.patch('fast_application.api.v1.auth_user.verify_telegram_auth', return_value=True)

        # 2. Override DB session
        from fast_application.models.db_helper import db_helper
        async def override_get_db_session():
            yield mock_session
        app.dependency_overrides[db_helper.session_getter] = override_get_db_session

        # 3. Mock User found - return mock_user_base
        # Ensure the mock_user_base has the necessary attributes the endpoint will use
        mock_user_base.id = "existing_user_db_id"
        mock_user_base.first_name = "Existing"
        mock_user_base.telegram_id = 12345 # Should match payload id for consistency
        mock_scalar_result.first.return_value = mock_user_base

        # 4. Mock encode_jwt
        mocked_encode_jwt = mocker.patch('fast_application.api.v1.auth_user.encode_jwt')
        def encode_jwt_side_effect(payload, token_type, **kwargs):
            if token_type == Token.access:
                return "test_access_token_existing_user"
            elif token_type == Token.refresh:
                return "test_refresh_token_existing_user"
            return "default_mock_token"
        mocked_encode_jwt.side_effect = encode_jwt_side_effect

        # 5. Prepare payload
        auth_payload_data = {
            "id": 12345, "first_name": "Test", "username": "testuser", # first_name can differ from DB
            "auth_date": 1678886400, "hash": "dummyhash"
        }
        payload = TelegramAuthPayload(**auth_payload_data)

        # 6. Make request
        response = await client.post("/api/v1/auth/telegram/login", json=payload.model_dump())

        # 7. Assertions
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["access_token"] == "test_access_token_existing_user"
        assert response_data["refresh_token"] == "test_refresh_token_existing_user"

        # Assert encode_jwt calls
        call_args_access = mocked_encode_jwt.call_args_list[0][1]
        assert call_args_access['payload']['sub'] == "existing_user_db_id"
        assert call_args_access['payload']['first_name'] == "Existing" # Uses name from DB user
        assert call_args_access['payload']['telegram_id'] == 12345
        assert call_args_access['token_type'] == Token.access

        call_args_refresh = mocked_encode_jwt.call_args_list[1][1]
        assert call_args_refresh['payload']['sub'] == "existing_user_db_id"
        assert call_args_refresh['token_type'] == Token.refresh

        # Assert session methods for new user creation were NOT called
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
        mock_session.refresh.assert_not_called() # refresh is an AsyncMock, check it wasn't called

        # Cleanup
        del app.dependency_overrides[db_helper.session_getter]

    @pytest.mark.asyncio
    async def test_telegram_login_invalid_data(self, client: AsyncClient, mocker):
        # 1. Mock verify_telegram_auth to return False
        mocker.patch('fast_application.api.v1.auth_user.verify_telegram_auth', return_value=False)

        # (No DB interaction expected, so no need to mock session or user find)

        # 2. Prepare payload
        auth_payload_data = {
            "id": 12345, "first_name": "Test", "username": "testuser",
            "auth_date": 1678886400, "hash": "dummyhash" # Hash doesn't matter as verify_telegram_auth is mocked
        }
        payload = TelegramAuthPayload(**auth_payload_data)

        # 3. Make request
        response = await client.post("/api/v1/auth/telegram/login", json=payload.model_dump())

        # 4. Assertions
        assert response.status_code == 401
        response_data = response.json()
        assert "Invalid Telegram data!" in response_data["detail"]
        # (Ensure other mocks like encode_jwt were NOT called - though not strictly necessary if verify_telegram_auth is the first check)

    @pytest.mark.asyncio
    async def test_refresh_token_successful(self, client: AsyncClient, mocker, mock_user_base):
        from fast_application.api.v1.auth_user import _get_payload_refresh_token as get_refresh_payload_dependency
        from fast_application.api.v1.auth_user import _get_current_user as get_current_user_dependency
        from fast_application.models.db_helper import db_helper
        from fastapi import HTTPException # For asserting

        refresh_payload_content = {"sub": mock_user_base.id, "token_type": Token.refresh.value}

        async def mock_override_get_refresh_payload():
            return refresh_payload_content

        async def mock_override_get_current_user(session: AsyncSession, payload: dict):
            # Ensure payload from get_refresh_payload_dependency is passed here
            assert payload == refresh_payload_content
            return mock_user_base

        mock_session = AsyncMock(spec=AsyncSession)
        async def override_get_db_session():
            yield mock_session

        app.dependency_overrides[get_refresh_payload_dependency] = mock_override_get_refresh_payload
        app.dependency_overrides[get_current_user_dependency] = mock_override_get_current_user
        app.dependency_overrides[db_helper.session_getter] = override_get_db_session

        mocked_encode_jwt = mocker.patch('fast_application.api.v1.auth_user.encode_jwt')
        mocked_encode_jwt.return_value = "new_test_access_token"

        response = await client.post("/api/v1/auth/telegram/refresh", headers={"Authorization": "Bearer fakerefresh"})

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["access_token"] == "new_test_access_token"
        assert "refresh_token" not in response_data

        mocked_encode_jwt.assert_called_once()
        call_args_access = mocked_encode_jwt.call_args[1]
        assert call_args_access['payload']['sub'] == mock_user_base.id
        assert call_args_access['payload']['first_name'] == mock_user_base.first_name
        assert call_args_access['payload']['telegram_id'] == mock_user_base.telegram_id
        assert call_args_access['token_type'] == Token.access

        del app.dependency_overrides[get_refresh_payload_dependency]
        del app.dependency_overrides[get_current_user_dependency]
        del app.dependency_overrides[db_helper.session_getter]

    @pytest.mark.asyncio
    async def test_refresh_token_user_not_found(self, client: AsyncClient, mocker, mock_user_base):
        from fast_application.api.v1.auth_user import _get_payload_refresh_token as get_refresh_payload_dependency
        from fast_application.api.v1.auth_user import _get_current_user as get_current_user_dependency
        from fast_application.models.db_helper import db_helper
        from fastapi import HTTPException

        refresh_payload_content = {"sub": mock_user_base.id, "token_type": Token.refresh.value}

        async def mock_override_get_refresh_payload():
            return refresh_payload_content

        async def mock_override_get_current_user_raises_not_found(session: AsyncSession, payload: dict):
            raise HTTPException(status_code=404, detail="user not found from mock")

        mock_session = AsyncMock(spec=AsyncSession)
        async def override_get_db_session():
            yield mock_session

        app.dependency_overrides[get_refresh_payload_dependency] = mock_override_get_refresh_payload
        app.dependency_overrides[get_current_user_dependency] = mock_override_get_current_user_raises_not_found
        app.dependency_overrides[db_helper.session_getter] = override_get_db_session

        response = await client.post("/api/v1/auth/telegram/refresh", headers={"Authorization": "Bearer fakerefresh"})

        assert response.status_code == 404
        response_data = response.json()
        assert "user not found from mock" in response_data["detail"]

        del app.dependency_overrides[get_refresh_payload_dependency]
        del app.dependency_overrides[get_current_user_dependency]
        del app.dependency_overrides[db_helper.session_getter]


    @pytest.mark.asyncio
    async def test_refresh_token_invalid_token_payload(self, client: AsyncClient, mocker):
        from fast_application.api.v1.auth_user import _get_payload_refresh_token as get_refresh_payload_dependency
        from fastapi import HTTPException

        async def mock_override_get_refresh_payload_raises_invalid():
            raise HTTPException(status_code=401, detail="Original token invalid from mock")

        app.dependency_overrides[get_refresh_payload_dependency] = mock_override_get_refresh_payload_raises_invalid

        response = await client.post("/api/v1/auth/telegram/refresh", headers={"Authorization": "Bearer invalidtoken"})

        assert response.status_code == 401
        response_data = response.json()
        assert "Original token invalid from mock" in response_data["detail"]

        del app.dependency_overrides[get_refresh_payload_dependency]


class TestVerifyTelegramAuth:

    def test_verify_telegram_auth_valid(self, mocker):
        from fast_application.api.v1.auth_user import verify_telegram_auth # Target function
        import hashlib
        import hmac

        TEST_BOT_TOKEN_VALUE = "test_bot_token_12345"
        # Patch the BOT_TOKEN where it's defined and used by verify_telegram_auth
        mocker.patch('fast_application.api.v1.auth_user.BOT_TOKEN', TEST_BOT_TOKEN_VALUE)

        data_dict = {"id": "123", "first_name": "Test", "auth_date": "1678886400", "username": "testuser"}
        sorted_items = sorted(data_dict.items())
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_items)

        secret_key = hashlib.sha256(TEST_BOT_TOKEN_VALUE.encode("utf-8")).digest()
        correct_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

        valid_auth_data = {**data_dict, "hash": correct_hash}

        assert verify_telegram_auth(valid_auth_data.copy()) == True

    def test_verify_telegram_auth_invalid_hash(self, mocker):
        from fast_application.api.v1.auth_user import verify_telegram_auth
        TEST_BOT_TOKEN_VALUE = "test_bot_token_12345"
        mocker.patch('fast_application.api.v1.auth_user.BOT_TOKEN', TEST_BOT_TOKEN_VALUE)

        data_dict_with_hash = {"id": "123", "first_name": "Test", "auth_date": "1678886400", "hash": "totallyinvalidhash"}
        assert verify_telegram_auth(data_dict_with_hash.copy()) == False

    def test_verify_telegram_auth_missing_hash(self, mocker):
        from fast_application.api.v1.auth_user import verify_telegram_auth
        TEST_BOT_TOKEN_VALUE = "test_bot_token_12345"
        mocker.patch('fast_application.api.v1.auth_user.BOT_TOKEN', TEST_BOT_TOKEN_VALUE)

        data_dict_without_hash = {"id": "123", "first_name": "Test", "auth_date": "1678886400"}
        assert verify_telegram_auth(data_dict_without_hash.copy()) == False

    def test_verify_telegram_auth_tampered_data(self, mocker):
        from fast_application.api.v1.auth_user import verify_telegram_auth
        import hashlib
        import hmac

        TEST_BOT_TOKEN_VALUE = "test_bot_token_12345"
        mocker.patch('fast_application.api.v1.auth_user.BOT_TOKEN', TEST_BOT_TOKEN_VALUE)

        data_dict = {"id": "123", "first_name": "Test", "auth_date": "1678886400", "username": "testuser"}
        sorted_items = sorted(data_dict.items())
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted_items)
        secret_key = hashlib.sha256(TEST_BOT_TOKEN.encode("utf-8")).digest()
        correct_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

        auth_data_with_correct_hash = {**data_dict, "hash": correct_hash}

        # Now tamper one of the data fields after hash generation
        auth_data_with_correct_hash["first_name"] = "TamperedTest"

        assert verify_telegram_auth(auth_data_with_correct_hash.copy()) == False
