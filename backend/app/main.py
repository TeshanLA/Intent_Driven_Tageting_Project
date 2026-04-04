from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401
from app.core.config import get_settings
from app.core.database import Base, engine
from app.routers import ads, articles, dashboard, events, health
from app.services.inference import inference_service
from app.services.seed_service import seed_demo_content

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_demo_content()
    inference_service.load_artifacts()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(articles.router)
app.include_router(events.router)
app.include_router(ads.router)
app.include_router(dashboard.router)
