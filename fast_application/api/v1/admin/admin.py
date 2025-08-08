from fastapi import APIRouter

router = APIRouter(
    tags=["Admin"],
    prefix="/admin",
)

@router.get('/')
async def admin_panel():
    pass