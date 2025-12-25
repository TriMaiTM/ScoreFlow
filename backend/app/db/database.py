from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import QueuePool

from app.core.config import settings

import ssl
import os

# Determine if we need SSL (Render requires it)
# Check for RENDER env var or if URL contains 'render'
# Also check if database host contains 'render' (common in connection strings)
use_ssl = os.getenv("RENDER") or "render" in settings.DATABASE_URL_ASYNC or "onrender" in settings.DATABASE_URL_ASYNC

connect_args = {
    "statement_cache_size": 0,
    "server_settings": {
        "jit": "off",
    },
    "timeout": 60,          # Increase connection timeout to 60s (for Render cold starts)
    "command_timeout": 60,  # Increase query timeout to 60s
}

if use_ssl:
    # Create a permissive SSL context for Render
    print("🔒 SSL Context: ACTIVATING for Render...")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ctx
else:
    print("🔓 SSL Context: Disabled")

engine = create_async_engine(
    settings. DATABASE_URL_ASYNC,
    echo=False,
    future=True,
    poolclass=QueuePool,                          # ✅ Đổi từ NullPool
    pool_size=settings.DB_POOL_SIZE,              # 5 connections
    max_overflow=settings.DB_MAX_OVERFLOW,        # Tối đa +10
    pool_timeout=settings.DB_POOL_TIMEOUT,        # Đợi 30s
    pool_recycle=settings.DB_POOL_RECYCLE,        # Recycle sau 1 giờ
    pool_pre_ping=settings.DB_POOL_PRE_PING,      # Kiểm tra trước khi dùng
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
