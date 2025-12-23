
import asyncio
from app.db.database import AsyncSessionLocal
from app.db.models import User
from sqlalchemy import select

async def cleanup():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "debug_user@example.com"))
        user = result.scalar_one_or_none()
        if user:
            print(f"Deleting debug user {user.email}")
            await db.delete(user)
            await db.commit()

if __name__ == "__main__":
    asyncio.run(cleanup())
