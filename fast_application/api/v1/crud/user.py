from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from core.config import settings
from models import Users


async def _get_all_users(session:AsyncSession)-> Sequence[Users]:
    stmt = select(Users).order_by(Users.id)
    result = await session.scalars(stmt)
    return result.all()