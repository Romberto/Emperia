#python3.12
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from api import router as api_router
from core.config import settings
from models.db_helper import db_helper

@asynccontextmanager
async def lifespan(app:FastAPI):
    yield
    await db_helper.dispose()




app_main = FastAPI(
    lifespan=lifespan
    )
app_main.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run('main:app_main',
                host = settings.run.host,
                port= settings.run.port,
                reload=True)