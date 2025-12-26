import asyncio
from sqlalchemy import select, func
from app.db.database import AsyncSessionLocal
from app.db.models import User, Match, League

async def check_data():
    async with AsyncSessionLocal() as db:
        # Check counts
        u_count = await db.scalar(select(func.count(User.id)))
        m_count = await db.scalar(select(func.count(Match.id)))
        l_count = await db.scalar(select(func.count(League.id)))
        
        # Check for Superuser
        admin = await db.scalar(select(User).where(User.is_superuser == True))
        
        print(f"--- DB Status ---")
        print(f"Users: {u_count}")
        print(f"Matches: {m_count}")
        print(f"Leagues: {l_count}")
        print(f"Admin Exists: {'YES' if admin else 'NO'}")
        if admin:
            print(f"Admin Email: {admin.email}")

if __name__ == "__main__":
    asyncio.run(check_data())
