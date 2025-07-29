import hashlib
import hmac

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.jwt_utils import (
    encode_jwt,
    _get_payload_refresh_token,
    Token,
    verify_telegram_auth,
)
from api.crud.user_utils import _get_current_user, add_user_to_db
from core.config import settings
from models.db_helper import db_helper
from models.user import UserBase
from shcemes.auth_sheams import TelegramAuthPayload, TokenPair, UserCreate

router = APIRouter(
    tags=["Auth"],
    prefix="/auth",
)
BOT_TOKEN = settings.bot.bot_token


@router.get("/")
async def test():
    return {"message": "saccess /"}


@router.post(
    "/telegram/login", response_model=TokenPair, response_model_exclude_none=True
)
async def telegram_login(
    payload: TelegramAuthPayload,
    session: AsyncSession = Depends(db_helper.session_getter),
) -> TokenPair:
    data = payload.model_dump()
    if not verify_telegram_auth(data.copy(), BOT_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid Telegram data!")

    telegram_id = data["id"]
    result = await session.execute(
        select(UserBase).where(UserBase.telegram_id == telegram_id),
    )
    user = result.scalars().first()
    if not user:
        user = await add_user_to_db(session, UserCreate(**data))
    access_token = encode_jwt(
        payload={
            "sub": str(user.id),
            "first_name": user.first_name,
            "telegram_id": user.telegram_id,
        },
        token_type=Token.access,
    )
    _refresh_token = encode_jwt(
        payload={
            "sub": str(user.id),
        },
        expire_timedelta=settings.auth_jwt.refresh_token_expire_days,
        token_type=Token.refresh,
    )
    return TokenPair(access_token=access_token, refresh_token=_refresh_token)


@router.post(
    "/telegram/refresh", response_model=TokenPair, response_model_exclude_none=True
)
async def refresh_token(
    payload: dict = Depends(_get_payload_refresh_token),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    user = await _get_current_user(session=session, payload=payload)
    _access_token = encode_jwt(
        payload={
            "sub": str(user.id),
            "first_name": user.first_name,
            "telegram_id": user.telegram_id,
        },
        token_type=Token.access,
    )
    return TokenPair(access_token=_access_token)
