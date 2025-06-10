from fastapi import APIRouter
from fastapi.responses import JSONResponse

from fast_application.core.config import settings

router = APIRouter(
    prefix=settings.api.prefix, )


@router.get("/health")
async def health_check():
    return JSONResponse(content={"status": "ok"})