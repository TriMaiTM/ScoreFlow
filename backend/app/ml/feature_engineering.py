import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Match, Team, TeamStats


class FeatureEngineer:
    """Feature engineering for match prediction"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_team_elo(self, team_id: int) -> float:
        """Get team's Elo rating"""
        result = await self.db.execute(
            select(TeamStats)
            .where(TeamStats.team_id == team_id)
            .order_by(TeamStats.season.desc())
            .limit(1)
        )
        stats = result.scalar_one_or_none()
        return stats.elo_rating if stats else 1500.0
    
    async def get_team_form(self, team_id: int, last_n: int = 5) -> float:
        """Calculate team form from last N matches"""
        result = await self.db.execute(
            select(Match)
            .where(
                ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)),
                Match.status == "finished"
            )
            .order_by(Match.match_date.desc())
            .limit(last_n)
        )
        matches = result.scalars().all()
        
        if not matches:
            return 0.5
        
        points = 0
        for match in matches:
            if match.home_team_id == team_id:
                if match.home_score > match.away_score:
                    points += 3
                elif match.home_score == match.away_score:
                    points += 1
            else:
                if match.away_score > match.home_score:
                    points += 3
                elif match.away_score == match.home_score:
                    points += 1
        
        max_points = last_n * 3
        return points / max_points
    
    async def get_goals_avg(self, team_id: int, last_n: int = 10) -> Tuple[float, float]:
        """Get average goals scored and conceded"""
        result = await self.db.execute(
            select(Match)
            .where(
                ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)),
                Match.status == "finished"
            )
            .order_by(Match.match_date.desc())
            .limit(last_n)
        )
        matches = result.scalars().all()
        
        if not matches:
            return 1.0, 1.0
        
        scored = []
        conceded = []
        
        for match in matches:
            if match.home_team_id == team_id:
                scored.append(match.home_score or 0)
                conceded.append(match.away_score or 0)
            else:
                scored.append(match.away_score or 0)
                conceded.append(match.home_score or 0)
        
        return np.mean(scored), np.mean(conceded)
    
    async def get_h2h_stats(self, home_team_id: int, away_team_id: int, last_n: int = 5) -> Dict:
        """Get head-to-head statistics"""
        result = await self.db.execute(
            select(Match)
            .where(
                ((Match.home_team_id == home_team_id) & (Match.away_team_id == away_team_id)) |
                ((Match.home_team_id == away_team_id) & (Match.away_team_id == home_team_id)),
                Match.status == "finished"
            )
            .order_by(Match.match_date.desc())
            .limit(last_n)
        )
        matches = result.scalars().all()
        
        home_wins = draws = away_wins = 0
        
        for match in matches:
            if match.home_team_id == home_team_id:
                if match.home_score > match.away_score:
                    home_wins += 1
                elif match.home_score == match.away_score:
                    draws += 1
                else:
                    away_wins += 1
            else:
                if match.away_score > match.home_score:
                    home_wins += 1
                elif match.away_score == match.home_score:
                    draws += 1
                else:
                    away_wins += 1
        
        return {
            "home_wins": home_wins,
            "draws": draws,
            "away_wins": away_wins,
            "total": len(matches)
        }
    
    async def get_days_since_last_match(self, team_id: int) -> int:
        """Get days since team's last match"""
        result = await self.db.execute(
            select(Match)
            .where(
                ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)),
                Match.status == "finished"
            )
            .order_by(Match.match_date.desc())
            .limit(1)
        )
        last_match = result.scalar_one_or_none()
        
        if not last_match:
            return 7
        
        days = (datetime.utcnow() - last_match.match_date).days
        return max(days, 0)
    
    async def extract_features(self, match_id: int) -> Dict:
        """Extract all features for a match"""
        # Get match
        result = await self.db.execute(
            select(Match).where(Match.id == match_id)
        )
        match = result.scalar_one_or_none()
        
        if not match:
            raise ValueError(f"Match {match_id} not found")
        
        # Extract features
        home_elo = await self.get_team_elo(match.home_team_id)
        away_elo = await self.get_team_elo(match.away_team_id)
        
        home_form = await self.get_team_form(match.home_team_id)
        away_form = await self.get_team_form(match.away_team_id)
        
        home_goals_avg, home_conceded_avg = await self.get_goals_avg(match.home_team_id)
        away_goals_avg, away_conceded_avg = await self.get_goals_avg(match.away_team_id)
        
        h2h = await self.get_h2h_stats(match.home_team_id, match.away_team_id)
        
        home_days = await self.get_days_since_last_match(match.home_team_id)
        away_days = await self.get_days_since_last_match(match.away_team_id)
        
        return {
            "home_team_elo": home_elo,
            "away_team_elo": away_elo,
            "elo_diff": home_elo - away_elo,
            "home_form": home_form,
            "away_form": away_form,
            "form_diff": home_form - away_form,
            "home_goals_avg": home_goals_avg,
            "away_goals_avg": away_goals_avg,
            "home_conceded_avg": home_conceded_avg,
            "away_conceded_avg": away_conceded_avg,
            "h2h_home_wins": h2h["home_wins"],
            "h2h_draws": h2h["draws"],
            "h2h_away_wins": h2h["away_wins"],
            "is_home_match": 1.0,  # Always 1 for prediction
            "days_since_last_match_home": home_days,
            "days_since_last_match_away": away_days,
            "injured_players_home": 0,  # TODO: Add injury data
            "injured_players_away": 0,
        }
    
    def features_to_array(self, features: Dict) -> np.ndarray:
        """Convert features dict to numpy array"""
        feature_order = [
            "home_team_elo", "away_team_elo", "elo_diff",
            "home_form", "away_form", "form_diff",
            "home_goals_avg", "away_goals_avg",
            "home_conceded_avg", "away_conceded_avg",
            "h2h_home_wins", "h2h_draws", "h2h_away_wins",
            "is_home_match",
            "days_since_last_match_home", "days_since_last_match_away",
            "injured_players_home", "injured_players_away"
        ]
        
        return np.array([features[key] for key in feature_order]).reshape(1, -1)
