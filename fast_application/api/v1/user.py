from sys import prefix

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.user_utils import _get_user, _get_all_user
from models.db_helper import db_helper
from shcemes.auth_sheams import UserRead

router = APIRouter(
    tags=['Users'],
    prefix='/user'
    )

@router.get('/me')
async def get_user(user = Depends(_get_user)):
    return user

@router.get('/all')
async def get_all_users(users = Depends(_get_all_user)):
    return users