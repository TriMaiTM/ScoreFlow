from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings

engine = create_async_engine(
    echo=False,  # Tắt log SQL cho nhẹ
    future=True,
    poolclass=NullPool, # Bắt buộc dùng NullPool với Supabase Transaction Mode
    
    connect_args={
        # 1. Cấu hình cho Server Postgres
        "server_settings": {
            "jit": "off",
        },
        
        # 2. Cấu hình riêng cho Driver Asyncpg (PHẢI NẰM Ở ĐÂY, NGOÀI server_settings)
        "statement_cache_size": 0,  # <--- Dòng này quan trọng nhất
        "prepared_statement_cache_size": 0, # Thêm dòng này dự phòng cho chắc
        "ssl": "require"
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
