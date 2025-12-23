
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
    # Try absolute path just in case
    load_dotenv(r"d:\HK7\DACN2\ScoreFlow\backend\.env")
    DATABASE_URL = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def check_match_count():
    if not DATABASE_URL:
        print("❌ Error: Could not find DATABASE_URL in .env")
        return

    print(f"Checking matches in DB...")
    engine = create_async_engine(DATABASE_URL)
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT COUNT(*) FROM matches;"))
            count = result.scalar()
            print(f"✅ Total Matches in DB: {count}")
    except Exception as e:
        print(f"❌ Error querying database: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_match_count())
