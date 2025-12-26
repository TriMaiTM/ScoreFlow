
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
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
from app.services.news_service import NewsService

# Windows Asyncio Fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def sync_news():
    print("📰 Starting Manual News Sync...")
    if not DATABASE_URL:
        print("❌ Error: No DATABASE_URL defined.")
        return

    print(f"🔌 Connecting to DB...")
    engine = create_async_engine(DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        service = NewsService(db)
        print("⏳ Fetching news from RSS feeds...")
        try:
            count = await service.fetch_and_save_news()
            print(f"✅ News Sync Complete! Added {count} new articles.")
        except Exception as e:
            print(f"❌ Error syncing news: {e}")
            import traceback
            traceback.print_exc()

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(sync_news())
