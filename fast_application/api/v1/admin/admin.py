from fastapi import APIRouter, Depends
from api.v1.admin.admin_utils import is_admin

from api.v1.admin.admin_utils import get_models

router = APIRouter(
    tags=["Admin"],
    prefix="/admin",
)


@router.get("/")
async def admin_panel(is_admin: bool = Depends(is_admin)):
    models = list(get_models())
    # Возвращаем список имён классов моделей
    return {"models": [model.__name__ for model in models]}
