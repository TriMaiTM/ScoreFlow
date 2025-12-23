
import asyncio
import httpx
from sqlalchemy import select, func
from app.db.database import AsyncSessionLocal
from app.db.models import Match
from app.core.config import settings

async def check_status():
    print("--- DIAGNOSTICS ---")
    
    # 1. Check DB
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(func.count(Match.id)))
            count = result.scalar()
            print(f"✅ Database Connection: OK")
            print(f"📊 Total Matches in DB: {count}")
    except Exception as e:
        print(f"❌ Database Error: {e}")

    # 2. Check API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:8000/api/v1/health")
            print(f"✅ API Health Check: {response.status_code} - {response.json()}")
            
            # Check matches endpoint
            response = await client.get("http://127.0.0.1:8000/api/v1/matches/live")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Match API (/live): OK - Found {len(data.get('data', []))} live matches")
            else:
                print(f"❌ Match API Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ API Connection Error: {e}")
        print("   (Ensure backend is running on port 8000)")

if __name__ == "__main__":
    asyncio.run(check_status())
