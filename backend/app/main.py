import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.ws.interview_ws import router as ws_router
from app.config import settings
from app.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup (dev only; use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)
    yield


app = FastAPI(
    title="ExpertFlow API",
    description="专家访谈智能助手 API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST routes
app.include_router(api_router)

# WebSocket routes
app.include_router(ws_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ExpertFlow"}
