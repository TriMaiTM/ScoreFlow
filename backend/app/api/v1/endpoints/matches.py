from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db.models import Match, Team, League
from app.schemas.schemas import ApiResponse, PaginatedResponse
from app.core.security import get_current_user
from app.services.cache import get_cache, RedisCache

router = APIRouter()


@router.get("/upcoming", response_model=ApiResponse)
async def get_upcoming_matches(
    league_id: Optional[int] = None,
    team_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    cache: RedisCache = Depends(get_cache),
):
    # Check cache first
    cache_key = f"matches:upcoming:{league_id}:{team_id}:{date_from}:{date_to}"
    cached = await cache.get(cache_key)
    if cached:
        return ApiResponse(success=True, data=cached)
    
    query = (
        select(Match)
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
            selectinload(Match.league)
        )
        .where(Match.status == "scheduled")
    )
    
    # Apply filters
    if league_id:
        query = query.where(Match.league_id == league_id)
    if team_id:
        query = query.where(
            or_(Match.home_team_id == team_id, Match.away_team_id == team_id)
        )
    
    # Date range (default: next 7 days)
    now = datetime.utcnow()
    default_to = now + timedelta(days=7)
    
    if date_from:
        query = query.where(Match.match_date >= datetime.fromisoformat(date_from))
    else:
        query = query.where(Match.match_date >= now)
    
    if date_to:
        query = query.where(Match.match_date <= datetime.fromisoformat(date_to))
    else:
        query = query.where(Match.match_date <= default_to)
    
    query = query.order_by(Match.match_date)
    
    result = await db.execute(query)
    matches = result.scalars().all()
    
    # Format response
    matches_data = [
        {
            "id": match.id,
            "homeTeam": {
                "id": match.home_team.id,
                "name": match.home_team.name,
                "shortName": match.home_team.short_name,
                "logo": match.home_team.logo,
                "country": match.home_team.country,
            },
            "awayTeam": {
                "id": match.away_team.id,
                "name": match.away_team.name,
                "shortName": match.away_team.short_name,
                "logo": match.away_team.logo,
                "country": match.away_team.country,
            },
            "league": {
                "id": match.league.id,
                "name": match.league.name,
                "country": match.league.country,
                "logo": match.league.logo,
                "season": match.league.season,
            },
            "matchDate": match.match_date.isoformat(),
            "status": match.status,
            "homeScore": match.home_score,
            "awayScore": match.away_score,
            "venue": match.venue,
            "round": match.round,
        }
        for match in matches
    ]
    
    # Cache for 2 minutes
    await cache.set(cache_key, matches_data, expire=120)
    
    return ApiResponse(success=True, data=matches_data)


@router.get("/live", response_model=ApiResponse)
async def get_live_matches(db: AsyncSession = Depends(get_db)):
    query = (
        select(Match)
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
            selectinload(Match.league)
        )
        .where(Match.status == "live")
        .order_by(Match.match_date.desc())
    )
    
    result = await db.execute(query)
    matches = result.scalars().all()
    
    # Format response
    matches_data = [
        {
            "id": match.id,
            "homeTeam": {
                "id": match.home_team.id,
                "name": match.home_team.name,
                "shortName": match.home_team.short_name,
                "logo": match.home_team.logo,
            },
            "awayTeam": {
                "id": match.away_team.id,
                "name": match.away_team.name,
                "shortName": match.away_team.short_name,
                "logo": match.away_team.logo,
            },
            "league": {
                "id": match.league.id,
                "name": match.league.name,
                "country": match.league.country,
                "logo": match.league.logo,
            },
            "matchDate": match.match_date.isoformat(),
            "status": match.status,
            "homeScore": match.home_score,
            "awayScore": match.away_score,
            "venue": match.venue,
        }
        for match in matches
    ]
    
    return ApiResponse(success=True, data=matches_data)


@router.get("/finished")
async def get_finished_matches(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Match).where(Match.status == "finished")
    query = query.order_by(Match.match_date.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    
    result = await db.execute(query)
    matches = result.scalars().all()
    
    # TODO: Get total count
    total = 0
    
    return {
        "data": [],
        "page": page,
        "total_pages": (total + limit - 1) // limit,
        "total_items": total,
    }


@router.get("/by-date", response_model=ApiResponse)
async def get_matches_by_date(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    league_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    cache: RedisCache = Depends(get_cache),
):
    """
    Get all matches for a specific date (SCHEDULED, LIVE, FINISHED)
    Real-time scores included for all statuses
    """
    # Check cache (30 seconds for real-time updates)
    cache_key = f"matches:by-date:{date}:{league_id}"
    cached = await cache.get(cache_key)
    if cached:
        return ApiResponse(success=True, data=cached)
    
    try:
        target_date = datetime.fromisoformat(date)
        # Get matches for the entire day (00:00 to 23:59)
        date_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    except ValueError:
        return ApiResponse(success=False, message="Invalid date format. Use YYYY-MM-DD")
    
    query = (
        select(Match)
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
            selectinload(Match.league)
        )
        .where(
            and_(
                Match.match_date >= date_start,
                Match.match_date <= date_end
            )
        )
    )
    
    if league_id:
        query = query.where(Match.league_id == league_id)
    
    query = query.order_by(Match.match_date)
    
    result = await db.execute(query)
    matches = result.scalars().all()
    
    # Format response with real-time scores
    matches_data = [
        {
            "id": match.id,
            "homeTeam": {
                "id": match.home_team.id,
                "name": match.home_team.name,
                "shortName": match.home_team.short_name,
                "logo": match.home_team.logo,
            },
            "awayTeam": {
                "id": match.away_team.id,
                "name": match.away_team.name,
                "shortName": match.away_team.short_name,
                "logo": match.away_team.logo,
            },
            "league": {
                "id": match.league.id,
                "name": match.league.name,
                "country": match.league.country,
                "logo": match.league.logo,
            },
            "matchDate": match.match_date.isoformat(),
            "status": match.status.upper(),  # SCHEDULED, LIVE, FINISHED
            "homeScore": match.home_score,
            "awayScore": match.away_score,
            "venue": match.venue,
            "round": match.round,
        }
        for match in matches
    ]
    
    # Group by league for better UI organization
    grouped_data = {}
    for match_data in matches_data:
        league_name = match_data["league"]["name"]
        if league_name not in grouped_data:
            grouped_data[league_name] = {
                "league": match_data["league"],
                "matches": []
            }
        grouped_data[league_name]["matches"].append(match_data)
    
    response_data = {
        "date": date,
        "totalMatches": len(matches_data),
        "leagues": list(grouped_data.values())
    }
    
    # Cache for 30 seconds (real-time updates)
    await cache.set(cache_key, response_data, expire=30)
    
    return ApiResponse(success=True, data=response_data)


@router.get("/date-range", response_model=ApiResponse)
async def get_matches_date_range(
    date_from: str = Query(..., description="Start date YYYY-MM-DD"),
    date_to: str = Query(..., description="End date YYYY-MM-DD"),
    league_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Get matches for a date range (for calendar/slider preload)
    """
    try:
        start_date = datetime.fromisoformat(date_from)
        end_date = datetime.fromisoformat(date_to)
    except ValueError:
        return ApiResponse(success=False, message="Invalid date format. Use YYYY-MM-DD")
    
    query = (
        select(Match)
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
            selectinload(Match.league)
        )
        .where(
            and_(
                Match.match_date >= start_date,
                Match.match_date <= end_date
            )
        )
    )
    
    if league_id:
        query = query.where(Match.league_id == league_id)
    
    query = query.order_by(Match.match_date)
    
    result = await db.execute(query)
    matches = result.scalars().all()
    
    # Group by date
    matches_by_date = {}
    for match in matches:
        date_key = match.match_date.date().isoformat()
        if date_key not in matches_by_date:
            matches_by_date[date_key] = []
        
        matches_by_date[date_key].append({
            "id": match.id,
            "homeTeam": {
                "id": match.home_team.id,
                "name": match.home_team.name,
                "shortName": match.home_team.short_name,
                "logo": match.home_team.logo,
            },
            "awayTeam": {
                "id": match.away_team.id,
                "name": match.away_team.name,
                "shortName": match.away_team.short_name,
                "logo": match.away_team.logo,
            },
            "matchDate": match.match_date.isoformat(),
            "status": match.status.upper(),
            "homeScore": match.home_score,
            "awayScore": match.away_score,
        })
    
    return ApiResponse(
        success=True,
        data={
            "dateFrom": date_from,
            "dateTo": date_to,
            "matchesByDate": matches_by_date
        }
    )


@router.get("/{match_id}", response_model=ApiResponse)
async def get_match_by_id(match_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(Match)
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
            selectinload(Match.league)
        )
        .where(Match.id == match_id)
    )
    
    result = await db.execute(query)
    match = result.scalar_one_or_none()
    
    if not match:
        return ApiResponse(success=False, message="Match not found")
    
    # Format response
    match_data = {
        "id": match.id,
        "homeTeam": {
            "id": match.home_team.id,
            "name": match.home_team.name,
            "shortName": match.home_team.short_name,
            "logo": match.home_team.logo,
            "country": match.home_team.country,
        },
        "awayTeam": {
            "id": match.away_team.id,
            "name": match.away_team.name,
            "shortName": match.away_team.short_name,
            "logo": match.away_team.logo,
            "country": match.away_team.country,
        },
        "league": {
            "id": match.league.id,
            "name": match.league.name,
            "country": match.league.country,
            "logo": match.league.logo,
            "season": match.league.season,
        },
        "matchDate": match.match_date.isoformat(),
        "status": match.status,
        "homeScore": match.home_score,
        "awayScore": match.away_score,
        "venue": match.venue,
        "round": match.round,
        "externalId": match.external_id,
    }
    
    return ApiResponse(success=True, data=match_data)


@router.get("/{match_id}/prediction", response_model=ApiResponse)
async def get_match_prediction(match_id: int, db: AsyncSession = Depends(get_db)):
    # TODO: Get prediction from ML service
    # For now, return dummy data with proper camelCase field names
    return ApiResponse(
        success=True,
        data={
            "matchId": match_id,
            "homeWinProbability": 0.45,
            "drawProbability": 0.25,
            "awayWinProbability": 0.30,
            "predictedScore": {"home": 2, "away": 1},
            "confidence": 0.75,
            "features": {
                "homeTeamElo": 1500,
                "awayTeamElo": 1480,
                "homeForm": 2.1,
                "awayForm": 1.8,
                "homeGoalsAvg": 1.8,
                "awayGoalsAvg": 1.5,
                "h2hHomeWins": 3,
                "h2hAwayWins": 2,
                "h2hDraws": 1,
                "isHomeMatch": True,
                "daysSinceLastMatch": {"home": 7, "away": 5},
                "injuredPlayers": {"home": 0, "away": 1},
            },
        },
    )


@router.get("/h2h", response_model=ApiResponse)
async def get_head_to_head(
    home_team: int,
    away_team: int,
    db: AsyncSession = Depends(get_db),
):
    # Get last 5 H2H matches
    query = select(Match).where(
        and_(
            Match.status == "finished",
            (
                (Match.home_team_id == home_team) & (Match.away_team_id == away_team)
                | (Match.home_team_id == away_team) & (Match.away_team_id == home_team)
            ),
        )
    )
    query = query.order_by(Match.match_date.desc()).limit(5)
    
    result = await db.execute(query)
    matches = result.scalars().all()
    
    return ApiResponse(
        success=True,
        data={
            "matches": [],
            "home_team_wins": 0,
            "away_team_wins": 0,
            "draws": 0,
        },
    )

