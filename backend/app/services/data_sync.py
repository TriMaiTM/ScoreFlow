from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from typing import List, Dict

from app.db.models import Team, League, Match, TeamStats, Standing
from app.services.football_api import get_football_api_client


class DataSyncService:
    """Service to sync data from external API to database"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_client = get_football_api_client()
    
    async def sync_leagues(self) -> int:
        """Sync leagues/competitions from API"""
        competitions = await self.api_client.get_competitions()
        synced_count = 0
        
        for comp in competitions:
            # Check if league exists
            result = await self.db.execute(
                select(League).where(League.external_id == comp["id"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                league = League(
                    name=comp["name"],
                    country=comp.get("area", {}).get("name", "International"),
                    logo=comp.get("emblem", ""),
                    season=int(comp.get("currentSeason", {}).get("startDate", "")[:4]),
                    external_id=comp["id"]
                )
                self.db.add(league)
                synced_count += 1
        
        await self.db.commit()
        return synced_count
    
    async def sync_team(self, team_data: Dict) -> Team:
        """Sync a single team"""
        result = await self.db.execute(
            select(Team).where(Team.external_id == team_data["id"])
        )
        team = result.scalar_one_or_none()
        
        if not team:
            team = Team(
                name=team_data["name"],
                short_name=team_data.get("shortName", team_data["name"][:3]),
                logo=team_data.get("crest", ""),
                country=team_data.get("area", {}).get("name", ""),
                external_id=team_data["id"]
            )
            self.db.add(team)
            await self.db.commit()
            await self.db.refresh(team)
        
        return team
    
    async def sync_past_matches(self, league_id: int, days_back: int = 30) -> int:
        """Sync past FINISHED matches for recent form testing"""
        from datetime import timedelta
        
        date_to = datetime.now().strftime("%Y-%m-%d")
        date_from = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        print(f"📅 Fetching matches from {date_from} to {date_to}")
        
        matches_data = await self.api_client.get_matches(
            competition_id=league_id,
            date_from=date_from,
            date_to=date_to
        )
        
        synced_count = 0
        finished_count = 0
        
        for match_data in matches_data:
            # Only process FINISHED matches
            if match_data["status"] not in ["FINISHED", "AWARDED"]:
                continue
            
            finished_count += 1
            
            # Sync teams first
            home_team = await self.sync_team(match_data["homeTeam"])
            away_team = await self.sync_team(match_data["awayTeam"])
            
            # Get league from DB
            result = await self.db.execute(
                select(League).where(League.external_id == league_id)
            )
            league = result.scalar_one_or_none()
            
            if not league:
                continue
            
            # Check if match exists
            result = await self.db.execute(
                select(Match).where(Match.external_id == match_data["id"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                match = Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    league_id=league.id,
                    match_date=(datetime.fromisoformat(match_data["utcDate"].replace("Z", "+00:00")) + timedelta(hours=7)).replace(tzinfo=None),
                    status="FINISHED",  # Force FINISHED status
                    home_score=match_data["score"]["fullTime"]["home"],
                    away_score=match_data["score"]["fullTime"]["away"],
                    venue=match_data.get("venue", ""),
                    round=str(match_data.get("matchday", "")),
                    external_id=match_data["id"]
                )
                self.db.add(match)
                synced_count += 1
            else:
                # Update existing match
                existing.match_date = (datetime.fromisoformat(match_data["utcDate"].replace("Z", "+00:00")) + timedelta(hours=7)).replace(tzinfo=None)
                existing.status = "FINISHED"
                existing.home_score = match_data["score"]["fullTime"]["home"]
                existing.away_score = match_data["score"]["fullTime"]["away"]
                synced_count += 1
        
        await self.db.commit()
        print(f"📊 Found {finished_count} finished matches, synced {synced_count} new matches")
        return synced_count
    
    async def sync_matches(self, league_id: int, days_ahead: int = 7) -> int:
        """Sync upcoming/scheduled matches for a league"""
        from datetime import timedelta
        
        date_from = datetime.now().strftime("%Y-%m-%d")
        date_to = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        matches_data = await self.api_client.get_matches(
            competition_id=league_id,
            date_from=date_from,
            date_to=date_to
        )
        
        synced_count = 0
        
        for match_data in matches_data:
            # Sync teams first
            home_team = await self.sync_team(match_data["homeTeam"])
            away_team = await self.sync_team(match_data["awayTeam"])
            
            # Get league from DB
            result = await self.db.execute(
                select(League).where(League.external_id == league_id)
            )
            league = result.scalar_one_or_none()
            
            if not league:
                continue
            
            # Check if match exists
            result = await self.db.execute(
                select(Match).where(Match.external_id == match_data["id"])
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                match = Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    league_id=league.id,
                    match_date=(datetime.fromisoformat(match_data["utcDate"].replace("Z", "+00:00")) + timedelta(hours=7)).replace(tzinfo=None),
                    status=self._map_status(match_data["status"]),
                    home_score=match_data["score"]["fullTime"]["home"],
                    away_score=match_data["score"]["fullTime"]["away"],
                    venue=match_data.get("venue", ""),
                    round=str(match_data.get("matchday", "")),
                    external_id=match_data["id"]
                )
                self.db.add(match)
                synced_count += 1
            else:
                # Update existing match
                new_date = (datetime.fromisoformat(match_data["utcDate"].replace("Z", "+00:00")) + timedelta(hours=7)).replace(tzinfo=None)
                print(f"🔄 Updating Match {existing.id}: {existing.match_date} -> {new_date}")
                existing.match_date = new_date
                existing.status = self._map_status(match_data["status"])
                existing.home_score = match_data["score"]["fullTime"]["home"]
                existing.away_score = match_data["score"]["fullTime"]["away"]
                synced_count += 1
        
        await self.db.commit()
        return synced_count
    
    async def sync_matches_date_range(self, league_id: int, date_from: str, date_to: str) -> int:
        """Sync matches for a specific date range
        Args:
            league_id: League ID (e.g., 2021 for Premier League)
            date_from: Start date in format YYYY-MM-DD
            date_to: End date in format YYYY-MM-DD
        Returns:
            Number of matches synced/updated
        """
        matches_data = await self.api_client.get_matches(
            competition_id=league_id,
            date_from=date_from,
            date_to=date_to
        )
        
        synced_count = 0
        updated_count = 0
        
        for match_data in matches_data:
            # Sync teams first
            home_team = await self.sync_team(match_data["homeTeam"])
            away_team = await self.sync_team(match_data["awayTeam"])
            
            # Get league from DB
            result = await self.db.execute(
                select(League).where(League.external_id == league_id)
            )
            league = result.scalar_one_or_none()
            
            if not league:
                continue
            
            # Check if match exists
            result = await self.db.execute(
                select(Match).where(Match.external_id == match_data["id"])
            )
            existing = result.scalar_one_or_none()
            
            # Map status
            status = match_data["status"]
            if status in ["SCHEDULED", "TIMED"]:
                db_status = "SCHEDULED"
            elif status in ["IN_PLAY", "PAUSED", "HALFTIME"]:
                db_status = "LIVE"
            elif status in ["FINISHED", "AWARDED"]:
                db_status = "FINISHED"
            else:
                db_status = "SCHEDULED"
            
            if existing:
                # Update existing match (scores, status, date)
                existing.status = db_status
                existing.home_score = match_data["score"]["fullTime"]["home"]
                existing.away_score = match_data["score"]["fullTime"]["away"]
                existing.match_date = (datetime.fromisoformat(match_data["utcDate"].replace("Z", "+00:00")) + timedelta(hours=7)).replace(tzinfo=None)
                updated_count += 1
            else:
                # Create new match
                match = Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    league_id=league.id,
                    match_date=(datetime.fromisoformat(match_data["utcDate"].replace("Z", "+00:00")) + timedelta(hours=7)).replace(tzinfo=None),
                    status=db_status,
                    home_score=match_data["score"]["fullTime"]["home"],
                    away_score=match_data["score"]["fullTime"]["away"],
                    venue=match_data.get("venue", ""),
                    round=str(match_data.get("matchday", "")),
                    external_id=match_data["id"]
                )
                self.db.add(match)
                synced_count += 1
        
        await self.db.commit()
        return synced_count + updated_count
    
    def _map_status(self, api_status: str) -> str:
        """Map API status to our status"""
        status_map = {
            "SCHEDULED": "scheduled",
            "TIMED": "scheduled",
            "IN_PLAY": "live",
            "PAUSED": "live",
            "FINISHED": "finished",
            "POSTPONED": "postponed",
            "CANCELLED": "cancelled",
            "SUSPENDED": "postponed"
        }
        return status_map.get(api_status, "scheduled")
    
    async def update_live_matches(self) -> int:
        """Update scores for live matches"""
        # Get all live matches from DB
        result = await self.db.execute(
            select(Match).where(Match.status == "live")
        )
        live_matches = result.scalars().all()
        
        updated_count = 0
        
        for match in live_matches:
            # Fetch updated data from API
            matches_data = await self.api_client.get_matches()
            
            for match_data in matches_data:
                if match_data["id"] == match.external_id:
                    # Update scores
                    match.home_score = match_data["score"]["fullTime"]["home"]
                    match.away_score = match_data["score"]["fullTime"]["away"]
                    match.status = self._map_status(match_data["status"])
                    updated_count += 1
                    break
        
        await self.db.commit()
        return updated_count
    
    async def calculate_team_stats(self, team_id: int, season: int = 2024) -> TeamStats:
        """Calculate team statistics from matches"""
        # Get all matches for team in current season
        result = await self.db.execute(
            select(Match).where(
                (Match.home_team_id == team_id) | (Match.away_team_id == team_id),
                Match.status == "finished"
            ).order_by(Match.match_date.desc()).limit(20)
        )
        matches = result.scalars().all()
        
        wins = draws = losses = 0
        goals_scored = goals_conceded = clean_sheets = 0
        form_list = []
        
        for match in matches[:5]:  # Last 5 for form
            if match.home_team_id == team_id:
                scored = match.home_score or 0
                conceded = match.away_score or 0
            else:
                scored = match.away_score or 0
                conceded = match.home_score or 0
            
            if scored > conceded:
                wins += 1
                form_list.append("W")
            elif scored < conceded:
                losses += 1
                form_list.append("L")
            else:
                draws += 1
                form_list.append("D")
            
            goals_scored += scored
            goals_conceded += conceded
            if conceded == 0:
                clean_sheets += 1
        
        # Check if stats exist
        result = await self.db.execute(
            select(TeamStats).where(
                TeamStats.team_id == team_id,
                TeamStats.season == season
            )
        )
        stats = result.scalar_one_or_none()
        
        if not stats:
            stats = TeamStats(team_id=team_id, season=season)
            self.db.add(stats)
        
        stats.form = "".join(form_list)
        stats.goals_scored = goals_scored
        stats.goals_conceded = goals_conceded
        stats.clean_sheets = clean_sheets
        stats.matches_played = len(matches)
        stats.wins = wins
        stats.draws = draws
        stats.losses = losses
        
        await self.db.commit()
        await self.db.refresh(stats)
        
        return stats
    
    async def sync_standings(self, league_external_id: int) -> int:
        """
        Sync league standings/table from API
        """
        # Get league from database
        result = await self.db.execute(
            select(League).where(League.external_id == league_external_id)
        )
        league = result.scalar_one_or_none()
        
        if not league:
            raise ValueError(f"League with external_id {league_external_id} not found")
        
        # Fetch standings from API
        response = await self.api_client.get_competition_standings(league_external_id)
        standings_list = response.get("standings", [])
        
        if not standings_list:
            return 0
        
        # Get the first standings (TOTAL type)
        standings_data = standings_list[0].get("table", [])
        
        if not standings_data:
            return 0
        
        synced_count = 0
        
        # Clear existing standings for this league
        await self.db.execute(
            select(Standing).where(Standing.league_id == league.id)
        )
        await self.db.execute(
            Standing.__table__.delete().where(Standing.league_id == league.id)
        )
        
        # Insert new standings
        for standing_item in standings_data:
            # Sync team first
            team = await self.sync_team(standing_item["team"])
            
            # Create standing entry
            standing = Standing(
                league_id=league.id,
                team_id=team.id,
                position=standing_item["position"],
                played=standing_item["playedGames"],
                won=standing_item["won"],
                drawn=standing_item["draw"],
                lost=standing_item["lost"],
                goals_for=standing_item["goalsFor"],
                goals_against=standing_item["goalsAgainst"],
                goal_difference=standing_item["goalDifference"],
                points=standing_item["points"],
                form=standing_item.get("form") or ""
            )
            self.db.add(standing)
            synced_count += 1
        
        await self.db.commit()
        return synced_count
