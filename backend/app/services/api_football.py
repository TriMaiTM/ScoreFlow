"""
API-Football.com integration service
Free tier: 100 requests/day
Documentation: https://www.api-football.com/documentation-v3
"""
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class APIFootballService:
    """Service for interacting with API-Football.com"""
    
    BASE_URL = "https://v3.football.api-sports.io"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, 'API_FOOTBALL_KEY', None)
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to API-Football"""
        if not self.api_key:
            logger.warning("API-Football key not configured")
            return {"response": []}
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"API-Football request failed: {e}")
            return {"response": []}
    
    async def get_team_statistics(self, team_id: int, league_id: int, season: int) -> Dict[str, Any]:
        """
        Get team statistics for a specific league/season
        Endpoint: GET /teams/statistics
        """
        params = {
            "team": team_id,
            "league": league_id,
            "season": season
        }
        
        data = await self._make_request("teams/statistics", params)
        
        if not data.get("response"):
            return {}
        
        stats = data["response"]
        
        # Extract and format key statistics
        return {
            "team_id": team_id,
            "league_id": league_id,
            "season": season,
            "form": stats.get("form", ""),
            "fixtures": {
                "played": stats.get("fixtures", {}).get("played", {}).get("total", 0),
                "wins": stats.get("fixtures", {}).get("wins", {}).get("total", 0),
                "draws": stats.get("fixtures", {}).get("draws", {}).get("total", 0),
                "loses": stats.get("fixtures", {}).get("loses", {}).get("total", 0),
            },
            "goals": {
                "scored": stats.get("goals", {}).get("for", {}).get("total", {}).get("total", 0),
                "conceded": stats.get("goals", {}).get("against", {}).get("total", {}).get("total", 0),
                "avg_scored": stats.get("goals", {}).get("for", {}).get("average", {}).get("total", "0"),
                "avg_conceded": stats.get("goals", {}).get("against", {}).get("average", {}).get("total", "0"),
            },
            "biggest": {
                "win": stats.get("biggest", {}).get("wins", {}).get("home", ""),
                "lose": stats.get("biggest", {}).get("loses", {}).get("home", ""),
            },
            "clean_sheet": stats.get("clean_sheet", {}).get("total", 0),
            "failed_to_score": stats.get("failed_to_score", {}).get("total", 0),
            "penalty": {
                "scored": stats.get("penalty", {}).get("scored", {}).get("total", 0),
                "missed": stats.get("penalty", {}).get("missed", {}).get("total", 0),
            },
            "lineups": stats.get("lineups", []),
            "cards": {
                "yellow": stats.get("cards", {}).get("yellow", {}),
                "red": stats.get("cards", {}).get("red", {}),
            }
        }
    
    async def get_head_to_head(self, team1_id: int, team2_id: int, last: int = 10) -> List[Dict[str, Any]]:
        """
        Get head-to-head matches between two teams
        Endpoint: GET /fixtures/headtohead
        """
        params = {
            "h2h": f"{team1_id}-{team2_id}",
            "last": last
        }
        
        data = await self._make_request("fixtures/headtohead", params)
        
        if not data.get("response"):
            return []
        
        matches = []
        for fixture in data["response"]:
            matches.append({
                "id": fixture.get("fixture", {}).get("id"),
                "date": fixture.get("fixture", {}).get("date"),
                "venue": fixture.get("fixture", {}).get("venue", {}).get("name"),
                "status": fixture.get("fixture", {}).get("status", {}).get("short"),
                "league": {
                    "id": fixture.get("league", {}).get("id"),
                    "name": fixture.get("league", {}).get("name"),
                    "country": fixture.get("league", {}).get("country"),
                },
                "home": {
                    "id": fixture.get("teams", {}).get("home", {}).get("id"),
                    "name": fixture.get("teams", {}).get("home", {}).get("name"),
                    "logo": fixture.get("teams", {}).get("home", {}).get("logo"),
                    "score": fixture.get("goals", {}).get("home"),
                },
                "away": {
                    "id": fixture.get("teams", {}).get("away", {}).get("id"),
                    "name": fixture.get("teams", {}).get("away", {}).get("name"),
                    "logo": fixture.get("teams", {}).get("away", {}).get("logo"),
                    "score": fixture.get("goals", {}).get("away"),
                }
            })
        
        return matches
    
    async def get_match_statistics(self, fixture_id: int) -> Dict[str, Any]:
        """
        Get detailed statistics for a specific match
        Endpoint: GET /fixtures/statistics
        """
        params = {"fixture": fixture_id}
        
        data = await self._make_request("fixtures/statistics", params)
        
        if not data.get("response"):
            return {}
        
        # API returns array with stats for both teams
        stats_data = data["response"]
        
        result = {
            "fixture_id": fixture_id,
            "teams": []
        }
        
        for team_stats in stats_data:
            team_info = {
                "team_id": team_stats.get("team", {}).get("id"),
                "team_name": team_stats.get("team", {}).get("name"),
                "statistics": {}
            }
            
            # Convert statistics array to dict
            for stat in team_stats.get("statistics", []):
                stat_type = stat.get("type")
                stat_value = stat.get("value")
                
                # Normalize stat names
                stat_key = stat_type.lower().replace(" ", "_")
                team_info["statistics"][stat_key] = stat_value
            
            result["teams"].append(team_info)
        
        return result
    
    async def get_match_events(self, fixture_id: int) -> List[Dict[str, Any]]:
        """
        Get match events (goals, cards, substitutions)
        Endpoint: GET /fixtures/events
        """
        params = {"fixture": fixture_id}
        
        data = await self._make_request("fixtures/events", params)
        
        if not data.get("response"):
            return []
        
        events = []
        for event in data["response"]:
            events.append({
                "time": event.get("time", {}).get("elapsed"),
                "extra_time": event.get("time", {}).get("extra"),
                "team": {
                    "id": event.get("team", {}).get("id"),
                    "name": event.get("team", {}).get("name"),
                },
                "player": {
                    "id": event.get("player", {}).get("id"),
                    "name": event.get("player", {}).get("name"),
                },
                "assist": {
                    "id": event.get("assist", {}).get("id"),
                    "name": event.get("assist", {}).get("name"),
                } if event.get("assist", {}).get("id") else None,
                "type": event.get("type"),  # Goal, Card, subst
                "detail": event.get("detail"),  # Normal Goal, Yellow Card, etc.
                "comments": event.get("comments"),
            })
        
        return events
    
    async def get_predictions(self, fixture_id: int) -> Dict[str, Any]:
        """
        Get AI predictions from API-Football
        Endpoint: GET /predictions
        """
        params = {"fixture": fixture_id}
        
        data = await self._make_request("predictions", params)
        
        if not data.get("response") or len(data["response"]) == 0:
            return {}
        
        prediction = data["response"][0]
        
        return {
            "fixture_id": fixture_id,
            "predictions": {
                "winner": prediction.get("predictions", {}).get("winner", {}).get("name"),
                "win_or_draw": prediction.get("predictions", {}).get("win_or_draw"),
                "under_over": prediction.get("predictions", {}).get("under_over"),
                "goals_home": prediction.get("predictions", {}).get("goals", {}).get("home"),
                "goals_away": prediction.get("predictions", {}).get("goals", {}).get("away"),
                "advice": prediction.get("predictions", {}).get("advice"),
                "percent": {
                    "home": prediction.get("predictions", {}).get("percent", {}).get("home"),
                    "draw": prediction.get("predictions", {}).get("percent", {}).get("draw"),
                    "away": prediction.get("predictions", {}).get("percent", {}).get("away"),
                }
            },
            "comparison": prediction.get("comparison", {}),
            "h2h": prediction.get("h2h", []),
        }
    
    async def get_injuries(self, league_id: int, season: int, team_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get team injuries
        Endpoint: GET /injuries
        """
        params = {
            "league": league_id,
            "season": season
        }
        
        if team_id:
            params["team"] = team_id
        
        data = await self._make_request("injuries", params)
        
        if not data.get("response"):
            return []
        
        injuries = []
        for injury in data["response"]:
            injuries.append({
                "player": {
                    "id": injury.get("player", {}).get("id"),
                    "name": injury.get("player", {}).get("name"),
                    "photo": injury.get("player", {}).get("photo"),
                },
                "team": {
                    "id": injury.get("team", {}).get("id"),
                    "name": injury.get("team", {}).get("name"),
                },
                "fixture": {
                    "id": injury.get("fixture", {}).get("id"),
                    "date": injury.get("fixture", {}).get("date"),
                },
                "league": {
                    "id": injury.get("league", {}).get("id"),
                    "name": injury.get("league", {}).get("name"),
                },
                "type": injury.get("player", {}).get("type"),
                "reason": injury.get("player", {}).get("reason"),
            })
        
        return injuries


# Create singleton instance
api_football_service = APIFootballService()
