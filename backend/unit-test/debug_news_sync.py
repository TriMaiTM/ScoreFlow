import asyncio
import logging
import sys
import os

# Add current directory to path so imports work
sys.path.append(os.getcwd())

from app.db.database import AsyncSessionLocal
from app.services.news_service import NewsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_news_sync():
    print("🚀 Starting Main News Sync Debug...")
    async with AsyncSessionLocal() as db:
        service = NewsService(db)
        print("📰 Initialized NewsService. Fetching news...")
        try:
            count = await service.fetch_and_save_news()
            print(f"✅ Successfully synced {count} articles.")
        except Exception as e:
            print(f"❌ Synchronization FAILED: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debug_news_sync())
