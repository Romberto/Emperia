from fastapi import APIRouter
from sqlalchemy.dialects.oracle.dictionary import all_users
from .v1 import router as v1_router
from core.config import settings

router = APIRouter(
    )

router.include_router(v1_router)


