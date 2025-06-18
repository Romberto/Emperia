from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud.jwt_utils import decode_jwt
from models.db_helper import db_helper
from models.user import UserBase
from shcemes.auth_sheams import UserRead

http_bearer = HTTPBearer()


async def _get_current_payload(token:HTTPAuthorizationCredentials = Depends(http_bearer)):
    token = token.credentials
    payload = decode_jwt(token)
    return payload


async def _get_user( session:AsyncSession = Depends(db_helper.session_getter),  payload:dict = Depends(_get_current_payload) ):
    stmt = select(UserBase).where(UserBase.id == payload['sub'])
    result = await session.scalars(stmt)
    return result.first()

async def _get_all_user(session:AsyncSession = Depends(db_helper.session_getter),  payload:dict = Depends(_get_current_payload) ):
    stmt = select(UserBase)
    result = await session.scalars(stmt)
    return result.all()
