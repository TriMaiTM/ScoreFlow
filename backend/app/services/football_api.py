import httpx
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os

from app.core.config import settings


class FootballAPIClient:
    """Client for football-data.org API"""
    
    def __init__(self):
        self.base_url = settings.FOOTBALL_API_BASE_URL
        self.api_key = settings.FOOTBALL_API_KEY
        self.headers = {
            "X-Auth-Token": self.api_key
        }
    
    async def get_competitions(self) -> List[Dict]:
        """Get available competitions/leagues"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/competitions",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("competitions", [])
    
    async def get_competition_standings(self, competition_id: int) -> Dict:
        """Get standings for a competition"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/competitions/{competition_id}/standings",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_matches(
        self,
        competition_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get matches with filters"""
        params = {}
        
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to
        if status:
            params["status"] = status
        
        url = f"{self.base_url}/competitions/{competition_id}/matches" if competition_id else f"{self.base_url}/matches"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self.headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("matches", [])
    
    async def get_team(self, team_id: int) -> Dict:
        """Get team details"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/teams/{team_id}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_team_matches(
        self,
        team_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict]:
        """Get matches for a specific team"""
        params = {}
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/teams/{team_id}/matches",
                headers=self.headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("matches", [])


# Alternative: API-Football (RapidAPI)
class APIFootballClient:
    """Client for API-Football (RapidAPI)"""
    
    def __init__(self):
        self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
        self.api_key = os.getenv("RAPID_API_KEY", "")
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
        }
    
    async def get_leagues(self, season: int = 2024) -> List[Dict]:
        """Get leagues"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/leagues",
                headers=self.headers,
                params={"season": season},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", [])
    
    async def get_fixtures(
        self,
        league_id: Optional[int] = None,
        date: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get fixtures/matches"""
        params = {}
        if league_id:
            params["league"] = league_id
        if date:
            params["date"] = date
        if status:
            params["status"] = status
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", [])
    
    async def get_standings(self, league_id: int, season: int = 2024) -> List[Dict]:
        """Get league standings"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/standings",
                headers=self.headers,
                params={"league": league_id, "season": season},
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", [])


# Factory to get the right client
def get_football_api_client():
    provider = settings.FOOTBALL_API_PROVIDER if hasattr(settings, 'FOOTBALL_API_PROVIDER') else "football-data.org"
    
    if provider == "api-football":
        return APIFootballClient()
    else:
        return FootballAPIClient()
