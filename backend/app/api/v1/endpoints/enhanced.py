"""
Enhanced endpoints using API-Football data
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.database import get_db
from app.schemas.schemas import ApiResponse
from app.services.cache import get_cache, RedisCache
from app.services.enhanced_data_service import EnhancedDataService

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_enhanced_service(cache: RedisCache = Depends(get_cache)) -> EnhancedDataService:
    """Dependency to get enhanced data service"""
    return EnhancedDataService(cache)


@router.get("/teams/{team_id}/statistics", response_model=ApiResponse)
async def get_team_statistics(
    team_id: int,
    league_id: int,
    season: int = 2024,
    db: AsyncSession = Depends(get_db),
    enhanced_service: EnhancedDataService = Depends(get_enhanced_service),
):
    """
    Get comprehensive team statistics
    Combines data from API-Football and database
    """
    try:
        stats = await enhanced_service.get_team_statistics(team_id, league_id, season, db)
        
        if not stats:
            # Return empty stats instead of 404
            return ApiResponse(
                success=True, 
                data={
                    "teamId": team_id,
                    "leagueId": league_id,
                    "form": "",
                    "fixtures": {"played": {"total": 0}, "wins": {"total": 0}, "draws": {"total": 0}, "loses": {"total": 0}},
                    "goals": {"for": {"average": {"total": "0"}}, "against": {"average": {"total": "0"}}},
                },
                message="No statistics available for this team"
            )
        
        return ApiResponse(success=True, data=stats)
    except Exception as e:
        logger.error(f"Error fetching team statistics: {e}", exc_info=True)
        return ApiResponse(
            success=False,
            message=f"Failed to fetch team statistics: {str(e)}"
        )


@router.get("/matches/{match_id}/statistics", response_model=ApiResponse)
async def get_match_statistics(
    match_id: int,
    external_fixture_id: int = None,
    enhanced_service: EnhancedDataService = Depends(get_enhanced_service),
):
    """
    Get detailed match statistics (possession, shots, etc.)
    Only available if API-Football is enabled
    """
    stats = await enhanced_service.get_match_statistics(match_id, external_fixture_id)
    
    if not stats:
        return ApiResponse(
            success=False,
            message="Match statistics not available. Enable API-Football for detailed stats."
        )
    
    return ApiResponse(success=True, data=stats)


@router.get("/matches/h2h-detailed", response_model=ApiResponse)
async def get_head_to_head_detailed(
    team1_id: int,
    team2_id: int,
    last: int = 10,
    db: AsyncSession = Depends(get_db),
    enhanced_service: EnhancedDataService = Depends(get_enhanced_service),
):
    """
    Get detailed head-to-head matches between two teams
    Includes match statistics if available
    """
    h2h_data = await enhanced_service.get_head_to_head(team1_id, team2_id, db, last)
    
    return ApiResponse(success=True, data=h2h_data)


@router.get("/teams/{team_id}/injuries", response_model=ApiResponse)
async def get_team_injuries(
    team_id: int,
    league_id: int,
    season: int = 2024,
    enhanced_service: EnhancedDataService = Depends(get_enhanced_service),
):
    """
    Get team injuries
    Only available if API-Football is enabled
    """
    injuries = await enhanced_service.get_team_injuries(team_id, league_id, season)
    
    return ApiResponse(
        success=True,
        data=injuries,
        message="No injuries data available" if not injuries else None
    )


@router.get("/matches/{match_id}/ai-prediction", response_model=ApiResponse)
async def get_ai_prediction(
    match_id: int,
    external_fixture_id: int = None,
    enhanced_service: EnhancedDataService = Depends(get_enhanced_service),
):
    """
    Get AI prediction from API-Football
    Falls back to our ML model if unavailable
    """
    prediction = await enhanced_service.get_ai_prediction(match_id, external_fixture_id)
    
    if not prediction:
        return ApiResponse(
            success=False,
            message="AI prediction not available. Enable API-Football or train ML model."
        )
    
    return ApiResponse(success=True, data=prediction)


@router.get("/api-status", response_model=ApiResponse)
async def get_api_status(
    enhanced_service: EnhancedDataService = Depends(get_enhanced_service),
):
    """
    Check API-Football status and remaining requests
    """
    status = await enhanced_service.check_api_status()
    
    return ApiResponse(success=True, data=status)
