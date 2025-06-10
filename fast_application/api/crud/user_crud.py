from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from models.user import UserBase


async def _get_all_user(session:AsyncSession)-> Sequence[UserBase]:
    stmt = select(UserBase).order_by(UserBase.id)
    result = await session.scalars(stmt)
    return result.all()