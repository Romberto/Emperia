from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from models.user import UserBase


async def _get_current_user(session: AsyncSession, payload: dict):
    stmt = select(UserBase).where(UserBase.id == payload['sub'])
    result = await session.scalars(stmt)
    return result.first()


async def _get_all_user(session: AsyncSession, payload: dict):
    if payload:
        stmt = select(UserBase)
        result = await session.scalars(stmt)
        return result.all()
    else:
        raise HTTPException(status_code=403, detail="the user is not authenticated")