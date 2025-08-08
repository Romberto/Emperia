from fastapi import APIRouter

from core.config import settings
from api.v1.auth.auth_user import router as auth_router
from api.v1.users.user import router as user_router
from .sendler import router as send_router
from api.v1.admin.admin import router as admin_router

router = APIRouter(prefix=settings.api.v1.prefix)

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(send_router)
router.include_router(admin_router)
