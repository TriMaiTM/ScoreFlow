import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import Match

async def main():
    async with AsyncSessionLocal() as db:
        # Find match with ID 2481 (as seen in log "match 2481")
        # Or find by date if ID is not 2481
        match = await db.scalar(select(Match).where(Match.id == 2481))
        
        if match:
            print(f"Match ID: {match.id}")
            print(f"Home Team ID: {match.home_team_id}")
            print(f"Away Team ID: {match.away_team_id}")
        else:
            print("Match 2481 not found via ID. Checking logs context.")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(main())
