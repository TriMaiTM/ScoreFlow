from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

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
    settings.DATABASE_URL_ASYNC,
    echo=False,
    future=True,
    pool_pre_ping=True,  # Check connection liveness before usingg
    pool_size=40,  
    pool_recycle=1800,      # Keep 10 connections open
    max_overflow=40,     # Allow 20 more temporary connections
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
