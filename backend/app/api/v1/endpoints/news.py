
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.db.database import get_db
from app.db.models import News

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_news(
    skip: int = 0, 
    limit: int = 20, 
    db: AsyncSession = Depends(get_db)
):
    """Get latest news"""
    try:
        result = await db.execute(
            select(News)
            .order_by(desc(News.published_at))
            .offset(skip)
            .limit(limit)
        )
        news_list = result.scalars().all()
        
        return [
            {
                "id": item.id,
                "title": item.title,
                "summary": item.summary,
                "url": item.url,
                "imageUrl": item.image_url,
                "source": item.source,
                "publishedAt": item.published_at,
                "timeAgo": item.published_at.isoformat() # Frontend can handle formatting
            }
            for item in news_list
        ]
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def sync_news_manual(db: AsyncSession = Depends(get_db)):
    """Trigger manual news sync"""
    try:
        from app.services.news_service import NewsService
        service = NewsService(db)
        count = await service.fetch_and_save_news()
        return {"success": True, "message": f"Synced {count} articles", "count": count}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear")
async def clear_news(db: AsyncSession = Depends(get_db)):
    """Delete all news"""
    try:
        from app.services.news_service import NewsService
        service = NewsService(db)
        await service.delete_all_news()
        return {"success": True, "message": "All news deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
