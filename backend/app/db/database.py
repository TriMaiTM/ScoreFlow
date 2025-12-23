from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

import ssl
import os

# Determine if we need SSL (Render requires it)
# Check for RENDER env var or if URL contains 'render'
use_ssl = os.getenv("RENDER") or "render" in settings.DATABASE_URL_ASYNC

connect_args = {
    "statement_cache_size": 0,
    "server_settings": {
        "jit": "off",
    },
}

if use_ssl:
    # Create a permissive SSL context for Render
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ctx

engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=False,
    future=True,
    poolclass=NullPool,
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
