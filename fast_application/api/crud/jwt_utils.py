from datetime import datetime, timezone, timedelta
from typing import Literal

import jwt

from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette import status

from core.config import settings
from enum import Enum

class Token(str, Enum):
    access = "access"
    refresh = "refresh"
    field = "token_type"

"""получаем токен"""
def encode_jwt(
        payload:dict,
        token_type: Literal[Token.access, Token.refresh],
        private_key:str = settings.auth_jwt.private_key_path.read_text(),
        algorithm:str = settings.auth_jwt.algorithm,
        expire_minutes:int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: int | None = None,
        ):
    to_encode = payload.copy()
    now=datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + timedelta(days=expire_timedelta)
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat = now,
        token_type = token_type
        )
    encode = jwt.encode(
        to_encode,
        private_key,
        algorithm
        )
    return encode

"""декодируем токен"""

def decode_jwt(token:str|bytes, public_key:str = settings.auth_jwt.public_key_path.read_text(), algorithm:str=settings.auth_jwt.algorithm):
    decode = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
        )
    return decode

http_bearer = HTTPBearer()

async def _get_current_payload(token:HTTPAuthorizationCredentials = Depends(http_bearer))->dict:
    token = token.credentials
    try:
        payload = decode_jwt(token)
        if payload[Token.field] != Token.access:
            raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail=f"token_type {payload[Token.field]}, expected token_type {Token.access}")
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid")
    return payload

async def _get_payload_refresh_token(token:HTTPAuthorizationCredentials = Depends(http_bearer))->dict:
    token = token.credentials
    try:
        payload = decode_jwt(token)
        if payload[Token.field] != Token.refresh:
            raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail=f"token_type {payload[Token.field]}, expected token_type {Token.refresh}")
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid")
    return payload
