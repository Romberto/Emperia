import time, hmac, hashlib
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import jwt
from jwt.api_jwk import PyJWK

from core.config import settings

JWT_SECRET_KEY = settings.auth_jwt.private_key_path.read_text()
ACCESS_TOKEN_EXPIRE_MINUTES = settings.auth_jwt.access_token_expire_minutes
ALGORITHM = settings.auth_jwt.algorithm
REFRESH_TOKEN_EXPIRE_DAYS = settings.auth_jwt.refresh_token_expire_days

def check_telegram_auth(data: dict):
    check_hash = data.pop("hash")
    sorted_data = sorted([f"{k}={v}" for k, v in data.items()])
    data_check_string = "\n".join(sorted_data)
    secret_key = hashlib.sha256(settings.token_bot.encode()).digest()
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if hmac_hash != check_hash:
        raise HTTPException(status_code=403, detail="Invalid Telegram login")

    if time.time() - int(data.get("auth_date", 0)) > 86400:
        raise HTTPException(status_code=403, detail="Login expired")
    return data

def create_access_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int):
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str | bytes, public_key: PyJWK | str | bytes = None,
                algorithms: str | None = settings.auth_jwt.algorithm):
    if public_key is None:
        public_key = settings.auth_jwt.public_key_path.read_text()
    return jwt.decode(token, key=public_key, algorithms=[algorithms])


