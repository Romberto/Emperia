from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio.session import AsyncSession

from sqlalchemy import select
from sqlalchemy.sql.functions import func

from api.v1.admin.admin_utils import is_admin, get_model_by_name

from api.v1.admin.admin_utils import get_models
from models.db_helper import db_helper

router = APIRouter(
    tags=["Admin"],
    prefix="/admin",
)


@router.get("/")
async def admin_panel(is_admin: bool = Depends(is_admin)):
    models = list(get_models())
    # Возвращаем список имён классов моделей
    return {"models": [model.__name__ for model in models]}


@router.get("/{tablename}")
async def get_rows_tablenames(
    tablename: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_admin: bool = Depends(is_admin),
    session: AsyncSession = Depends(db_helper.session_getter),
):
    model = get_model_by_name(tablename)
    total_stmt = select(func.count()).select_from(model)
    total_result = await session.execute(total_stmt)
    total = total_result.scalar_one()

    stmt = select(model).offset(skip).limit(limit)
    result = await session.execute(stmt)
    dbdata = result.scalars().all()

    def serialize(record):
        return {col.name: getattr(record, col.name) for col in record.__table__.columns}

    data = [serialize(res) for res in dbdata]

    return {"total": total, "skip": skip, "limit": limit, "data": data}
