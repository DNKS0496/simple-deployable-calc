import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api_routes.calculations import router as calculations_router
from app.config import settings
from app.database import Base, engine
from app.db_models import calculation
from app.logging_config import configure_logging


configure_logging(settings.log_level)

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Calculator API started")
    yield
    logger.info("Calculator API stopped")

app = FastAPI(title="Calculator API", lifespan=lifespan)

app.include_router(calculations_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "environment": settings.app_env,
    }
