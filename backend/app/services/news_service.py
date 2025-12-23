
import feedparser
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from email.utils import parsedate_to_datetime

from app.db.models import News

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.feeds = [
            {"name": "VNExpress", "url": "https://vnexpress.net/rss/the-thao.rss"},
            {"name": "Thanh Niên", "url": "https://thanhnien.vn/rss/the-thao.rss"},
            {"name": "24h Bóng Đá", "url": "https://cdn.24h.com.vn/upload/rss/bongda.rss"}
        ]

    async def fetch_and_save_news(self):
        """Fetch news from all configured feeds and save to DB"""
        total_added = 0
        
        for feed_info in self.feeds:
            try:
                logger.info(f"📰 Fetching news from {feed_info['name']}...")
                feed = feedparser.parse(feed_info["url"])
                
                for entry in feed.entries:
                    try:
                        # Check if already exists (primary check)
                        result = await self.db.execute(select(News).where(News.url == entry.link))
                        if result.scalar_one_or_none():
                            continue
                            
                        # Parse date
                        published_at = datetime.utcnow()
                        if hasattr(entry, "published_parsed") and entry.published_parsed:
                             try:
                                 # struct_time to datetime
                                 import time
                                 from datetime import timedelta
                                 ts = time.mktime(entry.published_parsed)
                                 published_at = datetime.fromtimestamp(ts)
                             except:
                                 pass
                        
                        # Extract image
                        image_url = None
                        if "media_content" in entry:
                            image_url = entry.media_content[0]["url"]
                        elif "links" in entry:
                             for link in entry.links:
                                 if link.type.startswith('image/'):
                                     image_url = link.href
                                     break
                        
                        # Try getting image from summary if not found
                        if not image_url and "summary" in entry:
                            try:
                                from bs4 import BeautifulSoup
                                soup = BeautifulSoup(entry.summary, 'html.parser')
                                img = soup.find('img')
                                if img:
                                    image_url = img['src']
                            except ImportError:
                                pass # bs4 not installed, skip image extraction from summary
                        
                        # Clean summary
                        summary = entry.summary
                        if summary:
                             try:
                                 from bs4 import BeautifulSoup
                                 soup = BeautifulSoup(summary, 'html.parser')
                                 summary = soup.get_text()[:200] + "..."
                             except ImportError:
                                 # Fallback cleanup if bs4 missing
                                 import re
                                 summary = re.sub('<[^<]+?>', '', summary)[:200] + "..."
                        
                        # Decode HTML entities (fixes &agrave; etc.)
                        import html
                        title = html.unescape(entry.title)
                        if summary:
                            summary = html.unescape(summary)

                        news_item = News(
                            title=title,
                            summary=summary,
                            url=entry.link,
                            image_url=image_url,
                            source=feed_info["name"],
                            published_at=published_at
                        )
                        
                        # Add and commit individually to prevent one fail blocking others
                        # This is slower but safer for sync
                        self.db.add(news_item)
                        await self.db.commit()
                        total_added += 1
                        
                    except Exception as e:
                        # Rollback only if the inner transaction failed
                        await self.db.rollback()
                        # If it's a unique constraint violation that slipped through, we just ignore it
                        if "unique constraint" not in str(e).lower() and "integrity" not in str(e).lower():
                            logger.error(f"⚠️ Error processing entry {entry.get('title', 'Unknown')}: {e}")
                            
            except Exception as e:
                logger.error(f"❌ Error fetching from {feed_info['name']}: {e}")
                
        return total_added

    async def delete_all_news(self):
        """Delete all news articles"""
        from sqlalchemy import delete
        await self.db.execute(delete(News))
        await self.db.commit()
