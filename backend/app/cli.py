"""
Management commands for ScoreFlow backend
Run with: python -m app.cli <command>
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.services.data_sync import DataSyncService


async def sync_leagues():
    """Sync leagues from API"""
    async with AsyncSessionLocal() as db:
        service = DataSyncService(db)
        count = await service.sync_leagues()
        print(f"✅ Synced {count} leagues")


async def sync_matches(league_id: int, days: int = 7):
    """Sync matches for a league"""
    async with AsyncSessionLocal() as db:
        service = DataSyncService(db)
        count = await service.sync_matches(league_id, days)
        print(f"✅ Synced {count} matches for league {league_id}")


async def sync_standings(league_id: int):
    """Sync standings/table for a league"""
    async with AsyncSessionLocal() as db:
        service = DataSyncService(db)
        count = await service.sync_standings(league_id)
        print(f"✅ Synced standings for league {league_id} ({count} teams)")


async def update_live():
    """Update live match scores"""
    async with AsyncSessionLocal() as db:
        service = DataSyncService(db)
        count = await service.update_live_matches()
        print(f"✅ Updated {count} live matches")


async def seed_data():
    """Seed initial data for testing"""
    print("🌱 Seeding initial data...")
    
    # Sync popular leagues
    await sync_leagues()
    
    # Sync matches for Premier League (2021), La Liga (2014), etc.
    popular_leagues = [2021, 2014, 2002, 2019, 2015]  # Football-Data.org IDs
    
    for league_id in popular_leagues:
        try:
            await sync_matches(league_id, days=14)
        except Exception as e:
            print(f"⚠️  Failed to sync league {league_id}: {e}")
    
    print("✅ Seeding completed!")


async def seed_past_matches(league_id: int, days_back: int = 30):
    """Seed past FINISHED matches for recent form testing"""
    print(f"🌱 Seeding past matches for league {league_id} ({days_back} days back)...")
    async with AsyncSessionLocal() as db:
        service = DataSyncService(db)
        count = await service.sync_past_matches(league_id, days_back)
        print(f"✅ Synced {count} past matches")




async def seed_full():
    """
    Seed/Sync all data for ALL leagues in DB:
    - Past 14 days matches
    - Upcoming 14 days matches
    - Standings
    """
    print("🚀 Starting full seed (14 days back/forward) for ALL leagues...")
    
    # 1. Sync Leagues first
    await sync_leagues()
    
    async with AsyncSessionLocal() as db:
        # Get all leagues
        from app.db.models import League
        result = await db.execute(select(League))
        leagues = result.scalars().all()
        
        print(f"📋 Found {len(leagues)} leagues to process...")
        
        for league in leagues:
            league_id = league.external_id
            print(f"\n⚽ Processing {league.name} (ID: {league_id})...")
            try:
                # Sync past 14 days
                await seed_past_matches(league_id, days_back=14)
                
                # Sync upcoming 14 days
                await sync_matches(league_id, days=14)
                
                # Sync standings
                await sync_standings(league_id)
                
            except Exception as e:
                print(f"⚠️  Error processing league {league_id}: {e}")
            
            # Rate limit: Free tier allows 10 req/min (1 req every 6s)
            # We make 3 requests per league (3 * 6s = 18s required)
            # Adding extra buffer to be safe
            print("⏳ Waiting 25s to respect rate limit (Free tier: 10 req/min)...")
            await asyncio.sleep(20)
            
    print("\n✅ Full seed completed successfully!")


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.cli <command>")
        print("\nAvailable commands:")
        print("  sync-leagues                      - Sync all leagues from API")
        print("  sync-matches <league_id> [days]   - Sync upcoming matches")
        print("  sync-standings <league_id>        - Sync standings/table")
        print("  update-live                       - Update live match scores")
        print("  seed                              - Seed initial data")
        print("  seed-past-matches <league_id> [days_back] - Seed FINISHED matches")
        print("  seed-full                         - Sync all data (-14/+14 days) for 5 major leagues")
        print("\nExamples:")
        print("  python -m app.cli seed-past-matches 2021 30   # Seed last 30 days of Premier League")
        print("  python -m app.cli seed-full                   # Full sync for dev/demo")
        return
    
    command = sys.argv[1]
    
    if command == "sync-leagues":
        asyncio.run(sync_leagues())
    elif command == "sync-matches":
        if len(sys.argv) < 3:
            print("Error: league_id required")
            return
        league_id = int(sys.argv[2])
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        asyncio.run(sync_matches(league_id, days))
    elif command == "sync-standings":
        if len(sys.argv) < 3:
            print("Error: league_id required")
            return
        league_id = int(sys.argv[2])
        asyncio.run(sync_standings(league_id))
    elif command == "update-live":
        asyncio.run(update_live())
    elif command == "seed":
        asyncio.run(seed_data())
    elif command == "seed-past-matches":
        if len(sys.argv) < 3:
            print("Error: league_id required")
            print("Usage: python -m app.cli seed-past-matches <league_id> [days_back]")
            return
        league_id = int(sys.argv[2])
        days_back = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        asyncio.run(seed_past_matches(league_id, days_back))
    elif command == "seed-full":
        asyncio.run(seed_full())
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
