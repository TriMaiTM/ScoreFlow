from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=True,
    future=True,
    pool_pre_ping=True,  # Tự động kiểm tra kết nối sống/chết trước khi dùng
    connect_args={
        "prepare_threshold": None, # <--- QUAN TRỌNG NHẤT: Trị bệnh Timeout với Supabase
    }
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
