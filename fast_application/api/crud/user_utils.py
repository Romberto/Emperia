from starlette import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from models.user import UserBase
from shcemes.auth_sheams import UserCreate


async def _get_current_user(session: AsyncSession, payload: dict):
    stmt = select(UserBase).where(UserBase.id == payload["sub"])
    result = await session.scalars(stmt)
    user = result.first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not font"
        )
    return user


async def _get_all_user(session: AsyncSession, payload: dict):
    stmt = select(UserBase)
    result = await session.scalars(stmt)
    return result.all()


async def add_user_to_db(session: AsyncSession, payload: UserCreate):
    user = UserBase(
        telegram_id=payload.telegram_id,
        first_name=payload.get("first_name"),
        last_name=payload.get("last_name"),
        username=payload.get("username"),
        photo_url=payload.get("photo_url"),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
