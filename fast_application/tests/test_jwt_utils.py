import sys
import os
# Add the parent directory of 'fast_application' to sys.path
# This allows 'from fast_application...' imports to work correctly
# and also ensures that imports like 'from core...' work from within the app code
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pytest
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from pathlib import Path
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
# Mock settings before importing jwt_utils
settings_mock = MagicMock()
# Ensure these are Path objects if the application code expects to call .read_text() on them
# Paths should be relative to the root of the project where pytest is run (e.g., /app/fast_application)
settings_mock.auth_jwt.private_key_path = Path("tests/private_key.pem")
settings_mock.auth_jwt.public_key_path = Path("tests/public_key.pem")
settings_mock.auth_jwt.algorithm = "RS256"
settings_mock.auth_jwt.access_token_expire_minutes = 15
settings_mock.auth_jwt.refresh_token_expire_days = 7

# Mock database settings as well, as they are used during import time by db_helper
settings_mock.db.url = "sqlite+aiosqlite:///:memory:"
settings_mock.db.echo = False
settings_mock.db.echo_pool = False
settings_mock.db.max_overflow = 10
settings_mock.db.pool_size = 15

# Mock API prefix
settings_mock.api.v1.prefix = "/api/v1"
settings_mock.api.prefix = "/api"

# Ensure this mock is in place before jwt_utils is imported by other modules indirectly
sys.modules['fast_application.core.config'] = MagicMock(settings=settings_mock)
# Also mock core if it's imported directly as 'core'
sys.modules['core'] = MagicMock()
sys.modules['core.config'] = MagicMock(settings=settings_mock)


from fast_application.api.crud.jwt_utils import encode_jwt, decode_jwt, Token, _get_current_payload, _get_payload_refresh_token

@pytest.fixture
def sample_payload():
    return {"user_id": "test_user"}

@pytest.fixture
def private_key():
    with open(settings_mock.auth_jwt.private_key_path, "rb") as f:
        return f.read()

@pytest.fixture
def public_key():
    with open(settings_mock.auth_jwt.public_key_path, "rb") as f:
        return f.read()

class TestJwtUtils:
    def test_encode_jwt_access_token(self, sample_payload, private_key, public_key):
        token = encode_jwt(payload=sample_payload,
                             token_type=Token.access,
                             private_key=private_key,
                             algorithm=settings_mock.auth_jwt.algorithm)
        assert token is not None
        decoded_token = jwt.decode(token, public_key, algorithms=[settings_mock.auth_jwt.algorithm])
        assert decoded_token["user_id"] == sample_payload["user_id"]
        assert decoded_token["token_type"] == "access"
        assert "exp" in decoded_token
        # Check if expiry is approximately correct (within a small delta)
        expected_expiry = datetime.now(timezone.utc) + timedelta(minutes=settings_mock.auth_jwt.access_token_expire_minutes)
        actual_expiry = datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc)
        assert abs((actual_expiry - expected_expiry).total_seconds()) < 5 # 5 seconds tolerance

    def test_encode_jwt_refresh_token(self, sample_payload, private_key, public_key):
        token = encode_jwt(payload=sample_payload,
                             token_type=Token.refresh,
                             private_key=private_key,
                             algorithm=settings_mock.auth_jwt.algorithm,
                             expire_timedelta=settings_mock.auth_jwt.refresh_token_expire_days)
        assert token is not None
        decoded_token = jwt.decode(token, public_key, algorithms=[settings_mock.auth_jwt.algorithm])
        assert decoded_token["user_id"] == sample_payload["user_id"]
        assert decoded_token["token_type"] == "refresh"
        assert "exp" in decoded_token
        expected_expiry = datetime.now(timezone.utc) + timedelta(days=settings_mock.auth_jwt.refresh_token_expire_days)
        actual_expiry = datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc)
        assert abs((actual_expiry - expected_expiry).total_seconds()) < 5  # 5 seconds tolerance

    def test_decode_jwt_valid_token(self, sample_payload, private_key, public_key):
        token = encode_jwt(payload=sample_payload,
                             token_type=Token.access,
                             private_key=private_key,
                             algorithm=settings_mock.auth_jwt.algorithm)
        decoded_payload = decode_jwt(token, public_key, settings_mock.auth_jwt.algorithm)
        assert decoded_payload["user_id"] == sample_payload["user_id"]
        assert decoded_payload["token_type"] == "access"

    def test_decode_jwt_invalid_token(self, public_key):
        invalid_token = "this.is.an.invalid.token"
        with pytest.raises(jwt.exceptions.InvalidTokenError):
            decode_jwt(invalid_token, public_key, settings_mock.auth_jwt.algorithm)

    def test_decode_jwt_malformed_token(self, public_key):
        malformed_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0" # Missing signature
        with pytest.raises(jwt.exceptions.InvalidTokenError):
            decode_jwt(malformed_token, public_key, settings_mock.auth_jwt.algorithm)

    def test_decode_jwt_expired_token(self, sample_payload, private_key, public_key, mocker):
        # Mock datetime.now to be in the past for token generation
        # Token will be created with an expiry based on this past time
        past_datetime = datetime.now(timezone.utc) - timedelta(minutes=30) # 30 minutes in the past

        # Create a token that is already expired
        payload_with_exp = sample_payload.copy()
        payload_with_exp["exp"] = past_datetime - timedelta(minutes=1) # Expired 1 minute before "now" (which is past_datetime)
        payload_with_exp["token_type"] = "access"

        # We need to manually craft an expired token because encode_jwt sets a new 'exp'
        # when called for setup. encode_jwt also has its own default expiry.
        # For this test, we want a token that *was* valid but *is now* expired.

        # Generate a token that expired settings.auth_jwt.access_token_expire_minutes AGO
        # by setting the "iat" (issued at) time to be in the past.
        # The encode_jwt function calculates 'exp' based on 'iat' + 'expire_minutes'.
        # So, if 'iat' is set to (now - (expire_minutes + some_buffer)), the token will be expired.

        # However, encode_jwt itself sets 'iat' to datetime.now(timezone.utc).
        # So, to test an expired token *decoded* by decode_jwt, we must craft one
        # where the 'exp' field is in the past relative to the moment of decoding.

        payload_for_expired_token = sample_payload.copy()
        # Set 'exp' to a time in the past.
        # The actual 'iat' for this token doesn't matter as much as 'exp' for this test.
        payload_for_expired_token["exp"] = datetime.now(timezone.utc) - timedelta(seconds=1)
        payload_for_expired_token["iat"] = datetime.now(timezone.utc) - timedelta(minutes=settings_mock.auth_jwt.access_token_expire_minutes + 1)
        payload_for_expired_token["token_type"] = "access" # Or Token.access

        expired_token = jwt.encode(
            payload_for_expired_token,
            private_key, # Use the fixture
            algorithm=settings_mock.auth_jwt.algorithm
        )

        with pytest.raises(jwt.exceptions.ExpiredSignatureError):
            decode_jwt(expired_token, public_key, settings_mock.auth_jwt.algorithm)

    def test_decode_jwt_wrong_key(self, sample_payload, private_key):
        # Generate a different key pair
        _ , wrong_public_key_pem = self._generate_temp_rsa_keys() # Corrected: only need public for decoding with wrong key

        token = encode_jwt(payload=sample_payload,
                             token_type=Token.access,
                             private_key=private_key,
                             algorithm=settings_mock.auth_jwt.algorithm)

        with pytest.raises(jwt.exceptions.InvalidSignatureError): # It might also be InvalidTokenError depending on the lib version and specific error
            decode_jwt(token, wrong_public_key_pem, settings_mock.auth_jwt.algorithm)

    def _generate_temp_rsa_keys(self):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        private_key_pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_key_pem = key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return private_key_pem, public_key_pem

    def test_decode_jwt_different_algorithm(self, sample_payload, private_key, public_key):
        token = encode_jwt(payload=sample_payload,
                             token_type=Token.access,
                             private_key=private_key,
                             algorithm=settings_mock.auth_jwt.algorithm)

        with pytest.raises(jwt.exceptions.InvalidAlgorithmError):
            decode_jwt(token, public_key, "HS256") # Trying to decode with a different algorithm

    # Tests for _get_current_payload
    @pytest.mark.asyncio
    async def test_get_current_payload_valid_access_token(self, sample_payload, private_key):
        token_str = encode_jwt(payload=sample_payload, token_type=Token.access, private_key=private_key, algorithm=settings_mock.auth_jwt.algorithm)
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_str)

        # Mock the http_bearer dependency within the function's scope if direct call is hard,
        # or rely on FastAPI's Depends handling if testing through an endpoint.
        # For direct unit test, we might need to patch 'decode_jwt' if it's easier,
        # but let's try calling it as directly as possible.
        # The Depends(http_bearer) makes direct calling tricky without a FastAPI context.
        # A common way is to call the function with the dependency explicitly passed.
        # However, these functions are defined as `_get_current_payload(token: HTTPAuthorizationCredentials = Depends(http_bearer))`.
        # We can directly pass the `token` argument.

        payload = await _get_current_payload(token=mock_credentials)
        assert payload["user_id"] == sample_payload["user_id"]
        assert payload["token_type"] == Token.access.value # jwt_utils uses the enum value

    @pytest.mark.asyncio
    async def test_get_current_payload_with_refresh_token(self, sample_payload, private_key):
        token_str = encode_jwt(
            payload=sample_payload,
            token_type=Token.refresh,
            private_key=private_key,
            algorithm=settings_mock.auth_jwt.algorithm,
            expire_timedelta=settings_mock.auth_jwt.refresh_token_expire_days
        )
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_str)
        with pytest.raises(HTTPException) as exc_info:
            await _get_current_payload(token=mock_credentials)
        assert exc_info.value.status_code == 401
        detail_lower = exc_info.value.detail.lower()
        # Check that the detail mentions the type of token that was received (refresh)
        # and the type of token that was expected (Token.access)
        assert Token.refresh.value in detail_lower # "refresh"
        assert "expected token_type token.access" in detail_lower

    @pytest.mark.asyncio
    async def test_get_current_payload_invalid_token(self):
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.string")
        with pytest.raises(HTTPException) as exc_info:
            await _get_current_payload(token=mock_credentials)
        assert exc_info.value.status_code == 401
        assert "token invalid" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_current_payload_expired_access_token(self, sample_payload, private_key):
        # Create an already expired token
        expired_payload = sample_payload.copy()
        expired_payload["exp"] = datetime.now(timezone.utc) - timedelta(seconds=1)
        expired_payload["iat"] = datetime.now(timezone.utc) - timedelta(minutes=settings_mock.auth_jwt.access_token_expire_minutes + 1)
        expired_payload["token_type"] = Token.access.value
        expired_token_str = jwt.encode(expired_payload, private_key, algorithm=settings_mock.auth_jwt.algorithm)

        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token_str)
        with pytest.raises(HTTPException) as exc_info:
            await _get_current_payload(token=mock_credentials)
        assert exc_info.value.status_code == 401
        assert "token invalid" in exc_info.value.detail.lower() # decode_jwt raises InvalidTokenError, which _get_current_payload turns into this


    # Tests for _get_payload_refresh_token
    @pytest.mark.asyncio
    async def test_get_payload_refresh_token_valid_refresh_token(self, sample_payload, private_key):
        token_str = encode_jwt(
            payload=sample_payload,
            token_type=Token.refresh,
            private_key=private_key,
            algorithm=settings_mock.auth_jwt.algorithm,
            expire_timedelta=settings_mock.auth_jwt.refresh_token_expire_days
        )
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_str)
        payload = await _get_payload_refresh_token(token=mock_credentials)
        assert payload["user_id"] == sample_payload["user_id"]
        assert payload["token_type"] == Token.refresh.value

    @pytest.mark.asyncio
    async def test_get_payload_refresh_token_with_access_token(self, sample_payload, private_key):
        token_str = encode_jwt(payload=sample_payload, token_type=Token.access, private_key=private_key, algorithm=settings_mock.auth_jwt.algorithm)
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_str)
        with pytest.raises(HTTPException) as exc_info:
            await _get_payload_refresh_token(token=mock_credentials)
        assert exc_info.value.status_code == 401
        detail_lower = exc_info.value.detail.lower()
        # Check that the detail mentions the type of token that was received (access)
        # and the type of token that was expected (Token.refresh)
        assert Token.access.value in detail_lower # "access"
        assert "expected token_type token.refresh" in detail_lower

    @pytest.mark.asyncio
    async def test_get_payload_refresh_token_invalid_token(self):
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.string")
        with pytest.raises(HTTPException) as exc_info:
            await _get_payload_refresh_token(token=mock_credentials)
        assert exc_info.value.status_code == 401
        assert "token invalid" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_payload_refresh_token_expired_refresh_token(self, sample_payload, private_key):
        expired_payload = sample_payload.copy()
        expired_payload["exp"] = datetime.now(timezone.utc) - timedelta(seconds=1)
        # Ensure 'iat' is also in the past, consistent with how 'exp' would have been calculated
        expired_payload["iat"] = datetime.now(timezone.utc) - timedelta(days=settings_mock.auth_jwt.refresh_token_expire_days + 1)
        expired_payload["token_type"] = Token.refresh.value # Crucial: use the enum's value

        expired_token_str = jwt.encode(expired_payload, private_key, algorithm=settings_mock.auth_jwt.algorithm)

        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token_str)
        with pytest.raises(HTTPException) as exc_info:
            await _get_payload_refresh_token(token=mock_credentials)
        assert exc_info.value.status_code == 401
        assert "token invalid" in exc_info.value.detail.lower()
