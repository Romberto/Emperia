import hashlib
import hmac

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_application.core.config import settings
from models.db_helper import db_helper
from models.user import UserBase
from shcemes.auth_sheams import TelegramAuthPayload

router = APIRouter(
    prefix="/auth",
    )
BOT_TOKEN = settings.bot_token


def verify_telegram_auth(data: dict) -> bool:
    auth_hash = data.pop("hash")
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    hmac_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac_hash == auth_hash

"""
 Получаю данные от телеграмма, с помощью бот токена расшифровываю хеш
"""
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
        user = UserBase(
            telegram_id=telegram_id, first_name=data["first_name"], username=data.get("username"),
            photo_url=data.get("photo_url"), )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user

    # token = create_access_token({"sub": str(user.id)})  #  # return {"access_token": token}
