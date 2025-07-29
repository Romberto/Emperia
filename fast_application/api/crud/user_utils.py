from uuid import UUID
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import DBAPIError, IntegrityError, DataError
from starlette import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException

from models.user import UserBase
from shcemes.auth_sheams import UserCreate


async def _get_current_user(session: AsyncSession, payload: dict) -> UserBase:
    try:
        user_id = payload["sub"]

        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Некорректный формат ID")
        if not isinstance(user_id, UUID):
            raise HTTPException(status_code=400, detail="Некорректный формат ID")

        stmt = select(UserBase).where(UserBase.id == user_id)
        result = await session.scalars(stmt)
        user = result.first()

    except DBAPIError:
        raise HTTPException(
            status_code=400, detail="Ошибка при получении пользователя из базы"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )

    return user


async def _get_all_user(session: AsyncSession):
    stmt = select(UserBase)
    result = await session.scalars(stmt)
    return result.all()


async def add_user_to_db(session: AsyncSession, payload: UserCreate):
    try:
        user = UserBase(
            telegram_id=payload.id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            username=payload.username,
            photo_url=payload.photo_url,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    except IntegrityError as e:
        # Уникальное ограничение
        if isinstance(e.orig, UniqueViolationError):
            raise HTTPException(
                status_code=409,
                detail="Пользователь с таким Telegram ID уже существует",
            )
        raise HTTPException(
            status_code=400, detail="Нарушение ограничений в базе данных"
        )
    except DBAPIError as e:
        # Ошибка формата данных, например DataError
        if isinstance(e.orig, DataError):
            raise HTTPException(
                status_code=400, detail="Неверный формат данных (например, не int)"
            )
        raise HTTPException(
            status_code=400, detail="Ошибка при добавлении пользователя в базу"
        )
