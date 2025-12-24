"""
Background scheduler for automatic data updates
Uses APScheduler to run periodic tasks
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, date, timedelta
import logging
import asyncio

from app.db.database import AsyncSessionLocal
from app.services.data_sync import DataSyncService

logger = logging.getLogger(__name__)

# Limit max concurrent jobs to 2
MAX_CONCURRENT_JOBS = 2
job_semaphore = asyncio.Semaphore(MAX_CONCURRENT_JOBS)

scheduler = AsyncIOScheduler()


async def seed_monthly_matches_job():
    """Job to seed 1 month of matches (2 weeks before + 2 weeks after today)
    Runs daily at midnight to ensure fresh data
    """
    try:
        async with job_semaphore:
            logger.info("🌱 Running scheduled job: seed_monthly_matches")
            async with AsyncSessionLocal() as db:
                service = DataSyncService(db)
                
                # Calculate date range: 14 days before + 14 days after = 28 days
                today = date.today()
                date_from = (today - timedelta(days=14)).strftime("%Y-%m-%d")
                date_to = (today + timedelta(days=14)).strftime("%Y-%m-%d")
                
                logger.info(f"📅 Seeding matches from {date_from} to {date_to}")
                
                # Get ALL leagues from DB
                from sqlalchemy import select
                from app.db.models import League
                result = await db.execute(select(League))
                leagues = result.scalars().all()
                
                logger.info(f"📋 Processing {len(leagues)} leagues...")
                
                total_synced = 0
                for league in leagues:
                    try:
                        count = await service.sync_matches_date_range(
                            league_id=league.external_id,
                            date_from=date_from,
                            date_to=date_to
                        )
                        total_synced += count
                        logger.info(f"  ✅ {league.name}: {count} matches")
                        
                        # Rate limit: 10 req/min -> 1 req every 6s (now 20s for safety)
                        await asyncio.sleep(20)
                        
                    except Exception as e:
                        logger.error(f"  ❌ {league.name} failed: {e}")
                
                logger.info(f"✅ Total seeded: {total_synced} matches for 1 month")
    except Exception as e:
        logger.error(f"❌ Error seeding monthly matches: {e}")


async def sync_realtime_scores_job():
    """Job to sync real-time scores for matches within the monthly window
    Runs every 5 minutes to keep scores up-to-date
    """
    try:
        async with job_semaphore:
            logger.info("🔄 Running scheduled job: sync_realtime_scores")
            async with AsyncSessionLocal() as db:
                service = DataSyncService(db)
                
                # Sync yesterday, today, and tomorrow to catch all recent/ongoing matches
                today = date.today()
                date_from = (today - timedelta(days=1)).strftime("%Y-%m-%d")
                date_to = (today + timedelta(days=1)).strftime("%Y-%m-%d")
                
                # Get leagues that have matches in this date range
                from sqlalchemy import select
                from app.db.models import Match, League
                
                # Query: Select distinct league external_ids that have matches in range
                result = await db.execute(
                    select(League.external_id)
                    .join(Match)
                    .where(
                        Match.match_date >= datetime.strptime(date_from, "%Y-%m-%d"),
                        Match.match_date < datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
                    )
                    .distinct()
                )
                active_leagues = result.scalars().all()
                
                logger.info(f"🎯 Syncing {len(active_leagues)} active leagues: {active_leagues}")
                
                total_updated = 0
                for league_id in active_leagues:
                    try:
                        count = await service.sync_matches_date_range(
                            league_id=league_id,
                            date_from=date_from,
                            date_to=date_to
                        )
                        total_updated += count
                        
                        # Rate limit: Sleep 20s between leagues to avoid 429
                        await asyncio.sleep(20)
                        
                    except Exception as e:
                        logger.error(f"  ❌ League {league_id} failed: {e}")
                
                logger.info(f"✅ Updated {total_updated} matches (real-time)")
    except Exception as e:
        logger.error(f"❌ Error syncing real-time scores: {e}")


async def sync_today_matches_job():
    """Job to sync today's matches for ALL leagues"""
    try:
        async with job_semaphore:
            logger.info("🔄 Running scheduled job: sync_today_matches")
            async with AsyncSessionLocal() as db:
                service = DataSyncService(db)
                
                # Get ALL leagues
                from sqlalchemy import select
                from app.db.models import League
                result = await db.execute(select(League))
                leagues = result.scalars().all()
                
                total_synced = 0
                for league in leagues:
                    try:
                        count = await service.sync_matches(league.external_id, days_ahead=1)
                        total_synced += count
                        logger.info(f"  ✅ {league.name}: {count} matches")
                        
                        # Rate limit
                        await asyncio.sleep(20)
                        
                    except Exception as e:
                        logger.error(f"  ❌ {league.name} failed: {e}")
                
                logger.info(f"✅ Total synced: {total_synced} matches")
    except Exception as e:
        logger.error(f"❌ Error syncing today's matches: {e}")


async def sync_standings_job():
    """Job to sync league standings/tables"""
    try:
        async with job_semaphore:
            logger.info("🔄 Running scheduled job: sync_standings")
            async with AsyncSessionLocal() as db:
                service = DataSyncService(db)
                
                # Get ALL leagues
                from sqlalchemy import select
                from app.db.models import League
                result = await db.execute(select(League))
                leagues = result.scalars().all()
                
                for league in leagues:
                    try:
                        count = await service.sync_standings(league.external_id)
                        logger.info(f"  ✅ {league.name}: {count} teams")
                        
                        # Rate limit
                        await asyncio.sleep(20)
                        
                    except Exception as e:
                        logger.error(f"  ❌ {league.name} failed: {e}")
    except Exception as e:
        logger.error(f"❌ Error syncing standings: {e}")


async def sync_upcoming_matches_job():
    """Job to sync upcoming matches (next 7 days)"""
    try:
        async with job_semaphore:
            logger.info("🔄 Running scheduled job: sync_upcoming_matches")
            async with AsyncSessionLocal() as db:
                service = DataSyncService(db)
                
                # Get ALL leagues
                from sqlalchemy import select
                from app.db.models import League
                result = await db.execute(select(League))
                leagues = result.scalars().all()
                
                total_synced = 0
                for league in leagues:
                    try:
                        count = await service.sync_matches(league.external_id, days_ahead=7)
                        total_synced += count
                        
                        # Rate limit
                        await asyncio.sleep(20)
                        
                    except Exception as e:
                        logger.error(f"  ❌ {league.name} failed: {e}")
                
                logger.info(f"✅ Total synced: {total_synced} upcoming matches")
    except Exception as e:
        logger.error(f"❌ Error syncing upcoming matches: {e}")


async def sync_news_job():
    """Job to fetch latest football news from RSS feeds"""
    try:
        async with job_semaphore:
            logger.info("📰 Running scheduled job: sync_news")
            async with AsyncSessionLocal() as db:
                from app.services.news_service import NewsService
                service = NewsService(db)
                
                count = await service.fetch_and_save_news()
                logger.info(f"✅ News sync complete: {count} new articles")
            
    except Exception as e:
        logger.error(f"❌ Error syncing news: {e}")


def start_scheduler():
    """Start the background scheduler"""
    
    # Seed 1 month of matches daily at midnight (2 weeks before + 2 weeks after)
    scheduler.add_job(
        seed_monthly_matches_job,
        trigger=CronTrigger(hour="0", minute="0"),
        id="seed_monthly_matches",
        name="Seed monthly matches (1 month window)",
        replace_existing=True
    )
    
    # Sync real-time scores every 5 minutes (today + tomorrow)
    scheduler.add_job(
        sync_realtime_scores_job,
        trigger=IntervalTrigger(minutes=5),
        id="sync_realtime_scores",
        name="Sync real-time scores",
        replace_existing=True
    )
    
    # Sync standings twice daily (6 AM and 6 PM)
    scheduler.add_job(
        sync_standings_job,
        trigger=CronTrigger(hour="6,18", minute="0"),
        id="sync_standings",
        name="Sync league standings",
        replace_existing=True
    )
    
    # Sync upcoming matches every 6 hours
    scheduler.add_job(
        sync_upcoming_matches_job,
        trigger=IntervalTrigger(hours=6),
        id="sync_upcoming_matches",
        name="Sync upcoming matches",
        replace_existing=True
    )
    
    # Sync news every 30 minutes
    scheduler.add_job(
        sync_news_job,
        trigger=IntervalTrigger(minutes=30),
        id="sync_news",
        name="Sync football news",
        replace_existing=True
    )

    scheduler.start()
    logger.info("📅 Scheduler started successfully")
    logger.info("  - Monthly seed (2 weeks ± today): Daily at midnight")
    logger.info("  - Real-time scores: Every 5 minutes")
    logger.info("  - Standings: Twice daily (6 AM, 6 PM)")
    logger.info("  - Upcoming matches: Every 6 hours")
    logger.info("  - News: Every 30 minutes")


def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.shutdown()
    logger.info("📅 Scheduler stopped")
