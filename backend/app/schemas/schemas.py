from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    name: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class NotificationSettings(BaseModel):
    enabled: bool = True
    matchStart: bool = True
    goals: bool = True
    matchEnd: bool = True
    favoriteTeamsOnly: bool = False

class UserProfile(BaseModel):
    id: str  # Frontend expects string ID
    email: str
    name: str
    favoriteTeams: List[int] = []
    favoriteLeagues: List[int] = []
    followedMatches: List[int] = []
    notificationSettings: NotificationSettings = NotificationSettings()

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool
    is_superuser: bool = False
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class TeamBase(BaseModel):
    id: int
    name: str
    short_name: str
    logo: str
    country: str
    
    class Config:
        from_attributes = True


class LeagueBase(BaseModel):
    id: int
    name: str
    country: str
    logo: str
    season: int
    
    class Config:
        from_attributes = True


class MatchBase(BaseModel):
    id: int
    home_team: TeamBase
    away_team: TeamBase
    league: LeagueBase
    match_date: datetime
    status: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    venue: str
    round: Optional[str] = None
    
    class Config:
        from_attributes = True


class PredictionFeatures(BaseModel):
    home_team_elo: float
    away_team_elo: float
    home_form: float
    away_form: float
    home_goals_avg: float
    away_goals_avg: float
    h2h_home_wins: int
    h2h_away_wins: int
    h2h_draws: int
    is_home_match: bool
    days_since_last_match_home: int
    days_since_last_match_away: int
    injured_players_home: int
    injured_players_away: int


class PredictionResponse(BaseModel):
    match_id: int
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    predicted_score: dict
    confidence: float
    features: PredictionFeatures
    
    class Config:
        from_attributes = True


class TeamStatsResponse(BaseModel):
    team_id: int
    form: str
    goals_scored: int
    goals_conceded: int
    clean_sheets: int
    avg_goals_scored: float
    avg_goals_conceded: float
    home_win_percentage: float
    away_win_percentage: float
    
    class Config:
        from_attributes = True


class StandingResponse(BaseModel):
    position: int
    team: TeamBase
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    form: str
    
    class Config:
        from_attributes = True


class ApiResponse(BaseModel):
    success: bool
    data: Optional[dict | list] = None
    message: Optional[str] = None


class PaginatedResponse(BaseModel):
    data: List[dict]
    page: int
    total_pages: int
    total_items: int
