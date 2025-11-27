from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.db.models import League, Standing, Team
from app.schemas.schemas import ApiResponse

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def get_leagues(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(League))
    leagues = result.scalars().all()
    
    leagues_data = [
        {
            "id": league.id,
            "name": league.name,
            "country": league.country,
            "logo": league.logo,
            "season": league.season,
        }
        for league in leagues
    ]
    
    return ApiResponse(success=True, data=leagues_data)


@router.get("/{league_id}", response_model=ApiResponse)
async def get_league_by_id(league_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(League).where(League.id == league_id))
    league = result.scalar_one_or_none()
    
    if not league:
        return ApiResponse(success=False, message="League not found")
    
    league_data = {
        "id": league.id,
        "name": league.name,
        "country": league.country,
        "logo": league.logo,
        "season": league.season,
    }
    
    return ApiResponse(success=True, data=league_data)


@router.get("/{league_id}/standings", response_model=ApiResponse)
async def get_standings(league_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get league standings/table
    Returns teams sorted by points, goal difference, etc.
    """
    # Query standings with team relationship
    result = await db.execute(
        select(Standing)
        .options(selectinload(Standing.team))
        .where(Standing.league_id == league_id)
        .order_by(Standing.position.asc())
    )
    standings = result.scalars().all()
    
    if not standings:
        return ApiResponse(
            success=True,
            data=[],
            message="No standings data available for this league"
        )
    
    # Format standings data
    standings_data = [
        {
            "position": standing.position,
            "team": {
                "id": standing.team.id,
                "name": standing.team.name,
                "shortName": standing.team.short_name,
                "logo": standing.team.logo,
            },
            "played": standing.played,
            "won": standing.won,
            "drawn": standing.drawn,
            "lost": standing.lost,
            "goalsFor": standing.goals_for,
            "goalsAgainst": standing.goals_against,
            "goalDifference": standing.goal_difference,
            "points": standing.points,
            "form": standing.form or "",
        }
        for standing in standings
    ]
    
    return ApiResponse(success=True, data=standings_data)
