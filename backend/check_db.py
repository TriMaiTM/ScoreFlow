
import asyncio
from sqlalchemy import select, func
from datetime import datetime, date
from app.db.database import engine
from app.db.models import Match

async def check_data():
    async with engine.begin() as conn:
        # Check matches for today
        today = date.today()
        print(f"Checking matches for today: {today}")
        
        # Simple count query
        # access result using stream/execute
        # For simplicity in script, just use text or simple select
        pass

    # A simpler approach using session
    from app.db.database import get_db
    # We can't easily use get_db dependency here without context, 
    # but we can construct session manually if needed or just use engine.
    
    # Let's use the same async engine pattern
    import app.db.database as db_mod
    
    async with db_mod.AsyncSessionLocal() as session:
        # Check total matches
        result = await session.execute(select(func.count(Match.id)))
        total = result.scalar()
        print(f"Total Matches in DB: {total}")
        
        # Check today's matches
        # Note: Match.match_date is DateTime.
        # We want where date part is today.
        
        # Approximate check
        query = select(Match).limit(5)
        result = await session.execute(query)
        matches = result.scalars().all()
        print(f"Sample matches: {len(matches)}")
        for m in matches:
             print(f" - {m.home_team_id} vs {m.away_team_id} at {m.match_date}")

if __name__ == "__main__":
    asyncio.run(check_data())
