
import asyncio
from sqlalchemy import text
from app.db.database import engine

async def update_schema():
    print("Migrating schema v2...")
    async with engine.begin() as conn:
        # Add avatar_url
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR;"))
            print("Added avatar_url column.")
        except Exception as e:
            print(f"avatar_url might exist: {e}")

        # Add is_verified
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE;"))
            print("Added is_verified column.")
        except Exception as e:
            print(f"is_verified might exist: {e}")

        # Add verification_token
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN verification_token VARCHAR;"))
            print("Added verification_token column.")
        except Exception as e:
            print(f"verification_token might exist: {e}")

if __name__ == "__main__":
    asyncio.run(update_schema())
