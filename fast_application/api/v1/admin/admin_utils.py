from fastapi import HTTPException, Depends
from starlette import status
from api.crud.jwt_utils import _get_current_payload
from models.base import Base


def get_model_by_name(name: str):
    for mapper in Base.registry.mappers:
        model = mapper.class_
        if model.__name__ == name:
            return model
    raise HTTPException(status_code=404, detail="Model not found")


def get_models():
    # Base.registry.mappers — генератор всех мапперов моделей
    for mapper in Base.registry.mappers:
        model = mapper.class_
        yield model


async def is_admin(payload: dict = Depends(_get_current_payload)):
    role = payload.get("role")
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins allowed"
        )
    return True
