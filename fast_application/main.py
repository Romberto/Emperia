# python3.12
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <-- добавлено
from api import router as api_router
from core.config import settings
from models.db_helper import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db_helper.dispose()


app_main = FastAPI(lifespan=lifespan)

# ✅ Добавляем CORS Middleware сразу после создания app_main
app_main.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # dev
        "https://cafeapi.ru",     # прод
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_main.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app_main",
        host=settings.run.host,
        port=settings.run.port,
        reload=True
    )
