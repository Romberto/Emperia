import pytest
from sqlalchemy import select

from api.crud.user_utils import _get_current_user
from models.user import UserBase


async def test__get_current_user(session, init_test_data):
    stmt = select(UserBase)
    result = await session.scalars(stmt)
    user = result.first()
    payload = {"sub": user.id}
    current_user = await _get_current_user(session, payload)
    assert user.telegram_id == current_user.telegram_id
