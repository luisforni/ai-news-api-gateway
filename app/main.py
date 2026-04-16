from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.routers import articles, health, pipeline, topics
from app.ws import pipeline as ws_pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="AI News Platform — API Gateway",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(topics.router, prefix="/topics")
app.include_router(articles.router, prefix="/articles")
app.include_router(pipeline.router, prefix="/pipeline")
app.include_router(ws_pipeline.router)
