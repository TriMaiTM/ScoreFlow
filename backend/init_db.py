"""
Script to initialize database tables
Run: python init_db.py
"""
import asyncio
from app.db.database import engine
from app.db.models import Base


async def init_db():
    """Create all database tables"""
    print("🔨 Creating database tables...")
    
    async with engine.begin() as conn:
        # Drop all tables (nếu muốn reset)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created successfully!")
    print("\nTables created:")
    print("  - users")
    print("  - leagues")
    print("  - teams")
    print("  - matches")
    print("  - predictions")
    print("  - team_stats")
    print("\nBây giờ có thể chạy: python -m app.cli seed")


if __name__ == "__main__":
    asyncio.run(init_db())
