from fastapi.exceptions import HTTPException
import uuid
import pytest
from sqlalchemy import select

from api.crud.user_utils import _get_current_user
from models.user import UserBase


async def test__get_current_user(session,init_test_data):
    stmt = select(UserBase)
    result = await session.scalars(stmt)
    user = result.first()
    payload = {"sub": user.id}
    current_user = await _get_current_user(session, payload)
    assert user.telegram_id == current_user.telegram_id


@pytest.mark.parametrize(
    "payload, exc ", (
        ({"sub": '1231123123'}, pytest.raises(HTTPException)), # не валидный id
        ({'sub': 231323431}, pytest.raises(HTTPException)), # не валидный id
        ({'sub': uuid.uuid4()}, pytest.raises(HTTPException)) # не существующий пользователь
    )
    )

async def test__get_current_user_invalid_id(session, init_test_data, payload, exc):
    with exc:
        await _get_current_user(session, payload)


