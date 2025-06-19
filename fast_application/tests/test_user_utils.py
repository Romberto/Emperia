import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path # Added for Path objects in settings

# Add project root to sys.path to allow 'from fast_application...' imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# --- Start Comprehensive Mocking of settings ---
# Create a master mock for the settings instance
mock_settings_object = MagicMock()

# Mock database settings
mock_settings_object.db.url = "sqlite+aiosqlite:///:memory:"
mock_settings_object.db.echo = False
mock_settings_object.db.echo_pool = False
mock_settings_object.db.max_overflow = 10
mock_settings_object.db.pool_size = 15

# Mock bot_token
mock_settings_object.bot_token = "dummy_bot_token_for_tests"

# Mock API prefixes
mock_settings_object.api.v1.prefix = "/api/v1"
mock_settings_object.api.prefix = "/api"

# Mock JWT settings (paths should be Path objects if config expects them)
# Using dummy paths as these tests might not rely on actual key files,
# but Settings class might try to access/validate them.
# For consistency with test_jwt_utils, we can point to the test keys.
# Ensure these paths exist if Settings attempts to read them during init,
# otherwise, ensure that part of Settings is also mocked if necessary.
# For now, assuming the paths themselves are what's needed on the settings object.
private_key_path = Path(os.path.join(os.path.dirname(__file__), "private_key.pem"))
public_key_path = Path(os.path.join(os.path.dirname(__file__), "public_key.pem"))
# Create dummy key files if they don't exist and Settings() tries to read them
if not private_key_path.exists():
    private_key_path.touch()
if not public_key_path.exists():
    public_key_path.touch()

mock_settings_object.auth_jwt.private_key_path = private_key_path
mock_settings_object.auth_jwt.public_key_path = public_key_path
mock_settings_object.auth_jwt.algorithm = "RS256"
mock_settings_object.auth_jwt.access_token_expire_minutes = 15
mock_settings_object.auth_jwt.refresh_token_expire_days = 7

# Create a mock for the entire 'fast_application.core.config' module
mock_config_module = MagicMock()
mock_config_module.settings = mock_settings_object

# Apply the mock to sys.modules BEFORE any application imports
sys.modules['fast_application.core.config'] = mock_config_module
sys.modules['core'] = mock_config_module # If there are any 'from core import settings'
sys.modules['core.config'] = mock_config_module
# --- End Comprehensive Mocking of settings ---

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException # Changed import

from fast_application.api.crud.user_utils import _get_current_user, _get_all_user
from fast_application.models.user import UserBase # Assuming UserBase is the model used

@pytest.fixture
def mock_session_parts(): # Renamed fixture
    """Fixture to create a mock AsyncSession and the result object of session.scalars()."""
    session_mock = AsyncMock(spec=AsyncSession)
    # This is the object that `await session.scalars()` will return.
    # This object then has synchronous .first() and .all() methods.
    scalar_results_mock = MagicMock()
    session_mock.scalars = AsyncMock(return_value=scalar_results_mock)
    return session_mock, scalar_results_mock

@pytest.fixture
def mock_user_base():
    """Fixture to create a mock UserBase object."""
    user = MagicMock(spec=UserBase)
    user.id = "user_id_123"
    user.telegram_id = 123456789
    user.first_name = "Test"
    user.username = "TestUser"
    # Add any other attributes that might be accessed by the code or assertions
    return user

class TestUserUtils:
    @pytest.mark.asyncio
    async def test_get_current_user_found(self, mock_session_parts, mock_user_base): # Use new fixture
        mock_session, scalar_results_mock = mock_session_parts # Unpack
        sample_payload = {'sub': 'user_id_123'}

        scalar_results_mock.first.return_value = mock_user_base # Configure .first()

        returned_user = await _get_current_user(session=mock_session, payload=sample_payload)

        mock_session.scalars.assert_called_once()
        scalar_results_mock.first.assert_called_once()
        assert returned_user == mock_user_base

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self, mock_session_parts): # Use new fixture
        mock_session, scalar_results_mock = mock_session_parts # Unpack
        sample_payload = {'sub': 'user_id_404'}

        scalar_results_mock.first.return_value = None # Simulate user not found

        with pytest.raises(HTTPException) as exc_info:
            await _get_current_user(session=mock_session, payload=sample_payload)

        assert exc_info.value.status_code == 404
        # The detail message in the app is "user not font" - typo from app code.
        assert "user not font" in exc_info.value.detail.lower()
        mock_session.scalars.assert_called_once()
        scalar_results_mock.first.assert_called_once() # Check call on scalar_results_mock

    @pytest.mark.asyncio
    async def test_get_all_user_multiple_found(self, mock_session_parts, mock_user_base): # Use new fixture
        mock_session, scalar_results_mock = mock_session_parts # Unpack
        # Create a list of mock users
        mock_user_list = [mock_user_base, MagicMock(spec=UserBase), MagicMock(spec=UserBase)]

        scalar_results_mock.all.return_value = mock_user_list # Configure .all()

        # The payload is unused by _get_all_user in the current implementation
        returned_users = await _get_all_user(session=mock_session, payload={})

        mock_session.scalars.assert_called_once()
        scalar_results_mock.all.assert_called_once() # Check call on scalar_results_mock
        assert returned_users == mock_user_list
        assert len(returned_users) == 3

    @pytest.mark.asyncio
    async def test_get_all_user_none_found(self, mock_session_parts): # Use new fixture
        mock_session, scalar_results_mock = mock_session_parts # Unpack
        scalar_results_mock.all.return_value = [] # Simulate no users found

        returned_users = await _get_all_user(session=mock_session, payload={})

        mock_session.scalars.assert_called_once()
        scalar_results_mock.all.assert_called_once() # Check call on scalar_results_mock
        assert returned_users == []
        assert len(returned_users) == 0
