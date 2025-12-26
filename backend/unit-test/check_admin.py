from app.db.database import AsyncSessionLocal
from app.db.models import User
from sqlalchemy import select
import asyncio

async def check_admin():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.is_superuser == True))
        admin = result.scalar_one_or_none()
        if admin:
            print(f"✅ Found Admin: {admin.email}")
        else:
            print("❌ No Admin found")

if __name__ == "__main__":
    asyncio.run(check_admin())
