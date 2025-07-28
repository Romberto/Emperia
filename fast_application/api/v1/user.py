from sys import prefix

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.jwt_utils import _get_current_payload
from api.crud.user_utils import _get_all_user, _get_current_user
from models.db_helper import db_helper

router = APIRouter(tags=["Users"], prefix="/user")


@router.get("/me")
async def get_user(
    payload: dict = Depends(_get_current_payload),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    current_user = await _get_current_user(session=session, payload=payload)
    return current_user


@router.get("/all")
async def get_all_users(
    payload: dict = Depends(_get_current_payload),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    users = await _get_all_user(payload=payload, session=session)
    return users
