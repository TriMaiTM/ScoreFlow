"""
API-Football.com client for enhanced data
Free tier: 100 requests/day
"""
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class APIFootballClient:
    """Client for API-Football.com"""
    
    BASE_URL = "https://v3.football.api-sports.io"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "x-apisports-key": api_key,
            "x-apisports-host": "v3.football.api-sports.io"
        }
    
    async def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make API request with error handling"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                if data.get("errors"):
                    logger.error(f"API-Football error: {data['errors']}")
                    return None
                
                return data
        except httpx.HTTPError as e:
            logger.error(f"API-Football request failed: {e}")
            return None
    
    async def get_team_statistics(self, team_id: int, league_id: int, season: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed team statistics
        Endpoint: /teams/statistics
        """
        params = {
            "team": team_id,
            "league": league_id,
            "season": season
        }
        
        data = await self._request("teams/statistics", params)
        if not data or not data.get("response"):
            return None
        
        stats = data["response"]
        
        # Parse and normalize statistics
        return {
            "teamId": team_id,
            "leagueId": league_id,
            "season": season,
            "form": stats.get("form", ""),
            "fixtures": {
                "played": {
                    "home": stats.get("fixtures", {}).get("played", {}).get("home", 0),
                    "away": stats.get("fixtures", {}).get("played", {}).get("away", 0),
                    "total": stats.get("fixtures", {}).get("played", {}).get("total", 0),
                },
                "wins": {
                    "home": stats.get("fixtures", {}).get("wins", {}).get("home", 0),
                    "away": stats.get("fixtures", {}).get("wins", {}).get("away", 0),
                    "total": stats.get("fixtures", {}).get("wins", {}).get("total", 0),
                },
                "draws": {
                    "home": stats.get("fixtures", {}).get("draws", {}).get("home", 0),
                    "away": stats.get("fixtures", {}).get("draws", {}).get("away", 0),
                    "total": stats.get("fixtures", {}).get("draws", {}).get("total", 0),
                },
                "loses": {
                    "home": stats.get("fixtures", {}).get("loses", {}).get("home", 0),
                    "away": stats.get("fixtures", {}).get("loses", {}).get("away", 0),
                    "total": stats.get("fixtures", {}).get("loses", {}).get("total", 0),
                },
            },
            "goals": {
                "for": {
                    "total": {
                        "home": stats.get("goals", {}).get("for", {}).get("total", {}).get("home", 0),
                        "away": stats.get("goals", {}).get("for", {}).get("total", {}).get("away", 0),
                        "total": stats.get("goals", {}).get("for", {}).get("total", {}).get("total", 0),
                    },
                    "average": {
                        "home": stats.get("goals", {}).get("for", {}).get("average", {}).get("home", "0"),
                        "away": stats.get("goals", {}).get("for", {}).get("average", {}).get("away", "0"),
                        "total": stats.get("goals", {}).get("for", {}).get("average", {}).get("total", "0"),
                    },
                },
                "against": {
                    "total": {
                        "home": stats.get("goals", {}).get("against", {}).get("total", {}).get("home", 0),
                        "away": stats.get("goals", {}).get("against", {}).get("total", {}).get("away", 0),
                        "total": stats.get("goals", {}).get("against", {}).get("total", {}).get("total", 0),
                    },
                    "average": {
                        "home": stats.get("goals", {}).get("against", {}).get("average", {}).get("home", "0"),
                        "away": stats.get("goals", {}).get("against", {}).get("average", {}).get("away", "0"),
                        "total": stats.get("goals", {}).get("against", {}).get("average", {}).get("total", "0"),
                    },
                },
            },
            "cleanSheet": {
                "home": stats.get("clean_sheet", {}).get("home", 0),
                "away": stats.get("clean_sheet", {}).get("away", 0),
                "total": stats.get("clean_sheet", {}).get("total", 0),
            },
            "failedToScore": {
                "home": stats.get("failed_to_score", {}).get("home", 0),
                "away": stats.get("failed_to_score", {}).get("away", 0),
                "total": stats.get("failed_to_score", {}).get("total", 0),
            },
            "biggestStreak": {
                "wins": stats.get("biggest", {}).get("streak", {}).get("wins", 0),
                "draws": stats.get("biggest", {}).get("streak", {}).get("draws", 0),
                "loses": stats.get("biggest", {}).get("streak", {}).get("loses", 0),
            },
        }
    
    async def get_head_to_head(self, team1_id: int, team2_id: int, last: int = 10) -> Optional[List[Dict[str, Any]]]:
        """
        Get head-to-head matches between two teams
        Endpoint: /fixtures/headtohead
        """
        params = {
            "h2h": f"{team1_id}-{team2_id}",
            "last": last
        }
        
        data = await self._request("fixtures/headtohead", params)
        if not data or not data.get("response"):
            return []
        
        matches = []
        for fixture in data["response"]:
            matches.append({
                "fixtureId": fixture["fixture"]["id"],
                "date": fixture["fixture"]["date"],
                "homeTeam": {
                    "id": fixture["teams"]["home"]["id"],
                    "name": fixture["teams"]["home"]["name"],
                    "logo": fixture["teams"]["home"]["logo"],
                },
                "awayTeam": {
                    "id": fixture["teams"]["away"]["id"],
                    "name": fixture["teams"]["away"]["name"],
                    "logo": fixture["teams"]["away"]["logo"],
                },
                "score": {
                    "home": fixture["goals"]["home"],
                    "away": fixture["goals"]["away"],
                },
                "winner": fixture["teams"]["home"]["winner"],
            })
        
        return matches
    
    async def get_match_statistics(self, fixture_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed match statistics
        Endpoint: /fixtures/statistics
        """
        params = {"fixture": fixture_id}
        
        data = await self._request("fixtures/statistics", params)
        if not data or not data.get("response"):
            return None
        
        # Parse statistics for both teams
        stats_list = data["response"]
        if len(stats_list) < 2:
            return None
        
        home_stats = {stat["type"]: stat["value"] for stat in stats_list[0]["statistics"]}
        away_stats = {stat["type"]: stat["value"] for stat in stats_list[1]["statistics"]}
        
        return {
            "fixtureId": fixture_id,
            "homeTeam": {
                "shotsOnGoal": home_stats.get("Shots on Goal", 0),
                "shotsOffGoal": home_stats.get("Shots off Goal", 0),
                "totalShots": home_stats.get("Total Shots", 0),
                "blockedShots": home_stats.get("Blocked Shots", 0),
                "shotsInsideBox": home_stats.get("Shots insidebox", 0),
                "shotsOutsideBox": home_stats.get("Shots outsidebox", 0),
                "fouls": home_stats.get("Fouls", 0),
                "cornerKicks": home_stats.get("Corner Kicks", 0),
                "offsides": home_stats.get("Offsides", 0),
                "ballPossession": home_stats.get("Ball Possession", "0%"),
                "yellowCards": home_stats.get("Yellow Cards", 0),
                "redCards": home_stats.get("Red Cards", 0),
                "saves": home_stats.get("Goalkeeper Saves", 0),
                "totalPasses": home_stats.get("Total passes", 0),
                "passesAccurate": home_stats.get("Passes accurate", 0),
                "passesPercentage": home_stats.get("Passes %", "0%"),
            },
            "awayTeam": {
                "shotsOnGoal": away_stats.get("Shots on Goal", 0),
                "shotsOffGoal": away_stats.get("Shots off Goal", 0),
                "totalShots": away_stats.get("Total Shots", 0),
                "blockedShots": away_stats.get("Blocked Shots", 0),
                "shotsInsideBox": away_stats.get("Shots insidebox", 0),
                "shotsOutsideBox": away_stats.get("Shots outsidebox", 0),
                "fouls": away_stats.get("Fouls", 0),
                "cornerKicks": away_stats.get("Corner Kicks", 0),
                "offsides": away_stats.get("Offsides", 0),
                "ballPossession": away_stats.get("Ball Possession", "0%"),
                "yellowCards": away_stats.get("Yellow Cards", 0),
                "redCards": away_stats.get("Red Cards", 0),
                "saves": away_stats.get("Goalkeeper Saves", 0),
                "totalPasses": away_stats.get("Total passes", 0),
                "passesAccurate": away_stats.get("Passes accurate", 0),
                "passesPercentage": away_stats.get("Passes %", "0%"),
            },
        }
    
    async def get_predictions(self, fixture_id: int) -> Optional[Dict[str, Any]]:
        """
        Get AI predictions from API-Football
        Endpoint: /predictions
        """
        params = {"fixture": fixture_id}
        
        data = await self._request("predictions", params)
        if not data or not data.get("response"):
            return None
        
        prediction = data["response"][0]
        predictions_data = prediction.get("predictions", {})
        
        return {
            "fixtureId": fixture_id,
            "winner": {
                "id": predictions_data.get("winner", {}).get("id"),
                "name": predictions_data.get("winner", {}).get("name"),
                "comment": predictions_data.get("winner", {}).get("comment", ""),
            },
            "winOrDraw": predictions_data.get("win_or_draw", False),
            "underOver": predictions_data.get("under_over"),
            "goalsHome": predictions_data.get("goals", {}).get("home", "0-0"),
            "goalsAway": predictions_data.get("goals", {}).get("away", "0-0"),
            "advice": predictions_data.get("advice", ""),
            "percentages": {
                "home": predictions_data.get("percent", {}).get("home", "0%"),
                "draw": predictions_data.get("percent", {}).get("draw", "0%"),
                "away": predictions_data.get("percent", {}).get("away", "0%"),
            },
        }
    
    async def get_team_injuries(self, team_id: int, league_id: int, season: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get team injuries
        Endpoint: /injuries
        """
        params = {
            "team": team_id,
            "league": league_id,
            "season": season
        }
        
        data = await self._request("injuries", params)
        if not data or not data.get("response"):
            return []
        
        injuries = []
        for injury in data["response"]:
            injuries.append({
                "playerId": injury["player"]["id"],
                "playerName": injury["player"]["name"],
                "playerPhoto": injury["player"]["photo"],
                "type": injury["player"]["type"],
                "reason": injury["player"]["reason"],
            })
        
        return injuries
    
    async def check_api_status(self) -> Dict[str, Any]:
        """
        Check API status and remaining requests
        Endpoint: /status
        """
        data = await self._request("status")
        if not data:
            return {"error": "Failed to check API status"}
        
        account = data.get("response", {}).get("account", {})
        requests_info = data.get("response", {}).get("requests", {})
        
        return {
            "firstName": account.get("firstname", ""),
            "lastName": account.get("lastname", ""),
            "email": account.get("email", ""),
            "requests": {
                "current": requests_info.get("current", 0),
                "limit": requests_info.get("limit_day", 100),
            },
        }


# Singleton instance
_api_football_client: Optional[APIFootballClient] = None


def get_api_football_client(api_key: str) -> APIFootballClient:
    """Get or create API-Football client instance"""
    global _api_football_client
    if _api_football_client is None:
        _api_football_client = APIFootballClient(api_key)
    return _api_football_client
