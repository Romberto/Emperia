#python3.12
import uvicorn
from fastapi import FastAPI
from api import router as api_router
from fast_application.core.config import settings
from models.db_helper import db_helper


def lifespan(app:FastAPI):
    yield app
    db_helper.dispose()




app_main = FastAPI(
    lifespan=lifespan()
    )
app_main.include_router(api_router, prefix=settings.api.prefix)

if __name__ == "__main__":
    uvicorn.run('main:app_main',
                host = settings.run.host,
                port= settings.run.port,
                reload=True)