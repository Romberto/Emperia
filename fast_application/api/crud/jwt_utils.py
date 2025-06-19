from datetime import datetime, timezone, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.config import settings

"""получаем токен"""
def encode_jwt(
        payload:dict,
        private_key:str = settings.auth_jwt.private_key_path.read_text(),
        algorithm:str = settings.auth_jwt.algorithm,
        expire_minutes:int = settings.auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None
        ):
    to_encode = payload.copy()
    now=datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat = now,
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
    payload = decode_jwt(token)
    if payload:
        return payload
    else:
        raise HTTPException(status_code=401, detail="token invalid")