import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import TeamStats

async def main():
    async with AsyncSessionLocal() as db:
        for tid in [162, 96]:
            result = await db.execute(select(TeamStats).where(TeamStats.team_id == tid))
            stats = result.scalar_one_or_none()
            elo = stats.elo_rating if stats else "No Stats"
            print(f"Team {tid} Elo in DB: {elo}")

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.getcwd())
    asyncio.run(main())
