from fastapi import APIRouter

from core.config import settings
from .auth_user import router as auth_router
from .user import router as user_router
from .sendler import router as send_router

router = APIRouter(prefix=settings.api.v1.prefix)

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(send_router)
