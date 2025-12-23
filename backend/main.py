from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.v1 import router as api_router
from app.api.v1.endpoints import admin, users
from app.db.database import engine, Base
from app.services.cache import cache
from app.core.scheduler import start_scheduler, stop_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting ScoreFlow API...")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Connect to Redis
    await cache.connect()
    
    # Start background scheduler for auto-updates
    if settings.ENABLE_SCHEDULER:
        start_scheduler()
        logger.info("✅ Background scheduler enabled")
    else:
        logger.info("⚠️  Background scheduler disabled")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down ScoreFlow API...")
    if settings.ENABLE_SCHEDULER:
        stop_scheduler()
    await engine.dispose()
    await cache.disconnect()


app = FastAPI(
    title="ScoreFlow API",
    description="Football match prediction and tracking API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://localhost:8081",
        "exp://192.168.1.3:8081",
        "http://192.168.1.3:8081",
        "*"
    ],  # Explicitly allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
from app.api.v1.endpoints import news
app.include_router(news.router, prefix="/api/v1/news", tags=["news"])

from fastapi.staticfiles import StaticFiles
import os

if not os.path.exists("static"):
    os.makedirs("static")
    
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"message": "ScoreFlow API", "version": "1.0.0"}


@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    return {"status": "healthy"}