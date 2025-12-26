
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, text
from dotenv import load_dotenv

# Setup path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Load Env
load_dotenv("backend/.env")
DATABASE_URL = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    load_dotenv(r"d:\HK7\DACN2\ScoreFlow\backend\.env")
    DATABASE_URL = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Imports
from app.db.models import Match

# Windows Fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def check_match_counts():
    print(f"🔌 Connecting to: {DATABASE_URL.split('@')[-1]}") # Hide credentials
    
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        # Count Total
        result = await db.execute(select(func.count(Match.id)))
        total = result.scalar()
        print(f"📊 Total Matches in DB: {total}")

        # Group by Status
        print("\n📋 Validation by Status:")
        stmt = select(Match.status, func.count(Match.id)).group_by(Match.status)
        result = await db.execute(stmt)
        for status, count in result.fetchall():
            print(f"   - '{status}': {count}")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_match_counts())
