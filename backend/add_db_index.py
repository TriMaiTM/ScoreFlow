
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Try loading from backend/.env
load_dotenv("backend/.env")

# Fallback or specific override
DATABASE_URL = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    load_dotenv(r"d:\HK7\DACN2\ScoreFlow\backend\.env")
    DATABASE_URL = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def add_index():
    if not DATABASE_URL:
        print("❌ Error: Could not find DATABASE_URL in .env")
        return

    print(f"Adding Index to matches(match_date) in DB...")
    engine = create_async_engine(DATABASE_URL)
    
    try:
        async with engine.begin() as conn:
            # Check if index exists usually requires more complex query, but we can just try creating if not exists
            # PostgreSQL 'IF NOT EXISTS' is supported in recent versions
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_matches_match_date ON matches(match_date);"))
            print(f"✅ Index 'idx_matches_match_date' created/verified successfully.")
    except Exception as e:
        print(f"❌ Error adding index: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_index())
