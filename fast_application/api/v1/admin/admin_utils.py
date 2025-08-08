from fastapi import HTTPException

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

