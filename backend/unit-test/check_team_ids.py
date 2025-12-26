import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import Team

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Team).limit(20))
        teams = result.scalars().all()
        
        import json
        
        team_list = []
        for t in teams:
            team_list.append({
                "id": t.id,
                "name": t.name,
                "external_id": t.external_id
            })
        print(json.dumps(team_list, indent=2))

if __name__ == "__main__":
    import sys
    import os
    # Add project root to path
    sys.path.append(os.getcwd())
    
    # Run async main
    asyncio.run(main())
