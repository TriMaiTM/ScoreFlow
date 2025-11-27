"""
Enhanced data service combining Football-Data.org + API-Football
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from app.services.api_football_client import get_api_football_client
from app.services.cache import RedisCache
from app.db.models import Match, Team, TeamStats
from app.core.config import settings

logger = logging.getLogger(__name__)


class EnhancedDataService:
    """Service to get enhanced match and team data"""
    
    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.api_football_enabled = settings.API_FOOTBALL_ENABLED
        
        if self.api_football_enabled and settings.API_FOOTBALL_KEY:
            self.api_football = get_api_football_client(settings.API_FOOTBALL_KEY)
        else:
            self.api_football = None
            logger.info("API-Football is disabled or no API key provided")
    
    async def get_team_statistics(
        self, 
        team_id: int, 
        league_id: int, 
        season: int,
        db: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """
        Get team statistics with caching
        Falls back to database if API-Football is unavailable
        """
        cache_key = f"team_stats:{team_id}:{league_id}:{season}"
        
        # Check cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Try API-Football if enabled
        if self.api_football:
            try:
                stats = await self.api_football.get_team_statistics(team_id, league_id, season)
                if stats:
                    # Cache for 1 hour
                    await self.cache.set(cache_key, stats, expire=3600)
                    return stats
            except Exception as e:
                logger.error(f"API-Football failed for team stats: {e}")
        
        # Fallback to database
        result = await db.execute(
            select(TeamStats).where(
                TeamStats.team_id == team_id
            ).order_by(TeamStats.updated_at.desc()).limit(1)
        )
        team_stats = result.scalar_one_or_none()
        
        if team_stats:
            # Calculate goals per match
            goals_per_match = 0
            goals_conceded_per_match = 0
            if team_stats.matches_played and team_stats.matches_played > 0:
                goals_per_match = round(team_stats.goals_scored / team_stats.matches_played, 2)
                goals_conceded_per_match = round(team_stats.goals_conceded / team_stats.matches_played, 2)
            
            stats = {
                "teamId": team_id,
                "leagueId": league_id,
                "season": season,
                "form": team_stats.form or "",
                "fixtures": {
                    "played": {"total": team_stats.matches_played or 0},
                    "wins": {"total": team_stats.wins or 0},
                    "draws": {"total": team_stats.draws or 0},
                    "loses": {"total": team_stats.losses or 0},
                },
                "goals": {
                    "for": {
                        "total": {"total": team_stats.goals_scored or 0},
                        "average": {"total": str(goals_per_match)},
                    },
                    "against": {
                        "total": {"total": team_stats.goals_conceded or 0},
                        "average": {"total": str(goals_conceded_per_match)},
                    },
                },
                "cleanSheet": {"total": team_stats.clean_sheets or 0},
            }
            # Cache for 30 minutes
            await self.cache.set(cache_key, stats, expire=1800)
            return stats
        
        return None
    
    async def get_head_to_head(
        self,
        team1_id: int,
        team2_id: int,
        db: AsyncSession,
        last: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get head-to-head matches between two teams
        """
        cache_key = f"h2h:{team1_id}:{team2_id}:{last}"
        
        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        # Try API-Football if enabled
        if self.api_football:
            try:
                h2h_matches = await self.api_football.get_head_to_head(team1_id, team2_id, last)
                if h2h_matches:
                    # Cache for 6 hours
                    await self.cache.set(cache_key, h2h_matches, expire=21600)
                    return h2h_matches
            except Exception as e:
                logger.error(f"API-Football failed for H2H: {e}")
        
        # Fallback to database
        from sqlalchemy import and_, or_
        from sqlalchemy.orm import selectinload
        
        query = (
            select(Match)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.league)
            )
            .where(
                and_(
                    Match.status == "finished",
                    or_(
                        and_(Match.home_team_id == team1_id, Match.away_team_id == team2_id),
                        and_(Match.home_team_id == team2_id, Match.away_team_id == team1_id)
                    )
                )
            )
            .order_by(Match.match_date.desc())
            .limit(last)
        )
        
        result = await db.execute(query)
        matches = result.scalars().all()
        
        h2h_data = [
            {
                "fixtureId": match.id,
                "date": match.match_date.isoformat(),
                "homeTeam": {
                    "id": match.home_team.id,
                    "name": match.home_team.name,
                    "logo": match.home_team.logo,
                },
                "awayTeam": {
                    "id": match.away_team.id,
                    "name": match.away_team.name,
                    "logo": match.away_team.logo,
                },
                "score": {
                    "home": match.home_score,
                    "away": match.away_score,
                },
                "winner": (
                    True if match.home_score > match.away_score else
                    False if match.home_score < match.away_score else
                    None
                ),
            }
            for match in matches
        ]
        
        # Cache for 6 hours
        await self.cache.set(cache_key, h2h_data, expire=21600)
        return h2h_data
    
    async def get_match_statistics(
        self,
        match_id: int,
        external_fixture_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed match statistics
        Only available from API-Football
        """
        if not self.api_football or not external_fixture_id:
            return None
        
        cache_key = f"match_stats:{match_id}"
        
        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            stats = await self.api_football.get_match_statistics(external_fixture_id)
            if stats:
                # Cache for 15 minutes (live matches change frequently)
                await self.cache.set(cache_key, stats, expire=900)
                return stats
        except Exception as e:
            logger.error(f"Failed to get match statistics: {e}")
        
        return None
    
    async def get_ai_prediction(
        self,
        match_id: int,
        external_fixture_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get AI prediction from API-Football
        Falls back to our ML model if unavailable
        """
        if not self.api_football or not external_fixture_id:
            return None
        
        cache_key = f"api_prediction:{match_id}"
        
        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            prediction = await self.api_football.get_predictions(external_fixture_id)
            if prediction:
                # Cache for 24 hours (predictions don't change)
                await self.cache.set(cache_key, prediction, expire=86400)
                return prediction
        except Exception as e:
            logger.error(f"Failed to get API prediction: {e}")
        
        return None
    
    async def get_team_injuries(
        self,
        team_id: int,
        league_id: int,
        season: int
    ) -> List[Dict[str, Any]]:
        """
        Get team injuries
        Only available from API-Football
        """
        if not self.api_football:
            return []
        
        cache_key = f"injuries:{team_id}:{league_id}:{season}"
        
        # Check cache
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            injuries = await self.api_football.get_team_injuries(team_id, league_id, season)
            if injuries:
                # Cache for 6 hours
                await self.cache.set(cache_key, injuries, expire=21600)
                return injuries
        except Exception as e:
            logger.error(f"Failed to get team injuries: {e}")
        
        return []
    
    async def check_api_status(self) -> Dict[str, Any]:
        """Check API-Football status and remaining requests"""
        if not self.api_football:
            return {
                "enabled": False,
                "message": "API-Football is disabled"
            }
        
        try:
            status = await self.api_football.check_api_status()
            return {
                "enabled": True,
                "requests": status.get("requests", {}),
                "email": status.get("email", ""),
            }
        except Exception as e:
            logger.error(f"Failed to check API status: {e}")
            return {
                "enabled": True,
                "error": str(e)
            }


# Dependency injection
async def get_enhanced_data_service(cache: RedisCache) -> EnhancedDataService:
    """Get enhanced data service instance"""
    return EnhancedDataService(cache)
