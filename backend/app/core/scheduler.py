"""
Background scheduler for automatic data updates
Uses APScheduler to run periodic tasks
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, date, timedelta
import logging

from app.db.database import AsyncSessionLocal
from app.services.data_sync import DataSyncService

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def seed_monthly_matches_job():
    """Job to seed 1 month of matches (2 weeks before + 2 weeks after today)
    Runs daily at midnight to ensure fresh data
    """
    try:
        logger.info("🌱 Running scheduled job: seed_monthly_matches")
        async with AsyncSessionLocal() as db:
            service = DataSyncService(db)
            
            # Calculate date range: 14 days before + 14 days after = 28 days
            today = date.today()
            date_from = (today - timedelta(days=14)).strftime("%Y-%m-%d")
            date_to = (today + timedelta(days=14)).strftime("%Y-%m-%d")
            
            logger.info(f"📅 Seeding matches from {date_from} to {date_to}")
            
            # Top 5 leagues: Premier League, La Liga, Bundesliga, Serie A, Ligue 1
            top_leagues = {
                2021: "Premier League",
                2014: "La Liga",
                2002: "Bundesliga",
                2019: "Serie A",
                2015: "Ligue 1"
            }
            
            total_synced = 0
            for league_id, league_name in top_leagues.items():
                try:
                    count = await service.sync_matches_date_range(
                        league_id=league_id,
                        date_from=date_from,
                        date_to=date_to
                    )
                    total_synced += count
                    logger.info(f"  ✅ {league_name}: {count} matches")
                except Exception as e:
                    logger.error(f"  ❌ {league_name} failed: {e}")
            
            logger.info(f"✅ Total seeded: {total_synced} matches for 1 month")
    except Exception as e:
        logger.error(f"❌ Error seeding monthly matches: {e}")


async def sync_realtime_scores_job():
    """Job to sync real-time scores for matches within the monthly window
    Runs every 5 minutes to keep scores up-to-date
    """
    try:
        logger.info("🔄 Running scheduled job: sync_realtime_scores")
        async with AsyncSessionLocal() as db:
            service = DataSyncService(db)
            
            # Sync today and tomorrow for real-time updates
            today = date.today()
            date_from = today.strftime("%Y-%m-%d")
            date_to = (today + timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Top 5 leagues
            top_leagues = [2021, 2014, 2002, 2019, 2015]
            
            total_updated = 0
            for league_id in top_leagues:
                try:
                    count = await service.sync_matches_date_range(
                        league_id=league_id,
                        date_from=date_from,
                        date_to=date_to
                    )
                    total_updated += count
                except Exception as e:
                    logger.error(f"  ❌ League {league_id} failed: {e}")
            
            logger.info(f"✅ Updated {total_updated} matches (real-time)")
    except Exception as e:
        logger.error(f"❌ Error syncing real-time scores: {e}")


async def sync_today_matches_job():
    """Job to sync today's matches for popular leagues"""
    try:
        logger.info("🔄 Running scheduled job: sync_today_matches")
        async with AsyncSessionLocal() as db:
            service = DataSyncService(db)
            
            # Premier League, La Liga, Bundesliga, Serie A, Ligue 1
            popular_leagues = [2021, 2014, 2002, 2019, 2015]
            
            total_synced = 0
            for league_id in popular_leagues:
                try:
                    count = await service.sync_matches(league_id, days_ahead=1)
                    total_synced += count
                    logger.info(f"  ✅ League {league_id}: {count} matches")
                except Exception as e:
                    logger.error(f"  ❌ League {league_id} failed: {e}")
            
            logger.info(f"✅ Total synced: {total_synced} matches")
    except Exception as e:
        logger.error(f"❌ Error syncing today's matches: {e}")


async def sync_standings_job():
    """Job to sync league standings/tables"""
    try:
        logger.info("🔄 Running scheduled job: sync_standings")
        async with AsyncSessionLocal() as db:
            service = DataSyncService(db)
            
            popular_leagues = [2021, 2014, 2002, 2019, 2015]
            
            for league_id in popular_leagues:
                try:
                    count = await service.sync_standings(league_id)
                    logger.info(f"  ✅ League {league_id}: {count} teams")
                except Exception as e:
                    logger.error(f"  ❌ League {league_id} failed: {e}")
    except Exception as e:
        logger.error(f"❌ Error syncing standings: {e}")


async def sync_upcoming_matches_job():
    """Job to sync upcoming matches (next 7 days)"""
    try:
        logger.info("🔄 Running scheduled job: sync_upcoming_matches")
        async with AsyncSessionLocal() as db:
            service = DataSyncService(db)
            
            popular_leagues = [2021, 2014, 2002, 2019, 2015]
            
            total_synced = 0
            for league_id in popular_leagues:
                try:
                    count = await service.sync_matches(league_id, days_ahead=7)
                    total_synced += count
                except Exception as e:
                    logger.error(f"  ❌ League {league_id} failed: {e}")
            
            logger.info(f"✅ Total synced: {total_synced} upcoming matches")
    except Exception as e:
        logger.error(f"❌ Error syncing upcoming matches: {e}")


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
    
    scheduler.start()
    logger.info("📅 Scheduler started successfully")
    logger.info("  - Monthly seed (2 weeks ± today): Daily at midnight")
    logger.info("  - Real-time scores: Every 5 minutes")
    logger.info("  - Standings: Twice daily (6 AM, 6 PM)")
    logger.info("  - Upcoming matches: Every 6 hours")


def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.shutdown()
    logger.info("📅 Scheduler stopped")
