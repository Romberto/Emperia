import hashlib
import hmac

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.jwt_utils import encode_jwt
from fast_application.core.config import settings
from models.db_helper import db_helper
from models.user import UserBase
from shcemes.auth_sheams import TelegramAuthPayload, TokenPair

router = APIRouter(
    prefix="/auth", )
BOT_TOKEN = settings.bot_token


def verify_telegram_auth(data: dict) -> bool:
    auth_hash = data.get("hash")
    if not auth_hash:
        return False
    check_data = {k: str(v) for k, v in data.items() if k != "hash" and v is not None}
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(check_data.items()))
    secret_key = hashlib.sha256(BOT_TOKEN.encode("utf-8")).digest()
    hmac_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.compare_digest(hmac_hash, auth_hash)





@router.post("/telegram")
async def telegram_login(payload: TelegramAuthPayload, session: AsyncSession = Depends(db_helper.session_getter)):
    data = payload.model_dump()
    if not verify_telegram_auth(data.copy()):
        raise HTTPException(status_code=401, detail="Invalid Telegram data!")

    telegram_id = data["id"]
    result = await session.execute(
        select(UserBase).where(UserBase.telegram_id == telegram_id), )
    user = result.scalars().first()

    if not user:
        user:UserBase = UserBase(
            telegram_id=telegram_id, first_name=data["first_name"], username=data.get("username"),
            photo_url=data.get("photo_url"), )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    access_token = encode_jwt(payload={
        "sub":str(user.id),
        "first_name": user.first_name,
        "telegram_id" : user.telegram_id
        })
    refresh_token = encode_jwt(payload={
        "sub": str(user.id)
        },
        expire_timedelta=settings.auth_jwt.refresh_token_expire_days)
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token
        )


