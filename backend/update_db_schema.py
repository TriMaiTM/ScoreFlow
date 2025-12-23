
import asyncio
from sqlalchemy import text
from app.db.database import engine

async def add_superuser_column():
    print("🔄 Adding is_superuser column to users table...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE"))
            print("✅ Column added successfully")
        except Exception as e:
            if "duplicate column" in str(e):
                print("⚠️ Column already exists, skipping")
            else:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(add_superuser_column())
