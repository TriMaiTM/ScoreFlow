
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Try loading from backend/.env
load_dotenv("backend/.env")

# Fallback or specific override
DATABASE_URL = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Try absolute path just in case
    load_dotenv(r"d:\HK7\DACN2\ScoreFlow\backend\.env")
    DATABASE_URL = os.getenv("DATABASE_URL_ASYNC") or os.getenv("DATABASE_URL")

print(f"DEBUG: Loaded URL: {DATABASE_URL}")

if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def update_schema():
    if not DATABASE_URL:
        print("❌ Error: Could not find DATABASE_URL in .env")
        return

    print("Migrating schema v2 (Standalone)...")
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        # Add avatar_url
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR;"))
            print("✅ Added avatar_url column.")
        except Exception as e:
            print(f"ℹ️  avatar_url might exist: {e}")

        # Add is_verified
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE;"))
            print("✅ Added is_verified column.")
        except Exception as e:
            print(f"ℹ️  is_verified might exist: {e}")

        # Add verification_token
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN verification_token VARCHAR;"))
            print("✅ Added verification_token column.")
        except Exception as e:
            print(f"ℹ️  verification_token might exist: {e}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(update_schema())
