from contextlib import nullcontext

from fastapi.exceptions import HTTPException
from unittest.mock import patch

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from contextlib import nullcontext as not_raises
import core.config
from api.crud.jwt_utils import (
    encode_jwt,
    Token,
    decode_jwt,
    _get_current_payload,
    _get_payload_refresh_token,
)


@pytest.mark.parametrize(
    "payload, tokenType",
    (({"user_id": 123}, Token.access), ({"user_id": "1ew435"}, Token.refresh)),
)
@patch("core.config.settings")
def test_encode_jwt(mock_path, payload, tokenType):
    mock_path.auth_jwt.private_key_path.read_text.return_value = "mocked_private_key"
    mock_path.auth_jwt.algorithm = "RS256"
    mock_path.auth_jwt.access_token_expire_minutes = 15
    mock_path.auth_jwt.public_key_path.read_text.return_value = "mocked_private_key"
    token = encode_jwt(payload=payload, token_type=tokenType)
    decode_token = decode_jwt(token)
    assert decode_token["user_id"] == payload["user_id"]
    assert decode_token["token_type"] == tokenType


@pytest.mark.parametrize("payload", (({"user_id": 123}), ({"user_id": "1ew435"})))
@pytest.mark.anyio
@patch("core.config.settings")
async def test_get_current_payload(mock_path, payload):
    mock_path.auth_jwt.private_key_path.read_text.return_value = "mocked_private_key"
    mock_path.auth_jwt.algorithm = "RS256"
    mock_path.auth_jwt.access_token_expire_minutes = 15
    mock_path.auth_jwt.public_key_path.read_text.return_value = "mocked_private_key"
    token = encode_jwt(payload=payload, token_type=Token.access)

    cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    result = await _get_current_payload(cred)
    assert result["user_id"] == payload["user_id"]


@pytest.mark.asyncio
async def test_get_current_payload_invalid_token():
    with pytest.raises(HTTPException) as exc:
        cred = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid token"
        )
        await _get_current_payload(cred)
        assert exc.value.status_code == 401
        assert exc.value.detail == "token invalid"


@patch("core.config.settings")
@pytest.mark.anyio
async def test_get_current_payload_invalid_type_token(mock_path):
    mock_path.auth_jwt.private_key_path.read_text.return_value = "mocked_private_key"
    mock_path.auth_jwt.algorithm = "RS256"
    mock_path.auth_jwt.access_token_expire_minutes = 15
    mock_path.auth_jwt.public_key_path.read_text.return_value = "mocked_private_key"
    token = encode_jwt(payload={"user_id": 123}, token_type=Token.refresh)
    with pytest.raises(HTTPException) as exc:
        cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        await _get_current_payload(cred)
        assert exc.value.status_code == 401
        assert (
            exc.value.detail
            == f"token_type {token[Token.field]}, expected token_type {Token.access}"
        )


@pytest.mark.parametrize(
    "payload, typeToken, exc",
    (
        ({"user_id": 123}, Token.access, pytest.raises(HTTPException)),
        ({"user_id": 123}, Token.refresh, not_raises()),
        ({"user_id": "123"}, Token.refresh, not_raises()),
        ({"user_id": 23432123445435}, Token.refresh, not_raises()),
        ({"user_id": 123}, Token.access, pytest.raises(HTTPException)),
    ),
)
@patch("core.config.settings")
async def test_get_payload_refresh_token(mock_settings, payload, typeToken, exc):
    mock_settings.auth_jwt.private_key_path.read_text.return_value = (
        "mocked_private_key"
    )
    mock_settings.auth_jwt.algorithm = "RS256"
    mock_settings.auth_jwt.access_token_expire_minutes = 15
    mock_settings.auth_jwt.public_key_path.read_text.return_value = "mocked_private_key"
    token = encode_jwt(payload=payload, token_type=typeToken)
    with exc:
        cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        result = await _get_payload_refresh_token(cred)
        assert result["user_id"] == payload["user_id"]
