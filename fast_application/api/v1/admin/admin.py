from fastapi import APIRouter

from api.v1.admin.admin_utils import get_models

router = APIRouter(
    tags=["Admin"],
    prefix="/admin",
)

@router.get('/')
async def admin_panel():
    models = list(get_models())
    # Возвращаем список имён классов моделей
    return {"models": [model.__name__ for model in models]}

