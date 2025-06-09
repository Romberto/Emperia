from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.crud.user import _get_all_users
from core.config import settings
from models.db_helper import db_helper

router = APIRouter(
    tags=["Users"],
    prefix=settings.api.v1.users
    )

@router.get('/')
async def get_all_users(session:AsyncSession = Depends(db_helper.session_getter)):
    return await _get_all_users(session)