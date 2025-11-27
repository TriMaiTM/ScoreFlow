from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from datetime import datetime

from app.db.database import get_db
from app.db.models import Team, TeamStats, Match
from app.schemas.schemas import ApiResponse

router = APIRouter()


@router.get("/{team_id}", response_model=ApiResponse)
async def get_team_by_id(team_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    
    if not team:
        return ApiResponse(success=False, message="Team not found")
    
    team_data = {
        "id": team.id,
        "name": team.name,
        "shortName": team.short_name,
        "logo": team.logo,
        "country": team.country,
    }
    
    return ApiResponse(success=True, data=team_data)


@router.get("/search", response_model=ApiResponse)
async def search_teams(
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db),
):
    query = select(Team).where(Team.name.ilike(f"%{q}%"))
    result = await db.execute(query)
    teams = result.scalars().all()
    
    teams_data = [
        {
            "id": team.id,
            "name": team.name,
            "shortName": team.short_name,
            "logo": team.logo,
            "country": team.country,
        }
        for team in teams
    ]
    
    return ApiResponse(success=True, data=teams_data)


@router.get("/{team_id}/stats", response_model=ApiResponse)
async def get_team_stats(team_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TeamStats)
        .where(TeamStats.team_id == team_id)
        .order_by(TeamStats.season.desc())
        .limit(1)
    )
    stats = result.scalar_one_or_none()
    
    if not stats:
        return ApiResponse(success=False, message="Stats not found")
    
    stats_data = {
        "teamId": stats.team_id,
        "form": stats.form,
        "goalsScored": stats.goals_scored,
        "goalsConceded": stats.goals_conceded,
        "cleanSheets": stats.clean_sheets,
        "avgGoalsScored": stats.goals_scored / max(stats.matches_played, 1),
        "avgGoalsConceded": stats.goals_conceded / max(stats.matches_played, 1),
        "homeWinPercentage": 0.0,  # TODO: Calculate from matches
        "awayWinPercentage": 0.0,  # TODO: Calculate from matches
    }
    
    return ApiResponse(success=True, data=stats_data)


@router.get("/{team_id}/recent-matches", response_model=ApiResponse)
async def get_team_recent_matches(
    team_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """Get recent finished matches for a team"""
    # Query matches where team is either home or away, and status is FINISHED
    query = (
        select(Match)
        .where(
            and_(
                or_(
                    Match.home_team_id == team_id,
                    Match.away_team_id == team_id
                ),
                Match.status == "FINISHED"
            )
        )
        .order_by(Match.match_date.desc())
        .limit(limit)
    )
    
    result = await db.execute(query)
    matches = result.scalars().all()
    
    matches_data = []
    for match in matches:
        # Determine if team is home or away
        is_home = match.home_team_id == team_id
        opponent_id = match.away_team_id if is_home else match.home_team_id
        
        # Get opponent team
        opponent_result = await db.execute(
            select(Team).where(Team.id == opponent_id)
        )
        opponent = opponent_result.scalar_one_or_none()
        
        # Determine result
        if match.home_score is not None and match.away_score is not None:
            if is_home:
                if match.home_score > match.away_score:
                    result = "W"
                elif match.home_score < match.away_score:
                    result = "L"
                else:
                    result = "D"
                team_score = match.home_score
                opponent_score = match.away_score
            else:
                if match.away_score > match.home_score:
                    result = "W"
                elif match.away_score < match.home_score:
                    result = "L"
                else:
                    result = "D"
                team_score = match.away_score
                opponent_score = match.home_score
        else:
            result = None
            team_score = None
            opponent_score = None
        
        match_data = {
            "matchId": match.id,
            "date": match.match_date.isoformat() if match.match_date else None,
            "isHome": is_home,
            "opponent": {
                "id": opponent.id if opponent else None,
                "name": opponent.name if opponent else "Unknown",
                "shortName": opponent.short_name if opponent else "Unknown",
                "logo": opponent.logo if opponent else None,
            },
            "teamScore": team_score,
            "opponentScore": opponent_score,
            "result": result,  # W, D, L
        }
        matches_data.append(match_data)
    
    return ApiResponse(success=True, data=matches_data)
