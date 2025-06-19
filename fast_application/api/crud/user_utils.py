from starlette import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from models.user import UserBase


async def _get_current_user(session: AsyncSession, payload: dict):
    stmt = select(UserBase).where(UserBase.id == payload['sub'])
    result = await session.scalars(stmt)
    user = result.first()
    if not user:
        raise HTTPException( status_code=status.HTTP_404_NOT_FOUND, detail="user not font")
    return user


async def _get_all_user(session: AsyncSession, payload: dict):
    stmt = select(UserBase)
    result = await session.scalars(stmt)
    return result.all()
